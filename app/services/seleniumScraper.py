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

    def get_player_url(player_name: str):
        # Splits player name into first and last name
        name_parts = NameFormat.get_name_parts(player_name)
        # Checks if player name has both first and last name to avoid errors
        if len(name_parts) < 2:
            return "Please enter both first and last name"
        # [-1] grabs last item in list, [0] grabs first item in list
        last_name, first_name = name_parts[-1], name_parts[0]
        # [:1] grabs first letter of last name, [:5] grabs first 5 letters of last name, [:2] grabs first 2 letters of first name
        main_player_url = f"{ScraperConstants.BASE_URL}/players/{last_name[:1]}/{last_name[:5]}{first_name[:2]}01.html"
        splits_player_url = f"{ScraperConstants.BASE_URL}/players/{last_name[:1]}/{last_name[:5]}{first_name[:2]}01/splits/2025" # TODO: Make way to get current year
        gamelog_player_url = f"{ScraperConstants.BASE_URL}/players/{last_name[:1]}/{last_name[:5]}{first_name[:2]}01/gamelog/2025"
        advanced_gamelog_player_url = f"{ScraperConstants.BASE_URL}/players/{last_name[:1]}/{last_name[:5]}{first_name[:2]}01/gamelog-advanced/2025"
        
        return main_player_url, splits_player_url, gamelog_player_url, advanced_gamelog_player_url

    def get_opposing_team_url(self, main_player_url: str) -> str:
        # Gets the opposing team from the main player url
        try:
            # Loads the main player url
            self.driver.set_page_load_timeout(10)
            self.driver.get(main_player_url)
            # Finds the opposing team key
            opposing_team_key = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ScraperConstants.SELECTORS['OPPOSING_TEAM'])))
            
        except Exception as e:
            print(f"Error getting opposing team: {str(e)}")
            return None
        
        return opposing_team_key.text
    
    
    def get_player_five_game_stats(self, gamelog_player_url: str, player_name: str):
        try:
            # Loads the gamelog player url
            self.driver.get(gamelog_player_url)
            # Finds the table
            table = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ScraperConstants.SELECTORS['GAME_TABLE'])))
            # Finds the last 5 rows while excluding the headers
            rows = table.find_elements(By.CSS_SELECTOR, ScraperConstants.SELECTORS['LAST_FIVE_ROWS'])[-5:] 
            
            # Creates a list to store the last 5 game stats
            last_five_game_stats = []
            
            # Loops through the last 5 rows
            for i, row in enumerate(rows, 1):
                try:
                    # Finds the cells in the row
                    cells = row.find_elements(By.TAG_NAME, "td")
                    
                    # Creates a dictionary to store the last 5 game stats to send to playerInfo.py
                    game_stats = {
                        'player_name': NameFormat.format_name(NameFormat.get_name_parts(player_name)),
                        'opponent': row.find_elements(By.TAG_NAME, 'td')[5].text,  # Opponent team
                        'is_away': row.find_elements(By.TAG_NAME, 'td')[4].text == '@',  # Location
                        'minutes_played': TimeConverter.convert_time_string_to_float(cells[8].text),
                        
                        'field_goals': int(cells[9].text),
                        'field_goal_attempts': int(cells[10].text),
                        'field_goal_percentage': float(cells[11].text) * 100,
                        
                        'three_points': int(cells[12].text),
                        'three_point_attempts': int(cells[13].text),
                        'three_point_percentage': float(cells[14].text) * 100,
                            
                        'free_throws': int(cells[15].text),
                        'free_throw_attempts': int(cells[16].text),
                        'free_throw_percentage': float(cells[17].text) * 100,
                        
                        'offensive_rebounds': int(cells[18].text),
                        'defensive_rebounds': int(cells[19].text),
                        'total_rebounds': int(cells[20].text),
                        
                        'assists': int(cells[21].text),
                        'steals': int(cells[22].text),
                        'blocks': int(cells[23].text),
                        'turnovers': int(cells[24].text),
                        
                        'points': int(cells[26].text),
                        'game_score': float(cells[27].text),
                        'plusminus': int(cells[28].text)
                    }
                    # Adds the game stats to the list
                    last_five_game_stats.append(game_stats)
                    
                except (ValueError, IndexError) as e:
                    print(f"Error processing game {i}: {str(e)}")
                    continue
                
            return last_five_game_stats
            
        except Exception as e:
            print(f"Error retrieving game stats: {str(e)}")
            return []
        
    def get_player_advanced_five_game_stats(self, advanced_gamelog_player_url: str):
        try:
            self.driver.get(advanced_gamelog_player_url)
            table = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#pgl_advanced")))
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr:not(.thead)")[-5:]
            
            advanced_five_game_stats = []
            
            for i, row in enumerate(rows, 1):
                cells = row.find_elements(By.TAG_NAME, "td") 
                
                game_stats = {
                    'true_shooting_percentage': float(cells[9].text) * 100,
                    'effective_field_goal_percentage': float(cells[10].text) * 100,
                    'usage_percentage': float(cells[18].text),
                    'offensive_rating': float(cells[19].text),
                    'defensive_rating': float(cells[20].text)
                }
                advanced_five_game_stats.append(game_stats)
                
            return advanced_five_game_stats
        
        except Exception as e:
            print(f"Error retrieving advanced game stats: {str(e)}")
            return []
        
    def calculate_player_five_game_averages(self, last_five_game_stats: list, advanced_five_game_stats: list):
        # Checks if the last 5 game stats is empty
        if not last_five_game_stats:
            return {
                'average_minutes_played': 0.0,
                
                'average_field_goals': 0.0,
                'average_field_goal_attempts': 0.0,
                'average_field_goal_percentage': 0.0,
                
                
                'average_three_points': 0.0,
                'average_three_point_attempts': 0.0,
                'average_three_point_percentage': 0.0,
                
                'average_free_throws': 0.0,
                'average_free_throw_attempts': 0.0,
                'average_free_throw_percentage': 0.0,
                
                'average_offensive_rebounds': 0.0,
                'average_defensive_rebounds': 0.0,
                'average_total_rebounds': 0.0,
                
                'average_assists': 0.0,
                'average_steals': 0.0,
                'average_blocks': 0.0,
                'average_turnovers': 0.0,
                
                'average_points': 0.0,
                'average_game_score': 0.0,
                'average_plusminus': 0.0,
                
                'average_true_shooting_percentage': 0.0,
                'average_effective_field_goal_percentage': 0.0,
                'average_usage_percentage': 0.0,
                'average_offensive_rating': 0.0,
                'average_defensive_rating': 0.0
            }
        
        # Grabs the number of games
        num_games = len(last_five_game_stats)
        # Calculates the averages
        averages = {
            'average_minutes_played': float(sum(game['minutes_played'] for game in last_five_game_stats) / num_games),
            
            'average_field_goals': float(sum(game['field_goals'] for game in last_five_game_stats) / num_games),
            'average_field_goal_attempts': float(sum(game['field_goal_attempts'] for game in last_five_game_stats) / num_games),
            'average_field_goal_percentage': float(sum(game['field_goal_percentage'] for game in last_five_game_stats) / num_games),
            
            'average_three_points': float(sum(game['three_points'] for game in last_five_game_stats) / num_games),
            'average_three_point_attempts': float(sum(game['three_point_attempts'] for game in last_five_game_stats) / num_games),
            'average_three_point_percentage': float(sum(game['three_point_percentage'] for game in last_five_game_stats) / num_games),
            
            'average_free_throws': float(sum(game['free_throws'] for game in last_five_game_stats) / num_games),
            'average_free_throw_attempts': float(sum(game['free_throw_attempts'] for game in last_five_game_stats) / num_games),
            'average_free_throw_percentage': float(sum(game['free_throw_percentage'] for game in last_five_game_stats) / num_games),
            
            'average_offensive_rebounds': float(sum(game['offensive_rebounds'] for game in last_five_game_stats) / num_games),
            'average_defensive_rebounds': float(sum(game['defensive_rebounds'] for game in last_five_game_stats) / num_games),
            'average_total_rebounds': float(sum(game['total_rebounds'] for game in last_five_game_stats) / num_games),
            
            'average_assists': float(sum(game['assists'] for game in last_five_game_stats) / num_games),
            'average_steals': float(sum(game['steals'] for game in last_five_game_stats) / num_games),
            'average_blocks': float(sum(game['blocks'] for game in last_five_game_stats) / num_games),
            'average_turnovers': float(sum(game['turnovers'] for game in last_five_game_stats) / num_games),
            
            'average_points': float(sum(game['points'] for game in last_five_game_stats) / num_games),
            'average_game_score': float(sum(game['game_score'] for game in last_five_game_stats) / num_games),
            'average_plusminus': float(sum(game['plusminus'] for game in last_five_game_stats) / num_games),
            
            'average_true_shooting_percentage': float(sum(game['true_shooting_percentage'] for game in advanced_five_game_stats) / num_games),
            'average_effective_field_goal_percentage': float(sum(game['effective_field_goal_percentage'] for game in advanced_five_game_stats) / num_games),
            'average_usage_percentage': float(sum(game['usage_percentage'] for game in advanced_five_game_stats) / num_games),
            'average_offensive_rating': float(sum(game['offensive_rating'] for game in advanced_five_game_stats) / num_games),
            'average_defensive_rating': float(sum(game['defensive_rating'] for game in advanced_five_game_stats) / num_games)
        }
        
        return averages
        

