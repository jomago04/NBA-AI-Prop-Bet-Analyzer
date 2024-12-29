
class UrlLoaders:
    def __init__(self, driver):
        self.driver = driver
        
    def loadMainUrl(self, mainUrl: str):
        print(f"Loading main url: {mainUrl}")
        self.driver.get(mainUrl)
    
    def loadSplitsUrl(self, splitsUrl: str):
        print(f"Loading splits url: {splitsUrl}")
        self.driver.get(splitsUrl)
    
    def loadGamelogUrl(self, gamelogUrl: str):
        print(f"Loading gamelog url: {gamelogUrl}")
        self.driver.get(gamelogUrl)
    
    def loadAdvancedGamelogUrl(self, advancedGamelogUrl: str):
        print(f"Loading advanced gamelog url: {advancedGamelogUrl}")
        self.driver.get(advancedGamelogUrl)
    