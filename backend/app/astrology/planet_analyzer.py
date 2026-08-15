"""Assembles the complete Planet Analysis object (SECTIONS A through V).

This module composes the individual engines. It performs no astrological
reasoning of its own beyond the lordship/lagna facts declared in
``functional_classification_rules``, and it never interprets.
"""
from __future__ import annotations

from typing import List, Optional

from . import (
    avastha_engine,
    combustion_engine,
    conjunction_engine,
    dignity_engine,
    dispositor_engine,
    neecha_bhanga_engine,
    planet_findings,
    shadbala_engine,
    yoga_engine,
)
from .aspect_engine import aspecting_lagna, aspects_given, aspects_received
from .chart_calculator import ChartContext
from .relationship_engine import relationship, relationship_profile
from .rules import planetary_rules as pr
from .rules.functional_classification_rules import (
    CATEGORY_BADHAKA, CATEGORY_DUSTHANA, CATEGORY_KENDRA, CATEGORY_MARAKA,
    CATEGORY_TRIKONA, CATEGORY_UPACHAYA, CATEGORY_DEFINITIONS,
    house_categories, is_yoga_karaka,
)


# ---------------------------------------------------------------------------
# SECTION A — Basic position
# ---------------------------------------------------------------------------
def basic_position(ctx: ChartContext, planet: int) -> dict:
    pos = ctx.positions[planet]
    d9_sign = ctx.varga_sign(planet, 9)
    d9_lord = ctx.lord_of_sign(d9_sign) if d9_sign is not None else None

    speed = ctx.speed_info.get(planet)

    return {
        "planet": planet,
        "planetName": pr.planet_name(planet),
        "planetSanskrit": pr.PLANET_SANSKRIT[planet],
        "symbol": pr.PLANET_SYMBOLS[planet],

        "absoluteLongitude": round(pos.absolute_longitude, 6),
        "absoluteLongitudeDms": pr.to_dms(pos.absolute_longitude),
        "degreeInSign": round(pos.degree_in_sign, 6),
        "degreeInSignDms": pr.to_dms(pos.degree_in_sign),

        "rashi": pos.sign,
        "rashiName": pr.sign_name(pos.sign),
        "rashiSanskrit": pr.SIGN_SANSKRIT[pos.sign],
        "rashiLord": ctx.lord_of_sign(pos.sign),
        "rashiLordName": pr.planet_name(ctx.lord_of_sign(pos.sign)),

        "bhava": pos.bhava,
        "bhavaCategories": house_categories(pos.bhava, ctx.lagna_sign),
        "bhavaChalita": pos.bhava_chalita,
        "bhavaNote": (
            "Bhava is the whole-sign house counted from the Lagna sign "
            "(rule HOUSE_001); this is the frame used by every rule in this "
            "application. Bhava Chalita is PyJHora's cusp-based house and is "
            "shown as an independent fact."
        ),

        "nakshatra": pos.nakshatra,
        "nakshatraName": pr.NAKSHATRA_NAMES[pos.nakshatra - 1],
        "pada": pos.pada,
        "nakshatraLord": pos.nakshatra_lord,
        "nakshatraLordName": pr.planet_name(pos.nakshatra_lord),

        "navamsha": d9_sign,
        "navamshaName": pr.sign_name(d9_sign) if d9_sign is not None else pr.NOT_AVAILABLE,
        "navamshaLord": d9_lord,
        "navamshaLordName": pr.planet_name(d9_lord) if d9_lord is not None else pr.NOT_AVAILABLE,
        "navamshaDegreeDms": (
            pr.to_dms(ctx.varga_degree(planet, 9))
            if ctx.varga_degree(planet, 9) is not None else None
        ),

        "dailyMotion": round(speed[2], 6) if speed and len(speed) > 2 else None,
        "eclipticLatitude": round(speed[1], 6) if speed and len(speed) > 1 else None,

        "sources": {
            "position": {"source": "PyJHora", "methodology": "charts.rasi_chart"},
            "nakshatra": {"source": "PyJHora", "methodology": "drik.nakshatra_pada"},
            "nakshatraLord": {"source": "Custom Rule Engine", "rule": "NAK_001"},
            "bhava": {"source": "Custom Rule Engine", "rule": "HOUSE_001"},
            "navamsha": {"source": "PyJHora",
                         "methodology": "charts.divisional_chart(factor=9)"},
        },
    }


