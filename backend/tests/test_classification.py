"""Benefic/malefic classification (RULES NATURE_001 .. NATURE_008)."""
import pytest

from app.astrology.planet_findings import build_findings, natural_nature_of
from app.astrology.rules import classification_rules as cr
from app.astrology.rules import planetary_rules as pr

from .conftest import make_context

# Libra Lagna, used because its functional classifications are well known.
LIBRA_CHART = (1994, 8, 14, 11, 45, 0, 26.72882, 85.92628, 5.75)

CHARTS = [
    LIBRA_CHART,
    (1990, 5, 15, 10, 30, 0, 13.0827, 80.2707, 5.5),
    (1975, 1, 3, 4, 15, 0, 51.5074, -0.1278, 0.0),
    (2001, 9, 20, 23, 45, 0, 40.7128, -74.0060, -4.0),
]

FIXED_CHECKS = [
    "nature-natural",
    "dignity-exalted", "dignity-debilitated", "dignity-own",
    "dignity-mooltrikona", "dignity-signlord", "dignity-vargottama",
    "house-placement",
    "lord-houses", "lord-functional", "lord-yogakaraka", "lord-badhaka",
    "lord-maraka",
    "rel-rashi-lord", "rel-nakshatra-lord", "rel-navamsha-lord", "rel-lagnesh",
    "state-retrograde", "state-combust", "state-war",
    "avastha-kumaradi", "avastha-chaitanyadi",
    "strength-shadbala", "special-neechabhanga",
]


GROUPS = ("favourable", "challenging", "yogas", "doshas", "neutral",
          "interpretive")


def all_items(findings):
    return [x for g in GROUPS for x in findings[g]]


def item(findings, key):
    return next(x for x in all_items(findings) if x["key"] == key)


# --- Natural nature (NATURE_001) -------------------------------------------
@pytest.mark.parametrize("planet", [pr.JUPITER, pr.VENUS])
def test_jupiter_and_venus_are_always_benefic(planet):
    assert cr.natural_nature(planet).nature == cr.BENEFIC


@pytest.mark.parametrize("planet", [pr.SUN, pr.MARS, pr.SATURN, pr.RAHU, pr.KETU])
def test_the_cruel_grahas_are_always_malefic(planet):
    assert cr.natural_nature(planet).nature == cr.MALEFIC


@pytest.mark.parametrize("elongation,expected", [
    (0.0, cr.MALEFIC),      # new moon, dark
    (71.9, cr.MALEFIC),
    (72.0, cr.BENEFIC),     # boundary
    (180.0, cr.BENEFIC),    # full moon
    (288.0, cr.BENEFIC),    # boundary
    (288.1, cr.MALEFIC),
    (350.0, cr.MALEFIC),
])
def test_moon_nature_follows_its_brightness(elongation, expected):
    assert cr.natural_nature(pr.MOON, moon_elongation=elongation).nature == expected


@pytest.mark.parametrize("companions,expected", [
    ([], cr.NEUTRAL),                      # alone
    ([pr.JUPITER], cr.BENEFIC),
    ([pr.VENUS], cr.BENEFIC),
    ([pr.SATURN], cr.MALEFIC),
    ([pr.SUN], cr.MALEFIC),
    ([pr.RAHU], cr.MALEFIC),
    ([pr.JUPITER, pr.SATURN], cr.NEUTRAL),  # both kinds of company
])
def test_mercury_takes_the_nature_of_its_company(companions, expected):
    assert cr.natural_nature(pr.MERCURY,
                             mercury_companions=companions).nature == expected


# --- House nature (NATURE_002, NATURE_003) ---------------------------------
@pytest.mark.parametrize("house", [1, 2, 4, 5, 7, 9, 10, 11])
def test_auspicious_houses(house):
    assert cr.HOUSE_NATURE[house] == cr.HOUSE_BENEFIC


@pytest.mark.parametrize("house", [6, 8, 12])
def test_dusthana_houses(house):
    assert cr.HOUSE_NATURE[house] == cr.HOUSE_MALEFIC


def test_third_house_is_mixed():
    assert cr.HOUSE_NATURE[3] == cr.HOUSE_MIXED


@pytest.mark.parametrize("house", [3, 6, 10, 11])
def test_malefics_are_grouped_favourably_in_upachaya(house):
    """A malefic grows strong in the Upachayas, including the 6th."""
    category, _ = cr.placement_category(house, cr.MALEFIC)
    assert category == cr.FAVOURABLE


