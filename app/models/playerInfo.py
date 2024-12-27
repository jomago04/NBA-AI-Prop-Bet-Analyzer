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

    
 #########################################
 #         FOR SELENIUM SCRAPING 
 #########################################
    
class PlayerInfo(BaseModel):
    name: str #(top of page)
    team: str #(top of page)
    position: str #(per game log - seasonal)
    age: int #(per game log - seasonal)
    experience: int #(top of page)
    days_since_last_game: int #(advanced game log (might be better way))
    
class PlayerLastFiveGameStats(BaseModel):
    # https://www.basketball-reference.com/players/j/jamesle01.html
    average_minutes_played: float
    average_field_goals: float
    average_field_goals_attempted: float
    average_field_goal_percentage: float
    average_three_points: float
    average_three_points_attempted: float
    average_three_point_percentage: float
    average_free_throws: float
    average_free_throws_attempted: float
    average_free_throw_percentage: float
    average_offensive_rebounds: float
    average_defensive_rebounds: float
    average_total_rebounds: float
    average_assists: float
    average_steals: float
    average_blocks: float
    average_turnovers: float
    average_points: float
    average_game_score: float
    average_plusminus: float
        # https://www.basketball-reference.com/players/j/jamesle01/gamelog-advanced/2025
    true_shooting_percentage: float
    effective_field_goal_percentage: float
    usage_percentage: float
    offensive_rating: float
    defensive_rating: float
    
class PlayerCurrentSeasonStats(BaseModel):
    games_played: int
    games_started: int
    games_started_percentage: float
    field_goals: float
    field_goals_attempted: float
    field_goal_percentage: float
    three_points: float
    three_points_attempted: float
    three_point_percentage: float
    free_throws: float
    free_throws_attempted: float
    free_throw_percentage: float
    offensive_rebounds: float
    defensive_rebounds: float
    total_rebounds: float
    assists: float
    steals: float
    blocks: float
    turnovers: float
    points: float
    true_shooting_percentage: float
    usage_percentage: float
    offensive_rating: float
    defensive_rating: float
    plusminus: float
    average_minutes_played: float
    average_points: float
    average_total_rebounds: float
    average_assists: float
    
class PlayerOpposingTeamStats(BaseModel):
    opponent_team_name: str
    opponent_wins: int
    opponent_losses: int
    opponent_win_percentage: float
    opponent_field_goals: float
    opponent_field_goals_attempted: float
    opponent_field_goal_ratio: float
    opponent_three_points: float
    opponent_three_points_attempted: float
    opponent_three_point_ratio: float
    opponent_two_points: float
    opponent_two_points_attempted: float
    opponent_two_point_ratio: float
    opponent_free_throws: float
    opponent_free_throws_attempted: float
    opponent_free_throw_ratio: float
    opponent_offensive_rebounds: float
    opponent_defensive_rebounds: float
    opponent_average_assists: float
    opponent_average_steals: float
    opponent_average_blocks: float
    opponent_average_turnovers: float
    opponent_average_points: float
    opponent_offensive_rating: float
    opponent_defensive_rating: float
    opponent_pace_factor: float
    opponent_free_throw_rate: float
    opponent_three_point_rate: float
    opponent_effective_field_goal_percentage: float
    opponent_turnover_percentage: float
    opponent_offensive_rebound_percentage: float
    opponent_free_throw_rate: float
    #HOW OTHER TEAMS PLAY AGAINST OPPONENT
    opponent_opponent_field_goals: float
    opponent_opponent_field_goals_attempted: float
    opponent_opponent_field_goal_ratio: float
    opponent_opponent_three_points: float
    opponent_opponent_three_points_attempted: float
    opponent_opponent_three_point_ratio: float
    opponent_opponent_two_points: float
    opponent_opponent_two_points_attempted: float
    opponent_opponent_two_point_ratio: float
    opponent_opponent_free_throws: float
    opponent_opponent_free_throws_attempted: float
    opponent_opponent_free_throw_ratio: float
    opponent_opponent_offensive_rebounds: float
    opponent_opponent_defensive_rebounds: float
    opponent_opponent_average_assists: float
    opponent_opponent_average_steals: float
    opponent_opponent_average_blocks: float
    opponent_opponent_average_turnovers: float
    #DEFENSIVE FOUR FACTORS
    opponent_opponent_effective_field_goal_percentage: float
    opponent_opponent_turnover_percentage: float
    opponent_opponent_defensive_rebound_percentage: float
    opponent_opponent_free_throw_rate: float






    #potential addtions - Pace (possesions per 48 mins), On/Off splits, home/away splits, days since last game, injuries
    
    
    
    
    
    # prop bet database prep: https://www.bettingpros.com/nba/props/nikola-jokic/points/ for reference
    # catagories to scrape: points, assists, rebounds, 3pts, steals, blocks
    