# ---------------------------------------------------------------------------
# SECTION C — Rashi lord relationship
# ---------------------------------------------------------------------------
def rashi_lord_relationship(ctx: ChartContext, planet: int) -> dict:
    lord = ctx.lord_of_sign(ctx.sign_of(planet))
    return {
        "rashi": pr.sign_name(ctx.sign_of(planet)),
        "rashiLord": lord,
        "rashiLordName": pr.planet_name(lord),
        "rashiLordSign": pr.sign_name(ctx.sign_of(lord)),
        "rashiLordBhava": ctx.bhava_of(lord),
        "isSelfLorded": lord == planet,
        "relationship": relationship(ctx, planet, lord),
    }


# ---------------------------------------------------------------------------
# SECTIONS D & E — House ownership and functional classification
# ---------------------------------------------------------------------------
def lordship(ctx: ChartContext, planet: int) -> dict:
    owned = ctx.houses_owned.get(planet, [])
    badhaka = pr.badhaka_house(ctx.lagna_sign)

    owned_detail = []
    for h in owned:
        cats = house_categories(h, ctx.lagna_sign)
        owned_detail.append({
            "house": h,
            "sign": ctx.house_sign[h],
            "signName": pr.sign_name(ctx.house_sign[h]),
            "categories": cats,
            "categoriesText": ", ".join(cats) or "No category",
        })

    def owns_category(cat: str) -> bool:
        return any(cat in d["categories"] for d in owned_detail)

    yoga_karaka = is_yoga_karaka(owned)
    is_node = planet in pr.NODES

    return {
        "planet": planet,
        "planetName": pr.planet_name(planet),
        "housesOwned": owned,
        "housesOwnedDetail": owned_detail,
        "ownsNoHouse": not owned,
        "nodeNote": (
            "Rahu and Ketu lord no sign in the selected rule set, so they hold no "
            "house lordship and no functional classification derived from it."
        ) if is_node else None,

        "kendraLord": owns_category(CATEGORY_KENDRA),
        "trikonaLord": owns_category(CATEGORY_TRIKONA),
        "dusthanaLord": owns_category(CATEGORY_DUSTHANA),
        "upachayaLord": owns_category(CATEGORY_UPACHAYA),
        "marakaLord": owns_category(CATEGORY_MARAKA),
        "badhakesh": owns_category(CATEGORY_BADHAKA),
        "yogaKaraka": yoga_karaka,

        "badhakaHouse": badhaka,
        "badhakaSign": pr.sign_name(ctx.house_sign[badhaka]),
        "badhakaLord": ctx.house_lord[badhaka],
        "badhakaLordName": pr.planet_name(ctx.house_lord[badhaka]),
        "lagnaModality": pr.sign_modality(ctx.lagna_sign),

        "categoryDefinitions": CATEGORY_DEFINITIONS,
        "evidence": {
            "ownership": (
                "; ".join(
                    f"House {d['house']} ({d['signName']}) → {d['categoriesText']}"
                    for d in owned_detail
                ) or f"{pr.planet_name(planet)} owns no house in this rule set."
            ),
            "badhaka": (
                f"The Lagna sign {pr.sign_name(ctx.lagna_sign)} is "
                f"{pr.sign_modality(ctx.lagna_sign)}, so the Badhaka house is the "
                f"{pr.ordinal(badhaka)} house ({pr.sign_name(ctx.house_sign[badhaka])}), lorded by "
                f"{pr.planet_name(ctx.house_lord[badhaka])}."
            ),
            "yogaKaraka": (
                f"Yoga Karaka requires ownership of a Kendra among houses 4, 7, 10 "
                f"and a Trikona among houses 5, 9. Houses owned: "
                f"{owned or 'none'}. Result: {'Yes' if yoga_karaka else 'No'}."
            ),
        },
        "sources": {
            "ownership": {"source": "PyJHora", "rule": "FUNC_001",
                          "methodology": "const._house_owners_list"},
            "categories": {"source": "Custom Rule Engine", "rule": "FUNC_002"},
            "badhaka": {"source": "Custom Rule Engine", "rule": "FUNC_003"},
            "yogaKaraka": {"source": "Custom Rule Engine", "rule": "FUNC_004"},
        },
    }