@pytest.mark.parametrize("house", [8, 12])
def test_malefics_in_the_other_dusthanas_are_still_a_difficulty(house):
    category, _ = cr.placement_category(house, cr.MALEFIC)
    assert category == cr.CHALLENGING


@pytest.mark.parametrize("house", [6, 8, 12])
def test_benefics_in_dusthanas_are_a_difficulty(house):
    category, _ = cr.placement_category(house, cr.BENEFIC)
    assert category == cr.CHALLENGING


# --- Functional nature (NATURE_004) ----------------------------------------
def houses_owned(planet: int, lagna: int):
    return sorted(((s - lagna) % 12) + 1 for s in pr.owned_signs(planet))


ARIES, TAURUS, GEMINI, CANCER = 0, 1, 2, 3
LEO, VIRGO, LIBRA, SCORPIO = 4, 5, 6, 7
SAGITTARIUS, CAPRICORN, AQUARIUS, PISCES = 8, 9, 10, 11


@pytest.mark.parametrize("planet,lagna", [
    (pr.SATURN, LIBRA),      # owns 4th and 5th
    (pr.SATURN, TAURUS),     # owns 9th and 10th
    (pr.MARS, CANCER),       # owns 5th and 10th
    (pr.VENUS, CAPRICORN),   # owns 5th and 10th
    (pr.VENUS, AQUARIUS),    # owns 4th and 9th
])
def test_the_classical_yoga_karakas_are_functional_benefics(planet, lagna):
    owned = houses_owned(planet, lagna)
    nature = cr.natural_nature(planet).nature
    verdict, reasons = cr.functional_nature(owned, nature)
    assert verdict == cr.BENEFIC
    assert any("Yoga Karaka" in r for r in reasons)


def test_jupiter_is_a_functional_malefic_for_libra():
    """Jupiter lords the 3rd and 6th from Libra, both Trishadaya houses."""
    owned = houses_owned(pr.JUPITER, LIBRA)
    assert owned == [3, 6]
    verdict, _ = cr.functional_nature(owned, cr.BENEFIC)
    assert verdict == cr.MALEFIC


def test_venus_is_a_functional_benefic_for_libra_despite_the_eighth():
    """Venus lords the 1st and 8th; the Lagna lordship excuses the 8th."""
    owned = houses_owned(pr.VENUS, LIBRA)
    assert owned == [1, 8]
    verdict, reasons = cr.functional_nature(owned, cr.BENEFIC)
    assert verdict == cr.BENEFIC
    assert any("excused" in r for r in reasons)


def test_kendradhipatya_costs_a_benefic_its_benefic_power():
    """The Moon lords only the 10th from Libra, a Kendra."""
    owned = houses_owned(pr.MOON, LIBRA)
    assert owned == [10]
    verdict, reasons = cr.functional_nature(owned, cr.BENEFIC)
    assert verdict == cr.NEUTRAL
    assert any("Kendradhipatya" in r for r in reasons)


def test_kendradhipatya_turns_a_malefic_auspicious():
    """Mars lords the 2nd and 7th from Libra; the 7th is a Kendra."""
    owned = houses_owned(pr.MARS, LIBRA)
    assert owned == [2, 7]
    verdict, reasons = cr.functional_nature(owned, cr.MALEFIC)
    assert verdict == cr.BENEFIC
    assert any("Kendradhipatya" in r for r in reasons)


def test_trishadaya_lordship_is_a_functional_malefic():
    """The Sun lords only the 11th from Libra."""
    owned = houses_owned(pr.SUN, LIBRA)
    assert owned == [11]
    verdict, _ = cr.functional_nature(owned, cr.MALEFIC)
    assert verdict == cr.MALEFIC


def test_trikona_lordship_prevails_over_a_difficult_one():
    verdict, reasons = cr.functional_nature([5, 6], cr.BENEFIC)
    assert verdict == cr.BENEFIC
    assert any("prevail" in r for r in reasons)


def test_nodes_have_no_functional_nature():
    verdict, _ = cr.functional_nature([], cr.MALEFIC)
    assert verdict == cr.NOT_DEFINED


# --- Retrogression (NATURE_005) --------------------------------------------
def test_retrograde_malefic_is_grouped_favourably():
    category, _, _ = cr.retrograde_category(pr.SATURN, True, cr.MALEFIC)
    assert category == cr.FAVOURABLE


