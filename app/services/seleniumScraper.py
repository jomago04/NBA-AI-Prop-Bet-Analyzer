from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class SeleniumScraper:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--log-level=3")  # Only show fatal errors
        chrome_options.add_argument("--ignore-certificate-errors") 
        chrome_options.add_argument("--ignore-ssl-errors")  
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Suppress console logging
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-browser-side-navigation")
        chrome_options.add_argument("--dns-prefetch-disable")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.page_load_strategy = 'eager'  # Don't wait for all resources to load
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.wait = WebDriverWait(self.driver, 5)

    def get_player_url(player_name: str) -> str:
        # Splits player name into first and last name
        name_parts = player_name.lower().split()
        # Checks if player name has both first and last name to avoid errors
        if len(name_parts) < 2:
            return "Please enter both first and last name"
        # [-1] grabs last item in list, [0] grabs first item in list
        last_name, first_name = name_parts[-1], name_parts[0]
        # [:1] grabs first letter of last name, [:5] grabs first 5 letters of last name, [:2] grabs first 2 letters of first name
        main_player_url = f"https://www.basketball-reference.com/players/{last_name[:1]}/{last_name[:5]}{first_name[:2]}01.html"
        splits_player_url = f"https://www.basketball-reference.com/players/{last_name[:1]}/{last_name[:5]}{first_name[:2]}01/splits/2025" # TODO: Make way to get current year
        gamelog_player_url = f"https://www.basketball-reference.com/players/{last_name[:1]}/{last_name[:5]}{first_name[:2]}01/gamelog/2025"
        advanced_gamelog_player_url = f"https://www.basketball-reference.com/players/{last_name[:1]}/{last_name[:5]}{first_name[:2]}01/gamelog-advanced/2025"
        
        return main_player_url, splits_player_url, gamelog_player_url, advanced_gamelog_player_url

    def get_opposing_team_url(self, main_player_url: str) -> str:
        try:
            self.driver.set_page_load_timeout(10)
            self.driver.get(main_player_url)
            opposing_team_key = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tfooter_last5 a")), message="Could not find opposing team element")
            
        except Exception as e:
            print(f"Error getting opposing team: {str(e)}")
            return None
        
        return opposing_team_key.text
    
    def get_player_five_game_stats(self, gamelog_player_url: str):
        try:
            self.driver.get(gamelog_player_url)
            table = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#pgl_basic")))
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr:not(.thead)")[-5:]  # Get only last 5 rows
            
            last_five_game_stats = []
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                try:
                    game_stats = {
                        'field_goals': int(cells[9].text),
                        'field_goal_attempts': int(cells[10].text),
                        'field_goal_percentage': float(cells[11].text),
                        'points': int(cells[26].text)
                    }
                    last_five_game_stats.append(game_stats)
                except (ValueError, IndexError) as e:
                    continue
                    
            return last_five_game_stats
            
        except Exception as e:
            print(f"Error retrieving game stats: {str(e)}")
            return []
        
    def calculate_player_five_game_stats(self, last_five_game_stats: list):
        if not last_five_game_stats:
            return {}
        
        averages = {
            'average_field_goals': sum(game['field_goals'] for game in last_five_game_stats) / len(last_five_game_stats),
            'average_field_goal_attempts': sum(game['field_goal_attempts'] for game in last_five_game_stats) / len(last_five_game_stats),
            'average_field_goal_percentage': sum(game['field_goal_percentage'] for game in last_five_game_stats) / len(last_five_game_stats),
            'average_points': sum(game['points'] for game in last_five_game_stats) / len(last_five_game_stats)
        }
        
        return averages
        

