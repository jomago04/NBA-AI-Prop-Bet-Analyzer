from pydantic import BaseModel
from typing import Optional

class PlayerBasicInfo(BaseModel):
    name: str
    team: str
    position: str
    age: int
    experience: int


class PlayerAverageLastFiveGameStats(BaseModel):
    # Text fields (strings)  (May be ideal to move name to seasonal stats since it already has strings)
    
    # Decimal numbers (floats) 
    minutes_played: float
    field_goals: float
    field_goals_attempted: float
    field_goal_percentage: float
    free_throws: float
    free_throws_attempted: float
    free_throw_percentage: float
    three_points: float
    three_points_attempted: float
    three_point_percentage: float
    rebounds: float
    assists: float
    steals: float
    turnovers: float

class PlayerSeasonalStats(BaseModel):
    # Text fields (strings)
    season: str
    team: str
    position: str

    # Whole numbers (integers)
    age: int
    games: int
    games_started: int

    # Decimal numbers (floats)
    games_started_percentage: float
    minutes_played: float
    field_goals: float
    field_goals_attempted: float
    field_goal_percentage: float
    three_points: float
    three_points_attempted: float
    three_point_percentage: float
    two_points: float
    two_points_attempted: float
    two_point_percentage: float
    free_throws: float
    free_throws_attempted: float
    free_throw_percentage: float
    effective_field_goal_percentage: float
    total_rebounds: float
    total_assists: float
    total_steals: float
    points: float

class PlayerOpposingTeamStats(BaseModel):
    team_name: str
    wins: int
    losses: int
    games_played: int
    points_per_game: float
    field_goal_percentage: float
    three_point_percentage: float
    rebounds: float
    assists: float
    steals: float
    blocks: float
    turnovers: float
    
    
    
    #BASIC INFO
    #name (top of page)
    #team (top of page)
    #position (per game log - seasonal)
    #age (per game log - seasonal)
    #experience (top of page)
    #days_since_last_game (advanced game log (might be better way))
    
    #5 GAME AVERAGE STATS
    # https://www.basketball-reference.com/players/j/jamesle01.html
    #average_minutes_played
    #average_field_goals
    #average_field_goals_attempted
    #average_field_goal_percentage
    #average_three_points
    #average_three_points_attempted
    #average_three_point_percentage
    #average_free_throws
    #average_free_throws_attempted
    #average_free_throw_percentage
    #average_offensive_rebounds
    #average_defensive_rebounds
    #average_total_rebounds
    #average_assists
    #average_steals
    #average_blocks
    #average_turnovers
    #average_points
    #average_game_score
    #average_plusminus
    # https://www.basketball-reference.com/players/j/jamesle01/gamelog-advanced/2025
    #true_shooting_percentage
    #effective_field_goal_percentage
    #usage_percentage
    #offensive_rating
    #defensive_rating
    
    #SEASONAL STATS
    #games_played
    #games_started
    #games_started_percentage
    #field_goals
    #field_goals_attempted
    #field_goal_percentage
    #three_points
    #three_points_attempted
    #three_point_percentage
    #free_throws
    #free_throws_attempted
    #free_throw_percentage
    #offensive_rebounds
    #defensive_rebounds
    #total_rebounds
    #assists
    #steals
    #blocks
    #turnovers
    #points
    #true_shooting_percentage
    #usage_percentage
    #offensive_rating
    #defensive_rating
    #plusminus
    #average_minutes_played
    #average_points
    #average_total_rebounds
    #average_assists
    
    #OPPOSING TEAM STATS
    
    #potential addtions - Pace (possesions per 48 mins), On/Off splits, home/away splits, days since last game, 
    
    
    
    
    
    # prop bet database prep: https://www.bettingpros.com/nba/props/nikola-jokic/points/ for reference
    # catagories to scrape: points, assists, rebounds, 3pts, steals, blocks
    #