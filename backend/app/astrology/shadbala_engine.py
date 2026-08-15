"""Shadbala presentation (SECTION R).

Every number comes from PyJHora. This module reshapes them for one planet and
attaches the required minimum. It deliberately emits no qualitative label of
any kind — no "strong", "weak", "excellent" or "poor".
"""
from __future__ import annotations

from typing import List, Optional

from .chart_calculator import ChartContext
from .rules import planetary_rules as pr

_SOURCE = {"source": "PyJHora", "rule": None,
           "methodology": "strength.shad_bala and its component functions"}

STHANA_COMPONENT_LABELS = [
    ("uchcha_bala", "Uchcha Bala"),
    ("saptavargaja_bala", "Saptavargaja Bala"),
    ("oja_yugma_bala", "Oja-Yugma Bala"),
    ("kendradi_bala", "Kendradi Bala"),
    ("drekkana_bala", "Drekkana Bala"),
]

KALA_COMPONENT_LABELS = [
    ("nathonnatha_bala", "Nathonnatha Bala"),
    ("paksha_bala", "Paksha Bala"),
    ("tribhaga_bala", "Tribhaga Bala"),
    ("varsha_bala", "Varsha Bala"),
    ("masa_bala", "Masa Bala"),
    ("dina_bala", "Dina Bala"),
    ("hora_bala", "Hora Bala"),
    ("ayana_bala", "Ayana Bala"),
    ("yuddha_bala", "Yuddha Bala"),
]


def shadbala(ctx: ChartContext, planet: int) -> dict:
    if planet in pr.NODES:
        return {
            "available": False,
            "reason": (
                "Shadbala is defined for the Sun through Saturn in the selected "
                "calculation engine. PyJHora does not compute it for Rahu or Ketu."
            ),
            "status": pr.NOT_AVAILABLE,
            "sources": _SOURCE,
        }

    data = ctx.shadbala
    if data is None:
        return {
            "available": False,
            "reason": ctx.shadbala_error or "Shadbala could not be calculated.",
            "status": pr.NOT_AVAILABLE,
            "sources": _SOURCE,
        }

    def at(key: str) -> Optional[float]:
        values = data.get(key)
        if not values or planet >= len(values):
            return None
        return values[planet]

    sthana_components = [
        {"name": label, "virupa": _safe(data["sthana_components"].get(key), planet)}
        for key, label in STHANA_COMPONENT_LABELS
    ]
    kala_components = [
        {"name": label, "virupa": _safe(data["kala_components"].get(key), planet)}
        for key, label in KALA_COMPONENT_LABELS
    ]

    total_virupa = at("total_virupa")
    total_rupa = at("total_rupa")
    required = data["required_rupa"][planet] if planet < len(data["required_rupa"]) else None

    return {
        "available": True,
        "planet": planet,
        "planetName": pr.planet_name(planet),

        "sthanaBala": {
            "total": at("sthana_bala"),
            "components": sthana_components,
        },
        "digBala": {"total": at("dig_bala")},
        "kalaBala": {
            "total": at("kala_bala"),
            "components": kala_components,
        },
        "cheshtaBala": {"total": at("cheshta_bala")},
        "naisargikaBala": {"total": at("naisargika_bala")},
        "drikBala": {
            "total": at("drik_bala"),
            "contributions": _drik_contributions(data, planet),
        },

        "totalVirupa": total_virupa,
        "totalRupa": total_rupa,
        "requiredRupa": required,
        "ratioToRequired": at("ratio_to_required"),

        "units": {
            "virupa": "1 Rupa = 60 Virupas",
            "note": "Values are reported exactly as PyJHora calculates them. "
                    "No qualitative label is applied.",
        },
        "sources": _SOURCE,
    }


def _safe(values, planet: int) -> Optional[float]:
    if not values or planet >= len(values):
        return None
    return values[planet]


def _drik_contributions(data: dict, planet: int) -> Optional[List[dict]]:
    """Which planets contributed what to this planet's Drik Bala.

    PyJHora's ``planet_aspect_relationship_table`` is indexed
    [aspecting][aspected] in virupas.
    """
    matrix = data.get("drik_bala_aspect_matrix")
    if not matrix:
        return None
    out: List[dict] = []
    for source, row in enumerate(matrix):
        if source == planet or planet >= len(row):
            continue
        value = row[planet]
        if value == 0:
            continue
        out.append({
            "fromPlanet": source,
            "fromPlanetName": pr.planet_name(source) if source < 9 else str(source),
            "virupa": value,
        })
    out.sort(key=lambda d: abs(d["virupa"]), reverse=True)
    return out


def shadbala_table(ctx: ChartContext) -> List[dict]:
    """Compact Shadbala row per planet, for the chart overview."""
    return [shadbala(ctx, p) for p in pr.ALL_PLANETS]
