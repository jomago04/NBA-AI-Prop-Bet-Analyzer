from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from app.models.playerInfo import (
    PlayerAverageLastFiveGameStats,
    PlayerSeasonalStats,
    PlayerOpposingTeamStats,
    PlayerBasicInfo
)

class SeleniumPlayerService:
    def __init__(self):
        self.driver = self._initialize_driver()
        self.wait = WebDriverWait(self.driver, 10)

    def _initialize_driver(self):
        """Initialize and configure Chrome driver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Add these SSL-specific options
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--ignore-ssl-errors")
            chrome_options.add_argument("--ignore-certificate-errors-spki-list")
            
            # Reduce logging
            chrome_options.add_argument("--log-level=3")
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            return webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
        except Exception as e:
            raise Exception(f"Failed to initialize Chrome driver: {str(e)}")

    def _calculate_percentage(self, made: float, attempted: float) -> float:
        """Calculate percentage with error handling"""
        try:
            return round((made / attempted * 100), 2) if attempted > 0 else 0.0
        except ZeroDivisionError:
            return 0.0

    def get_player_page(self, player_name: str) -> bool:
        """Navigate to player's page"""
        try:
            name_parts = player_name.lower().split()
            if len(name_parts) < 2:
                raise ValueError("Please enter both first and last name")
            
            last_name, first_name = name_parts[-1], name_parts[0]
            player_url = f"https://www.basketball-reference.com/players/{last_name[0]}/{last_name[:5]}{first_name[:2]}01.html"
            
            self.driver.get(player_url)
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#info h1")))
            return True
            
        except Exception as e:
            raise Exception(f"Error accessing player page: {str(e)}")

    def get_opposing_team_page(self) -> bool:
        """Navigate to opposing team's page by clicking team link"""
        try:
            # Find the div with ID tfooter_last5
            footer_div = self.wait.until(EC.presence_of_element_located((By.ID, 'tfooter_last5')))
            
            # Get the first link and scroll it into view
            team_link = footer_div.find_element(By.TAG_NAME, "a")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", team_link)
            
            # Wait a moment for any animations to complete
            time.sleep(1)
            
            # Wait for element to be clickable
            clickable_link = self.wait.until(EC.element_to_be_clickable(team_link))
            clickable_link.click()
            
            # Wait for team page to load
            self.wait.until(EC.presence_of_element_located((By.ID, 'team_stats')))
            return True
                
        except Exception as e:
            raise Exception(f"Error accessing opposing team page: {str(e)}")
    
    def get_basic_player_info(self) -> PlayerBasicInfo:
        """Get basic player information"""
        try:
            name = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#info h1"))
            ).text.strip()
            
            info_div = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#meta div[data-template='Partials/Teams/NBA']"))
            )
            
            team = info_div.find_element(By.TAG_NAME, "strong").text.strip()
            position = info_div.text.split("Position:")[1].split("▪")[0].strip()
            
            exp_element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#meta p"))
            )
            exp_text = exp_element.text
            
            age = int(exp_text.split("Age:")[1].split("years")[0].strip())
            exp_str = exp_text.split("Experience:")[1].strip()
            experience = 0 if "Rookie" in exp_str else int(exp_str.split("years")[0].strip())
            
            return PlayerBasicInfo(
                name=name,
                team=team,
                position=position,
                age=age,
                experience=experience
            )
            
        except Exception as e:
            raise Exception(f"Error getting basic player info: {str(e)}")

    def get_last_five_games(self) -> PlayerAverageLastFiveGameStats:
        """Get last 5 games statistics"""
        try:
            # Get the table and rows
            table = self.wait.until(EC.presence_of_element_located((By.ID, 'last5')))
            rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip header row
            games = len(rows)
            
            # Initialize totals
            totals = {
                'mp': 0, 'fg': 0, 'fga': 0, 'ft': 0, 'fta': 0,
                '3p': 0, '3pa': 0, 'reb': 0, 'ast': 0,
                'stl': 0, 'tov': 0
            }
            
            # Sum up the stats from each game
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                totals['mp'] += float(cells[5].text.strip() or 0)
                totals['fg'] += float(cells[6].text.strip() or 0)
                totals['fga'] += float(cells[7].text.strip() or 0)
                totals['3p'] += float(cells[9].text.strip() or 0)
                totals['3pa'] += float(cells[10].text.strip() or 0)
                totals['ft'] += float(cells[12].text.strip() or 0)
                totals['fta'] += float(cells[13].text.strip() or 0)
                totals['reb'] += float(cells[17].text.strip() or 0)
                totals['ast'] += float(cells[18].text.strip() or 0)
                totals['stl'] += float(cells[19].text.strip() or 0)
                totals['tov'] += float(cells[21].text.strip() or 0)
            
            # Calculate averages
            averages = {key: value / games for key, value in totals.items()}
            
            # Get player name
            name = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#info h1"))
            ).text.strip()
            
            return PlayerAverageLastFiveGameStats(
                name=name,
                minutes_played=averages['mp'],
                field_goals=averages['fg'],
                field_goals_attempted=averages['fga'],
                field_goal_percentage=self._calculate_percentage(averages['fg'], averages['fga']),
                free_throws=averages['ft'],
                free_throws_attempted=averages['fta'],
                free_throw_percentage=self._calculate_percentage(averages['ft'], averages['fta']),
                three_points=averages['3p'],
                three_points_attempted=averages['3pa'],
                three_point_percentage=self._calculate_percentage(averages['3p'], averages['3pa']),
                rebounds=averages['reb'],
                assists=averages['ast'],
                steals=averages['stl'],
                turnovers=averages['tov']
            )

        except Exception as e:
            raise Exception(f"Error processing last 5 games: {str(e)}")

    def get_seasonal_stats(self) -> PlayerSeasonalStats:
        """Get player's current season statistics"""
        try:
            print("\nDebug: Looking for per_game table...")
            # Get the table and last row
            table = self.wait.until(EC.presence_of_element_located((By.ID, 'totals_stats')))
            print("Debug: Found table, getting rows...")
            
            rows = table.find_elements(By.TAG_NAME, "tr")
            if not rows:
                raise Exception("No rows found in per_game table")
            print(f"Debug: Found {len(rows)} rows")
            
            # Get the last row that isn't empty
            current_season = None
            for row in reversed(rows):
                cells = row.find_elements(By.TAG_NAME, "td")
                if cells:
                    current_season = cells
                    break
                    
            if not current_season:
                raise Exception("Could not find current season stats")
            print("Debug: Found current season row")
                
            return PlayerSeasonalStats(
                season=(rows[-1].find_element(By.TAG_NAME, "th")).text,
                team=current_season[3].text,
                position=current_season[4].text,
                age=int(current_season[5].text),
                games=int(current_season[6].text),
                games_started=int(current_season[7].text),
                games_started_percentage=float(current_season[8].text or 0),
                minutes_played=float(current_season[9].text or 0),
                field_goals=float(current_season[10].text or 0),
                field_goals_attempted=float(current_season[11].text or 0),
                field_goal_percentage=float(current_season[12].text or 0),
                three_points=float(current_season[13].text or 0),
                three_points_attempted=float(current_season[14].text or 0),
                three_point_percentage=float(current_season[15].text or 0),
                two_points=float(current_season[16].text or 0),
                two_points_attempted=float(current_season[17].text or 0),
                two_point_percentage=float(current_season[18].text or 0),
                free_throws=float(current_season[19].text or 0),
                free_throws_attempted=float(current_season[20].text or 0),
                free_throw_percentage=float(current_season[21].text or 0),
                effective_field_goal_percentage=float(current_season[22].text or 0),
                total_rebounds=float(current_season[23].text or 0),
                total_assists=float(current_season[24].text or 0),
                total_steals=float(current_season[25].text or 0),
                points=float(current_season[26].text or 0)
            )
                    
        except Exception as e:
            print(f"\nDebug: Current URL = {self.driver.current_url}")
            print(f"Debug: Page source snippet = {self.driver.page_source[:500]}...")
            raise Exception(f"Error getting seasonal stats: {str(e)}")

    def get_opposing_team_stats(self) -> PlayerOpposingTeamStats:
        """Get opposing team statistics"""
        try:
            # Get team name
            team_name = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#meta h1"))
            ).text.strip()
            
            # Get record (wins/losses)
            record_element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#meta p"))
            )
            record_text = record_element.text
            wins = int(record_text.split('-')[0].strip())
            losses = int(record_text.split('-')[1].split(',')[0].strip())
            games_played = wins + losses
            
            # Get team stats table
            table = self.wait.until(EC.presence_of_element_located((By.ID, 'team_stats')))
            rows = table.find_elements(By.TAG_NAME, "tr")
            team_stats = rows[1].find_elements(By.TAG_NAME, "td")  # Team row
            
            return PlayerOpposingTeamStats(
                team_name=team_name,
                wins=wins,
                losses=losses,
                games_played=games_played,
                points_per_game=float(team_stats[26].text or 0),
                field_goal_percentage=float(team_stats[6].text or 0),
                three_point_percentage=float(team_stats[9].text or 0),
                rebounds=float(team_stats[18].text or 0),
                assists=float(team_stats[19].text or 0),
                steals=float(team_stats[20].text or 0),
                blocks=float(team_stats[21].text or 0),
                turnovers=float(team_stats[22].text or 0)
            )
                
        except Exception as e:
            raise Exception(f"Error getting opposing team stats: {str(e)}")
    
    def __del__(self):
        """Cleanup method"""
        if hasattr(self, 'driver'):
            self.driver.quit()