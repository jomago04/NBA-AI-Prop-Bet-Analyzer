"""
Outcome tracking service.

Persists every AI analysis, settles it against the real bet result, and reports
accuracy. Designed so the upcoming "simulate a period in time" feature can pull
graded analyses by date range and replay them to estimate the bot's edge.
"""

import logging
from datetime import datetime, timezone
from typing import Optional, List

from app.database.connection import get_connection, init_db
from app.models.betRecord import BetAnalysisRecord, AccuracyStats
from app.services.predictionParser import parse_prediction

logger = logging.getLogger(__name__)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _row_to_record(row) -> BetAnalysisRecord:
    correct = row["correct"]
    return BetAnalysisRecord(
        id=row["id"],
        player_name=row["player_name"],
        bet_type=row["bet_type"],
        line=row["line"],
        predicted_direction=row["predicted_direction"],
        confidence=row["confidence"],
        analysis_text=row["analysis_text"],
        model=row["model"],
        game_date=row["game_date"],
        created_at=row["created_at"],
        status=row["status"],
        actual_value=row["actual_value"],
        actual_direction=row["actual_direction"],
        correct=None if correct is None else bool(correct),
        settled_at=row["settled_at"],
    )


def grade_outcome(line: float, actual_value: float, predicted_direction: str):
    """Given the line and real stat, return (actual_direction, correct).

    `correct` is None on a PUSH (actual exactly equals the line) since the bet
    neither wins nor loses and shouldn't count for/against accuracy.
    """
    if actual_value > line:
        actual_direction = "OVER"
    elif actual_value < line:
        actual_direction = "UNDER"
    else:
        return "PUSH", None

    correct = (predicted_direction == actual_direction)
    return actual_direction, correct


