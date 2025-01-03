from archive.seleniumScraper import SeleniumPlayerService
from pprint import pprint

class PlayerStatsTester:
    def __init__(self):
        self.scraper = SeleniumPlayerService()

    def test_player(self, player_name: str) -> None:
        """Test player stats scraping functions"""
        print(f"\n{'='*50}")
        print(f"Testing Player Stats for: {player_name}")
        print(f"{'='*50}")

        # Get and test player page access
        player_success = self._test_player_page(player_name)
        if not player_success:
            return

        # Test each type of player stat
        self._test_basic_info()
        self._test_last_five_games()
        self._test_seasonal_stats()

    def _test_player_page(self, player_name: str) -> bool:
        """Test player page access"""
        print("\n1. Testing Player Page Access...")
        try:
            success = self.scraper.get_player_page(player_name)
            print("✓ Success: Player page loaded")
            return success
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return False

    def _test_basic_info(self) -> None:
        """Test basic player info retrieval"""
        print("\n2. Testing Basic Player Info...")
        try:
            info = self.scraper.get_basic_player_info()
            print("✓ Success! Basic Info:")
            pprint(info.model_dump())
        except Exception as e:
            print(f"✗ Error: {str(e)}")

    def _test_last_five_games(self) -> None:
        """Test last 5 games stats retrieval"""
        print("\n3. Testing Last 5 Games Stats...")
        try:
            stats = self.scraper.get_last_five_games()
            print("✓ Success! Last 5 Games Stats:")
            pprint(stats.model_dump())
        except Exception as e:
            print(f"✗ Error: {str(e)}")

    def _test_seasonal_stats(self) -> None:
        """Test seasonal stats retrieval"""
        print("\n4. Testing Seasonal Stats...")
        try:
            stats = self.scraper.get_seasonal_stats()
            print("✓ Success! Seasonal Stats:")
            pprint(stats.model_dump())
        except Exception as e:
            print(f"✗ Error: {str(e)}")

    def cleanup(self):
        """Clean up Selenium driver"""
        try:
            self.scraper.driver.quit()
        except:
            pass

def main():
    tester = PlayerStatsTester()
    try:
        player_name = input("Enter NBA player name (First Last): ")
        tester.test_player(player_name)
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main()