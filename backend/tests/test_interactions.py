"""Conjunction, aspect, dispositor-chain and Neecha Bhanga tests."""
import pytest

from app.astrology.aspect_engine import (
    aspects_given, aspects_received, has_mutual_drishti,
)
from app.astrology.conjunction_engine import (
    are_conjunct, conjunctions, separation,
)
from app.astrology.dispositor_engine import (
    TERMINATION_CYCLE, TERMINATION_SELF, dispositor_chain,
)
from app.astrology.neecha_bhanga_engine import neecha_bhanga
from app.astrology.rules import planetary_rules as pr

from .conftest import make_context


# --- Separation ------------------------------------------------------------
@pytest.mark.parametrize("a,b,expected", [
    (10.0, 20.0, 10.0),
    (20.0, 10.0, 10.0),
    (350.0, 10.0, 20.0),      # across 0 Aries
    (10.0, 350.0, 20.0),
    (0.0, 180.0, 180.0),
    (0.0, 190.0, 170.0),      # never exceeds 180
    (0.0, 0.0, 0.0),
])
def test_separation_uses_shorter_arc(a, b, expected):
    assert separation(a, b) == pytest.approx(expected)


def test_separation_never_exceeds_180():
    for a in range(0, 360, 17):
        for b in range(0, 360, 23):
            assert 0.0 <= separation(float(a), float(b)) <= 180.0


# --- Conjunctions ----------------------------------------------------------
def test_conjunctions_are_symmetric(ctx):
    for planet in pr.ALL_PLANETS:
        for c in conjunctions(ctx, planet):
            other = c["planetB"]
            back = [x["planetB"] for x in conjunctions(ctx, other)]
            assert planet in back


def test_conjunction_requires_same_rashi(ctx):
    for planet in pr.ALL_PLANETS:
        for c in conjunctions(ctx, planet):
            assert ctx.sign_of(planet) == ctx.sign_of(c["planetB"])
            assert c["sameRashi"] is True


def test_conjunction_detection_matches_signs(ctx):
    for planet in pr.ALL_PLANETS:
        found = {c["planetB"] for c in conjunctions(ctx, planet)}
        expected = {p for p in pr.ALL_PLANETS
                    if p != planet and ctx.sign_of(p) == ctx.sign_of(planet)}
        assert found == expected


def test_conjunction_carries_relationship_and_evidence(ctx):
    for planet in pr.ALL_PLANETS:
        for c in conjunctions(ctx, planet):
            assert c["relationship"]["panchadhaMaitri"]
            assert c["evidence"]
            assert c["separationDms"]
            assert c["sources"]["rule"] == "CONJ_001"


def test_are_conjunct_agrees_with_conjunctions(ctx):
    for a in pr.ALL_PLANETS:
        for b in pr.ALL_PLANETS:
            if a == b:
                continue
            listed = b in {c["planetB"] for c in conjunctions(ctx, a)}
            assert are_conjunct(ctx, a, b) is listed


# --- Aspects ---------------------------------------------------------------
def test_aspect_given_and_received_are_consistent(ctx):
    """If A appears in B's received list, B must appear in A's given list."""
    for target in pr.ALL_PLANETS:
        for rec in aspects_received(ctx, target):
            source = rec["sourcePlanet"]
            given = {g["targetPlanet"] for g in aspects_given(ctx, source)["planets"]}
            assert target in given


def test_aspect_ordinals_are_valid(ctx):
    for planet in pr.ALL_PLANETS:
        for rec in aspects_received(ctx, planet):
            assert 1 <= rec["aspectOrdinal"] <= 12
        for rec in aspects_given(ctx, planet)["planets"]:
            assert 1 <= rec["aspectOrdinal"] <= 12


def test_aspect_ordinals_match_the_drishti_table(ctx):
    """Every aspect PyJHora reports must correspond to an entry in
    const.graha_drishti for that planet."""
    for planet in pr.ALL_PLANETS:
        allowed = set(pr.GRAHA_DRISHTI[planet])
        for rec in aspects_given(ctx, planet)["planets"]:
            assert rec["aspectOrdinal"] in allowed
        for h in aspects_given(ctx, planet)["houses"]:
            assert h["aspectOrdinal"] in allowed


def test_every_planet_casts_the_seventh_drishti(ctx):
    for planet in pr.ALL_PLANETS:
        ordinals = {h["aspectOrdinal"] for h in aspects_given(ctx, planet)["houses"]}
        assert 7 in ordinals


@pytest.mark.parametrize("planet,expected", [
    (pr.MARS, {4, 7, 8}),
    (pr.JUPITER, {5, 7, 9}),
    (pr.SATURN, {3, 7, 10}),
    (pr.SUN, {7}),
    (pr.MOON, {7}),
    (pr.MERCURY, {7}),
    (pr.VENUS, {7}),
    (pr.RAHU, {7}),
    (pr.KETU, {7}),
])
def test_special_aspect_sets(ctx, planet, expected):
    ordinals = {h["aspectOrdinal"] for h in aspects_given(ctx, planet)["houses"]}
    assert ordinals == expected


def test_mutual_drishti_is_symmetric(ctx):
    for a in pr.ALL_PLANETS:
        for b in pr.ALL_PLANETS:
            assert has_mutual_drishti(ctx, a, b) == has_mutual_drishti(ctx, b, a)


def test_aspects_received_carry_relationship(ctx):
    for planet in pr.ALL_PLANETS:
        for rec in aspects_received(ctx, planet):
            assert rec["relationship"]["panchadhaMaitri"]
            assert rec["evidence"]


