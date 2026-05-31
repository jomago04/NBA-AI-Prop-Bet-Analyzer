"""
Base scraper for Sports Reference family sites (PFR, BBRef, HockeyRef, FBref).
All use the same search pattern and data-stat attribute conventions.
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from app.config.selenium_config import SeleniumConfig
from app.utilities.safeConvert import safe_convert
from datetime import datetime, date
import unicodedata
import logging

logger = logging.getLogger(__name__)


class BaseScraper:
    BASE_URL = ""

    def __init__(self):
        self.driver, self.wait = SeleniumConfig.initialize_driver()
        self.currentYear = None

    def __del__(self):
        SeleniumConfig.cleanup_driver(self.driver)

    # ── helpers ────────────────────────────────────────────────────────────────

    def get_stat(self, row, data_stat: str, convert=float):
        """Return a stat value from a row by its data-stat attribute."""
        try:
            cell = row.find_element(By.CSS_SELECTOR, f'[data-stat="{data_stat}"]')
            text = cell.text.strip()
            if not text or text in ('-', '—', ''):
                return convert(0)
            return convert(text)
        except (NoSuchElementException, ValueError, TypeError):
            return convert(0)

    def get_stat_text(self, row, data_stat: str) -> str:
        """Return raw text from a data-stat cell."""
        try:
            cell = row.find_element(By.CSS_SELECTOR, f'[data-stat="{data_stat}"]')
            return cell.text.strip()
        except NoSuchElementException:
            return ''

    def is_active_game_row(self, row) -> bool:
        """True if the row represents an actually played game."""
        classes = row.get_attribute('class') or ''
        if 'thead' in classes or 'partial_table' in classes:
            return False
        try:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if not cells:
                return False
            sample = ' '.join(c.text for c in cells[:10])
            inactive_kws = ['inactive', 'did not play', 'dnp', 'suspended', 'injured reserve', 'not with team']
            if any(kw in sample.lower() for kw in inactive_kws):
                return False
            return True
        except Exception:
            return False

    def get_last_n_game_rows(self, table_css: str, n: int = 5) -> list:
        """Return the last N active game rows from a table."""
        try:
            table = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, table_css)))
            rows = table.find_elements(By.CSS_SELECTOR, 'tbody tr')
            active = []
            for row in reversed(rows):
                if self.is_active_game_row(row):
                    active.append(row)
                if len(active) >= n:
                    break
            return active
        except TimeoutException:
            logger.warning(f"Timed out waiting for {table_css}")
            return []

    def days_since(self, date_str: str) -> int:
        """Return days since a date string (tries common formats)."""
        for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%B %d, %Y', '%Y-%m'):
            try:
                game_date = datetime.strptime(date_str.strip(), fmt).date()
                return (date.today() - game_date).days
            except ValueError:
                continue
        return 0

    # ── player search ──────────────────────────────────────────────────────────

    def _normalize(self, name: str) -> tuple:
        """Return (normalized_name, current_year) from a search result name."""
        current_year = None
        if '(' in name:
            bracket = name.split(')')[0].split('(')[1]
            if '-' in bracket:
                current_year = bracket.split('-')[1].strip()
        name = name.split('(')[0].strip()
        normalized = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
        return normalized.lower(), current_year

    def search_player(self, player_name: str):
        """
        Search for a player on a Sports Reference site.
        Returns (player_url_path, current_year) or None on failure.
        """
        parts = player_name.strip().split()
        query = '+'.join(parts)
        search_url = f"{self.BASE_URL}/search/search.fcgi?search={query}"
        logger.info(f"Searching: {search_url}")
        self.driver.get(search_url)

        # Site may redirect directly to a unique player's page
        if '/players/' in self.driver.current_url and '/search/' not in self.driver.current_url:
            path = self.driver.current_url.replace(self.BASE_URL, '').split('?')[0]
            logger.info(f"Redirected directly to player: {path}")
            self.currentYear = str(datetime.now().year)
            return path, self.currentYear

        try:
            div = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div#players')))
            items = div.find_elements(By.CSS_SELECTOR, 'div.search-item')
            target_norm, _ = self._normalize(player_name)
            for item in items:
                try:
                    name_el = item.find_element(By.CSS_SELECTOR, 'div.search-item-name')
                    norm, year = self._normalize(name_el.text.strip())
                    if norm == target_norm:
                        url_el = item.find_element(By.CSS_SELECTOR, 'div.search-item-url')
                        path = url_el.text.strip()
                        self.currentYear = year or str(datetime.now().year)
                        logger.info(f"Found player: {path} (year={self.currentYear})")
                        return path, self.currentYear
                except NoSuchElementException:
                    continue
        except TimeoutException:
            logger.error(f"No search results for '{player_name}'")
        return None
