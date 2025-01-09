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
        last_five_game_averages = stats['last_five_game_averages']
        opposing_team = stats['opposing_team']
        
        base_prompt = f"""
        Player: {player_name} ({player_info.position}, {player_info.team}) 
        Days since last game: {player_info.daysSinceLastGame}
        Usage Rate: {last_five_game_averages.averageUsagePercentage}%
        True Shooting: {last_five_game_averages.averageTrueShootingPercentage}%
        Offensive Rating: {last_five_game_averages.averageOffensiveRating}
        Defensive Rating: {last_five_game_averages.averageDefensiveRating}
        """
        
        base_opposing_team_prompt = f"""
        Opposing Team: {opposing_team.opponentTeamName} ({opposing_team.opponentWins}-{opposing_team.opponentLosses})
        Opposing Team Average Season Stats: 
        Steals: {opposing_team.opponentAverageSteals}
        Blocks: {opposing_team.opponentAverageBlocks}
        Turnovers: {opposing_team.opponentAverageTurnovers}
        
        Offensive Rating: {opposing_team.opponentOffensiveRating}
        Defensive Rating: {opposing_team.opponentDefensiveRating}
        Pace Factor: {opposing_team.opponentPaceFactor}
        Effective Field Goal Percentage: {opposing_team.opponentEffectiveFieldGoalPercentage}
        Turnover Percentage: {opposing_team.opponentTurnoverPercentage}
        Defensive Rebound Percentage: {opposing_team.opponentDefensiveReboundPercentage}
        Free Throw Rate: {opposing_team.opponentFreeThrowRate}
        Three Point Rate: {opposing_team.opponentThreePointRate}
        """
        
        if bet_type.lower() == 'points':
            return f"""{base_prompt}
            POINTS Analysis for line: {line}

            Recent Performance (Last 5 Game Averages):
            - Points: {last_five_game_averages.averagePoints}
            - Minutes: {last_five_game_averages.averageMinutesPlayed}
            - True Shooting: {last_five_game_averages.averageTrueShootingPercentage}%
            - Field Goal %: {last_five_game_averages.averageFieldGoalPercentage}%

            Season Averages:
            - Points: {season_averages.averagePoints}
            - Minutes: {season_averages.averageMinutesPlayed}
            - Field Goal %: {season_averages.averageFieldGoalPercentage}%

            {base_opposing_team_prompt}
            Points: {opposing_team.opponentAveragePoints}

            Analyze the likelihood of {player_name} scoring OVER/UNDER {line} points. Consider:
            1. Recent scoring trend and efficiency
            2. Minutes played and usage rate
            3. Opponent's defensive metrics
            4. Rest days impact

            Provide your response in two clearly separated sections:

            PREDICTION:
            - State clearly if this is an OVER or UNDER
            - Give a one-sentence summary of your call

            ANALYSIS:
            Provide a detailed analysis considering:
            1. [bet-type specific factors...]
            2. [bet-type specific factors...]
            3. [bet-type specific factors...]
            4. [bet-type specific factors...]
            """
        elif bet_type.lower() == "rebounds":
            return f"""{base_prompt}
            REBOUNDS Analysis for line: {line}

            Recent Performance (Last 5 Game Averages):
            - Total Rebounds: {last_five_game_averages.averageTotalRebounds}
            - Offensive Rebounds: {last_five_game_averages.averageOffensiveRebounds}
            - Defensive Rebounds: {last_five_game_averages.averageDefensiveRebounds}
            - Minutes: {last_five_game_averages.averageMinutesPlayed}
            
            Season Averages:
            - Total Rebounds: {season_averages.averageTotalRebounds}
            - Offensive Rebounds: {season_averages.averageOffensiveRebounds}
            - Defensive Rebounds: {season_averages.averageDefensiveRebounds}
            - Minutes: {season_averages.averageMinutesPlayed}

            {base_opposing_team_prompt}
            Rebounds: {opposing_team.opponentAverageTotalRebounds}
            Offensive Rebounds: {opposing_team.opponentAverageOffensiveRebounds}
            Defensive Rebounds: {opposing_team.opponentAverageDefensiveRebounds}

            Analyze the likelihood of {player_name} getting OVER/UNDER {line} rebounds. Consider:
            1. Recent rebounding trend
            2. Minutes played and positioning
            3. Opponent's rebounding metrics
            4. Team rebounding scheme

            Provide your response in two clearly separated sections:

            PREDICTION:
            - State clearly if this is an OVER or UNDER
            - Give a one-sentence summary of your call

            ANALYSIS:
            Provide a detailed analysis considering:
            1. [bet-type specific factors...]
            2. [bet-type specific factors...]
            3. [bet-type specific factors...]
            4. [bet-type specific factors...]
            """

        elif bet_type.lower() == "assists":
            return f"""{base_prompt}
            ASSISTS Analysis for line: {line}

            Recent Performance (Last 5 Game Averages):
            - Assists: {last_five_game_averages.averageAssists}
            - Minutes: {last_five_game_averages.averageMinutesPlayed}
            - Turnovers: {last_five_game_averages.averageTurnovers}
            
            Season Averages:
            - Assists: {season_averages.averageAssists}
            - Minutes: {season_averages.averageMinutesPlayed}
            - Turnovers: {season_averages.averageTurnovers}

            
            {base_opposing_team_prompt}
            - Team Assists: {opposing_team.opponentAverageAssists}

            Analyze the likelihood of {player_name} getting OVER/UNDER {line} assists. Consider:
            1. Recent playmaking trend
            2. Ball-handling responsibilities
            3. Team's offensive scheme
            4. Opponent's defensive pressure

            Provide your response in two clearly separated sections:

            PREDICTION:
            - State clearly if this is an OVER or UNDER
            - Give a one-sentence summary of your call

            ANALYSIS:
            Provide a detailed analysis considering:
            1. [bet-type specific factors...]
            2. [bet-type specific factors...]
            3. [bet-type specific factors...]
            4. [bet-type specific factors...]
            """

        elif bet_type.lower() == "threes":
            return f"""{base_prompt}
            THREE POINTERS Analysis for line: {line}

            Recent Performance (Last 5 Game Averages):
            - Three Pointers Made: {last_five_game_averages.averageThreePoints}
            - Three Point Attempts: {last_five_game_averages.averageThreePointAttempts}
            - Three Point %: {last_five_game_averages.averageThreePointPercentage}%
            - Minutes: {last_five_game_averages.averageMinutesPlayed}
            
            Season Averages:
            - Three Pointers Made: {season_averages.averageThreePoints}
            - Three Point %: {season_averages.averageThreePointPercentage}%
            - Minutes: {season_averages.averageMinutesPlayed}

            {base_opposing_team_prompt}
            - Three Point % Allowed: {opposing_team.opponentOpponentThreePointPercentage}%
            - Three Point Rate: {opposing_team.opponentThreePointRate}

            Analyze the likelihood of {player_name} making OVER/UNDER {line} three-pointers. Consider:
            1. Recent three-point shooting trend
            2. Volume of attempts
            3. Opponent's perimeter defense
            4. Team's offensive style

            Provide your response in two clearly separated sections:

            PREDICTION:
            - State clearly if this is an OVER or UNDER
            - Give a one-sentence summary of your call

            ANALYSIS:
            Provide a detailed analysis considering:
            1. [bet-type specific factors...]
            2. [bet-type specific factors...]
            3. [bet-type specific factors...]
            4. [bet-type specific factors...]
            """

        else:
            raise ValueError(f"Unsupported bet type: {bet_type}")

    async def analyze_bet(self, player_name: str, bet_type: str, line: float, stats: dict):

        # Create prompt
        prompt = self.create_analysis_prompt(player_name, bet_type, line, stats)

        # Get GPT prediction
        response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """You are a master sports betting analyst. 
                    Always structure your response in exactly two parts:
                    
                    PREDICTION:
                    - Clear OVER/UNDER call
                    - One-sentence summary
                    
                    ANALYSIS:
                    Detailed analysis of all relevant factors supporting your prediction."""},
                    {"role": "user", "content": prompt}
                ]
            )

        return response.choices[0].message.content