from openai import AsyncOpenAI
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def _game_log(games: list, columns: list) -> str:
    """
    Build a plain-text game log table.
    columns: list of (header_label, callable(game) -> value)
    """
    col_w = 7
    header = f"  {'Location':<11}" + "".join(f"{lbl:<{col_w}}" for lbl, _ in columns)
    rows = [header, "  " + "-" * (9 + col_w * len(columns))]
    for g in games:
        loc = f"@ {g.opponent}" if g.isAway else f"vs {g.opponent}"
        row = f"  {loc:<11}"
        for _, fn in columns:
            val = fn(g)
            row += f"{(val if isinstance(val, int) else round(val, 1)):<{col_w}}"
        rows.append(row)
    return "\n".join(rows)


def _trend(games: list, fn, label: str) -> str:
    """Compare last-3 vs last-5 average for a stat, return a readable trend line."""
    if not games:
        return ""
    vals = [fn(g) for g in games]
    avg5 = sum(vals) / len(vals)
    avg3 = sum(vals[:3]) / min(3, len(vals))
    diff = avg3 - avg5
    arrow = "↑ trending up" if diff > 0.4 else "↓ trending down" if diff < -0.4 else "→ stable"
    return f"  {label}: L3 avg {avg3:.1f}  vs  L5 avg {avg5:.1f}  {arrow}"


