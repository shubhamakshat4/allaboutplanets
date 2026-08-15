"""Combustion (COMBUST_001) and the Rahu/Ketu contract (RK_001..RK_014)."""
import pytest

from app.astrology import combustion_engine as ce
from app.astrology.planet_analyzer import analyze_planet, combustion, lordship
from app.astrology.rules import planetary_rules as pr

from .conftest import make_context

CHARTS = [
    (1990, 5, 15, 10, 30, 13.0827, 80.2707, 5.5),
    (1975, 1, 3, 4, 15, 51.5074, -0.1278, 0.0),
    (2001, 9, 20, 23, 45, 40.7128, -74.0060, -4.0),
    (1994, 8, 14, 11, 45, 26.72882, 85.92628, 5.75),
]


# --- Classical orbs --------------------------------------------------------
@pytest.mark.parametrize("planet,orb", [
    (pr.MOON, 12.0), (pr.MARS, 17.0), (pr.MERCURY, 14.0),
    (pr.JUPITER, 11.0), (pr.VENUS, 10.0), (pr.SATURN, 15.0),
])
def test_direct_orbs_are_classical(planet, orb):
    assert ce.threshold_for(planet, retrograde=False) == orb


@pytest.mark.parametrize("planet,orb", [
    (pr.MERCURY, 12.0), (pr.VENUS, 8.0),
])
def test_retrograde_orbs_narrow_for_mercury_and_venus(planet, orb):
    assert ce.threshold_for(planet, retrograde=True) == orb
    assert ce.threshold_for(planet, retrograde=True) < ce.threshold_for(planet, False)


@pytest.mark.parametrize("planet", [pr.MARS, pr.JUPITER, pr.SATURN])
def test_other_orbs_are_unchanged_by_retrogression(planet):
    assert ce.threshold_for(planet, True) == ce.threshold_for(planet, False)


def test_sun_and_nodes_have_no_orb():
    """RK_008 — the nodes are outside combustion, and the Sun is the reference."""
    for planet in (pr.SUN, pr.RAHU, pr.KETU):
        assert ce.threshold_for(planet, False) is None
        assert ce.is_combust(planet, 100.0, 100.0, False) is False


# --- Shorter-arc separation ------------------------------------------------
@pytest.mark.parametrize("planet_long,sun_long,expected", [
    (10.0, 20.0, 10.0),
    (359.0, 2.0, 3.0),      # straddling 0 Aries
    (2.0, 359.0, 3.0),
    (355.0, 5.0, 10.0),
    (180.0, 0.0, 180.0),
    (190.0, 0.0, 170.0),
])
def test_separation_uses_the_shorter_arc(planet_long, sun_long, expected):
    assert ce.separation_from_sun(planet_long, sun_long) == pytest.approx(expected)


def test_combustion_detected_across_the_zero_aries_boundary():
    """The failure mode of a raw-longitude comparison: Mercury at 359 and the
    Sun at 2 are 3 degrees apart and must register as combust."""
    assert ce.is_combust(pr.MERCURY, 359.0, 2.0, retrograde=False) is True
    assert ce.is_combust(pr.MERCURY, 2.0, 359.0, retrograde=False) is True


@pytest.mark.parametrize("planet,orb", [
    (pr.MOON, 12.0), (pr.MARS, 17.0), (pr.MERCURY, 14.0),
    (pr.JUPITER, 11.0), (pr.VENUS, 10.0), (pr.SATURN, 15.0),
])
def test_orb_boundary_is_inclusive(planet, orb):
    sun = 100.0
    assert ce.is_combust(planet, sun + orb - 0.0001, sun, False) is True
    assert ce.is_combust(planet, sun + orb, sun, False) is True
    assert ce.is_combust(planet, sun + orb + 0.0001, sun, False) is False


def test_each_planet_uses_its_own_orb_not_a_neighbours():
    """Guards the off-by-one that PyJHora exhibits: at 13 degrees from the Sun
    Mercury (orb 14) is combust while Jupiter (orb 11) is not."""
    sun = 200.0
    assert ce.is_combust(pr.MERCURY, sun + 13.0, sun, False) is True
    assert ce.is_combust(pr.JUPITER, sun + 13.0, sun, False) is False
    # And the Moon must not inherit Saturn's wider orb.
    assert ce.is_combust(pr.MOON, sun + 14.0, sun, False) is False
    assert ce.is_combust(pr.SATURN, sun + 14.0, sun, False) is True


