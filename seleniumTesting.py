from app.services.seleniumScraper import SeleniumScraper
from app.models.playerInfo import PlayerLastFiveGameStats, PlayerIndividualFiveGameStats
from app.utilities.timeConverter import TimeConverter

def test_scraper(player_name):
    # Initialize scraper
    scraper = SeleniumScraper()
    
    try:
        # Test 1: Get player URLs
        print("\n=== Testing Player URL Generation ===")
        main_url, splits_url, gamelog_url, advanced_gamelog_url = SeleniumScraper.get_player_url(player_name)
        print(f"Main URL: {main_url}")
        print(f"Splits URL: {splits_url}")
        print(f"Gamelog URL: {gamelog_url}")
        print(f"Advanced Gamelog URL: {advanced_gamelog_url}")

        player_stats = scraper.get_player_five_game_stats(gamelog_url, player_name)
        advanced_player_stats = scraper.get_player_advanced_five_game_stats(advanced_gamelog_url)
        
        combined_stats = []
        for default, advanced in zip(player_stats, advanced_player_stats):
            combine_stats = default.copy()
            combine_stats.update(advanced)
            combined_stats.append(combine_stats)
            
        individual_games = [PlayerIndividualFiveGameStats(**game) for game in combined_stats]
            
        print("\n=== Individual Game Stats ===")
        for i, game in enumerate(individual_games, 1):
            
            # Display individual game stats
            location_text = "@ " if game.is_away else "vs "
            print(f"\nGame {i} ({game.player_name} {location_text}{game.opponent}):")
            print(f"Minutes: {TimeConverter.convert_time_float_to_string(game.minutes_played)}")
            print(f"FG: {game.field_goals}/{game.field_goal_attempts} ({game.field_goal_percentage:.1f}%)")
            print(f"3PT: {game.three_points}/{game.three_point_attempts} ({game.three_point_percentage:.1f}%)")
            print(f"FT: {game.free_throws}/{game.free_throw_attempts} ({game.free_throw_percentage:.1f}%)")
            print(f"Rebounds: {game.total_rebounds} (O: {game.offensive_rebounds}, D: {game.defensive_rebounds})")
            print(f"Assists: {game.assists}")
            print(f"Steals: {game.steals}")
            print(f"Blocks: {game.blocks}")
            print(f"Turnovers: {game.turnovers}")
            print(f"Points: {game.points}")
            print(f"Game Score: {game.game_score:.1f}")
            print(f"Plus/Minus: {game.plusminus}")
            print(f"True Shooting %: {game.true_shooting_percentage:.1f}%")
            print(f"eFG%: {game.effective_field_goal_percentage:.1f}%")
            print(f"Usage %: {game.usage_percentage:.1f}%")
            print(f"Offensive Rating: {game.offensive_rating:.1f}")
            print(f"Defensive Rating: {game.defensive_rating:.1f}")
        
        # Calculate averages
        averages = scraper.calculate_player_five_game_averages(player_stats, advanced_player_stats)
        player_averages = PlayerLastFiveGameStats(**averages)
        
        # Display averages
        print("\n=== Five Game Averages ===")
        print(f"Average Minutes: {TimeConverter.convert_time_float_to_string(player_averages.average_minutes_played)}")
        print(f"Average FG: {player_averages.average_field_goals:.1f}/{player_averages.average_field_goal_attempts:.1f} ({player_averages.average_field_goal_percentage:.1f}%)")
        print(f"Average 3PT: {player_averages.average_three_points:.1f}/{player_averages.average_three_point_attempts:.1f} ({player_averages.average_three_point_percentage:.1f}%)")
        print(f"Average FT: {player_averages.average_free_throws:.1f}/{player_averages.average_free_throw_attempts:.1f} ({player_averages.average_free_throw_percentage:.1f}%)")
        print(f"Average Rebounds: {player_averages.average_total_rebounds:.1f} (O: {player_averages.average_offensive_rebounds:.1f}, D: {player_averages.average_defensive_rebounds:.1f})")
        print(f"Average Assists: {player_averages.average_assists:.1f}")
        print(f"Average Steals: {player_averages.average_steals:.1f}")
        print(f"Average Blocks: {player_averages.average_blocks:.1f}")
        print(f"Average Turnovers: {player_averages.average_turnovers:.1f}")
        print(f"Average Points: {player_averages.average_points:.1f}")
        print(f"Average Game Score: {player_averages.average_game_score:.1f}")
        print(f"Average Plus/Minus: {player_averages.average_plusminus:.1f}")
        print(f"Average True Shooting %: {player_averages.average_true_shooting_percentage:.1f}%")
        print(f"Average eFG%: {player_averages.average_effective_field_goal_percentage:.1f}%")
        print(f"Average Usage %: {player_averages.average_usage_percentage:.1f}%")
        print(f"Average Offensive Rating: {player_averages.average_offensive_rating:.1f}")
        print(f"Average Defensive Rating: {player_averages.average_defensive_rating:.1f}")
     
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
    finally:
        # Clean up
        scraper.driver.quit()

if __name__ == "__main__":
    #player_name = input("Enter player name: ")
    player_name = "LeBron James"
    test_scraper(player_name) 