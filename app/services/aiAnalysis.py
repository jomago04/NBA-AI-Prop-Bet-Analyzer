from openai import AsyncOpenAI
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

_RESPONSE_TEMPLATE = """Provide your response in exactly two sections:

PREDICTION:
- OVER or UNDER
- One-sentence summary
- Confidence: [XX]% (50–95)

ANALYSIS:
"""

_SYSTEM_PROMPTS = {
    'nba': (
        "You are an expert NBA prop bet analyst. "
        "Structure every response in exactly two sections:\n\n"
        "PREDICTION:\n- OVER or UNDER\n- One-sentence summary of your call\n"
        "- Confidence: [XX]% (use 50–95; below 50 is not actionable)\n\n"
        "ANALYSIS:\nDetailed, numbered analysis of every factor listed in the prompt. "
        "Be specific — reference actual stat values, not vague statements."
    ),
    'nfl': (
        "You are an expert NFL prop bet analyst. "
        "Structure every response in exactly two sections:\n\n"
        "PREDICTION:\n- OVER or UNDER\n- One-sentence summary of your call\n"
        "- Confidence: [XX]% (use 50–95)\n\n"
        "ANALYSIS:\nDetailed, numbered analysis referencing actual stat values."
    ),
    'mlb': (
        "You are an expert MLB prop bet analyst. "
        "Structure every response in exactly two sections:\n\n"
        "PREDICTION:\n- OVER or UNDER\n- One-sentence summary of your call\n"
        "- Confidence: [XX]% (use 50–95)\n\n"
        "ANALYSIS:\nDetailed, numbered analysis referencing actual stat values."
    ),
    'nhl': (
        "You are an expert NHL prop bet analyst. "
        "Structure every response in exactly two sections:\n\n"
        "PREDICTION:\n- OVER or UNDER\n- One-sentence summary of your call\n"
        "- Confidence: [XX]% (use 50–95)\n\n"
        "ANALYSIS:\nDetailed, numbered analysis referencing actual stat values."
    ),
    'soccer': (
        "You are an expert soccer prop bet analyst. "
        "Structure every response in exactly two sections:\n\n"
        "PREDICTION:\n- OVER or UNDER\n- One-sentence summary of your call\n"
        "- Confidence: [XX]% (use 50–95)\n\n"
        "ANALYSIS:\nDetailed, numbered analysis referencing actual stat values."
    ),
}


# ── Shared helpers ─────────────────────────────────────────────────────────────

def _game_log(games: list, columns: list) -> str:
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
    if not games:
        return ""
    vals = [fn(g) for g in games]
    avg5 = sum(vals) / len(vals)
    avg3 = sum(vals[:3]) / min(3, len(vals))
    diff = avg3 - avg5
    arrow = "↑ trending up" if diff > 0.4 else "↓ trending down" if diff < -0.4 else "→ stable"
    return f"  {label}: L3 avg {avg3:.1f}  vs  L5 avg {avg5:.1f}  {arrow}"


# ── NBA prompts ────────────────────────────────────────────────────────────────

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
        Steals/g: {opp.opponentAverageSteals}  |  Blocks/g: {opp.opponentAverageBlocks}
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

            {_RESPONSE_TEMPLATE}1. Scoring trend: Compare L3 vs L5 and season average.
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

            {_RESPONSE_TEMPLATE}1. Rebounding trend: L3 vs L5 vs season.
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

            {_RESPONSE_TEMPLATE}1. Playmaking trend: L3 vs L5 vs season.
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

            {_RESPONSE_TEMPLATE}1. Volume and efficiency: Attempt rate and 3P% vs. season norms.
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

            {_RESPONSE_TEMPLATE}1. Steal trend: L3 vs L5 vs season.
            2. Defensive role: Does the player gamble for steals or play disciplined defense?
            3. Opponent ball-handling: High-turnover teams create more steal opportunities.
            4. Variance: Steals are highly variable — note consistency across the game log.
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

            {_RESPONSE_TEMPLATE}1. Block trend: L3 vs L5 vs season.
            2. Defensive positioning: Help defense vs. man coverage and rim protection role.
            3. Opponent interior attack: Teams that attack the paint create more block opportunities.
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

            {_RESPONSE_TEMPLATE}1. Combined PRA trend: Is the player tracking above or below the line?
            2. Scoring component: Efficiency and usage impact on points contribution.
            3. Rebounding component: Minutes and matchup implications for boards.
            4. Assists component: Playmaking role and opponent defensive pressure on ball handlers.
            5. Opponent pace and defense: High-pace games with a weaker defense inflate all three categories.
            """

        else:
            raise ValueError(f"Unsupported NBA bet type: {bet_type}")

    # ── NFL prompts ────────────────────────────────────────────────────────────

    def create_nfl_prompt(self, player_name: str, bet_type: str, line: float, stats: dict) -> str:
        info = stats['player_info']
        ss = stats['season_stats']
        l5 = stats['last_five_averages']
        opp = stats['opposing_team']
        games = stats.get('individual_games', [])

        base = f"""Player: {player_name} ({info.position}, {info.team}, age {info.age})
