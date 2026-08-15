"""Kumaradi and Chaitanyadi Avastha bands (RULES KUMARADI_001, CHAITANYADI_001).

Bands are lower-inclusive and upper-exclusive, so a planet at exactly 6°00'00"
in an odd sign is Kumara, not Bala. The final band is closed at 30° so that a
degree of exactly 30.0 (which should not occur, but can appear through floating
point) still resolves.
"""
from __future__ import annotations

from typing import List, Tuple

# (start_degree, end_degree, name)
Band = Tuple[float, float, str]

KUMARADI_ODD: List[Band] = [
    (0.0, 6.0, "Bala"),
    (6.0, 12.0, "Kumara"),
    (12.0, 18.0, "Yuva"),
    (18.0, 24.0, "Vriddha"),
    (24.0, 30.0, "Mrita"),
]

KUMARADI_EVEN: List[Band] = [
    (0.0, 6.0, "Mrita"),
    (6.0, 12.0, "Vriddha"),
    (12.0, 18.0, "Yuva"),
    (18.0, 24.0, "Kumara"),
    (24.0, 30.0, "Bala"),
]

CHAITANYADI_ODD: List[Band] = [
    (0.0, 10.0, "Jagrut"),
    (10.0, 20.0, "Swapna"),
    (20.0, 30.0, "Sushupta"),
]

CHAITANYADI_EVEN: List[Band] = [
    (0.0, 10.0, "Sushupta"),
    (10.0, 20.0, "Swapna"),
    (20.0, 30.0, "Jagrut"),
]

KUMARADI_NAMES = ["Bala", "Kumara", "Yuva", "Vriddha", "Mrita"]
CHAITANYADI_NAMES = ["Jagrut", "Swapna", "Sushupta"]


def resolve_band(bands: List[Band], degree: float) -> Band:
    """Return the band containing ``degree``.

    Raises ValueError if the degree lies outside 0-30, which would indicate a
    calculation fault upstream rather than a missing rule.
    """
    if degree < 0.0 or degree > 30.0:
        raise ValueError(f"Degree within sign out of range: {degree}")
    for band in bands:
        start, end, _ = band
        if start <= degree < end:
            return band
    # Only reachable at exactly 30.0.
    return bands[-1]


# Applicability note. The supplied rule material states the bands in terms of
# sign parity and planetary degree without restricting the set of grahas.
# Classical Baladi/Chaitanyadi descriptions address the seven grahas. Rather
# than silently choosing, the values are computed by the same degree rule for
# Rahu and Ketu and carry this note so the astrologer can discount them.
NODE_APPLICABILITY_NOTE = (
    "Classical Baladi and Chaitanyadi Avastha descriptions address the seven "
    "grahas. The value shown for Rahu/Ketu is produced by the same degree-band "
    "rule and is provided for reference only."
)
