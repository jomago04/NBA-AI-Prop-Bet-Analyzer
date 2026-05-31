"""
Soccer scraper using FBref.com.
FBref uses UUIDs for player IDs, not the standard Sports Reference letter/code format.
Player pages: /en/players/{uuid}/{Name}/
Match log:    /en/players/{uuid}/matchlogs/{year}/summary/{Name}-Match-Logs
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from app.scrapers.base_scraper import BaseScraper
from app.models.soccer_models import (
    SoccerPlayerInfo, SoccerGameStats, SoccerLastFiveAverages, SoccerSeasonStats, SoccerOpposingTeamStats
)
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)

BASE = "https://fbref.com"


class SoccerScraper(BaseScraper):
    BASE_URL = BASE

    def search_player(self, player_name: str):
        """
        FBref search returns UUID-based URLs like /en/players/{uuid}/{Name}/
        Override base class to handle this URL format.
        """
        parts = player_name.strip().split()
        query = '+'.join(parts)
        search_url = f"{BASE}/search/search.fcgi?search={query}"
        logger.info(f"FBref search: {search_url}")
        self.driver.get(search_url)

        # Direct redirect to player page
        if '/en/players/' in self.driver.current_url and '/search/' not in self.driver.current_url:
            path = self.driver.current_url.replace(BASE, '').split('?')[0]
            self.currentYear = str(datetime.now().year)
            logger.info(f"Redirected to player: {path}")
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
                        return path, self.currentYear
                except NoSuchElementException:
                    continue
        except Exception as e:
            logger.error(f"FBref search error: {e}")
        return None

    def _extract_player_uuid(self, path: str) -> str:
        """Extract UUID from /en/players/{uuid}/{Name}/ path."""
        parts = path.strip('/').split('/')
        # Expected: ['en', 'players', '{uuid}', '{Name}']
        if len(parts) >= 3:
            return parts[2]
        return ''

    def _extract_player_slug(self, path: str) -> str:
        """Extract name slug from path for building match log URL."""
        parts = path.strip('/').split('/')
        return parts[-1] if parts else ''

    def get_player_stats(self, player_name: str) -> dict:
        result = self.search_player(player_name)
        if not result:
            raise RuntimeError(f"Player not found: {player_name}")
        path, year = result

        uuid = self._extract_player_uuid(path)
        slug = self._extract_player_slug(path)

        player_url = f"{BASE}{path}"
        matchlog_url = f"{BASE}/en/players/{uuid}/matchlogs/{year}/summary/{slug}-Match-Logs"

        # ── Player page ────────────────────────────────────────────────────────
        self.driver.get(player_url)

        name = ''
        team = ''
        position = ''
        age = 0
        try:
            meta = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div#meta')))
            name = meta.find_element(By.CSS_SELECTOR, 'h1').text.strip()
            for p in meta.find_elements(By.TAG_NAME, 'p'):
                text = p.text
                if 'Position' in text:
                    position = text.split(':')[1].strip().split()[0]
                if 'Club' in text or 'Team' in text:
                    try:
                        team = p.find_element(By.TAG_NAME, 'a').text.strip()
                    except Exception:
                        team = text.split(':')[1].strip() if ':' in text else ''
                m = re.search(r'Age:\s*(\d+)', text)
                if m:
                    age = int(m.group(1))
        except Exception as e:
            logger.warning(f"Error reading soccer player meta: {e}")

        # Season stats from standard stats table
        season_stats = SoccerSeasonStats()
        try:
            season_stats = self._extract_season_stats()
        except Exception as e:
            logger.warning(f"Error reading soccer season stats: {e}")

        # ── Match log ──────────────────────────────────────────────────────────
        self.driver.get(matchlog_url)
        rows = self.get_last_n_game_rows('table#matchlogs_all, table[id*="matchlog"]', 5)

        days_since = 0
        individual_games = []
        for row in rows:
            try:
                date_text = self.get_stat_text(row, 'date')
                if not individual_games:
                    days_since = self.days_since(date_text)

                opp_text = self.get_stat_text(row, 'opponent')
                loc_text = self.get_stat_text(row, 'venue')
                is_away = 'Away' in loc_text or loc_text == 'A'

                mins_text = self.get_stat_text(row, 'minutes')
                mins = float(mins_text) if mins_text.isdigit() else 0.0

                g = self.get_stat(row, 'goals', int)
                a = self.get_stat(row, 'assists', int)
                game = SoccerGameStats(
                    opponent=opp_text,
                    isAway=is_away,
                    minutesPlayed=mins,
                    goals=g,
                    assists=a,
                    shots=self.get_stat(row, 'shots', int),
                    shotsOnTarget=self.get_stat(row, 'shots_on_target', int),
                    xG=self.get_stat(row, 'xg'),
                    xA=self.get_stat(row, 'xg_assist') or self.get_stat(row, 'xa'),
                )
                individual_games.append(game)
            except Exception as e:
                logger.warning(f"Error processing soccer match row: {e}")

        n = len(individual_games) or 1
        l5 = SoccerLastFiveAverages(
            averageGoals=sum(g.goals for g in individual_games) / n,
            averageAssists=sum(g.assists for g in individual_games) / n,
            averageShots=sum(g.shots for g in individual_games) / n,
            averageShotsOnTarget=sum(g.shotsOnTarget for g in individual_games) / n,
            averageXG=sum(g.xG for g in individual_games) / n,
            averageXA=sum(g.xA for g in individual_games) / n,
            averageMinutesPlayed=sum(g.minutesPlayed for g in individual_games) / n,
        )

        player_info = SoccerPlayerInfo(
            name=name or player_name,
            team=team,
            position=position,
            age=age,
            daysSinceLastGame=days_since,
        )

        # Opposing team stats — load the opponent's FBref team page
        opp_stats = SoccerOpposingTeamStats(teamName='Unknown', wins=0, draws=0, losses=0)

        return {
            'player_info': player_info,
            'season_stats': season_stats,
            'last_five_averages': l5,
            'opposing_team': opp_stats,
            'individual_games': individual_games,
        }

    def _extract_season_stats(self) -> SoccerSeasonStats:
        # FBref standard stats table has ID like stats_standard_{comp}
        try:
            table = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'table[id^="stats_standard"]')))
            rows = table.find_elements(By.CSS_SELECTOR, 'tbody tr:not(.thead)')
            row = rows[-1] if rows else None
            if not row:
                return SoccerSeasonStats()
            gp = max(1, self.get_stat(row, 'games', int) or 1)
            g = self.get_stat(row, 'goals', int)
            a = self.get_stat(row, 'assists', int)
            sh = self.get_stat(row, 'shots', int)
            sot = self.get_stat(row, 'shots_on_target', int)
            mins = self.get_stat(row, 'minutes')
            return SoccerSeasonStats(
                gamesPlayed=gp,
                goals=g,
                assists=a,
                averageGoals=g / gp,
                averageAssists=a / gp,
                averageShots=sh / gp,
                averageShotsOnTarget=sot / gp,
                averageXG=self.get_stat(row, 'xg') / gp,
                shotConversionRate=(g / sh * 100) if sh else 0.0,
                averageMinutesPlayed=mins / gp,
            )
        except Exception as e:
            logger.warning(f"Error reading FBref season stats: {e}")
            return SoccerSeasonStats()
