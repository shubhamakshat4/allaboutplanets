"""The curated dosha set (RULES DOSHA_001 .. DOSHA_014, DOSHA_100)."""
import pytest

from app.astrology import dosha_engine as de
from app.astrology.conjunction_engine import separation
from app.astrology.planet_findings import build_findings, natural_nature_of
from app.astrology.rules import classification_rules as cr
from app.astrology.rules import planetary_rules as pr

from .conftest import make_context

CHARTS = [
    (1994, 8, 14, 11, 45, 0, 26.72882, 85.92628, 5.75),   # Libra Lagna
    (1990, 5, 15, 10, 30, 0, 13.0827, 80.2707, 5.5),
    (1975, 1, 3, 4, 15, 0, 51.5074, -0.1278, 0.0),
    (2001, 9, 20, 23, 45, 0, 40.7128, -74.0060, -4.0),
    (1985, 10, 12, 7, 20, 0, 28.6139, 77.2090, 5.5),
]

GROUPS = ("favourable", "challenging", "yogas", "doshas", "neutral",
          "interpretive")


def by_key(doshas):
    return {d["key"]: d for d in doshas}


# --- Shape -----------------------------------------------------------------
def test_every_dosha_is_evaluated():
    ctx = make_context(*CHARTS[0])
    doshas = de.evaluate_all_doshas(ctx)
    assert len(doshas) == len(de.DOSHA_SPECS) == 14
    assert [d["key"] for d in doshas] == [s.key for s in de.DOSHA_SPECS]


@pytest.mark.parametrize("chart", CHARTS)
def test_every_dosha_carries_its_evidence(chart):
    ctx = make_context(*chart)
    for d in de.evaluate_all_doshas(ctx):
        assert d["ruleId"].startswith("DOSHA_")
        assert d["name"] and d["formation"]
        assert len(d["evidence"]) > 20, d["key"]
        assert isinstance(d["present"], bool)
        if d["present"]:
            assert d["participants"], d["key"]
        else:
            assert d["participants"] == []


# --- Conjunction-based doshas ----------------------------------------------
@pytest.mark.parametrize("chart", CHARTS)
@pytest.mark.parametrize("key,a,others", [
    ("guru_chandal", pr.JUPITER, (pr.RAHU, pr.KETU)),
    ("angarak", pr.MARS, (pr.RAHU, pr.KETU)),
    ("shrapit", pr.SATURN, (pr.RAHU,)),
    ("vish", pr.MOON, (pr.SATURN,)),
])
def test_conjunction_doshas_need_a_shared_sign(chart, key, a, others):
    ctx = make_context(*chart)
    d = by_key(de.evaluate_all_doshas(ctx))[key]
    expected = any(ctx.sign_of(a) == ctx.sign_of(b) for b in others)
    assert d["present"] is expected
    if expected:
        assert a in d["participants"]


@pytest.mark.parametrize("chart", CHARTS)
def test_grahan_needs_a_luminary_with_a_node(chart):
    ctx = make_context(*chart)
    d = by_key(de.evaluate_all_doshas(ctx))["grahan"]
    expected = any(ctx.sign_of(lum) == ctx.sign_of(node)
                   for lum in (pr.SUN, pr.MOON) for node in pr.NODES)
    assert d["present"] is expected


def test_guru_chandal_is_found_in_the_reference_chart():
    """Jupiter and Rahu share Libra in this chart."""
    ctx = make_context(*CHARTS[0])
    d = by_key(de.evaluate_all_doshas(ctx))["guru_chandal"]
    assert d["present"] is True
    assert set(d["participants"]) == {pr.JUPITER, pr.RAHU}


# --- Mangal ----------------------------------------------------------------
def test_mangal_houses_are_the_classical_set():
    assert de.MANGAL_HOUSES == (1, 2, 4, 7, 8, 12)


