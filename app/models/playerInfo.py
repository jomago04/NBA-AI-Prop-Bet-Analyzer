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
    daysSinceLastGame: int #(advanced game log (might be better way))]
    
class PlayerIndividualFiveGameStats(BaseModel):
    playerName: str
    opponent: str
    isAway: bool
    minutesPlayed: float
    
    fieldGoals: int
    fieldGoalAttempts: int
    fieldGoalPercentage: float
    
    threePoints: int
    threePointAttempts: int
    threePointPercentage: float
    
    freeThrows: int
    freeThrowAttempts: int
    freeThrowPercentage: float
        
    offensiveRebounds: int
    defensiveRebounds: int
    totalRebounds: int
        
    assists: int
    steals: int
    blocks: int
    turnovers: int
    
    points: int
    gameScore: float
    plusMinus: int
    
    trueShootingPercentage: float
    effectiveFieldGoalPercentage: float
    usagePercentage: float
    offensiveRating: float
    defensiveRating: float
        
class PlayerLastFiveGameStats(BaseModel):

    averageMinutesPlayed: float
    
    averageFieldGoals: float
    averageFieldGoalAttempts: float
    averageFieldGoalPercentage: float
    
    averageThreePoints: float
    averageThreePointAttempts: float
    averageThreePointPercentage: float
    
    averageFreeThrows: float
    averageFreeThrowAttempts: float
    averageFreeThrowPercentage: float
    
    averageOffensiveRebounds: float
    averageDefensiveRebounds: float
    averageTotalRebounds: float
    
    averageAssists: float
    averageSteals: float
    averageBlocks: float
    averageTurnovers: float

    averagePoints: float
    averageGameScore: float
    averagePlusMinus: float
    
    averageTrueShootingPercentage: float
    averageEffectiveFieldGoalPercentage: float
    averageUsagePercentage: float
    averageOffensiveRating: float
    averageDefensiveRating: float
    
    
class PlayerCurrentSeasonTotalStats(BaseModel):
    gamesPlayed: int
    gamesStarted: int
    gamesStartedPercentage: float
    
    minutesPlayed: float
    
    fieldGoals: float
    fieldGoalAttempts: float
    fieldGoalPercentage: float
    
    threePoints: float
    threePointAttempts: float
    threePointPercentage: float
    
    freeThrows: float
    freeThrowAttempts: float
    freeThrowPercentage: float  
    
    offensiveRebounds: float
    defensiveRebounds: float
    totalRebounds: float
    
    assists: float
    steals: float
    blocks: float
    turnovers: float    
    
    personalFouls: float
    points: float
    
    averageTrueShootingPercentage: float
    averageUsagePercentage: float
    averageOffensiveRating: float
    averageDefensiveRating: float
    
class PlayerCurrentSeasonAverageStats(BaseModel):
    averageGamesPlayed: float
    averageGamesStarted: float
    averageGamesStartedPercentage: float
    
    averageMinutesPlayed: float
    
    averageFieldGoals: float
    averageFieldGoalAttempts: float
    averageFieldGoalPercentage: float
    
    averageThreePoints: float
    averageThreePointAttempts: float
    averageThreePointPercentage: float   
    
    averageTwoPoints: float
    averageTwoPointsAttempts: float
    averageTwoPointPercentage: float
    
    averageEffectiveFieldGoalPercentage: float
    
    averageFreeThrows: float
    averageFreeThrowAttempts: float
    averageFreeThrowPercentage: float
    
    averageOffensiveRebounds: float
    averageDefensiveRebounds: float
    averageTotalRebounds: float
    
    averageAssists: float
    averageSteals: float
    averageBlocks: float
    averageTurnovers: float 
    
    averagePoints: float
    
class PlayerOpposingTeamStats(BaseModel):
    opponentTeamName: str
    opponentWins: int
    opponentLosses: int
    opponentWinPercentage: float
    opponentAverageFieldGoals: float
    opponentAverageFieldGoalsAttempted: float
    opponentAverageFieldGoalRatio: float
    opponentAverageThreePoints: float
    opponentAverageThreePointsAttempted: float
    opponentAverageThreePointRatio: float
    opponentAverageTwoPoints: float
    opponentAverageTwoPointsAttempted: float
    opponentAverageTwoPointRatio: float
    opponentAverageFreeThrows: float
    opponentAverageFreeThrowAttempts: float
    opponentAverageFreeThrowRatio: float
    opponentAverageOffensiveRebounds: float
    opponentAverageDefensiveRebounds: float
    opponentAverageAssists: float
    opponentAverageSteals: float
    opponentAverageBlocks: float
    opponentAverageTurnovers: float
    opponentAveragePoints: float
    opponentOffensiveRating: float
    opponentDefensiveRating: float
    opponentPaceFactor: float
    opponentFreeThrowRate: float
    opponentThreePointRate: float
    opponentEffectiveFieldGoalPercentage: float
    opponentTurnoverPercentage: float
    opponentOffensiveReboundPercentage: float
    opponentFreeThrowRate: float
    #HOW OTHER TEAMS PLAY AGAINST OPPONENT
    opponentOpponentFieldGoals: float
    opponentOpponentFieldGoalsAttempted: float
    opponentOpponentFieldGoalRatio: float
    opponentOpponentThreePoints: float
    opponentOpponentThreePointsAttempted: float
    opponentOpponentThreePointRatio: float
    opponentOpponentTwoPoints: float
    opponentOpponentTwoPointsAttempted: float
    opponentOpponentTwoPointRatio: float
    opponentOpponentFreeThrows: float
    opponentOpponentFreeThrowsAttempted: float
    opponentOpponentFreeThrowRatio: float
    opponentOpponentOffensiveRebounds: float
    opponentOpponentDefensiveRebounds: float
    opponentOpponentAverageAssists: float
    opponentOpponentAverageSteals: float
    opponentOpponentAverageBlocks: float
    opponentOpponentAverageTurnovers: float
    #DEFENSIVE FOUR FACTORS
    opponentOpponentEffectiveFieldGoalPercentage: float
    opponentOpponentTurnoverPercentage: float
    opponentOpponentDefensiveReboundPercentage: float
    opponentOpponentFreeThrowRate: float






    #potential addtions - Pace (possesions per 48 mins), On/Off splits, home/away splits, days since last game, injuries
    
    
    
    
    
    # prop bet database prep: https://www.bettingpros.com/nba/props/nikola-jokic/points/ for reference
    # catagories to scrape: points, assists, rebounds, 3pts, steals, blocks
    