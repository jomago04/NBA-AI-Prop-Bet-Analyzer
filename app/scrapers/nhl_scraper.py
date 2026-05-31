"""
NHL scraper using Hockey-Reference.com.
Player pages: /players/{L}/{code}.html
Game log:     /players/{L}/{code}/gamelog/{year}/
Team page:    /teams/{abbr}/{year}.html
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from app.scrapers.base_scraper import BaseScraper
from app.models.nhl_models import (
    NHLPlayerInfo, NHLGameStats, NHLLastFiveAverages, NHLSeasonStats, NHLOpposingTeamStats
)
from app.utilities.timeConverter import TimeConverter
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)

BASE = "https://www.hockey-reference.com"


class NHLScraper(BaseScraper):
    BASE_URL = BASE

    def _build_urls(self, player_name: str):
        result = self.search_player(player_name)
        if not result:
            raise RuntimeError(f"Player not found: {player_name}")
        path, year = result
        player_url = f"{BASE}{path}"
        gamelog_url = f"{BASE}{path.replace('.html', '')}/gamelog/{year}/"
        return player_url, gamelog_url, year

    def _get_position(self) -> str:
        try:
            meta = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div#meta')))
            for p in meta.find_elements(By.TAG_NAME, 'p'):
                if 'Position' in p.text:
                    return p.text.split(':')[1].strip().split()[0]
        except Exception:
            pass
        return 'F'

    def get_player_stats(self, player_name: str) -> dict:
        player_url, gamelog_url, year = self._build_urls(player_name)

        # ── Player page ────────────────────────────────────────────────────────
        self.driver.get(player_url)
        position = self._get_position()

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
            logger.warning(f"Error reading NHL player meta: {e}")

        # Season stats
        season_stats = NHLSeasonStats()
        try:
            season_stats = self._extract_season_stats()
        except Exception as e:
            logger.warning(f"Error reading NHL season stats: {e}")

        # ── Game log ───────────────────────────────────────────────────────────
        self.driver.get(gamelog_url)
        rows = self.get_last_n_game_rows(f'table#gamelog{year}, table#gamelog, table#stats', 5)
        if not rows:
            rows = self.get_last_n_game_rows('table', 5)

        days_since = 0
        individual_games = []
        for row in rows:
            try:
                date_text = (self.get_stat_text(row, 'date_game') or
                             self.get_stat_text(row, 'date'))
                if not individual_games:
                    days_since = self.days_since(date_text)

                opp_text = (self.get_stat_text(row, 'opp_id') or
                            self.get_stat_text(row, 'opp'))
                loc_text = self.get_stat_text(row, 'game_location')
                is_away = loc_text == '@'

                toi_str = (self.get_stat_text(row, 'toi') or
                           self.get_stat_text(row, 'time_on_ice') or '0:00')
                toi = TimeConverter.convertTimeStringToFloat(toi_str)

                g = self.get_stat(row, 'goals', int)
                a = self.get_stat(row, 'assists', int)
                game = NHLGameStats(
                    opponent=opp_text,
                    isAway=is_away,
                    goals=g,
                    assists=a,
                    points=g + a,
                    shots=self.get_stat(row, 'shots', int),
                    plusMinus=self.get_stat(row, 'plus_minus', int),
                    penaltyMinutes=self.get_stat(row, 'pim', int),
                    timeOnIce=toi,
                )
                individual_games.append(game)
            except Exception as e:
                logger.warning(f"Error processing NHL game row: {e}")

        n = len(individual_games) or 1
        l5 = NHLLastFiveAverages(
            averageGoals=sum(g.goals for g in individual_games) / n,
            averageAssists=sum(g.assists for g in individual_games) / n,
            averagePoints=sum(g.points for g in individual_games) / n,
            averageShots=sum(g.shots for g in individual_games) / n,
            averagePlusMinus=sum(g.plusMinus for g in individual_games) / n,
            averageTimeOnIce=sum(g.timeOnIce for g in individual_games) / n,
        )

        player_info = NHLPlayerInfo(
            name=name or player_name,
            team=team,
            position=position,
            age=age,
            daysSinceLastGame=days_since,
        )

        # ── Opposing team ──────────────────────────────────────────────────────
        opp_stats = NHLOpposingTeamStats(teamName='Unknown', wins=0, losses=0)
        if individual_games:
            opp_abbr = individual_games[0].opponent
            opp_url = f"{BASE}/teams/{opp_abbr}/{year}.html"
            try:
                self.driver.get(opp_url)
                opp_stats = self._extract_team_stats(opp_abbr)
            except Exception as e:
                logger.warning(f"Could not load NHL team page: {e}")

        return {
            'player_info': player_info,
            'season_stats': season_stats,
            'last_five_averages': l5,
            'opposing_team': opp_stats,
            'individual_games': individual_games,
        }

    def _extract_season_stats(self) -> NHLSeasonStats:
        table = self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'table#skaterstats, table#stats')))
        rows = table.find_elements(By.CSS_SELECTOR, 'tbody tr:not(.thead)')
        row = rows[-1] if rows else None
        if not row:
            return NHLSeasonStats()
        gp = max(1, self.get_stat(row, 'games_played', int) or self.get_stat(row, 'GP', int) or 1)
        g = self.get_stat(row, 'goals', int)
        a = self.get_stat(row, 'assists', int)
        sh = self.get_stat(row, 'shots', int)
        return NHLSeasonStats(
            gamesPlayed=gp,
            goals=g,
            assists=a,
            points=g + a,
            averageGoals=g / gp,
            averageAssists=a / gp,
            averagePoints=(g + a) / gp,
            averageShots=sh / gp,
            shootingPct=self.get_stat(row, 'shooting_pct') or self.get_stat(row, 'S%'),
        )

    def _extract_team_stats(self, opp_abbr: str) -> NHLOpposingTeamStats:
        try:
            meta = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div#meta')))
            team_name = meta.find_element(By.CSS_SELECTOR, 'h1').text.strip()
            wins, losses, ot = 0, 0, 0
            for p in meta.find_elements(By.TAG_NAME, 'p'):
                m = re.search(r'(\d+)-(\d+)-(\d+)', p.text)
                if m:
                    wins, losses, ot = int(m.group(1)), int(m.group(2)), int(m.group(3))
                    break
            return NHLOpposingTeamStats(teamName=team_name, wins=wins, losses=losses, otLosses=ot)
        except Exception as e:
            logger.warning(f"Error extracting NHL team stats: {e}")
            return NHLOpposingTeamStats(teamName=opp_abbr, wins=0, losses=0)