@pytest.mark.parametrize("chart", CHARTS)
def test_mangal_is_reckoned_from_three_reference_points(chart):
    ctx = make_context(*chart)
    d = by_key(de.evaluate_all_doshas(ctx))["mangal"]
    assert len(d["detail"]) == 3
    expected = any(
        ctx.house_from(ref, ctx.sign_of(pr.MARS)) in de.MANGAL_HOUSES
        for ref in (ctx.lagna_sign, ctx.sign_of(pr.MOON), ctx.sign_of(pr.VENUS)))
    assert d["present"] is expected
    if d["present"]:
        assert d["participants"] == [pr.MARS]


# --- Kaal Sarpa ------------------------------------------------------------
@pytest.mark.parametrize("chart", CHARTS)
def test_kaal_sarpa_requires_every_graha_inside_the_arc(chart):
    ctx = make_context(*chart)
    d = by_key(de.evaluate_all_doshas(ctx))["kaal_sarpa"]
    rahu = ctx.positions[pr.RAHU].absolute_longitude
    outside = [p for p in pr.SUN_TO_SATURN
               if (ctx.positions[p].absolute_longitude - rahu) % 360.0 >= 180.0]
    assert d["present"] is (not outside)


# --- Kemadruma -------------------------------------------------------------
@pytest.mark.parametrize("chart", CHARTS)
def test_kemadruma_excludes_the_sun_and_the_nodes(chart):
    ctx = make_context(*chart)
    d = by_key(de.evaluate_all_doshas(ctx))["kemadruma"]
    moon = ctx.sign_of(pr.MOON)
    qualifying = [p for s in ((moon + 1) % 12, (moon - 1) % 12)
                  for p in ctx.planets_in_sign.get(s, [])
                  if p not in (pr.MOON, pr.SUN, pr.RAHU, pr.KETU)]
    assert d["present"] is (not qualifying)


# --- Sakata, Daridra, Amavasya, Pitru --------------------------------------
@pytest.mark.parametrize("chart", CHARTS)
def test_sakata_counts_the_moon_from_jupiter(chart):
    ctx = make_context(*chart)
    d = by_key(de.evaluate_all_doshas(ctx))["sakata"]
    house = ctx.house_from(ctx.sign_of(pr.JUPITER), ctx.sign_of(pr.MOON))
    assert d["present"] is (house in (6, 8, 12))


@pytest.mark.parametrize("chart", CHARTS)
def test_daridra_needs_the_eleventh_lord_in_a_dusthana(chart):
    ctx = make_context(*chart)
    d = by_key(de.evaluate_all_doshas(ctx))["daridra"]
    lord = ctx.house_lord[11]
    assert d["present"] is (ctx.bhava_of(lord) in (6, 8, 12))


@pytest.mark.parametrize("chart", CHARTS)
def test_amavasya_uses_a_twelve_degree_orb(chart):
    ctx = make_context(*chart)
    d = by_key(de.evaluate_all_doshas(ctx))["amavasya"]
    gap = separation(ctx.positions[pr.SUN].absolute_longitude,
                     ctx.positions[pr.MOON].absolute_longitude)
    assert d["present"] is (gap <= 12.0)


@pytest.mark.parametrize("chart", CHARTS)
def test_pitru_checks_the_ninth_house_and_its_lord(chart):
    ctx = make_context(*chart)
    d = by_key(de.evaluate_all_doshas(ctx))["pitru"]
    ninth = ctx.house_sign[9]
    nodes_there = any(ctx.sign_of(n) == ninth for n in pr.NODES)
    lord_afflicted = ctx.bhava_of(ctx.house_lord[9]) in (6, 8, 12)
    assert d["present"] is (nodes_there or lord_afflicted)


# --- Kendradhipatya and Papakartari ----------------------------------------
@pytest.mark.parametrize("chart", CHARTS)
def test_kendradhipatya_catches_only_natural_benefics(chart):
    ctx = make_context(*chart)
    d = by_key(de.evaluate_all_doshas(ctx))["kendradhipatya"]
    for planet in d["participants"]:
        assert natural_nature_of(ctx, planet).nature == cr.BENEFIC
        assert any(h in (4, 7, 10) for h in ctx.houses_owned.get(planet, []))


