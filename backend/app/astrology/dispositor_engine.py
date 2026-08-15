"""Dispositor chain with cycle detection (RULE DISPOSITOR_001) — SECTION T."""
from __future__ import annotations

from typing import List

from .chart_calculator import ChartContext
from .relationship_engine import relationship
from .rules import planetary_rules as pr

_SOURCE = {"source": "Custom Rule Engine", "rule": "DISPOSITOR_001",
           "methodology": "X occupies a sign owned by Y, therefore X -> Y"}

TERMINATION_SELF = "Self-dispositor"
TERMINATION_CYCLE = "Cycle detected"
TERMINATION_UNDEFINED = "Chain ends: dispositor not defined for this body"


def dispositor_chain(ctx: ChartContext, planet: int) -> dict:
    links: List[dict] = []
    visited: List[int] = []
    current = planet
    termination = TERMINATION_UNDEFINED
    cycle_members: List[int] = []

    while True:
        if current in visited:
            termination = TERMINATION_CYCLE
            cycle_members = visited[visited.index(current):]
            break
        visited.append(current)

        sign = ctx.sign_of(current)
        lord = ctx.lord_of_sign(sign)

        links.append({
            "planet": current,
            "planetName": pr.planet_name(current),
            "sign": sign,
            "signName": pr.sign_name(sign),
            "signLord": lord,
            "signLordName": pr.planet_name(lord),
            "isSelfDispositor": lord == current,
            "relationship": relationship(ctx, current, lord),
            "evidence": (
                f"{pr.planet_name(current)} occupies {pr.sign_name(sign)}, "
                f"which is owned by {pr.planet_name(lord)}. "
                f"Therefore {pr.planet_name(current)} → {pr.planet_name(lord)}."
            ),
        })

        if lord == current:
            termination = TERMINATION_SELF
            break
        current = lord

    return {
        "startPlanet": planet,
        "startPlanetName": pr.planet_name(planet),
        "chain": links,
        "chainText": " → ".join(pr.planet_name(l["planet"]) for l in links)
                     + (f" → {pr.planet_name(cycle_members[0])}" if cycle_members else ""),
        "termination": termination,
        "cycleDetected": termination == TERMINATION_CYCLE,
        "cycleMembers": [
            {"planet": p, "planetName": pr.planet_name(p)} for p in cycle_members
        ],
        "nodeNote": (
            "Rahu and Ketu own no sign in this rule set, so they may appear in a "
            "chain but never act as a dispositor."
        ) if planet in pr.NODES else None,
        "sources": _SOURCE,
    }
