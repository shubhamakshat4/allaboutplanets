"""Declarations for the curated V1 yoga set (RULES YOGA_001 .. YOGA_022).

The engine in ``yoga_engine.py`` evaluates these; this module holds only the
declarative constants so the rules can be reviewed without reading the engine.
"""
from __future__ import annotations

from typing import Dict, List, NamedTuple

from .planetary_rules import (
    JUPITER, MARS, MERCURY, MOON, SATURN, SUN, VENUS,
)


class YogaSpec(NamedTuple):
    rule_id: str
    key: str
    name: str
    summary: str


YOGA_SPECS: List[YogaSpec] = [
    YogaSpec("YOGA_001", "raja_yoga", "Raja Yoga",
             "Kendra lord and Trikona lord associate by conjunction, mutual Graha "
             "Drishti or sign exchange."),
    YogaSpec("YOGA_002", "dharma_karmadhipati", "Dharma-Karmadhipati Yoga",
             "9th lord and 10th lord associate by conjunction, mutual Graha "
             "Drishti or sign exchange."),
    YogaSpec("YOGA_003", "ruchaka", "Ruchaka Yoga",
             "Mars in Aries, Scorpio or Capricorn and in a Kendra from Lagna."),
    YogaSpec("YOGA_004", "bhadra", "Bhadra Yoga",
             "Mercury in Gemini or Virgo and in a Kendra from Lagna."),
    YogaSpec("YOGA_005", "hamsa", "Hamsa Yoga",
             "Jupiter in Sagittarius, Pisces or Cancer and in a Kendra from Lagna."),
    YogaSpec("YOGA_006", "malavya", "Malavya Yoga",
             "Venus in Taurus, Libra or Pisces and in a Kendra from Lagna."),
    YogaSpec("YOGA_007", "sasa", "Sasa Yoga",
             "Saturn in Capricorn, Aquarius or Libra and in a Kendra from Lagna."),
    YogaSpec("YOGA_008", "gaja_kesari", "Gaja Kesari Yoga",
             "Jupiter in a Kendra from Lagna or Moon, with a qualifying benefic "
             "association, not debilitated, not combust, not in an enemy sign."),
    YogaSpec("YOGA_009", "budha_aditya", "Budha-Aditya Yoga",
             "Sun and Mercury in the same Rashi."),
    YogaSpec("YOGA_010", "chandra_mangala", "Chandra-Mangala Yoga",
             "Moon and Mars in the same Rashi."),
    YogaSpec("YOGA_011", "guru_mangala", "Guru-Mangala Yoga",
             "Jupiter and Mars in the same Rashi."),
    YogaSpec("YOGA_012", "adhi", "Adhi Yoga",
             "Natural benefics occupy the 6th, 7th and/or 8th from the Moon."),
    YogaSpec("YOGA_013", "amala", "Amala Yoga",
             "A natural benefic occupies the 10th from Lagna or the 10th from the Moon."),
    YogaSpec("YOGA_014", "harsha", "Harsha Yoga",
             "The 6th lord occupies the 6th, 8th or 12th house."),
    YogaSpec("YOGA_015", "sarala", "Sarala Yoga",
             "The 8th lord occupies the 6th, 8th or 12th house."),
    YogaSpec("YOGA_016", "vimala", "Vimala Yoga",
             "The 12th lord occupies the 6th, 8th or 12th house."),
    YogaSpec("YOGA_017", "dhana", "Dhana Yoga",
             "Lords of the 2nd, 5th, 9th and 11th associate, with the 2nd or 11th "
             "lord among the participants."),
    YogaSpec("YOGA_018", "lakshmi", "Lakshmi Yoga",
             "Lagna lord in a Kendra or Trikona, and the 9th lord in own, "
             "Mooltrikona or exaltation sign while in a Kendra or Trikona."),
    YogaSpec("YOGA_019", "saraswati", "Saraswati Yoga",
             "Jupiter, Venus and Mercury each in the 2nd, a Kendra or a Trikona, "
             "with Jupiter additionally in own, Mooltrikona, exaltation or "
             "friend's sign."),
    YogaSpec("YOGA_020", "kemadruma", "Kemadruma Yoga",
             "No qualifying planet in the 2nd or 12th from the Moon."),
    YogaSpec("YOGA_021", "parivartana", "Parivartana Yoga",
             "Two planets occupy each other's owned signs."),
    YogaSpec("YOGA_022", "neecha_bhanga_raja_yoga", "Neecha Bhanga Raja Yoga",
             "A debilitated planet with at least one satisfied Neecha Bhanga "
             "condition that also owns or occupies a Kendra or Trikona."),
]

