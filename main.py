from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator
from app.services.runScraper import GetNBAPlayerStats
from app.services.aiAnalysis import NBAAiAnalysis
from app.services import sport_analyzer
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

_nba_stats = GetNBAPlayerStats()
ai_analysis = NBAAiAnalysis()

SPORT_BET_TYPES = {
    'nba':    {'points', 'rebounds', 'assists', 'threes', 'steals', 'blocks', 'pra'},
    'nfl':    {'pass_yards', 'rush_yards', 'receiving_yards', 'receptions', 'pass_tds', 'rush_tds'},
    'mlb':    {'hits', 'home_runs', 'rbis', 'total_bases', 'strikeouts', 'earned_runs', 'innings_pitched'},
    'nhl':    {'goals', 'assists', 'points', 'shots'},
    'soccer': {'goals', 'assists', 'shots', 'shots_on_target'},
}


class BetRequest(BaseModel):
    player_name: str
    bet_type: str
    line: float
    sport: str = 'nba'

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

    @field_validator('sport')
    @classmethod
    def sport_must_be_valid(cls, v: str) -> str:
        v = v.lower().strip()
        if v not in SPORT_BET_TYPES:
            raise ValueError(f"Sport must be one of: {', '.join(sorted(SPORT_BET_TYPES))}")
        return v


# ── Stats panel builders ───────────────────────────────────────────────────────

def _build_nba_stats_panel(season_avgs, l5, opposing_team, individual_games) -> dict:
    return {
        "sport": "nba",
        "season_averages": {
            "pts": season_avgs.averagePoints,
            "reb": season_avgs.averageTotalRebounds,
            "ast": season_avgs.averageAssists,
            "stl": season_avgs.averageSteals,
            "blk": season_avgs.averageBlocks,
            "3pm": season_avgs.averageThreePoints,
            "min": season_avgs.averageMinutesPlayed,
        },
        "last_5_averages": {
            "pts": round(l5.averagePoints, 1),
            "reb": round(l5.averageTotalRebounds, 1),
            "ast": round(l5.averageAssists, 1),
            "stl": round(l5.averageSteals, 1),
            "blk": round(l5.averageBlocks, 1),
            "3pm": round(l5.averageThreePoints, 1),
            "min": round(l5.averageMinutesPlayed, 1),
            "ts%": round(l5.averageTrueShootingPercentage, 1),
            "usg%": round(l5.averageUsagePercentage, 1),
        },
        "opponent": {
            "name": opposing_team.opponentTeamName,
            "record": f"{opposing_team.opponentWins}-{opposing_team.opponentLosses}",
            "def_rtg": opposing_team.opponentDefensiveRating,
            "pace": opposing_team.opponentPaceFactor,
            "pts_allowed": opposing_team.opponentAveragePoints,
            "reb_allowed": opposing_team.opponentAverageTotalRebounds,
        },
        "game_log": [
            {
                "opp": ("@ " if g.isAway else "vs ") + g.opponent,
                "pts": g.points, "reb": g.totalRebounds, "ast": g.assists,
                "stl": g.steals, "blk": g.blocks, "3pm": g.threePoints,
                "pra": g.points + g.totalRebounds + g.assists,
                "min": round(g.minutesPlayed, 1),
            }
            for g in individual_games
        ],
    }


def _build_nfl_stats_panel(ss, l5, opp, games) -> dict:
    return {
        "sport": "nfl",
        "season_averages": {
            "pass_yds": round(ss.averagePassYards, 1),
            "pass_tds": round(ss.averagePassTDs, 1),
            "rush_yds": round(ss.averageRushYards, 1),
            "rec_yds": round(ss.averageRecYards, 1),
            "receptions": round(ss.averageReceptions, 1),
            "targets": round(ss.averageTargets, 1),
        },
        "last_5_averages": {
            "pass_yds": round(l5.averagePassYards, 1),
            "pass_tds": round(l5.averagePassTDs, 1),
            "rush_yds": round(l5.averageRushYards, 1),
            "rec_yds": round(l5.averageRecYards, 1),
            "receptions": round(l5.averageReceptions, 1),
            "targets": round(l5.averageTargets, 1),
        },
        "opponent": {
            "name": opp.teamName,
            "record": f"{opp.wins}-{opp.losses}",
            "pts_allowed": opp.pointsAllowedPerGame,
            "pass_yds_allowed": opp.passYardsAllowedPerGame,
            "rush_yds_allowed": opp.rushYardsAllowedPerGame,
        },
        "game_log": [
            {
                "opp": ("@ " if g.isAway else "vs ") + g.opponent,
                "pass_yds": g.passYards, "rush_yds": g.rushYards,
                "rec_yds": g.recYards, "receptions": g.receptions,
                "targets": g.targets, "pass_tds": g.passTDs, "rush_tds": g.rushTDs,
            }
            for g in games
        ],
    }


