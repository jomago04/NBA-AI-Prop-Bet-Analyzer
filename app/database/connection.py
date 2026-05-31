"""
SQLite connection management and schema initialization for bet outcome tracking.

A single-file SQLite database is used to persist every AI analysis and, once the
game is played, the real outcome of the bet. This lets us measure how accurate
the bot's predictions are over time and is the foundation for the future
"simulate a period in time" backtesting feature.
"""

import os
import sqlite3
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Database location is configurable so tests / deployments can point elsewhere.
DEFAULT_DB_PATH = os.path.join("data", "nba_bets.db")
DB_PATH = os.getenv("BET_DB_PATH", DEFAULT_DB_PATH)

# Each row captures one AI analysis and (later) its graded real-world outcome.
SCHEMA = """
CREATE TABLE IF NOT EXISTS bet_analyses (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name         TEXT    NOT NULL,
    bet_type            TEXT    NOT NULL,
    line                REAL    NOT NULL,

    predicted_direction TEXT    NOT NULL,           -- OVER / UNDER / UNKNOWN
    confidence          REAL,                        -- 0-1 if the AI gave one
    analysis_text       TEXT,                        -- full AI response
    model               TEXT,                        -- model that produced it

    game_date           TEXT,                        -- ISO date the bet applies to
    created_at          TEXT    NOT NULL,            -- ISO timestamp of analysis

    status              TEXT    NOT NULL DEFAULT 'pending',  -- pending/settled/void
    actual_value        REAL,                        -- real stat once played
    actual_direction    TEXT,                        -- OVER / UNDER / PUSH
    correct             INTEGER,                     -- 1 if AI was right, 0 if wrong
    settled_at          TEXT                         -- ISO timestamp of settlement
);

CREATE INDEX IF NOT EXISTS idx_bet_analyses_status     ON bet_analyses(status);
CREATE INDEX IF NOT EXISTS idx_bet_analyses_player     ON bet_analyses(player_name);
CREATE INDEX IF NOT EXISTS idx_bet_analyses_game_date  ON bet_analyses(game_date);
CREATE INDEX IF NOT EXISTS idx_bet_analyses_created_at ON bet_analyses(created_at);
"""


def _ensure_db_dir(db_path: str) -> None:
    directory = os.path.dirname(db_path)
    if directory:
        os.makedirs(directory, exist_ok=True)


@contextmanager
def get_connection(db_path: str = None):
    """Yield a SQLite connection with row access by column name.

    A fresh connection is opened per operation which keeps things simple and
    thread-safe for FastAPI's async request handling (sqlite3 connections are
    not safe to share across threads).
    """
    path = db_path or DB_PATH
    _ensure_db_dir(path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: str = None) -> None:
    """Create the database file and tables if they do not yet exist."""
    path = db_path or DB_PATH
    _ensure_db_dir(path)
    with get_connection(path) as conn:
        conn.executescript(SCHEMA)
    logger.info("Bet tracking database initialized at %s", path)
