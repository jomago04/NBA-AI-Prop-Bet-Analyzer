"""
Parse the AI analysis free-text response into a structured prediction.

The AI returns a string with a `PREDICTION:` section followed by an `ANALYSIS:`
section. To track outcomes we need a machine-readable OVER/UNDER call (and an
optional confidence) extracted from that text.
"""

import re
from typing import Optional, Tuple

# Matches an explicit percentage anywhere, e.g. "65% confidence" or "confidence: 70%".
_CONFIDENCE_RE = re.compile(r"(\d{1,3}(?:\.\d+)?)\s*%")


def _extract_prediction_section(analysis_text: str) -> str:
    """Return just the PREDICTION section text, or the whole string if absent."""
    if not analysis_text:
        return ""

    upper = analysis_text.upper()
    pred_idx = upper.find("PREDICTION")
    if pred_idx == -1:
        return analysis_text

    # Cut off at the ANALYSIS header so we don't read OVER/UNDER mentions that
    # appear while reasoning rather than as the actual call.
    section = analysis_text[pred_idx:]
    analysis_idx = section.upper().find("ANALYSIS")
    if analysis_idx != -1:
        section = section[:analysis_idx]
    return section


def parse_predicted_direction(analysis_text: str) -> str:
    """Extract the OVER/UNDER call. Returns 'OVER', 'UNDER', or 'UNKNOWN'.

    We look in the PREDICTION section first (the AI's explicit call), falling
    back to the first OVER/UNDER mention in the whole text.
    """
    section = _extract_prediction_section(analysis_text)

    for text in (section, analysis_text or ""):
        upper = text.upper()
        over_idx = upper.find("OVER")
        under_idx = upper.find("UNDER")

        if over_idx == -1 and under_idx == -1:
            continue
        if over_idx == -1:
            return "UNDER"
        if under_idx == -1:
            return "OVER"
        # Both present: whichever the AI states first is the call.
        return "OVER" if over_idx < under_idx else "UNDER"

    return "UNKNOWN"


def parse_confidence(analysis_text: str) -> Optional[float]:
    """Extract a confidence as a 0-1 float if the AI stated a percentage.

    Returns None when no percentage is present in the prediction section.
    """
    section = _extract_prediction_section(analysis_text)
    match = _CONFIDENCE_RE.search(section)
    if not match:
        return None
    try:
        pct = float(match.group(1))
    except ValueError:
        return None
    if pct < 0 or pct > 100:
        return None
    return round(pct / 100.0, 4)


def parse_prediction(analysis_text: str) -> Tuple[str, Optional[float]]:
    """Convenience helper returning (direction, confidence)."""
    return parse_predicted_direction(analysis_text), parse_confidence(analysis_text)
