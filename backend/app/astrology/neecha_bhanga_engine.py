"""Neecha Bhanga conditions (RULES NB_001..NB_006, NB_100) — SECTION U.

Every condition is evaluated and reported separately. Nothing is merged into a
single opaque boolean, and retrograde motion is not used as a condition.
"""
from __future__ import annotations

from typing import List, Optional

from .aspect_engine import has_mutual_drishti
from .chart_calculator import ChartContext
from .conjunction_engine import are_conjunct
from .rules import neecha_bhanga_rules as nbr
from .rules import planetary_rules as pr
from .rules.functional_classification_rules import (
    CATEGORY_KENDRA, CATEGORY_TRIKONA, house_categories,
)


def _kendra_from(ctx: ChartContext, reference_sign: int, planet: int) -> tuple:
    count = ctx.house_from(reference_sign, ctx.sign_of(planet))
    return count in nbr.KENDRA_OFFSETS_1_BASED, count


def neecha_bhanga(ctx: ChartContext, planet: int) -> dict:
    is_debilitated = (
        pr.dignity_code(planet, ctx.sign_of(planet)) == pr.DIGNITY_DEBILITATED
    )

    if not is_debilitated:
        return {
            "applicable": False,
            "status": pr.NOT_APPLICABLE,
            "isDebilitated": False,
            "reason": (
                f"{pr.planet_name(planet)} occupies "
                f"{pr.sign_name(ctx.sign_of(planet))}, which is not its "
                f"debilitation sign. Neecha Bhanga is not evaluated."
            ),
            "conditions": [],
            "conditionsSatisfied": 0,
            "neechaBhangaRajaYoga": {
                "present": False,
                "reason": "The planet is not debilitated.",
            },
            "exclusionNote": nbr.V1_EXCLUSION_NOTE,
            "sources": {"source": "Custom Rule Engine", "rule": "NB_100"},
        }

    debil_sign = ctx.sign_of(planet)
    debil_lord = ctx.lord_of_sign(debil_sign)

    exalt_signs = pr.exaltation_signs(planet)
    exalt_sign: Optional[int] = exalt_signs[0] if exalt_signs else None
    exalt_lord: Optional[int] = ctx.lord_of_sign(exalt_sign) if exalt_sign is not None else None

    moon_sign = ctx.sign_of(pr.MOON)
    conditions: List[dict] = []

    # --- Condition 1 : debilitation lord in Kendra from Lagna ---------------
    ok, count = _kendra_from(ctx, ctx.lagna_sign, debil_lord)
    conditions.append(_condition(
        1, ok,
        f"Lord of the debilitation sign {pr.sign_name(debil_sign)} is "
        f"{pr.planet_name(debil_lord)}, occupying "
        f"{pr.sign_name(ctx.sign_of(debil_lord))}, the {pr.ordinal(count)} sign from the "
        f"Lagna ({pr.sign_name(ctx.lagna_sign)}). "
        f"Kendra positions are 1, 4, 7, 10.",
        participants=[debil_lord],
    ))

    # --- Condition 2 : debilitation lord in Kendra from Moon ----------------
    ok, count = _kendra_from(ctx, moon_sign, debil_lord)
    conditions.append(_condition(
        2, ok,
        f"{pr.planet_name(debil_lord)} (lord of the debilitation sign) occupies "
        f"{pr.sign_name(ctx.sign_of(debil_lord))}, the {pr.ordinal(count)} sign from the "
        f"Moon ({pr.sign_name(moon_sign)}). Kendra positions are 1, 4, 7, 10.",
        participants=[debil_lord],
    ))

    # --- Condition 3 : exaltation lord in Kendra from Lagna -----------------
    if exalt_lord is None:
        conditions.append(_condition(
            3, None,
            "No exaltation sign is defined for this body in the selected rule "
            "set, so the condition cannot be evaluated.",
        ))
    else:
        ok, count = _kendra_from(ctx, ctx.lagna_sign, exalt_lord)
        conditions.append(_condition(
            3, ok,
            f"Lord of the exaltation sign {pr.sign_name(exalt_sign)} is "
            f"{pr.planet_name(exalt_lord)}, occupying "
            f"{pr.sign_name(ctx.sign_of(exalt_lord))}, the {pr.ordinal(count)} sign from "
            f"the Lagna ({pr.sign_name(ctx.lagna_sign)}). "
            f"Kendra positions are 1, 4, 7, 10.",
            participants=[exalt_lord],
        ))

    # --- Condition 4 : exaltation lord in Kendra from Moon ------------------
    if exalt_lord is None:
        conditions.append(_condition(
            4, None,
            "No exaltation sign is defined for this body in the selected rule set.",
        ))
    else:
        ok, count = _kendra_from(ctx, moon_sign, exalt_lord)
        conditions.append(_condition(
            4, ok,
            f"{pr.planet_name(exalt_lord)} (lord of the exaltation sign) occupies "
            f"{pr.sign_name(ctx.sign_of(exalt_lord))}, the {pr.ordinal(count)} sign from the "
            f"Moon ({pr.sign_name(moon_sign)}). Kendra positions are 1, 4, 7, 10.",
            participants=[exalt_lord],
        ))

    # --- Condition 5 : association with a cancellation lord -----------------
    triggers: List[dict] = []
    for lord, role in ((debil_lord, "lord of the debilitation sign"),
                       (exalt_lord, "lord of the exaltation sign")):
        if lord is None or lord == planet:
            continue
        if are_conjunct(ctx, planet, lord):
            triggers.append({
                "planet": lord, "planetName": pr.planet_name(lord),
                "role": role, "association": "Conjunction",
                "detail": (f"{pr.planet_name(planet)} and {pr.planet_name(lord)} "
                           f"both occupy {pr.sign_name(ctx.sign_of(lord))}."),
            })
        elif has_mutual_drishti(ctx, planet, lord):
            triggers.append({
                "planet": lord, "planetName": pr.planet_name(lord),
                "role": role, "association": "Mutual Graha Drishti",
                "detail": (f"{pr.planet_name(planet)} and {pr.planet_name(lord)} "
                           f"aspect each other by Graha Drishti."),
            })
    conditions.append(_condition(
        5, bool(triggers),
        ("; ".join(f"{t['planetName']} ({t['role']}) — {t['association']}: {t['detail']}"
                   for t in triggers))
        if triggers else
        (f"{pr.planet_name(planet)} is neither conjunct with nor in mutual Graha "
         f"Drishti with the lord of its debilitation sign "
         f"({pr.planet_name(debil_lord)})"
         + (f" or the lord of its exaltation sign ({pr.planet_name(exalt_lord)})."
            if exalt_lord is not None else ".")),
        participants=[t["planet"] for t in triggers],
        extra={"triggers": triggers},
    ))

    # --- Condition 6 : debilitation lord and exaltation lord in mutual Kendras
    if exalt_lord is None:
        conditions.append(_condition(
            6, None,
            "No exaltation sign is defined for this body in the selected rule set.",
        ))
    else:
        count = ctx.house_from(ctx.sign_of(debil_lord), ctx.sign_of(exalt_lord))
        ok = count in nbr.KENDRA_OFFSETS_1_BASED
        conditions.append(_condition(
            6, ok,
            f"{pr.planet_name(exalt_lord)} occupies "
            f"{pr.sign_name(ctx.sign_of(exalt_lord))}, the {pr.ordinal(count)} sign from "
            f"{pr.planet_name(debil_lord)} in "
            f"{pr.sign_name(ctx.sign_of(debil_lord))}. "
            f"Mutual Kendra requires 1, 4, 7 or 10.",
            participants=[debil_lord, exalt_lord],
        ))

    satisfied = sum(1 for c in conditions if c["satisfied"] is True)

    return {
        "applicable": True,
        "status": "Evaluated",
        "isDebilitated": True,
        "debilitationSign": debil_sign,
        "debilitationSignName": pr.sign_name(debil_sign),
        "debilitationLord": debil_lord,
        "debilitationLordName": pr.planet_name(debil_lord),
        "exaltationSign": exalt_sign,
        "exaltationSignName": pr.sign_name(exalt_sign) if exalt_sign is not None else pr.NOT_DEFINED,
        "exaltationLord": exalt_lord,
        "exaltationLordName": pr.planet_name(exalt_lord) if exalt_lord is not None else pr.NOT_DEFINED,
        "conditions": conditions,
        "conditionsSatisfied": satisfied,
        "neechaBhangaRajaYoga": _raja_yoga(ctx, planet, satisfied),
        "exclusionNote": nbr.V1_EXCLUSION_NOTE,
        "sources": {"source": "Custom Rule Engine", "rule": "NB_100",
                    "methodology": "Conditions NB_001..NB_006 evaluated independently"},
    }