def test_retrograde_benefic_is_grouped_as_a_difficulty():
    category, _, _ = cr.retrograde_category(pr.JUPITER, True, cr.BENEFIC)
    assert category == cr.CHALLENGING


@pytest.mark.parametrize("planet", [pr.SUN, pr.MOON])
def test_luminaries_never_carry_a_retrograde_grouping(planet):
    category, text, _ = cr.retrograde_category(planet, False, cr.MALEFIC)
    assert category == cr.INDIFFERENT
    assert "does not apply" in text


@pytest.mark.parametrize("planet", [pr.RAHU, pr.KETU])
def test_nodes_carry_no_retrograde_distinction(planet):
    category, _, _ = cr.retrograde_category(planet, True, cr.MALEFIC)
    assert category == cr.INDIFFERENT


# --- The fixed catalogue (NATURE_007) --------------------------------------
@pytest.mark.parametrize("chart", CHARTS)
def test_every_planet_gets_every_fixed_check(chart):
    ctx = make_context(*chart)
    for planet in pr.ALL_PLANETS:
        keys = {x["key"] for x in all_items(build_findings(ctx, planet))}
        missing = [k for k in FIXED_CHECKS if k not in keys]
        assert not missing, f"{pr.PLANET_NAMES[planet]} missing {missing}"


@pytest.mark.parametrize("chart", CHARTS)
def test_every_bullet_is_in_exactly_one_group(chart):
    ctx = make_context(*chart)
    for planet in pr.ALL_PLANETS:
        f = build_findings(ctx, planet)
        keys = [x["key"] for x in all_items(f)]
        assert len(keys) == len(set(keys)), "a bullet appears twice"
        # Yogas are green and doshas red, so their bullets carry those
        # categories while living in their own lists.
        for group in ("favourable", "challenging", "neutral"):
            for x in f[group]:
                assert x["category"] == group
        for x in f["yogas"]:
            assert x["category"] == "favourable"
        for x in f["doshas"]:
            assert x["category"] == "challenging"
        for x in f["interpretive"]:
            assert x["openKind"] == cr.OPEN_INTERPRETIVE


@pytest.mark.parametrize("chart", CHARTS)
def test_checks_that_cannot_apply_land_in_neutral(chart):
    ctx = make_context(*chart)
    for planet in pr.NODES:
        f = build_findings(ctx, planet)
        for key in ("dignity-own", "dignity-mooltrikona", "lord-houses",
                    "lord-functional", "lord-yogakaraka", "lord-badhaka",
                    "lord-maraka", "state-combust", "state-war",
                    "strength-shadbala"):
            assert item(f, key)["category"] == "neutral", key


@pytest.mark.parametrize("chart", CHARTS)
def test_every_bullet_carries_text_and_an_explanation(chart):
    ctx = make_context(*chart)
    for planet in pr.ALL_PLANETS:
        for x in all_items(build_findings(ctx, planet)):
            assert x["text"].strip()
            assert len(x["explanation"].strip()) > 20, x["key"]


# --- Consistency between the bullets and the underlying facts --------------
@pytest.mark.parametrize("chart", CHARTS)
def test_dignity_bullets_match_the_dignity_engine(chart):
    """For the seven grahas exaltation is green and debilitation red. For the
    nodes both are yellow instead, because the classics do not fix their
    exaltation signs (RK_004, NATURE_009)."""
    from app.astrology.dignity_engine import dignity
    ctx = make_context(*chart)
    for planet in pr.ALL_PLANETS:
        f = build_findings(ctx, planet)
        d = dignity(ctx, planet)
        exalted = item(f, "dignity-exalted")
        debilitated = item(f, "dignity-debilitated")

        if planet in pr.NODES:
            if d["exalted"]:
                assert exalted["openKind"] == cr.OPEN_INTERPRETIVE
            if d["debilitated"]:
                assert debilitated["openKind"] == cr.OPEN_INTERPRETIVE
            continue

        assert (exalted["category"] == "favourable") is d["exalted"]
        assert (debilitated["category"] == "challenging") is d["debilitated"]


@pytest.mark.parametrize("chart", CHARTS)
def test_retrograde_bullet_matches_the_chart(chart):
    ctx = make_context(*chart)
    for planet in pr.ALL_PLANETS:
        f = build_findings(ctx, planet)
        text = item(f, "state-retrograde")["text"].lower()
        if planet in (pr.SUN, pr.MOON):
            assert "does not apply" in text
        elif planet in pr.NODES:
            assert "always" in text
        elif ctx.is_retrograde(planet):
            assert text.startswith("retrograde")
        else:
            assert text == "not retrograde"


