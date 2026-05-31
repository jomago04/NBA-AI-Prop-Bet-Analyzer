from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator
from typing import Literal, Optional
from app.services.runScraper import GetNBAPlayerStats
from app.services.aiAnalysis import NBAAiAnalysis
from app.services.outcomeTracker import OutcomeTracker
from app.models.betRecord import SettleOutcomeRequest
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

AI_MODEL = "gpt-4o-mini"

player_stats = GetNBAPlayerStats()
ai_analysis = NBAAiAnalysis()
outcome_tracker = OutcomeTracker()

class BetRequest(BaseModel):
    player_name: str
    bet_type: Literal['points', 'rebounds', 'assists', 'threes']
    line: float
    game_date: Optional[str] = None  # ISO date the bet applies to (optional)

    @field_validator('player_name')
    @classmethod
    def player_name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Player name cannot be empty')
        return v

    @field_validator('line')
    @classmethod
    def line_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Line must be a positive number')
        return v

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze")
async def analyzeBet(bet_request: BetRequest):
    try:
        player_info, season_averages, season_totals, last_five_game_averages, opposing_team, individual_last_five_games = (
            player_stats.getAllPlayerStats(bet_request.player_name)
        )

        if not all([player_info, season_averages, season_totals, last_five_game_averages, opposing_team, individual_last_five_games]):
            raise HTTPException(status_code=404, detail=f"Could not retrieve stats for '{bet_request.player_name}'. Check the player name and try again.")

        analysis = await ai_analysis.analyze_bet(
            player_name=bet_request.player_name,
            bet_type=bet_request.bet_type,
            line=bet_request.line,
            stats={
                'player_info': player_info,
                'season_averages': season_averages,
                'season_totals': season_totals,
                'last_five_game_averages': last_five_game_averages,
                'opposing_team': opposing_team,
                'individual_last_five_games': individual_last_five_games
            }
        )

        # Persist the analysis so its prediction can later be graded against the
        # real bet outcome and fed into accuracy / backtesting reports.
        record = outcome_tracker.record_analysis(
            player_name=bet_request.player_name,
            bet_type=bet_request.bet_type,
            line=bet_request.line,
            analysis_text=analysis,
            model=AI_MODEL,
            game_date=bet_request.game_date,
        )

        return {
            "id": record.id,
            "player": bet_request.player_name,
            "bet_type": bet_request.bet_type,
            "line": bet_request.line,
            "predicted_direction": record.predicted_direction,
            "confidence": record.confidence,
            "analysis": analysis,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyses/{analysis_id}/outcome")
async def settle_analysis_outcome(analysis_id: int, outcome: SettleOutcomeRequest):
    """Record the real result of a bet and grade the AI's prediction.

    Submit the actual stat value (e.g. the points the player actually scored).
    The system computes whether the real outcome was OVER/UNDER/PUSH the line
    and whether the AI's prediction was correct.
    """
    record = outcome_tracker.settle_outcome(analysis_id, outcome.actual_value)
    if record is None:
        raise HTTPException(status_code=404, detail=f"No analysis found with id {analysis_id}")
    return record


@app.get("/analyses/{analysis_id}")
async def get_analysis(analysis_id: int):
    """Fetch a single stored analysis (and its outcome if settled)."""
    record = outcome_tracker.get_analysis(analysis_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"No analysis found with id {analysis_id}")
    return record


@app.get("/analyses")
async def list_analyses(
    status: Optional[str] = None,
    player_name: Optional[str] = None,
    bet_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
):
    """List stored analyses with optional filtering (supports date ranges)."""
    return outcome_tracker.list_analyses(
        status=status,
        player_name=player_name,
        bet_type=bet_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )


@app.get("/stats/accuracy")
async def accuracy_stats(
    player_name: Optional[str] = None,
    bet_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """Aggregate how often the bot's predictions were correct.

    Filterable by player, bet type, and date range. This is the foundation for
    the upcoming feature that simulates a period in time to test the bot's
    probability outcomes.
    """
    return outcome_tracker.accuracy_stats(
        player_name=player_name,
        bet_type=bet_type,
        start_date=start_date,
        end_date=end_date,
    )
