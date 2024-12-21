"""
NBA Stats Models
Contains data models for player and team statistics
"""

from .playerInfo import (
    PlayerAverageLastFiveGameStats,
    PlayerSeasonalStats,
    PlayerOpposingTeamStats
)

# This allows you to import directly from models:
# from app.models import PlayerSeasonalStats