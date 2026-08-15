"""The curated V1 yoga engine (RULES YOGA_001 .. YOGA_022) — SECTIONS V, 10, 11.

Every yoga returns its participants, its individual conditions and the evidence
behind each condition. Nothing here says whether a yoga is desirable.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from .aspect_engine import has_mutual_drishti
from .chart_calculator import ChartContext
from .conjunction_engine import are_conjunct, separation
from .dignity_engine import natural_benefic_classification
from .neecha_bhanga_engine import neecha_bhanga
from .relationship_engine import relationship
from .rules import planetary_rules as pr
from .rules import yoga_rules as yr
from .rules.functional_classification_rules import (
    CATEGORY_KENDRA, CATEGORY_TRIKONA, house_categories,
)

PRESENT = "Present"
NOT_PRESENT = "Not Present"


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
def _condition(title: str, satisfied, evidence: str,
               group: Optional[str] = None) -> dict:
    out = {
        "title": title,
        "satisfied": satisfied,
        "status": ("Satisfied" if satisfied is True
                   else "Not satisfied" if satisfied is False
                   else pr.NOT_DEFINED),
        "evidence": evidence,
    }
    if group:
        out["group"] = group
    return out


def _participant(ctx: ChartContext, planet: int, role: str) -> dict:
    return {
        "planet": planet,
        "planetName": pr.planet_name(planet),
        "role": role,
        "sign": ctx.sign_of(planet),
        "signName": pr.sign_name(ctx.sign_of(planet)),
        "bhava": ctx.bhava_of(planet),
        "housesOwned": ctx.houses_owned.get(planet, []),
    }


def _parivartana(ctx: ChartContext, a: int, b: int) -> bool:
    """A occupies a sign owned by B and B occupies a sign owned by A."""
    if a == b:
        return False
    return (ctx.lord_of_sign(ctx.sign_of(a)) == b
            and ctx.lord_of_sign(ctx.sign_of(b)) == a)


def _association(ctx: ChartContext, a: int, b: int) -> Optional[dict]:
    """Conjunction, mutual Graha Drishti, or sign exchange — with evidence."""
    if a == b:
        return None
    if are_conjunct(ctx, a, b):
        sep = separation(ctx.positions[a].absolute_longitude,
                         ctx.positions[b].absolute_longitude)
        return {
            "type": yr.ASSOC_CONJUNCTION,
            "evidence": (
                f"{pr.planet_name(a)} and {pr.planet_name(b)} both occupy "
                f"{pr.sign_name(ctx.sign_of(a))}. Separation = {pr.to_dms(sep)}."
            ),
            "separation": round(sep, 6),
            "separationDms": pr.to_dms(sep),
        }
    if has_mutual_drishti(ctx, a, b):
        ord_ab = ctx.house_from(ctx.sign_of(a), ctx.sign_of(b))
        ord_ba = ctx.house_from(ctx.sign_of(b), ctx.sign_of(a))
        return {
            "type": yr.ASSOC_MUTUAL_DRISHTI,
            "evidence": (
                f"{pr.planet_name(a)} in {pr.sign_name(ctx.sign_of(a))} casts its "
                f"{pr.ordinal(ord_ab)} Drishti on {pr.planet_name(b)}; "
                f"{pr.planet_name(b)} in {pr.sign_name(ctx.sign_of(b))} casts its "
                f"{pr.ordinal(ord_ba)} Drishti on {pr.planet_name(a)}."
            ),
            "aspectAtoB": ord_ab,
            "aspectBtoA": ord_ba,
        }
    if _parivartana(ctx, a, b):
        return {
            "type": yr.ASSOC_PARIVARTANA,
            "evidence": (
                f"{pr.planet_name(a)} occupies {pr.sign_name(ctx.sign_of(a))} "
                f"(owned by {pr.planet_name(b)}) while {pr.planet_name(b)} occupies "
                f"{pr.sign_name(ctx.sign_of(b))} (owned by {pr.planet_name(a)})."
            ),
        }
    return None


def _yoga(spec_key: str, present: bool, participants: List[dict],
          conditions: List[dict], association_type: Optional[str] = None,
          evidence: Optional[str] = None, extra: Optional[dict] = None,
          instances: Optional[List[dict]] = None,
          applicable: bool = True) -> dict:
    spec = yr.YOGA_SPEC_BY_KEY[spec_key]
    out = {
        "key": spec.key,
        "name": spec.name,
        "ruleId": spec.rule_id,
        "summary": spec.summary,
        "present": present,
        "status": (PRESENT if present else NOT_PRESENT) if applicable else pr.NOT_APPLICABLE,
        "participants": participants,
        "conditions": conditions,
        "associationType": association_type,
        "evidence": evidence,
        "instances": instances or [],
        "sources": {"source": "Custom Rule Engine", "rule": spec.rule_id,
                    "methodology": spec.summary},
    }
    if extra:
        out.update(extra)
    return out


# ---------------------------------------------------------------------------
# YOGA_001 Raja Yoga
# ---------------------------------------------------------------------------
def _raja_yoga(ctx: ChartContext) -> dict:
    kendra_lords = {ctx.house_lord[h] for h in (1, 4, 7, 10)}
    trikona_lords = {ctx.house_lord[h] for h in (1, 5, 9)}

    instances: List[dict] = []
    seen = set()
    for kl in sorted(kendra_lords):
        for tl in sorted(trikona_lords):
            if kl == tl:
                continue
            pair = tuple(sorted((kl, tl)))
            if pair in seen:
                continue
            assoc = _association(ctx, kl, tl)
            if not assoc:
                continue
            seen.add(pair)
            kendra_houses = [h for h in (1, 4, 7, 10) if ctx.house_lord[h] == kl]
            trikona_houses = [h for h in (1, 5, 9) if ctx.house_lord[h] == tl]
            instances.append({
                "kendraLord": kl,
                "kendraLordName": pr.planet_name(kl),
                "kendraHousesOwned": kendra_houses,
                "trikonaLord": tl,
                "trikonaLordName": pr.planet_name(tl),
                "trikonaHousesOwned": trikona_houses,
                "associationType": assoc["type"],
                "associationEvidence": assoc["evidence"],
                "separationDms": assoc.get("separationDms"),
                "aspectAtoB": assoc.get("aspectAtoB"),
                "aspectBtoA": assoc.get("aspectBtoA"),
                "kendraLordPosition": {
                    "sign": pr.sign_name(ctx.sign_of(kl)),
                    "degree": pr.to_dms(ctx.positions[kl].degree_in_sign),
                    "bhava": ctx.bhava_of(kl),
                },
                "trikonaLordPosition": {
                    "sign": pr.sign_name(ctx.sign_of(tl)),
                    "degree": pr.to_dms(ctx.positions[tl].degree_in_sign),
                    "bhava": ctx.bhava_of(tl),
                },
                "relationship": relationship(ctx, kl, tl),
                "participants": [kl, tl],
            })

    participants: List[dict] = []
    for inst in instances:
        for p, role in ((inst["kendraLord"], "Kendra Lord"),
                        (inst["trikonaLord"], "Trikona Lord")):
            if not any(x["planet"] == p and x["role"] == role for x in participants):
                participants.append(_participant(ctx, p, role))

    conditions = [_condition(
        "A Kendra lord and a Trikona lord associate",
        bool(instances),
        f"Kendra lords: {_names(kendra_lords)}. Trikona lords: {_names(trikona_lords)}. "
        + (f"{len(instances)} qualifying association(s) found."
           if instances else "No qualifying association found."),
    )]

    return _yoga("raja_yoga", bool(instances), participants, conditions,
                 association_type=instances[0]["associationType"] if instances else None,
                 instances=instances,
                 extra={"note": "The Lagna lord qualifies as both a Kendra lord "
                                "and a Trikona lord, since the 1st house is both."})


# ---------------------------------------------------------------------------
# YOGA_002 Dharma-Karmadhipati
# ---------------------------------------------------------------------------
def _dharma_karmadhipati(ctx: ChartContext) -> dict:
    l9 = ctx.house_lord[9]
    l10 = ctx.house_lord[10]

    if l9 == l10:
        conditions = [_condition(
            "9th lord and 10th lord associate", False,
            f"The 9th and 10th houses share a single lord ({pr.planet_name(l9)}), "
            f"so no association between two planets exists.",
        )]
        return _yoga("dharma_karmadhipati", False,
                     [_participant(ctx, l9, "9th and 10th Lord")], conditions)

    assoc = _association(ctx, l9, l10)
    conditions = [_condition(
        "9th lord and 10th lord associate by conjunction, mutual Graha Drishti "
        "or sign exchange",
        bool(assoc),
        assoc["evidence"] if assoc else
        (f"{pr.planet_name(l9)} (9th lord) in {pr.sign_name(ctx.sign_of(l9))} and "
         f"{pr.planet_name(l10)} (10th lord) in {pr.sign_name(ctx.sign_of(l10))} "
         f"form no qualifying association."),
    )]

    return _yoga("dharma_karmadhipati", bool(assoc),
                 [_participant(ctx, l9, "9th Lord"), _participant(ctx, l10, "10th Lord")],
                 conditions,
                 association_type=assoc["type"] if assoc else None,
                 evidence=assoc["evidence"] if assoc else None,
                 extra={"relationship": relationship(ctx, l9, l10)})


# ---------------------------------------------------------------------------
# YOGA_003..007 Panchamahapurusha
# ---------------------------------------------------------------------------
def _mahapurusha(ctx: ChartContext, key: str) -> dict:
    cfg = yr.MAHAPURUSHA[key]
    planet, signs = cfg["planet"], cfg["signs"]
    sign = ctx.sign_of(planet)
    bhava = ctx.bhava_of(planet)

    in_sign = sign in signs
    in_kendra = bhava in pr.KENDRA_HOUSES

    conditions = [
        _condition(
            f"{pr.planet_name(planet)} occupies "
            f"{', '.join(pr.sign_name(s) for s in signs)}",
            in_sign,
            f"{pr.planet_name(planet)} occupies {pr.sign_name(sign)}.",
        ),
        _condition(
            f"{pr.planet_name(planet)} occupies a Kendra (1, 4, 7, 10) from the Lagna",
            in_kendra,
            f"{pr.planet_name(planet)} occupies house {bhava} counted from the "
            f"Lagna ({pr.sign_name(ctx.lagna_sign)}).",
        ),
    ]
    present = in_sign and in_kendra
    return _yoga(key, present, [_participant(ctx, planet, "Primary")], conditions,
                 evidence=(f"{pr.planet_name(planet)}: "
                           f"{pr.sign_name(sign)}, house {bhava}."))


# ---------------------------------------------------------------------------
# YOGA_008 Gaja Kesari
# ---------------------------------------------------------------------------
def _gaja_kesari(ctx: ChartContext, benefics: dict) -> dict:
    jup = pr.JUPITER
    jup_sign = ctx.sign_of(jup)
    from_lagna = ctx.house_from(ctx.lagna_sign, jup_sign)
    from_moon = ctx.house_from(ctx.sign_of(pr.MOON), jup_sign)

    c1 = from_lagna in pr.KENDRA_HOUSES or from_moon in pr.KENDRA_HOUSES

    # Condition 2 — qualifying benefic association
    assoc_details: List[dict] = []
    for other in pr.ALL_PLANETS:
        if other == jup or not benefics[other]["benefic"]:
            continue
        assoc = _association(ctx, jup, other)
        if assoc and assoc["type"] in (yr.ASSOC_CONJUNCTION, yr.ASSOC_MUTUAL_DRISHTI):
            assoc_details.append({
                "planet": other, "planetName": pr.planet_name(other),
                "association": assoc["type"], "evidence": assoc["evidence"],
                "beneficReason": benefics[other]["reason"],
            })
    c2 = bool(assoc_details)

    code = pr.dignity_code(jup, jup_sign)
    c3 = code != pr.DIGNITY_DEBILITATED
    c4 = not ctx.is_combust(jup)
    c5 = code != pr.DIGNITY_ENEMY

    conditions = [
        _condition("Jupiter occupies a Kendra from the Lagna or from the Moon", c1,
                   f"Jupiter occupies {pr.sign_name(jup_sign)}: the "
                   f"{pr.ordinal(from_lagna)} sign from the Lagna and the "
                   f"{pr.ordinal(from_moon)} sign from the Moon. "
                   f"Kendra positions are 1, 4, 7, 10.",
                   group=yr.GROUP_CORE),
        _condition("Jupiter has a qualifying natural-benefic association "
                   "(conjunction or mutual Graha Drishti)", c2,
                   "; ".join(f"{d['planetName']} — {d['association']}: {d['evidence']}"
                             for d in assoc_details)
                   if assoc_details else
                   "Jupiter forms no conjunction or mutual Graha Drishti with a "
                   "natural benefic (rule BENEFIC_001).",
                   group=yr.GROUP_STRENGTHENING),
        _condition("Jupiter is not debilitated", c3,
                   f"Jupiter in {pr.sign_name(jup_sign)} is classified "
                   f"'{pr.DIGNITY_CODE_NAMES.get(code)}'.",
                   group=yr.GROUP_STRENGTHENING),
        _condition("Jupiter is not combust", c4,
                   f"PyJHora combustion status for Jupiter: "
                   f"{'combust' if ctx.is_combust(jup) else 'not combust'}.",
                   group=yr.GROUP_STRENGTHENING),
        _condition("Jupiter does not occupy an enemy's sign", c5,
                   f"Jupiter in {pr.sign_name(jup_sign)} is classified "
                   f"'{pr.DIGNITY_CODE_NAMES.get(code)}'. "
                   f"Sources differ on whether this governs the formation of the "
                   f"yoga or only the extent of its results.",
                   group=yr.GROUP_STRENGTHENING),
    ]

    # The core formation alone determines the status. The strengthening
    # conditions are reported beside it so neither reading is hidden.
    strengthening = (c2, c3, c4, c5)
    present = c1
    participants = [_participant(ctx, jup, "Primary")]
    for d in assoc_details:
        participants.append(_participant(ctx, d["planet"], "Benefic association"))

    return _yoga("gaja_kesari", present, participants, conditions,
                 extra={"note": yr.GAJA_KESARI_NOTE,
                        "coreFormation": c1,
                        "strengtheningConditionsSatisfied": sum(1 for x in strengthening if x),
                        "strengtheningConditionsTotal": len(strengthening),
                        "allConditionsSatisfied": c1 and all(strengthening),
                        "beneficAssociations": assoc_details})


# ---------------------------------------------------------------------------
# YOGA_009/010/011 same-Rashi pairs
# ---------------------------------------------------------------------------
def _same_rashi_pair(ctx: ChartContext, key: str, a: int, b: int,
                     extra_facts: Optional[dict] = None) -> dict:
    same = ctx.sign_of(a) == ctx.sign_of(b)
    sep = separation(ctx.positions[a].absolute_longitude,
                     ctx.positions[b].absolute_longitude)

    conditions = [_condition(
        f"{pr.planet_name(a)} and {pr.planet_name(b)} occupy the same Rashi",
        same,
        f"{pr.planet_name(a)} occupies {pr.sign_name(ctx.sign_of(a))}; "
        f"{pr.planet_name(b)} occupies {pr.sign_name(ctx.sign_of(b))}.",
    )]

    extra = {
        "rashi": pr.sign_name(ctx.sign_of(a)) if same else None,
        "degreeA": pr.to_dms(ctx.positions[a].degree_in_sign),
        "degreeB": pr.to_dms(ctx.positions[b].degree_in_sign),
        "separationDms": pr.to_dms(sep) if same else None,
        "relationship": relationship(ctx, a, b),
    }
    if extra_facts:
        extra.update(extra_facts)

    return _yoga(key, same,
                 [_participant(ctx, a, "Participant"), _participant(ctx, b, "Participant")],
                 conditions, extra=extra)


# ---------------------------------------------------------------------------
# YOGA_012 Adhi
# ---------------------------------------------------------------------------
def _adhi(ctx: ChartContext, benefics: dict) -> dict:
    moon_sign = ctx.sign_of(pr.MOON)
    positions: List[dict] = []
    found_benefics: List[int] = []

    for offset in yr.ADHI_HOUSES_FROM_MOON:
        sign = (moon_sign + offset - 1) % 12
        occupants = ctx.planets_in_sign.get(sign, [])
        entries = []
        for p in occupants:
            is_benefic = benefics[p]["benefic"]
            entries.append({
                "planet": p, "planetName": pr.planet_name(p),
                "benefic": is_benefic, "reason": benefics[p]["reason"],
            })
            if is_benefic:
                found_benefics.append(p)
        positions.append({
            "houseFromMoon": offset,
            "sign": sign,
            "signName": pr.sign_name(sign),
            "occupants": entries,
        })

    present = bool(found_benefics)
    conditions = [_condition(
        "A natural benefic occupies the 6th, 7th or 8th sign from the Moon",
        present,
        "; ".join(
            f"{pr.ordinal(p['houseFromMoon'])} from Moon = {p['signName']}: "
            + (", ".join(f"{o['planetName']} ({'benefic' if o['benefic'] else 'malefic'})"
                         for o in p["occupants"]) or "empty")
            for p in positions
        ),
    )]

    return _yoga("adhi", present,
                 [_participant(ctx, p, "Benefic") for p in sorted(set(found_benefics))],
                 conditions,
                 extra={"moonSign": pr.sign_name(moon_sign), "positions": positions})


# ---------------------------------------------------------------------------
# YOGA_013 Amala
# ---------------------------------------------------------------------------
def _amala(ctx: ChartContext, benefics: dict) -> dict:
    references = [
        ("Lagna", ctx.lagna_sign),
        ("Moon", ctx.sign_of(pr.MOON)),
    ]
    found: List[dict] = []
    details: List[dict] = []

    for label, ref_sign in references:
        tenth = (ref_sign + 9) % 12
        occupants = ctx.planets_in_sign.get(tenth, [])
        entries = [{
            "planet": p, "planetName": pr.planet_name(p),
            "benefic": benefics[p]["benefic"], "reason": benefics[p]["reason"],
        } for p in occupants]
        details.append({
            "referencePoint": label,
            "referenceSign": pr.sign_name(ref_sign),
            "tenthSign": pr.sign_name(tenth),
            "occupants": entries,
        })
        for e in entries:
            if e["benefic"]:
                found.append({"referencePoint": label, **e})

    present = bool(found)
    conditions = [_condition(
        "A natural benefic occupies the 10th from the Lagna or the 10th from the Moon",
        present,
        "; ".join(
            f"10th from {d['referencePoint']} = {d['tenthSign']}: "
            + (", ".join(f"{o['planetName']} ({'benefic' if o['benefic'] else 'malefic'})"
                         for o in d["occupants"]) or "empty")
            for d in details
        ),
    )]

    return _yoga("amala", present,
                 [_participant(ctx, f["planet"], f"Benefic in 10th from {f['referencePoint']}")
                  for f in found],
                 conditions, extra={"referencePoints": details})


# ---------------------------------------------------------------------------
# YOGA_014/015/016 Viparita family
# ---------------------------------------------------------------------------
def _viparita(ctx: ChartContext, key: str) -> dict:
    owned_house = yr.VIPARITA_YOGAS[key]
    lord = ctx.house_lord[owned_house]
    placed = ctx.bhava_of(lord)
    present = placed in yr.VIPARITA_TARGET_HOUSES

    conditions = [_condition(
        f"The {pr.ordinal(owned_house)} lord occupies the 6th, 8th or 12th house",
        present,
        f"The {pr.ordinal(owned_house)} house is {pr.sign_name(ctx.house_sign[owned_house])}, "
        f"lorded by {pr.planet_name(lord)}. {pr.planet_name(lord)} occupies "
        f"{pr.sign_name(ctx.sign_of(lord))}, which is house {placed}.",
    )]

    return _yoga(key, present, [_participant(ctx, lord, f"{pr.ordinal(owned_house)} Lord")],
                 conditions,
                 extra={"lordOfHouse": owned_house, "lordPlacedInHouse": placed})


# ---------------------------------------------------------------------------
# YOGA_017 Dhana
# ---------------------------------------------------------------------------
def _dhana(ctx: ChartContext) -> dict:
    lords: Dict[int, List[int]] = {}
    for h in yr.DHANA_HOUSES:
        lords.setdefault(ctx.house_lord[h], []).append(h)

    instances: List[dict] = []
    planets = sorted(lords)
    for i, a in enumerate(planets):
        for b in planets[i + 1:]:
            assoc = _association(ctx, a, b)
            if not assoc:
                continue
            houses = sorted(set(lords[a]) | set(lords[b]))
            if not any(h in yr.DHANA_REQUIRED_HOUSES for h in houses):
                continue
            instances.append({
                "participants": [a, b],
                "participantNames": [pr.planet_name(a), pr.planet_name(b)],
                "housesOwned": {pr.planet_name(a): lords[a], pr.planet_name(b): lords[b]},
                "associationType": assoc["type"],
                "associationEvidence": assoc["evidence"],
                "relationship": relationship(ctx, a, b),
            })

    present = bool(instances)
    participants: List[dict] = []
    for inst in instances:
        for p in inst["participants"]:
            if not any(x["planet"] == p for x in participants):
                roles = ", ".join(f"{pr.ordinal(h)} Lord" for h in lords[p])
                participants.append(_participant(ctx, p, roles))

    conditions = [
        _condition(
            "Two or more lords of the 2nd, 5th, 9th and 11th houses associate",
            bool(instances),
            "Lords — "
            + "; ".join(f"{pr.planet_name(p)}: houses {lords[p]}" for p in planets)
            + (f". {len(instances)} qualifying association(s)."
               if instances else ". No qualifying association."),
        ),
        _condition(
            "At least one participant is the 2nd lord or the 11th lord",
            bool(instances),
            f"2nd lord = {pr.planet_name(ctx.house_lord[2])}, "
            f"11th lord = {pr.planet_name(ctx.house_lord[11])}.",
        ),
    ]

    return _yoga("dhana", present, participants, conditions, instances=instances)


# ---------------------------------------------------------------------------
# YOGA_018 Lakshmi
# ---------------------------------------------------------------------------
def _lakshmi(ctx: ChartContext) -> dict:
    l1 = ctx.house_lord[1]
    l9 = ctx.house_lord[9]

    kendra_trikona = set(pr.KENDRA_HOUSES) | set(pr.TRIKONA_HOUSES)

    c1 = ctx.bhava_of(l1) in kendra_trikona
    c2 = ctx.bhava_of(l9) in kendra_trikona

    code9 = pr.dignity_code(l9, ctx.sign_of(l9))
    mt = pr.mooltrikona_range(l9)
    in_mt = bool(mt and ctx.sign_of(l9) == mt[0]
                 and mt[1] <= ctx.positions[l9].degree_in_sign < mt[2])
    c3 = code9 in (pr.DIGNITY_OWN, pr.DIGNITY_EXALTED) or in_mt

    conditions = [
        _condition("The Lagna lord occupies a Kendra or Trikona house", c1,
                   f"Lagna lord {pr.planet_name(l1)} occupies house "
                   f"{ctx.bhava_of(l1)} ({pr.sign_name(ctx.sign_of(l1))})."),
        _condition("The 9th lord occupies a Kendra or Trikona house", c2,
                   f"9th lord {pr.planet_name(l9)} occupies house "
                   f"{ctx.bhava_of(l9)} ({pr.sign_name(ctx.sign_of(l9))})."),
        _condition("The 9th lord occupies its own, Mooltrikona or exaltation sign", c3,
                   f"9th lord {pr.planet_name(l9)} in {pr.sign_name(ctx.sign_of(l9))} "
                   f"is classified '{pr.DIGNITY_CODE_NAMES.get(code9)}'"
                   + (f"; Mooltrikona range "
                      f"{pr.sign_name(mt[0])} {mt[1]:g}°–{mt[2]:g}°, "
                      f"planet at {pr.to_dms(ctx.positions[l9].degree_in_sign)} → "
                      f"{'inside' if in_mt else 'outside'}."
                      if mt else "; Mooltrikona not defined for this body.")),
    ]

    present = c1 and c2 and c3
    return _yoga("lakshmi", present,
                 [_participant(ctx, l1, "Lagna Lord"), _participant(ctx, l9, "9th Lord")],
                 conditions)


# ---------------------------------------------------------------------------
# YOGA_019 Saraswati
# ---------------------------------------------------------------------------
def _saraswati(ctx: ChartContext) -> dict:
    conditions: List[dict] = []
    placements: List[dict] = []
    all_placed = True

    for planet in yr.SARASWATI_PLANETS:
        bhava = ctx.bhava_of(planet)
        ok = bhava in yr.SARASWATI_ALLOWED_HOUSES
        all_placed = all_placed and ok
        placements.append({
            "planet": planet, "planetName": pr.planet_name(planet),
            "sign": pr.sign_name(ctx.sign_of(planet)),
            "bhava": bhava,
            "degree": pr.to_dms(ctx.positions[planet].degree_in_sign),
            "qualifies": ok,
        })
        conditions.append(_condition(
            f"{pr.planet_name(planet)} occupies the 2nd house, a Kendra or a Trikona",
            ok,
            f"{pr.planet_name(planet)} occupies house {bhava} "
            f"({pr.sign_name(ctx.sign_of(planet))}). Qualifying houses: "
            f"{', '.join(str(h) for h in yr.SARASWATI_ALLOWED_HOUSES)}.",
        ))

    jup = pr.JUPITER
    code = pr.dignity_code(jup, ctx.sign_of(jup))
    mt = pr.mooltrikona_range(jup)
    in_mt = bool(mt and ctx.sign_of(jup) == mt[0]
                 and mt[1] <= ctx.positions[jup].degree_in_sign < mt[2])
    jup_ok = code in (pr.DIGNITY_OWN, pr.DIGNITY_EXALTED, pr.DIGNITY_FRIEND) or in_mt
    conditions.append(_condition(
        "Jupiter occupies its own, Mooltrikona, exaltation or a friend's sign",
        jup_ok,
        f"Jupiter in {pr.sign_name(ctx.sign_of(jup))} is classified "
        f"'{pr.DIGNITY_CODE_NAMES.get(code)}'"
        + (f"; Mooltrikona {pr.sign_name(mt[0])} {mt[1]:g}°–{mt[2]:g}° → "
           f"{'inside' if in_mt else 'outside'}." if mt else "."),
    ))

    present = all_placed and jup_ok
    return _yoga("saraswati", present,
                 [_participant(ctx, p, "Participant") for p in yr.SARASWATI_PLANETS],
                 conditions, extra={"placements": placements})


# ---------------------------------------------------------------------------
# YOGA_020 Kemadruma
# ---------------------------------------------------------------------------
def _kemadruma(ctx: ChartContext) -> dict:
    moon_sign = ctx.sign_of(pr.MOON)
    second = (moon_sign + 1) % 12
    twelfth = (moon_sign - 1) % 12

    def occupancy(sign: int) -> dict:
        occupants = [p for p in ctx.planets_in_sign.get(sign, []) if p != pr.MOON]
        qualifying = [p for p in occupants if p not in yr.KEMADRUMA_EXCLUDED_PLANETS]
        return {
            "sign": sign,
            "signName": pr.sign_name(sign),
            "occupants": [{"planet": p, "planetName": pr.planet_name(p),
                           "qualifies": p not in yr.KEMADRUMA_EXCLUDED_PLANETS}
                          for p in occupants],
            "qualifyingPlanets": qualifying,
        }

    second_occ = occupancy(second)
    twelfth_occ = occupancy(twelfth)

    present = not second_occ["qualifyingPlanets"] and not twelfth_occ["qualifyingPlanets"]

    conditions = [
        _condition("No qualifying planet occupies the 2nd sign from the Moon",
                   not second_occ["qualifyingPlanets"],
                   f"2nd from Moon = {second_occ['signName']}: "
                   + (", ".join(o["planetName"] for o in second_occ["occupants"]) or "empty")),
        _condition("No qualifying planet occupies the 12th sign from the Moon",
                   not twelfth_occ["qualifyingPlanets"],
                   f"12th from Moon = {twelfth_occ['signName']}: "
                   + (", ".join(o["planetName"] for o in twelfth_occ["occupants"]) or "empty")),
    ]

    return _yoga("kemadruma", present,
                 [_participant(ctx, pr.MOON, "Reference")], conditions,
                 extra={"moonSign": pr.sign_name(moon_sign),
                        "secondFromMoon": second_occ,
                        "twelfthFromMoon": twelfth_occ,
                        "exclusionNote": yr.KEMADRUMA_NOTE})


# ---------------------------------------------------------------------------
# YOGA_021 Parivartana
# ---------------------------------------------------------------------------
def _parivartana_yoga(ctx: ChartContext) -> dict:
    instances: List[dict] = []
    for i, a in enumerate(pr.ALL_PLANETS):
        for b in pr.ALL_PLANETS[i + 1:]:
            if not _parivartana(ctx, a, b):
                continue
            instances.append({
                "planetA": a, "planetAName": pr.planet_name(a),
                "planetB": b, "planetBName": pr.planet_name(b),
                "signA": pr.sign_name(ctx.sign_of(a)),
                "signB": pr.sign_name(ctx.sign_of(b)),
                "signAOwnedBy": pr.planet_name(b),
                "signBOwnedBy": pr.planet_name(a),
                "housesOwnedA": ctx.houses_owned.get(a, []),
                "housesOwnedB": ctx.houses_owned.get(b, []),
                "exchange": True,
                "relationship": relationship(ctx, a, b),
                "evidence": (
                    f"{pr.planet_name(a)} occupies {pr.sign_name(ctx.sign_of(a))} "
                    f"(owned by {pr.planet_name(b)}); {pr.planet_name(b)} occupies "
                    f"{pr.sign_name(ctx.sign_of(b))} (owned by {pr.planet_name(a)})."
                ),
                "participants": [a, b],
            })

    participants: List[dict] = []
    for inst in instances:
        for p in inst["participants"]:
            if not any(x["planet"] == p for x in participants):
                participants.append(_participant(ctx, p, "Exchange participant"))

    conditions = [_condition(
        "Two planets occupy each other's owned signs",
        bool(instances),
        f"{len(instances)} exchange(s) found." if instances
        else "No sign exchange found.",
    )]

    return _yoga("parivartana", bool(instances), participants, conditions,
                 instances=instances,
                 extra={"note": "Maha / Khala / Dainya subclassification is not "
                                "applied in V1."})


# ---------------------------------------------------------------------------
# YOGA_022 Neecha Bhanga Raja Yoga
# ---------------------------------------------------------------------------
def _neecha_bhanga_raja_yoga(ctx: ChartContext) -> dict:
    instances: List[dict] = []
    for planet in pr.ALL_PLANETS:
        nb = neecha_bhanga(ctx, planet)
        if not nb["applicable"]:
            continue
        nbry = nb["neechaBhangaRajaYoga"]
        instances.append({
            "planet": planet,
            "planetName": pr.planet_name(planet),
            "debilitationSign": nb["debilitationSignName"],
            "conditionsSatisfied": nb["conditionsSatisfied"],
            "present": nbry["present"],
            "conditions": nbry["conditions"],
            "neechaBhangaConditions": nb["conditions"],
            "participants": [planet],
        })

    present = any(i["present"] for i in instances)
    conditions = [_condition(
        "A debilitated planet satisfies at least one Neecha Bhanga condition and "
        "owns or occupies a Kendra or Trikona",
        present,
        "; ".join(
            f"{i['planetName']} debilitated in {i['debilitationSign']}: "
            f"{i['conditionsSatisfied']} condition(s) satisfied, "
            f"Raja Yoga {'present' if i['present'] else 'not present'}"
            for i in instances
        ) if instances else "No planet is debilitated in this chart.",
    )]

    return _yoga("neecha_bhanga_raja_yoga", present,
                 [_participant(ctx, i["planet"], "Debilitated planet")
                  for i in instances if i["present"]],
                 conditions, instances=instances,
                 applicable=bool(instances))


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------
def evaluate_all_yogas(ctx: ChartContext) -> List[dict]:
    """All 22 V1 yoga checks, in the order given by the specification."""
    benefics = natural_benefic_classification(ctx)

    return [
        _raja_yoga(ctx),
        _dharma_karmadhipati(ctx),
        _mahapurusha(ctx, "ruchaka"),
        _mahapurusha(ctx, "bhadra"),
        _mahapurusha(ctx, "hamsa"),
        _mahapurusha(ctx, "malavya"),
        _mahapurusha(ctx, "sasa"),
        _gaja_kesari(ctx, benefics),
        _same_rashi_pair(ctx, "budha_aditya", pr.SUN, pr.MERCURY, {
            "mercuryCombust": ctx.is_combust(pr.MERCURY),
            "combustionNote": (
                "Mercury's combustion is reported as an independent fact. It does "
                "not invalidate the formation under this rule set."
            ),
        }),
        _same_rashi_pair(ctx, "chandra_mangala", pr.MOON, pr.MARS, {
            "variantNote": "Mutual-aspect variants are not included in V1.",
        }),
        _same_rashi_pair(ctx, "guru_mangala", pr.JUPITER, pr.MARS),
        _adhi(ctx, benefics),
        _amala(ctx, benefics),
        _viparita(ctx, "harsha"),
        _viparita(ctx, "sarala"),
        _viparita(ctx, "vimala"),
        _dhana(ctx),
        _lakshmi(ctx),
        _saraswati(ctx),
        _kemadruma(ctx),
        _parivartana_yoga(ctx),
        _neecha_bhanga_raja_yoga(ctx),
    ]


def yoga_participation(ctx: ChartContext, planet: int,
                       yogas: Optional[List[dict]] = None) -> List[dict]:
    """SECTION 10 — only the yogas the given planet takes part in."""
    yogas = yogas if yogas is not None else evaluate_all_yogas(ctx)
    out: List[dict] = []

    for yoga in yogas:
        roles: List[str] = []
        others: List[int] = []

        for p in yoga.get("participants", []):
            if p["planet"] == planet:
                roles.append(p["role"])
            else:
                others.append(p["planet"])

        matching_instances = []
        for inst in yoga.get("instances", []):
            members = inst.get("participants", [])
            if planet in members:
                matching_instances.append(inst)
                others.extend(m for m in members if m != planet)

        if not roles and not matching_instances:
            continue

        row = {
            "key": yoga["key"],
            "name": yoga["name"],
            "ruleId": yoga["ruleId"],
            "status": yoga["status"],
            "present": yoga["present"],
            "role": ", ".join(dict.fromkeys(roles)) or "Participant",
            "otherParticipants": [
                {"planet": p, "planetName": pr.planet_name(p)}
                for p in sorted(dict.fromkeys(others))
            ],
            "conditions": yoga["conditions"],
            "instances": matching_instances or yoga.get("instances", []),
            "evidence": yoga.get("evidence"),
            "associationType": yoga.get("associationType"),
            "sources": yoga["sources"],
        }

        # Carry through the yoga-level summary facts, so a planet's own view
        # shows the same detail as the whole-chart view.
        for key in ("note", "coreFormation", "strengtheningConditionsSatisfied",
                    "strengtheningConditionsTotal", "allConditionsSatisfied"):
            if key in yoga:
                row[key] = yoga[key]

        out.append(row)

    return out


def _names(planets) -> str:
    return ", ".join(pr.planet_name(p) for p in sorted(planets))
