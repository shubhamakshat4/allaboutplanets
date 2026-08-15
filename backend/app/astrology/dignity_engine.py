"""Rashi dignity facts (RULES DIGNITY_001, DIGNITY_002, VARGA_001).

Each dignity is an independent fact. Nothing here collapses into a single
"strength" statement.
"""
from __future__ import annotations

from typing import List, Optional

from .chart_calculator import ChartContext
from .rules import planetary_rules as pr


def dignity(ctx: ChartContext, planet: int) -> dict:
    """SECTION B."""
    pos = ctx.positions[planet]
    sign = pos.sign
    degree = pos.degree_in_sign

    code = pr.dignity_code(planet, sign)
    classification = pr.DIGNITY_CODE_NAMES.get(code, pr.NOT_DEFINED)

    exalt_signs = pr.exaltation_signs(planet)
    debil_signs = pr.debilitation_signs(planet)
    own = pr.owned_signs(planet)

    # Exaltation and debilitation are taken from the deep-exaltation longitudes,
    # which are unambiguous. The dignity table stores one code per cell and so
    # cannot record exaltation and own-sign together (Mercury in Virgo).
    is_exalted = sign in exalt_signs
    is_debilitated = sign in debil_signs
    is_own = sign in own

    coincident = is_exalted and is_own

    mt = _mooltrikona(planet, sign, degree)

    is_node = planet in pr.NODES

    return {
        "planet": planet,
        "planetName": pr.planet_name(planet),
        "currentRashi": sign,
        "currentRashiName": pr.sign_name(sign),
        "currentRashiLord": ctx.lord_of_sign(sign),
        "currentRashiLordName": pr.planet_name(ctx.lord_of_sign(sign)),
        "degreeInSign": round(degree, 6),
        "degreeInSignDms": pr.to_dms(degree),

        "exalted": is_exalted,
        "debilitated": is_debilitated,
        "swarashi": pr.NOT_DEFINED if is_node else is_own,
        "mooltrikona": mt["result"],
        "friendSign": code == pr.DIGNITY_FRIEND,
        "neutralSign": code == pr.DIGNITY_NEUTRAL,
        "enemySign": code == pr.DIGNITY_ENEMY,
        "signRelationship": classification,

        "exaltationSigns": [pr.sign_name(s) for s in exalt_signs],
        "debilitationSigns": [pr.sign_name(s) for s in debil_signs],
        "ownSigns": [pr.sign_name(s) for s in own] or ([pr.NOT_DEFINED] if is_node else []),
        "mooltrikonaRange": mt["range_text"],

        "deepExaltationLongitude": _deep(pr.deep_exaltation_longitude(planet)),
        "deepDebilitationLongitude": _deep(pr.deep_debilitation_longitude(planet)),

        "evidence": {
            "table": (
                "PyJHora const.house_strengths_of_planets"
                f"[{pr.planet_name(planet)}][{pr.sign_name(sign)}] = {code} "
                f"({classification})"
            ),
            "codeLegend": "5 = Own, 4 = Exalted, 3 = Friend's, 2 = Neutral, "
                          "1 = Enemy's, 0 = Debilitated",
            "exaltation": (
                f"Exaltation sign(s): "
                f"{', '.join(pr.sign_name(s) for s in exalt_signs) or pr.NOT_DEFINED}. "
                f"Debilitation sign(s): "
                f"{', '.join(pr.sign_name(s) for s in debil_signs) or pr.NOT_DEFINED}. "
                f"The planet occupies {pr.sign_name(sign)}."
                + (" Exaltation and own-sign coincide here; both are reported as "
                   "independent facts and neither is suppressed." if coincident else "")
            ),
            "mooltrikona": mt["evidence"],
            "nodeNote": (
                "Rahu and Ketu lord no sign in the lordship table used for houses, "
                "so Swarashi and Mooltrikona are not defined for them. The "
                "exaltation and debilitation signs shown come from PyJHora's "
                "dignity table and represent one tradition among several."
            ) if is_node else None,
        },
        "sources": {
            "dignity": {"source": "PyJHora", "rule": "DIGNITY_001",
                        "methodology": "const.house_strengths_of_planets"},
            "mooltrikona": {"source": "PyJHora", "rule": "DIGNITY_002",
                            "methodology": "const.moola_trikona_range_of_planets"},
        },
    }


