class ScraperConstants:
    BASE_URL = "https://www.basketball-reference.com"
    SELECTORS = {
        'GAME_TABLE': "#pgl_basic",
        'ADVANCED_TABLE': "#pgl_advanced",
        'LAST_FIVE_ROWS': "tbody tr:not(.thead)",
        'OPPOSING_TEAM': "#tfooter_last5 a"
    }
    