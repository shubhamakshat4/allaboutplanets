"""Yoga detection tests (RULES YOGA_001 .. YOGA_022)."""
import pytest

from app.astrology import yoga_engine
from app.astrology.rules import planetary_rules as pr
from app.astrology.rules import yoga_rules as yr

from .conftest import make_context

CHARTS = [
    (1990, 5, 15, 10, 30, 13.0827, 80.2707, 5.5),
    (1975, 1, 3, 4, 15, 51.5074, -0.1278, 0.0),
    (2001, 9, 20, 23, 45, 40.7128, -74.0060, -4.0),
    (1962, 11, 30, 6, 5, -33.8688, 151.2093, 10.0),
    (2015, 6, 21, 12, 0, 28.6139, 77.2090, 5.5),
    (1983, 3, 8, 18, 20, 19.0760, 72.8777, 5.5),
]


def test_all_twenty_two_yogas_are_evaluated(yogas):
    assert len(yogas) == 22
    assert len(yr.YOGA_SPECS) == 22
    keys = [y["key"] for y in yogas]
    assert keys == [s.key for s in yr.YOGA_SPECS]


def test_every_yoga_carries_rule_and_conditions(yogas):
    for y in yogas:
        assert y["ruleId"].startswith("YOGA_")
        assert y["name"]
        assert y["summary"]
        assert y["conditions"], y["name"]
        for c in y["conditions"]:
            assert c["title"]
            assert c["evidence"], f"{y['name']} / {c['title']}"
            assert c["status"] in ("Satisfied", "Not satisfied", pr.NOT_DEFINED)
        assert y["status"] in ("Present", "Not Present", pr.NOT_APPLICABLE)
        assert y["sources"]["rule"] == y["ruleId"]


def test_present_yogas_have_all_conditions_satisfied(yogas):
    """A yoga reported Present must not carry an unsatisfied condition, except
    the aggregate yogas that report per-instance results."""
    # These report per-instance or per-group results, so a Present verdict does
    # not imply every listed condition is satisfied.
    aggregate = {"raja_yoga", "dhana", "parivartana", "neecha_bhanga_raja_yoga",
                 "adhi", "amala", "gaja_kesari"}
    for y in yogas:
        if y["key"] in aggregate or not y["present"]:
            continue
        for c in y["conditions"]:
            assert c["satisfied"] is True, f"{y['name']} / {c['title']}"


def test_absent_yogas_have_a_failing_condition(yogas):
    aggregate = {"neecha_bhanga_raja_yoga"}
    for y in yogas:
        if y["present"] or y["key"] in aggregate:
            continue
        assert any(c["satisfied"] is not True for c in y["conditions"]), y["name"]


# --- Panchamahapurusha -----------------------------------------------------
@pytest.mark.parametrize("key", ["ruchaka", "bhadra", "hamsa", "malavya", "sasa"])
@pytest.mark.parametrize("chart", CHARTS)
def test_mahapurusha_requires_sign_and_kendra(key, chart):
    ctx = make_context(*chart[:5], 0, *chart[5:])
    yogas = {y["key"]: y for y in yoga_engine.evaluate_all_yogas(ctx)}
    y = yogas[key]
    cfg = yr.MAHAPURUSHA[key]
    planet = cfg["planet"]

    expected = (ctx.sign_of(planet) in cfg["signs"]
                and ctx.bhava_of(planet) in pr.KENDRA_HOUSES)
    assert y["present"] is expected
    assert len(y["conditions"]) == 2


def test_mahapurusha_sign_sets_match_the_specification():
    assert yr.MAHAPURUSHA["ruchaka"]["signs"] == [0, 7, 9]      # Aries, Scorpio, Capricorn
    assert yr.MAHAPURUSHA["bhadra"]["signs"] == [2, 5]          # Gemini, Virgo
    assert yr.MAHAPURUSHA["hamsa"]["signs"] == [8, 11, 3]       # Sag, Pisces, Cancer
    assert yr.MAHAPURUSHA["malavya"]["signs"] == [1, 6, 11]     # Taurus, Libra, Pisces
    assert yr.MAHAPURUSHA["sasa"]["signs"] == [9, 10, 6]        # Cap, Aquarius, Libra


# --- Same-Rashi yogas ------------------------------------------------------
@pytest.mark.parametrize("chart", CHARTS)
def test_same_rashi_yogas(chart):
    ctx = make_context(*chart[:5], 0, *chart[5:])
    yogas = {y["key"]: y for y in yoga_engine.evaluate_all_yogas(ctx)}

    assert yogas["budha_aditya"]["present"] is (
        ctx.sign_of(pr.SUN) == ctx.sign_of(pr.MERCURY))
    assert yogas["chandra_mangala"]["present"] is (
        ctx.sign_of(pr.MOON) == ctx.sign_of(pr.MARS))
    assert yogas["guru_mangala"]["present"] is (
        ctx.sign_of(pr.JUPITER) == ctx.sign_of(pr.MARS))


