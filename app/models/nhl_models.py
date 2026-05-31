from pydantic import BaseModel


class NHLPlayerInfo(BaseModel):
    name: str
    team: str
    position: str       # C, LW, RW, D, G
    age: int
    daysSinceLastGame: int


class NHLGameStats(BaseModel):
    opponent: str
    isAway: bool
    goals: int = 0
    assists: int = 0
    points: int = 0
    shots: int = 0
    plusMinus: int = 0
    penaltyMinutes: int = 0
    timeOnIce: float = 0.0      # decimal minutes


class NHLLastFiveAverages(BaseModel):
    averageGoals: float = 0.0
    averageAssists: float = 0.0
    averagePoints: float = 0.0
    averageShots: float = 0.0
    averagePlusMinus: float = 0.0
    averageTimeOnIce: float = 0.0


class NHLSeasonStats(BaseModel):
    gamesPlayed: int = 0
    goals: int = 0
    assists: int = 0
    points: int = 0
    averageGoals: float = 0.0
    averageAssists: float = 0.0
    averagePoints: float = 0.0
    averageShots: float = 0.0
    shootingPct: float = 0.0
    averageTimeOnIce: float = 0.0


class NHLOpposingTeamStats(BaseModel):
    teamName: str
    wins: int
    losses: int
    otLosses: int = 0
    goalsAllowedPerGame: float = 0.0
    shotsAllowedPerGame: float = 0.0
    savePct: float = 0.0
    powerPlayPct: float = 0.0
    penaltyKillPct: float = 0.0