Days since last game: {info.daysSinceLastGame}
"""
        opp_block = f"""Opponent: {opp.teamName} ({opp.wins}-{opp.losses})
Pts allowed/g: {opp.pointsAllowedPerGame}  |  Pass yds allowed/g: {opp.passYardsAllowedPerGame}
Rush yds allowed/g: {opp.rushYardsAllowedPerGame}  |  Total yds allowed/g: {opp.totalYardsAllowedPerGame}
"""

        bt = bet_type.lower()
        if bt == 'pass_yards':
            log = _game_log(games, [
                ("PassYd", lambda g: g.passYards),
                ("Cmp/At", lambda g: f"{g.completions}/{g.passAttempts}"),
                ("TD", lambda g: g.passTDs),
                ("INT", lambda g: g.interceptions),
            ])
            return f"""{base}
PASSING YARDS — Line: {line}

Season:  {ss.averagePassYards:.1f} yds/g  |  {ss.completionPct:.1f}% cmp  |  {ss.averagePassTDs:.1f} TD/g
L5:      {l5.averagePassYards:.1f} yds/g  |  {l5.averagePassTDs:.1f} TD/g  |  {l5.averageInterceptions:.1f} INT/g

Game log:
{log}

Trend:
{_trend(games, lambda g: g.passYards, "Pass yards")}

{opp_block}
{_RESPONSE_TEMPLATE}1. Passing volume trend vs. the line.
2. Completion efficiency and turnover risk in this matchup.
3. Opponent pass defense and pressure rate.
4. Game script: Will this game be close (high volume) or a blowout?
"""
        elif bt == 'rush_yards':
            log = _game_log(games, [
                ("RushYd", lambda g: g.rushYards),
                ("Att", lambda g: g.rushAttempts),
                ("TD", lambda g: g.rushTDs),
                ("RecYd", lambda g: g.recYards),
            ])
            return f"""{base}
RUSHING YARDS — Line: {line}

Season:  {ss.averageRushYards:.1f} yds/g  |  {ss.averageRushTDs:.1f} TD/g
L5:      {l5.averageRushYards:.1f} yds/g  |  {l5.averageRushTDs:.1f} TD/g

Game log:
{log}

Trend:
{_trend(games, lambda g: g.rushYards, "Rush yards")}

{opp_block}
{_RESPONSE_TEMPLATE}1. Rush volume trend and carries consistency.
2. Opponent run defense: yards allowed per carry.
3. Game script: Favored teams run more in the second half.
4. Receiving role: Is the RB also contributing in the pass game?
"""
        elif bt in ('receiving_yards', 'receptions'):
            stat_fn = (lambda g: g.recYards) if bt == 'receiving_yards' else (lambda g: g.receptions)
            stat_label = "Rec Yds" if bt == 'receiving_yards' else "Rec"
            log = _game_log(games, [
                ("Rec", lambda g: g.receptions),
                ("RecYd", lambda g: g.recYards),
                ("Tgt", lambda g: g.targets),
                ("TD", lambda g: g.recTDs),
            ])
            return f"""{base}
{stat_label.upper()} — Line: {line}

Season:  {ss.averageReceptions:.1f} rec/g  |  {ss.averageRecYards:.1f} yds/g  |  {ss.averageTargets:.1f} tgt/g
L5:      {l5.averageReceptions:.1f} rec/g  |  {l5.averageRecYards:.1f} yds/g  |  {l5.averageTargets:.1f} tgt/g

Game log:
{log}

Trend:
{_trend(games, stat_fn, stat_label)}