def _mooltrikona(planet: int, sign: int, degree: float) -> dict:
    rng = pr.mooltrikona_range(planet)
    if rng is None:
        return {
            "result": pr.NOT_DEFINED,
            "range_text": pr.NOT_DEFINED,
            "evidence": (
                "Mooltrikona is not defined for this body in the selected rule "
                "set (PyJHora const.moola_trikona_range_of_planets covers "
                "Sun to Saturn only)."
            ),
        }
    mt_sign, start, end = rng
    range_text = f"{pr.sign_name(mt_sign)} {start:g}°–{end:g}°"
    in_sign = sign == mt_sign
    in_range = in_sign and start <= degree < end
    if not in_sign:
        evidence = (f"Mooltrikona range is {range_text}. The planet occupies "
                    f"{pr.sign_name(sign)}, so the condition fails on the sign.")
    elif not in_range:
        evidence = (f"Mooltrikona range is {range_text}. The planet occupies "
                    f"{pr.sign_name(sign)} at {pr.to_dms(degree)}, outside the range.")
    else:
        evidence = (f"Mooltrikona range is {range_text}. The planet occupies "
                    f"{pr.sign_name(sign)} at {pr.to_dms(degree)}, inside the range.")
    return {"result": in_range, "range_text": range_text, "evidence": evidence}


def _deep(value: Optional[float]) -> Optional[dict]:
    if value is None:
        return None
    sign = int(value // 30) % 12
    return {
        "absoluteLongitude": round(value, 4),
        "sign": sign,
        "signName": pr.sign_name(sign),
        "degreeInSign": round(value % 30.0, 4),
        "degreeInSignDms": pr.to_dms(value % 30.0),
    }


def vargottama(ctx: ChartContext, planet: int) -> dict:
    """RULE VARGA_001 — SECTION H."""
    d1 = ctx.varga_sign(planet, 1)
    d9 = ctx.varga_sign(planet, 9)
    if d1 is None or d9 is None:
        return {
            "isVargottama": pr.NOT_AVAILABLE,
            "evidence": "D1 or D9 position unavailable.",
            "sources": {"source": "Custom Rule Engine", "rule": "VARGA_001"},
        }
    result = d1 == d9
    return {
        "isVargottama": result,
        "d1Sign": d1,
        "d1SignName": pr.sign_name(d1),
        "d9Sign": d9,
        "d9SignName": pr.sign_name(d9),
        "evidence": (
            f"D1 Rashi = {pr.sign_name(d1)}; D9 Rashi = {pr.sign_name(d9)}; "
            f"therefore Vargottama = {'Yes' if result else 'No'}"
        ),
        "sources": {"source": "Custom Rule Engine", "rule": "VARGA_001",
                    "methodology": "D1 Rashi equals D9 Rashi"},
    }


def dignity_in_sign(planet: int, sign: int) -> str:
    """Dignity classification of a planet in an arbitrary sign (used by vargas)."""
    return pr.DIGNITY_CODE_NAMES.get(pr.dignity_code(planet, sign), pr.NOT_DEFINED)


def natural_benefic_classification(ctx: ChartContext) -> dict:
    """RULE BENEFIC_001 — evaluated once per chart and reused by every yoga."""
    result = {}
    malefics = {pr.SUN, pr.MARS, pr.SATURN, pr.RAHU, pr.KETU}

    for planet in pr.ALL_PLANETS:
        if planet in (pr.JUPITER, pr.VENUS):
            result[planet] = {
                "benefic": True,
                "reason": f"{pr.planet_name(planet)} is an unconditional natural benefic.",
            }
        elif planet == pr.MERCURY:
            companions = [p for p in ctx.planets_in_sign[ctx.sign_of(pr.MERCURY)]
                          if p != pr.MERCURY]
            afflicting = [p for p in companions if p in malefics]
            result[planet] = {
                "benefic": not afflicting,
                "reason": (
                    "Mercury shares "
                    f"{pr.sign_name(ctx.sign_of(pr.MERCURY))} with "
                    + ", ".join(pr.planet_name(p) for p in afflicting)
                    + " (natural malefics), so it is classified malefic."
                ) if afflicting else (
                    "Mercury shares its sign with no natural malefic, so it is "
                    "classified benefic."
                ),
            }
        elif planet == pr.MOON:
            elong = (ctx.positions[pr.MOON].absolute_longitude
                     - ctx.positions[pr.SUN].absolute_longitude) % 360.0
            waxing = 72.0 <= elong <= 288.0
            result[planet] = {
                "benefic": waxing,
                "reason": (
                    f"Moon's elongation from the Sun is {pr.to_dms(elong)}. "
                    f"The rule treats 72°–288° as benefic (bright); "
                    f"result: {'benefic' if waxing else 'malefic'}."
                ),
            }
        else:
            result[planet] = {
                "benefic": False,
                "reason": f"{pr.planet_name(planet)} is a natural malefic.",
            }
        result[planet]["planet"] = planet
        result[planet]["planetName"] = pr.planet_name(planet)
        result[planet]["rule"] = "BENEFIC_001"
    return result
