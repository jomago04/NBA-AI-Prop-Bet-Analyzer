from pydantic import BaseModel
from typing import Optional


class NFLPlayerInfo(BaseModel):
    name: str
    team: str
    position: str       # QB, RB, WR, TE, K, etc.
    age: int
    daysSinceLastGame: int


class NFLGameStats(BaseModel):
    opponent: str
    isAway: bool
    # Passing
    completions: int = 0
    passAttempts: int = 0
    passYards: int = 0
    passTDs: int = 0
    interceptions: int = 0
    passerRating: float = 0.0
    # Rushing
    rushAttempts: int = 0
    rushYards: int = 0
    rushTDs: int = 0
    # Receiving
    targets: int = 0
    receptions: int = 0
    recYards: int = 0
    recTDs: int = 0


class NFLLastFiveAverages(BaseModel):
    averagePassYards: float = 0.0
    averagePassTDs: float = 0.0
    averageInterceptions: float = 0.0
    averagePasserRating: float = 0.0
    averageRushYards: float = 0.0
    averageRushTDs: float = 0.0
    averageReceptions: float = 0.0
    averageRecYards: float = 0.0
    averageRecTDs: float = 0.0
    averageTargets: float = 0.0


class NFLSeasonStats(BaseModel):
    gamesPlayed: int = 0
    averagePassYards: float = 0.0
    averagePassTDs: float = 0.0
    averageInterceptions: float = 0.0
    averagePasserRating: float = 0.0
    averageRushYards: float = 0.0
    averageRushTDs: float = 0.0
    averageReceptions: float = 0.0
    averageRecYards: float = 0.0
    averageRecTDs: float = 0.0
    averageTargets: float = 0.0
    completionPct: float = 0.0


class NFLOpposingTeamStats(BaseModel):
    teamName: str
    wins: int
    losses: int
    pointsAllowedPerGame: float = 0.0
    passYardsAllowedPerGame: float = 0.0
    rushYardsAllowedPerGame: float = 0.0
    totalYardsAllowedPerGame: float = 0.0
    sacks: float = 0.0
    interceptions: float = 0.0
    touchdownsAllowed: float = 0.0