{opp_block}
{_RESPONSE_TEMPLATE}1. Target share and reception rate trend.
2. Route depth: YAC vs. yards after contact vs. deep targets.
3. Opponent coverage: scheme and cornerback matchup.
4. Game script: Passing game volume in this matchup.
"""
        elif bt in ('pass_tds', 'rush_tds'):
            is_pass = bt == 'pass_tds'
            log = _game_log(games, [
                ("PassTD", lambda g: g.passTDs),
                ("RushTD", lambda g: g.rushTDs),
                ("INT", lambda g: g.interceptions),
                ("PassYd", lambda g: g.passYards),
            ])
            return f"""{base}
{"PASSING" if is_pass else "RUSHING"} TOUCHDOWNS — Line: {line}

Season:  {ss.averagePassTDs:.1f} pass TD/g  |  {ss.averageRushTDs:.1f} rush TD/g
L5:      {l5.averagePassTDs:.1f} pass TD/g  |  {l5.averageRushTDs:.1f} rush TD/g

Game log:
{log}

Trend:
{_trend(games, lambda g: g.passTDs if is_pass else g.rushTDs, "TDs")}

{opp_block}
{_RESPONSE_TEMPLATE}1. TD rate and red zone opportunity trend.
2. Opponent TD defense in the red zone.
3. Game script: High-scoring games favor more TDs.
4. Variance: TDs are bursty — note streaks and droughts in the game log.
"""
        else:
            raise ValueError(f"Unsupported NFL bet type: {bet_type}")

    # ── MLB prompts ────────────────────────────────────────────────────────────

    def create_mlb_prompt(self, player_name: str, bet_type: str, line: float, stats: dict) -> str:
        info = stats['player_info']
        ss = stats['season_stats']
        l5 = stats['last_five_averages']
        opp = stats['opposing_team']
        games = stats.get('individual_games', [])

        base = f"""Player: {player_name} ({'Pitcher' if info.isPitcher else info.position}, {info.team}, age {info.age})
Days since last game: {info.daysSinceLastGame}
"""
        opp_block = f"""Opponent: {opp.teamName} ({opp.wins}-{opp.losses})\n"""

        bt = bet_type.lower()
        if bt == 'strikeouts' and info.isPitcher:
            log = _game_log(games, [
                ("IP", lambda g: g.inningsPitched),
                ("SO", lambda g: g.strikeouts),
                ("H", lambda g: g.hitsAllowed),
                ("ER", lambda g: g.earnedRuns),
                ("BB", lambda g: g.walks),
            ])
            return f"""{base}
PITCHER STRIKEOUTS — Line: {line}

Season:  {ss.averageStrikeouts:.1f} K/start  |  {ss.strikeoutsPerNine:.1f} K/9  |  ERA {ss.era:.2f}  |  WHIP {ss.whip:.2f}
L5:      {l5.averageStrikeouts:.1f} K/start  |  {l5.averageInningsPitched:.1f} IP/start

Game log:
{log}

Trend:
{_trend(games, lambda g: g.strikeouts, "Strikeouts")}

{opp_block}
{_RESPONSE_TEMPLATE}1. Strikeout trend vs. season K/9 baseline.
2. Innings pitched: Will the pitcher go deep enough to accumulate Ks?
3. Opponent lineup: Strikeout rate and contact-heavy hitters.
4. Ballpark and conditions: Some parks suppress strikeouts.
"""
        elif bt == 'earned_runs':
            log = _game_log(games, [
                ("IP", lambda g: g.inningsPitched),
                ("ER", lambda g: g.earnedRuns),
                ("H", lambda g: g.hitsAllowed),
                ("HR", lambda g: g.homeRunsAllowed),
                ("BB", lambda g: g.walks),
            ])
            return f"""{base}
EARNED RUNS — Line: {line}

Season:  ERA {ss.era:.2f}  |  WHIP {ss.whip:.2f}  |  {ss.averageEarnedRuns:.1f} ER/start
L5:      {l5.averageEarnedRuns:.1f} ER/start  |  {l5.averageInningsPitched:.1f} IP/start

Game log:
{log}

Trend:
{_trend(games, lambda g: g.earnedRuns, "Earned runs")}