class OutcomeTracker:
    """Repository over the bet_analyses table."""

    def __init__(self, db_path: str = None):
        self.db_path = db_path
        init_db(db_path)

    def record_analysis(
        self,
        player_name: str,
        bet_type: str,
        line: float,
        analysis_text: str,
        model: str = None,
        game_date: str = None,
    ) -> BetAnalysisRecord:
        """Persist a new AI analysis and return the stored record (status pending)."""
        predicted_direction, confidence = parse_prediction(analysis_text)
        created_at = _utc_now_iso()

        with get_connection(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO bet_analyses (
                    player_name, bet_type, line,
                    predicted_direction, confidence, analysis_text, model,
                    game_date, created_at, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
                """,
                (
                    player_name, bet_type, line,
                    predicted_direction, confidence, analysis_text, model,
                    game_date, created_at,
                ),
            )
            new_id = cursor.lastrowid

        logger.info(
            "Recorded analysis #%s: %s %s %s -> %s",
            new_id, player_name, bet_type, line, predicted_direction,
        )
        return self.get_analysis(new_id)

    def get_analysis(self, analysis_id: int) -> Optional[BetAnalysisRecord]:
        with get_connection(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM bet_analyses WHERE id = ?", (analysis_id,)
            ).fetchone()
        return _row_to_record(row) if row else None

    def settle_outcome(
        self, analysis_id: int, actual_value: float
    ) -> Optional[BetAnalysisRecord]:
        """Grade a pending analysis against its real result.

        Returns the updated record, or None if the id doesn't exist.
        """
        record = self.get_analysis(analysis_id)
        if record is None:
            return None

        actual_direction, correct = grade_outcome(
            record.line, actual_value, record.predicted_direction
        )
        settled_at = _utc_now_iso()

        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                UPDATE bet_analyses
                SET status = 'settled',
                    actual_value = ?,
                    actual_direction = ?,
                    correct = ?,
                    settled_at = ?
                WHERE id = ?
                """,
                (
                    actual_value,
                    actual_direction,
                    None if correct is None else int(correct),
                    settled_at,
                    analysis_id,
                ),
            )

        logger.info(
            "Settled analysis #%s: actual=%s (%s), correct=%s",
            analysis_id, actual_value, actual_direction, correct,
        )
        return self.get_analysis(analysis_id)

    def list_analyses(
        self,
        status: str = None,
        player_name: str = None,
        bet_type: str = None,
        start_date: str = None,
        end_date: str = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[BetAnalysisRecord]:
        """List analyses with optional filters.

        `start_date`/`end_date` filter on game_date (falling back to created_at
        when game_date is null) so the future simulation feature can pull a slice
        of time to replay.
        """
        clauses = []
        params = []

        if status:
            clauses.append("status = ?")
            params.append(status)
        if player_name:
            clauses.append("player_name = ?")
            params.append(player_name)
        if bet_type:
            clauses.append("bet_type = ?")
            params.append(bet_type)
        if start_date:
            clauses.append("COALESCE(game_date, created_at) >= ?")
            params.append(start_date)
        if end_date:
            clauses.append("COALESCE(game_date, created_at) <= ?")
            params.append(end_date)

        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        query = (
            f"SELECT * FROM bet_analyses {where} "
            "ORDER BY COALESCE(game_date, created_at) DESC, id DESC "
            "LIMIT ? OFFSET ?"
        )
        params.extend([limit, offset])

        with get_connection(self.db_path) as conn:
            rows = conn.execute(query, params).fetchall()
        return [_row_to_record(r) for r in rows]

    def accuracy_stats(
        self,
        player_name: str = None,
        bet_type: str = None,
        start_date: str = None,
        end_date: str = None,
    ) -> AccuracyStats:
        """Aggregate accuracy metrics over the matching analyses.

        This is the metric the simulation feature will optimize against:
        across a window of time, how often was the bot's OVER/UNDER call right?
        """
        clauses = []
        params = []
        if player_name:
            clauses.append("player_name = ?")
            params.append(player_name)
        if bet_type:
            clauses.append("bet_type = ?")
            params.append(bet_type)
        if start_date:
            clauses.append("COALESCE(game_date, created_at) >= ?")
            params.append(start_date)
        if end_date:
            clauses.append("COALESCE(game_date, created_at) <= ?")
            params.append(end_date)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""

        with get_connection(self.db_path) as conn:
            rows = conn.execute(
                f"SELECT bet_type, predicted_direction, status, correct, "
                f"actual_direction FROM bet_analyses {where}",
                params,
            ).fetchall()

        total = len(rows)
        pending = settled = pushes = correct = incorrect = 0
        by_bet_type: dict = {}
        by_direction: dict = {}

        for row in rows:
            if row["status"] == "settled":
                settled += 1
                if row["actual_direction"] == "PUSH":
                    pushes += 1
                elif row["correct"] == 1:
                    correct += 1
                elif row["correct"] == 0:
                    incorrect += 1
            else:
                pending += 1

            bt = by_bet_type.setdefault(
                row["bet_type"], {"correct": 0, "incorrect": 0}
            )
            di = by_direction.setdefault(
                row["predicted_direction"], {"correct": 0, "incorrect": 0}
            )
            if row["status"] == "settled" and row["actual_direction"] != "PUSH":
                if row["correct"] == 1:
                    bt["correct"] += 1
                    di["correct"] += 1
                elif row["correct"] == 0:
                    bt["incorrect"] += 1
                    di["incorrect"] += 1

        graded = correct + incorrect
        accuracy = round(correct / graded, 4) if graded else None

        # Attach per-bucket accuracy for convenience.
        for bucket in (by_bet_type, by_direction):
            for key, counts in bucket.items():
                g = counts["correct"] + counts["incorrect"]
                counts["accuracy"] = round(counts["correct"] / g, 4) if g else None

        return AccuracyStats(
            total_analyses=total,
            pending=pending,
            settled=settled,
            pushes=pushes,
            correct=correct,
            incorrect=incorrect,
            accuracy=accuracy,
            by_bet_type=by_bet_type,
            by_direction=by_direction,
        )
