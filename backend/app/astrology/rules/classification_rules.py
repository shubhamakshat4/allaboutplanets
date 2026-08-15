"""Benefic / malefic classification (RULES NATURE_001 .. NATURE_008).

Three separate questions, kept apart because the classics keep them apart:

1. **Natural nature** (Naisargika) — what a graha is in itself, in every chart.
2. **House nature** — whether a bhava is counted auspicious or difficult.
3. **Functional nature** — what a graha becomes for one particular Lagna,
   decided by the houses it lords.

A planet can be a natural benefic and a functional malefic at once. Jupiter for
a Libra Lagna lords the 3rd and the 6th and is a functional malefic, while
remaining the greatest natural benefic. Both facts are reported.
"""
from __future__ import annotations

from typing import Dict, List, NamedTuple, Optional, Tuple

from .planetary_rules import (
    JUPITER, KETU, MARS, MERCURY, MOON, NODES, RAHU, SATURN, SUN, VENUS,
    planet_name,
)

# --- Verdict vocabulary ----------------------------------------------------
BENEFIC = "Benefic"
MALEFIC = "Malefic"
NEUTRAL = "Neutral"
NOT_DEFINED = "Not defined by lordship"

# --- The three finding groups ---------------------------------------------
FAVOURABLE = "favourable"      # green
CHALLENGING = "challenging"    # red
INDIFFERENT = "neutral"        # yellow

# Why a bullet sits in the yellow group. The distinction matters: a check that
# structurally cannot apply is a very different thing from one the classics
# genuinely disagree about, and the astrologer should be able to tell them
# apart at a glance.
OPEN_NOT_APPLICABLE = "not_applicable"
OPEN_NEUTRAL = "neutral"
OPEN_INTERPRETIVE = "interpretive"

OPEN_LABELS = {
    OPEN_NOT_APPLICABLE: "Does not apply",
    OPEN_NEUTRAL: "Neutral",
    OPEN_INTERPRETIVE: "Your call",
}

# --- Situations the classics do not settle (RULE NATURE_009) ---------------
# Each entry is a reason shown on the bullet, so the astrologer knows exactly
# what is being left to them and why.
CONTESTED = {
    "node_dignity": (
        "The classics do not place Rahu and Ketu in the exaltation table. The "
        "sign used here is one tradition among several: some give Rahu "
        "exaltation in Taurus alone, others in Gemini, with Ketu placed "
        "correspondingly. Whether to read this as a strength is yours to "
        "decide."),
    "mixed_lordship": (
        "This graha holds lordships that pull in opposite directions. The rule "
        "followed here lets the Trikona lordship prevail, but many astrologers "
        "weigh the difficult lordship more heavily, and the Kendradhipatya "
        "treatment of a Kendra lord is itself read differently by different "
        "schools."),
    "maraka_and_kendra": (
        "This graha lords a Kendra, which turns a natural malefic auspicious "
        "by Kendradhipatya, and also a Maraka house. The two pull against each "
        "other and the classics do not settle which prevails."),
    "mercury_combustion": (
        "Mercury never travels far from the Sun and is combust in a great many "
        "charts. Many astrologers hold Mercury's combustion to be far less "
        "telling than that of the other grahas, especially where Budha-Aditya "
        "is formed."),
    "node_association": (
        "Rahu and Ketu are widely held to take on the character of the graha "
        "they join, of their dispositor, or of the house they occupy. Reading "
        "an association with a node purely as a difficulty is only one view."),
    "partial_neecha_bhanga": (
        "Some of the cancelling conditions are met and some are not. How far a "
        "partial Neecha Bhanga lifts the debilitation is one of the most "
        "argued points in the classics, and the count alone does not settle "
        "it."),
    "vargottama_debilitated": (
        "The graha is Vargottama while debilitated. One reading is that "
        "Vargottama steadies it; another is that holding the same sign in both "
        "charts deepens the debilitation."),
    "retrograde_school": (
        "Schools differ on retrogression. Some hold that a retrograde graha is "
        "simply strengthened, some that it gives the results of the previous "
        "sign, and some that it acts contrary to its usual nature."),
}


# ===========================================================================
# 1. NATURAL NATURE  (RULE NATURE_001)
# ===========================================================================
# BPHS: the Sun, Mars, Saturn, Rahu, Ketu and the waning Moon are papa grahas.
# Jupiter, Venus, the waxing Moon and an unafflicted Mercury are shubha grahas.
# The Moon and Mercury are therefore conditional and resolved per chart.
ALWAYS_BENEFIC = (JUPITER, VENUS)
ALWAYS_MALEFIC = (SUN, MARS, SATURN, RAHU, KETU)
CONDITIONAL = (MOON, MERCURY)

