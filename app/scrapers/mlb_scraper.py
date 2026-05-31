"""
MLB scraper using Baseball-Reference.com.
Player pages: /players/{L}/{code}.shtml  (note: .shtml extension)
Game log:     /players/{L}/{code}/gamelog/{year}/
Team page:    /teams/{abbr}/{year}.shtml
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from app.scrapers.base_scraper import BaseScraper
from app.models.mlb_models import (
    MLBPlayerInfo, MLBGameStats, MLBLastFiveAverages, MLBSeasonStats, MLBOpposingTeamStats
)
from app.utilities.safeConvert import safe_convert
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)

BASE = "https://www.baseball-reference.com"

PITCHER_POSITIONS = {'SP', 'RP', 'P', 'CL'}


class MLBScraper(BaseScraper):
    BASE_URL = BASE

    def _is_pitcher(self, position: str) -> bool:
        return position.upper() in PITCHER_POSITIONS or 'P' == position.upper()

    def _build_urls(self, player_name: str):
        result = self.search_player(player_name)
        if not result:
            raise RuntimeError(f"Player not found: {player_name}")
        path, year = result
        player_url = f"{BASE}{path}"
        gamelog_url = f"{BASE}{path.replace('.shtml', '')}/gamelog/{year}/"
        return player_url, gamelog_url, year

    def _get_position(self) -> str:
        try:
            meta = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div#meta')))
            for p in meta.find_elements(By.TAG_NAME, 'p'):
                if 'Position' in p.text:
                    return p.text.split(':')[1].strip().split()[0]
        except Exception:
            pass
        return 'UNKNOWN'

    def get_player_stats(self, player_name: str) -> dict:
        player_url, gamelog_url, year = self._build_urls(player_name)

        # ── Player page ────────────────────────────────────────────────────────
        self.driver.get(player_url)
        position = self._get_position()
        is_pitcher = self._is_pitcher(position)

        name = ''
        team = ''
        age = 0
        try:
            meta = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div#meta')))
            name = meta.find_element(By.CSS_SELECTOR, 'h1').text.strip()
            for p in meta.find_elements(By.TAG_NAME, 'p'):
                if 'Team' in p.text:
                    team = p.text.split(':')[1].strip().split()[0]
                m = re.search(r'Age:\s*(\d+)', p.text)
                if m:
                    age = int(m.group(1))
        except Exception as e:
            logger.warning(f"Error reading player meta: {e}")

        # Season stats
        season_stats = MLBSeasonStats()
        try:
            if is_pitcher:
                season_stats = self._extract_pitcher_season()
            else:
                season_stats = self._extract_batter_season()
        except Exception as e:
            logger.warning(f"Error reading MLB season stats: {e}")

        # ── Game log ───────────────────────────────────────────────────────────
        self.driver.get(gamelog_url)
        table_sel = 'table#pitching_gamelogs' if is_pitcher else 'table#batting_gamelogs'
        rows = self.get_last_n_game_rows(table_sel, 5)
        if not rows:
            # Fallback selectors
            for sel in ['table#batting', 'table#pitching', 'table']:
                rows = self.get_last_n_game_rows(sel, 5)
                if rows:
                    break

        days_since = 0
        individual_games = []
        for row in rows:
            try:
                date_text = self.get_stat_text(row, 'date_game')
                if not individual_games:
                    days_since = self.days_since(date_text)

                opp_text = self.get_stat_text(row, 'opp_ID') or self.get_stat_text(row, 'opp_id')
                loc_text = self.get_stat_text(row, 'game_location')
                is_away = loc_text == '@'

                if is_pitcher:
                    ip_raw = self.get_stat_text(row, 'IP')
                    ip = self._parse_ip(ip_raw)
                    game = MLBGameStats(
                        opponent=opp_text,
                        isAway=is_away,
                        inningsPitched=ip,
                        hitsAllowed=self.get_stat(row, 'H', int),
                        earnedRuns=self.get_stat(row, 'ER', int),
                        strikeouts=self.get_stat(row, 'SO', int),
                        walks=self.get_stat(row, 'BB', int),
                        homeRunsAllowed=self.get_stat(row, 'HR', int),
                    )
                else:
                    h = self.get_stat(row, 'H', int)
                    hr = self.get_stat(row, 'HR', int)
                    ab = self.get_stat(row, 'AB', int)
                    tb = self.get_stat(row, 'TB', int) or (h + hr)
                    game = MLBGameStats(
                        opponent=opp_text,
                        isAway=is_away,
                        atBats=ab,
                        hits=h,
                        runs=self.get_stat(row, 'R', int),
                        rbis=self.get_stat(row, 'RBI', int),
                        homeRuns=hr,
                        batterStrikeouts=self.get_stat(row, 'SO', int),
                        batterWalks=self.get_stat(row, 'BB', int),
                        totalBases=tb,
                    )
                individual_games.append(game)
            except Exception as e:
                logger.warning(f"Error processing MLB game row: {e}")

        n = len(individual_games) or 1
        if is_pitcher:
            l5 = MLBLastFiveAverages(
                averageInningsPitched=sum(g.inningsPitched for g in individual_games) / n,
                averageHitsAllowed=sum(g.hitsAllowed for g in individual_games) / n,
                averageEarnedRuns=sum(g.earnedRuns for g in individual_games) / n,
                averageStrikeouts=sum(g.strikeouts for g in individual_games) / n,
                averageWalks=sum(g.walks for g in individual_games) / n,
            )
        else:
            l5 = MLBLastFiveAverages(
                averageAtBats=sum(g.atBats for g in individual_games) / n,
                averageHits=sum(g.hits for g in individual_games) / n,
                averageRBIs=sum(g.rbis for g in individual_games) / n,
                averageHomeRuns=sum(g.homeRuns for g in individual_games) / n,
                averageTotalBases=sum(g.totalBases for g in individual_games) / n,
                averageBatterStrikeouts=sum(g.batterStrikeouts for g in individual_games) / n,
            )

        player_info = MLBPlayerInfo(
            name=name or player_name,
            team=team,
            position=position,
            age=age,
            isPitcher=is_pitcher,
            daysSinceLastGame=days_since,
        )

        # ── Opposing team ──────────────────────────────────────────────────────
        opp_stats = MLBOpposingTeamStats(teamName='Unknown', wins=0, losses=0)
        if individual_games:
            opp_abbr = individual_games[0].opponent
            opp_url = f"{BASE}/teams/{opp_abbr}/{year}.shtml"
            try:
                self.driver.get(opp_url)
                opp_stats = self._extract_team_stats(opp_abbr, year, is_pitcher)
            except Exception as e:
                logger.warning(f"Could not load MLB team page: {e}")

        return {
            'player_info': player_info,
            'season_stats': season_stats,
            'last_five_averages': l5,
            'opposing_team': opp_stats,
            'individual_games': individual_games,
        }

    def _parse_ip(self, ip_str: str) -> float:
        """Convert '6.1' (6 innings + 1 out) to decimal."""
        try:
            parts = str(ip_str).split('.')
            full = int(parts[0])
            outs = int(parts[1]) if len(parts) > 1 else 0
            return full + outs / 3
        except (ValueError, IndexError):
            return 0.0

    def _extract_pitcher_season(self) -> MLBSeasonStats:
        table = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table#pitching_standard, table#pitching')))
        rows = table.find_elements(By.CSS_SELECTOR, 'tbody tr:not(.thead)')
        row = rows[-1] if rows else None
        if not row:
            return MLBSeasonStats()
        gp = max(1, self.get_stat(row, 'G', int) or 1)
        ip = self._parse_ip(self.get_stat_text(row, 'IP'))
        so = self.get_stat(row, 'SO')
        return MLBSeasonStats(
            gamesPlayed=gp,
            era=self.get_stat(row, 'earned_run_avg') or self.get_stat(row, 'ERA'),
            whip=self.get_stat(row, 'whip') or self.get_stat(row, 'WHIP'),
            strikeoutsPerNine=(so / ip * 9) if ip else 0.0,
            averageInningsPitched=ip / gp,
            averageStrikeouts=so / gp,
            averageEarnedRuns=self.get_stat(row, 'ER') / gp,
        )

    def _extract_batter_season(self) -> MLBSeasonStats:
        table = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table#batting_standard, table#batting')))
        rows = table.find_elements(By.CSS_SELECTOR, 'tbody tr:not(.thead)')
        row = rows[-1] if rows else None
        if not row:
            return MLBSeasonStats()
        gp = max(1, self.get_stat(row, 'G', int) or 1)
        h = self.get_stat(row, 'H')
        hr = self.get_stat(row, 'HR')
        return MLBSeasonStats(
            gamesPlayed=gp,
            battingAverage=self.get_stat(row, 'batting_avg') or self.get_stat(row, 'BA'),
            obp=self.get_stat(row, 'onbase_perc') or self.get_stat(row, 'OBP'),
            slg=self.get_stat(row, 'slugging_perc') or self.get_stat(row, 'SLG'),
            averageHits=h / gp,
            averageHomeRuns=hr / gp,
            averageRBIs=self.get_stat(row, 'RBI') / gp,
            averageTotalBases=(self.get_stat(row, 'TB') or (h + hr)) / gp,
        )

    def _extract_team_stats(self, opp_abbr: str, year: str, player_is_pitcher: bool) -> MLBOpposingTeamStats:
        try:
            meta = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div#meta')))
            team_name = meta.find_element(By.CSS_SELECTOR, 'h1').text.strip()
            wins, losses = 0, 0
            for p in meta.find_elements(By.TAG_NAME, 'p'):
                m = re.search(r'(\d+)-(\d+)', p.text)
                if m:
                    wins, losses = int(m.group(1)), int(m.group(2))
                    break
            return MLBOpposingTeamStats(teamName=team_name, wins=wins, losses=losses)
        except Exception as e:
            logger.warning(f"Error extracting MLB team stats: {e}")
            return MLBOpposingTeamStats(teamName=opp_abbr, wins=0, losses=0)
