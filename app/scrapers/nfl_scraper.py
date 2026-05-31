"""
NFL scraper using Pro-Football-Reference.com.
Player pages: /players/{L}/{code}.htm  (note: .htm extension)
Game log:     /players/{L}/{code}/gamelog/{year}/
Team page:    /teams/{abbr}/{year}.htm
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from app.scrapers.base_scraper import BaseScraper
from app.models.nfl_models import (
    NFLPlayerInfo, NFLGameStats, NFLLastFiveAverages, NFLSeasonStats, NFLOpposingTeamStats
)
from app.utilities.safeConvert import safe_convert
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)

BASE = "https://www.pro-football-reference.com"


class NFLScraper(BaseScraper):
    BASE_URL = BASE

    def _build_urls(self, player_name: str):
        result = self.search_player(player_name)
        if not result:
            raise RuntimeError(f"Player not found: {player_name}")
        path, year = result
        # path like /players/M/MahoPa00.htm
        player_url = f"{BASE}{path}"
        gamelog_url = f"{BASE}{path.rstrip('.htm').rstrip('/')}/gamelog/{year}/"
        return player_url, gamelog_url, year

    def _get_position(self) -> str:
        try:
            meta = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div#meta')))
            for p in meta.find_elements(By.TAG_NAME, 'p'):
                if 'Position' in p.text:
                    # e.g. "Position: QB"
                    return p.text.split(':')[1].strip().split()[0]
        except Exception:
            pass
        return 'UNKNOWN'

    def _detect_gamelog_table(self) -> str:
        """Return CSS selector for the gamelog table (varies by year/type)."""
        for sel in ['table#stats', 'table#gamelog', 'table[id^="gamelog"]', 'table[id*="passing"]']:
            try:
                self.driver.find_element(By.CSS_SELECTOR, sel)
                return sel
            except Exception:
                continue
        return 'table'

    def get_player_stats(self, player_name: str) -> dict:
        player_url, gamelog_url, year = self._build_urls(player_name)

        # ── Player page ────────────────────────────────────────────────────────
        self.driver.get(player_url)
        position = self._get_position()

        # Player info
        name = ''
        team = ''
        age = 0
        try:
            meta = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div#meta')))
            name = meta.find_element(By.CSS_SELECTOR, 'h1 span').text.strip()
            for p in meta.find_elements(By.TAG_NAME, 'p'):
                if 'Team' in p.text or 'Club' in p.text:
                    team = p.text.split(':')[1].strip().split()[0]
                if 'Born' in p.text or 'Age' in p.text:
                    m = re.search(r'Age:\s*(\d+)', p.text)
                    if m:
                        age = int(m.group(1))
        except Exception as e:
            logger.warning(f"Error reading player meta: {e}")

        # Season stats (detect position-specific table)
        season_stats = NFLSeasonStats()
        try:
            pos = position.upper()
            if 'QB' in pos:
                table_id = 'table#passing'
                stats_map = self._extract_qb_season(table_id)
            elif 'RB' in pos or 'FB' in pos:
                table_id = 'table#rushing'
                stats_map = self._extract_rb_season(table_id)
            else:  # WR, TE
                table_id = 'table#receiving'
                stats_map = self._extract_rec_season(table_id)
            season_stats = NFLSeasonStats(**stats_map)
        except Exception as e:
            logger.warning(f"Error reading season stats: {e}")

        # ── Game log page ──────────────────────────────────────────────────────
        self.driver.get(gamelog_url)
        table_sel = self._detect_gamelog_table()
        rows = self.get_last_n_game_rows(table_sel, 5)
        if not rows:
            logger.warning("No game rows found in gamelog")

        days_since = 0
        individual_games = []
        for row in rows:
            try:
                date_text = self.get_stat_text(row, 'game_date')
                if not date_text:
                    date_text = self.get_stat_text(row, 'date_game')
                if not individual_games:  # most recent game
                    days_since = self.days_since(date_text)

                opp_text = self.get_stat_text(row, 'opp')
                loc_text = self.get_stat_text(row, 'game_location')
                is_away = loc_text == '@'

                game = NFLGameStats(
                    opponent=opp_text,
                    isAway=is_away,
                    completions=self.get_stat(row, 'pass_cmp', int),
                    passAttempts=self.get_stat(row, 'pass_att', int),
                    passYards=self.get_stat(row, 'pass_yds', int),
                    passTDs=self.get_stat(row, 'pass_td', int),
                    interceptions=self.get_stat(row, 'pass_int', int),
                    passerRating=self.get_stat(row, 'passer_rating'),
                    rushAttempts=self.get_stat(row, 'rush_att', int),
                    rushYards=self.get_stat(row, 'rush_yds', int),
                    rushTDs=self.get_stat(row, 'rush_td', int),
                    targets=self.get_stat(row, 'targets', int) or self.get_stat(row, 'rec_tgt', int),
                    receptions=self.get_stat(row, 'rec', int),
                    recYards=self.get_stat(row, 'rec_yds', int),
                    recTDs=self.get_stat(row, 'rec_td', int),
                )
                individual_games.append(game)
            except Exception as e:
                logger.warning(f"Error processing NFL game row: {e}")

        # Compute last-5 averages
        n = len(individual_games) or 1
        l5 = NFLLastFiveAverages(
            averagePassYards=sum(g.passYards for g in individual_games) / n,
            averagePassTDs=sum(g.passTDs for g in individual_games) / n,
            averageInterceptions=sum(g.interceptions for g in individual_games) / n,
            averagePasserRating=sum(g.passerRating for g in individual_games) / n,
            averageRushYards=sum(g.rushYards for g in individual_games) / n,
            averageRushTDs=sum(g.rushTDs for g in individual_games) / n,
            averageReceptions=sum(g.receptions for g in individual_games) / n,
            averageRecYards=sum(g.recYards for g in individual_games) / n,
            averageRecTDs=sum(g.recTDs for g in individual_games) / n,
            averageTargets=sum(g.targets for g in individual_games) / n,
        )

        player_info = NFLPlayerInfo(
            name=name or player_name,
            team=team,
            position=position,
            age=age,
            daysSinceLastGame=days_since,
        )

        # ── Opposing team stats ────────────────────────────────────────────────
        opp_stats = NFLOpposingTeamStats(teamName='Unknown', wins=0, losses=0)
        if individual_games:
            opp_abbr = individual_games[0].opponent
            opp_url = f"{BASE}/teams/{opp_abbr.lower()}/{year}.htm"
            try:
                self.driver.get(opp_url)
                opp_stats = self._extract_team_defense(opp_abbr, year)
            except Exception as e:
                logger.warning(f"Could not load opposing team page: {e}")

        return {
            'player_info': player_info,
            'season_stats': season_stats,
            'last_five_averages': l5,
            'opposing_team': opp_stats,
            'individual_games': individual_games,
        }

    # ── Season stat extractors ─────────────────────────────────────────────────

    def _last_season_row(self, table_sel: str):
        try:
            table = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, table_sel)))
            rows = table.find_elements(By.CSS_SELECTOR, 'tbody tr:not(.thead)')
            return rows[-1] if rows else None
        except Exception:
            return None

    def _extract_qb_season(self, table_sel) -> dict:
        row = self._last_season_row(table_sel)
        if not row:
            return {}
        cmp = self.get_stat(row, 'pass_cmp')
        att = self.get_stat(row, 'pass_att')
        gp = max(1, self.get_stat(row, 'game_num', int) or self.get_stat(row, 'games', int) or 1)
        return dict(
            gamesPlayed=gp,
            averagePassYards=self.get_stat(row, 'pass_yds') / gp,
            averagePassTDs=self.get_stat(row, 'pass_td') / gp,
            averageInterceptions=self.get_stat(row, 'pass_int') / gp,
            averagePasserRating=self.get_stat(row, 'passer_rating'),
            averageRushYards=self.get_stat(row, 'rush_yds') / gp,
            averageRushTDs=self.get_stat(row, 'rush_td') / gp,
            completionPct=(cmp / att * 100) if att else 0.0,
        )

    def _extract_rb_season(self, table_sel) -> dict:
        row = self._last_season_row(table_sel)
        if not row:
            return {}
        gp = max(1, self.get_stat(row, 'game_num', int) or self.get_stat(row, 'games', int) or 1)
        return dict(
            gamesPlayed=gp,
            averageRushYards=self.get_stat(row, 'rush_yds') / gp,
            averageRushTDs=self.get_stat(row, 'rush_td') / gp,
            averageReceptions=self.get_stat(row, 'rec') / gp,
            averageRecYards=self.get_stat(row, 'rec_yds') / gp,
        )

    def _extract_rec_season(self, table_sel) -> dict:
        row = self._last_season_row(table_sel)
        if not row:
            return {}
        gp = max(1, self.get_stat(row, 'game_num', int) or self.get_stat(row, 'games', int) or 1)
        return dict(
            gamesPlayed=gp,
            averageReceptions=self.get_stat(row, 'rec') / gp,
            averageRecYards=self.get_stat(row, 'rec_yds') / gp,
            averageRecTDs=self.get_stat(row, 'rec_td') / gp,
            averageTargets=(self.get_stat(row, 'targets') or self.get_stat(row, 'rec_tgt')) / gp,
        )

    def _extract_team_defense(self, opp_abbr: str, year: str) -> NFLOpposingTeamStats:
        try:
            meta = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div#meta')))
            team_name = meta.find_element(By.CSS_SELECTOR, 'h1').text.strip()

            # Win-loss from standings or team info
            wins, losses = 0, 0
            for p in meta.find_elements(By.TAG_NAME, 'p'):
                m = re.search(r'(\d+)-(\d+)', p.text)
                if m:
                    wins, losses = int(m.group(1)), int(m.group(2))
                    break

            # Team defense table
            table = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table#team_stats')))
            # Row 0 = offense, row 1 = defense (opponent stats)
            rows = table.find_elements(By.CSS_SELECTOR, 'tbody tr:not(.thead)')
            def_row = rows[1] if len(rows) > 1 else rows[0]

            return NFLOpposingTeamStats(
                teamName=team_name,
                wins=wins,
                losses=losses,
                pointsAllowedPerGame=self.get_stat(def_row, 'points'),
                passYardsAllowedPerGame=self.get_stat(def_row, 'pass_yds'),
                rushYardsAllowedPerGame=self.get_stat(def_row, 'rush_yds'),
                totalYardsAllowedPerGame=self.get_stat(def_row, 'yards'),
            )
        except Exception as e:
            logger.warning(f"Error extracting team defense for {opp_abbr}: {e}")
            return NFLOpposingTeamStats(teamName=opp_abbr, wins=0, losses=0)
