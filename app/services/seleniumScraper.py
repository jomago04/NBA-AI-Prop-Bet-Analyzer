from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from app.utilities.timeConverter import TimeConverter
from app.utilities.nameFormat import NameFormat
from app.config.selenium_config import SeleniumConfig
from app.config.constants import ScraperConstants
from app.utilities.urlLoaders import UrlLoaders
from app.utilities.calculateDaysSinceLastGame import calculateDaysSinceLastGame        
from html import unescape

class SeleniumScraper:
    
    # Initializes the scraper on run
    def __init__(self):
        self.driver, self.wait = SeleniumConfig.initialize_driver()
        self.urlLoaders = UrlLoaders(self.driver)
        
    def __del__(self):
        SeleniumConfig.cleanup_driver(self.driver)
        
    # Gets all necessary urls for the player
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

 #FOR ALL FUNCTIONS THAT USE URLS, need to find a way to load pages only once so we can get all data on one load per page
    #this can be done by making functions that load the pages and call them before scraping the data
    #for example, 1. run player urls, 2. run main url, then run all functions that use main url, 3. run splits url, then run all functions that use splits url,.....
    # Gets the opposing team URL from the main player url (need to better optimize for loading pages only when needed)
    
    # USES MAIN URL
    def getOpposingTeamUrl(self):
        # Gets the opposing team from the main player url
        try:
            # Finds the opposing team key
            opposingTeamKey = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ScraperConstants.SELECTORS['OPPOSING_TEAM']))).text
            opposingTeamUrl = "https://www.basketball-reference.com/teams/" + opposingTeamKey + "/2025.html"
        except Exception as e:
            print(f"Error getting opposing team: {str(e)}")
            return None
        
        return opposingTeamUrl
    
    # USES MAIN URL
    def getPlayerInfo(self):
        try: 
            # Gets the player current position from the seasonal stats table
            seasonalTable = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table#per_game_stats')))
            seasonalRow = seasonalTable.find_elements(By.CSS_SELECTOR, 'tbody tr:not(.thead)')[-1]
            seasonalCells = seasonalRow.find_elements(By.TAG_NAME, 'td' )
            
            playerInfo = {
                'name': '',
                'age': seasonalCells[0].text,
                'position': seasonalCells[3].text,
                'team': '',
                'daysSinceLastGame': 0
            }
            
            # Gets the player name, team, and experience from the info div
            div = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div#meta')))
            
            # Gets the player name from the only h1 tag
            h1Name = div.find_element(By.TAG_NAME, 'h1').text
            playerInfo['name'] = h1Name
            
            # Gets all the p tags in the info div
            pTags = div.find_elements(By.TAG_NAME, 'p')

            # Loops through the p tags and adds only the team and experience to the playerInfo dictionary
            for p in pTags:
                if 'Team:' in p.text:
                    playerInfo['team'] = p.text.split(':')[1].strip()
            
            # Gets the days since last game from the last 5 games table
            fiveGameTable = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table#last5')))
            fiveGameRow = fiveGameTable.find_elements(By.CSS_SELECTOR, 'tbody tr:not(.thead)')[0]
            dateCell = fiveGameRow.find_elements(By.TAG_NAME, 'th')[0].text
            
            playerInfo['daysSinceLastGame'] = calculateDaysSinceLastGame(dateCell)
            
            return playerInfo   
        
        except Exception as e:
            print(f"Error getting player info: {str(e)}")
            return {}
        
    # USES GAMELOG URL
    def getPlayerFiveGameStats(self, playerName: str):
        try:
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
        
    # USES ADVANCED GAMELOG URL
    def getPlayerAdvancedFiveGameStats(self):
        try:
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
    
    # USES SPLITS URL
    def getPlayerCurrentSeasonTotalStats(self):
        try: 
            table = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table#splits')))
            
            seasonalRow = table.find_elements(By.CSS_SELECTOR, 'tbody tr:not(.thead)')[0]
            cells = seasonalRow.find_elements(By.TAG_NAME, 'td')
            
            currentSeasonTotalStats = {
                'gamesPlayed': int(cells[1].text),
                'gamesStarted': int(cells[2].text),
                'gamesStartedPercentage': float(int(cells[1].text) / int(cells[2].text)) * 100,
                
                'minutesPlayed': float(cells[3].text),
                
                'fieldGoals': float(cells[4].text),
                'fieldGoalAttempts': float(cells[5].text),
                'fieldGoalPercentage': float(int(cells[4].text) / int(cells[5].text)) * 100,
                
                'threePoints': float(cells[6].text),
                'threePointAttempts': float(cells[7].text),
                'threePointPercentage': float(int(cells[6].text) / int(cells[7].text)) * 100,
                
                'freeThrows': float(cells[8].text),
                'freeThrowAttempts': float(cells[9].text),
                'freeThrowPercentage': float(int(cells[8].text) / int(cells[9].text)) * 100,
                
                'offensiveRebounds': float(cells[10].text),
                'defensiveRebounds': float(float(cells[11].text) - float(cells[10].text)),
                'totalRebounds': float(cells[11].text),
                
                'assists': float(cells[12].text),
                'steals': float(cells[13].text),
                'blocks': float(cells[14].text),
                'turnovers': float(cells[15].text),
                
                'personalFouls': float(cells[16].text),
                'points': float(cells[17].text),
                'averageTrueShootingPercentage': float(cells[23].text) * 100,
                'averageUsagePercentage': float(cells[24].text),
                'averageOffensiveRating': float(cells[25].text),
                'averageDefensiveRating': float(cells[26].text)   
            }

            
            return currentSeasonTotalStats
        
        except Exception as e:
            print(f"Error retrieving current season total stats: {str(e)}")
            return {}
    
    # USES MAIN URL
    def getPlayerCurrentSeasonAverageStats(self):
        try:
            table = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table#per_game_stats')))
            
            seasonalRow = table.find_elements(By.CSS_SELECTOR, 'tbody tr:not(.thead)')[-1]
            cells = seasonalRow.find_elements(By.TAG_NAME, 'td' )
            
            currentSeasonAverageStats = {
                'averageGamesPlayed': float(cells[4].text),
                'averageGamesStarted': float(cells[5].text),
                'averageGamesStartedPercentage': float(float(cells[4].text) / float(cells[5].text)) * 100,
                
                'averageMinutesPlayed': float(cells[6].text),
                
                'averageFieldGoals': float(cells[7].text),
                'averageFieldGoalAttempts': float(cells[8].text),
                'averageFieldGoalPercentage': float(float(cells[7].text) / float(cells[8].text)) * 100,
                
                'averageThreePoints': float(cells[10].text),
                'averageThreePointAttempts': float(cells[11].text),
                'averageThreePointPercentage': float(float(cells[10].text) / float(cells[11].text)) * 100,
                
                'averageTwoPoints': float(cells[13].text),
                'averageTwoPointsAttempts': float(cells[14].text),
                'averageTwoPointPercentage': float(float(cells[13].text) / float(cells[14].text)) * 100,
                
                'averageEffectiveFieldGoalPercentage': float(cells[16].text) * 100,
                
                'averageFreeThrows': float(cells[17].text),
                'averageFreeThrowAttempts': float(cells[18].text),
                'averageFreeThrowPercentage': float(float(cells[17].text) / float(cells[18].text)) * 100,
                
                'averageOffensiveRebounds': float(cells[20].text),
                'averageDefensiveRebounds': float(cells[21].text),
                'averageTotalRebounds': float(cells[22].text),
                
                'averageAssists': float(cells[23].text),
                'averageSteals': float(cells[24].text),
                'averageBlocks': float(cells[25].text),
                'averageTurnovers': float(cells[26].text),
                
                'averagePoints': float(cells[27].text),
            }
            return currentSeasonAverageStats
        
        except Exception as e:
            print(f"Error retrieving current season average stats: {str(e)}")
            return {}
        
    def getOpposingTeamStats(self):
        try:
            opposingTeamInfoDiv = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div#meta')))
            # Find all spans and get the second one using index [1]
            opposingTeamName = opposingTeamInfoDiv.find_element(By.CSS_SELECTOR, 'h1').find_elements(By.TAG_NAME, 'span')[1].text
            
            
            # Gets the team and opponent table
            teamAndOpponentTable = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table#team_and_opponent')))
            
            # Gets the average opponent team per game row
            averageOpponentTeamPerGameRow = teamAndOpponentTable.find_elements(By.CSS_SELECTOR, 'tbody tr:not(.thead)')[1]
            # Gets the average opponent opponent team per game row
            averageOpponentOpponentTeamPerGameRow = teamAndOpponentTable.find_elements(By.CSS_SELECTOR, 'tbody tr:not(.thead)')[5]
            
            # Gets the cells in the average opponent team per game row
            averageOpponentTeamPerGameCells = averageOpponentTeamPerGameRow.find_elements(By.TAG_NAME, 'td')
            # Gets the cells in the average opponent opponent team per game row
            averageOpponentOpponentTeamPerGameCells = averageOpponentOpponentTeamPerGameRow.find_elements(By.TAG_NAME, 'td')
            
            opponentTeamMiscTable = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table#team_misc')))
            opponentTeamMiscRow = opponentTeamMiscTable.find_elements(By.CSS_SELECTOR, 'tbody tr:not(.thead)')[0]
            opponentTeamMiscCells = opponentTeamMiscRow.find_elements(By.TAG_NAME, 'td')
            
            opposingTeamStats = {
                'opponentTeamName': opposingTeamName,
                'opponentWins': int(opponentTeamMiscCells[0].text),
                'opponentLosses': int(opponentTeamMiscCells[1].text),
                'opponentWinPercentage': float(float(opponentTeamMiscCells[0].text) / (float(opponentTeamMiscCells[0].text) + float(opponentTeamMiscCells[1].text))) * 100,
                
                'opponentAverageFieldGoals': float(averageOpponentTeamPerGameCells[2].text),
                'opponentAverageFieldGoalsAttempted': float(averageOpponentTeamPerGameCells[3].text),
                'opponentAverageFieldGoalPercentage': float(float(averageOpponentTeamPerGameCells[2].text) / float(averageOpponentTeamPerGameCells[3].text)) * 100,
                
                'opponentAverageThreePoints': float(averageOpponentTeamPerGameCells[5].text),
                'opponentAverageThreePointsAttempted': float(averageOpponentTeamPerGameCells[6].text),
                'opponentAverageThreePointPercentage': float(float(averageOpponentTeamPerGameCells[5].text) / float(averageOpponentTeamPerGameCells[6].text)) * 100,
                
                'opponentAverageTwoPoints': float(averageOpponentTeamPerGameCells[8].text),
                'opponentAverageTwoPointsAttempted': float(averageOpponentTeamPerGameCells[9].text),
                'opponentAverageTwoPointPercentage': float(float(averageOpponentTeamPerGameCells[8].text) / float(averageOpponentTeamPerGameCells[9].text)) * 100,
                
                'opponentAverageFreeThrows': float(averageOpponentTeamPerGameCells[11].text),
                'opponentAverageFreeThrowAttempts': float(averageOpponentTeamPerGameCells[12].text),
                'opponentAverageFreeThrowPercentage': float(float(averageOpponentTeamPerGameCells[11].text) / float(averageOpponentTeamPerGameCells[12].text)) * 100,
                
                'opponentAverageOffensiveRebounds': float(averageOpponentTeamPerGameCells[14].text),
                'opponentAverageDefensiveRebounds': float(averageOpponentTeamPerGameCells[15].text),
                'opponentAverageTotalRebounds': float(averageOpponentTeamPerGameCells[16].text),
                
                'opponentAverageAssists': float(averageOpponentTeamPerGameCells[17].text),
                'opponentAverageSteals': float(averageOpponentTeamPerGameCells[18].text),
                'opponentAverageBlocks': float(averageOpponentTeamPerGameCells[19].text),
                'opponentAverageTurnovers': float(averageOpponentTeamPerGameCells[20].text),
                
                'opponentAveragePoints': float(averageOpponentTeamPerGameCells[22].text),
                
                'opponentOffensiveRating': float(opponentTeamMiscCells[8].text),
                'opponentDefensiveRating': float(opponentTeamMiscCells[9].text),
                'opponentPaceFactor': float(opponentTeamMiscCells[10].text),
                'opponentFreeThrowRate': float(opponentTeamMiscCells[11].text),
                'opponentThreePointRate': float(opponentTeamMiscCells[12].text),
                
                'opponentEffectiveFieldGoalPercentage': float(opponentTeamMiscCells[16].text) * 100,
                'opponentTurnoverPercentage': float(opponentTeamMiscCells[17].text),
                'opponentDefensiveReboundPercentage': float(opponentTeamMiscCells[18].text),
                'opponentFreeThrowRate': float(opponentTeamMiscCells[19].text) * 100,
                
                'opponentOpponentFieldGoals': float(averageOpponentOpponentTeamPerGameCells[2].text),
                'opponentOpponentFieldGoalsAttempted': float(averageOpponentOpponentTeamPerGameCells[3].text),
                'opponentOpponentFieldGoalPercentage': float(float(averageOpponentOpponentTeamPerGameCells[2].text) / float(averageOpponentOpponentTeamPerGameCells[3].text)) * 100,
                
                'opponentOpponentThreePoints': float(averageOpponentOpponentTeamPerGameCells[5].text),
                'opponentOpponentThreePointsAttempted': float(averageOpponentOpponentTeamPerGameCells[6].text),
                'opponentOpponentThreePointPercentage': float(float(averageOpponentOpponentTeamPerGameCells[5].text) / float(averageOpponentOpponentTeamPerGameCells[6].text)) * 100,
                
                'opponentOpponentTwoPoints': float(averageOpponentOpponentTeamPerGameCells[8].text),
                'opponentOpponentTwoPointsAttempted': float(averageOpponentOpponentTeamPerGameCells[9].text),
                'opponentOpponentTwoPointPercentage': float(float(averageOpponentOpponentTeamPerGameCells[8].text) / float(averageOpponentOpponentTeamPerGameCells[9].text)) * 100,
                
                'opponentOpponentFreeThrows': float(averageOpponentOpponentTeamPerGameCells[11].text),
                'opponentOpponentFreeThrowsAttempted': float(averageOpponentOpponentTeamPerGameCells[12].text),
                'opponentOpponentFreeThrowPercentage': float(float(averageOpponentOpponentTeamPerGameCells[11].text) / float(averageOpponentOpponentTeamPerGameCells[12].text)) * 100,
                
                'opponentOpponentOffensiveRebounds': float(averageOpponentOpponentTeamPerGameCells[14].text),
                'opponentOpponentDefensiveRebounds': float(averageOpponentOpponentTeamPerGameCells[15].text),
                'opponentOpponentTotalRebounds': float(averageOpponentOpponentTeamPerGameCells[16].text),

                'opponentOpponentAverageAssists': float(averageOpponentOpponentTeamPerGameCells[17].text),
                'opponentOpponentAverageSteals': float(averageOpponentOpponentTeamPerGameCells[18].text),
                'opponentOpponentAverageBlocks': float(averageOpponentOpponentTeamPerGameCells[19].text),
                'opponentOpponentAverageTurnovers': float(averageOpponentOpponentTeamPerGameCells[20].text),
                
                'opponentOpponentAveragePoints': float(averageOpponentOpponentTeamPerGameCells[22].text),
                
            }
            return opposingTeamStats
        
        except Exception as e:
            print(f"Error retrieving opposing team stats: {str(e)}")
            return {}
      
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
            'averageMinutesPlayed': float(sum(game.minutesPlayed for game in lastFiveGameStats) / numGames),
            
            'averageFieldGoals': float(sum(game.fieldGoals for game in lastFiveGameStats) / numGames),
            'averageFieldGoalAttempts': float(sum(game.fieldGoalAttempts for game in lastFiveGameStats) / numGames),
            'averageFieldGoalPercentage': float(sum(game.fieldGoalPercentage for game in lastFiveGameStats) / numGames),
            
            'averageThreePoints': float(sum(game.threePoints for game in lastFiveGameStats) / numGames),
            'averageThreePointAttempts': float(sum(game.threePointAttempts for game in lastFiveGameStats) / numGames),
            'averageThreePointPercentage': float(sum(game.threePointPercentage for game in lastFiveGameStats) / numGames),
            
            'averageFreeThrows': float(sum(game.freeThrows for game in lastFiveGameStats) / numGames),
            'averageFreeThrowAttempts': float(sum(game.freeThrowAttempts for game in lastFiveGameStats) / numGames),
            'averageFreeThrowPercentage': float(sum(game.freeThrowPercentage for game in lastFiveGameStats) / numGames),
            
            'averageOffensiveRebounds': float(sum(game.offensiveRebounds for game in lastFiveGameStats) / numGames),
            'averageDefensiveRebounds': float(sum(game.defensiveRebounds for game in lastFiveGameStats) / numGames),
            'averageTotalRebounds': float(sum(game.totalRebounds for game in lastFiveGameStats) / numGames),
            
            'averageAssists': float(sum(game.assists for game in lastFiveGameStats) / numGames),
            'averageSteals': float(sum(game.steals for game in lastFiveGameStats) / numGames),
            'averageBlocks': float(sum(game.blocks for game in lastFiveGameStats) / numGames),
            'averageTurnovers': float(sum(game.turnovers for game in lastFiveGameStats) / numGames),
            
            'averagePoints': float(sum(game.points for game in lastFiveGameStats) / numGames),
            'averageGameScore': float(sum(game.gameScore for game in lastFiveGameStats) / numGames),
            'averagePlusMinus': float(sum(game.plusMinus for game in lastFiveGameStats) / numGames),
            
            'averageTrueShootingPercentage': float(sum(game['trueShootingPercentage'] for game in advancedFiveGameStats) / numGames),
            'averageEffectiveFieldGoalPercentage': float(sum(game['effectiveFieldGoalPercentage'] for game in advancedFiveGameStats) / numGames),
            'averageUsagePercentage': float(sum(game['usagePercentage'] for game in advancedFiveGameStats) / numGames),
            'averageOffensiveRating': float(sum(game['offensiveRating'] for game in advancedFiveGameStats) / numGames),
            'averageDefensiveRating': float(sum(game['defensiveRating'] for game in advancedFiveGameStats) / numGames)
        }
        
        return averages