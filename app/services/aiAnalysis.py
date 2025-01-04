from openai import OpenAI
import os
from dotenv import load_dotenv


class NBAAiAnalysis:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
            
    def create_analysis_prompt(self, player_name: str, bet_type: str, line: float, stats: dict):
        player_info = stats['player_info']
        season_averages = stats['season_averages']
        season_totals = stats['season_totals']
        last_five_game_averages = stats['last_five_game_averages']
        opposing_team = stats['opposing_team']
        individual_last_five_games = stats['individual_last_five_games']

        return f"""
        Analyze this bet for {player_name}:
        {bet_type.upper()} line: {line}

        Last 5 Games Average:
        Points: {last_five_game_averages.averagePoints}
        Rebounds: {last_five_game_averages.averageTotalRebounds}
        Assists: {last_five_game_averages.averageAssists}
        Minutes: {last_five_game_averages.averageMinutesPlayed}

        Season Averages:
        Points: {season_averages.averagePoints}
        Rebounds: {season_averages.averageTotalRebounds}
        Assists: {season_averages.averageAssists}
        Minutes: {season_averages.averageMinutesPlayed}

        Additional Context:
        - Days since last game: {player_info.daysSinceLastGame}
        - Usage rate (last 5): {last_five_game_averages.averageUsagePercentage}%
        - True shooting (last 5): {last_five_game_averages.averageTrueShootingPercentage}%
        - Team: {player_info.team}
        - Position: {player_info.position}
        - Opposing Team: {opposing_team.opponentTeamName} ({opposing_team.opponentWins}-{opposing_team.opponentLosses})

        Based on these statistics, should I bet OVER or UNDER {line} {bet_type}?
        Provide a brief explanation with your prediction and provide a confidence score from 0 to 100.
        """

    async def analyze_bet(self, player_name: str, bet_type: str, line: float, stats: dict):

        # Create prompt
        prompt = self.create_analysis_prompt(player_name, bet_type, line, stats)

        # Get GPT prediction
        response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a master sports betting analyst."},
                    {"role": "user", "content": prompt}
                ]
            )

        return response.choices[0].message.content