from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from app.utilities.timeConverter import TimeConverter
from app.utilities.nameFormat import NameFormat
from app.config.selenium_config import SeleniumConfig
from app.config.constants import ScraperConstants

class SeleniumScraper:
    # Initializes the scraper on run
    def __init__(self):
        self.driver, self.wait = SeleniumConfig.initialize_driver()
        
    def __del__(self):
        SeleniumConfig.cleanup_driver(self.driver)

    def getPlayerUrl(playerName: str):
        # Splits player name into first and last name
        nameParts = NameFormat.getNameParts(playerName)
        # Checks if player name has both first and last name to avoid errors
        if len(nameParts) < 2:
            return "Please enter both first and last name"
        # [-1] grabs last item in list, [0] grabs first item in list
        lastName, firstName = nameParts[-1], nameParts[0]
        # [:1] grabs first letter of last name, [:5] grabs first 5 letters of last name, [:2] grabs first 2 letters of first name
        mainPlayerUrl = f"{ScraperConstants.BASE_URL}/players/{lastName[:1]}/{lastName[:5]}{firstName[:2]}01.html"
        splitsPlayerUrl = f"{ScraperConstants.BASE_URL}/players/{lastName[:1]}/{lastName[:5]}{firstName[:2]}01/splits/2025" # TODO: Make way to get current year
        gamelogPlayerUrl = f"{ScraperConstants.BASE_URL}/players/{lastName[:1]}/{lastName[:5]}{firstName[:2]}01/gamelog/2025"
        advancedGamelogPlayerUrl = f"{ScraperConstants.BASE_URL}/players/{lastName[:1]}/{lastName[:5]}{firstName[:2]}01/gamelog-advanced/2025"
        
        return mainPlayerUrl, splitsPlayerUrl, gamelogPlayerUrl, advancedGamelogPlayerUrl

    def getOpposingTeamUrl(self, mainPlayerUrl: str):
        # Gets the opposing team from the main player url
        try:
            # Loads the main player url
            self.driver.set_page_load_timeout(10)
            self.driver.get(mainPlayerUrl)
            # Finds the opposing team key
            opposingTeamKey = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ScraperConstants.SELECTORS['OPPOSING_TEAM'])))
            
        except Exception as e:
            print(f"Error getting opposing team: {str(e)}")
            return None
        
        return opposingTeamKey.text
    
    
    def getPlayerFiveGameStats(self, gamelogPlayerUrl: str, playerName: str):
        try:
            # Loads the gamelog player url
            self.driver.get(gamelogPlayerUrl)
            # Finds the table
            table = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ScraperConstants.SELECTORS['GAME_TABLE'])))
            # Finds the last 5 rows while excluding the headers
            rows = table.find_elements(By.CSS_SELECTOR, ScraperConstants.SELECTORS['LAST_FIVE_ROWS'])[-5:] 
            
            # Creates a list to store the last 5 game stats
            lastFiveGameStats = []
            
            # Loops through the last 5 rows
            for i, row in enumerate(rows, 1):
                try:
                    # Finds the cells in the row
                    cells = row.find_elements(By.TAG_NAME, "td")
                    
                    # Creates a dictionary to store the last 5 game stats to send to playerInfo.py
                    gameStats = {
                        'playerName': NameFormat.formatName(NameFormat.getNameParts(playerName)),
                        'opponent': row.find_elements(By.TAG_NAME, 'td')[5].text,  # Opponent team
                        'isAway': row.find_elements(By.TAG_NAME, 'td')[4].text == '@',  # Location
                        'minutesPlayed': TimeConverter.convertTimeStringToFloat(cells[8].text),
                        
                        'fieldGoals': int(cells[9].text),
                        'fieldGoalAttempts': int(cells[10].text),
                        'fieldGoalPercentage': float(cells[11].text) * 100,
                        
                        'threePoints': int(cells[12].text),
                        'threePointAttempts': int(cells[13].text),
                        'threePointPercentage': float(cells[14].text) * 100,
                            
                        'freeThrows': int(cells[15].text),
                        'freeThrowAttempts': int(cells[16].text),
                        'freeThrowPercentage': float(cells[17].text) * 100,
                        
                        'offensiveRebounds': int(cells[18].text),
                        'defensiveRebounds': int(cells[19].text),
                        'totalRebounds': int(cells[20].text),
                        
                        'assists': int(cells[21].text),
                        'steals': int(cells[22].text),
                        'blocks': int(cells[23].text),
                        'turnovers': int(cells[24].text),
                        
                        'points': int(cells[26].text),
                        'gameScore': float(cells[27].text),
                        'plusMinus': int(cells[28].text)
                    }
                    # Adds the game stats to the list
                    lastFiveGameStats.append(gameStats)
                    
                except (ValueError, IndexError) as e:
                    print(f"Error processing game {i}: {str(e)}")
                    continue
                
            return lastFiveGameStats
            
        except Exception as e:
            print(f"Error retrieving game stats: {str(e)}")
            return []
        
    def getPlayerAdvancedFiveGameStats(self, advancedGamelogPlayerUrl: str):
        try:
            self.driver.get(advancedGamelogPlayerUrl)
            table = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#pgl_advanced")))
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr:not(.thead)")[-5:]
            
            advancedFiveGameStats = []
            
            for i, row in enumerate(rows, 1):
                cells = row.find_elements(By.TAG_NAME, "td") 
                
                gameStats = {
                    'trueShootingPercentage': float(cells[9].text) * 100,
                    'effectiveFieldGoalPercentage': float(cells[10].text) * 100,
                    'usagePercentage': float(cells[18].text),
                    'offensiveRating': float(cells[19].text),
                    'defensiveRating': float(cells[20].text)
                }
                advancedFiveGameStats.append(gameStats)
                
            return advancedFiveGameStats
        
        except Exception as e:
            print(f"Error retrieving advanced game stats: {str(e)}")
            return []
        
    def calculatePlayerFiveGameAverages(self, lastFiveGameStats: list, advancedFiveGameStats: list):
        # Checks if the last 5 game stats is empty
        if not lastFiveGameStats:
            return {
                'averageMinutesPlayed': 0.0,
                
                'averageFieldGoals': 0.0,
                'averageFieldGoalAttempts': 0.0,
                'averageFieldGoalPercentage': 0.0,
                
                
                'averageThreePoints': 0.0,
                'averageThreePointAttempts': 0.0,
                'averageThreePointPercentage': 0.0,
                
                'averageFreeThrows': 0.0,
                'averageFreeThrowAttempts': 0.0,
                'averageFreeThrowPercentage': 0.0,
                
                'averageOffensiveRebounds': 0.0,
                'averageDefensiveRebounds': 0.0,
                'averageTotalRebounds': 0.0,
                
                'averageAssists': 0.0,
                'averageSteals': 0.0,
                'averageBlocks': 0.0,
                'averageTurnovers': 0.0,
                
                'averagePoints': 0.0,
                'averageGameScore': 0.0,
                'averagePlusMinus': 0.0,
                
                'averageTrueShootingPercentage': 0.0,
                'averageEffectiveFieldGoalPercentage': 0.0,
                'averageUsagePercentage': 0.0,
                'averageOffensiveRating': 0.0,
                'averageDefensiveRating': 0.0
            }
        
        # Grabs the number of games
        numGames = len(lastFiveGameStats)
        # Calculates the averages
        averages = {
            'averageMinutesPlayed': float(sum(game['minutesPlayed'] for game in lastFiveGameStats) / numGames),
            
            'averageFieldGoals': float(sum(game['fieldGoals'] for game in lastFiveGameStats) / numGames),
            'averageFieldGoalAttempts': float(sum(game['fieldGoalAttempts'] for game in lastFiveGameStats) / numGames),
            'averageFieldGoalPercentage': float(sum(game['fieldGoalPercentage'] for game in lastFiveGameStats) / numGames),
            
            'averageThreePoints': float(sum(game['threePoints'] for game in lastFiveGameStats) / numGames),
            'averageThreePointAttempts': float(sum(game['threePointAttempts'] for game in lastFiveGameStats) / numGames),
            'averageThreePointPercentage': float(sum(game['threePointPercentage'] for game in lastFiveGameStats) / numGames),
            
            'averageFreeThrows': float(sum(game['freeThrows'] for game in lastFiveGameStats) / numGames),
            'averageFreeThrowAttempts': float(sum(game['freeThrowAttempts'] for game in lastFiveGameStats) / numGames),
            'averageFreeThrowPercentage': float(sum(game['freeThrowPercentage'] for game in lastFiveGameStats) / numGames),
            
            'averageOffensiveRebounds': float(sum(game['offensiveRebounds'] for game in lastFiveGameStats) / numGames),
            'averageDefensiveRebounds': float(sum(game['defensiveRebounds'] for game in lastFiveGameStats) / numGames),
            'averageTotalRebounds': float(sum(game['totalRebounds'] for game in lastFiveGameStats) / numGames),
            
            'averageAssists': float(sum(game['assists'] for game in lastFiveGameStats) / numGames),
            'averageSteals': float(sum(game['steals'] for game in lastFiveGameStats) / numGames),
            'averageBlocks': float(sum(game['blocks'] for game in lastFiveGameStats) / numGames),
            'averageTurnovers': float(sum(game['turnovers'] for game in lastFiveGameStats) / numGames),
            
            'averagePoints': float(sum(game['points'] for game in lastFiveGameStats) / numGames),
            'averageGameScore': float(sum(game['gameScore'] for game in lastFiveGameStats) / numGames),
            'averagePlusMinus': float(sum(game['plusMinus'] for game in lastFiveGameStats) / numGames),
            
            'averageTrueShootingPercentage': float(sum(game['trueShootingPercentage'] for game in advancedFiveGameStats) / numGames),
            'averageEffectiveFieldGoalPercentage': float(sum(game['effectiveFieldGoalPercentage'] for game in advancedFiveGameStats) / numGames),
            'averageUsagePercentage': float(sum(game['usagePercentage'] for game in advancedFiveGameStats) / numGames),
            'averageOffensiveRating': float(sum(game['offensiveRating'] for game in advancedFiveGameStats) / numGames),
            'averageDefensiveRating': float(sum(game['defensiveRating'] for game in advancedFiveGameStats) / numGames)
        }
        
        return averages
        

