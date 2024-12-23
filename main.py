from fastapi import FastAPI, HTTPException
from app.services.scraperLogic import PlayerService
from app.services.aiService import AIAnalysisService
from app.models.aiQuery import AIQueryInput

app = FastAPI(title="NBA Props Analysis API")
player_service = PlayerService()
ai_service = AIAnalysisService()

@app.get("/")
async def root():
    return {"message": "Welcome to NBA Props Analysis API"}

@app.get("/player/{player_name}")
async def get_player_analysis(player_name: str, prop_type: str, prop_line: float):
    try:
        # Get player data
        player_response = player_service.get_nbaplayer_url(player_name)
        
        # Get all required stats
        last_five_stats = player_service.get_nbaplayer_5game_stats(player_response)
        seasonal_stats = player_service.get_nbaplayer_seasonal_stats(player_response)
        
        # Get opposing team stats
        opposing_team_url = player_service.get_nbaplayer_opposingteam_url(player_response)
        opposing_team_stats = player_service.get_opposing_team_stats(opposing_team_url)
        
        # Package for AI analysis
        query = AIQueryInput(
            player_last_five=last_five_stats,
            player_seasonal=seasonal_stats,
            opposing_team=opposing_team_stats,
            prop_type=prop_type,
            prop_line=prop_line
        )
        
        # Get AI prediction
        analysis = await ai_service.analyze_prop_bet(query)
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))