def test_budha_aditya_keeps_combustion_separate(yogas):
    y = next(y for y in yogas if y["key"] == "budha_aditya")
    assert "mercuryCombust" in y
    assert "combustionNote" in y
    # Combustion must never appear as a condition of the yoga.
    for c in y["conditions"]:
        assert "combust" not in c["title"].lower()


# --- Viparita family -------------------------------------------------------
@pytest.mark.parametrize("key,house", [("harsha", 6), ("sarala", 8), ("vimala", 12)])
@pytest.mark.parametrize("chart", CHARTS)
def test_viparita_yogas(key, house, chart):
    ctx = make_context(*chart[:5], 0, *chart[5:])
    yogas = {y["key"]: y for y in yoga_engine.evaluate_all_yogas(ctx)}
    lord = ctx.house_lord[house]
    expected = ctx.bhava_of(lord) in (6, 8, 12)
    assert yogas[key]["present"] is expected
    assert yogas[key]["lordOfHouse"] == house


# --- Kemadruma -------------------------------------------------------------
@pytest.mark.parametrize("chart", CHARTS)
def test_kemadruma(chart):
    ctx = make_context(*chart[:5], 0, *chart[5:])
    y = {x["key"]: x for x in yoga_engine.evaluate_all_yogas(ctx)}["kemadruma"]

    moon_sign = ctx.sign_of(pr.MOON)
    second = (moon_sign + 1) % 12
    twelfth = (moon_sign - 1) % 12
    qualifying = [p for s in (second, twelfth)
                  for p in ctx.planets_in_sign.get(s, [])
                  if p != pr.MOON and p not in yr.KEMADRUMA_EXCLUDED_PLANETS]

    assert y["present"] is (not qualifying)
    assert y["secondFromMoon"]["sign"] == second
    assert y["twelfthFromMoon"]["sign"] == twelfth
    assert y["exclusionNote"]


# --- Parivartana -----------------------------------------------------------
@pytest.mark.parametrize("chart", CHARTS)
def test_parivartana_is_a_true_exchange(chart):
    ctx = make_context(*chart[:5], 0, *chart[5:])
    y = {x["key"]: x for x in yoga_engine.evaluate_all_yogas(ctx)}["parivartana"]
    for inst in y["instances"]:
        a, b = inst["planetA"], inst["planetB"]
        assert ctx.lord_of_sign(ctx.sign_of(a)) == b
        assert ctx.lord_of_sign(ctx.sign_of(b)) == a


def test_parivartana_does_not_subclassify(yogas):
    y = next(y for y in yogas if y["key"] == "parivartana")
    text = str(y).lower()
    for word in ("maha yoga", "khala", "dainya"):
        assert word not in text.replace("maha / khala / dainya", "")


# --- Raja Yoga -------------------------------------------------------------
@pytest.mark.parametrize("chart", CHARTS)
def test_raja_yoga_participants_are_lords(chart):
    ctx = make_context(*chart[:5], 0, *chart[5:])
    y = {x["key"]: x for x in yoga_engine.evaluate_all_yogas(ctx)}["raja_yoga"]
    kendra_lords = {ctx.house_lord[h] for h in (1, 4, 7, 10)}
    trikona_lords = {ctx.house_lord[h] for h in (1, 5, 9)}
    for inst in y["instances"]:
        assert inst["kendraLord"] in kendra_lords
        assert inst["trikonaLord"] in trikona_lords
        assert inst["associationType"] in (
            yr.ASSOC_CONJUNCTION, yr.ASSOC_MUTUAL_DRISHTI, yr.ASSOC_PARIVARTANA)
        assert inst["associationEvidence"]
        assert inst["relationship"]["panchadhaMaitri"]


# --- Dhana -----------------------------------------------------------------
@pytest.mark.parametrize("chart", CHARTS)
def test_dhana_requires_second_or_eleventh_lord(chart):
    ctx = make_context(*chart[:5], 0, *chart[5:])
    y = {x["key"]: x for x in yoga_engine.evaluate_all_yogas(ctx)}["dhana"]
    l2, l11 = ctx.house_lord[2], ctx.house_lord[11]
    for inst in y["instances"]:
        assert l2 in inst["participants"] or l11 in inst["participants"]


