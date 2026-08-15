"""The curated V1 dosha set (RULES DOSHA_001 .. DOSHA_014).

A dosha is reported by its formation only. Where the classics give well-known
grounds for cancellation those are listed on the finding, but the software does
not decide whether a cancellation carries: that is the astrologer's to weigh.

Every dosha reports which planets take part in it, so a planet's page can show
only the doshas it is actually involved in.
"""
from __future__ import annotations

from typing import Dict, List, NamedTuple, Optional

from .chart_calculator import ChartContext
from .conjunction_engine import separation
from .rules import classification_rules as cr
from .rules import planetary_rules as pr
from .rules.dosha_rules import (
    CANCELLATIONS, DOSHA_SPECS, MALEFICS_FOR_HEMMING, MANGAL_HOUSES,
    SPEC_BY_KEY, DoshaSpec,
)


class Dosha(NamedTuple):
    spec: DoshaSpec
    present: bool
    participants: List[int]
    evidence: str
    detail: List[Dict[str, str]]

    def as_dict(self) -> dict:
        return {
            "key": self.spec.key,
            "ruleId": self.spec.rule_id,
            "name": self.spec.name,
            "formation": self.spec.formation,
            "present": self.present,
            "participants": self.participants,
            "participantNames": [pr.planet_name(p) for p in self.participants],
            "evidence": self.evidence,
            "detail": self.detail,
            "cancellation": CANCELLATIONS.get(self.spec.key),
        }


def _d(key: str, present: bool, participants: List[int], evidence: str,
       detail: Optional[List[Dict[str, str]]] = None) -> Dosha:
    return Dosha(SPEC_BY_KEY[key], present, participants, evidence, detail or [])


def _shares_sign(ctx: ChartContext, a: int, b: int) -> bool:
    return ctx.sign_of(a) == ctx.sign_of(b)


def _gap(ctx: ChartContext, a: int, b: int) -> str:
    return pr.to_dms(separation(ctx.positions[a].absolute_longitude,
                                ctx.positions[b].absolute_longitude))


def evaluate_all_doshas(ctx: ChartContext) -> List[dict]:
    """Every dosha in the V1 set, present or not."""
    return [d.as_dict() for d in (
        _mangal(ctx), _kaal_sarpa(ctx), _guru_chandal(ctx), _angarak(ctx),
        _grahan(ctx), _shrapit(ctx), _vish(ctx), _kemadruma(ctx),
        _sakata(ctx), _papakartari(ctx), _kendradhipatya(ctx), _daridra(ctx),
        _amavasya(ctx), _pitru(ctx),
    )]


def doshas_for_planet(ctx: ChartContext, planet: int,
                      doshas: Optional[List[dict]] = None) -> List[dict]:
    doshas = doshas if doshas is not None else evaluate_all_doshas(ctx)
    return [d for d in doshas if d["present"] and planet in d["participants"]]


# ---------------------------------------------------------------------------
def _mangal(ctx: ChartContext) -> Dosha:
    """DOSHA_001. Reckoned from the Lagna, the Moon and Venus."""
    mars_sign = ctx.sign_of(pr.MARS)
    references = [
        ("Lagna", ctx.lagna_sign),
        ("Moon", ctx.sign_of(pr.MOON)),
        ("Venus", ctx.sign_of(pr.VENUS)),
    ]
    hits, rows = [], []
    for label, ref in references:
        house = ctx.house_from(ref, mars_sign)
        caught = house in MANGAL_HOUSES
        if caught:
            hits.append(label)
        rows.append({"label": f"From the {label}",
                     "value": f"{house}th house" + (" — caught" if caught else "")})

    return _d("mangal", bool(hits), [pr.MARS] if hits else [],
              (f"Mars stands in {pr.sign_name(mars_sign)}. Counted from the "
               f"{', the '.join(hits)}, it falls in one of the houses that "
               f"carry the dosha (1st, 2nd, 4th, 7th, 8th, 12th)."
               if hits else
               f"Mars stands in {pr.sign_name(mars_sign)} and falls in none of "
               f"the dosha houses from the Lagna, the Moon or Venus."),
              rows)


def _kaal_sarpa(ctx: ChartContext) -> Dosha:
    """DOSHA_002. Every graha inside the Rahu-to-Ketu arc."""
    rahu = ctx.positions[pr.RAHU].absolute_longitude
    inside, outside = [], []
    for planet in pr.SUN_TO_SATURN:
        # Distance travelled from Rahu in zodiacal order; the nodes are 180
        # apart, so anything under 180 lies in the Rahu-to-Ketu half.
        arc = (ctx.positions[planet].absolute_longitude - rahu) % 360.0
        (inside if arc < 180.0 else outside).append(planet)

    present = not outside
    return _d("kaal_sarpa", present,
              list(pr.ALL_PLANETS) if present else [],
              (f"All seven grahas lie in the half of the zodiac running from "
               f"Rahu in {pr.sign_name(ctx.sign_of(pr.RAHU))} to Ketu in "
               f"{pr.sign_name(ctx.sign_of(pr.KETU))}."
               if present else
               f"{', '.join(pr.planet_name(p) for p in outside)} "
               f"{'lies' if len(outside) == 1 else 'lie'} outside the arc from "
               f"Rahu to Ketu, so the axis is not closed."),
              [{"label": "Inside the arc",
                "value": ", ".join(pr.planet_name(p) for p in inside) or "none"},
               {"label": "Outside the arc",
                "value": ", ".join(pr.planet_name(p) for p in outside) or "none"}])