class NBAAiAnalysis:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        self.client = AsyncOpenAI(api_key=api_key)

    def create_analysis_prompt(self, player_name: str, bet_type: str, line: float, stats: dict) -> str:
        player_info = stats['player_info']
        season_avgs = stats['season_averages']
        l5 = stats['last_five_game_averages']
        opp = stats['opposing_team']
        games = stats.get('individual_last_five_games', [])

        base = f"""Player: {player_name} ({player_info.position}, {player_info.team})
        Days since last game: {player_info.daysSinceLastGame}
        Usage Rate (L5): {l5.averageUsagePercentage:.1f}%  |  True Shooting (L5): {l5.averageTrueShootingPercentage:.1f}%
        ORtg (L5): {l5.averageOffensiveRating:.1f}  |  DRtg (L5): {l5.averageDefensiveRating:.1f}
        """

        opp_block = f"""Opponent: {opp.opponentTeamName} ({opp.opponentWins}-{opp.opponentLosses})
        DRtg: {opp.opponentDefensiveRating}  |  ORtg: {opp.opponentOffensiveRating}  |  Pace: {opp.opponentPaceFactor}
        eFG% allowed: {opp.opponentEffectiveFieldGoalPercentage:.1f}%  |  DReb%: {opp.opponentDefensiveReboundPercentage}
        Steals/g: {opp.opponentAverageSteals}  |  Blocks/g: {opp.opponentAverageBlocks}  |  Pace: {opp.opponentPaceFactor}
        """

        closing = """Provide your response in exactly two sections:

PREDICTION:
- OVER or UNDER
- One-sentence summary
- Confidence: [XX]% (50–95)

ANALYSIS:
"""

        if bet_type.lower() == 'points':
            log = _game_log(games, [
                ("Pts", lambda g: g.points),
                ("Reb", lambda g: g.totalRebounds),
                ("Ast", lambda g: g.assists),
                ("FG%", lambda g: g.fieldGoalPercentage),
                ("Min", lambda g: g.minutesPlayed),
            ])
            trend = _trend(games, lambda g: g.points, "Points")
            return f"""{base}
            POINTS — Line: {line}

            Season averages:  {season_avgs.averagePoints} pts  |  {season_avgs.averageFieldGoalPercentage:.1f}% FG  |  {season_avgs.averageMinutesPlayed} min
            L5 averages:      {l5.averagePoints:.1f} pts  |  {l5.averageFieldGoalPercentage:.1f}% FG  |  {l5.averageMinutesPlayed:.1f} min

            Game log (most recent first):
{log}

            Trend:
{trend}

            {opp_block}
            Opponent pts allowed/g: {opp.opponentAveragePoints}

            {closing}1. Scoring trend: Compare L3 vs L5 and season average.
            2. Efficiency: Is TS% / FG% tracking toward or away from season norms?
            3. Matchup: Opponent DRtg, pts allowed, and interior vs. perimeter defense.
            4. Opportunity: Usage rate, minutes, and pace implications.
            """

        elif bet_type.lower() == 'rebounds':
            log = _game_log(games, [
                ("TReb", lambda g: g.totalRebounds),
                ("OReb", lambda g: g.offensiveRebounds),
                ("DReb", lambda g: g.defensiveRebounds),
                ("Min", lambda g: g.minutesPlayed),
            ])
            trend = _trend(games, lambda g: g.totalRebounds, "Rebounds")
            return f"""{base}
            REBOUNDS — Line: {line}

            Season averages:  {season_avgs.averageTotalRebounds} reb  ({season_avgs.averageOffensiveRebounds} off / {season_avgs.averageDefensiveRebounds} def)  |  {season_avgs.averageMinutesPlayed} min
            L5 averages:      {l5.averageTotalRebounds:.1f} reb  ({l5.averageOffensiveRebounds:.1f} off / {l5.averageDefensiveRebounds:.1f} def)  |  {l5.averageMinutesPlayed:.1f} min

            Game log (most recent first):
{log}

            Trend:
{trend}

            {opp_block}
            Opponent rebounds/g: {opp.opponentAverageTotalRebounds}  |  DReb%: {opp.opponentDefensiveReboundPercentage}

            {closing}1. Rebounding trend: L3 vs L5 vs season.
            2. Role: Offensive vs. defensive rebounding split and positional matchup.
            3. Opponent rebounding: How aggressively does this team box out?
            4. Pace: More possessions = more missed shots = more rebound chances.
            """

        elif bet_type.lower() == 'assists':
            log = _game_log(games, [
                ("Ast", lambda g: g.assists),
                ("Pts", lambda g: g.points),
                ("TOV", lambda g: g.turnovers),
                ("Min", lambda g: g.minutesPlayed),
            ])
            trend = _trend(games, lambda g: g.assists, "Assists")
            return f"""{base}
            ASSISTS — Line: {line}

            Season averages:  {season_avgs.averageAssists} ast  |  {season_avgs.averageTurnovers} tov  |  {season_avgs.averageMinutesPlayed} min
            L5 averages:      {l5.averageAssists:.1f} ast  |  {l5.averageTurnovers:.1f} tov  |  {l5.averageMinutesPlayed:.1f} min

            Game log (most recent first):
{log}

            Trend:
{trend}

            {opp_block}
            Opponent assists/g: {opp.opponentAverageAssists}  |  Steals/g: {opp.opponentAverageSteals}

            {closing}1. Playmaking trend: L3 vs L5 vs season.
            2. Turnover risk: High-pressure defenses inflate turnovers and suppress assists.
            3. Teammate shooting: Poor shooting nights reduce assisted buckets.
            4. Opponent pressure: Assess steal rate and whether they target the ball handler.
            """

        elif bet_type.lower() == 'threes':
            log = _game_log(games, [
                ("3PM", lambda g: g.threePoints),
                ("3PA", lambda g: g.threePointAttempts),
                ("3P%", lambda g: g.threePointPercentage),
                ("Min", lambda g: g.minutesPlayed),
            ])
            trend = _trend(games, lambda g: g.threePoints, "Three-pointers made")
            return f"""{base}
            THREE-POINTERS — Line: {line}

            Season averages:  {season_avgs.averageThreePoints} 3PM  |  {season_avgs.averageThreePointPercentage:.1f}% 3P%  |  {season_avgs.averageMinutesPlayed} min
            L5 averages:      {l5.averageThreePoints:.1f} 3PM  |  {l5.averageThreePointPercentage:.1f}% 3P%  |  {l5.averageThreePointAttempts:.1f} 3PA  |  {l5.averageMinutesPlayed:.1f} min

            Game log (most recent first):
{log}

            Trend:
{trend}

            {opp_block}
            Opponent 3P% allowed: {opp.opponentOpponentThreePointPercentage:.1f}%  |  3P rate: {opp.opponentThreePointRate}

            {closing}1. Volume and efficiency: Attempt rate and 3P% vs. season norms.
            2. Shot quality: Are makes coming in rhythm or as forced looks?
            3. Perimeter defense: Opponent 3P% allowed and how they contest the arc.
            4. Game script: Pace and offensive scheme — does this matchup encourage or suppress threes?
            """

        elif bet_type.lower() == 'steals':
            log = _game_log(games, [
                ("Stl", lambda g: g.steals),
                ("Blk", lambda g: g.blocks),
                ("Pts", lambda g: g.points),
                ("Min", lambda g: g.minutesPlayed),
            ])
            trend = _trend(games, lambda g: g.steals, "Steals")
            return f"""{base}
            STEALS — Line: {line}

            Season averages:  {season_avgs.averageSteals} stl/g  |  {season_avgs.averageMinutesPlayed} min
            L5 averages:      {l5.averageSteals:.1f} stl/g  |  {l5.averageMinutesPlayed:.1f} min

            Game log (most recent first):
{log}

            Trend:
{trend}

            {opp_block}
            Opponent turnovers/g: {opp.opponentAverageTurnovers}  |  Opponent assists/g: {opp.opponentAverageAssists}

            {closing}1. Steal trend: L3 vs L5 vs season — is the player in an active defensive stretch?
            2. Defensive role: Does the player gamble for steals or play disciplined defense?
            3. Opponent ball-handling: Teams with high turnovers and ball movement create more steal opportunities.
            4. Variance: Steals are highly game-to-game variable — note the consistency across the game log.
            """

        elif bet_type.lower() == 'blocks':
            log = _game_log(games, [
                ("Blk", lambda g: g.blocks),
                ("Stl", lambda g: g.steals),
                ("Reb", lambda g: g.totalRebounds),
                ("Min", lambda g: g.minutesPlayed),
            ])
            trend = _trend(games, lambda g: g.blocks, "Blocks")
            return f"""{base}
            BLOCKS — Line: {line}

            Season averages:  {season_avgs.averageBlocks} blk/g  |  {season_avgs.averageMinutesPlayed} min
            L5 averages:      {l5.averageBlocks:.1f} blk/g  |  {l5.averageMinutesPlayed:.1f} min

            Game log (most recent first):
{log}

            Trend:
{trend}

            {opp_block}
            Opponent field goals/g: {opp.opponentAverageFieldGoals}  |  Two-pointers/g: {opp.opponentAverageTwoPoints}

            {closing}1. Block trend: L3 vs L5 vs season — recent rim-protection activity.
            2. Defensive positioning: Does the player play help defense or stay attached to their man?
            3. Opponent interior attack: Teams that attack the paint frequently create more block opportunities.
            4. Foul trouble risk: Aggressive shot-blocking can lead to foul trouble and reduced minutes.
            """

        elif bet_type.lower() == 'pra':
            pra_vals = [g.points + g.totalRebounds + g.assists for g in games]
            avg_pra_l5 = sum(pra_vals) / len(pra_vals) if pra_vals else 0.0
            avg_pra_l3 = sum(pra_vals[:3]) / min(3, len(pra_vals)) if pra_vals else 0.0
            log = _game_log(games, [
                ("Pts", lambda g: g.points),
                ("Reb", lambda g: g.totalRebounds),
                ("Ast", lambda g: g.assists),
                ("PRA", lambda g: g.points + g.totalRebounds + g.assists),
                ("Min", lambda g: g.minutesPlayed),
            ])
            pra_diff = avg_pra_l3 - avg_pra_l5
            pra_arrow = "↑ trending up" if pra_diff > 1.0 else "↓ trending down" if pra_diff < -1.0 else "→ stable"
            season_pra = season_avgs.averagePoints + season_avgs.averageTotalRebounds + season_avgs.averageAssists
            return f"""{base}
            POINTS + REBOUNDS + ASSISTS (PRA) — Line: {line}

            Season averages:  {season_avgs.averagePoints} pts + {season_avgs.averageTotalRebounds} reb + {season_avgs.averageAssists} ast = {season_pra:.1f} PRA
            L5 averages:      {l5.averagePoints:.1f} pts + {l5.averageTotalRebounds:.1f} reb + {l5.averageAssists:.1f} ast = {avg_pra_l5:.1f} PRA

            Game log (most recent first):
{log}

            Trend:
              PRA: L3 avg {avg_pra_l3:.1f}  vs  L5 avg {avg_pra_l5:.1f}  {pra_arrow}
{_trend(games, lambda g: g.points, "Points")}
{_trend(games, lambda g: g.totalRebounds, "Rebounds")}
{_trend(games, lambda g: g.assists, "Assists")}

            {opp_block}
            Opponent pts allowed/g: {opp.opponentAveragePoints}  |  Opponent reb/g: {opp.opponentAverageTotalRebounds}

            {closing}1. Combined PRA trend: Is the player tracking above or below the line across recent games?
            2. Scoring component: Efficiency and usage impact on points contribution.
            3. Rebounding component: Minutes and matchup implications for boards.
            4. Assists component: Playmaking role and opponent defensive pressure on ball handlers.
            5. Opponent pace and defense: High-pace games with a weaker defense inflate all three categories.
            """

        else:
            raise ValueError(f"Unsupported bet type: {bet_type}")

    async def analyze_bet(self, player_name: str, bet_type: str, line: float, stats: dict) -> str:
        prompt = self.create_analysis_prompt(player_name, bet_type, line, stats)

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert NBA prop bet analyst. "
                        "Structure every response in exactly two sections:\n\n"
                        "PREDICTION:\n"
                        "- OVER or UNDER\n"
                        "- One-sentence summary of your call\n"
                        "- Confidence: [XX]% (use 50–95; below 50 is not actionable)\n\n"
                        "ANALYSIS:\n"
                        "Detailed, numbered analysis of every factor listed in the prompt. "
                        "Be specific — reference actual stat values, not vague statements."
                    )
                },
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content
