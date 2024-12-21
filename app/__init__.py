"""
NBA Stats Scraper Package
Main package initialization
"""

from .services.scraperLogic import PlayerService
from .models.playerInfo import (
    PlayerAverageLastFiveGameStats,
    PlayerSeasonalStats,
    PlayerOpposingTeamStats
)

__version__ = "0.0.1"
__author__ = "Joshua Gould"