# The Moon counts as bright, and so benefic, between these elongations.
MOON_BRIGHT_FROM = 72.0
MOON_BRIGHT_TO = 288.0


class NatureVerdict(NamedTuple):
    nature: str
    reason: str


def natural_nature(planet: int, *, moon_elongation: Optional[float] = None,
                   mercury_companions: Optional[List[int]] = None
                   ) -> NatureVerdict:
    """RULE NATURE_001. Natural benefic, malefic or neutral."""
    if planet in ALWAYS_BENEFIC:
        return NatureVerdict(
            BENEFIC, f"{planet_name(planet)} is a natural benefic in every chart.")

    if planet == SUN:
        return NatureVerdict(
            MALEFIC,
            "The Sun is counted among the cruel grahas, though it is a mild "
            "malefic rather than a harsh one.")

    if planet in (MARS, SATURN):
        return NatureVerdict(
            MALEFIC, f"{planet_name(planet)} is a natural malefic in every chart.")

    if planet in NODES:
        return NatureVerdict(
            MALEFIC, f"{planet_name(planet)} is counted a natural malefic.")

    if planet == MOON:
        if moon_elongation is None:
            return NatureVerdict(NEUTRAL, "The Moon's phase is not known.")
        bright = MOON_BRIGHT_FROM <= moon_elongation <= MOON_BRIGHT_TO
        return NatureVerdict(
            BENEFIC if bright else MALEFIC,
            f"The Moon stands {moon_elongation:.1f}° from the Sun. A Moon "
            f"between {MOON_BRIGHT_FROM:g}° and {MOON_BRIGHT_TO:g}° is bright "
            f"and counted benefic; nearer the Sun than that it is dark and "
            f"counted malefic.")

    if planet == MERCURY:
        companions = mercury_companions or []
        if not companions:
            return NatureVerdict(
                NEUTRAL,
                "Mercury sits alone, and alone it is neutral. It takes the "
                "nature of whatever it joins.")
        malefics = [p for p in companions if p in ALWAYS_MALEFIC]
        benefics = [p for p in companions if p in ALWAYS_BENEFIC]
        if malefics and not benefics:
            return NatureVerdict(
                MALEFIC,
                "Mercury takes the nature of its company, and it shares its "
                f"sign with {_names(malefics)}.")
        if benefics and not malefics:
            return NatureVerdict(
                BENEFIC,
                "Mercury takes the nature of its company, and it shares its "
                f"sign with {_names(benefics)}.")
        return NatureVerdict(
            NEUTRAL,
            "Mercury shares its sign with both benefic and malefic company, "
            "so it is left neutral.")

    return NatureVerdict(NEUTRAL, "Not classified.")


# ===========================================================================
# 2. HOUSE NATURE  (RULE NATURE_002)
# ===========================================================================
TRIKONA = (1, 5, 9)
KENDRA = (1, 4, 7, 10)
UPACHAYA = (3, 6, 10, 11)
DUSTHANA = (6, 8, 12)
MARAKA = (2, 7)
TRISHADAYA = (3, 6, 11)

HOUSE_BENEFIC = "Auspicious"
HOUSE_MALEFIC = "Difficult"
HOUSE_MIXED = "Mixed"

# 1, 5, 9 are the trikonas; 4, 7, 10 the kendras; 2 and 11 the houses of
# wealth. 6, 8 and 12 are the trik or dusthana houses. The 3rd is an upachaya
# but counted among the mildly difficult houses.
HOUSE_NATURE: Dict[int, str] = {
    1: HOUSE_BENEFIC, 2: HOUSE_BENEFIC, 3: HOUSE_MIXED, 4: HOUSE_BENEFIC,
    5: HOUSE_BENEFIC, 6: HOUSE_MALEFIC, 7: HOUSE_BENEFIC, 8: HOUSE_MALEFIC,
    9: HOUSE_BENEFIC, 10: HOUSE_BENEFIC, 11: HOUSE_BENEFIC, 12: HOUSE_MALEFIC,
}


