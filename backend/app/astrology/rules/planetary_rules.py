"""Naming tables and structural constants.

Everything astrological here is read from PyJHora's ``const`` module wherever
PyJHora defines it, so that a single source of truth governs the calculations.
Only presentation names and the house-category sets that the specification
fixes explicitly are declared locally.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from jhora import const

# --- Planet identity -------------------------------------------------------
SUN, MOON, MARS, MERCURY, JUPITER, VENUS, SATURN, RAHU, KETU = range(9)

LAGNA = "L"

ALL_PLANETS: List[int] = list(range(9))
SUN_TO_SATURN: List[int] = list(range(7))
NODES: List[int] = [RAHU, KETU]

PLANET_NAMES: Dict[int, str] = {
    SUN: "Sun", MOON: "Moon", MARS: "Mars", MERCURY: "Mercury",
    JUPITER: "Jupiter", VENUS: "Venus", SATURN: "Saturn",
    RAHU: "Rahu", KETU: "Ketu",
}

PLANET_SANSKRIT: Dict[int, str] = {
    SUN: "Surya", MOON: "Chandra", MARS: "Mangala", MERCURY: "Budha",
    JUPITER: "Guru", VENUS: "Shukra", SATURN: "Shani",
    RAHU: "Rahu", KETU: "Ketu",
}

PLANET_SYMBOLS: Dict[int, str] = {
    SUN: "☉", MOON: "☽", MARS: "♂", MERCURY: "☿",
    JUPITER: "♃", VENUS: "♀", SATURN: "♄",
    RAHU: "☊", KETU: "☋",
}

# --- Signs -----------------------------------------------------------------
SIGN_NAMES: List[str] = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGN_SANSKRIT: List[str] = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena",
]

# Sign lords, read from PyJHora (Aries..Pisces).
SIGN_LORDS: List[int] = list(const._house_owners_list)

# --- Nakshatras ------------------------------------------------------------
NAKSHATRA_NAMES: List[str] = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada",
    "Revati",
]

# Vimshottari sequence: lords of nakshatras 1..9, repeating three times.
# RULE NAK_001
VIMSHOTTARI_ORDER: List[int] = [
    KETU, VENUS, SUN, MOON, MARS, RAHU, JUPITER, SATURN, MERCURY,
]


def nakshatra_lord(nakshatra_index_1_based: int) -> int:
    """RULE NAK_001."""
    return VIMSHOTTARI_ORDER[(nakshatra_index_1_based - 1) % 9]


# --- House categories (RULE FUNC_002) --------------------------------------
KENDRA_HOUSES = (1, 4, 7, 10)
TRIKONA_HOUSES = (1, 5, 9)
DUSTHANA_HOUSES = (6, 8, 12)
UPACHAYA_HOUSES = (3, 6, 10, 11)
MARAKA_HOUSES = (2, 7)

# --- Sign modality / parity (RULES FUNC_006, FUNC_007) ---------------------
MOVABLE_SIGNS = tuple(const.movable_signs)   # Aries, Cancer, Libra, Capricorn
FIXED_SIGNS = tuple(const.fixed_signs)       # Taurus, Leo, Scorpio, Aquarius
DUAL_SIGNS = tuple(const.dual_signs)         # Gemini, Virgo, Sagittarius, Pisces

ODD_SIGNS = tuple(const.odd_signs)           # 0-based: Aries, Gemini, ...
EVEN_SIGNS = tuple(const.even_signs)


def sign_modality(sign: int) -> str:
    """RULE FUNC_006."""
    if sign in MOVABLE_SIGNS:
        return "Movable"
    if sign in FIXED_SIGNS:
        return "Fixed"
    return "Dual"


def sign_parity(sign: int) -> str:
    """RULE FUNC_007. Sign index is 0-based, so Aries (0) is an odd sign."""
    return "Odd" if sign in ODD_SIGNS else "Even"


# --- Badhaka (RULE FUNC_003) ----------------------------------------------
BADHAKA_BY_MODALITY = {"Movable": 11, "Fixed": 9, "Dual": 7}


def badhaka_house(lagna_sign: int) -> int:
    """RULE FUNC_003."""
    return BADHAKA_BY_MODALITY[sign_modality(lagna_sign)]


# --- Dignity tables --------------------------------------------------------
# PyJHora encodes dignity as 5=Owner 4=Exalted 3=Friend 2=Neutral 1=Enemy 0=Debilitated
# Dignity codes, re-exported so the engines never import PyJHora internals
# directly. The rules layer owns every table read from the library.
DIGNITY_OWN = const._OWNER_RULER
DIGNITY_EXALTED = const._EXALTED_UCCHAM
DIGNITY_FRIEND = const._FRIEND
DIGNITY_NEUTRAL = const._NEUTRAL_SAMAM
DIGNITY_ENEMY = const._ENEMY
DIGNITY_DEBILITATED = const._DEBILITATED_NEECHAM

DIGNITY_CODE_NAMES: Dict[int, str] = {
    DIGNITY_OWN: "Own Sign",
    DIGNITY_EXALTED: "Exaltation Sign",
    DIGNITY_FRIEND: "Friend's Sign",
    DIGNITY_NEUTRAL: "Neutral Sign",
    DIGNITY_ENEMY: "Enemy's Sign",
    DIGNITY_DEBILITATED: "Debilitation Sign",
}

NOT_DEFINED = "Not defined in selected rule set"
NOT_AVAILABLE = "Not available"
NOT_APPLICABLE = "Not applicable"


def dignity_code(planet: int, sign: int) -> int:
    """RULE DIGNITY_001."""
    return const.house_strengths_of_planets[planet][sign]


def owned_signs(planet: int) -> List[int]:
    """Signs lorded by a planet. Rahu and Ketu lord no sign in this rule set."""
    return [s for s, lord in enumerate(SIGN_LORDS) if lord == planet]


def exaltation_signs(planet: int) -> List[int]:
    """Signs in which a planet is exalted.

    For Sun..Saturn this is derived from ``const.planet_deep_exaltation_longitudes``
    rather than from ``const.house_strengths_of_planets``. The dignity table
    stores one code per cell, so where exaltation and own-sign coincide it can
    only record one of them — it marks Mercury in Virgo as Own Sign, which would
    otherwise hide Mercury's exaltation. The deep-exaltation longitudes are
    unambiguous, so they are the source for this fact.

    Rahu and Ketu have no deep-exaltation longitude, so their exaltation signs
    come from the dignity table (which gives each of them two).
    """
    if planet in SUN_TO_SATURN:
        return [int(const.planet_deep_exaltation_longitudes[planet] // 30) % 12]
    return [s for s in range(12)
            if const.house_strengths_of_planets[planet][s] == const._EXALTED_UCCHAM]


def debilitation_signs(planet: int) -> List[int]:
    """Signs in which a planet is debilitated. See ``exaltation_signs``."""
    if planet in SUN_TO_SATURN:
        return [int(const.planet_deep_debilitation_longitudes[planet] // 30) % 12]
    return [s for s in range(12)
            if const.house_strengths_of_planets[planet][s] == const._DEBILITATED_NEECHAM]


def exaltation_sign(planet: int) -> Optional[int]:
    signs = exaltation_signs(planet)
    return signs[0] if signs else None


def debilitation_sign(planet: int) -> Optional[int]:
    signs = debilitation_signs(planet)
    return signs[0] if signs else None


def deep_exaltation_longitude(planet: int) -> Optional[float]:
    if planet in SUN_TO_SATURN:
        return const.planet_deep_exaltation_longitudes[planet]
    return None


def deep_debilitation_longitude(planet: int) -> Optional[float]:
    if planet in SUN_TO_SATURN:
        return const.planet_deep_debilitation_longitudes[planet]
    return None


# Mooltrikona ranges as given in Brihat Parashara Hora Shastra, Ch. 3.
#
# Declared here rather than read from PyJHora, whose table differs from BPHS on
# two entries: it starts the Moon at Taurus 3 (BPHS: 4, the degree after the
# Moon's exaltation point) and Mercury at Virgo 15 (BPHS: 16, the degree after
# Mercury's exaltation point). Both boundaries matter, because a planet sitting
# on them changes classification.
#
# Undefined for Rahu and Ketu: BPHS assigns them no Mooltrikona (see RK_002).
MOOLTRIKONA_RANGES: Dict[int, tuple] = {
    SUN:     (4, 0.0, 20.0),    # Leo 0-20
    MOON:    (1, 4.0, 30.0),    # Taurus 4-30
    MARS:    (0, 0.0, 12.0),    # Aries 0-12
    MERCURY: (5, 16.0, 20.0),   # Virgo 16-20
    JUPITER: (8, 0.0, 10.0),    # Sagittarius 0-10
    VENUS:   (6, 0.0, 15.0),    # Libra 0-15
    SATURN:  (10, 0.0, 20.0),   # Aquarius 0-20
}


def mooltrikona_range(planet: int):
    """RULE DIGNITY_002. Returns (sign, start_deg, end_deg) or None if undefined."""
    return MOOLTRIKONA_RANGES.get(planet)


# --- Graha Drishti table (read from PyJHora) -------------------------------
GRAHA_DRISHTI = {p: list(const.graha_drishti[p]) for p in ALL_PLANETS}

# --- Divisional charts requested by the specification ----------------------
VARGA_FACTORS: List[int] = [1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60]

VARGA_NAMES: Dict[int, str] = {
    1: "Rashi (D1)", 2: "Hora (D2)", 3: "Drekkana (D3)", 4: "Chaturthamsha (D4)",
    7: "Saptamsha (D7)", 9: "Navamsha (D9)", 10: "Dashamsha (D10)",
    12: "Dwadashamsha (D12)", 16: "Shodashamsha (D16)", 20: "Vimshamsha (D20)",
    24: "Chaturvimshamsha (D24)", 27: "Nakshatramsha (D27)", 30: "Trimshamsha (D30)",
    40: "Khavedamsha (D40)", 45: "Akshavedamsha (D45)", 60: "Shashtiamsha (D60)",
}

# Vargas in which a sign is not derived by a simple 30/D division and for which a
# lord-based dignity readout would be misleading are still reported by sign; the
# UI labels the varga so no methodology is implied.

# --- Combustion (Asta) thresholds -----------------------------------------
#
# Classical Parashari orbs of combustion, measured from the Sun.
#
# Declared here rather than read from PyJHora. PyJHora 4.8.7 indexes its
# combustion table as `combustion_range[p - 2]` while iterating planet ids 1..6
# (Moon..Saturn), so every planet receives the previous planet's orb and the
# Moon wraps to index -1 and picks up Saturn's. Its comparison also comes from
# raw longitudes rather than the shorter arc, so a pair straddling 0 Aries is
# missed. Both are demonstrable faults, so combustion is evaluated by rule
# COMBUST_001 here and PyJHora's verdict is reported alongside for comparison.
COMBUSTION_RANGE_DIRECT: Dict[int, float] = {
    MOON: 12.0,
    MARS: 17.0,
    MERCURY: 14.0,
    JUPITER: 11.0,
    VENUS: 10.0,
    SATURN: 15.0,
}

# Retrograde orbs. The classical statement narrows only Mercury and Venus; the
# remaining bodies keep their direct-motion orb (and the Moon never retrogrades).
COMBUSTION_RANGE_RETROGRADE: Dict[int, float] = {
    MOON: 12.0,
    MARS: 17.0,
    MERCURY: 12.0,
    VENUS: 8.0,
    JUPITER: 11.0,
    SATURN: 15.0,
}

COMBUSTION_ELIGIBLE = (MOON, MARS, MERCURY, JUPITER, VENUS, SATURN)

# --- Graha Yuddha categories (from PyJHora's docstring) --------------------
GRAHA_YUDDHA_CATEGORIES: Dict[int, str] = {
    0: "Bhed-yuti",
    1: "Ullekh-yuti",
    2: "Apsavya-yuti",
    3: "Anshumard-yuti",
}
GRAHA_YUDDHA_ELIGIBLE = (MARS, MERCURY, JUPITER, VENUS, SATURN)

# --- Shadbala ---------------------------------------------------------------
REQUIRED_SHADBALA_RUPAS: Dict[int, float] = {
    p: const.shad_bala_factors[p] for p in SUN_TO_SATURN
}


# --- Formatting helpers ----------------------------------------------------
def to_dms(degrees: float) -> str:
    """Format a decimal degree value as D° MM' SS\"."""
    neg = degrees < 0
    degrees = abs(degrees)
    d = int(degrees)
    rem = (degrees - d) * 60.0
    m = int(rem)
    s = (rem - m) * 60.0
    # Guard the rounding boundary so 29.99999 never renders as 30° 00' 60".
    if round(s, 2) >= 60.0:
        s = 0.0
        m += 1
    if m >= 60:
        m = 0
        d += 1
    return f"{'-' if neg else ''}{d}° {m:02d}' {s:05.2f}\""


def ordinal(n: int) -> str:
    """1 -> '1st', 2 -> '2nd', 3 -> '3rd', 4 -> '4th', 11 -> '11th'."""
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def sign_name(sign: int) -> str:
    return SIGN_NAMES[sign % 12]


def planet_name(planet) -> str:
    if planet == LAGNA:
        return "Lagna"
    return PLANET_NAMES[planet]
