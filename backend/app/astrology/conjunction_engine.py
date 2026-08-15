"""Conjunctions (RULE CONJ_001) — SECTION M.

A conjunction is same-Rashi occupancy. Same-Bhava is reported as a separate
fact because the whole-sign frame makes them coincide while Bhava Chalita may
not.
"""
from __future__ import annotations

from typing import List

from .chart_calculator import ChartContext
from .relationship_engine import relationship
from .rules import planetary_rules as pr

_SOURCE = {"source": "Custom Rule Engine", "rule": "CONJ_001",
           "methodology": "Same Rashi occupancy in D1"}


def separation(long_a: float, long_b: float) -> float:
    """Shorter arc between two absolute longitudes, in degrees."""
    diff = abs(long_a - long_b) % 360.0
    return min(diff, 360.0 - diff)


def conjunctions(ctx: ChartContext, planet: int) -> List[dict]:
    pos = ctx.positions[planet]
    out: List[dict] = []

    for other in ctx.planets_in_sign.get(pos.sign, []):
        if other == planet:
            continue
        other_pos = ctx.positions[other]
        sep = separation(pos.absolute_longitude, other_pos.absolute_longitude)
        out.append({
            "planetA": planet,
            "planetAName": pr.planet_name(planet),
            "planetB": other,
            "planetBName": pr.planet_name(other),
            "rashi": pos.sign,
            "rashiName": pr.sign_name(pos.sign),
            "sameRashi": True,
            "sameBhava": pos.bhava == other_pos.bhava,
            "bhavaA": pos.bhava,
            "bhavaB": other_pos.bhava,
            "sameBhavaChalita": (
                pos.bhava_chalita == other_pos.bhava_chalita
                if pos.bhava_chalita is not None and other_pos.bhava_chalita is not None
                else None
            ),
            "bhavaChalitaA": pos.bhava_chalita,
            "bhavaChalitaB": other_pos.bhava_chalita,
            "degreeA": round(pos.degree_in_sign, 6),
            "degreeADms": pr.to_dms(pos.degree_in_sign),
            "degreeB": round(other_pos.degree_in_sign, 6),
            "degreeBDms": pr.to_dms(other_pos.degree_in_sign),
            "longitudeA": round(pos.absolute_longitude, 6),
            "longitudeB": round(other_pos.absolute_longitude, 6),
            "separation": round(sep, 6),
            "separationDms": pr.to_dms(sep),
            "relationship": relationship(ctx, planet, other),
            "evidence": (
                f"{pr.planet_name(planet)} at {pr.to_dms(pos.degree_in_sign)} and "
                f"{pr.planet_name(other)} at {pr.to_dms(other_pos.degree_in_sign)} "
                f"both occupy {pr.sign_name(pos.sign)}. "
                f"Separation = {pr.to_dms(sep)}."
            ),
            "sources": _SOURCE,
        })

    out.sort(key=lambda c: c["separation"])
    return out


def are_conjunct(ctx: ChartContext, planet_a: int, planet_b: int) -> bool:
    return ctx.sign_of(planet_a) == ctx.sign_of(planet_b)
