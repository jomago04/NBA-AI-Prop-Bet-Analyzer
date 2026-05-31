from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator
from typing import Literal
from app.services.runScraper import GetNBAPlayerStats
from app.services.aiAnalysis import NBAAiAnalysis
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

player_stats = GetNBAPlayerStats()
ai_analysis = NBAAiAnalysis()

class BetRequest(BaseModel):
    player_name: str
    bet_type: Literal['points', 'rebounds', 'assists', 'threes']
    line: float

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

        return {
            "player": bet_request.player_name,
            "bet_type": bet_request.bet_type,
            "line": bet_request.line,
            "analysis": analysis,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