def _build_mlb_stats_panel(info, ss, l5, opp, games) -> dict:
    if info.isPitcher:
        season_s = {"era": ss.era, "whip": ss.whip, "k9": round(ss.strikeoutsPerNine, 2),
                    "avg_ip": round(ss.averageInningsPitched, 1), "avg_so": round(ss.averageStrikeouts, 1)}
        l5_s = {"avg_ip": round(l5.averageInningsPitched, 1), "avg_so": round(l5.averageStrikeouts, 1),
                "avg_er": round(l5.averageEarnedRuns, 1), "avg_h": round(l5.averageHitsAllowed, 1)}
        log = [{"opp": ("@ " if g.isAway else "vs ") + g.opponent,
                "ip": round(g.inningsPitched, 1), "so": g.strikeouts,
                "h": g.hitsAllowed, "er": g.earnedRuns, "bb": g.walks}
               for g in games]
    else:
        season_s = {"ba": ss.battingAverage, "obp": ss.obp, "slg": ss.slg,
                    "avg_h": round(ss.averageHits, 2), "avg_hr": round(ss.averageHomeRuns, 2)}
        l5_s = {"avg_h": round(l5.averageHits, 1), "avg_hr": round(l5.averageHomeRuns, 1),
                "avg_rbi": round(l5.averageRBIs, 1), "avg_tb": round(l5.averageTotalBases, 1)}
        log = [{"opp": ("@ " if g.isAway else "vs ") + g.opponent,
                "h": g.hits, "hr": g.homeRuns, "rbi": g.rbis,
                "tb": g.totalBases, "ab": g.atBats}
               for g in games]
    return {
        "sport": "mlb",
        "is_pitcher": info.isPitcher,
        "season_averages": season_s,
        "last_5_averages": l5_s,
        "opponent": {"name": opp.teamName, "record": f"{opp.wins}-{opp.losses}"},
        "game_log": log,
    }


def _build_nhl_stats_panel(ss, l5, opp, games) -> dict:
    ot = getattr(opp, 'otLosses', 0)
    rec = f"{opp.wins}-{opp.losses}" + (f"-{ot}" if ot else "")
    return {
        "sport": "nhl",
        "season_averages": {
            "goals": round(ss.averageGoals, 2), "assists": round(ss.averageAssists, 2),
            "points": round(ss.averagePoints, 2), "shots": round(ss.averageShots, 1),
            "s_pct": round(ss.shootingPct, 1),
        },
        "last_5_averages": {
            "goals": round(l5.averageGoals, 1), "assists": round(l5.averageAssists, 1),
            "points": round(l5.averagePoints, 1), "shots": round(l5.averageShots, 1),
            "toi": round(l5.averageTimeOnIce, 1),
        },
        "opponent": {"name": opp.teamName, "record": rec},
        "game_log": [
            {
                "opp": ("@ " if g.isAway else "vs ") + g.opponent,
                "goals": g.goals, "assists": g.assists, "points": g.points,
                "shots": g.shots, "plus_minus": g.plusMinus, "toi": round(g.timeOnIce, 1),
            }
            for g in games
        ],
    }