# --- Engine integration ----------------------------------------------------
@pytest.mark.parametrize("chart", CHARTS)
def test_chart_combustion_matches_the_rule(chart):
    ctx = make_context(*chart[:5], 0, *chart[5:])
    sun = ctx.positions[pr.SUN].absolute_longitude
    for planet in pr.COMBUSTION_ELIGIBLE:
        expected = ce.is_combust(
            planet, ctx.positions[planet].absolute_longitude, sun,
            ctx.is_retrograde(planet))
        assert ctx.is_combust(planet) is expected, pr.PLANET_NAMES[planet]


@pytest.mark.parametrize("chart", CHARTS)
def test_pyjhora_verdict_is_reported_alongside(chart):
    ctx = make_context(*chart[:5], 0, *chart[5:])
    for planet in pr.COMBUSTION_ELIGIBLE:
        result = combustion(ctx, planet)
        assert result["applicable"] is True
        assert isinstance(result["pyjhoraVerdict"], bool)
        assert result["verdictsAgree"] == (
            result["combust"] == result["pyjhoraVerdict"])
        assert result["thresholdDegrees"] == ce.threshold_for(
            planet, ctx.is_retrograde(planet))
        assert result["sources"]["rule"] == "COMBUST_001"


@pytest.mark.parametrize("chart", CHARTS)
def test_sun_and_nodes_report_not_applicable(chart):
    ctx = make_context(*chart[:5], 0, *chart[5:])
    for planet in (pr.SUN, pr.RAHU, pr.KETU):
        result = combustion(ctx, planet)
        assert result["applicable"] is False
        assert result["status"] == pr.NOT_APPLICABLE
        assert result["combust"] is False


# --- Rahu / Ketu contract --------------------------------------------------
@pytest.mark.parametrize("chart", CHARTS)
def test_nodes_are_always_opposite(chart):
    """RK_013."""
    ctx = make_context(*chart[:5], 0, *chart[5:])
    rahu = ctx.positions[pr.RAHU].absolute_longitude
    ketu = ctx.positions[pr.KETU].absolute_longitude
    assert (ketu - rahu) % 360.0 == pytest.approx(180.0, abs=1e-6)
    assert ctx.house_from(ctx.sign_of(pr.RAHU), ctx.sign_of(pr.KETU)) == 7


@pytest.mark.parametrize("chart", CHARTS)
def test_nodes_hold_no_lordship_or_functional_role(chart):
    """RK_001."""
    ctx = make_context(*chart[:5], 0, *chart[5:])
    for node in pr.NODES:
        assert pr.owned_signs(node) == []
        result = lordship(ctx, node)
        assert result["housesOwned"] == []
        for role in ("kendraLord", "trikonaLord", "dusthanaLord", "upachayaLord",
                     "marakaLord", "badhakesh", "yogaKaraka"):
            assert result[role] is False, f"{pr.PLANET_NAMES[node]} {role}"


def test_no_sign_is_lorded_by_a_node():
    """RK_001 — the twelve signs belong to the Sun through Saturn only."""
    assert set(pr.SIGN_LORDS) <= set(pr.SUN_TO_SATURN)


@pytest.mark.parametrize("chart", CHARTS)
def test_nodes_report_undefined_rather_than_guessing(chart):
    """RK_002, RK_003, RK_007, RK_009."""
    ctx = make_context(*chart[:5], 0, *chart[5:])
    for node in pr.NODES:
        a = analyze_planet(ctx, node)
        assert a["dignity"]["swarashi"] == pr.NOT_DEFINED
        assert a["dignity"]["mooltrikona"] == pr.NOT_DEFINED
        assert pr.mooltrikona_range(node) is None
        assert a["shadbala"]["available"] is False
        assert a["shadbala"]["status"] == pr.NOT_AVAILABLE
        assert a["planetaryWar"]["status"] == pr.NOT_APPLICABLE
        assert a["combustion"]["status"] == pr.NOT_APPLICABLE


@pytest.mark.parametrize("chart", CHARTS)
def test_nodes_cast_only_the_seventh_drishti(chart):
    """RK_005."""
    ctx = make_context(*chart[:5], 0, *chart[5:])
    for node in pr.NODES:
        assert pr.GRAHA_DRISHTI[node] == [7]
        a = analyze_planet(ctx, node)
        assert {h["aspectOrdinal"] for h in a["aspectsGiven"]["houses"]} == {7}
        assert a["aspectsGiven"]["nodeNote"] is not None


