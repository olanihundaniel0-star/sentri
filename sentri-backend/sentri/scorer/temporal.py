"""Hour-of-day deviation scoring."""

from __future__ import annotations

import math

from sentri.canonical.timestamps import ingest_timestamp
from sentri.models.profile import UserProfile
from sentri.models.transaction import TransactionEvent

_HOURS_PER_DAY = 24


def score_hour(profile: UserProfile, event: TransactionEvent) -> float:
    """Score how unusual the event's hour is against the user's historical hour histogram.

    Uses the circular-mean (von Mises-style) formula rather than the bin-based
    alternative (1 - histogram[hour] / max(histogram)): hours wrap around
    midnight, so 23:00 and 01:00 are close in real behavioral terms but would
    be treated as maximally distinct categorical bins under a naive histogram
    lookup. The circular formula captures that adjacency naturally.
    """
    event_hour = ingest_timestamp(event.timestamp).hour
    angle_event = 2 * math.pi * event_hour / _HOURS_PER_DAY

    sin_sum = 0.0
    cos_sum = 0.0
    for hour, count in enumerate(profile.hour_histogram):
        angle = 2 * math.pi * hour / _HOURS_PER_DAY
        sin_sum += count * math.sin(angle)
        cos_sum += count * math.cos(angle)
    mean_angle = math.atan2(sin_sum, cos_sum)

    return (1 - math.cos(angle_event - mean_angle)) / 2
