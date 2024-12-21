from app import PlayerService  # Clean import from main package
from app.models import (
    PlayerAverageLastFiveGameStats,
    PlayerSeasonalStats,
    PlayerOpposingTeamStats
)
from pprint import pprint
import sys
from typing import Optional

class ScraperTester:
    def __init__(self):
        self.player_service = PlayerService()

    def test_player(self, player_name: str) -> None:
        """Test all stats for a given player"""
        print(f"\n{'='*50}")
        print(f"Testing stats for: {player_name}")
        print(f"{'='*50}")

        # Get and test player URL
        player_response = self._test_player_url(player_name)
        if not player_response:
            return

        # Test each type of stat
        self._test_last_five_games(player_response)
        self._test_seasonal_stats(player_response)
        self._test_opposing_team(player_response)

    def _test_player_url(self, player_name: str) -> Optional[object]:
        """Test player URL generation and access"""
        print("\n1. Testing Player URL Generation...")
        try:
            response = self.player_service.get_nbaplayer_url(player_name)
            print(f"✓ Success: {response.url}")
            return response
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return None

    def _test_last_five_games(self, player_response: object) -> None:
        """Test last 5 games stats retrieval"""
        print("\n2. Testing Last 5 Games Stats...")
        try:
            stats = self.player_service.get_nbaplayer_5game_stats(player_response)
            print("✓ Success! Last 5 Games Stats:")
            pprint(stats.model_dump())
        except Exception as e:
            print(f"✗ Error: {str(e)}")

    def _test_seasonal_stats(self, player_response: object) -> None:
        """Test seasonal stats retrieval"""
        print("\n3. Testing Seasonal Stats...")
        try:
            stats = self.player_service.get_nbaplayer_seasonal_stats(player_response)
            print("✓ Success! Seasonal Stats:")
            pprint(stats.model_dump())
        except Exception as e:
            print(f"✗ Error: {str(e)}")

    def _test_opposing_team(self, player_response: object) -> None:
        """Test opposing team stats retrieval"""
        print("\n4. Testing Opposing Team Stats...")
        try:
            # Get opposing team URL
            opposing_team_url = self.player_service.get_nbaplayer_opposingteam_url(player_response)
            print(f"Opposing Team URL: {opposing_team_url}")
            
            if isinstance(opposing_team_url, str) and opposing_team_url.startswith("Error"):
                print(f"✗ Error: {opposing_team_url}")
                return

            # Get opposing team stats
            team_stats = self.player_service.get_opposing_team_stats(opposing_team_url)
            print("✓ Success! Opposing Team Stats:")
            pprint(team_stats.model_dump())
        except Exception as e:
            print(f"✗ Error: {str(e)}")

def main():
    # Initialize tester
    tester = ScraperTester()
    player_name = input("Enter NBA player name (First Last): ")
    tester.test_player(player_name)

if __name__ == "__main__":
    main()