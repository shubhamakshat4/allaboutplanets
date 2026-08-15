"""Panchadha Maitri rule tables (RULES MAITRI_001, MAITRI_002, MAITRI_003).

These are pure tables and pure functions. The engine that applies them to a
chart lives in ``relationship_engine.py``.
"""
from __future__ import annotations

from typing import Optional

from jhora import const

from .planetary_rules import NOT_DEFINED

# --- Natural relationship (RULE MAITRI_001) --------------------------------
# PyJHora's const.planet_relations is a 9x9 table with
#   3 = Friend, 2 = Neutral, 1 = Enemy, 5 = the planet itself.
NATURAL_FRIEND = "Friend"
NATURAL_NEUTRAL = "Neutral"
NATURAL_ENEMY = "Enemy"
SELF = "Self"

_NATURAL_CODE_NAMES = {
    const._FRIEND: NATURAL_FRIEND,
    const._NEUTRAL_SAMAM: NATURAL_NEUTRAL,
    const._ENEMY: NATURAL_ENEMY,
    const._OWNER_RULER: SELF,
}


def natural_relationship(planet_a: int, planet_b: int) -> str:
    """RULE MAITRI_001."""
    if planet_a == planet_b:
        return SELF
    try:
        code = const.planet_relations[planet_a][planet_b]
    except (IndexError, TypeError):
        return NOT_DEFINED
    return _NATURAL_CODE_NAMES.get(code, NOT_DEFINED)


# --- Temporary relationship (RULE MAITRI_002) ------------------------------
TEMPORARY_FRIEND = "Friend"
TEMPORARY_ENEMY = "Enemy"

# Offsets from a planet's own sign. PyJHora stores these 0-based, i.e. offset 1
# is the 2nd sign from the planet.
TEMPORARY_FRIEND_OFFSETS = tuple(const.temporary_friend_raasi_positions)  # 1,2,3,9,10,11
TEMPORARY_ENEMY_OFFSETS = tuple(const.temporary_enemy_raasi_positions)    # 0,4,5,6,7,8

# Human-readable house numbers for the evidence panel.
TEMPORARY_FRIEND_HOUSES = tuple(o + 1 for o in TEMPORARY_FRIEND_OFFSETS)   # 2,3,4,10,11,12
TEMPORARY_ENEMY_HOUSES = tuple(o + 1 for o in TEMPORARY_ENEMY_OFFSETS)     # 1,5,6,7,8,9


def temporary_relationship(sign_a: int, sign_b: int) -> str:
    """RULE MAITRI_002.

    ``sign_a`` is the sign occupied by the planet whose viewpoint is taken;
    ``sign_b`` is the sign occupied by the other planet.
    """
    offset = (sign_b - sign_a) % 12
    if offset in TEMPORARY_FRIEND_OFFSETS:
        return TEMPORARY_FRIEND
    return TEMPORARY_ENEMY


def temporary_offset_house(sign_a: int, sign_b: int) -> int:
    """The 1-based sign count from A to B, for the evidence panel."""
    return ((sign_b - sign_a) % 12) + 1


# --- Panchadha Maitri (RULE MAITRI_003) ------------------------------------
ATI_MITRA = "Ati Mitra"
MITRA = "Mitra"
SAMA = "Sama"
SHATRU = "Shatru"
ATI_SHATRU = "Ati Shatru"

PANCHADHA_ORDER = [ATI_MITRA, MITRA, SAMA, SHATRU, ATI_SHATRU]

# The combination table exactly as specified.
_PANCHADHA_TABLE = {
    (NATURAL_FRIEND, TEMPORARY_FRIEND): ATI_MITRA,
    (NATURAL_NEUTRAL, TEMPORARY_FRIEND): MITRA,
    (NATURAL_FRIEND, TEMPORARY_ENEMY): SAMA,
    (NATURAL_ENEMY, TEMPORARY_FRIEND): SAMA,
    (NATURAL_NEUTRAL, TEMPORARY_ENEMY): SHATRU,
    (NATURAL_ENEMY, TEMPORARY_ENEMY): ATI_SHATRU,
}

PANCHADHA_EXPLANATION = {
    ATI_MITRA: "Natural Friend + Temporary Friend",
    MITRA: "Natural Neutral + Temporary Friend",
    SAMA: "Natural Friend + Temporary Enemy, or Natural Enemy + Temporary Friend",
    SHATRU: "Natural Neutral + Temporary Enemy",
    ATI_SHATRU: "Natural Enemy + Temporary Enemy",
}


def panchadha_maitri(natural: str, temporary: str) -> str:
    """RULE MAITRI_003."""
    if natural in (SELF, NOT_DEFINED) or temporary == NOT_DEFINED:
        return NOT_DEFINED
    return _PANCHADHA_TABLE.get((natural, temporary), NOT_DEFINED)


# Mapping to PyJHora's own compound-relationship codes, used only by the test
# suite to prove the two implementations agree.
PYJHORA_COMPOUND_CODE_NAMES = {
    4: ATI_MITRA,
    3: MITRA,
    2: SAMA,
    1: SHATRU,
    0: ATI_SHATRU,
}
