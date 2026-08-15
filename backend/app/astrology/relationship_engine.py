"""The single Panchadha Maitri engine (RULES MAITRI_001/002/003).

Every planetary pair in this application — rashi lord, bhava lord, nakshatra
lord, navamsha lord, lagnesh, conjunct planet, aspecting planet, aspected
planet, yoga participant — resolves its relationship here. There is no other
relationship implementation in the codebase.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from .chart_calculator import ChartContext
from .rules import maitri_rules as mr
from .rules import planetary_rules as pr


def relationship(ctx: ChartContext, planet_a: int, planet_b: int) -> dict:
    """Full relationship record between two planets, with evidence."""
    if planet_a == planet_b:
        return {
            "planetA": planet_a,
            "planetAName": pr.planet_name(planet_a),
            "planetB": planet_b,
            "planetBName": pr.planet_name(planet_b),
            "naturalRelationship": mr.SELF,
            "temporaryRelationship": mr.SELF,
            "panchadhaMaitri": mr.SELF,
            "evidence": {
                "note": "A planet is not related to itself under the Panchadha "
                        "Maitri rule set.",
            },
            "sources": _sources(),
        }

    natural = mr.natural_relationship(planet_a, planet_b)

    sign_a = ctx.sign_of(planet_a)
    sign_b = ctx.sign_of(planet_b)
    temporary = mr.temporary_relationship(sign_a, sign_b)
    offset_house = mr.temporary_offset_house(sign_a, sign_b)

    panchadha = mr.panchadha_maitri(natural, temporary)

    return {
        "planetA": planet_a,
        "planetAName": pr.planet_name(planet_a),
        "planetB": planet_b,
        "planetBName": pr.planet_name(planet_b),
        "naturalRelationship": natural,
        "temporaryRelationship": temporary,
        "panchadhaMaitri": panchadha,
        "panchadhaExplanation": mr.PANCHADHA_EXPLANATION.get(panchadha),
        "evidence": {
            "naturalRule": (
                f"const.planet_relations[{pr.planet_name(planet_a)}]"
                f"[{pr.planet_name(planet_b)}] = {natural}"
            ),
            "planetASign": pr.sign_name(sign_a),
            "planetBSign": pr.sign_name(sign_b),
            "signCountFromAtoB": offset_house,
            "temporaryRule": (
                f"{pr.planet_name(planet_b)} occupies the {pr.ordinal(offset_house)} "
                f"sign from {pr.planet_name(planet_a)}. Signs "
                f"{', '.join(str(h) for h in mr.TEMPORARY_FRIEND_HOUSES)} are "
                f"temporary friends; signs "
                f"{', '.join(str(h) for h in mr.TEMPORARY_ENEMY_HOUSES)} are "
                f"temporary enemies. Result: {temporary}."
            ),
            "combination": (
                f"Natural {natural} + Temporary {temporary} = {panchadha}"
                if panchadha != pr.NOT_DEFINED
                else "Combination not defined in the selected rule set."
            ),
        },
        "sources": _sources(),
    }


def relationship_profile(ctx: ChartContext, planet: int) -> List[dict]:
    """SECTION Q — the planet's relationship with every other planet."""
    return [relationship(ctx, planet, other)
            for other in pr.ALL_PLANETS if other != planet]


def natural_relationship_only(planet_a: int, planet_b: int) -> str:
    return mr.natural_relationship(planet_a, planet_b)


def compound_matrix(ctx: ChartContext) -> Dict[int, Dict[int, str]]:
    """Full 9x9 Panchadha Maitri matrix for the chart."""
    out: Dict[int, Dict[int, str]] = {}
    for a in pr.ALL_PLANETS:
        out[a] = {}
        for b in pr.ALL_PLANETS:
            if a == b:
                out[a][b] = mr.SELF
                continue
            natural = mr.natural_relationship(a, b)
            temporary = mr.temporary_relationship(ctx.sign_of(a), ctx.sign_of(b))
            out[a][b] = mr.panchadha_maitri(natural, temporary)
    return out


def relationship_or_none(ctx: ChartContext, planet_a: int,
                         planet_b: Optional[int]) -> Optional[dict]:
    if planet_b is None:
        return None
    return relationship(ctx, planet_a, planet_b)


def _sources() -> dict:
    return {
        "natural": {"source": "PyJHora", "rule": "MAITRI_001",
                    "methodology": "const.planet_relations"},
        "temporary": {"source": "PyJHora", "rule": "MAITRI_002",
                      "methodology": "const.temporary_friend_raasi_positions"},
        "panchadha": {"source": "Custom Rule Engine", "rule": "MAITRI_003",
                      "methodology": "Supplied Panchadha Maitri combination table"},
    }