YOGA_SPEC_BY_KEY: Dict[str, YogaSpec] = {y.key: y for y in YOGA_SPECS}

# --- Panchamahapurusha definitions (YOGA_003 .. YOGA_007) ------------------
# Sign indices are 0-based: Aries = 0.
MAHAPURUSHA = {
    "ruchaka": {"planet": MARS, "signs": [0, 7, 9]},        # Aries, Scorpio, Capricorn
    "bhadra": {"planet": MERCURY, "signs": [2, 5]},          # Gemini, Virgo
    "hamsa": {"planet": JUPITER, "signs": [8, 11, 3]},       # Sagittarius, Pisces, Cancer
    "malavya": {"planet": VENUS, "signs": [1, 6, 11]},       # Taurus, Libra, Pisces
    "sasa": {"planet": SATURN, "signs": [9, 10, 6]},         # Capricorn, Aquarius, Libra
}

# --- Association types -----------------------------------------------------
ASSOC_CONJUNCTION = "Conjunction"
ASSOC_MUTUAL_DRISHTI = "Mutual Graha Drishti"
ASSOC_PARIVARTANA = "Sign exchange (Parivartana)"

# --- Dhana Yoga (YOGA_017) -------------------------------------------------
DHANA_HOUSES = (2, 5, 9, 11)
DHANA_REQUIRED_HOUSES = (2, 11)

# --- Viparita-family yogas (YOGA_014 .. YOGA_016) --------------------------
VIPARITA_TARGET_HOUSES = (6, 8, 12)
VIPARITA_YOGAS = {
    "harsha": 6,
    "sarala": 8,
    "vimala": 12,
}

# --- Kemadruma (YOGA_020) --------------------------------------------------
# Conventional formulation used consistently: the Sun and the nodes do not
# relieve Kemadruma; every other graha does.
KEMADRUMA_EXCLUDED_PLANETS = (SUN, 7, 8)
KEMADRUMA_NOTE = (
    "The Sun, Rahu and Ketu are excluded from relieving the formation. This is "
    "the conventional formulation and is applied consistently."
)

# --- Adhi (YOGA_012) -------------------------------------------------------
ADHI_HOUSES_FROM_MOON = (6, 7, 8)

# --- Saraswati (YOGA_019) --------------------------------------------------
SARASWATI_PLANETS = (JUPITER, VENUS, MERCURY)
SARASWATI_ALLOWED_HOUSES = (1, 2, 4, 5, 7, 9, 10)  # 2nd + Kendra + Trikona

# --- Gaja Kesari (YOGA_008) ------------------------------------------------
# The formation condition and the strengthening conditions are reported
# separately rather than merged.
#
# The core formulation given by the common classical sources is simply
# "Jupiter in a Kendra from the Moon" (a conjunction being the 1st from the
# Moon, and therefore a Kendra). The four further conditions -- benefic
# association, not debilitated, not combust, not in an enemy's sign -- are
# widely presented as conditions for the yoga to yield its full results, not as
# conditions for it to form at all. Traditions differ on the last of these in
# particular.
#
# Collapsing both sets into one Present/Not Present verdict would hide from the
# astrologer that the core formation exists, so the formation drives the status
# and every strengthening condition is reported as an independent fact.
GROUP_CORE = "Core formation"
GROUP_STRENGTHENING = "Strengthening condition"

GAJA_KESARI_NOTE = (
    "Status reflects the core formation only: Jupiter in a Kendra (1, 4, 7, 10) "
    "from the Lagna or from the Moon. The four strengthening conditions are "
    "reported separately and independently, because classical sources differ on "
    "whether they govern the formation of the yoga or only the extent of its "
    "results. The astrologer decides which reading to apply."
)
