"""Combustion / Asta (RULE COMBUST_001).

Evaluated by this engine rather than taken from PyJHora, because PyJHora 4.8.7
misindexes its own orb table and compares raw longitudes instead of the shorter
arc. See ``rules/planetary_rules.py`` for the detail. PyJHora's verdict is still
computed and reported beside ours so the divergence is visible, never hidden.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from .rules import planetary_rules as pr

SOURCE = {
    "source": "Custom Rule Engine",
    "rule": "COMBUST_001",
    "methodology": "Classical Parashari orbs of combustion, shorter-arc separation",
}


def separation_from_sun(planet_longitude: float, sun_longitude: float) -> float:
    """Shorter arc between a planet and the Sun, 0-180 degrees."""
    diff = abs(planet_longitude - sun_longitude) % 360.0
    return min(diff, 360.0 - diff)


def threshold_for(planet: int, retrograde: bool) -> Optional[float]:
    if planet not in pr.COMBUSTION_ELIGIBLE:
        return None
    table = (pr.COMBUSTION_RANGE_RETROGRADE if retrograde
             else pr.COMBUSTION_RANGE_DIRECT)
    return table.get(planet)


def is_combust(planet: int, planet_longitude: float, sun_longitude: float,
               retrograde: bool) -> bool:
    """RULE COMBUST_001."""
    threshold = threshold_for(planet, retrograde)
    if threshold is None:
        return False
    return separation_from_sun(planet_longitude, sun_longitude) <= threshold


def combust_planets(longitudes: Dict[int, float],
                    retrograde: List[int]) -> List[int]:
    """Every combust planet in a chart, by rule COMBUST_001."""
    sun_longitude = longitudes[pr.SUN]
    return [
        planet for planet in pr.COMBUSTION_ELIGIBLE
        if planet in longitudes
        and is_combust(planet, longitudes[planet], sun_longitude,
                       planet in retrograde)
    ]