{opp_block}
{_RESPONSE_TEMPLATE}1. Earned run trend and ERA trajectory.
2. Control: Walk rate and ability to limit base runners.
3. Opponent power: Home run rate and slugging against this pitcher type.
4. Ballpark and weather: Run-suppressing vs. hitter-friendly park.
"""
        elif bt == 'innings_pitched':
            log = _game_log(games, [
                ("IP", lambda g: g.inningsPitched),
                ("H", lambda g: g.hitsAllowed),
                ("ER", lambda g: g.earnedRuns),
                ("SO", lambda g: g.strikeouts),
                ("BB", lambda g: g.walks),
            ])
            return f"""{base}
INNINGS PITCHED — Line: {line}

Season:  {ss.averageInningsPitched:.1f} IP/start  |  ERA {ss.era:.2f}
L5:      {l5.averageInningsPitched:.1f} IP/start

Game log:
{log}

Trend:
{_trend(games, lambda g: g.inningsPitched, "Innings pitched")}

{opp_block}
{_RESPONSE_TEMPLATE}1. Innings trend and pitch count management.
2. Efficiency: High walk/hit rates lead to early exits.
3. Bullpen context: Does the team protect or pull their starters early?
4. Opponent lineup: High-OBP teams run up pitch counts.
"""
        elif bt == 'hits':
            log = _game_log(games, [
                ("H", lambda g: g.hits),
                ("AB", lambda g: g.atBats),
                ("HR", lambda g: g.homeRuns),
                ("RBI", lambda g: g.rbis),
                ("TB", lambda g: g.totalBases),
            ])
            return f"""{base}
HITS — Line: {line}

Season:  BA {ss.battingAverage:.3f}  |  OBP {ss.obp:.3f}  |  SLG {ss.slg:.3f}  |  {ss.averageHits:.2f} H/g
L5:      {l5.averageHits:.1f} H/g  |  {l5.averageAtBats:.1f} AB/g

Game log:
{log}

Trend:
{_trend(games, lambda g: g.hits, "Hits")}

{opp_block}
{_RESPONSE_TEMPLATE}1. Hits trend vs. batting average baseline.
2. At-bat volume: More ABs = more hit opportunities.
3. Opposing pitcher: ERA, WHIP, and strikeout rate vs. this batter type.
4. Handedness split: Does the batter face a favorable/unfavorable pitching hand?
"""
        elif bt == 'home_runs':
            log = _game_log(games, [
                ("HR", lambda g: g.homeRuns),
                ("H", lambda g: g.hits),
                ("TB", lambda g: g.totalBases),
                ("RBI", lambda g: g.rbis),
            ])
            return f"""{base}
HOME RUNS — Line: {line}

Season:  {ss.averageHomeRuns:.2f} HR/g  |  SLG {ss.slg:.3f}
L5:      {l5.averageHomeRuns:.1f} HR/g  |  {l5.averageTotalBases:.1f} TB/g

Game log:
{log}

Trend:
{_trend(games, lambda g: g.homeRuns, "Home runs")}

{opp_block}
{_RESPONSE_TEMPLATE}1. HR rate and power trend.
2. Opposing pitcher: Home run rate allowed, fly-ball rate.
3. Ballpark: Home run park factor.
4. Variance: HRs are bursty — note hot streaks and cold spells.
"""
        elif bt == 'rbis':
            log = _game_log(games, [
                ("RBI", lambda g: g.rbis),
                ("H", lambda g: g.hits),
                ("HR", lambda g: g.homeRuns),
                ("AB", lambda g: g.atBats),
            ])
            return f"""{base}
RBIs — Line: {line}

Season:  {ss.averageRBIs:.2f} RBI/g
L5:      {l5.averageRBIs:.1f} RBI/g

Game log:
{log}

Trend:
{_trend(games, lambda g: g.rbis, "RBIs")}

{opp_block}
{_RESPONSE_TEMPLATE}1. RBI opportunity: Batting order position and runners-on-base rate.
2. Power and contact: HR rate and extra-base hit frequency.
3. Opponent pitching: Run-prevention ability.
4. Lineup context: Quality of teammates ahead in the order.
"""
        elif bt == 'total_bases':
            log = _game_log(games, [
                ("TB", lambda g: g.totalBases),
                ("H", lambda g: g.hits),
                ("HR", lambda g: g.homeRuns),
                ("AB", lambda g: g.atBats),
            ])
            return f"""{base}