def _condition(number: int, satisfied, evidence: str,
               participants: Optional[List[int]] = None,
               extra: Optional[dict] = None) -> dict:
    spec = nbr.CONDITION_BY_NUMBER[number]
    if satisfied is True:
        status = "Satisfied"
    elif satisfied is False:
        status = "Not satisfied"
    else:
        status = pr.NOT_DEFINED
    out = {
        "number": number,
        "ruleId": spec.rule_id,
        "title": spec.title,
        "statement": spec.statement,
        "satisfied": satisfied,
        "status": status,
        "evidence": evidence,
        "participants": [
            {"planet": p, "planetName": pr.planet_name(p)}
            for p in (participants or [])
        ],
    }
    if extra:
        out.update(extra)
    return out


def _raja_yoga(ctx: ChartContext, planet: int, satisfied: int) -> dict:
    """RULE YOGA_022. Kept distinct from plain cancellation."""
    if satisfied == 0:
        return {
            "present": False,
            "statement": nbr.NBRY_STATEMENT,
            "conditions": [
                {"title": "At least one Neecha Bhanga condition satisfied",
                 "satisfied": False,
                 "evidence": "No Neecha Bhanga condition is satisfied."},
            ],
        }

    owned = ctx.houses_owned.get(planet, [])
    owns_kendra_trikona = [
        h for h in owned
        if CATEGORY_KENDRA in house_categories(h, ctx.lagna_sign)
        or CATEGORY_TRIKONA in house_categories(h, ctx.lagna_sign)
    ]
    occupied = ctx.bhava_of(planet)
    occupies_kendra_trikona = (
        CATEGORY_KENDRA in house_categories(occupied, ctx.lagna_sign)
        or CATEGORY_TRIKONA in house_categories(occupied, ctx.lagna_sign)
    )

    placement_ok = bool(owns_kendra_trikona) or occupies_kendra_trikona

    return {
        "present": placement_ok,
        "statement": nbr.NBRY_STATEMENT,
        "conditions": [
            {"title": "At least one Neecha Bhanga condition satisfied",
             "satisfied": True,
             "evidence": f"{satisfied} of 6 conditions satisfied."},
            {"title": "Planet owns a Kendra or Trikona house",
             "satisfied": bool(owns_kendra_trikona),
             "evidence": (
                 f"{pr.planet_name(planet)} owns house(s) "
                 f"{', '.join(str(h) for h in owned)}; "
                 f"Kendra/Trikona among them: "
                 f"{', '.join(str(h) for h in owns_kendra_trikona) or 'none'}."
             ) if owned else
             f"{pr.planet_name(planet)} owns no house in this rule set."},
            {"title": "Planet occupies a Kendra or Trikona house",
             "satisfied": occupies_kendra_trikona,
             "evidence": (
                 f"{pr.planet_name(planet)} occupies house {occupied} "
                 f"({', '.join(house_categories(occupied, ctx.lagna_sign)) or 'no category'})."
             )},
        ],
    }