# ---------------------------------------------------------------------------
# SECTION F — Lagna relationship
# ---------------------------------------------------------------------------
def lagna_relationship(ctx: ChartContext, planet: int) -> dict:
    lagnesh = ctx.house_lord[1]
    aspect = aspecting_lagna(ctx, planet)
    conjunct_lagnesh = (planet != lagnesh
                        and ctx.sign_of(planet) == ctx.sign_of(lagnesh))

    return {
        "lagnaSign": ctx.lagna_sign,
        "lagnaSignName": pr.sign_name(ctx.lagna_sign),
        "lagnaDegreeDms": pr.to_dms(ctx.lagna_degree_in_sign),
        "lagnesh": lagnesh,
        "lagneshName": pr.planet_name(lagnesh),
        "lagneshSign": pr.sign_name(ctx.sign_of(lagnesh)),
        "lagneshBhava": ctx.bhava_of(lagnesh),

        "isLagnesh": planet == lagnesh,
        "isPlacedInLagna": ctx.bhava_of(planet) == 1,
        "aspectsLagna": aspect["aspectsLagna"],
        "aspectType": aspect["aspectType"],
        "aspectEvidence": aspect["evidence"],
        "isConjunctLagnesh": conjunct_lagnesh,
        "conjunctLagneshEvidence": (
            f"{pr.planet_name(planet)} and the Lagnesh {pr.planet_name(lagnesh)} "
            f"both occupy {pr.sign_name(ctx.sign_of(planet))}."
            if conjunct_lagnesh else
            (f"{pr.planet_name(planet)} is itself the Lagnesh."
             if planet == lagnesh else
             f"{pr.planet_name(planet)} occupies "
             f"{pr.sign_name(ctx.sign_of(planet))}; the Lagnesh "
             f"{pr.planet_name(lagnesh)} occupies "
             f"{pr.sign_name(ctx.sign_of(lagnesh))}.")
        ),
        "relationshipWithLagnesh": relationship(ctx, planet, lagnesh),
    }


# ---------------------------------------------------------------------------
# SECTION G — Nakshatra analysis
# ---------------------------------------------------------------------------
def nakshatra_analysis(ctx: ChartContext, planet: int) -> dict:
    pos = ctx.positions[planet]
    lord = pos.nakshatra_lord
    return {
        "nakshatra": pos.nakshatra,
        "nakshatraName": pr.NAKSHATRA_NAMES[pos.nakshatra - 1],
        "pada": pos.pada,
        "nakshatraLord": lord,
        "nakshatraLordName": pr.planet_name(lord),
        "nakshatraLordRashi": ctx.sign_of(lord),
        "nakshatraLordRashiName": pr.sign_name(ctx.sign_of(lord)),
        "nakshatraLordBhava": ctx.bhava_of(lord),
        "isSelfLorded": lord == planet,
        "relationship": relationship(ctx, planet, lord),
        "evidence": (
            f"Longitude {pr.to_dms(pos.absolute_longitude)} falls in "
            f"{pr.NAKSHATRA_NAMES[pos.nakshatra - 1]} "
            f"(nakshatra {pos.nakshatra}), pada {pos.pada}. "
            f"By the Vimshottari sequence (rule NAK_001) its lord is "
            f"{pr.planet_name(lord)}."
        ),
        "sources": {
            "nakshatra": {"source": "PyJHora", "methodology": "drik.nakshatra_pada"},
            "lord": {"source": "Custom Rule Engine", "rule": "NAK_001"},
        },
    }


