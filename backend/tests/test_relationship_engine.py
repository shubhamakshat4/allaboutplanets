"""Panchadha Maitri tests (RULES MAITRI_001, MAITRI_002, MAITRI_003).

Includes a cross-check that our independent implementation agrees with
PyJHora's own compound-relationship matrix for a real chart.
"""
import pytest

from app.astrology import pyjhora_adapter as adapter
from app.astrology.relationship_engine import compound_matrix, relationship
from app.astrology.rules import maitri_rules as mr
from app.astrology.rules.planetary_rules import (
    ALL_PLANETS, JUPITER, KETU, MARS, MERCURY, MOON, RAHU, SATURN, SUN, VENUS,
)

from .conftest import make_context


# --- The combination table itself -----------------------------------------
@pytest.mark.parametrize("natural,temporary,expected", [
    (mr.NATURAL_FRIEND, mr.TEMPORARY_FRIEND, mr.ATI_MITRA),
    (mr.NATURAL_NEUTRAL, mr.TEMPORARY_FRIEND, mr.MITRA),
    (mr.NATURAL_FRIEND, mr.TEMPORARY_ENEMY, mr.SAMA),
    (mr.NATURAL_ENEMY, mr.TEMPORARY_FRIEND, mr.SAMA),
    (mr.NATURAL_NEUTRAL, mr.TEMPORARY_ENEMY, mr.SHATRU),
    (mr.NATURAL_ENEMY, mr.TEMPORARY_ENEMY, mr.ATI_SHATRU),
])
def test_panchadha_table(natural, temporary, expected):
    assert mr.panchadha_maitri(natural, temporary) == expected


def test_panchadha_covers_every_combination():
    """All six natural x temporary combinations must resolve."""
    for natural in (mr.NATURAL_FRIEND, mr.NATURAL_NEUTRAL, mr.NATURAL_ENEMY):
        for temporary in (mr.TEMPORARY_FRIEND, mr.TEMPORARY_ENEMY):
            assert mr.panchadha_maitri(natural, temporary) in mr.PANCHADHA_ORDER


# --- Temporary relationship ------------------------------------------------
@pytest.mark.parametrize("offset,expected", [
    (0, mr.TEMPORARY_ENEMY),    # same sign is the 1st, a temporary enemy position
    (1, mr.TEMPORARY_FRIEND),   # 2nd
    (2, mr.TEMPORARY_FRIEND),   # 3rd
    (3, mr.TEMPORARY_FRIEND),   # 4th
    (4, mr.TEMPORARY_ENEMY),    # 5th
    (5, mr.TEMPORARY_ENEMY),    # 6th
    (6, mr.TEMPORARY_ENEMY),    # 7th
    (7, mr.TEMPORARY_ENEMY),    # 8th
    (8, mr.TEMPORARY_ENEMY),    # 9th
    (9, mr.TEMPORARY_FRIEND),   # 10th
    (10, mr.TEMPORARY_FRIEND),  # 11th
    (11, mr.TEMPORARY_FRIEND),  # 12th
])
def test_temporary_relationship_by_offset(offset, expected):
    for base in range(12):
        assert mr.temporary_relationship(base, (base + offset) % 12) == expected


def test_temporary_offset_house_is_one_based():
    assert mr.temporary_offset_house(0, 0) == 1
    assert mr.temporary_offset_house(0, 1) == 2
    assert mr.temporary_offset_house(3, 2) == 12


def test_temporary_partition_is_complete_and_disjoint():
    friends = set(mr.TEMPORARY_FRIEND_OFFSETS)
    enemies = set(mr.TEMPORARY_ENEMY_OFFSETS)
    assert friends | enemies == set(range(12))
    assert friends & enemies == set()


# --- Natural relationship --------------------------------------------------
def test_natural_relationship_is_defined_for_all_pairs():
    for a in ALL_PLANETS:
        for b in ALL_PLANETS:
            result = mr.natural_relationship(a, b)
            assert result in (mr.NATURAL_FRIEND, mr.NATURAL_NEUTRAL,
                              mr.NATURAL_ENEMY, mr.SELF)


