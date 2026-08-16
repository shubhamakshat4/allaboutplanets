"""The per-planet finding list.

Every planet is put through the same fixed catalogue of checks, so the same
bullets appear for all nine grahas. A check that cannot apply to a body still
produces its bullet, saying so, and sits in the neutral group.

The group a bullet falls into is decided by ``rules/classification_rules.py``,
which holds the natural, house and functional classifications separately. No
bullet is coloured by anything but a declared rule, and nothing here is
combined into a score or a verdict on the planet as a whole.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from . import (
    avastha_engine, combustion_engine, dignity_engine, dosha_engine,
    neecha_bhanga_engine, shadbala_engine, yoga_engine,
)
from .aspect_engine import aspects_received
from .chart_calculator import ChartContext
from .conjunction_engine import conjunctions
from .relationship_engine import relationship
from .rules import classification_rules as cr
from .rules import maitri_rules as mr
from .rules import planetary_rules as pr

FAVOURABLE = cr.FAVOURABLE
CHALLENGING = cr.CHALLENGING
NEUTRAL = cr.INDIFFERENT

NOT_APPLICABLE = "Does not apply"

_MAITRI_GOOD = (mr.ATI_MITRA, mr.MITRA)
_MAITRI_HARD = (mr.SHATRU, mr.ATI_SHATRU)

_KUMARADI = {
    "Bala": (NEUTRAL, "Bala means infancy, the first of the five states."),
    "Kumara": (NEUTRAL, "Kumara means boyhood, the second of the five states."),
    "Yuva": (FAVOURABLE, "Yuva means youth, the fullest of the five states."),
    "Vriddha": (CHALLENGING, "Vriddha means old age, the fourth of the five states."),
    "Mrita": (CHALLENGING, "Mrita is the last of the five states."),
}

_CHAITANYADI = {
    "Jagrut": (FAVOURABLE, "Jagrut means awake."),
    "Swapna": (NEUTRAL, "Swapna means dreaming."),
    "Sushupta": (CHALLENGING, "Sushupta means deep sleep."),
}

_NATURAL_PHRASE = {
    "Friend": "natural friends",
    "Neutral": "naturally neutral to each other",
    "Enemy": "natural enemies",
}
_TEMPORARY_PHRASE = {
    "Friend": "temporary friends",
    "Enemy": "temporary enemies",
}


def _f(key: str, category: str, text: str, explanation: str,
       detail: Optional[List[Dict[str, str]]] = None,
       open_kind: Optional[str] = None,
       contested: Optional[str] = None) -> dict:
    """One bullet.

    ``open_kind`` applies only to the yellow group and says why the bullet is
    there: the check cannot apply, the rule resolves to neither side, or the
    classics genuinely differ and it is left to the astrologer.
    """
    if category == NEUTRAL and open_kind is None:
        open_kind = cr.OPEN_NEUTRAL
    if contested:
        category = NEUTRAL
        open_kind = cr.OPEN_INTERPRETIVE
        explanation = f"{explanation} {cr.CONTESTED[contested]}"
    return {
        "key": key,
        "category": category,
        "text": text,
        "explanation": explanation,
        "detail": detail or [],
        "openKind": open_kind,
        "openLabel": cr.OPEN_LABELS.get(open_kind) if open_kind else None,
    }


def _na(key: str, text: str, explanation: str) -> dict:
    """A check that structurally cannot apply to this body."""
    return _f(key, NEUTRAL, text, explanation, open_kind=cr.OPEN_NOT_APPLICABLE)


def _ord(n: int) -> str:
    if 10 <= n % 100 <= 20:
        return f"{n}th"
    return f"{n}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th') }".replace(" ", "")


def _article(word: str) -> str:
    w = word.lower()
    return f"{'an' if w[0] in 'aeiou' else 'a'} {w}"


# ===========================================================================
def natural_nature_of(ctx: ChartContext, planet: int) -> cr.NatureVerdict:
    """RULE NATURE_001, resolved against this chart."""
    elongation = None
    companions = None
    if planet == pr.MOON:
        elongation = (ctx.positions[pr.MOON].absolute_longitude
                      - ctx.positions[pr.SUN].absolute_longitude) % 360.0
    if planet == pr.MERCURY:
        companions = [p for p in ctx.planets_in_sign[ctx.sign_of(pr.MERCURY)]
                      if p != pr.MERCURY]
    return cr.natural_nature(planet, moon_elongation=elongation,
                             mercury_companions=companions)


def build_findings(ctx: ChartContext, planet: int,
                   yogas: Optional[List[dict]] = None,
                   doshas: Optional[List[dict]] = None) -> dict:
    """Six streams: green, red, yogas, doshas, yellow and pink.

    Yogas and doshas are pulled out of the two main groups so they can be read
    on their own, and anything the classics leave open is pulled out of the
    yellow group into its own, so a genuine disagreement is never mistaken for
    a routine 'does not apply'.
    """
    yogas = yogas if yogas is not None else yoga_engine.evaluate_all_yogas(ctx)
    doshas = doshas if doshas is not None else dosha_engine.evaluate_all_doshas(ctx)
    name = pr.planet_name(planet)
    nature = natural_nature_of(ctx, planet)

    items: List[dict] = []
    items += _nature(ctx, planet, name, nature)
    items += _dignity(ctx, planet, name)
    items += _placement(ctx, planet, name, nature)
    items += _lordship(ctx, planet, name, nature)
    items += _relationships(ctx, planet, name)
    items += _motion_and_state(ctx, planet, name, nature)
    items += _company(ctx, planet, name)
    items += _avasthas(ctx, planet, name)
    items += _strength(ctx, planet, name)
    items += _special(ctx, planet, name)

    groups = {FAVOURABLE: [], CHALLENGING: [], NEUTRAL: []}
    interpretive: List[dict] = []
    for item in items:
        if item.get("openKind") == cr.OPEN_INTERPRETIVE:
            interpretive.append(item)
        else:
            groups[item["category"]].append(item)

    yoga_items = _yoga_items(ctx, planet, name, yogas)
    dosha_items = _dosha_items(ctx, planet, name, doshas)

    return {
        "favourable": groups[FAVOURABLE],
        "challenging": groups[CHALLENGING],
        "yogas": yoga_items,
        "doshas": dosha_items,
        "neutral": groups[NEUTRAL],
        "interpretive": interpretive,
        "counts": {
            "favourable": len(groups[FAVOURABLE]),
            "challenging": len(groups[CHALLENGING]),
            "yogas": len(yoga_items),
            "doshas": len(dosha_items),
            "neutral": len(groups[NEUTRAL]),
            "interpretive": len(interpretive),
        },
        "naturalNature": nature.nature,
        "note": (
            "Every planet is put through the same checks, so a point that "
            "cannot apply still appears. Yogas and doshas are listed on their "
            "own. The yellow group holds points that came out on neither side "
            "or cannot apply; the pink group holds those the classics "
            "genuinely differ over, each with its reason under Explain. No "
            f"overall judgement is made about {name}, and no result is "
            f"predicted."
        ),
    }


# --- 1. Natural nature -----------------------------------------------------
def _nature(ctx, planet, name, nature) -> List[dict]:
    category = {
        cr.BENEFIC: FAVOURABLE,
        cr.MALEFIC: CHALLENGING,
    }.get(nature.nature, NEUTRAL)
    return [_f("nature-natural", category,
               f"Natural nature: {nature.nature.lower()}", nature.reason)]


# --- 2. Dignity ------------------------------------------------------------
def _dignity(ctx, planet, name) -> List[dict]:
    d = dignity_engine.dignity(ctx, planet)
    pos = ctx.positions[planet]
    sign = pr.sign_name(pos.sign)
    node = planet in pr.NODES
    out = []

    # Exaltation
    if d["exalted"]:
        deep = d.get("deepExaltationLongitude")
        point = (f" Its deepest point of exaltation is {deep['signName']} "
                 f"{deep['degreeInSignDms']}." if deep else "")
        out.append(_f("dignity-exalted", FAVOURABLE, f"Exalted in {sign}",
                      f"{sign} is the exaltation sign of {name}.{point}",
                      contested="node_dignity" if node else None))
    else:
        ex = ", ".join(pr.sign_name(s) for s in pr.exaltation_signs(planet))
        out.append(_f("dignity-exalted", NEUTRAL, "Not exalted",
                      f"{name} is exalted in {ex or 'no sign in this rule set'}. "
                      f"It stands in {sign}."))

    # Debilitation
    if d["debilitated"]:
        out.append(_f("dignity-debilitated", CHALLENGING, f"Debilitated in {sign}",
                      f"{sign} is the debilitation sign of {name}.",
                      contested="node_dignity" if node else None))
    else:
        de = ", ".join(pr.sign_name(s) for s in pr.debilitation_signs(planet))
        out.append(_f("dignity-debilitated", NEUTRAL, "Not debilitated",
                      f"{name} is debilitated in "
                      f"{de or 'no sign in this rule set'}. It stands in {sign}."))

    # Own sign
    if node:
        out.append(_na("dignity-own", f"Own sign: {NOT_APPLICABLE.lower()}",
                      f"{name} lords no sign, so it cannot stand in its own."))
    elif d["swarashi"] is True:
        out.append(_f("dignity-own", FAVOURABLE, f"In its own sign, {sign}",
                      f"{name} lords {sign} and stands in it."))
    else:
        owned = ", ".join(pr.sign_name(s) for s in pr.owned_signs(planet))
        out.append(_f("dignity-own", NEUTRAL, "Not in its own sign",
                      f"{name} lords {owned}. It stands in {sign}."))

    # Mooltrikona
    rng = pr.mooltrikona_range(planet)
    if rng is None:
        out.append(_na("dignity-mooltrikona",
                      f"Mooltrikona: {NOT_APPLICABLE.lower()}",
                      f"No Mooltrikona is given for {name} in this rule set."))
    elif d["mooltrikona"] is True:
        out.append(_f("dignity-mooltrikona", FAVOURABLE, "In its Mooltrikona portion",
                      f"The Mooltrikona of {name} is {d['mooltrikonaRange']}, and "
                      f"it stands at {pos.degree_in_sign:.2f}° of {sign}."))
    else:
        out.append(_f("dignity-mooltrikona", NEUTRAL, "Not in its Mooltrikona",
                      f"The Mooltrikona of {name} is {d['mooltrikonaRange']}. It "
                      f"stands at {pos.degree_in_sign:.2f}° of {sign}."))

    # Friend / neutral / enemy sign
    lord = d["currentRashiLordName"]
    if d["friendSign"]:
        out.append(_f("dignity-signlord", FAVOURABLE, f"In a friend's sign, {sign}",
                      f"{sign} is lorded by {lord}, a natural friend of {name}."))
    elif d["enemySign"]:
        out.append(_f("dignity-signlord", CHALLENGING, f"In an enemy's sign, {sign}",
                      f"{sign} is lorded by {lord}, a natural enemy of {name}."))
    elif d["neutralSign"]:
        out.append(_f("dignity-signlord", NEUTRAL, f"In a neutral sign, {sign}",
                      f"{sign} is lorded by {lord}, towards whom {name} is "
                      f"neither friend nor enemy."))
    else:
        out.append(_f("dignity-signlord", NEUTRAL,
                      f"Sign relationship: {d['signRelationship'].lower()}",
                      f"{sign} is lorded by {lord}."))

    # Vargottama
    varg = dignity_engine.vargottama(ctx, planet)
    if varg.get("isVargottama") is True:
        out.append(_f("dignity-vargottama", FAVOURABLE, "Vargottama",
                      f"{name} holds {sign} in both the Rashi chart and the "
                      f"Navamsha.",
                      contested="vargottama_debilitated" if d["debilitated"] else None))
    else:
        out.append(_f("dignity-vargottama", NEUTRAL, "Not Vargottama",
                      f"{name} stands in {varg.get('d1SignName', sign)} in the "
                      f"Rashi chart and {varg.get('d9SignName', '—')} in the "
                      f"Navamsha."))
    return out


# --- 3. House placement ----------------------------------------------------
def _placement(ctx, planet, name, nature) -> List[dict]:
    house = ctx.positions[planet].bhava
    category, why = cr.placement_category(house, nature.nature)
    groups = cr.house_groups(house)
    return [_f("house-placement", category,
               f"Sits in the {_ord(house)} house"
               + (f", {groups[0] if len(groups) == 1 else ' and '.join(groups)}"
                  if groups else ""),
               f"{name} occupies {pr.sign_name(ctx.sign_of(planet))}, the "
               f"{_ord(house)} house from the Lagna. {why}",
               detail=[
                   {"label": "House", "value": _ord(house)},
                   {"label": "Sign", "value": pr.sign_name(ctx.sign_of(planet))},
                   {"label": "House groups", "value": ", ".join(groups) or "None"},
                   {"label": f"{name}'s nature", "value": nature.nature},
               ])]


# --- 4. Lordship and functional nature -------------------------------------
def _lordship(ctx, planet, name, nature) -> List[dict]:
    owned = ctx.houses_owned.get(planet, [])
    verdict, reasons = cr.functional_nature(owned, nature.nature)
    out = []

    if not owned:
        out.append(_na("lord-houses",
                      f"House lordship: {NOT_APPLICABLE.lower()}",
                      f"{name} lords no sign, so it holds no house."))
        out.append(_na("lord-functional",
                       "Functional nature: not set by lordship", reasons[0]))
        out.append(_na("lord-yogakaraka",
                      f"Yoga Karaka: {NOT_APPLICABLE.lower()}",
                      f"A Yoga Karaka lords both a Kendra and a Trikona. "
                      f"{name} lords no house."))
        out.append(_na("lord-badhaka",
                      f"Badhakesh: {NOT_APPLICABLE.lower()}",
                      f"{name} lords no house, so it cannot be the Badhakesh."))
        out.append(_na("lord-maraka",
                      f"Maraka lord: {NOT_APPLICABLE.lower()}",
                      f"The 2nd and 7th are the Maraka houses, lorded here by "
                      f"{pr.planet_name(ctx.house_lord[2])} and "
                      f"{pr.planet_name(ctx.house_lord[7])}. {name} lords no "
                      f"house, so it cannot be among them."))
        return out

    signs = ", ".join(pr.sign_name(ctx.house_sign[h]) for h in owned)
    out.append(_f("lord-houses", NEUTRAL,
                  f"Lords the {cr._list(owned)} house"
                  + ("s" if len(owned) > 1 else ""),
                  f"{name} lords {signs}, which fall as the {cr._list(owned)} "
                  f"from the Lagna.",
                  detail=[{"label": _ord(h),
                           "value": f"{pr.sign_name(ctx.house_sign[h])} — "
                                    f"{', '.join(cr.house_groups(h)) or 'no group'}"}
                          for h in owned]))

    category = {cr.BENEFIC: FAVOURABLE, cr.MALEFIC: CHALLENGING}.get(verdict, NEUTRAL)
    contested = cr.functional_contested(owned, nature.nature)
    out.append(_f("lord-functional", category,
                  f"Functional nature for this Lagna: "
                  + (f"{verdict.lower()}, but the lordships conflict"
                     if contested else verdict.lower()),
                  f"For a {pr.sign_name(ctx.lagna_sign)} Lagna, {name} lords the "
                  f"{cr._list(owned)}. " + " ".join(reasons),
                  contested=contested,
                  detail=[{"label": f"Reason {i + 1}", "value": r}
                          for i, r in enumerate(reasons)]))

    kendra = [h for h in owned if h in (4, 7, 10)]
    trikona = [h for h in owned if h in (5, 9)]
    if kendra and (trikona or 1 in owned):
        out.append(_f("lord-yogakaraka", FAVOURABLE, "Yoga Karaka",
                      f"{name} lords both a Kendra ({cr._list(kendra)}) and a "
                      f"Trikona, which makes it the Yoga Karaka for a "
                      f"{pr.sign_name(ctx.lagna_sign)} Lagna."))
    else:
        out.append(_f("lord-yogakaraka", NEUTRAL, "Not a Yoga Karaka",
                      f"A Yoga Karaka lords both a Kendra (4th, 7th, 10th) and "
                      f"a Trikona (5th, 9th). {name} lords the {cr._list(owned)}."))

    badhaka = pr.badhaka_house(ctx.lagna_sign)
    if badhaka in owned:
        out.append(_f("lord-badhaka", CHALLENGING, "Badhakesh",
                      f"A {pr.sign_modality(ctx.lagna_sign).lower()} Lagna takes "
                      f"the {_ord(badhaka)} as its Badhaka house, and {name} "
                      f"lords it."))
    else:
        out.append(_f("lord-badhaka", NEUTRAL, "Not the Badhakesh",
                      f"For a {pr.sign_modality(ctx.lagna_sign).lower()} Lagna "
                      f"the Badhaka house is the {_ord(badhaka)}, lorded by "
                      f"{pr.planet_name(ctx.house_lord[badhaka])}."))

    maraka = [h for h in owned if h in cr.MARAKA]
    if maraka:
        out.append(_f("lord-maraka", CHALLENGING,
                      f"Maraka lord — lords the {cr._list(maraka)}",
                      f"The 2nd and 7th are the Maraka houses. {name} lords "
                      f"the {cr._list(maraka)}."))
    else:
        out.append(_f("lord-maraka", NEUTRAL, "Not a Maraka lord",
                      f"The Maraka houses are the 2nd and 7th, lorded by "
                      f"{pr.planet_name(ctx.house_lord[2])} and "
                      f"{pr.planet_name(ctx.house_lord[7])}."))
    return out


# --- 5. The four key relationships -----------------------------------------
def _relationships(ctx, planet, name) -> List[dict]:
    pos = ctx.positions[planet]
    d9 = ctx.varga_sign(planet, 9)
    targets = [
        ("rashi-lord", ctx.lord_of_sign(pos.sign), "the lord of its sign"),
        ("nakshatra-lord", pos.nakshatra_lord, "the lord of its nakshatra"),
        ("navamsha-lord", ctx.lord_of_sign(d9) if d9 is not None else None,
         "the lord of its Navamsha sign"),
        ("lagnesh", ctx.house_lord[1], "the Lagna lord"),
    ]

    out = []
    for key, other, role in targets:
        if other is None:
            out.append(_na(f"rel-{key}",
                          f"Relationship with {role}: {NOT_APPLICABLE.lower()}",
                          "That lord could not be determined."))
            continue
        if other == planet:
            out.append(_f(f"rel-{key}", NEUTRAL,
                          f"Is itself {role}",
                          f"{name} is {role}, so no relationship pair is formed."))
            continue

        rel = relationship(ctx, planet, other)
        maitri = rel["panchadhaMaitri"]
        category = (FAVOURABLE if maitri in _MAITRI_GOOD else
                    CHALLENGING if maitri in _MAITRI_HARD else NEUTRAL)
        out.append(_f(
            f"rel-{key}", category,
            f"{maitri} with {pr.planet_name(other)}, {role}",
            f"{name} and {pr.planet_name(other)} are "
            f"{_NATURAL_PHRASE[rel['naturalRelationship']]} by the fixed table, "
            f"and {_TEMPORARY_PHRASE[rel['temporaryRelationship']]} by their "
            f"places in this chart. Together these give {maitri}.",
            detail=[
                {"label": "Natural", "value": rel["naturalRelationship"]},
                {"label": "Temporary", "value": rel["temporaryRelationship"]},
                {"label": "Combined", "value": maitri},
            ]))
    return out


# --- 6. Motion, combustion, war --------------------------------------------
def _motion_and_state(ctx, planet, name, nature) -> List[dict]:
    out = []

    category, text, why = cr.retrograde_category(
        planet, ctx.is_retrograde(planet), nature.nature)
    if category != NEUTRAL:
        why = f"{why} {cr.CONTESTED['retrograde_school']}"
    out.append(_f("state-retrograde", category, text, why))

    # Combustion
    if planet == pr.SUN:
        out.append(_na("state-combust",
                      f"Combustion: {NOT_APPLICABLE.lower()}",
                      "Combustion is measured from the Sun, so it cannot apply "
                      "to the Sun itself."))
    elif planet in pr.NODES:
        out.append(_na("state-combust",
                      f"Combustion: {NOT_APPLICABLE.lower()}",
                      f"{name} is a shadow point without a disc, so combustion "
                      f"is not reckoned for it."))
    else:
        sun = ctx.positions[pr.SUN].absolute_longitude
        gap = combustion_engine.separation_from_sun(
            ctx.positions[planet].absolute_longitude, sun)
        orb = combustion_engine.threshold_for(planet, ctx.is_retrograde(planet))
        if ctx.is_combust(planet):
            out.append(_f("state-combust", CHALLENGING,
                          f"Combust — {pr.to_dms(gap)} from the Sun",
                          f"A graha within {orb:g}° of the Sun is combust. "
                          f"{name} stands {pr.to_dms(gap)} away.",
                          contested="mercury_combustion"
                          if planet == pr.MERCURY else None))
        else:
            out.append(_f("state-combust", FAVOURABLE,
                          f"Free of combustion — {pr.to_dms(gap)} from the Sun",
                          f"{name} would be combust within {orb:g}° of the Sun. "
                          f"It stands {pr.to_dms(gap)} away, so it is clear."))

    # Planetary war
    if planet not in pr.GRAHA_YUDDHA_ELIGIBLE:
        out.append(_na("state-war",
                      f"Planetary war: {NOT_APPLICABLE.lower()}",
                      "Graha Yuddha is fought only between Mars, Mercury, "
                      "Jupiter, Venus and Saturn."))
    else:
        engaged = [p for a, b, _ in ctx.graha_yuddha if planet in (a, b)
                   for p in (a, b) if p != planet]
        if engaged:
            out.append(_f("state-war", CHALLENGING,
                          f"In planetary war with {pr.planet_name(engaged[0])}",
                          f"{name} and {pr.planet_name(engaged[0])} stand at "
                          f"almost the same longitude, which is Graha Yuddha."))
        else:
            out.append(_f("state-war", NEUTRAL, "Not in planetary war",
                          f"{name} shares no near-identical longitude with "
                          f"another of the five star planets."))
    return out


# --- 7. Company ------------------------------------------------------------
def _company(ctx, planet, name) -> List[dict]:
    out = []
    joined = conjunctions(ctx, planet)
    if not joined:
        out.append(_f("company-conjunction", NEUTRAL, "Joined with no planet",
                      f"No other graha shares {pr.sign_name(ctx.sign_of(planet))} "
                      f"with {name}."))
    else:
        for conj in joined:
            other = conj["planetB"]
            other_nature = natural_nature_of(ctx, other)
            category = {cr.BENEFIC: FAVOURABLE,
                        cr.MALEFIC: CHALLENGING}.get(other_nature.nature, NEUTRAL)
            out.append(_f(
                f"company-conj-{other}", category,
                f"Joined with {conj['planetBName']} in {conj['rashiName']}",
                f"{name} and {conj['planetBName']} share {conj['rashiName']}, "
                f"{conj['separationDms']} apart. {conj['planetBName']} is "
                f"{_article(other_nature.nature)} by nature.",
                detail=[
                    {"label": name, "value": conj["degreeADms"]},
                    {"label": conj["planetBName"], "value": conj["degreeBDms"]},
                    {"label": "Gap", "value": conj["separationDms"]},
                    {"label": "Relationship",
                     "value": conj["relationship"]["panchadhaMaitri"]},
                ],
                contested="node_association" if other in pr.NODES else None))

    received = aspects_received(ctx, planet)
    if not received:
        out.append(_f("company-aspect", NEUTRAL, "Receives no aspect",
                      f"No graha casts a Graha Drishti on {name}."))
    else:
        for asp in received:
            source = asp["sourcePlanet"]
            source_nature = natural_nature_of(ctx, source)
            category = {cr.BENEFIC: FAVOURABLE,
                        cr.MALEFIC: CHALLENGING}.get(source_nature.nature, NEUTRAL)
            out.append(_f(
                f"company-asp-{source}", category,
                f"Receives the {asp['aspectType'].lower()} of "
                f"{asp['sourcePlanetName']}",
                f"{asp['sourcePlanetName']} casts its {asp['aspectType'].lower()} "
                f"on {pr.sign_name(ctx.sign_of(planet))}, where {name} stands. "
                f"{asp['sourcePlanetName']} is "
                f"{_article(source_nature.nature)} by nature.",
                detail=[{"label": "Relationship",
                         "value": asp["relationship"]["panchadhaMaitri"]}],
                contested="node_association" if source in pr.NODES else None))
    return out


# --- 8. Avasthas -----------------------------------------------------------
def _avasthas(ctx, planet, name) -> List[dict]:
    av = avastha_engine.avasthas(ctx, planet)
    out = []
    for key, table, label in (("kumaradi", _KUMARADI, "Kumaradi"),
                              ("chaitanyadi", _CHAITANYADI, "Chaitanyadi")):
        value = av[key]["result"]
        category, meaning = table[value]
        out.append(_f(f"avastha-{key}", category, f"{label} Avastha: {value}",
                      f"{meaning} {name} stands at {av[key]['degreeDms']} of "
                      f"{_article(av[key]['signType'])} sign, which is the "
                      f"{av[key]['rangeUsed']} band."))
    return out


# --- 9. Strength -----------------------------------------------------------
def _strength(ctx, planet, name) -> List[dict]:
    sb = shadbala_engine.shadbala(ctx, planet)
    if not sb.get("available"):
        return [_na("strength-shadbala",
                   f"Shadbala: {NOT_APPLICABLE.lower()}",
                   f"The six-fold strength is reckoned for the Sun through "
                   f"Saturn. It is not calculated for {name}.")]

    total, required = sb["totalRupa"], sb["requiredRupa"]
    if total is None or required is None:
        return [_f("strength-shadbala", NEUTRAL, "Shadbala: not available",
                   "The figures could not be calculated for this chart.")]

    meets = total >= required
    return [_f("strength-shadbala", FAVOURABLE if meets else CHALLENGING,
               f"Shadbala {total:.2f} rupas against the {required:.2f} required",
               f"The classical framework sets a required minimum for each "
               f"graha. For {name} that minimum is {required:.2f} rupas, and "
               f"the six strengths together come to {total:.2f} rupas.",
               detail=[
                   {"label": "Sthana", "value": f"{sb['sthanaBala']['total']:.2f}"},
                   {"label": "Dig", "value": f"{sb['digBala']['total']:.2f}"},
                   {"label": "Kala", "value": f"{sb['kalaBala']['total']:.2f}"},
                   {"label": "Cheshta", "value": f"{sb['cheshtaBala']['total']:.2f}"},
                   {"label": "Naisargika", "value": f"{sb['naisargikaBala']['total']:.2f}"},
                   {"label": "Drik", "value": f"{sb['drikBala']['total']:.2f}"},
               ])]


# --- 10. Neecha Bhanga and yogas -------------------------------------------
def _nb_detail(nb: dict) -> List[Dict[str, str]]:
    """One row per cancelling condition, naming the condition rather than just
    numbering it, so the reader can see what was actually tested."""
    return [{"label": f"{c['number']}. {c['title']}", "value": c["status"]}
            for c in nb["conditions"]]


def _nb_explanation(ctx, name: str, nb: dict) -> str:
    """The six conditions spelled out, each with what was found."""
    lines = [
        f"{name} is debilitated in {nb['debilitationSignName']}, whose lord is "
        f"{nb['debilitationLordName']}. Its exaltation sign is "
        f"{nb['exaltationSignName']}, whose lord is {nb['exaltationLordName']}. "
        f"The classics give six conditions under which a debilitation is "
        f"cancelled, and each is tested separately:",
    ]
    for c in nb["conditions"]:
        lines.append(f"({c['number']}) {c['statement']} — {c['status']}. "
                     f"{c['evidence']}")
    lines.append(f"{nb['conditionsSatisfied']} of the six are met. "
                 f"{nb['exclusionNote']}")
    return " ".join(lines)


def _special(ctx, planet, name) -> List[dict]:
    out = []

    nb = neecha_bhanga_engine.neecha_bhanga(ctx, planet)
    if not nb["applicable"]:
        out.append(_na("special-neechabhanga",
                      f"Neecha Bhanga: {NOT_APPLICABLE.lower()}",
                      f"{name} is not debilitated, so no cancellation of "
                      f"debilitation arises."))
    elif nb["conditionsSatisfied"] > 0:
        out.append(_f("special-neechabhanga", FAVOURABLE,
                      f"Neecha Bhanga — {nb['conditionsSatisfied']} of 6 "
                      f"conditions met",
                      _nb_explanation(ctx, name, nb),
                      detail=_nb_detail(nb),
                      contested=("partial_neecha_bhanga"
                                 if nb["conditionsSatisfied"] < 6 else None)))
    else:
        out.append(_f("special-neechabhanga", CHALLENGING,
                      "Neecha Bhanga — no cancelling condition is met",
                      _nb_explanation(ctx, name, nb),
                      detail=_nb_detail(nb)))

    return out


# --- Yogas, as their own list ----------------------------------------------
def _yoga_items(ctx, planet, name, yogas) -> List[dict]:
    """Only the yogas this planet takes part in, and only those that form.

    Kemadruma is left out here: it is a dosha by nature and is reported with
    the doshas instead.
    """
    out = []
    for row in yoga_engine.yoga_participation(ctx, planet, yogas):
        if not row["present"] or row["key"] == "kemadruma":
            continue
        others = ", ".join(o["planetName"] for o in row["otherParticipants"])
        out.append(_f(
            f"yoga-{row['key']}", FAVOURABLE,
            f"{row['name']}" + (f" — with {others}" if others else ""),
            f"{name} takes part in {row['name']} as {row['role'].lower()}. "
            f"The conditions checked are listed below.",
            detail=[{"label": c["title"], "value": c["status"]}
                    for c in row["conditions"]]))
    return out


# --- Doshas, as their own list ---------------------------------------------
def _dosha_items(ctx, planet, name, doshas) -> List[dict]:
    """Only the doshas this planet takes part in, and only those that form."""
    out = []
    for d in dosha_engine.doshas_for_planet(ctx, planet, doshas):
        others = [p for p in d["participants"] if p != planet]
        with_whom = (" — with " + ", ".join(pr.planet_name(p) for p in others)
                     if others else "")
        explanation = f"{d['formation']} {d['evidence']}"
        if d.get("cancellation"):
            explanation += (" The classics give grounds on which this is held "
                            f"to be lifted: {d['cancellation']}")
        out.append(_f(f"dosha-{d['key']}", CHALLENGING,
                      f"{d['name']}{with_whom}", explanation,
                      detail=d["detail"]))
    return out
