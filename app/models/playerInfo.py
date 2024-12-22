from pydantic import BaseModel
from typing import Optional

class PlayerAverageLastFiveGameStats(BaseModel):
    # Text fields (strings)  (May be ideal to move name to seasonal stats since it already has strings)
    name: str
    
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