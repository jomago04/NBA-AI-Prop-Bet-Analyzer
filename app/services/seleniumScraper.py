from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class SeleniumScraper:
    def __init__(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.wait = WebDriverWait(self.driver, 10)

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
        
        return main_player_url, splits_player_url, gamelog_player_url

    def get_opposing_team_url(self, main_player_url: str) -> str:
        self.driver.get(main_player_url)
        opposing_team_key = self.wait.until(EC.presence_of_element_located((By.ID, "GET ID UNDER LAST 5 GAME TABLE ")))

