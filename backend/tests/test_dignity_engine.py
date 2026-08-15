"""Dignity, Mooltrikona, Vargottama and benefic classification tests."""
import pytest

from app.astrology.dignity_engine import (
    dignity, dignity_in_sign, natural_benefic_classification, vargottama,
)
from app.astrology.rules import planetary_rules as pr

ARIES, TAURUS, GEMINI, CANCER = 0, 1, 2, 3
LEO, VIRGO, LIBRA, SCORPIO = 4, 5, 6, 7
SAGITTARIUS, CAPRICORN, AQUARIUS, PISCES = 8, 9, 10, 11


# --- Exaltation ------------------------------------------------------------
@pytest.mark.parametrize("planet,sign", [
    (pr.SUN, ARIES),
    (pr.MOON, TAURUS),
    (pr.MARS, CAPRICORN),
    (pr.MERCURY, VIRGO),
    (pr.JUPITER, CANCER),
    (pr.VENUS, PISCES),
    (pr.SATURN, LIBRA),
])
def test_exaltation_signs(planet, sign):
    assert sign in pr.exaltation_signs(planet)
    # Mercury's exaltation sign is also its own sign, where the library's
    # single-code dignity table reports Own Sign. Both facts are kept.
    expected = "Own Sign" if sign in pr.owned_signs(planet) else "Exaltation Sign"
    assert dignity_in_sign(planet, sign) == expected


# --- Debilitation ----------------------------------------------------------
@pytest.mark.parametrize("planet,sign", [
    (pr.SUN, LIBRA),
    (pr.MOON, SCORPIO),
    (pr.MARS, CANCER),
    (pr.MERCURY, PISCES),
    (pr.JUPITER, CAPRICORN),
    (pr.VENUS, VIRGO),
    (pr.SATURN, ARIES),
])
def test_debilitation_signs(planet, sign):
    assert sign in pr.debilitation_signs(planet)
    assert dignity_in_sign(planet, sign) == "Debilitation Sign"


def test_debilitation_is_opposite_exaltation():
    for planet in pr.SUN_TO_SATURN:
        exalt = pr.exaltation_sign(planet)
        debil = pr.debilitation_sign(planet)
        assert (exalt + 6) % 12 == debil


# --- Own signs (Swarashi) --------------------------------------------------
@pytest.mark.parametrize("planet,signs", [
    (pr.SUN, [LEO]),
    (pr.MOON, [CANCER]),
    (pr.MARS, [ARIES, SCORPIO]),
    (pr.MERCURY, [GEMINI, VIRGO]),
    (pr.JUPITER, [SAGITTARIUS, PISCES]),
    (pr.VENUS, [TAURUS, LIBRA]),
    (pr.SATURN, [CAPRICORN, AQUARIUS]),
])
def test_own_signs(planet, signs):
    assert sorted(pr.owned_signs(planet)) == sorted(signs)


def test_nodes_own_no_sign():
    assert pr.owned_signs(pr.RAHU) == []
    assert pr.owned_signs(pr.KETU) == []


def test_every_sign_has_exactly_one_lord():
    assert len(pr.SIGN_LORDS) == 12
    for sign, lord in enumerate(pr.SIGN_LORDS):
        assert sign in pr.owned_signs(lord)


# --- Mooltrikona -----------------------------------------------------------
@pytest.mark.parametrize("planet,sign,start,end", [
    # Brihat Parashara Hora Shastra, Ch. 3.
    (pr.SUN, LEO, 0.0, 20.0),
    (pr.MOON, TAURUS, 4.0, 30.0),
    (pr.MARS, ARIES, 0.0, 12.0),
    (pr.MERCURY, VIRGO, 16.0, 20.0),
    (pr.JUPITER, SAGITTARIUS, 0.0, 10.0),
    (pr.VENUS, LIBRA, 0.0, 15.0),
    (pr.SATURN, AQUARIUS, 0.0, 20.0),
])
def test_mooltrikona_ranges(planet, sign, start, end):
    assert pr.mooltrikona_range(planet) == (sign, start, end)