# ---------------------------------------------------------------------------
# SECTION H — Navamsha analysis
# ---------------------------------------------------------------------------
def navamsha_analysis(ctx: ChartContext, planet: int) -> dict:
    d1 = ctx.sign_of(planet)
    d9 = ctx.varga_sign(planet, 9)

    if d9 is None:
        return {
            "available": False,
            "status": pr.NOT_AVAILABLE,
            "reason": "PyJHora returned no D9 position for this body.",
        }

    d9_lord = ctx.lord_of_sign(d9)
    return {
        "available": True,
        "d1Rashi": d1,
        "d1RashiName": pr.sign_name(d1),
        "d9Rashi": d9,
        "d9RashiName": pr.sign_name(d9),
        "d9Degree": round(ctx.varga_degree(planet, 9) or 0.0, 6),
        "d9DegreeDms": pr.to_dms(ctx.varga_degree(planet, 9) or 0.0),
        "d9Lord": d9_lord,
        "d9LordName": pr.planet_name(d9_lord),
        "d9LordSign": pr.sign_name(ctx.sign_of(d9_lord)),
        "d9LordBhava": ctx.bhava_of(d9_lord),
        "isSelfLorded": d9_lord == planet,
        "relationship": relationship(ctx, planet, d9_lord),
        "vargottama": dignity_engine.vargottama(ctx, planet),
        "d9Dignity": dignity_engine.dignity_in_sign(planet, d9),
    }


# ---------------------------------------------------------------------------
# SECTION J — Retrograde
# ---------------------------------------------------------------------------
def retrograde(ctx: ChartContext, planet: int) -> dict:
    is_retro = ctx.is_retrograde(planet)
    speed = ctx.speed_info.get(planet)
    daily = speed[2] if speed and len(speed) > 2 else None
    is_node = planet in pr.NODES

    return {
        "retrograde": is_retro,
        "motion": "Retrograde" if is_retro else "Direct",
        "stationary": planet in ctx.stationary,
        "dailyMotionDegrees": round(daily, 6) if daily is not None else None,
        "dailyMotionDms": pr.to_dms(daily) if daily is not None else None,
        "note": (
            "Rahu and Ketu are mean nodes in this configuration and are always "
            "retrograde." if is_node else
            "The Sun and Moon never retrograde." if planet in (pr.SUN, pr.MOON)
            else None
        ),
        "evidence": (
            f"PyJHora drik.planets_in_retrograde reports "
            f"{pr.planet_name(planet)} as "
            f"{'retrograde' if is_retro else 'direct'}, determined from the sign "
            f"of its Swiss Ephemeris longitudinal speed."
        ),
        "sources": {"source": "PyJHora",
                    "methodology": "drik.planets_in_retrograde (true speed sign)"},
    }


