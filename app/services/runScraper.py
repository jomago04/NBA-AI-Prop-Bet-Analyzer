from app.services.scrapingLogic import SeleniumScraper
from app.models.playerInfo import PlayerIndividualFiveGameStats, PlayerLastFiveGameStats, PlayerCurrentSeasonTotalStats, PlayerCurrentSeasonAverageStats, PlayerInfo, PlayerOpposingTeamStats
from app.utilities.urlLoaders import UrlLoaders
import logging

logger = logging.getLogger(__name__)

class GetNBAPlayerStats:
    def __init__(self):
        self.scraper = SeleniumScraper()
        self.urlLoaders = UrlLoaders(self.scraper.driver)

    def __del__(self):
        if hasattr(self, 'scraper'):
            self.scraper.__del__()

    def getAllPlayerStats(self, playerName):
        try:
            # Gets the player urls
            mainUrl, splitsUrl, gamelogUrl, advancedGamelogUrl = self.scraper.getPlayerUrl(playerName)
            
            # Initializes the url loaders
            urlLoaders = UrlLoaders(self.scraper.driver)
            
            
            ## MAIN URL TASKS ##
            urlLoaders.loadMainUrl(mainUrl)
            # gets opposing team url
            opposingTeamUrl = self.scraper.getOpposingTeamUrl()
            # gets current season average stats
            currentSeasonAverageStats = PlayerCurrentSeasonAverageStats(**self.scraper.getPlayerCurrentSeasonAverageStats())
            # gets player info
            playerInfo = PlayerInfo(**self.scraper.getPlayerInfo())
            
            ## SPLITS URL TASKS ##
            urlLoaders.loadSplitsUrl(splitsUrl)
            # gets current season total stats
            currentSeasonTotalStats = PlayerCurrentSeasonTotalStats(**self.scraper.getPlayerCurrentSeasonTotalStats())
            
            # GAMELOG URL TASKS
            urlLoaders.loadGamelogUrl(gamelogUrl)
            # gets player stats for last 5 games
            playerFiveGameStats = self.scraper.getPlayerFiveGameStats(playerName)
            
            ## ADVANCED GAMELOG URL TASKS ##
            urlLoaders.loadAdvancedGamelogUrl(advancedGamelogUrl)
            # gets advanced player stats for last 5 games
            advancedPlayerFiveGameStats = self.scraper.getPlayerAdvancedFiveGameStats()
            
            # COMBINING STATS (for last 5 games)
            combinedStats = [
                {**default, **advanced} for default, advanced in zip(playerFiveGameStats, advancedPlayerFiveGameStats)
            ]
            playerIndividualFiveGameStats = [PlayerIndividualFiveGameStats(**game) for game in combinedStats]
            
            playerLastFiveGameAverages = self.scraper.calculatePlayerFiveGameAverages(playerIndividualFiveGameStats, advancedPlayerFiveGameStats)
            playerLastFiveGameStats = PlayerLastFiveGameStats(**playerLastFiveGameAverages)
            # OPPOSING TEAM WORK 
            urlLoaders.loadOpposingTeamUrl(opposingTeamUrl)
            opposingTeamStats = PlayerOpposingTeamStats(**self.scraper.getOpposingTeamStats())
                
                
            logger.info(f"Scraping complete for {playerName}")
            return playerInfo, currentSeasonAverageStats, currentSeasonTotalStats, playerLastFiveGameStats, opposingTeamStats, playerIndividualFiveGameStats

        except Exception as e:
            logger.error(f"Error scraping stats for {playerName}: {str(e)}")
            return None, None, None, None, None, None
