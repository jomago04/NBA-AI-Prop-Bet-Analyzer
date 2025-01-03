from pydantic import BaseModel
from typing import List
from ..app.models.playerInfo import PlayerAverageLastFiveGameStats, PlayerSeasonalStats, PlayerOpposingTeamStats

""" original test model for ai query using bs4 scraper logic """
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