def _build_soccer_stats_panel(ss, l5, opp, games) -> dict:
    return {
        "sport": "soccer",
        "season_averages": {
            "goals": round(ss.averageGoals, 2), "assists": round(ss.averageAssists, 2),
            "shots": round(ss.averageShots, 1), "sot": round(ss.averageShotsOnTarget, 1),
            "xg": round(ss.averageXG, 2), "conv": round(ss.shotConversionRate, 1),
        },
        "last_5_averages": {
            "goals": round(l5.averageGoals, 1), "assists": round(l5.averageAssists, 1),
            "shots": round(l5.averageShots, 1), "sot": round(l5.averageShotsOnTarget, 1),
            "xg": round(l5.averageXG, 2), "min": round(l5.averageMinutesPlayed, 0),
        },
        "opponent": {
            "name": opp.teamName,
            "record": f"{opp.wins}W-{opp.draws}D-{opp.losses}L",
            "goals_allowed": opp.goalsAllowedPerGame,
            "xg_allowed": opp.xGAllowedPerGame,
            "clean_sheets": opp.cleanSheets,
        },
        "game_log": [
            {
                "opp": ("@ " if g.isAway else "vs ") + g.opponent,
                "goals": g.goals, "assists": g.assists, "shots": g.shots,
                "sot": g.shotsOnTarget, "xg": round(g.xG, 2), "min": round(g.minutesPlayed, 0),
            }
            for g in games
        ],
    }


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "sport": "nba"})


@app.get("/nfl")
async def nfl_home(request: Request):
    return templates.TemplateResponse("nfl.html", {"request": request, "sport": "nfl"})


@app.get("/mlb")
async def mlb_home(request: Request):
    return templates.TemplateResponse("mlb.html", {"request": request, "sport": "mlb"})


@app.get("/nhl")
async def nhl_home(request: Request):
    return templates.TemplateResponse("nhl.html", {"request": request, "sport": "nhl"})


@app.get("/soccer")
async def soccer_home(request: Request):
    return templates.TemplateResponse("soccer.html", {"request": request, "sport": "soccer"})


@app.post("/analyze")
async def analyze_bet(bet_request: BetRequest):
    sport = bet_request.sport
    valid_types = SPORT_BET_TYPES.get(sport, set())
    if bet_request.bet_type not in valid_types:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid bet type '{bet_request.bet_type}' for {sport.upper()}. "
                   f"Valid types: {', '.join(sorted(valid_types))}"
        )

    try:
        if sport == 'nba':
            (player_info, season_averages, season_totals,
             last_five_game_averages, opposing_team, individual_games) = (
                _nba_stats.getAllPlayerStats(bet_request.player_name)
            )
            if not all([player_info, season_averages, last_five_game_averages,
                        opposing_team, individual_games]):
                raise HTTPException(
                    status_code=404,
                    detail=f"Could not retrieve stats for '{bet_request.player_name}'."
                )
            stats = {
                'player_info': player_info,
                'season_averages': season_averages,
                'season_totals': season_totals,
                'last_five_game_averages': last_five_game_averages,
                'opposing_team': opposing_team,
                'individual_last_five_games': individual_games,
            }
            stats_panel = _build_nba_stats_panel(
                season_averages, last_five_game_averages, opposing_team, individual_games
            )
        else:
            raw = sport_analyzer.get_stats(sport, bet_request.player_name)
            if not raw:
                raise HTTPException(
                    status_code=404,
                    detail=f"Could not retrieve stats for '{bet_request.player_name}'."
                )
            stats = raw
            games = raw.get('individual_games', [])
            ss = raw['season_stats']
            l5 = raw['last_five_averages']
            opp = raw['opposing_team']
            if sport == 'nfl':
                stats_panel = _build_nfl_stats_panel(ss, l5, opp, games)
            elif sport == 'mlb':
                stats_panel = _build_mlb_stats_panel(raw['player_info'], ss, l5, opp, games)
            elif sport == 'nhl':
                stats_panel = _build_nhl_stats_panel(ss, l5, opp, games)
            else:  # soccer
                stats_panel = _build_soccer_stats_panel(ss, l5, opp, games)

        analysis = await ai_analysis.analyze_bet(
            player_name=bet_request.player_name,
            bet_type=bet_request.bet_type,
            line=bet_request.line,
            stats=stats,
            sport=sport,
        )

        return {
            "player": bet_request.player_name,
            "bet_type": bet_request.bet_type,
            "line": bet_request.line,
            "sport": sport,
            "analysis": analysis,
            "stats": stats_panel,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
