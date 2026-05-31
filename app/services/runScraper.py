from app.services.scrapingLogic import SeleniumScraper
from app.models.playerInfo import (
    PlayerIndividualFiveGameStats, PlayerLastFiveGameStats,
    PlayerCurrentSeasonTotalStats, PlayerCurrentSeasonAverageStats,
    PlayerInfo, PlayerOpposingTeamStats
)
from app.utilities.urlLoaders import UrlLoaders
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

CACHE_TTL = timedelta(minutes=10)
_stats_cache: dict = {}


class GetNBAPlayerStats:
    def __init__(self):
        self.scraper = SeleniumScraper()
        self.urlLoaders = UrlLoaders(self.scraper.driver)

    def __del__(self):
        if hasattr(self, 'scraper'):
            self.scraper.__del__()

    def getAllPlayerStats(self, playerName: str):
        cache_key = playerName.lower().strip()
        if cache_key in _stats_cache:
            cached_at, result = _stats_cache[cache_key]
            if datetime.now() - cached_at < CACHE_TTL:
                logger.info(f"Cache hit for '{playerName}' (cached {int((datetime.now() - cached_at).total_seconds())}s ago)")
                return result

        try:
            mainUrl, splitsUrl, gamelogUrl, advancedGamelogUrl = self.scraper.getPlayerUrl(playerName)

            urlLoaders = UrlLoaders(self.scraper.driver)

            urlLoaders.loadMainUrl(mainUrl)
            opposingTeamUrl = self.scraper.getOpposingTeamUrl()
            currentSeasonAverageStats = PlayerCurrentSeasonAverageStats(**self.scraper.getPlayerCurrentSeasonAverageStats())
            playerInfo = PlayerInfo(**self.scraper.getPlayerInfo())

            urlLoaders.loadSplitsUrl(splitsUrl)
            currentSeasonTotalStats = PlayerCurrentSeasonTotalStats(**self.scraper.getPlayerCurrentSeasonTotalStats())

            urlLoaders.loadGamelogUrl(gamelogUrl)
            playerFiveGameStats = self.scraper.getPlayerFiveGameStats(playerName)

            urlLoaders.loadAdvancedGamelogUrl(advancedGamelogUrl)
            advancedPlayerFiveGameStats = self.scraper.getPlayerAdvancedFiveGameStats()

            combinedStats = [
                {**basic, **advanced}
                for basic, advanced in zip(playerFiveGameStats, advancedPlayerFiveGameStats)
            ]
            playerIndividualFiveGameStats = [PlayerIndividualFiveGameStats(**game) for game in combinedStats]

            playerLastFiveGameAverages = self.scraper.calculatePlayerFiveGameAverages(
                playerIndividualFiveGameStats, advancedPlayerFiveGameStats
            )
            playerLastFiveGameStats = PlayerLastFiveGameStats(**playerLastFiveGameAverages)

            urlLoaders.loadOpposingTeamUrl(opposingTeamUrl)
            opposingTeamStats = PlayerOpposingTeamStats(**self.scraper.getOpposingTeamStats())

            logger.info(f"Scraping complete for '{playerName}'")
            result = (
                playerInfo,
                currentSeasonAverageStats,
                currentSeasonTotalStats,
                playerLastFiveGameStats,
                opposingTeamStats,
                playerIndividualFiveGameStats,
            )
            _stats_cache[cache_key] = (datetime.now(), result)
            return result

        except Exception as e:
            logger.error(f"Error scraping stats for '{playerName}': {str(e)}")
            return None, None, None, None, None, None
