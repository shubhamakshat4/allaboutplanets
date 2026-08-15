"""Neecha Bhanga condition declarations (RULES NB_001 .. NB_006, NB_100).

Each condition is declared separately here and evaluated separately in
``neecha_bhanga_engine.py``. Conditions are never merged into one opaque
boolean, and retrograde motion is deliberately not used as a condition in V1.
"""
from __future__ import annotations

from typing import Dict, List, NamedTuple


class ConditionSpec(NamedTuple):
    rule_id: str
    number: int
    title: str
    statement: str


CONDITIONS: List[ConditionSpec] = [
    ConditionSpec(
        "NB_001", 1,
        "Debilitation-sign lord in Kendra from Lagna",
        "The lord of the sign in which the planet is debilitated occupies a "
        "Kendra (1, 4, 7 or 10) counted from the Lagna.",
    ),
    ConditionSpec(
        "NB_002", 2,
        "Debilitation-sign lord in Kendra from Moon",
        "The lord of the sign in which the planet is debilitated occupies a "
        "Kendra (1, 4, 7 or 10) counted from the Moon.",
    ),
    ConditionSpec(
        "NB_003", 3,
        "Exaltation-sign lord in Kendra from Lagna",
        "The lord of the sign in which the planet would be exalted occupies a "
        "Kendra (1, 4, 7 or 10) counted from the Lagna.",
    ),
    ConditionSpec(
        "NB_004", 4,
        "Exaltation-sign lord in Kendra from Moon",
        "The lord of the sign in which the planet would be exalted occupies a "
        "Kendra (1, 4, 7 or 10) counted from the Moon.",
    ),
    ConditionSpec(
        "NB_005", 5,
        "Association with a cancellation lord",
        "The debilitated planet is conjunct with, or in mutual Graha Drishti "
        "with, the lord of its debilitation sign or the lord of its exaltation "
        "sign.",
    ),
    ConditionSpec(
        "NB_006", 6,
        "Debilitation lord and exaltation lord in mutual Kendras",
        "The lord of the debilitation sign and the lord of the exaltation sign "
        "occupy Kendras from each other (1, 4, 7 or 10 signs apart).",
    ),
]

CONDITION_BY_NUMBER: Dict[int, ConditionSpec] = {c.number: c for c in CONDITIONS}

KENDRA_OFFSETS_1_BASED = (1, 4, 7, 10)

V1_EXCLUSION_NOTE = (
    "Retrograde motion of the debilitated planet is not used as a cancellation "
    "condition in V1."
)

# --- Neecha Bhanga Raja Yoga (RULE YOGA_022) -------------------------------
# Kept deliberately distinct from plain cancellation.
NBRY_STATEMENT = (
    "Neecha Bhanga Raja Yoga is recorded only when the planet is debilitated, "
    "at least one Neecha Bhanga condition (NB_001..NB_006) is satisfied, and "
    "the planet additionally owns or occupies a Kendra or a Trikona house. "
    "Debilitation, Neecha Bhanga and Neecha Bhanga Raja Yoga remain three "
    "distinct states."
)
