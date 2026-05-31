from pydantic import BaseModel


class MLBPlayerInfo(BaseModel):
    name: str
    team: str
    position: str       # SP, RP, C, 1B, 2B, 3B, SS, LF, CF, RF, DH
    age: int
    isPitcher: bool
    daysSinceLastGame: int


class MLBGameStats(BaseModel):
    opponent: str
    isAway: bool
    # Pitcher stats
    inningsPitched: float = 0.0
    hitsAllowed: int = 0
    earnedRuns: int = 0
    strikeouts: int = 0
    walks: int = 0
    homeRunsAllowed: int = 0
    # Batter stats
    atBats: int = 0
    hits: int = 0
    runs: int = 0
    rbis: int = 0
    homeRuns: int = 0
    batterStrikeouts: int = 0
    batterWalks: int = 0
    totalBases: int = 0


class MLBLastFiveAverages(BaseModel):
    # Pitcher
    averageInningsPitched: float = 0.0
    averageHitsAllowed: float = 0.0
    averageEarnedRuns: float = 0.0
    averageStrikeouts: float = 0.0
    averageWalks: float = 0.0
    # Batter
    averageAtBats: float = 0.0
    averageHits: float = 0.0
    averageRBIs: float = 0.0
    averageHomeRuns: float = 0.0
    averageTotalBases: float = 0.0
    averageBatterStrikeouts: float = 0.0


class MLBSeasonStats(BaseModel):
    gamesPlayed: int = 0
    # Pitcher season stats
    era: float = 0.0
    whip: float = 0.0
    strikeoutsPerNine: float = 0.0
    averageInningsPitched: float = 0.0
    averageStrikeouts: float = 0.0
    averageEarnedRuns: float = 0.0
    # Batter season stats
    battingAverage: float = 0.0
    obp: float = 0.0
    slg: float = 0.0
    averageHits: float = 0.0
    averageHomeRuns: float = 0.0
    averageRBIs: float = 0.0
    averageTotalBases: float = 0.0


class MLBOpposingTeamStats(BaseModel):
    teamName: str
    wins: int
    losses: int
    teamERA: float = 0.0
    runsPerGame: float = 0.0
    battingAverage: float = 0.0
    ops: float = 0.0
    strikeoutsPerGame: float = 0.0
    homeRunsPerGame: float = 0.0