# ---------------------------------------------------------------------------
# SECTION K — Combustion
# ---------------------------------------------------------------------------
def combustion(ctx: ChartContext, planet: int) -> dict:
    if planet == pr.SUN:
        return {
            "applicable": False,
            "status": pr.NOT_APPLICABLE,
            "combust": False,
            "reason": "Combustion is measured relative to the Sun.",
            "sources": {"source": "PyJHora",
                        "methodology": "charts.planets_in_combustion"},
        }
    if planet in pr.NODES:
        return {
            "applicable": False,
            "status": pr.NOT_APPLICABLE,
            "combust": False,
            "reason": ("PyJHora's combustion calculation covers the Moon through "
                       "Saturn. Rahu and Ketu are excluded from it."),
            "sources": {"source": "PyJHora",
                        "methodology": "charts.planets_in_combustion"},
        }

    sun_long = ctx.positions[pr.SUN].absolute_longitude
    planet_long = ctx.positions[planet].absolute_longitude
    distance = combustion_engine.separation_from_sun(planet_long, sun_long)

    is_retro = ctx.is_retrograde(planet)
    threshold = combustion_engine.threshold_for(planet, is_retro)
    is_combust = ctx.is_combust(planet)
    pyjhora_says = planet in ctx.combust_pyjhora

    return {
        "applicable": True,
        "status": "Evaluated",
        "combust": is_combust,
        "distanceFromSun": round(distance, 6),
        "distanceFromSunDms": pr.to_dms(distance),
        "sunLongitudeDms": pr.to_dms(sun_long),
        "planetLongitudeDms": pr.to_dms(planet_long),
        "thresholdDegrees": threshold,
        "thresholdBasis": ("Retrograde orb" if is_retro else "Direct-motion orb"),
        "pyjhoraVerdict": pyjhora_says,
        "verdictsAgree": is_combust == pyjhora_says,
        "evidence": (
            f"{pr.planet_name(planet)} at {pr.to_dms(planet_long)} and the Sun at "
            f"{pr.to_dms(sun_long)} are separated by {pr.to_dms(distance)} "
            f"(shorter arc). The classical orb for {pr.planet_name(planet)} "
            f"({'retrograde' if is_retro else 'direct'}) is {threshold:g}°, so "
            f"{pr.planet_name(planet)} is "
            f"{'combust' if is_combust else 'not combust'}."
        ),
        "note": (
            "Combustion is evaluated by rule COMBUST_001 using the classical "
            "Parashari orbs. PyJHora 4.8.7 is not used for this verdict: it "
            "indexes its orb table one position out for every planet and "
            "compares raw longitudes rather than the shorter arc. Its result is "
            "shown above for comparison."
            + ("" if is_combust == pyjhora_says else
               f" On this planet the two disagree: PyJHora reports "
               f"{'combust' if pyjhora_says else 'not combust'}.")
        ),
        "sources": combustion_engine.SOURCE,
    }


# ---------------------------------------------------------------------------
# SECTION L — Planetary war
# ---------------------------------------------------------------------------
def planetary_war(ctx: ChartContext, planet: int) -> dict:
    if planet not in pr.GRAHA_YUDDHA_ELIGIBLE:
        return {
            "applicable": False,
            "status": pr.NOT_APPLICABLE,
            "inWar": False,
            "reason": (
                "PyJHora evaluates Graha Yuddha only among Mars, Mercury, "
                "Jupiter, Venus and Saturn."
            ),
            "engagements": [],
            "sources": {"source": "PyJHora",
                        "methodology": "drik.planets_in_graha_yudh"},
        }

    engagements = []
    for a, b, category in ctx.graha_yuddha:
        if planet not in (a, b):
            continue
        other = b if a == planet else a
        sep = conjunction_engine.separation(
            ctx.positions[planet].absolute_longitude,
            ctx.positions[other].absolute_longitude)
        engagements.append({
            "opposingPlanet": other,
            "opposingPlanetName": pr.planet_name(other),
            "category": pr.GRAHA_YUDDHA_CATEGORIES.get(category, str(category)),
            "categoryCode": category,
            "planetDegreeDms": pr.to_dms(ctx.positions[planet].degree_in_sign),
            "opposingDegreeDms": pr.to_dms(ctx.positions[other].degree_in_sign),
            "separation": round(sep, 6),
            "separationDms": pr.to_dms(sep),
            "relationship": relationship(ctx, planet, other),
            "evidence": (
                f"PyJHora reports Graha Yuddha between {pr.planet_name(planet)} "
                f"and {pr.planet_name(other)}, category "
                f"{pr.GRAHA_YUDDHA_CATEGORIES.get(category, category)}. "
                f"Longitudinal separation {pr.to_dms(sep)}."
            ),
        })

    return {
        "applicable": True,
        "status": "Evaluated",
        "inWar": bool(engagements),
        "engagements": engagements,
        "reason": None if engagements else
        f"PyJHora reports no Graha Yuddha involving {pr.planet_name(planet)}.",
        "sources": {"source": "PyJHora", "methodology": "drik.planets_in_graha_yudh"},
    }


