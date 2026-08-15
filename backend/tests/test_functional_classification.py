"""House categories, Badhaka, Maraka, Yoga Karaka and lordship tests."""
import pytest

from app.astrology.planet_analyzer import lordship
from app.astrology.rules import planetary_rules as pr
from app.astrology.rules.functional_classification_rules import (
    CATEGORY_BADHAKA, CATEGORY_DUSTHANA, CATEGORY_KENDRA, CATEGORY_MARAKA,
    CATEGORY_TRIKONA, CATEGORY_UPACHAYA, house_categories, is_yoga_karaka,
)

ARIES, TAURUS, GEMINI, CANCER = 0, 1, 2, 3
LEO, VIRGO, LIBRA, SCORPIO = 4, 5, 6, 7
SAGITTARIUS, CAPRICORN, AQUARIUS, PISCES = 8, 9, 10, 11


# --- Category membership ---------------------------------------------------
@pytest.mark.parametrize("house", [1, 4, 7, 10])
def test_kendra_houses(house):
    assert CATEGORY_KENDRA in house_categories(house, ARIES)


@pytest.mark.parametrize("house", [1, 5, 9])
def test_trikona_houses(house):
    assert CATEGORY_TRIKONA in house_categories(house, ARIES)


@pytest.mark.parametrize("house", [6, 8, 12])
def test_dusthana_houses(house):
    assert CATEGORY_DUSTHANA in house_categories(house, ARIES)


@pytest.mark.parametrize("house", [3, 6, 10, 11])
def test_upachaya_houses(house):
    assert CATEGORY_UPACHAYA in house_categories(house, ARIES)


@pytest.mark.parametrize("house", [2, 7])
def test_maraka_houses(house):
    assert CATEGORY_MARAKA in house_categories(house, ARIES)


def test_first_house_is_both_kendra_and_trikona():
    cats = house_categories(1, LEO)
    assert CATEGORY_KENDRA in cats and CATEGORY_TRIKONA in cats


def test_houses_outside_every_category():
    """No category claims a house it should not."""
    assert house_categories(3, TAURUS) == [CATEGORY_UPACHAYA]


# --- Badhaka ---------------------------------------------------------------
@pytest.mark.parametrize("lagna,expected", [
    (ARIES, 11), (CANCER, 11), (LIBRA, 11), (CAPRICORN, 11),      # movable
    (TAURUS, 9), (LEO, 9), (SCORPIO, 9), (AQUARIUS, 9),           # fixed
    (GEMINI, 7), (VIRGO, 7), (SAGITTARIUS, 7), (PISCES, 7),       # dual
])
def test_badhaka_house_by_modality(lagna, expected):
    assert pr.badhaka_house(lagna) == expected
    assert CATEGORY_BADHAKA in house_categories(expected, lagna)


@pytest.mark.parametrize("lagna,expected", [
    (ARIES, "Movable"), (TAURUS, "Fixed"), (GEMINI, "Dual"),
    (CANCER, "Movable"), (LEO, "Fixed"), (VIRGO, "Dual"),
    (LIBRA, "Movable"), (SCORPIO, "Fixed"), (SAGITTARIUS, "Dual"),
    (CAPRICORN, "Movable"), (AQUARIUS, "Fixed"), (PISCES, "Dual"),
])
def test_sign_modality(lagna, expected):
    assert pr.sign_modality(lagna) == expected


# --- Yoga Karaka -----------------------------------------------------------
@pytest.mark.parametrize("houses,expected", [
    ([4, 9], True),      # Kendra + Trikona
    ([10, 5], True),
    ([7, 9], True),
    ([1], False),        # 1st alone does not qualify
    ([1, 4], False),     # Kendra only
    ([1, 5], False),     # Trikona only, 1st is not a second Kendra
    ([4, 7], False),
    ([5, 9], False),
    ([], False),
])
def test_yoga_karaka(houses, expected):
    assert is_yoga_karaka(houses) is expected


def test_classical_yoga_karakas():
    """Mars for Cancer/Scorpio Lagna, Venus for Capricorn/Aquarius,
    Saturn for Taurus/Libra — the classical results, derived not hard-coded."""
    def houses_owned(planet: int, lagna: int):
        return sorted(((s - lagna) % 12) + 1
                      for s in pr.owned_signs(planet))

    assert is_yoga_karaka(houses_owned(pr.MARS, CANCER))       # 5th & 10th
    assert is_yoga_karaka(houses_owned(pr.MARS, LEO))          # 4th & 9th
    assert is_yoga_karaka(houses_owned(pr.VENUS, CAPRICORN))   # 5th & 10th
    assert is_yoga_karaka(houses_owned(pr.VENUS, AQUARIUS))    # 4th & 9th
    assert is_yoga_karaka(houses_owned(pr.SATURN, TAURUS))     # 9th & 10th
    assert is_yoga_karaka(houses_owned(pr.SATURN, LIBRA))      # 4th & 5th


def test_mars_is_not_yoga_karaka_for_scorpio_lagna():
    houses = sorted(((s - SCORPIO) % 12) + 1 for s in pr.owned_signs(pr.MARS))
    assert houses == [1, 6]
    assert is_yoga_karaka(houses) is False


# --- Lordship record -------------------------------------------------------
def test_lordship_reports_every_component(ctx):
    result = lordship(ctx, pr.JUPITER)
    for key in ("kendraLord", "trikonaLord", "dusthanaLord", "upachayaLord",
                "marakaLord", "badhakesh", "yogaKaraka"):
        assert isinstance(result[key], bool), key
    assert result["housesOwned"]
    assert result["evidence"]["ownership"]
    assert result["evidence"]["badhaka"]
    assert result["evidence"]["yogaKaraka"]


def test_lordship_houses_owned_match_sign_lordship(ctx):
    for planet in pr.ALL_PLANETS:
        result = lordship(ctx, planet)
        expected = sorted(((s - ctx.lagna_sign) % 12) + 1
                          for s in pr.owned_signs(planet))
        assert result["housesOwned"] == expected


def test_nodes_hold_no_lordship(ctx):
    for node in (pr.RAHU, pr.KETU):
        result = lordship(ctx, node)
        assert result["housesOwned"] == []
        assert result["ownsNoHouse"] is True
        assert result["nodeNote"] is not None
        assert result["yogaKaraka"] is False


def test_every_house_has_a_lord(ctx):
    for house in range(1, 13):
        assert ctx.house_lord[house] in pr.SUN_TO_SATURN


def test_house_signs_follow_lagna(ctx):
    for house in range(1, 13):
        assert ctx.house_sign[house] == (ctx.lagna_sign + house - 1) % 12


def test_whole_sign_bhava_rule(ctx):
    """RULE HOUSE_001."""
    for planet in pr.ALL_PLANETS:
        expected = ((ctx.sign_of(planet) - ctx.lagna_sign) % 12) + 1
        assert ctx.bhava_of(planet) == expected