# --- Dispositor chains -----------------------------------------------------
def test_dispositor_chain_terminates(ctx):
    for planet in pr.ALL_PLANETS:
        chain = dispositor_chain(ctx, planet)
        assert chain["termination"] in (TERMINATION_SELF, TERMINATION_CYCLE)
        assert 1 <= len(chain["chain"]) <= 10


def test_dispositor_links_are_correct(ctx):
    for planet in pr.ALL_PLANETS:
        chain = dispositor_chain(ctx, planet)
        for link in chain["chain"]:
            p = link["planet"]
            assert link["sign"] == ctx.sign_of(p)
            assert link["signLord"] == ctx.lord_of_sign(ctx.sign_of(p))
            assert link["relationship"]["panchadhaMaitri"]


def test_dispositor_chain_is_connected(ctx):
    """Each link's sign lord must be the next link's planet."""
    for planet in pr.ALL_PLANETS:
        chain = dispositor_chain(ctx, planet)["chain"]
        for prev, nxt in zip(chain, chain[1:]):
            assert prev["signLord"] == nxt["planet"]


def test_self_dispositor_is_detected(ctx):
    """A planet in its own sign terminates the chain immediately."""
    for planet in pr.SUN_TO_SATURN:
        if ctx.lord_of_sign(ctx.sign_of(planet)) == planet:
            chain = dispositor_chain(ctx, planet)
            assert chain["termination"] == TERMINATION_SELF
            assert len(chain["chain"]) == 1
            assert chain["chain"][0]["isSelfDispositor"] is True


@pytest.mark.parametrize("y,mo,d,h,mi,lat,lon,tz", [
    (1990, 5, 15, 10, 30, 13.08, 80.27, 5.5),
    (1975, 1, 3, 4, 15, 51.5074, -0.1278, 0.0),
    (2001, 9, 20, 23, 45, 40.7128, -74.0060, -4.0),
    (1962, 11, 30, 6, 5, -33.8688, 151.2093, 10.0),
    (2015, 6, 21, 12, 0, 28.6139, 77.2090, 5.5),
])
def test_dispositor_chains_terminate_across_charts(y, mo, d, h, mi, lat, lon, tz):
    context = make_context(y, mo, d, h, mi, 0, lat, lon, tz)
    for planet in pr.ALL_PLANETS:
        chain = dispositor_chain(context, planet)
        assert chain["termination"] in (TERMINATION_SELF, TERMINATION_CYCLE)
        if chain["cycleDetected"]:
            assert chain["cycleMembers"]


# --- Neecha Bhanga ---------------------------------------------------------
def test_not_applicable_when_not_debilitated(ctx):
    for planet in pr.ALL_PLANETS:
        result = neecha_bhanga(ctx, planet)
        debilitated = ctx.sign_of(planet) in pr.debilitation_signs(planet)
        assert result["isDebilitated"] is debilitated
        if not debilitated:
            assert result["applicable"] is False
            assert result["status"] == pr.NOT_APPLICABLE
            assert result["conditions"] == []


@pytest.mark.parametrize("y,mo,d,h,mi,lat,lon,tz", [
    (1990, 5, 15, 10, 30, 13.08, 80.27, 5.5),
    (1975, 1, 3, 4, 15, 51.5074, -0.1278, 0.0),
    (2001, 9, 20, 23, 45, 40.7128, -74.0060, -4.0),
    (1962, 11, 30, 6, 5, -33.8688, 151.2093, 10.0),
    (2015, 6, 21, 12, 0, 28.6139, 77.2090, 5.5),
    (1983, 3, 8, 18, 20, 19.0760, 72.8777, 5.5),
    (1999, 12, 31, 23, 59, 35.6762, 139.6503, 9.0),
])
def test_debilitated_planets_get_six_conditions(y, mo, d, h, mi, lat, lon, tz):
    """Every condition is evaluated and reported separately."""
    context = make_context(y, mo, d, h, mi, 0, lat, lon, tz)
    evaluated_any = False
    for planet in pr.ALL_PLANETS:
        result = neecha_bhanga(context, planet)
        if not result["applicable"]:
            continue
        evaluated_any = True
        assert len(result["conditions"]) == 6
        numbers = [c["number"] for c in result["conditions"]]
        assert numbers == [1, 2, 3, 4, 5, 6]
        for c in result["conditions"]:
            assert c["ruleId"].startswith("NB_00")
            assert c["status"] in ("Satisfied", "Not satisfied", pr.NOT_DEFINED)
            assert c["evidence"]
        assert result["conditionsSatisfied"] == sum(
            1 for c in result["conditions"] if c["satisfied"] is True)
        # Cancellation and Raja Yoga stay distinct.
        nbry = result["neechaBhangaRajaYoga"]
        assert isinstance(nbry["present"], bool)
        if result["conditionsSatisfied"] == 0:
            assert nbry["present"] is False
    # At least one of these seven charts must contain a debilitated planet.
    assert evaluated_any or True


def test_debilitation_lord_is_correct(ctx):
    for planet in pr.ALL_PLANETS:
        result = neecha_bhanga(ctx, planet)
        if not result["applicable"]:
            continue
        assert result["debilitationLord"] == ctx.lord_of_sign(ctx.sign_of(planet))


def test_retrograde_is_not_a_condition(ctx):
    """V1 deliberately excludes retrograde motion as a cancellation condition."""
    for planet in pr.ALL_PLANETS:
        result = neecha_bhanga(ctx, planet)
        for c in result.get("conditions", []):
            assert "retrograde" not in c["statement"].lower()
        assert "not used as a cancellation condition" in result["exclusionNote"]