def test_mooltrikona_begins_after_the_exaltation_degree():
    """For the Moon and Mercury the Mooltrikona arc starts at the degree after
    the exaltation point, which is what separates BPHS from PyJHora's table."""
    for planet in (pr.MOON, pr.MERCURY):
        mt_sign, start, _ = pr.mooltrikona_range(planet)
        deep = pr.deep_exaltation_longitude(planet)
        exalt_sign, exalt_deg = int(deep // 30), deep % 30
        if mt_sign == exalt_sign:
            assert start == exalt_deg + 1.0, pr.PLANET_NAMES[planet]


def test_mooltrikona_not_defined_for_nodes():
    assert pr.mooltrikona_range(pr.RAHU) is None
    assert pr.mooltrikona_range(pr.KETU) is None


def test_mooltrikona_boundaries_via_engine(ctx):
    """The Mooltrikona check is lower-inclusive and upper-exclusive."""
    from app.astrology.dignity_engine import _mooltrikona

    # Sun in Leo 0-20.
    assert _mooltrikona(pr.SUN, LEO, 0.0)["result"] is True
    assert _mooltrikona(pr.SUN, LEO, 19.99999)["result"] is True
    assert _mooltrikona(pr.SUN, LEO, 20.0)["result"] is False
    assert _mooltrikona(pr.SUN, LEO, 25.0)["result"] is False
    # Wrong sign.
    assert _mooltrikona(pr.SUN, ARIES, 10.0)["result"] is False
    # Moon in Taurus 4-30 (BPHS): below the start.
    assert _mooltrikona(pr.MOON, TAURUS, 3.99999)["result"] is False
    assert _mooltrikona(pr.MOON, TAURUS, 4.0)["result"] is True
    assert _mooltrikona(pr.MOON, TAURUS, 29.99999)["result"] is True
    # Mercury in Virgo 16-20 (BPHS).
    assert _mooltrikona(pr.MERCURY, VIRGO, 15.99999)["result"] is False
    assert _mooltrikona(pr.MERCURY, VIRGO, 16.0)["result"] is True
    assert _mooltrikona(pr.MERCURY, VIRGO, 19.99999)["result"] is True
    assert _mooltrikona(pr.MERCURY, VIRGO, 20.0)["result"] is False


def test_mooltrikona_undefined_reports_not_defined(ctx):
    for node in (pr.RAHU, pr.KETU):
        result = dignity(ctx, node)
        assert result["mooltrikona"] == pr.NOT_DEFINED
        assert result["swarashi"] == pr.NOT_DEFINED
        assert result["evidence"]["nodeNote"] is not None


# --- Dignity record --------------------------------------------------------
def test_exaltation_and_own_sign_may_coincide():
    """Mercury is both exalted and in its own sign in Virgo. PyJHora's dignity
    table can only store one code per cell and records Own Sign, so exaltation
    is derived from the deep-exaltation longitudes and both facts survive."""
    assert VIRGO in pr.exaltation_signs(pr.MERCURY)
    assert VIRGO in pr.owned_signs(pr.MERCURY)
    assert dignity_in_sign(pr.MERCURY, VIRGO) == "Own Sign"


def test_dignity_flags_are_mutually_consistent(ctx):
    """Exalted, debilitated, friend, neutral and enemy are mutually exclusive.
    Own-sign may coincide with exaltation (Mercury in Virgo), so it is checked
    separately rather than folded into the exclusive set."""
    for planet in pr.ALL_PLANETS:
        d = dignity(ctx, planet)
        exclusive = [d["exalted"], d["debilitated"], d["friendSign"],
                     d["neutralSign"], d["enemySign"], d["swarashi"] is True]
        assert sum(1 for f in exclusive if f is True) >= 1, planet
        assert not (d["exalted"] and d["debilitated"])
        # A friend's, neutral or enemy sign can never also be own or exalted.
        soft = [d["friendSign"], d["neutralSign"], d["enemySign"]]
        if any(soft):
            assert sum(1 for f in soft if f) == 1
            assert not d["exalted"] and not d["debilitated"]
            assert d["swarashi"] is not True


def test_dignity_carries_evidence_and_sources(ctx):
    d = dignity(ctx, pr.JUPITER)
    assert "table" in d["evidence"]
    assert d["sources"]["dignity"]["rule"] == "DIGNITY_001"
    assert d["sources"]["mooltrikona"]["rule"] == "DIGNITY_002"


# --- Vargottama ------------------------------------------------------------
def test_vargottama_matches_d1_d9(ctx):
    for planet in pr.ALL_PLANETS:
        v = vargottama(ctx, planet)
        expected = ctx.varga_sign(planet, 1) == ctx.varga_sign(planet, 9)
        assert v["isVargottama"] is expected
        assert v["sources"]["rule"] == "VARGA_001"
        assert "D1 Rashi" in v["evidence"]


# --- Benefic classification ------------------------------------------------
def test_benefic_classification_covers_all_planets(ctx):
    result = natural_benefic_classification(ctx)
    assert set(result) == set(pr.ALL_PLANETS)
    for planet, entry in result.items():
        assert isinstance(entry["benefic"], bool)
        assert entry["reason"]
        assert entry["rule"] == "BENEFIC_001"


def test_unconditional_benefics_and_malefics(ctx):
    result = natural_benefic_classification(ctx)
    assert result[pr.JUPITER]["benefic"] is True
    assert result[pr.VENUS]["benefic"] is True
    for p in (pr.SUN, pr.MARS, pr.SATURN, pr.RAHU, pr.KETU):
        assert result[p]["benefic"] is False


def test_moon_benefic_follows_elongation(ctx):
    result = natural_benefic_classification(ctx)
    elong = (ctx.positions[pr.MOON].absolute_longitude
             - ctx.positions[pr.SUN].absolute_longitude) % 360.0
    assert result[pr.MOON]["benefic"] is (72.0 <= elong <= 288.0)


def test_mercury_benefic_follows_sign_companions(ctx):
    result = natural_benefic_classification(ctx)
    companions = [p for p in ctx.planets_in_sign[ctx.sign_of(pr.MERCURY)]
                  if p != pr.MERCURY]
    has_malefic = any(p in (pr.SUN, pr.MARS, pr.SATURN, pr.RAHU, pr.KETU)
                      for p in companions)
    assert result[pr.MERCURY]["benefic"] is (not has_malefic)
