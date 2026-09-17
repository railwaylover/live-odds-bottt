"""Line-movement classification from probability drift."""
from __future__ import annotations


def classify(open_prob: float, current_prob: float) -> str:
    """Return stable | steam | sharp | drift for a probability move."""
    delta = current_prob - open_prob
    ad = abs(delta)
    if ad < 0.03:
        return "stable"
    if ad >= 0.10:
        return "steam"
    if ad >= 0.05:
        return "sharp"
    return "drift"
