from app.services.seleniumScraper import SeleniumScraper
from app.models.playerInfo import PlayerLastFiveGameStats, PlayerIndividualFiveGameStats, PlayerCurrentSeasonTotalStats, PlayerCurrentSeasonAverageStats
from app.utilities.timeConverter import TimeConverter

def testScraper(playerName):
    # Initialize scraper
    scraper = SeleniumScraper()
    
    try:
        # Test 1: Get player URLs
        print("\n=== Testing Player URL Generation ===")
        mainUrl, splitsUrl, gamelogUrl, advancedGamelogUrl = SeleniumScraper.getPlayerUrl(playerName)
        print(f"Main URL: {mainUrl}")
        print(f"Splits URL: {splitsUrl}")
        print(f"Gamelog URL: {gamelogUrl}")
        print(f"Advanced Gamelog URL: {advancedGamelogUrl}")

        playerStats = scraper.getPlayerFiveGameStats(gamelogUrl, playerName)
        advancedPlayerStats = scraper.getPlayerAdvancedFiveGameStats(advancedGamelogUrl)
        
        combinedStats = []
        for default, advanced in zip(playerStats, advancedPlayerStats):
            combineStats = default.copy()
            combineStats.update(advanced)
            combinedStats.append(combineStats)
            
        individualGames = [PlayerIndividualFiveGameStats(**game) for game in combinedStats]
            
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
        averages = scraper.calculatePlayerFiveGameAverages(playerStats, advancedPlayerStats)
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
        
        currentSeasonTotalStats = scraper.getPlayerCurrentSeasonTotalStats(splitsUrl)
        currentSeasonAverages = scraper.getPlayerCurrentSeasonAverageStats(splitsUrl)
     
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
    finally:
        # Clean up
        scraper.driver.quit()

if __name__ == "__main__":
    #playerName = input("Enter player name: ")
    playerName = "LeBron James"
    testScraper(playerName)