@pytest.mark.parametrize("chart", CHARTS)
def test_nodes_are_retrograde_as_mean_nodes(chart):
    """RK_010."""
    ctx = make_context(*chart[:5], 0, *chart[5:])
    for node in pr.NODES:
        assert ctx.is_retrograde(node) is True
        a = analyze_planet(ctx, node)
        assert a["retrograde"]["motion"] == "Retrograde"
        assert a["retrograde"]["note"] is not None


@pytest.mark.parametrize("chart", CHARTS)
def test_nodes_never_act_as_a_dispositor(chart):
    """RK_011."""
    ctx = make_context(*chart[:5], 0, *chart[5:])
    for planet in pr.ALL_PLANETS:
        a = analyze_planet(ctx, planet)
        for link in a["dispositorChain"]["chain"]:
            assert link["signLord"] not in pr.NODES


@pytest.mark.parametrize("chart", CHARTS)
def test_nodes_are_natural_malefics(chart):
    """RK_014."""
    from app.astrology.dignity_engine import natural_benefic_classification
    ctx = make_context(*chart[:5], 0, *chart[5:])
    benefics = natural_benefic_classification(ctx)
    for node in pr.NODES:
        assert benefics[node]["benefic"] is False


@pytest.mark.parametrize("chart", CHARTS)
def test_nodes_carry_an_avastha_applicability_note(chart):
    """RK_012."""
    ctx = make_context(*chart[:5], 0, *chart[5:])
    for node in pr.NODES:
        a = analyze_planet(ctx, node)
        assert a["avastha"]["kumaradi"]["applicabilityNote"]
        assert a["avastha"]["chaitanyadi"]["applicabilityNote"]


def test_every_rahu_ketu_rule_is_registered():
    from app.astrology.rules.registry import all_rules
    ids = {r.rule_id for r in all_rules()}
    for n in range(1, 15):
        assert f"RK_{n:03d}" in ids
    assert "COMBUST_001" in ids


# --- Generated rule documents stay in sync ---------------------------------
def test_rules_document_is_up_to_date():
    """docs/RULES.md is generated. If a rule changes without regenerating it,
    the document silently lies about what the code does."""
    from pathlib import Path
    from tools.generate_rules_doc import build, OUT

    if not OUT.exists():
        pytest.fail("docs/RULES.md is missing. Run: python -m tools.generate_rules_doc")

    on_disk = Path(OUT).read_text(encoding="utf-8")
    assert on_disk == build(), (
        "docs/RULES.md is stale. Regenerate with: python -m tools.generate_rules_doc"
    )


def test_rules_pdf_and_html_were_rendered_from_the_current_markdown():
    """docs/RULES.pdf and docs/RULES.html are rendered from RULES.md.

    Re-rendering them needs a browser, so instead each carries the SHA-256 of
    the Markdown it came from. Comparing that to the current file catches a
    stale PDF without running Chrome.
    """
    import hashlib

    from tools.generate_rules_pdf import HTML_OUT, PDF_OUT, SRC

    if not SRC.exists():
        pytest.fail("docs/RULES.md is missing. Run: python -m tools.generate_rules_doc")

    expected = hashlib.sha256(SRC.read_bytes()).hexdigest()

    assert HTML_OUT.exists(), "docs/RULES.html is missing"
    html = HTML_OUT.read_text(encoding="utf-8")
    assert f'content="{expected}"' in html, (
        "docs/RULES.html is stale. Regenerate with: python -m tools.generate_rules_pdf")

    assert PDF_OUT.exists(), "docs/RULES.pdf is missing"
    try:
        import pymupdf
    except ImportError:
        pytest.skip("PyMuPDF not installed; cannot read the PDF fingerprint")

    doc = pymupdf.open(PDF_OUT)
    stamped = (doc.metadata or {}).get("keywords", "")
    doc.close()
    assert stamped == f"rules-source-sha256={expected}", (
        "docs/RULES.pdf is stale. Regenerate with: python -m tools.generate_rules_pdf")


def test_every_registered_rule_reaches_the_document():
    """A rule that exists in code but never appears in the reference document
    is invisible to the astrologer reviewing it."""
    from app.astrology.rules.registry import all_rules
    from tools.generate_rules_pdf import SRC

    text = SRC.read_text(encoding="utf-8")
    missing = [r.rule_id for r in all_rules() if f"`{r.rule_id}`" not in text]
    assert not missing, f"rules absent from docs/RULES.md: {missing}"
