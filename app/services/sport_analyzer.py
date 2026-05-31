"""
Unified sport stats dispatcher with per-sport caching.
NBA uses the existing GetNBAPlayerStats service.
NFL/MLB/NHL/Soccer use the new scrapers in app/scrapers/.
"""
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

CACHE_TTL = timedelta(minutes=10)
_stats_cache: dict = {}
_scrapers: dict = {}

SUPPORTED_SPORTS = {'nba', 'nfl', 'mlb', 'nhl', 'soccer'}


def _get_scraper(sport: str):
    if sport not in _scrapers:
        if sport == 'nba':
            from app.services.runScraper import GetNBAPlayerStats
            _scrapers['nba'] = GetNBAPlayerStats()
        elif sport == 'nfl':
            from app.scrapers.nfl_scraper import NFLScraper
            _scrapers['nfl'] = NFLScraper()
        elif sport == 'mlb':
            from app.scrapers.mlb_scraper import MLBScraper
            _scrapers['mlb'] = MLBScraper()
        elif sport == 'nhl':
            from app.scrapers.nhl_scraper import NHLScraper
            _scrapers['nhl'] = NHLScraper()
        elif sport == 'soccer':
            from app.scrapers.soccer_scraper import SoccerScraper
            _scrapers['soccer'] = SoccerScraper()
        else:
            raise ValueError(f"Unknown sport: {sport!r}. Must be one of: {SUPPORTED_SPORTS}")
    return _scrapers[sport]


def get_stats(sport: str, player_name: str) -> dict:
    """Return stats dict for the given sport and player, using cache when fresh."""
    sport = sport.lower().strip()
    if sport not in SUPPORTED_SPORTS:
        raise ValueError(f"Unknown sport: {sport!r}")

    cache_key = f"{sport}:{player_name.lower().strip()}"
    if cache_key in _stats_cache:
        cached_at, result = _stats_cache[cache_key]
        if datetime.now() - cached_at < CACHE_TTL:
            logger.info(f"Cache hit: {cache_key}")
            return result

    scraper = _get_scraper(sport)

    if sport == 'nba':
        (player_info, season_averages, season_totals,
         last_five_game_averages, opposing_team, individual_games) = scraper.getAllPlayerStats(player_name)
        result = {
            'sport': 'nba',
            'player_info': player_info,
            'season_averages': season_averages,
            'season_totals': season_totals,
            'last_five_game_averages': last_five_game_averages,
            'opposing_team': opposing_team,
            'individual_last_five_games': individual_games,
        }
    else:
        raw = scraper.get_player_stats(player_name)
        result = {'sport': sport, **raw}

    _stats_cache[cache_key] = (datetime.now(), result)
    return result