def _pair_dosha(ctx: ChartContext, key: str, a: int, others: List[int]) -> Dosha:
    """A dosha formed by one graha sharing a sign with any of ``others``."""
    joined = [b for b in others if _shares_sign(ctx, a, b)]
    if not joined:
        return _d(key, False, [],
                  f"{pr.planet_name(a)} in {pr.sign_name(ctx.sign_of(a))} "
                  f"shares its sign with "
                  f"{' or '.join(pr.planet_name(b) for b in others)} in neither case.")
    other = joined[0]
    return _d(key, True, [a, other],
              f"{pr.planet_name(a)} and {pr.planet_name(other)} both occupy "
              f"{pr.sign_name(ctx.sign_of(a))}, {_gap(ctx, a, other)} apart.",
              [{"label": pr.planet_name(a),
                "value": pr.to_dms(ctx.positions[a].degree_in_sign)},
               {"label": pr.planet_name(other),
                "value": pr.to_dms(ctx.positions[other].degree_in_sign)},
               {"label": "Gap", "value": _gap(ctx, a, other)}])


def _guru_chandal(ctx): return _pair_dosha(ctx, "guru_chandal", pr.JUPITER, [pr.RAHU, pr.KETU])
def _angarak(ctx): return _pair_dosha(ctx, "angarak", pr.MARS, [pr.RAHU, pr.KETU])
def _shrapit(ctx): return _pair_dosha(ctx, "shrapit", pr.SATURN, [pr.RAHU])
def _vish(ctx): return _pair_dosha(ctx, "vish", pr.MOON, [pr.SATURN])


def _grahan(ctx: ChartContext) -> Dosha:
    """DOSHA_005. Either luminary with either node."""
    pairs = [(lum, node) for lum in (pr.SUN, pr.MOON)
             for node in (pr.RAHU, pr.KETU) if _shares_sign(ctx, lum, node)]
    if not pairs:
        return _d("grahan", False, [],
                  "Neither the Sun nor the Moon shares its sign with Rahu or Ketu.")
    lum, node = pairs[0]
    return _d("grahan", True, sorted({p for pair in pairs for p in pair}),
              f"{pr.planet_name(lum)} and {pr.planet_name(node)} both occupy "
              f"{pr.sign_name(ctx.sign_of(lum))}, {_gap(ctx, lum, node)} apart.",
              [{"label": f"{pr.planet_name(a)} + {pr.planet_name(b)}",
                "value": f"{pr.sign_name(ctx.sign_of(a))}, {_gap(ctx, a, b)} apart"}
               for a, b in pairs])


def _kemadruma(ctx: ChartContext) -> Dosha:
    """DOSHA_008. Nothing beside the Moon."""
    moon = ctx.sign_of(pr.MOON)
    excluded = (pr.SUN, pr.RAHU, pr.KETU)
    rows, qualifying = [], []
    for label, sign in (("2nd from the Moon", (moon + 1) % 12),
                        ("12th from the Moon", (moon - 1) % 12)):
        occupants = [p for p in ctx.planets_in_sign.get(sign, []) if p != pr.MOON]
        counts = [p for p in occupants if p not in excluded]
        qualifying += counts
        rows.append({"label": f"{label} ({pr.sign_name(sign)})",
                     "value": ", ".join(pr.planet_name(p) for p in occupants) or "empty"})

    present = not qualifying
    return _d("kemadruma", present, [pr.MOON] if present else [],
              ("Neither the sign before nor the sign after the Moon holds a "
               "graha that relieves the formation. The Sun and the nodes are "
               "not counted as relieving it."
               if present else
               f"{', '.join(pr.planet_name(p) for p in qualifying)} stands "
               f"beside the Moon, so the formation does not arise."),
              rows)


def _sakata(ctx: ChartContext) -> Dosha:
    """DOSHA_009. The Moon reckoned from Jupiter."""
    house = ctx.house_from(ctx.sign_of(pr.JUPITER), ctx.sign_of(pr.MOON))
    present = house in (6, 8, 12)
    return _d("sakata", present, [pr.MOON, pr.JUPITER] if present else [],
              f"The Moon stands in the {house}th sign counted from Jupiter."
              + (" The 6th, 8th and 12th carry the dosha." if present
                 else " The dosha needs the 6th, 8th or 12th."),
              [{"label": "Jupiter", "value": pr.sign_name(ctx.sign_of(pr.JUPITER))},
               {"label": "Moon", "value": pr.sign_name(ctx.sign_of(pr.MOON))},
               {"label": "Moon from Jupiter", "value": f"{house}th"}])