@pytest.mark.parametrize("chart", CHARTS)
def test_no_aggregate_verdict_is_produced(chart):
    """RULE NATURE_008. Counts only, never a total or a rating."""
    ctx = make_context(*chart)
    for planet in pr.ALL_PLANETS:
        f = build_findings(ctx, planet)
        assert set(f) == set(GROUPS) | {"counts", "naturalNature", "note"}
        for g in GROUPS:
            assert f["counts"][g] == len(f[g])
        assert "score" not in f and "rating" not in f and "total" not in f


# --- The yellow group and its three kinds (NATURE_009) ---------------------
@pytest.mark.parametrize("chart", CHARTS)
def test_every_yellow_bullet_declares_why_it_is_yellow(chart):
    ctx = make_context(*chart)
    for planet in pr.ALL_PLANETS:
        f = build_findings(ctx, planet)
        for x in f["neutral"]:
            assert x["openKind"] in (cr.OPEN_NOT_APPLICABLE,
                                     cr.OPEN_NEUTRAL), x["key"]
            assert x["openLabel"], x["key"]
        for x in f["interpretive"]:
            assert x["openKind"] == cr.OPEN_INTERPRETIVE, x["key"]
        # Green and red bullets never carry an open kind.
        for group in ("favourable", "challenging", "yogas", "doshas"):
            for x in f[group]:
                assert x["openKind"] is None, x["key"]


@pytest.mark.parametrize("chart", CHARTS)
def test_interpretive_bullets_explain_the_disagreement(chart):
    ctx = make_context(*chart)
    for planet in pr.ALL_PLANETS:
        for x in build_findings(ctx, planet)["interpretive"]:
            prose = x["explanation"].lower()
            assert any(w in prose for w in
                       ("differ", "argued", "one view", "one tradition",
                        "not settle", "pull against", "yours to decide",
                        "another is", "many astrologers", "schools")), x["key"]


def test_node_exaltation_is_left_to_the_astrologer():
    """RK_004 says the classics do not fix it, so it must not be scored green."""
    ctx = make_context(*LIBRA_CHART)
    for node in pr.NODES:
        f = build_findings(ctx, node)
        for key in ("dignity-exalted", "dignity-debilitated"):
            bullet = item(f, key)
            if bullet["text"].startswith(("Exalted", "Debilitated")):
                assert bullet["category"] == "neutral"
                assert bullet["openKind"] == cr.OPEN_INTERPRETIVE


def test_conflicting_lordship_is_left_to_the_astrologer():
    """Mars for Libra lords the 7th, a Kendra, and both Maraka houses."""
    contested = cr.functional_contested([2, 7], cr.MALEFIC)
    assert contested == "maraka_and_kendra"
    assert cr.functional_contested([5, 6], cr.BENEFIC) == "mixed_lordship"
    # A clean lordship is not contested.
    assert cr.functional_contested([4, 5], cr.MALEFIC) is None
    assert cr.functional_contested([], cr.MALEFIC) is None


def test_mercury_combustion_is_left_to_the_astrologer():
    ctx = make_context(*CHARTS[1])
    f = build_findings(ctx, pr.MERCURY)
    bullet = item(f, "state-combust")
    if bullet["text"].startswith("Combust"):
        assert bullet["category"] == "neutral"
        assert bullet["openKind"] == cr.OPEN_INTERPRETIVE


@pytest.mark.parametrize("chart", CHARTS)
def test_association_with_a_node_is_left_to_the_astrologer(chart):
    ctx = make_context(*chart)
    for planet in pr.ALL_PLANETS:
        if planet in pr.NODES:
            continue
        for x in build_findings(ctx, planet)["interpretive"]:
            if x["key"] in ("company-conj-7", "company-conj-8",
                            "company-asp-7", "company-asp-8"):
                assert x["openKind"] == cr.OPEN_INTERPRETIVE


@pytest.mark.parametrize("chart", CHARTS)
def test_not_applicable_is_kept_apart_from_your_call(chart):
    """The two must never be conflated: one is structural, one is a judgement."""
    ctx = make_context(*chart)
    for node in pr.NODES:
        f = build_findings(ctx, node)
        assert item(f, "strength-shadbala")["openKind"] == cr.OPEN_NOT_APPLICABLE
        assert item(f, "lord-houses")["openKind"] == cr.OPEN_NOT_APPLICABLE
