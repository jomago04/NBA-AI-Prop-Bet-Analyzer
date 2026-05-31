"""
Pydantic models for persisted bet analyses and their settled outcomes.

These mirror the `bet_analyses` table and are used both for API request/response
bodies and for passing rows around the application in a type-safe way.
"""

from pydantic import BaseModel, field_validator
from typing import Literal, Optional


BetType = Literal["points", "rebounds", "assists", "threes"]
Direction = Literal["OVER", "UNDER", "UNKNOWN"]
ActualDirection = Literal["OVER", "UNDER", "PUSH"]


class BetAnalysisRecord(BaseModel):
    """A full row from the bet_analyses table."""
    id: int
    player_name: str
    bet_type: str
    line: float

    predicted_direction: str
    confidence: Optional[float] = None
    analysis_text: Optional[str] = None
    model: Optional[str] = None

    game_date: Optional[str] = None
    created_at: str

    status: str
    actual_value: Optional[float] = None
    actual_direction: Optional[str] = None
    correct: Optional[bool] = None
    settled_at: Optional[str] = None


class SettleOutcomeRequest(BaseModel):
    """Request body for settling a bet with its real-world result."""
    actual_value: float

    @field_validator("actual_value")
    @classmethod
    def actual_value_not_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Actual value cannot be negative")
        return v


class AccuracyStats(BaseModel):
    """Aggregate accuracy metrics over a set of settled analyses."""
    total_analyses: int
    pending: int
    settled: int
    pushes: int
    correct: int
    incorrect: int
    accuracy: Optional[float] = None  # correct / (correct + incorrect)
    by_bet_type: dict = {}
    by_direction: dict = {}
