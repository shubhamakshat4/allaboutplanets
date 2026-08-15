"""Declarations for the curated V1 dosha set (RULES DOSHA_001 .. DOSHA_014).

Declarative only, so the rules layer stays free of any dependency on the
engines. ``dosha_engine.py`` evaluates these against a chart.
"""
from __future__ import annotations

from typing import Dict, List, NamedTuple

from .planetary_rules import MARS, RAHU, SATURN, SUN, KETU


class DoshaSpec(NamedTuple):
    rule_id: str
    key: str
    name: str
    formation: str


DOSHA_SPECS: List[DoshaSpec] = [
    DoshaSpec("DOSHA_001", "mangal", "Mangal Dosha (Kuja Dosha)",
              "Mars occupies the 1st, 2nd, 4th, 7th, 8th or 12th house, "
              "counted from the Lagna, the Moon or Venus."),
    DoshaSpec("DOSHA_002", "kaal_sarpa", "Kaal Sarpa Dosha",
              "All seven grahas from the Sun to Saturn lie within the arc "
              "running from Rahu to Ketu."),
    DoshaSpec("DOSHA_003", "guru_chandal", "Guru Chandal Dosha",
              "Jupiter shares its sign with Rahu or Ketu."),
    DoshaSpec("DOSHA_004", "angarak", "Angarak Dosha",
              "Mars shares its sign with Rahu or Ketu."),
    DoshaSpec("DOSHA_005", "grahan", "Grahan Dosha",
              "The Sun or the Moon shares its sign with Rahu or Ketu."),
    DoshaSpec("DOSHA_006", "shrapit", "Shrapit Dosha",
              "Saturn shares its sign with Rahu."),
    DoshaSpec("DOSHA_007", "vish", "Vish Dosha (Punarphoo)",
              "The Moon shares its sign with Saturn."),
    DoshaSpec("DOSHA_008", "kemadruma", "Kemadruma Dosha",
              "No graha other than the Sun and the nodes occupies the 2nd or "
              "the 12th sign from the Moon."),
    DoshaSpec("DOSHA_009", "sakata", "Sakata Dosha",
              "The Moon occupies the 6th, 8th or 12th sign counted from Jupiter."),
    DoshaSpec("DOSHA_010", "papakartari", "Papakartari Dosha",
              "A graha stands hemmed, with a natural malefic in both the 2nd "
              "and the 12th sign from it."),
    DoshaSpec("DOSHA_011", "kendradhipatya", "Kendradhipatya Dosha",
              "A natural benefic lords a Kendra, the 4th, 7th or 10th house."),
    DoshaSpec("DOSHA_012", "daridra", "Daridra Dosha",
              "The lord of the 11th house occupies the 6th, 8th or 12th house."),
    DoshaSpec("DOSHA_013", "amavasya", "Amavasya Dosha",
              "The Sun and the Moon stand within 12 degrees of each other, the "
              "birth falling close to the new moon."),
    DoshaSpec("DOSHA_014", "pitru", "Pitru Dosha",
              "Rahu or Ketu occupies the 9th house, or the lord of the 9th "
              "occupies the 6th, 8th or 12th."),
]

SPEC_BY_KEY = {d.key: d for d in DOSHA_SPECS}

# Grounds on which the classics commonly hold a dosha to be lifted. These are
# shown to the astrologer; the software does not apply them.
CANCELLATIONS: Dict[str, str] = {
    "mangal": (
        "Commonly held to be lifted when Mars stands in its own sign or is "
        "exalted, when it occupies Aries, Scorpio, Capricorn, Cancer, Leo or "
        "Aquarius, when Jupiter or Venus joins or aspects it, or when both "
        "charts in a match carry the same dosha. Schools differ over whether "
        "the 2nd house counts at all, and over reckoning from the Moon and "
        "Venus as well as the Lagna."),
    "kaal_sarpa": (
        "Many hold the dosha to be partial rather than whole when a graha sits "
        "exactly on the nodal axis, and lifted where strong Raja Yogas are "
        "present. The formation itself is a modern favourite and is not found "
        "under this name in the older texts."),
    "guru_chandal": (
        "Often held to be softened when Jupiter is strong by sign or when the "
        "combination falls in a Trikona."),
    "kemadruma": (
        "Commonly held to be lifted when a graha occupies a Kendra from the "
        "Lagna or the Moon, when the Moon is joined or aspected by a benefic, "
        "or when the Moon is strong."),
    "papakartari": (
        "The hemming is weighed differently when the enclosing malefics are "
        "themselves functional benefics for the Lagna."),
    "kendradhipatya": (
        "Held to press harder on the greater benefics, Jupiter and Venus, than "
        "on Mercury or the Moon, and to be eased when the same graha also "
        "lords a Trikona."),
    "amavasya": (
        "Weighed by how close the two stand: a gap of a degree or two is read "
        "very differently from one of ten."),
    "pitru": (
        "The formulations vary widely between schools; the one used here is "
        "only one of several in circulation."),
}

MALEFICS_FOR_HEMMING = (SUN, MARS, SATURN, RAHU, KETU)
MANGAL_HOUSES = (1, 2, 4, 7, 8, 12)