def _papakartari(ctx: ChartContext) -> Dosha:
    """DOSHA_010. Every graha caught between two malefics."""
    caught: List[Dict[str, str]] = []
    participants: List[int] = []
    for planet in pr.ALL_PLANETS:
        sign = ctx.sign_of(planet)
        before = [p for p in ctx.planets_in_sign.get((sign - 1) % 12, [])
                  if p in MALEFICS_FOR_HEMMING and p != planet]
        after = [p for p in ctx.planets_in_sign.get((sign + 1) % 12, [])
                 if p in MALEFICS_FOR_HEMMING and p != planet]
        if before and after:
            participants += [planet, before[0], after[0]]
            caught.append({
                "label": pr.planet_name(planet),
                "value": f"{pr.planet_name(before[0])} behind, "
                         f"{pr.planet_name(after[0])} ahead",
            })

    present = bool(caught)
    return _d("papakartari", present, sorted(set(participants)),
              (f"{', '.join(c['label'] for c in caught)} "
               f"{'stands' if len(caught) == 1 else 'stand'} with a natural "
               f"malefic in the sign on either side."
               if present else
               "No graha stands with a natural malefic in both the sign before "
               "and the sign after it."),
              caught)


def _kendradhipatya(ctx: ChartContext) -> Dosha:
    """DOSHA_011. A natural benefic lording a Kendra."""
    from .planet_findings import natural_nature_of

    caught, participants = [], []
    for planet in pr.SUN_TO_SATURN:
        owned = ctx.houses_owned.get(planet, [])
        kendras = [h for h in owned if h in (4, 7, 10)]
        if not kendras:
            continue
        if natural_nature_of(ctx, planet).nature != cr.BENEFIC:
            continue
        participants.append(planet)
        caught.append({"label": pr.planet_name(planet),
                       "value": f"lords the {cr._list(kendras)}"})

    present = bool(caught)
    return _d("kendradhipatya", present, participants,
              (f"{', '.join(c['label'] for c in caught)} "
               f"{'is a natural benefic lording' if len(caught) == 1 else 'are natural benefics lording'} "
               f"a Kendra, which costs the benefic its power to give freely."
               if present else
               "No natural benefic lords a Kendra in this chart."),
              caught)


def _daridra(ctx: ChartContext) -> Dosha:
    """DOSHA_012. The 11th lord in a Dusthana."""
    lord = ctx.house_lord[11]
    house = ctx.bhava_of(lord)
    present = house in (6, 8, 12)
    return _d("daridra", present, [lord] if present else [],
              f"The 11th house is {pr.sign_name(ctx.house_sign[11])}, lorded by "
              f"{pr.planet_name(lord)}, which stands in the {house}th house."
              + (" The 6th, 8th and 12th carry the dosha." if present else ""),
              [{"label": "11th lord", "value": pr.planet_name(lord)},
               {"label": "Placed in", "value": f"{house}th house"}])


def _amavasya(ctx: ChartContext) -> Dosha:
    """DOSHA_013. Born close to the new moon."""
    gap = separation(ctx.positions[pr.SUN].absolute_longitude,
                     ctx.positions[pr.MOON].absolute_longitude)
    present = gap <= 12.0
    return _d("amavasya", present, [pr.SUN, pr.MOON] if present else [],
              f"The Sun and the Moon stand {pr.to_dms(gap)} apart."
              + (" Within 12° the birth counts as falling near the new moon."
                 if present else " The dosha needs a gap of 12° or less."),
              [{"label": "Sun", "value": pr.to_dms(ctx.positions[pr.SUN].absolute_longitude)},
               {"label": "Moon", "value": pr.to_dms(ctx.positions[pr.MOON].absolute_longitude)},
               {"label": "Gap", "value": pr.to_dms(gap)}])


def _pitru(ctx: ChartContext) -> Dosha:
    """DOSHA_014. The 9th house or its lord afflicted."""
    ninth_sign = ctx.house_sign[9]
    nodes_in_ninth = [n for n in pr.NODES if ctx.sign_of(n) == ninth_sign]
    lord = ctx.house_lord[9]
    lord_house = ctx.bhava_of(lord)
    lord_in_dusthana = lord_house in (6, 8, 12)

    present = bool(nodes_in_ninth) or lord_in_dusthana
    participants = list(nodes_in_ninth) + ([lord] if lord_in_dusthana else [])

    reasons = []
    if nodes_in_ninth:
        reasons.append(f"{' and '.join(pr.planet_name(n) for n in nodes_in_ninth)} "
                       f"occupies the 9th house")
    if lord_in_dusthana:
        reasons.append(f"the 9th lord {pr.planet_name(lord)} stands in the "
                       f"{lord_house}th house")

    return _d("pitru", present, participants,
              ("The formation is present because " + " and ".join(reasons) + "."
               if present else
               f"The 9th house is {pr.sign_name(ninth_sign)}, holding neither "
               f"node, and its lord {pr.planet_name(lord)} stands in the "
               f"{lord_house}th house rather than a Dusthana."),
              [{"label": "9th house", "value": pr.sign_name(ninth_sign)},
               {"label": "9th lord", "value": pr.planet_name(lord)},
               {"label": "9th lord placed in", "value": f"{lord_house}th house"}])
