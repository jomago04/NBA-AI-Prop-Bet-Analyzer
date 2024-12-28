from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from app.config.constants import ScraperConstants

class SeleniumConfig:
    @staticmethod
    def initialize_driver():
        chrome_options = Options()
        
        # Performance optimizations
        chrome_options.page_load_strategy = 'eager'  # Don't wait for all resources to load
        chrome_options.add_argument('--disable-extensions')  # Disable extensions
        chrome_options.add_argument('--disable-browser-side-navigation')  # Disable browser side navigation
        chrome_options.add_argument('--dns-prefetch-disable')  # Disable DNS prefetch
        chrome_options.add_argument('--disable-web-security')  # Disable web security
        chrome_options.add_argument("--disable-features=NetworkService")  # Disable network service
        chrome_options.add_argument("--window-size=1920,1080")  # Set window size
        chrome_options.add_argument("--disable-animations")  # Disable animations
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Hide automation
        
        # Memory optimizations
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-setuid-sandbox')
        
        # Security and SSL settings
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--ignore-ssl-errors")
        chrome_options.add_argument("--ignore-certificate-errors-spki-list")
        chrome_options.add_argument("--allow-insecure-localhost")
        
        # Logging and console settings
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--log-level=3")  # Only show fatal errors
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Additional privacy settings
        chrome_options.add_argument("--incognito")  # Use incognito mode
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-infobars')
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Set timeouts
            driver.set_page_load_timeout(10)
            driver.set_script_timeout(5)
            
            # Create WebDriverWait object
            wait = WebDriverWait(driver, 5)
            
            # Return both driver and wait objects
            return driver, wait
            
        except Exception as e:
            print(f"Error initializing Chrome driver: {str(e)}")
            raise
    
    @staticmethod
    def cleanup_driver(driver):
        try:
            if driver:
                driver.quit()
        except Exception as e:
            print(f"Error closing browser: {str(e)}")