# ---------------------------------------------------------------------------
# SECTION S — Divisional chart positions
# ---------------------------------------------------------------------------
def divisional_positions(ctx: ChartContext, planet: int) -> List[dict]:
    out: List[dict] = []
    d1_sign = ctx.sign_of(planet)

    for factor in pr.VARGA_FACTORS:
        sign = ctx.varga_sign(planet, factor)
        if sign is None:
            out.append({
                "factor": factor,
                "name": pr.VARGA_NAMES.get(factor, f"D{factor}"),
                "available": False,
                "status": pr.NOT_AVAILABLE,
            })
            continue
        degree = ctx.varga_degree(planet, factor)
        lord = ctx.lord_of_sign(sign)
        out.append({
            "factor": factor,
            "name": pr.VARGA_NAMES.get(factor, f"D{factor}"),
            "available": True,
            "rashi": sign,
            "rashiName": pr.sign_name(sign),
            "rashiLord": lord,
            "rashiLordName": pr.planet_name(lord),
            "degree": round(degree, 6) if degree is not None else None,
            "degreeDms": pr.to_dms(degree) if degree is not None else None,
            "dignity": dignity_engine.dignity_in_sign(planet, sign),
            "sameAsD1": sign == d1_sign,
        })
    return out


# ---------------------------------------------------------------------------
# SECTION 20 — Compact summary header
# ---------------------------------------------------------------------------
def summary_header(ctx: ChartContext, planet: int, dignity: dict,
                   avasthas: dict) -> dict:
    pos = ctx.positions[planet]
    d9 = ctx.varga_sign(planet, 9)

    # Each lord is paired with the relationship the planet holds towards it, so
    # the header reads as a summary rather than a list of bare names. A planet
    # that lords its own sign or nakshatra forms no pair, and says so.
    sign_lord = ctx.lord_of_sign(pos.sign)
    nak_lord = pos.nakshatra_lord

    def pair(other: int) -> dict:
        if other == planet:
            return {"lord": pr.planet_name(other), "maitri": None,
                    "isSelf": True}
        return {
            "lord": pr.planet_name(other),
            "maitri": relationship(ctx, planet, other)["panchadhaMaitri"],
            "isSelf": False,
        }

    owned = ctx.houses_owned.get(planet, [])

    return {
        "planet": planet,
        "planetName": pr.planet_name(planet),
        "symbol": pr.PLANET_SYMBOLS[planet],
        "rashi": pr.sign_name(pos.sign),
        "rashiLord": pair(sign_lord),
        "bhava": pos.bhava,
        "bhavaCategories": house_categories(pos.bhava, ctx.lagna_sign),
        "housesOwned": owned,
        "housesOwnedSigns": [pr.sign_name(ctx.house_sign[h]) for h in owned],
        "degreeDms": pr.to_dms(pos.degree_in_sign),
        "nakshatra": pr.NAKSHATRA_NAMES[pos.nakshatra - 1],
        "pada": pos.pada,
        "nakshatraLord": pair(nak_lord),
        "navamsha": pr.sign_name(d9) if d9 is not None else pr.NOT_AVAILABLE,
        "swarashi": dignity["swarashi"],
        "mooltrikona": dignity["mooltrikona"],
        "exalted": dignity["exalted"],
        "debilitated": dignity["debilitated"],
        "retrograde": ctx.is_retrograde(planet),
        "combust": (ctx.is_combust(planet)
                    if planet not in (pr.SUN,) + tuple(pr.NODES) else pr.NOT_APPLICABLE),
        "kumaradi": avasthas["kumaradi"]["result"],
        "chaitanyadi": avasthas["chaitanyadi"]["result"],
    }


