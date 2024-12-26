from app.services.seleniumScraper import SeleniumScraper

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

        # Test 2: Get opposing team
        print("\n=== Testing Opposing Team Retrieval ===")
        opposing_team = scraper.get_opposing_team_url(main_url)
        print(f"Opposing Team: {opposing_team}")
        
        # Get last 5 games stats
        print("\n=== Last 5 Games Stats ===")
        stats = scraper.get_player_five_game_stats(gamelog_url)
        
        # Print individual game stats
        for i, game in enumerate(stats, 1):
            print(f"Game {i}:")
            print(f"FG: {game['field_goals']}/{game['field_goal_attempts']} ({game['field_goal_percentage']:.3f})")
            print(f"Points: {game['points']}\n")
        
        # Calculate and print average
        fg_average = scraper.calculate_player_five_game_stats(stats)
        print(f"\nAverage Field Goals per game: {fg_average['average_field_goals']:.1f}")
        print(f"Average Field Goals Attempted per game: {fg_average['average_field_goal_attempts']:.1f}")
        print(f"Average Field Goal Percentage per game: {fg_average['average_field_goal_percentage']:.3f}")
        print(f"Average Points per game: {fg_average['average_points']:.1f}")

        
    finally:
        # Clean up
        scraper.driver.quit()

if __name__ == "__main__":
    player_name = "Lebron James"
    test_scraper(player_name)