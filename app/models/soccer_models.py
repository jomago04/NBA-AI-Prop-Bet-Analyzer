from pydantic import BaseModel


class SoccerPlayerInfo(BaseModel):
    name: str
    team: str
    position: str       # GK, DF, MF, FW
    age: int
    daysSinceLastGame: int


class SoccerGameStats(BaseModel):
    opponent: str
    isAway: bool
    minutesPlayed: float = 0.0
    goals: int = 0
    assists: int = 0
    shots: int = 0
    shotsOnTarget: int = 0
    xG: float = 0.0
    xA: float = 0.0
    keyPasses: int = 0


class SoccerLastFiveAverages(BaseModel):
    averageGoals: float = 0.0
    averageAssists: float = 0.0
    averageShots: float = 0.0
    averageShotsOnTarget: float = 0.0
    averageXG: float = 0.0
    averageXA: float = 0.0
    averageMinutesPlayed: float = 0.0


class SoccerSeasonStats(BaseModel):
    gamesPlayed: int = 0
    goals: int = 0
    assists: int = 0
    averageGoals: float = 0.0
    averageAssists: float = 0.0
    averageShots: float = 0.0
    averageShotsOnTarget: float = 0.0
    averageXG: float = 0.0
    shotConversionRate: float = 0.0
    averageMinutesPlayed: float = 0.0


class SoccerOpposingTeamStats(BaseModel):
    teamName: str
    wins: int
    draws: int
    losses: int
    goalsAllowedPerGame: float = 0.0
    xGAllowedPerGame: float = 0.0
    shotsAllowedPerGame: float = 0.0
    cleanSheets: int = 0