@pytest.mark.parametrize("chart", CHARTS)
def test_papakartari_needs_a_malefic_on_both_sides(chart):
    ctx = make_context(*chart)
    d = by_key(de.evaluate_all_doshas(ctx))["papakartari"]
    for row in d["detail"]:
        planet = next(p for p in pr.ALL_PLANETS
                      if pr.planet_name(p) == row["label"])
        sign = ctx.sign_of(planet)
        before = [p for p in ctx.planets_in_sign.get((sign - 1) % 12, [])
                  if p in de.MALEFICS_FOR_HEMMING and p != planet]
        after = [p for p in ctx.planets_in_sign.get((sign + 1) % 12, [])
                 if p in de.MALEFICS_FOR_HEMMING and p != planet]
        assert before and after


# --- Per-planet filtering (DOSHA_100) --------------------------------------
@pytest.mark.parametrize("chart", CHARTS)
def test_a_planet_only_sees_the_doshas_it_takes_part_in(chart):
    ctx = make_context(*chart)
    doshas = de.evaluate_all_doshas(ctx)
    for planet in pr.ALL_PLANETS:
        for d in de.doshas_for_planet(ctx, planet, doshas):
            assert d["present"] is True
            assert planet in d["participants"]


@pytest.mark.parametrize("chart", CHARTS)
def test_dosha_bullets_are_red_and_yoga_bullets_green(chart):
    ctx = make_context(*chart)
    for planet in pr.ALL_PLANETS:
        f = build_findings(ctx, planet)
        for x in f["doshas"]:
            assert x["category"] == "challenging"
            assert x["key"].startswith("dosha-")
        for x in f["yogas"]:
            assert x["category"] == "favourable"
            assert x["key"].startswith("yoga-")


@pytest.mark.parametrize("chart", CHARTS)
def test_kemadruma_is_reported_with_the_doshas_not_the_yogas(chart):
    ctx = make_context(*chart)
    for planet in pr.ALL_PLANETS:
        f = build_findings(ctx, planet)
        assert not any(x["key"] == "yoga-kemadruma" for x in f["yogas"])


@pytest.mark.parametrize("chart", CHARTS)
def test_the_six_groups_are_disjoint_and_counted(chart):
    ctx = make_context(*chart)
    for planet in pr.ALL_PLANETS:
        f = build_findings(ctx, planet)
        keys = [x["key"] for g in GROUPS for x in f[g]]
        assert len(keys) == len(set(keys)), "a bullet appears in two groups"
        for g in GROUPS:
            assert f["counts"][g] == len(f[g])


@pytest.mark.parametrize("chart", CHARTS)
def test_your_call_is_kept_out_of_the_yellow_group(chart):
    ctx = make_context(*chart)
    for planet in pr.ALL_PLANETS:
        f = build_findings(ctx, planet)
        assert all(x["openKind"] != cr.OPEN_INTERPRETIVE for x in f["neutral"])
        assert all(x["openKind"] == cr.OPEN_INTERPRETIVE for x in f["interpretive"])


def test_cancellations_are_shown_but_never_applied():
    """A dosha with known grounds for cancellation still reports as present."""
    ctx = make_context(*CHARTS[0])
    d = by_key(de.evaluate_all_doshas(ctx))["guru_chandal"]
    assert d["present"] is True
    assert d["cancellation"]
    f = build_findings(ctx, pr.JUPITER)
    bullet = next(x for x in f["doshas"] if x["key"] == "dosha-guru_chandal")
    assert "held" in bullet["explanation"].lower()


def test_every_dosha_rule_is_registered():
    from app.astrology.rules.registry import all_rules
    ids = {r.rule_id for r in all_rules()}
    for n in range(1, 15):
        assert f"DOSHA_{n:03d}" in ids
    assert "DOSHA_100" in ids
