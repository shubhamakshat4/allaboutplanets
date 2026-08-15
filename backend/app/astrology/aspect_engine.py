"""Graha Drishti given and received (SECTIONS N and O).

Which aspects exist comes entirely from PyJHora
(``house.graha_drishti_from_chart``). This module only inverts, labels and
attaches Panchadha Maitri to them.
"""
from __future__ import annotations

from typing import Dict, List

from .chart_calculator import ChartContext
from .relationship_engine import relationship
from .rules import planetary_rules as pr

_ASPECT_SOURCE = {
    "source": "PyJHora",
    "methodology": "house.graha_drishti_from_chart with const.graha_drishti",
    "rule": "ASPECT_001",
}

NODE_DRISHTI_NOTE = (
    "In this rule set Rahu and Ketu are given the 7th Graha Drishti only "
    "(PyJHora const.graha_drishti). Traditions that assign them the 5th and 9th "
    "are not applied."
)


def aspect_ordinal(ctx: ChartContext, source_planet: int, target_sign: int) -> int:
    """RULE ASPECT_001."""
    return ctx.house_from(ctx.sign_of(source_planet), target_sign)


def _ordinal_label(n: int) -> str:
    return f"{pr.ordinal(n)} Drishti"


def aspects_received(ctx: ChartContext, planet: int) -> List[dict]:
    """SECTION N — every planet giving Graha Drishti to ``planet``."""
    out: List[dict] = []
    for source in ctx.aspecting_planets.get(planet, []):
        ordinal = aspect_ordinal(ctx, source, ctx.sign_of(planet))
        out.append({
            "sourcePlanet": source,
            "sourcePlanetName": pr.planet_name(source),
            "targetPlanet": planet,
            "targetPlanetName": pr.planet_name(planet),
            "aspectType": _ordinal_label(ordinal),
            "aspectOrdinal": ordinal,
            "sourceHouse": ctx.bhava_of(source),
            "sourceSign": ctx.sign_of(source),
            "sourceSignName": pr.sign_name(ctx.sign_of(source)),
            "targetHouse": ctx.bhava_of(planet),
            "targetSign": ctx.sign_of(planet),
            "targetSignName": pr.sign_name(ctx.sign_of(planet)),
            "relationship": relationship(ctx, planet, source),
            "evidence": (
                f"{pr.planet_name(source)} occupies "
                f"{pr.sign_name(ctx.sign_of(source))} (house {ctx.bhava_of(source)}). "
                f"Its Graha Drishti set is "
                f"{sorted(pr.GRAHA_DRISHTI[source])} signs ahead. "
                f"{pr.sign_name(ctx.sign_of(planet))} is the {pr.ordinal(ordinal)} sign from it, "
                f"so {pr.planet_name(planet)} receives the {_ordinal_label(ordinal)}."
            ),
            "sources": _ASPECT_SOURCE,
        })
    out.sort(key=lambda a: a["sourcePlanet"])
    return out


def aspects_given(ctx: ChartContext, planet: int) -> dict:
    """SECTION O — houses and planets receiving ``planet``'s Graha Drishti."""
    aspected_signs = ctx.aspected_signs.get(planet, [])
    aspected_planets = ctx.aspected_planets.get(planet, [])

    houses: List[dict] = []
    for sign in aspected_signs:
        ordinal = ctx.house_from(ctx.sign_of(planet), sign)
        house_no = ctx.house_from(ctx.lagna_sign, sign)
        occupants = [p for p in ctx.planets_in_sign.get(sign, []) if p != planet]
        houses.append({
            "targetSign": sign,
            "targetSignName": pr.sign_name(sign),
            "targetHouse": house_no,
            "targetHouseLord": ctx.house_lord[house_no],
            "targetHouseLordName": pr.planet_name(ctx.house_lord[house_no]),
            "aspectType": _ordinal_label(ordinal),
            "aspectOrdinal": ordinal,
            "occupyingPlanets": [
                {"planet": p, "planetName": pr.planet_name(p)} for p in occupants
            ],
            "evidence": (
                f"{pr.planet_name(planet)} in {pr.sign_name(ctx.sign_of(planet))} "
                f"casts its {_ordinal_label(ordinal)} on {pr.sign_name(sign)} "
                f"(house {house_no})."
            ),
        })
    houses.sort(key=lambda h: h["aspectOrdinal"])

    planets: List[dict] = []
    for target in sorted(set(aspected_planets)):
        if target == planet:
            continue
        ordinal = aspect_ordinal(ctx, planet, ctx.sign_of(target))
        planets.append({
            "sourcePlanet": planet,
            "sourcePlanetName": pr.planet_name(planet),
            "targetPlanet": target,
            "targetPlanetName": pr.planet_name(target),
            "aspectType": _ordinal_label(ordinal),
            "aspectOrdinal": ordinal,
            "sourceHouse": ctx.bhava_of(planet),
            "targetHouse": ctx.bhava_of(target),
            "targetSign": ctx.sign_of(target),
            "targetSignName": pr.sign_name(ctx.sign_of(target)),
            "relationship": relationship(ctx, planet, target),
            "evidence": (
                f"{pr.planet_name(planet)} casts its {_ordinal_label(ordinal)} on "
                f"{pr.sign_name(ctx.sign_of(target))}, which "
                f"{pr.planet_name(target)} occupies."
            ),
            "sources": _ASPECT_SOURCE,
        })

    return {
        "houses": houses,
        "planets": planets,
        "drishtiSet": sorted(pr.GRAHA_DRISHTI[planet]),
        "drishtiSetText": ", ".join(_ordinal_label(n)
                                    for n in sorted(pr.GRAHA_DRISHTI[planet])),
        "nodeNote": NODE_DRISHTI_NOTE if planet in pr.NODES else None,
        "sources": _ASPECT_SOURCE,
    }


def has_mutual_drishti(ctx: ChartContext, planet_a: int, planet_b: int) -> bool:
    """Both planets aspect each other. Used by the yoga engine."""
    return (planet_b in ctx.aspected_planets.get(planet_a, [])
            and planet_a in ctx.aspected_planets.get(planet_b, []))


def aspects_planet(ctx: ChartContext, source: int, target: int) -> bool:
    return target in ctx.aspected_planets.get(source, [])


def aspects_house(ctx: ChartContext, planet: int, house: int) -> bool:
    return ctx.house_sign[house] in ctx.aspected_signs.get(planet, [])


def aspecting_lagna(ctx: ChartContext, planet: int) -> Dict[str, object]:
    """SECTION F helper — does the planet aspect the Lagna?"""
    result = ctx.lagna_sign in ctx.aspected_signs.get(planet, [])
    ordinal = ctx.house_from(ctx.sign_of(planet), ctx.lagna_sign)
    return {
        "aspectsLagna": result,
        "aspectType": _ordinal_label(ordinal) if result else None,
        "evidence": (
            f"{pr.planet_name(planet)} occupies "
            f"{pr.sign_name(ctx.sign_of(planet))}. The Lagna sign "
            f"{pr.sign_name(ctx.lagna_sign)} is the {pr.ordinal(ordinal)} sign from it. "
            f"{pr.planet_name(planet)}'s Graha Drishti set is "
            f"{sorted(pr.GRAHA_DRISHTI[planet])}, so the Lagna is "
            f"{'aspected' if result else 'not aspected'}."
        ),
        "sources": _ASPECT_SOURCE,
    }