def test_natural_relationship_self():
    for p in ALL_PLANETS:
        assert mr.natural_relationship(p, p) == mr.SELF


@pytest.mark.parametrize("a,b,expected", [
    # Classical Parashari natural friendships, as encoded by PyJHora.
    (SUN, MOON, mr.NATURAL_FRIEND),
    (SUN, JUPITER, mr.NATURAL_FRIEND),
    (SUN, VENUS, mr.NATURAL_ENEMY),
    (SUN, SATURN, mr.NATURAL_ENEMY),
    (MOON, MERCURY, mr.NATURAL_FRIEND),
    (MARS, MERCURY, mr.NATURAL_ENEMY),
    (JUPITER, MERCURY, mr.NATURAL_ENEMY),
    (VENUS, SATURN, mr.NATURAL_FRIEND),
    (SATURN, MARS, mr.NATURAL_ENEMY),
])
def test_known_natural_relationships(a, b, expected):
    assert mr.natural_relationship(a, b) == expected


def test_nodes_have_defined_natural_relationships():
    """Rahu and Ketu are covered by the selected rule set, so nothing is guessed."""
    for node in (RAHU, KETU):
        for other in ALL_PLANETS:
            if other == node:
                continue
            assert mr.natural_relationship(node, other) != "Not defined in selected rule set"


# --- Engine output ---------------------------------------------------------
def test_relationship_record_carries_evidence(ctx):
    rec = relationship(ctx, JUPITER, SATURN)
    assert rec["planetA"] == JUPITER
    assert rec["planetB"] == SATURN
    assert rec["panchadhaMaitri"] in mr.PANCHADHA_ORDER
    assert "naturalRule" in rec["evidence"]
    assert "temporaryRule" in rec["evidence"]
    assert "combination" in rec["evidence"]
    assert rec["sources"]["panchadha"]["rule"] == "MAITRI_003"


def test_self_relationship_is_marked(ctx):
    rec = relationship(ctx, JUPITER, JUPITER)
    assert rec["panchadhaMaitri"] == mr.SELF


def test_panchadha_derives_from_its_own_components(ctx):
    """The reported Panchadha must equal the table applied to the reported parts."""
    for a in ALL_PLANETS:
        for b in ALL_PLANETS:
            if a == b:
                continue
            rec = relationship(ctx, a, b)
            expected = mr.panchadha_maitri(rec["naturalRelationship"],
                                           rec["temporaryRelationship"])
            assert rec["panchadhaMaitri"] == expected


# --- Cross-check against PyJHora ------------------------------------------
def test_matches_pyjhora_compound_matrix(ctx):
    """Our engine and PyJHora's must agree on every pair of a real chart."""
    theirs = adapter.get_pyjhora_compound_relationships(ctx.house_to_planets)
    ours = compound_matrix(ctx)

    for a in ALL_PLANETS:
        for b in ALL_PLANETS:
            if a == b:
                continue
            expected = mr.PYJHORA_COMPOUND_CODE_NAMES[theirs[a][b]]
            assert ours[a][b] == expected, (
                f"Mismatch for {a}->{b}: ours={ours[a][b]} pyjhora={expected}")


@pytest.mark.parametrize("y,mo,d,h,mi,lat,lon,tz", [
    (1975, 1, 3, 4, 15, 51.5074, -0.1278, 0.0),
    (2001, 9, 20, 23, 45, 40.7128, -74.0060, -4.0),
    (1962, 11, 30, 6, 5, -33.8688, 151.2093, 10.0),
])
def test_matches_pyjhora_across_charts(y, mo, d, h, mi, lat, lon, tz):
    context = make_context(y, mo, d, h, mi, 0, lat, lon, tz)
    theirs = adapter.get_pyjhora_compound_relationships(context.house_to_planets)
    ours = compound_matrix(context)
    for a in ALL_PLANETS:
        for b in ALL_PLANETS:
            if a == b:
                continue
            assert ours[a][b] == mr.PYJHORA_COMPOUND_CODE_NAMES[theirs[a][b]]
