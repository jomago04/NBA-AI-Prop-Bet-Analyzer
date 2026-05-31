"""
Tests for the bet outcome tracking feature.

These run fully offline (temporary SQLite DB, no OpenAI / scraping) and cover
prediction parsing, grading, settlement, and accuracy aggregation.

Run with:  python -m pytest tests/test_outcome_tracker.py -v
       or:  python tests/test_outcome_tracker.py   (self-contained runner)
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.predictionParser import (
    parse_predicted_direction,
    parse_confidence,
)
from app.services.outcomeTracker import OutcomeTracker, grade_outcome


OVER_TEXT = """PREDICTION:
- This is an OVER with about 65% confidence.
- LeBron should clear this line comfortably.

ANALYSIS:
He has gone under in one recent game but the trend is up."""

UNDER_TEXT = """PREDICTION:
- UNDER. The matchup is tough.

ANALYSIS:
Strong perimeter defense limits the over."""


def _new_tracker():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.remove(path)  # let the tracker create it fresh
    return OutcomeTracker(db_path=path), path


def test_parse_direction():
    assert parse_predicted_direction(OVER_TEXT) == "OVER"
    assert parse_predicted_direction(UNDER_TEXT) == "UNDER"
    assert parse_predicted_direction("no call here") == "UNKNOWN"
    # ANALYSIS-section mentions of the opposite word must not flip the call.
    assert parse_predicted_direction(OVER_TEXT) == "OVER"


def test_parse_confidence():
    assert parse_confidence(OVER_TEXT) == 0.65
    assert parse_confidence(UNDER_TEXT) is None


def test_grade_outcome():
    assert grade_outcome(25.5, 30, "OVER") == ("OVER", True)
    assert grade_outcome(25.5, 20, "OVER") == ("UNDER", False)
    assert grade_outcome(25.5, 20, "UNDER") == ("UNDER", True)
    direction, correct = grade_outcome(25.0, 25.0, "OVER")
    assert direction == "PUSH" and correct is None


def test_record_and_settle():
    tracker, path = _new_tracker()
    try:
        rec = tracker.record_analysis(
            player_name="LeBron James", bet_type="points", line=25.5,
            analysis_text=OVER_TEXT, model="gpt-4o-mini", game_date="2026-05-30",
        )
        assert rec.id is not None
        assert rec.status == "pending"
        assert rec.predicted_direction == "OVER"
        assert rec.confidence == 0.65

        settled = tracker.settle_outcome(rec.id, actual_value=30)
        assert settled.status == "settled"
        assert settled.actual_direction == "OVER"
        assert settled.correct is True
        assert settled.actual_value == 30

        assert tracker.settle_outcome(99999, 10) is None
    finally:
        os.remove(path)


def test_accuracy_stats():
    tracker, path = _new_tracker()
    try:
        # 2 correct, 1 incorrect, 1 push, 1 left pending.
        r1 = tracker.record_analysis("A", "points", 20, OVER_TEXT, game_date="2026-05-01")
        r2 = tracker.record_analysis("B", "points", 20, OVER_TEXT, game_date="2026-05-02")
        r3 = tracker.record_analysis("C", "assists", 8, UNDER_TEXT, game_date="2026-05-03")
        r4 = tracker.record_analysis("D", "points", 20, OVER_TEXT, game_date="2026-05-04")
        tracker.record_analysis("E", "points", 20, OVER_TEXT, game_date="2026-05-05")

        tracker.settle_outcome(r1.id, 25)   # OVER -> correct
        tracker.settle_outcome(r2.id, 25)   # OVER -> correct
        tracker.settle_outcome(r3.id, 12)   # predicted UNDER, actual OVER -> incorrect
        tracker.settle_outcome(r4.id, 20)   # push

        stats = tracker.accuracy_stats()
        assert stats.total_analyses == 5
        assert stats.pending == 1
        assert stats.settled == 4
        assert stats.pushes == 1
        assert stats.correct == 2
        assert stats.incorrect == 1
        assert stats.accuracy == round(2 / 3, 4)

        # Date-range filter (the basis for time-period simulation).
        windowed = tracker.accuracy_stats(start_date="2026-05-01", end_date="2026-05-02")
        assert windowed.correct == 2
        assert windowed.incorrect == 0
        assert windowed.accuracy == 1.0

        listed = tracker.list_analyses(status="pending")
        assert len(listed) == 1 and listed[0].player_name == "E"
    finally:
        os.remove(path)


if __name__ == "__main__":
    failures = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS  {name}")
            except AssertionError as e:
                failures += 1
                print(f"FAIL  {name}: {e}")
            except Exception as e:  # noqa: BLE001
                failures += 1
                print(f"ERROR {name}: {e}")
    print(f"\n{'All tests passed' if not failures else f'{failures} test(s) failed'}")
    sys.exit(1 if failures else 0)