# --- Gaja Kesari -----------------------------------------------------------
def test_gaja_kesari_separates_core_from_strengthening_conditions(yogas):
    y = next(y for y in yogas if y["key"] == "gaja_kesari")
    assert len(y["conditions"]) == 5

    core = [c for c in y["conditions"] if c.get("group") == yr.GROUP_CORE]
    strengthening = [c for c in y["conditions"]
                     if c.get("group") == yr.GROUP_STRENGTHENING]
    assert len(core) == 1
    assert len(strengthening) == 4

    # Status follows the core formation alone.
    assert y["present"] is core[0]["satisfied"]
    assert y["coreFormation"] is core[0]["satisfied"]
    assert y["strengtheningConditionsTotal"] == 4
    assert y["strengtheningConditionsSatisfied"] == sum(
        1 for c in strengthening if c["satisfied"])
    assert y["allConditionsSatisfied"] is all(
        c["satisfied"] for c in y["conditions"])


@pytest.mark.parametrize("chart", CHARTS)
def test_gaja_kesari_core_is_kendra_from_lagna_or_moon(chart):
    ctx = make_context(*chart[:5], 0, *chart[5:])
    y = {x["key"]: x for x in yoga_engine.evaluate_all_yogas(ctx)}["gaja_kesari"]
    from_lagna = ctx.house_from(ctx.lagna_sign, ctx.sign_of(pr.JUPITER))
    from_moon = ctx.house_from(ctx.sign_of(pr.MOON), ctx.sign_of(pr.JUPITER))
    expected = from_lagna in pr.KENDRA_HOUSES or from_moon in pr.KENDRA_HOUSES
    assert y["present"] is expected


def test_moon_jupiter_conjunction_forms_gaja_kesari_even_in_an_enemy_sign():
    """Janakpur, Nepal — 14 Aug 1994, 11:45 local.

    Moon and Jupiter are conjunct in Libra, which is Jupiter's enemy sign
    (Venus-ruled). A conjunction is the 1st from the Moon, hence a Kendra, so
    the core formation holds. The enemy-sign fact is reported as a
    strengthening condition rather than suppressing the formation.
    """
    ctx = make_context(1994, 8, 14, 11, 45, 0, 26.72882, 85.92628, 5.75)
    assert ctx.sign_of(pr.MOON) == ctx.sign_of(pr.JUPITER)

    y = {x["key"]: x for x in yoga_engine.evaluate_all_yogas(ctx)}["gaja_kesari"]
    assert y["present"] is True
    assert y["status"] == "Present"
    assert y["coreFormation"] is True

    # The enemy-sign condition still fails, and is still visible.
    enemy = next(c for c in y["conditions"] if "enemy" in c["title"].lower())
    assert enemy["satisfied"] is False
    assert enemy["group"] == yr.GROUP_STRENGTHENING
    assert y["strengtheningConditionsSatisfied"] == 3
    assert y["allConditionsSatisfied"] is False


# --- Yoga participation ----------------------------------------------------
def test_participation_only_lists_relevant_yogas(ctx, yogas):
    for planet in pr.ALL_PLANETS:
        rows = yoga_engine.yoga_participation(ctx, planet, yogas)
        for row in rows:
            assert row["role"]
            assert row["status"] in ("Present", "Not Present", pr.NOT_APPLICABLE)
            assert row["conditions"]
            assert planet not in [o["planet"] for o in row["otherParticipants"]]


def test_participation_matches_the_full_yoga_list(ctx, yogas):
    """A planet must appear in a yoga's participation list exactly when it is
    named as a participant or appears in one of its instances."""
    for planet in pr.ALL_PLANETS:
        listed = {r["key"] for r in yoga_engine.yoga_participation(ctx, planet, yogas)}
        for y in yogas:
            named = any(p["planet"] == planet for p in y["participants"])
            in_instance = any(planet in i.get("participants", [])
                              for i in y.get("instances", []))
            assert (y["key"] in listed) is (named or in_instance), \
                f"{pr.planet_name(planet)} / {y['name']}"


def test_mahapurusha_participation_is_limited_to_its_planet(ctx, yogas):
    for key, cfg in yr.MAHAPURUSHA.items():
        for planet in pr.ALL_PLANETS:
            rows = {r["key"] for r in yoga_engine.yoga_participation(ctx, planet, yogas)}
            assert (key in rows) is (planet == cfg["planet"])


# --- No interpretation -----------------------------------------------------
FORBIDDEN = [
    "will bring", "will give", "will cause", "favourable", "favorable",
    "unfavourable", "unfavorable", "auspicious", "inauspicious", "lucky",
    "powerful yoga", "very strong", "beneficial for", "harmful", "success",
    "wealth will", "prosperity", "misfortune", "should avoid", "advis",
]


@pytest.mark.parametrize("chart", CHARTS)
def test_yoga_output_contains_no_interpretation(chart):
    ctx = make_context(*chart[:5], 0, *chart[5:])
    text = str(yoga_engine.evaluate_all_yogas(ctx)).lower()
    for phrase in FORBIDDEN:
        assert phrase not in text, f"Interpretive phrase found: {phrase}"
