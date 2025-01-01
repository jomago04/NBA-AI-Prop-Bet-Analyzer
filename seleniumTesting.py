from app.services.seleniumScraper import SeleniumScraper
from app.models.playerInfo import PlayerLastFiveGameStats, PlayerIndividualFiveGameStats, PlayerCurrentSeasonTotalStats, PlayerCurrentSeasonAverageStats, PlayerInfo, PlayerOpposingTeamStats
from app.utilities.timeConverter import TimeConverter
from app.utilities.urlLoaders import UrlLoaders
import time
        
def testScraper(playerName):
    scraper = SeleniumScraper()
    try:
        # Test 1: Get player URLs
        print("\n=== Testing Player URL Generation ===")
        mainUrl, splitsUrl, gamelogUrl, advancedGamelogUrl = SeleniumScraper.getPlayerUrl(playerName)
        print(f"Main URL: {mainUrl}")
        print(f"Splits URL: {splitsUrl}")
        print(f"Gamelog URL: {gamelogUrl}")
        print(f"Advanced Gamelog URL: {advancedGamelogUrl}")
        
        urlLoaders = UrlLoaders(scraper.driver)
        print("Scraping player stats...")
        
        
        ## MAIN URL TASKS ##
        urlLoaders.loadMainUrl(mainUrl)
        
        # gets opposing team url
        opposingTeamUrl = scraper.getOpposingTeamUrl()
        
        # gets current season average stats
        currentSeasonAverageStats = scraper.getPlayerCurrentSeasonAverageStats()
        if not currentSeasonAverageStats:
            print("No data returned for current season average stats.")
            return
        averageStats = PlayerCurrentSeasonAverageStats(**currentSeasonAverageStats)
        
        # gets player info
        playerInfo = scraper.getPlayerInfo()
        if not playerInfo:
            print("No data returned for player info.")
            return
        playerInfo = PlayerInfo(**playerInfo)
        
        ## SPLITS URL TASKS ##
        urlLoaders.loadSplitsUrl(splitsUrl)
        # gets current season total stats
        currentSeasonTotalStats = scraper.getPlayerCurrentSeasonTotalStats()
        if not currentSeasonTotalStats:
            print("No data returned for current season total stats.")
            return
        
        totalStats = PlayerCurrentSeasonTotalStats(**currentSeasonTotalStats) 
        
        # GAMELOG URL TASKS
        urlLoaders.loadGamelogUrl(gamelogUrl)
        # gets player stats for last 5 games
        playerFiveGameStats = scraper.getPlayerFiveGameStats(playerName)

        ## ADVANCED GAMELOG URL TASKS ##
        urlLoaders.loadAdvancedGamelogUrl(advancedGamelogUrl)
        # gets advanced player stats for last 5 games
        advancedPlayerFiveGameStats = scraper.getPlayerAdvancedFiveGameStats()
        
        # COMBINING STATS (for last 5 games)
        combinedStats = [
            {**default, **advanced} for default, advanced in zip(playerFiveGameStats, advancedPlayerFiveGameStats)
        ]
        
        individualGames = [PlayerIndividualFiveGameStats(**game) for game in combinedStats]
        
        # OPPOSING TEAM WORK 
        urlLoaders.loadOpposingTeamUrl(opposingTeamUrl)
        
        opposingTeamStats = scraper.getOpposingTeamStats()
        if not opposingTeamStats:
            print("No data returned for opposing team stats.")
            return
        opposingTeamStats = PlayerOpposingTeamStats(**opposingTeamStats)
            
        print("scraping complete")
        
        time.sleep(2)
        
        ### DISPLAYING STATS ###        
        print("\n=== Testing Opposing Team URL ===")
        print(f"Opposing Team URL: {opposingTeamUrl}")
        
        print("\n=== Player Info ===")
        print(f"Name: {playerInfo.name}")
        print(f"Team: {playerInfo.team}")
        print(f"Position: {playerInfo.position}")
        print(f"Age: {playerInfo.age}")
        print(f"Days Since Last Game: {playerInfo.daysSinceLastGame}")
        

        print("\n=== Individual Game Stats ===")
        for i, game in enumerate(individualGames, 1):
            
            # Display individual game stats
            locationText = "@ " if game.isAway else "vs "
            print(f"\nGame {i} ({game.playerName} {locationText}{game.opponent}):")
            print(f"Minutes: {TimeConverter.convertTimeFloatToString(game.minutesPlayed)}")
            print(f"Field Goals: {game.fieldGoals}/{game.fieldGoalAttempts} ({game.fieldGoalPercentage:.1f}%)")
            print(f"Three Points: {game.threePoints}/{game.threePointAttempts} ({game.threePointPercentage:.1f}%)")
            print(f"Free Throws: {game.freeThrows}/{game.freeThrowAttempts} ({game.freeThrowPercentage:.1f}%)")
            print(f"Rebounds: {game.totalRebounds} (O: {game.offensiveRebounds}, D: {game.defensiveRebounds})")
            print(f"Assists: {game.assists}")
            print(f"Steals: {game.steals}")
            print(f"Blocks: {game.blocks}")
            print(f"Turnovers: {game.turnovers}")
            print(f"Points: {game.points}")
            print(f"Game Score: {game.gameScore:.1f}")
            print(f"Plus/Minus: {game.plusMinus}")
            print(f"True Shooting %: {game.trueShootingPercentage:.1f}%")
            print(f"eFG%: {game.effectiveFieldGoalPercentage:.1f}%")
            print(f"Usage %: {game.usagePercentage:.1f}%")
            print(f"Offensive Rating: {game.offensiveRating:.1f}")
            print(f"Defensive Rating: {game.defensiveRating:.1f}")
            
                    # Calculate averages
        averages = scraper.calculatePlayerFiveGameAverages(playerFiveGameStats, advancedPlayerFiveGameStats)
        playerAverages = PlayerLastFiveGameStats(**averages)
        
        # Display averages
        print("\n=== Five Game Averages ===")
        print(f"Average Minutes: {TimeConverter.convertTimeFloatToString(playerAverages.averageMinutesPlayed)}")
        print(f"Average Field Goals: {playerAverages.averageFieldGoals:.1f}/{playerAverages.averageFieldGoalAttempts:.1f} ({playerAverages.averageFieldGoalPercentage:.1f}%)")
        print(f"Average Three Points: {playerAverages.averageThreePoints:.1f}/{playerAverages.averageThreePointAttempts:.1f} ({playerAverages.averageThreePointPercentage:.1f}%)")
        print(f"Average Free Throws: {playerAverages.averageFreeThrows:.1f}/{playerAverages.averageFreeThrowAttempts:.1f} ({playerAverages.averageFreeThrowPercentage:.1f}%)")
        print(f"Average Rebounds: {playerAverages.averageTotalRebounds:.1f} (O: {playerAverages.averageOffensiveRebounds:.1f}, D: {playerAverages.averageDefensiveRebounds:.1f})")
        print(f"Average Assists: {playerAverages.averageAssists:.1f}")
        print(f"Average Steals: {playerAverages.averageSteals:.1f}")
        print(f"Average Blocks: {playerAverages.averageBlocks:.1f}")
        print(f"Average Turnovers: {playerAverages.averageTurnovers:.1f}")
        print(f"Average Points: {playerAverages.averagePoints:.1f}")
        print(f"Average Game Score: {playerAverages.averageGameScore:.1f}")
        print(f"Average Plus/Minus: {playerAverages.averagePlusMinus:.1f}")
        print(f"Average True Shooting %: {playerAverages.averageTrueShootingPercentage:.1f}%")
        print(f"Average eFG%: {playerAverages.averageEffectiveFieldGoalPercentage:.1f}%")
        print(f"Average Usage %: {playerAverages.averageUsagePercentage:.1f}%")
        print(f"Average Offensive Rating: {playerAverages.averageOffensiveRating:.1f}")
        print(f"Average Defensive Rating: {playerAverages.averageDefensiveRating:.1f}")
        
        print("\n=== Current Season Total Stats ===")
        print(f"Games Played: {totalStats.gamesPlayed}")
        print(f"Games Started: {totalStats.gamesStarted}")
        print(f"Games Started %: {totalStats.gamesStartedPercentage:.1f}%")
        print(f"Minutes Played: {totalStats.minutesPlayed}")
        print(f"Field Goals: {totalStats.fieldGoals:.1f}/{totalStats.fieldGoalAttempts:.1f} ({totalStats.fieldGoalPercentage:.1f}%)")
        print(f"Three Points: {totalStats.threePoints:.1f}/{totalStats.threePointAttempts:.1f} ({totalStats.threePointPercentage:.1f}%)")
        print(f"Free Throws: {totalStats.freeThrows:.1f}/{totalStats.freeThrowAttempts:.1f} ({totalStats.freeThrowPercentage:.1f}%)")
        print(f"Offensive Rebounds: {totalStats.offensiveRebounds:.1f}")
        print(f"Defensive Rebounds: {totalStats.defensiveRebounds:.1f}")
        print(f"Total Rebounds: {totalStats.totalRebounds:.1f}")
        print(f"Assists: {totalStats.assists:.1f}")
        print(f"Steals: {totalStats.steals:.1f}")
        print(f"Blocks: {totalStats.blocks:.1f}")
        print(f"Turnovers: {totalStats.turnovers:.1f}")
        print(f"Points: {totalStats.points:.1f}")
        print(f"Personal Fouls: {totalStats.personalFouls:.1f}")
        
        print("\n=== Current Season Average Stats ===")
        print(f"Average Minutes Played: {averageStats.averageMinutesPlayed:.1f}")
        print(f"Average Field Goals: {averageStats.averageFieldGoals:.1f}/{averageStats.averageFieldGoalAttempts:.1f} ({averageStats.averageFieldGoalPercentage:.1f}%)")
        print(f"Average Three Points: {averageStats.averageThreePoints:.1f}/{averageStats.averageThreePointAttempts:.1f} ({averageStats.averageThreePointPercentage:.1f}%)")
        print(f"Average Two Points: {averageStats.averageTwoPoints:.1f}/{averageStats.averageTwoPointsAttempts:.1f} ({averageStats.averageTwoPointPercentage:.1f}%)")
        print(f"Average Effective Field Goal Percentage: {averageStats.averageEffectiveFieldGoalPercentage:.1f}%")
        print(f"Average Free Throws: {averageStats.averageFreeThrows:.1f}/{averageStats.averageFreeThrowAttempts:.1f} ({averageStats.averageFreeThrowPercentage:.1f}%)")
        print(f"Average Offensive Rebounds: {averageStats.averageOffensiveRebounds:.1f}")
        print(f"Average Defensive Rebounds: {averageStats.averageDefensiveRebounds:.1f}")
        print(f"Average Total Rebounds: {averageStats.averageTotalRebounds:.1f}")
        print(f"Average Assists: {averageStats.averageAssists:.1f}")
        print(f"Average Steals: {averageStats.averageSteals:.1f}")
        print(f"Average Blocks: {averageStats.averageBlocks:.1f}")
        print(f"Average Turnovers: {averageStats.averageTurnovers:.1f}")
        print(f"Average Points: {averageStats.averagePoints:.1f}")
        print(f"Average True Shooting %: {totalStats.averageTrueShootingPercentage:.1f}%")
        print(f"Average Usage %: {totalStats.averageUsagePercentage:.1f}%")
        print(f"Average Offensive Rating: {totalStats.averageOffensiveRating:.1f}")
        print(f"Average Defensive Rating: {totalStats.averageDefensiveRating:.1f}")
        
        print("\n=== Opposing Team Stats ===")
        print(f"Opponent Team Name: {opposingTeamStats.opponentTeamName}")
        print(f"Opponent Wins: {opposingTeamStats.opponentWins}")
        print(f"Opponent Losses: {opposingTeamStats.opponentLosses}")
        print(f"Opponent Win Percentage: {opposingTeamStats.opponentWinPercentage:.1f}%")
        print(f"Opponent Average Field Goals: {opposingTeamStats.opponentAverageFieldGoals:.1f}/{opposingTeamStats.opponentAverageFieldGoalsAttempted:.1f} ({opposingTeamStats.opponentAverageFieldGoalPercentage:.1f}%)")
        print(f"Opponent Average Three Points: {opposingTeamStats.opponentAverageThreePoints:.1f}/{opposingTeamStats.opponentAverageThreePointsAttempted:.1f} ({opposingTeamStats.opponentAverageThreePointPercentage:.1f}%)")
        print(f"Opponent Average Two Points: {opposingTeamStats.opponentAverageTwoPoints:.1f}/{opposingTeamStats.opponentAverageTwoPointsAttempted:.1f} ({opposingTeamStats.opponentAverageTwoPointPercentage:.1f}%)")
        print(f"Opponent Average Free Throws: {opposingTeamStats.opponentAverageFreeThrows:.1f}/{opposingTeamStats.opponentAverageFreeThrowAttempts:.1f} ({opposingTeamStats.opponentAverageFreeThrowPercentage:.1f}%)")
        print(f"Opponent Average Offensive Rebounds: {opposingTeamStats.opponentAverageOffensiveRebounds:.1f}")
        print(f"Opponent Average Defensive Rebounds: {opposingTeamStats.opponentAverageDefensiveRebounds:.1f}")
        print(f"Opponent Average Total Rebounds: {opposingTeamStats.opponentAverageTotalRebounds:.1f}")
        print(f"Opponent Average Assists: {opposingTeamStats.opponentAverageAssists:.1f}")
        print(f"Opponent Average Steals: {opposingTeamStats.opponentAverageSteals:.1f}")
        print(f"Opponent Average Blocks: {opposingTeamStats.opponentAverageBlocks:.1f}")
        print(f"Opponent Average Turnovers: {opposingTeamStats.opponentAverageTurnovers:.1f}")
        print(f"Opponent Average Points: {opposingTeamStats.opponentAveragePoints:.1f}")
        print(f"Opponent Offensive Rating: {opposingTeamStats.opponentOffensiveRating:.1f}")
        print(f"Opponent Defensive Rating: {opposingTeamStats.opponentDefensiveRating:.1f}")
        print(f"Opponent Pace Factor: {opposingTeamStats.opponentPaceFactor:.1f}")
        print(f"Opponent Free Throw Rate: {opposingTeamStats.opponentFreeThrowRate:.1f}")
        print(f"Opponent Three Point Rate: {opposingTeamStats.opponentThreePointRate:.1f}")
        print(f"Opponent Effective Field Goal Percentage: {opposingTeamStats.opponentEffectiveFieldGoalPercentage:.1f}%")
        print(f"Opponent Turnover Percentage: {opposingTeamStats.opponentTurnoverPercentage:.1f}%")
        print(f"Opponent Defensive Rebound Percentage: {opposingTeamStats.opponentDefensiveReboundPercentage:.1f}%")
        print(f"Opponent Free Throw Rate: {opposingTeamStats.opponentFreeThrowRate:.1f}")
        
        print("\n=== Opponent Opponent Stats ===")
        print(f"Opponent Opponent Field Goals: {opposingTeamStats.opponentOpponentFieldGoals:.1f}/{opposingTeamStats.opponentOpponentFieldGoalsAttempted:.1f} ({opposingTeamStats.opponentOpponentFieldGoalPercentage:.1f}%)")
        print(f"Opponent Opponent Three Points: {opposingTeamStats.opponentOpponentThreePoints:.1f}/{opposingTeamStats.opponentOpponentThreePointsAttempted:.1f} ({opposingTeamStats.opponentOpponentThreePointPercentage:.1f}%)")
        print(f"Opponent Opponent Two Points: {opposingTeamStats.opponentOpponentTwoPoints:.1f}/{opposingTeamStats.opponentOpponentTwoPointsAttempted:.1f} ({opposingTeamStats.opponentOpponentTwoPointPercentage:.1f}%)")
        print(f"Opponent Opponent Free Throws: {opposingTeamStats.opponentOpponentFreeThrows:.1f}/{opposingTeamStats.opponentOpponentFreeThrowsAttempted:.1f} ({opposingTeamStats.opponentOpponentFreeThrowPercentage:.1f}%)")
        print(f"Opponent Opponent Offensive Rebounds: {opposingTeamStats.opponentOpponentOffensiveRebounds:.1f}")
        print(f"Opponent Opponent Defensive Rebounds: {opposingTeamStats.opponentOpponentDefensiveRebounds:.1f}")
        print(f"Opponent Opponent Total Rebounds: {opposingTeamStats.opponentOpponentTotalRebounds:.1f}")
        print(f"Opponent Opponent Average Assists: {opposingTeamStats.opponentOpponentAverageAssists:.1f}")
        print(f"Opponent Opponent Average Steals: {opposingTeamStats.opponentOpponentAverageSteals:.1f}")
        print(f"Opponent Opponent Average Blocks: {opposingTeamStats.opponentOpponentAverageBlocks:.1f}")
        print(f"Opponent Opponent Average Turnovers: {opposingTeamStats.opponentOpponentAverageTurnovers:.1f}")
        print(f"Opponent Opponent Average Points: {opposingTeamStats.opponentOpponentAveragePoints:.1f}")
        
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        
    finally:
        # Clean up
        scraper.driver.quit()

if __name__ == "__main__":
    #playerName = input("Enter player name: ")
    playerName = "Nikola Jokic"
    testScraper(playerName)