TOTAL BASES — Line: {line}

Season:  {ss.averageTotalBases if hasattr(ss, 'averageTotalBases') else 'N/A'} TB/g  |  SLG {ss.slg:.3f}
L5:      {l5.averageTotalBases:.1f} TB/g

Game log:
{log}

Trend:
{_trend(games, lambda g: g.totalBases, "Total bases")}

{opp_block}
{_RESPONSE_TEMPLATE}1. Total bases trend vs. slugging percentage.
2. Extra-base hit frequency: doubles, triples, and HR rate.
3. Opponent pitcher: Fly-ball and HR rates, strikeout rate.
4. Ballpark: Extra-base hit park factor.
"""
        elif bt == 'strikeouts':  # batter strikeouts
            log = _game_log(games, [
                ("SO", lambda g: g.batterStrikeouts),
                ("H", lambda g: g.hits),
                ("AB", lambda g: g.atBats),
            ])
            return f"""{base}
BATTER STRIKEOUTS — Line: {line}

Season:  {ss.averageBatterStrikeouts if hasattr(ss, 'averageBatterStrikeouts') else 'N/A'} K/g
L5:      {l5.averageBatterStrikeouts:.1f} K/g

Game log:
{log}

Trend:
{_trend(games, lambda g: g.batterStrikeouts, "Strikeouts")}

{opp_block}
{_RESPONSE_TEMPLATE}1. Batter strikeout rate and contact ability.
2. Opposing pitcher: Strikeout rate and pitch mix.
3. Handedness: K rates often split significantly by pitcher hand.
4. Recent approach: Is the batter in an aggressive or passive phase?
"""
        else:
            raise ValueError(f"Unsupported MLB bet type: {bet_type}")

    # ── NHL prompts ────────────────────────────────────────────────────────────

    def create_nhl_prompt(self, player_name: str, bet_type: str, line: float, stats: dict) -> str:
        info = stats['player_info']
        ss = stats['season_stats']
        l5 = stats['last_five_averages']
        opp = stats['opposing_team']
        games = stats.get('individual_games', [])

        ot_str = f"-{opp.otLosses} OT" if hasattr(opp, 'otLosses') and opp.otLosses else ''
        base = f"""Player: {player_name} ({info.position}, {info.team}, age {info.age})
Days since last game: {info.daysSinceLastGame}
"""
        opp_block = f"""Opponent: {opp.teamName} ({opp.wins}-{opp.losses}{ot_str})\n"""

        bt = bet_type.lower()
        if bt == 'goals':
            log = _game_log(games, [
                ("G", lambda g: g.goals),
                ("A", lambda g: g.assists),
                ("Sh", lambda g: g.shots),
                ("+/-", lambda g: g.plusMinus),
                ("TOI", lambda g: g.timeOnIce),
            ])
            return f"""{base}
GOALS — Line: {line}

Season:  {ss.goals} G  |  {ss.averageGoals:.2f}/g  |  {ss.shootingPct:.1f}% S%  |  {ss.averageShots:.1f} shots/g
L5:      {l5.averageGoals:.1f} G/g  |  {l5.averageShots:.1f} shots/g  |  {l5.averageTimeOnIce:.1f} TOI/g

Game log:
{log}

Trend:
{_trend(games, lambda g: g.goals, "Goals")}

{opp_block}
{_RESPONSE_TEMPLATE}1. Goal-scoring trend and shooting percentage sustainability.
2. Shot volume and quality: Does the player generate high-danger chances?
3. Opponent goaltending: Save percentage and goals-against average.
4. Power play role: PP time generates elevated goal opportunities.
"""
        elif bt == 'assists':
            log = _game_log(games, [
                ("A", lambda g: g.assists),
                ("G", lambda g: g.goals),
                ("Sh", lambda g: g.shots),
                ("TOI", lambda g: g.timeOnIce),
            ])
            return f"""{base}
ASSISTS — Line: {line}

Season:  {ss.assists} A  |  {ss.averageAssists:.2f}/g
L5:      {l5.averageAssists:.1f} A/g  |  {l5.averageTimeOnIce:.1f} TOI/g

Game log:
{log}

Trend:
{_trend(games, lambda g: g.assists, "Assists")}