def house_groups(house: int) -> List[str]:
    groups = []
    if house in KENDRA:
        groups.append("Kendra")
    if house in TRIKONA:
        groups.append("Trikona")
    if house in DUSTHANA:
        groups.append("Dusthana")
    if house in UPACHAYA:
        groups.append("Upachaya")
    if house in MARAKA:
        groups.append("Maraka")
    return groups


def placement_category(house: int, planet_nature: str) -> Tuple[str, str]:
    """RULE NATURE_003. How a planet's house placement is grouped.

    Malefics are held to do well in the upachaya houses, which they grow
    stronger in, so a malefic in the 3rd, 6th or 11th is not counted a
    difficulty even though the 3rd and 6th are otherwise unwelcome.
    """
    nature = HOUSE_NATURE[house]
    groups = house_groups(house)
    named = ", ".join(groups) if groups else "no special group"

    if house in UPACHAYA and planet_nature == MALEFIC:
        return FAVOURABLE, (
            f"The {_ord(house)} is an Upachaya house ({named}). A natural "
            f"malefic is held to grow strong in the Upachayas.")

    if nature == HOUSE_MALEFIC:
        return CHALLENGING, (
            f"The {_ord(house)} is a Dusthana ({named}), among the difficult "
            f"houses of the chart.")

    if nature == HOUSE_MIXED:
        return INDIFFERENT, (
            f"The {_ord(house)} is an Upachaya but is counted mildly "
            f"difficult ({named}).")

    return FAVOURABLE, (
        f"The {_ord(house)} is counted an auspicious house ({named}).")


# ===========================================================================
# 3. FUNCTIONAL NATURE  (RULE NATURE_004)
# ===========================================================================
# Following the Parashari treatment of lordship:
#
#   * The Lagna lord is auspicious, the 1st being both kendra and trikona.
#   * Lords of the 5th and 9th, the trikonas, are auspicious.
#   * Lords of the 3rd, 6th and 11th, the trishadaya, are inauspicious.
#   * The 8th lord is inauspicious unless it also lords the Lagna.
#   * Lords of the 2nd and 12th are neutral in themselves.
#   * Kendradhipatya: a natural benefic lording a kendra (4th, 7th, 10th)
#     loses its benefic power, while a natural malefic doing so becomes
#     auspicious.
#   * A planet lording both a kendra and a trikona is a Yoga Karaka.
#   * Where a planet lords both a trikona and a difficult house, the trikona
#     lordship prevails.
def functional_nature(houses_owned: List[int], planet_nature: str
                      ) -> Tuple[str, List[str]]:
    """RULE NATURE_004. Returns (verdict, the reasons behind it)."""
    if not houses_owned:
        return NOT_DEFINED, [
            "This body lords no sign, so it holds no house lordship and takes "
            "no functional nature from one."]

    reasons: List[str] = []
    owned = sorted(houses_owned)

    lagna_lord = 1 in owned
    trikona = [h for h in owned if h in (5, 9)]
    kendra = [h for h in owned if h in (4, 7, 10)]
    trishadaya = [h for h in owned if h in TRISHADAYA]
    eighth = 8 in owned
    quiet = [h for h in owned if h in (2, 12)]

    if lagna_lord:
        reasons.append("Lords the 1st, which is both a Kendra and a Trikona, "
                       "so it is counted auspicious.")
    if trikona:
        reasons.append(
            f"Lords the {_list(trikona)}, a Trikona, which is auspicious.")
    if trishadaya:
        reasons.append(
            f"Lords the {_list(trishadaya)}, among the Trishadaya houses "
            f"(3rd, 6th, 11th), which is inauspicious.")
    if eighth:
        if lagna_lord:
            reasons.append("Lords the 8th, but is excused because it also "
                           "lords the Lagna.")
        else:
            reasons.append("Lords the 8th, which is inauspicious.")
    if quiet:
        reasons.append(
            f"Lords the {_list(quiet)}, which is neutral in itself and takes "
            f"its colour from association.")

    yoga_karaka = bool(kendra) and (bool(trikona) or lagna_lord)
    if yoga_karaka:
        reasons.append(
            f"Lords both a Kendra ({_list(kendra)}) and a Trikona, making it "
            f"a Yoga Karaka.")
        return BENEFIC, reasons

    if kendra:
        if planet_nature == BENEFIC:
            reasons.append(
                f"Lords the {_list(kendra)}, a Kendra. By Kendradhipatya a "
                f"natural benefic lording a kendra loses its benefic power.")
        elif planet_nature == MALEFIC:
            reasons.append(
                f"Lords the {_list(kendra)}, a Kendra. By Kendradhipatya a "
                f"natural malefic lording a kendra turns auspicious.")
        else:
            reasons.append(f"Lords the {_list(kendra)}, a Kendra.")

    # The trikona lordship outweighs a difficult one held at the same time.
    auspicious = lagna_lord or bool(trikona)
    inauspicious = bool(trishadaya) or (eighth and not lagna_lord)

    if auspicious and not inauspicious:
        return BENEFIC, reasons
    if auspicious and inauspicious:
        reasons.append("Holding both an auspicious and an inauspicious "
                       "lordship, the Trikona lordship is taken to prevail.")
        return BENEFIC, reasons
    if inauspicious:
        return MALEFIC, reasons

    if kendra:
        if planet_nature == MALEFIC:
            return BENEFIC, reasons
        if planet_nature == BENEFIC:
            return NEUTRAL, reasons
        return NEUTRAL, reasons

    return NEUTRAL, reasons or ["Lords only houses that are neutral in themselves."]


