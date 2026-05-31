from openai import AsyncOpenAI
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class NBAAiAnalysis:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")

        self.client = AsyncOpenAI(api_key=api_key)

    def create_analysis_prompt(self, player_name: str, bet_type: str, line: float, stats: dict):
        player_info = stats['player_info']
        season_averages = stats['season_averages']
        last_five_game_averages = stats['last_five_game_averages']
        opposing_team = stats['opposing_team']

        base_prompt = f"""
        Player: {player_name} ({player_info.position}, {player_info.team})
        Days since last game: {player_info.daysSinceLastGame}
        Usage Rate (L5): {last_five_game_averages.averageUsagePercentage:.1f}%
        True Shooting (L5): {last_five_game_averages.averageTrueShootingPercentage:.1f}%
        Offensive Rating (L5): {last_five_game_averages.averageOffensiveRating:.1f}
        Defensive Rating (L5): {last_five_game_averages.averageDefensiveRating:.1f}
        """

        base_opposing_team_prompt = f"""
        Opposing Team: {opposing_team.opponentTeamName} ({opposing_team.opponentWins}-{opposing_team.opponentLosses})
        Opposing Team Season Averages:
        - Steals: {opposing_team.opponentAverageSteals}
        - Blocks: {opposing_team.opponentAverageBlocks}
        - Turnovers: {opposing_team.opponentAverageTurnovers}

        Offensive Rating: {opposing_team.opponentOffensiveRating}
        Defensive Rating: {opposing_team.opponentDefensiveRating}
        Pace Factor: {opposing_team.opponentPaceFactor}
        Effective FG%: {opposing_team.opponentEffectiveFieldGoalPercentage:.1f}%
        Turnover %: {opposing_team.opponentTurnoverPercentage}
        Defensive Rebound %: {opposing_team.opponentDefensiveReboundPercentage}
        Free Throw Rate: {opposing_team.opponentFreeThrowRate}
        Three Point Rate: {opposing_team.opponentThreePointRate}
        """

        if bet_type.lower() == 'points':
            return f"""{base_prompt}
            POINTS Analysis for line: {line}

            Recent Performance (Last 5 Game Averages):
            - Points: {last_five_game_averages.averagePoints:.1f}
            - Minutes: {last_five_game_averages.averageMinutesPlayed:.1f}
            - True Shooting: {last_five_game_averages.averageTrueShootingPercentage:.1f}%
            - Field Goal %: {last_five_game_averages.averageFieldGoalPercentage:.1f}%

            Season Averages:
            - Points: {season_averages.averagePoints}
            - Minutes: {season_averages.averageMinutesPlayed}
            - Field Goal %: {season_averages.averageFieldGoalPercentage:.1f}%

            {base_opposing_team_prompt}
            Opponent Points Allowed Per Game: {opposing_team.opponentAveragePoints}

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
            1. Scoring trend: Is the player trending up or down over the last 5 games vs. their season average?
            2. Efficiency metrics: Evaluate true shooting %, field goal %, and how they compare to season norms.
            3. Defensive matchup: Assess the opponent's defensive rating, points allowed, and perimeter vs. interior defense.
            4. Usage and pace: Consider usage rate, minutes, and how the opponent's pace factor affects total scoring opportunities.
            """

        elif bet_type.lower() == "rebounds":
            return f"""{base_prompt}
            REBOUNDS Analysis for line: {line}

            Recent Performance (Last 5 Game Averages):
            - Total Rebounds: {last_five_game_averages.averageTotalRebounds:.1f}
            - Offensive Rebounds: {last_five_game_averages.averageOffensiveRebounds:.1f}
            - Defensive Rebounds: {last_five_game_averages.averageDefensiveRebounds:.1f}
            - Minutes: {last_five_game_averages.averageMinutesPlayed:.1f}

            Season Averages:
            - Total Rebounds: {season_averages.averageTotalRebounds}
            - Offensive Rebounds: {season_averages.averageOffensiveRebounds}
            - Defensive Rebounds: {season_averages.averageDefensiveRebounds}
            - Minutes: {season_averages.averageMinutesPlayed}

            {base_opposing_team_prompt}
            Opponent Rebounds Per Game: {opposing_team.opponentAverageTotalRebounds}
            Opponent Offensive Rebounds: {opposing_team.opponentAverageOffensiveRebounds}
            Opponent Defensive Rebounds: {opposing_team.opponentAverageDefensiveRebounds}
            Opponent Defensive Rebound %: {opposing_team.opponentDefensiveReboundPercentage}

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
            1. Rebounding trend: Is the player's rebounding rate rising or falling compared to their season average?
            2. Role and positioning: Evaluate offensive vs. defensive rebounding splits and how they match up with this opponent.
            3. Opponent rebounding defense: Consider the opponent's defensive rebound % and how aggressively they box out.
            4. Pace and opportunities: A higher-paced game creates more missed shots and rebounds for both teams.
            """

        elif bet_type.lower() == "assists":
            return f"""{base_prompt}
            ASSISTS Analysis for line: {line}

            Recent Performance (Last 5 Game Averages):
            - Assists: {last_five_game_averages.averageAssists:.1f}
            - Minutes: {last_five_game_averages.averageMinutesPlayed:.1f}
            - Turnovers: {last_five_game_averages.averageTurnovers:.1f}

            Season Averages:
            - Assists: {season_averages.averageAssists}
            - Minutes: {season_averages.averageMinutesPlayed}
            - Turnovers: {season_averages.averageTurnovers}

            {base_opposing_team_prompt}
            Opponent Team Assists: {opposing_team.opponentAverageAssists}
            Opponent Steals Per Game: {opposing_team.opponentAverageSteals}

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
            1. Playmaking trend: Is the player's assist rate consistent or variable over the last 5 games vs. season average?
            2. Turnover risk: Consider the assist-to-turnover ratio; a high turnover rate may indicate defensive pressure limiting assists.
            3. Opponent pressure: Assess the opponent's steal rate and defensive rating; aggressive defenses disrupt passing lanes.
            4. Team shooting: Consider teammates' recent shooting efficiency, as poor shooting reduces potential assisted buckets.
            """

        elif bet_type.lower() == "threes":
            return f"""{base_prompt}
            THREE POINTERS Analysis for line: {line}

            Recent Performance (Last 5 Game Averages):
            - Three Pointers Made: {last_five_game_averages.averageThreePoints:.1f}
            - Three Point Attempts: {last_five_game_averages.averageThreePointAttempts:.1f}
            - Three Point %: {last_five_game_averages.averageThreePointPercentage:.1f}%
            - Minutes: {last_five_game_averages.averageMinutesPlayed:.1f}

            Season Averages:
            - Three Pointers Made: {season_averages.averageThreePoints}
            - Three Point %: {season_averages.averageThreePointPercentage:.1f}%
            - Minutes: {season_averages.averageMinutesPlayed}

            {base_opposing_team_prompt}
            Opponent 3P% Allowed: {opposing_team.opponentOpponentThreePointPercentage:.1f}%
            Opponent Three Point Rate: {opposing_team.opponentThreePointRate}

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
            1. Volume and efficiency: Is the player taking and making threes at a consistent rate vs. their season average?
            2. Shot creation: Consider whether the player is generating high-quality looks or forced attempts.
            3. Opponent perimeter defense: Assess the opponent's three-point percentage allowed and how they guard the arc.
            4. Game script: Consider whether pace and offensive scheme encourage or limit three-point attempts in this matchup.
            """

        else:
            raise ValueError(f"Unsupported bet type: {bet_type}")

    async def analyze_bet(self, player_name: str, bet_type: str, line: float, stats: dict):
        prompt = self.create_analysis_prompt(player_name, bet_type, line, stats)

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """You are an expert sports betting analyst specializing in NBA player props.
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
