class ScraperConstants:
    BASE_URL = "https://www.basketball-reference.com"
    SELECTORS = {
        'GAME_TABLE': "#pgl_basic",
        'ADVANCED_TABLE': "#pgl_advanced",
        'LAST_FIVE_ROWS': "tbody tr:not(.thead)",
        'OPPOSING_TEAM': "#tfooter_last5 a",
        'CURRENT_SEASON_TABLE': "#per_game_stats",
        'CURRENT_SEASON_ROWS': "tbody tr:not(.thead)"
    }
    
    # TODO: this needs to get reworked at some point or maybe even removed 
    

    