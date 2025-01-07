from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from app.utilities.timeConverter import TimeConverter
from app.utilities.nameFormat import NameFormat
from app.config.selenium_config import SeleniumConfig
from app.config.constants import ScraperConstants
from app.utilities.urlLoaders import UrlLoaders
from app.utilities.calculateDaysSinceLastGame import calculateDaysSinceLastGame  
from app.utilities.safeConvert import safe_convert
      
import unicodedata

class SeleniumScraper:
    
    # Initializes the scraper on run
    def __init__(self):
        self.driver, self.wait = SeleniumConfig.initialize_driver()
        self.urlLoaders = UrlLoaders(self.driver)
        
    def __del__(self):
        SeleniumConfig.cleanup_driver(self.driver)
        
    # Gets all necessary urls for the player
 

 #FOR ALL FUNCTIONS THAT USE URLS, need to find a way to load pages only once so we can get all data on one load per page
    #this can be done by making functions that load the pages and call them before scraping the data
    #for example, 1. run player urls, 2. run main url, then run all functions that use main url, 3. run splits url, then run all functions that use splits url,.....
    # Gets the opposing team URL from the main player url (need to better optimize for loading pages only when needed)
    
    def getPlayerCode(self, playerName: str):
        try:
            def normalizeName(name: str):
                currentYear = None
                if "(" in name:
                    year = name.split(")")[0].split("(")[1]
                    if "-" in year:
                        currentYear = year.split("-")[1].strip()
                    
                    
                name = name.split("(")[0].strip()
                normalizedName = unicodedata.normalize('NFKD', name)
                normalizedName = normalizedName.encode('ASCII', 'ignore').decode('ASCII')
                return normalizedName.lower(), currentYear
            
            splitPlayerName = playerName.split(" ")
            firstName, lastName = splitPlayerName[0], splitPlayerName[1]
            searchLink = f"https://www.basketball-reference.com/search/search.fcgi?search={firstName}+{lastName}"
            
            print(f"Searching URL: {searchLink}")
            self.driver.get(searchLink)
            
            playerSearchDiv = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div#players")))
            
            getEachSearchedPlayer = playerSearchDiv.find_elements(By.CSS_SELECTOR, "div.search-item")
            print(f"Found {len(getEachSearchedPlayer)} search results")
            
            for player in getEachSearchedPlayer:
                nameDiv = player.find_element(By.CSS_SELECTOR, "div.search-item-name")
                name = nameDiv.text.strip()
                normalizedName, currentYear = normalizeName(name)
                print(f"Comparing: '{normalizedName}' with '{normalizeName(playerName)[0]}'")
                
                if normalizedName == normalizeName(playerName)[0]:
                    urlDiv = player.find_element(By.CSS_SELECTOR, "div.search-item-url")
                    playerUrl = urlDiv.text.strip()
                    print(f"Found match! URL: {playerUrl}") 
                    playerCode = playerUrl[9:-5]
                    
                    return playerCode, currentYear
            
        except Exception as e:
            print(f"Error getting player code: {str(e)}")
            return None
            
    # Gets all necessary urls for the player
    def getPlayerUrl(self, playerName: str):
        try:
            playerCode, currentYear = self.getPlayerCode(playerName)
            
            mainPlayerUrl = f"{ScraperConstants.BASE_URL}/players/{playerCode}.html"
            splitsPlayerUrl = f"{ScraperConstants.BASE_URL}/players/{playerCode}/splits/{currentYear}"
            gamelogPlayerUrl = f"{ScraperConstants.BASE_URL}/players/{playerCode}/gamelog/{currentYear}"
            advancedGamelogPlayerUrl = f"{ScraperConstants.BASE_URL}/players/{playerCode}/gamelog-advanced/{currentYear}"
            
            return mainPlayerUrl, splitsPlayerUrl, gamelogPlayerUrl, advancedGamelogPlayerUrl
        
        except Exception as e:
            print(f"Error getting player url: {str(e)}")
            return None
    
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
            print(f"Attempting to get game stats for {playerName}")
            # Gets the table
            table = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table#pgl_basic')))
            print("Successfully found table")
            # Finds all rows in the table excluding the headers
            allRows = table.find_elements(By.CSS_SELECTOR, 'tbody tr:not(.thead)')
            print(f"Found {len(allRows)} rows")
            # Creates a list to store the last 5 game stats
            lastFiveGameStats = []
            
            # Counter for the number of rows processed
            processedRows = 0
            
            # Index of the last row in the table
            rowIndex = len(allRows) - 1
            
            # Loops through the last 5 rows
            while processedRows < 5 and rowIndex >= 0:
                row = allRows[rowIndex]
                try:
                    # Checks cell 7 to verify if the row is a game played by checking for 'Inactive' text
                    verifyRow = row.find_elements(By.TAG_NAME, 'td')[7]
                    if 'Inactive' in verifyRow.text:
                        print(f"Skipping inactive game at index {rowIndex}")
                        # If Inactive is found, decrement the row index and continue
                        rowIndex -= 1
                        continue
                    
                    # Finds all cells in the row
                    cells = row.find_elements(By.TAG_NAME, 'td')
                    
                    # Additional check to ensure the row has the correct number of cells
                    if len(cells) < 28:
                        print(f"Skipping row {rowIndex} - insufficient cells")
                        rowIndex -= 1
                        continue
                    
                    
                    
                    # Creates a dictionary to store the last 5 game stats to send to playerInfo.py
                    gameStats = {
                        'playerName': NameFormat.formatName(NameFormat.getNameParts(playerName)),
                        'opponent': cells[5].text,
                        'isAway': cells[4].text == '@',
                        'minutesPlayed': TimeConverter.convertTimeStringToFloat(cells[8].text or '0:00'),
                        
                        'fieldGoals': safe_convert(cells[9].text, int),
                        'fieldGoalAttempts': safe_convert(cells[10].text, int),
                        'fieldGoalPercentage': safe_convert(cells[11].text) * 100,
                        
                        'threePoints': safe_convert(cells[12].text, int),
                        'threePointAttempts': safe_convert(cells[13].text, int),
                        'threePointPercentage': safe_convert(cells[14].text) * 100,
                        
                        'freeThrows': safe_convert(cells[15].text, int),
                        'freeThrowAttempts': safe_convert(cells[16].text, int),
                        'freeThrowPercentage': safe_convert(cells[17].text) * 100,
                        
                        'offensiveRebounds': safe_convert(cells[18].text, int),
                        'defensiveRebounds': safe_convert(cells[19].text, int),
                        'totalRebounds': safe_convert(cells[20].text, int),
                        
                        'assists': safe_convert(cells[21].text, int),
                        'steals': safe_convert(cells[22].text, int),
                        'blocks': safe_convert(cells[23].text, int),
                        'turnovers': safe_convert(cells[24].text, int),
                        
                        'points': safe_convert(cells[26].text, int),
                        'gameScore': safe_convert(cells[27].text),
                        'plusMinus': safe_convert(cells[28].text, int)
                    }
                    # Adds the game stats to the list
                    lastFiveGameStats.append(gameStats)
                    
                    # Increments the processed rows counter
                    processedRows += 1
                    print(f"Successfully processed game {processedRows}")

                except (ValueError, IndexError) as e:
                    raise RuntimeError(f"Error processing game at index {rowIndex}: {str(e)}")
                
                # Decrements the row index to move to the previous row
                rowIndex -= 1
            
            print(f"Completed processing with {len(lastFiveGameStats)} games")
            print("Last Five Game Stats:", lastFiveGameStats)     
            return lastFiveGameStats
            
        except Exception as e:
            raise RuntimeError(f"Failure to retrieve last 5 game stats for {playerName}: {str(e)}")

        
    # USES ADVANCED GAMELOG URL
    def getPlayerAdvancedFiveGameStats(self):
        try:
            table = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table#pgl_advanced")))
            allRows = table.find_elements(By.CSS_SELECTOR, 'tbody tr:not(.thead)')
            
            # Creates a list to store the last 5 game stats
            advancedFiveGameStats = []
            processedRows = 0
            rowIndex = len(allRows) - 1
            
            while processedRows < 5 and rowIndex >= 0:
                row = allRows[rowIndex]
                try:
                    verifyRow = row.find_elements(By.TAG_NAME, 'td')[7] # Checks td 7 to verify if the row is a game played
                    if 'Inactive' in verifyRow.text:
                        print(f"Skipping inactive game at index {rowIndex}")
                        rowIndex -= 1
                        continue
                    
                    cells = row.find_elements(By.TAG_NAME, 'td')
                    if len(cells) < 20:
                        print(f"Skipping row {rowIndex} - insufficient cells")
                        rowIndex -= 1
                        continue
                
                    gameStats = {
                        'trueShootingPercentage': safe_convert(cells[9].text, float) * 100,
                        'effectiveFieldGoalPercentage': safe_convert(cells[10].text, float) * 100,
                        'usagePercentage': safe_convert(cells[18].text, float),
                        'offensiveRating': safe_convert(cells[19].text, float),
                        'defensiveRating': safe_convert(cells[20].text, float)
                    }
                    advancedFiveGameStats.append(gameStats)
                    processedRows += 1
                    print(f"Successfully processed advanced game {processedRows}")
                
            
                except (ValueError, IndexError) as e:
                    print(f"Error processing game at index {rowIndex}: {str(e)}")\
                        
            rowIndex -= 1
            
            print("Advanced Stats:", advancedFiveGameStats)   
            return advancedFiveGameStats
        
        except Exception as e:
            raise RuntimeError(f"Failure to retrieve last 5 game advanced stats: {str(e)}")
    
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