def functional_contested(houses_owned: List[int], planet_nature: str
                         ) -> Optional[str]:
    """RULE NATURE_009. Is this lordship one the classics leave open?

    Returns the key of the contested situation, or None when the lordship
    points clearly one way.
    """
    if not houses_owned:
        return None

    owned = set(houses_owned)
    auspicious = bool(owned & {1, 5, 9})
    inauspicious = bool(owned & set(TRISHADAYA)) or (8 in owned and 1 not in owned)
    kendra = bool(owned & {4, 7, 10})
    maraka = bool(owned & set(MARAKA))

    if auspicious and inauspicious:
        return "mixed_lordship"
    if kendra and maraka and planet_nature == MALEFIC:
        return "maraka_and_kendra"
    return None


# ===========================================================================
# 4. RETROGRESSION  (RULE NATURE_005)
# ===========================================================================
# A retrograde graha is close to the earth and gains cheshta bala. The
# formulation followed here is the common one: retrogression in a natural
# malefic is taken favourably, while a natural benefic turning retrograde is
# taken as the less welcome case. The Sun and Moon never retrograde, and the
# nodes always do, so neither carries the distinction.
def retrograde_category(planet: int, is_retrograde: bool, planet_nature: str
                        ) -> Tuple[str, str, str]:
    """RULE NATURE_005. Returns (category, short text, explanation)."""
    name = planet_name(planet)

    if planet in (SUN, MOON):
        return INDIFFERENT, "Retrograde: does not apply", (
            f"The {name} never turns retrograde, so the question does not "
            f"arise.")

    if planet in NODES:
        return INDIFFERENT, "Retrograde: always, by nature", (
            f"{name} moves backwards through the zodiac at all times, so its "
            f"retrogression sets it apart from nothing.")

    if not is_retrograde:
        if planet_nature == MALEFIC:
            return INDIFFERENT, "Not retrograde", (
                f"{name} is in direct motion. A natural malefic gains from "
                f"retrogression under the rule followed here, so direct "
                f"motion is simply the ordinary case.")
        return FAVOURABLE, "Not retrograde", (
            f"{name} is in direct motion. A natural benefic is held to give "
            f"its results most readily when moving direct.")

    if planet_nature == MALEFIC:
        return FAVOURABLE, "Retrograde (vakri)", (
            f"{name} is retrograde. A retrograde graha stands near the earth "
            f"and gains cheshta bala, and retrogression in a natural malefic "
            f"is taken favourably.")

    if planet_nature == BENEFIC:
        return CHALLENGING, "Retrograde (vakri)", (
            f"{name} is retrograde. Though a retrograde graha gains cheshta "
            f"bala, retrogression in a natural benefic is taken as the less "
            f"welcome case.")

    return INDIFFERENT, "Retrograde (vakri)", (
        f"{name} is retrograde. Its natural nature is neutral here, so the "
        f"retrogression is not placed either way.")


# ===========================================================================
# helpers
# ===========================================================================
def _ord(n: int) -> str:
    if 10 <= n % 100 <= 20:
        return f"{n}th"
    return f"{n}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th') }".replace(" ", "")


def _list(houses: List[int]) -> str:
    parts = [_ord(h) for h in houses]
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + " and " + parts[-1]


def _names(planets: List[int]) -> str:
    parts = [planet_name(p) for p in planets]
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + " and " + parts[-1]