{opp_block}
{_RESPONSE_TEMPLATE}1. Assist trend and playmaking role.
2. Linemate quality: Scorers around the player create assist opportunities.
3. Power play role: PP assists are more predictable than ES assists.
4. Opponent penalty kill: Strong PKs suppress PP point opportunities.
"""
        elif bt == 'points':
            log = _game_log(games, [
                ("Pts", lambda g: g.points),
                ("G", lambda g: g.goals),
                ("A", lambda g: g.assists),
                ("Sh", lambda g: g.shots),
                ("TOI", lambda g: g.timeOnIce),
            ])
            return f"""{base}
POINTS — Line: {line}

Season:  {ss.points} Pts  |  {ss.averagePoints:.2f}/g  |  {ss.averageGoals:.2f} G/g  |  {ss.averageAssists:.2f} A/g
L5:      {l5.averagePoints:.1f} Pts/g  |  {l5.averageGoals:.1f} G/g  |  {l5.averageAssists:.1f} A/g

Game log:
{log}

Trend:
{_trend(games, lambda g: g.points, "Points")}

{opp_block}
{_RESPONSE_TEMPLATE}1. Overall point production trend.
2. Goal and assist split: Which component is driving production?
3. TOI and line deployment: First-line minutes and PP time.
4. Opponent defense and goaltending: Can they suppress high-event play?
"""
        elif bt == 'shots':
            log = _game_log(games, [
                ("Sh", lambda g: g.shots),
                ("G", lambda g: g.goals),
                ("Pts", lambda g: g.points),
                ("TOI", lambda g: g.timeOnIce),
            ])
            return f"""{base}
SHOTS ON GOAL — Line: {line}

Season:  {ss.averageShots:.1f} shots/g  |  {ss.shootingPct:.1f}% S%
L5:      {l5.averageShots:.1f} shots/g  |  {l5.averageTimeOnIce:.1f} TOI/g

Game log:
{log}

Trend:
{_trend(games, lambda g: g.shots, "Shots")}

{opp_block}
{_RESPONSE_TEMPLATE}1. Shot volume trend and consistency.
2. TOI impact: More ice time directly correlates with more shot attempts.
3. Shot selection: Quality zone entry and shooting role on the power play.
4. Opponent shot suppression: Defensive structure and shot-blocking rate.
"""
        else:
            raise ValueError(f"Unsupported NHL bet type: {bet_type}")

    # ── Soccer prompts ─────────────────────────────────────────────────────────

    def create_soccer_prompt(self, player_name: str, bet_type: str, line: float, stats: dict) -> str:
        info = stats['player_info']
        ss = stats['season_stats']
        l5 = stats['last_five_averages']
        opp = stats['opposing_team']
        games = stats.get('individual_games', [])

        base = f"""Player: {player_name} ({info.position}, {info.team}, age {info.age})
Days since last game: {info.daysSinceLastGame}
"""
        opp_block = f"""Opponent: {opp.teamName} ({opp.wins}W-{opp.draws}D-{opp.losses}L)
Goals allowed/g: {opp.goalsAllowedPerGame}  |  xG allowed/g: {opp.xGAllowedPerGame}
Clean sheets: {opp.cleanSheets}  |  Shots allowed/g: {opp.shotsAllowedPerGame}
"""

        bt = bet_type.lower()
        if bt == 'goals':
            log = _game_log(games, [
                ("G", lambda g: g.goals),
                ("xG", lambda g: g.xG),
                ("Sh", lambda g: g.shots),
                ("SoT", lambda g: g.shotsOnTarget),
                ("Min", lambda g: g.minutesPlayed),
            ])
            return f"""{base}
GOALS — Line: {line}

Season:  {ss.goals} G  |  {ss.averageGoals:.2f}/g  |  {ss.averageXG:.2f} xG/g  |  {ss.shotConversionRate:.1f}% conv
L5:      {l5.averageGoals:.1f} G/g  |  {l5.averageXG:.1f} xG/g  |  {l5.averageMinutesPlayed:.0f} min/g

Game log:
{log}

Trend:
{_trend(games, lambda g: g.goals, "Goals")}

