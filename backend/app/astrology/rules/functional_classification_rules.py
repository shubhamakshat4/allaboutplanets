"""House-category classification (RULES FUNC_002 .. FUNC_005)."""
from __future__ import annotations

from typing import List

from .planetary_rules import (
    DUSTHANA_HOUSES,
    KENDRA_HOUSES,
    MARAKA_HOUSES,
    TRIKONA_HOUSES,
    UPACHAYA_HOUSES,
    badhaka_house,
)

CATEGORY_KENDRA = "Kendra"
CATEGORY_TRIKONA = "Trikona"
CATEGORY_DUSTHANA = "Dusthana"
CATEGORY_UPACHAYA = "Upachaya"
CATEGORY_MARAKA = "Maraka"
CATEGORY_BADHAKA = "Badhaka"

CATEGORY_DEFINITIONS = {
    CATEGORY_KENDRA: "Houses 1, 4, 7, 10",
    CATEGORY_TRIKONA: "Houses 1, 5, 9",
    CATEGORY_DUSTHANA: "Houses 6, 8, 12",
    CATEGORY_UPACHAYA: "Houses 3, 6, 10, 11",
    CATEGORY_MARAKA: "Houses 2, 7",
    CATEGORY_BADHAKA: "Movable Lagna: 11th; Fixed Lagna: 9th; Dual Lagna: 7th",
}


def house_categories(house: int, lagna_sign: int) -> List[str]:
    """RULE FUNC_002 + FUNC_003. All categories a house belongs to."""
    cats: List[str] = []
    if house in KENDRA_HOUSES:
        cats.append(CATEGORY_KENDRA)
    if house in TRIKONA_HOUSES:
        cats.append(CATEGORY_TRIKONA)
    if house in DUSTHANA_HOUSES:
        cats.append(CATEGORY_DUSTHANA)
    if house in UPACHAYA_HOUSES:
        cats.append(CATEGORY_UPACHAYA)
    if house in MARAKA_HOUSES:
        cats.append(CATEGORY_MARAKA)
    if house == badhaka_house(lagna_sign):
        cats.append(CATEGORY_BADHAKA)
    return cats


def is_yoga_karaka(houses_owned: List[int]) -> bool:
    """RULE FUNC_004.

    Owning a Kendra other than the 1st alone, together with a Trikona other than
    the 1st alone. The 1st house is both a Kendra and a Trikona, so owning only
    the 1st house does not by itself make a planet a Yoga Karaka.
    """
    owns_kendra = any(h in (4, 7, 10) for h in houses_owned)
    owns_trikona = any(h in (5, 9) for h in houses_owned)
    return owns_kendra and owns_trikona
