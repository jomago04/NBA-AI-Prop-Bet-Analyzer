from pydantic import BaseModel
from typing import List
from .playerInfo import PlayerAverageLastFiveGameStats, PlayerSeasonalStats, PlayerOpposingTeamStats

class AIQueryInput(BaseModel):
    player_last_five: PlayerAverageLastFiveGameStats
    player_seasonal: PlayerSeasonalStats
    opposing_team: PlayerOpposingTeamStats
    prop_type: str
    prop_line: float

class AIQueryResponse(BaseModel):
    prediction: str  # "over" or "under"
    confidence: float
    reasoning: str
    key_stats: List[str]
    risk_level: str