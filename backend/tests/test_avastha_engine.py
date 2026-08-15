"""Boundary tests for the two Avastha systems (RULES KUMARADI_001, CHAITANYADI_001)."""
import pytest

from app.astrology.rules.avastha_rules import (
    CHAITANYADI_EVEN, CHAITANYADI_ODD, KUMARADI_EVEN, KUMARADI_ODD, resolve_band,
)
from app.astrology.rules.planetary_rules import sign_parity

ARIES, TAURUS, GEMINI, CANCER = 0, 1, 2, 3
LEO, VIRGO, LIBRA, SCORPIO = 4, 5, 6, 7
SAGITTARIUS, CAPRICORN, AQUARIUS, PISCES = 8, 9, 10, 11


def kumaradi(degree, sign):
    bands = KUMARADI_ODD if sign_parity(sign) == "Odd" else KUMARADI_EVEN
    return resolve_band(bands, degree)[2]


def chaitanyadi(degree, sign):
    bands = CHAITANYADI_ODD if sign_parity(sign) == "Odd" else CHAITANYADI_EVEN
    return resolve_band(bands, degree)[2]


# --- sign parity -----------------------------------------------------------
@pytest.mark.parametrize("sign,expected", [
    (ARIES, "Odd"), (TAURUS, "Even"), (GEMINI, "Odd"), (CANCER, "Even"),
    (LEO, "Odd"), (VIRGO, "Even"), (LIBRA, "Odd"), (SCORPIO, "Even"),
    (SAGITTARIUS, "Odd"), (CAPRICORN, "Even"), (AQUARIUS, "Odd"), (PISCES, "Even"),
])
def test_sign_parity(sign, expected):
    assert sign_parity(sign) == expected


# --- Kumaradi boundaries in odd signs --------------------------------------
@pytest.mark.parametrize("degree,expected", [
    (0.0, "Bala"),
    (5.0 + 59 / 60 + 59 / 3600, "Bala"),      # 5°59'59"
    (6.0, "Kumara"),                           # exact boundary moves up
    (11.0 + 59 / 60 + 59 / 3600, "Kumara"),
    (12.0, "Yuva"),
    (17.0 + 59 / 60 + 59 / 3600, "Yuva"),
    (18.0, "Vriddha"),
    (23.0 + 59 / 60 + 59 / 3600, "Vriddha"),
    (24.0, "Mrita"),
    (29.999, "Mrita"),
    (30.0, "Mrita"),
])
def test_kumaradi_odd_boundaries(degree, expected):
    assert kumaradi(degree, ARIES) == expected


# --- Kumaradi boundaries in even signs (order reversed) --------------------
@pytest.mark.parametrize("degree,expected", [
    (0.0, "Mrita"),
    (5.0 + 59 / 60 + 59 / 3600, "Mrita"),
    (6.0, "Vriddha"),
    (11.0 + 59 / 60 + 59 / 3600, "Vriddha"),
    (12.0, "Yuva"),
    (17.0 + 59 / 60 + 59 / 3600, "Yuva"),
    (18.0, "Kumara"),
    (23.0 + 59 / 60 + 59 / 3600, "Kumara"),
    (24.0, "Bala"),
    (29.999, "Bala"),
])
def test_kumaradi_even_boundaries(degree, expected):
    assert kumaradi(degree, TAURUS) == expected


def test_kumaradi_middle_band_is_yuva_in_both_parities():
    """Yuva occupies 12-18 in both orders, which is the fixed point of the reversal."""
    assert kumaradi(14.0 + 32 / 60, ARIES) == "Yuva"
    assert kumaradi(14.0 + 32 / 60, TAURUS) == "Yuva"


# --- Chaitanyadi boundaries in odd signs ----------------------------------
@pytest.mark.parametrize("degree,expected", [
    (0.0, "Jagrut"),
    (9.0 + 59 / 60 + 59 / 3600, "Jagrut"),
    (10.0, "Swapna"),
    (19.0 + 59 / 60 + 59 / 3600, "Swapna"),
    (20.0, "Sushupta"),
    (29.999, "Sushupta"),
    (30.0, "Sushupta"),
])
def test_chaitanyadi_odd_boundaries(degree, expected):
    assert chaitanyadi(degree, GEMINI) == expected


# --- Chaitanyadi boundaries in even signs ---------------------------------
@pytest.mark.parametrize("degree,expected", [
    (0.0, "Sushupta"),
    (9.0 + 59 / 60 + 59 / 3600, "Sushupta"),
    (10.0, "Swapna"),
    (19.0 + 59 / 60 + 59 / 3600, "Swapna"),
    (20.0, "Jagrut"),
    (29.999, "Jagrut"),
])
def test_chaitanyadi_even_boundaries(degree, expected):
    assert chaitanyadi(degree, CANCER) == expected


def test_chaitanyadi_middle_band_is_swapna_in_both_parities():
    assert chaitanyadi(15.0, ARIES) == "Swapna"
    assert chaitanyadi(15.0, TAURUS) == "Swapna"


# --- Out of range ----------------------------------------------------------
@pytest.mark.parametrize("degree", [-0.001, 30.001, 45.0])
def test_out_of_range_raises(degree):
    with pytest.raises(ValueError):
        resolve_band(KUMARADI_ODD, degree)


# --- Engine integration ----------------------------------------------------
def test_engine_reports_evidence(ctx):
    from app.astrology.avastha_engine import avasthas
    from app.astrology.rules.planetary_rules import JUPITER

    result = avasthas(ctx, JUPITER)
    k = result["kumaradi"]
    assert k["result"] in ("Bala", "Kumara", "Yuva", "Vriddha", "Mrita")
    assert k["signType"] in ("Odd", "Even")
    assert "Range" in k["evidence"]
    assert k["sources"]["rule"] == "KUMARADI_001"

    c = result["chaitanyadi"]
    assert c["result"] in ("Jagrut", "Swapna", "Sushupta")
    assert c["sources"]["rule"] == "CHAITANYADI_001"


def test_nodes_carry_applicability_note(ctx):
    from app.astrology.avastha_engine import avasthas
    from app.astrology.rules.planetary_rules import KETU, RAHU

    for node in (RAHU, KETU):
        result = avasthas(ctx, node)
        assert "applicabilityNote" in result["kumaradi"]
        assert "applicabilityNote" in result["chaitanyadi"]
