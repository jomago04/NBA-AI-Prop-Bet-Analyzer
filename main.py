from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services.runScraper import GetNBAPlayerStats
from app.services.aiAnalysis import NBAAiAnalysis
from dotenv import load_dotenv

load_dotenv()
# Create the FastAPI app instance
app = FastAPI()
player_stats = GetNBAPlayerStats()
ai_analysis = NBAAiAnalysis()

# Define what our AI query request should look like
class BetRequest(BaseModel):
    player_name: str
    bet_type: str
    line: float
    
@app.post("/analyze")
async def analyzeBet(bet_request: BetRequest):
    try:
        player_info, season_averages, season_totals, last_five_game_averages, opposing_team, individual_last_five_games = (
            player_stats.getAllPlayerStats(bet_request.player_name)
        )
        
        if not all([player_info, season_averages, season_totals, last_five_game_averages, opposing_team, individual_last_five_games]):
            raise HTTPException(status_code=404, detail="Failure to retrieve player stats")

        analysis = await ai_analysis.analyze_bet(
            player_name = bet_request.player_name,
            bet_type = bet_request.bet_type,
            line = bet_request.line,
            stats = {
                'player_info': player_info,              # PlayerInfo instance
                'season_averages': season_averages,      # PlayerCurrentSeasonAverageStats instance
                'season_totals': season_totals,
                'last_five_game_averages': last_five_game_averages,
                'opposing_team': opposing_team,           # PlayerOpposingTeamStats instance
                'individual_last_five_games': individual_last_five_games
            }
        )
        
        return {
            "player": bet_request.player_name,
            "bet_type": bet_request.bet_type,
            "line": bet_request.line,
            "analysis": analysis,
            # TODO: Add stats_used back in but actually have it be the stats used especially will be useful when additional prompt engineering is used
            #"stats_used": {
            #    "recent_games": last_five_game_averages,
            #    "season_averages": season_averages
            #}
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