# ---------------------------------------------------------------------------
# Full analysis
# ---------------------------------------------------------------------------
def analyze_planet(ctx: ChartContext, planet: int,
                   yogas: Optional[List[dict]] = None) -> dict:
    if planet not in pr.ALL_PLANETS:
        raise ValueError(f"Unknown planet id: {planet}")

    yogas = yogas if yogas is not None else yoga_engine.evaluate_all_yogas(ctx)

    dignity = dignity_engine.dignity(ctx, planet)
    avasthas = avastha_engine.avasthas(ctx, planet)

    return {
        "planet": planet,
        "planetName": pr.planet_name(planet),
        "summary": summary_header(ctx, planet, dignity, avasthas),
        "findings": planet_findings.build_findings(ctx, planet, yogas),

        "position": basic_position(ctx, planet),                    # A
        "dignity": dignity,                                          # B
        "rashiLordRelationship": rashi_lord_relationship(ctx, planet),  # C
        "lordship": lordship(ctx, planet),                           # D, E
        "lagnaRelationship": lagna_relationship(ctx, planet),        # F
        "nakshatraRelationship": nakshatra_analysis(ctx, planet),    # G
        "navamshaRelationship": navamsha_analysis(ctx, planet),      # H
        "avastha": avasthas,                                         # I
        "retrograde": retrograde(ctx, planet),                       # J
        "combustion": combustion(ctx, planet),                       # K
        "planetaryWar": planetary_war(ctx, planet),                  # L
        "conjunctions": conjunction_engine.conjunctions(ctx, planet),  # M
        "aspectsReceived": aspects_received(ctx, planet),            # N
        "aspectsGiven": aspects_given(ctx, planet),                  # O
        "relationships": relationship_profile(ctx, planet),          # P, Q
        "shadbala": shadbala_engine.shadbala(ctx, planet),           # R
        "divisionalPositions": divisional_positions(ctx, planet),    # S
        "dispositorChain": dispositor_engine.dispositor_chain(ctx, planet),  # T
        "neechaBhanga": neecha_bhanga_engine.neecha_bhanga(ctx, planet),     # U
        "yogaParticipation": yoga_engine.yoga_participation(ctx, planet, yogas),  # 10
        "allYogas": [
            {"key": y["key"], "name": y["name"], "ruleId": y["ruleId"],
             "status": y["status"], "present": y["present"],
             "participants": y["participants"]}
            for y in yogas
        ],                                                            # 11
    }


def planetary_master_table(ctx: ChartContext) -> List[dict]:
    """SECTION 7 — one row per planet."""
    rows: List[dict] = []
    for planet in pr.ALL_PLANETS:
        pos = ctx.positions[planet]
        dignity = dignity_engine.dignity(ctx, planet)
        d9 = ctx.varga_sign(planet, 9)
        d9_lord = ctx.lord_of_sign(d9) if d9 is not None else None
        rows.append({
            "planet": planet,
            "planetName": pr.planet_name(planet),
            "symbol": pr.PLANET_SYMBOLS[planet],
            "rashi": pos.sign,
            "rashiName": pr.sign_name(pos.sign),
            "degree": round(pos.degree_in_sign, 6),
            "degreeDms": pr.to_dms(pos.degree_in_sign),
            "absoluteLongitudeDms": pr.to_dms(pos.absolute_longitude),
            "bhava": pos.bhava,
            "bhavaChalita": pos.bhava_chalita,
            "nakshatra": pr.NAKSHATRA_NAMES[pos.nakshatra - 1],
            "pada": pos.pada,
            "nakshatraLord": pos.nakshatra_lord,
            "nakshatraLordName": pr.planet_name(pos.nakshatra_lord),
            "navamsha": pr.sign_name(d9) if d9 is not None else pr.NOT_AVAILABLE,
            "navamshaLordName": (pr.planet_name(d9_lord) if d9_lord is not None
                                 else pr.NOT_AVAILABLE),
            "retrograde": ctx.is_retrograde(planet),
            "combust": (ctx.is_combust(planet)
                        if planet not in (pr.SUN,) + tuple(pr.NODES)
                        else pr.NOT_APPLICABLE),
            "swarashi": dignity["swarashi"],
            "mooltrikona": dignity["mooltrikona"],
            "exalted": dignity["exalted"],
            "debilitated": dignity["debilitated"],
            "signRelationship": dignity["signRelationship"],
            "vargottama": dignity_engine.vargottama(ctx, planet)["isVargottama"],
            "kumaradi": avastha_engine.kumaradi_avastha(ctx, planet)["result"],
            "chaitanyadi": avastha_engine.chaitanyadi_avastha(ctx, planet)["result"],
            "housesOwned": ctx.houses_owned.get(planet, []),
        })
    return rows