{opp_block}
{_RESPONSE_TEMPLATE}1. Goal-scoring trend and xG sustainability.
2. Shot quality: Is the player generating high-xG chances?
3. Opponent defense: Goals allowed, clean sheet rate, and defensive structure.
4. Set pieces: Corner kicks and free kicks in dangerous areas boost goal probability.
"""
        elif bt == 'assists':
            log = _game_log(games, [
                ("A", lambda g: g.assists),
                ("xA", lambda g: g.xA),
                ("G", lambda g: g.goals),
                ("Sh", lambda g: g.shots),
                ("Min", lambda g: g.minutesPlayed),
            ])
            return f"""{base}
ASSISTS — Line: {line}

Season:  {ss.assists} A  |  {ss.averageAssists:.2f}/g
L5:      {l5.averageAssists:.1f} A/g  |  {l5.averageXA:.1f} xA/g  |  {l5.averageMinutesPlayed:.0f} min/g

Game log:
{log}

Trend:
{_trend(games, lambda g: g.assists, "Assists")}

{opp_block}
{_RESPONSE_TEMPLATE}1. Assist trend and chance-creation role.
2. xA vs. actual assists: Is the player creating but not converting?
3. Finisher quality: The player needs quality strikers to turn chances into assists.
4. Opponent defensive shape: High defensive blocks suppress through-balls.
"""
        elif bt == 'shots':
            log = _game_log(games, [
                ("Sh", lambda g: g.shots),
                ("SoT", lambda g: g.shotsOnTarget),
                ("xG", lambda g: g.xG),
                ("G", lambda g: g.goals),
                ("Min", lambda g: g.minutesPlayed),
            ])
            return f"""{base}
SHOTS — Line: {line}

Season:  {ss.averageShots:.1f} shots/g  |  {ss.averageShotsOnTarget:.1f} SoT/g
L5:      {l5.averageShots:.1f} shots/g  |  {l5.averageMinutesPlayed:.0f} min/g

Game log:
{log}

Trend:
{_trend(games, lambda g: g.shots, "Shots")}

{opp_block}
{_RESPONSE_TEMPLATE}1. Shot volume trend and attacking role.
2. Minutes: Shot rate is heavily minutes-dependent — track full vs. partial games.
3. Opponent defensive pressure: High-block defenses suppress shot attempts.
4. Game script: Trailing teams shoot more; leading teams sit back.
"""
        elif bt == 'shots_on_target':
            log = _game_log(games, [
                ("SoT", lambda g: g.shotsOnTarget),
                ("Sh", lambda g: g.shots),
                ("xG", lambda g: g.xG),
                ("Min", lambda g: g.minutesPlayed),
            ])
            return f"""{base}
SHOTS ON TARGET — Line: {line}

Season:  {ss.averageShotsOnTarget:.1f} SoT/g  |  {ss.averageShots:.1f} shots/g
L5:      {l5.averageShotsOnTarget:.1f} SoT/g  |  {l5.averageShots:.1f} shots/g  |  {l5.averageMinutesPlayed:.0f} min/g

Game log:
{log}

Trend:
{_trend(games, lambda g: g.shotsOnTarget, "Shots on target")}

{opp_block}
{_RESPONSE_TEMPLATE}1. SoT rate and shot quality trend.
2. Ratio of SoT to total shots: Is the player taking more speculative attempts?
3. Opponent goalkeeper: Strong keepers reduce SoT value but don't prevent shots.
4. Match context: Open, competitive games generate more SoT than lopsided fixtures.
"""
        else:
            raise ValueError(f"Unsupported soccer bet type: {bet_type}")

    # ── Dispatcher ─────────────────────────────────────────────────────────────

    async def analyze_bet(self, player_name: str, bet_type: str, line: float,
                          stats: dict, sport: str = 'nba') -> str:
        sport = sport.lower()
        if sport == 'nba':
            prompt = self.create_analysis_prompt(player_name, bet_type, line, stats)
        elif sport == 'nfl':
            prompt = self.create_nfl_prompt(player_name, bet_type, line, stats)
        elif sport == 'mlb':
            prompt = self.create_mlb_prompt(player_name, bet_type, line, stats)
        elif sport == 'nhl':
            prompt = self.create_nhl_prompt(player_name, bet_type, line, stats)
        elif sport == 'soccer':
            prompt = self.create_soccer_prompt(player_name, bet_type, line, stats)
        else:
            raise ValueError(f"Unknown sport: {sport}")

        system_prompt = _SYSTEM_PROMPTS.get(sport, _SYSTEM_PROMPTS['nba'])

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]
        )
        return response.choices[0].message.content
