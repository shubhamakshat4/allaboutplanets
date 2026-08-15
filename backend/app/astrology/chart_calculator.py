"""Builds the enriched ChartContext that every downstream engine consumes.

This layer contains no interpretation. It converts PyJHora output plus the
project's own deterministic rules into typed, reusable facts.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from . import combustion_engine
from . import pyjhora_adapter as adapter
from .rules import planetary_rules as pr
from .rules.planetary_rules import LAGNA


@dataclass(frozen=True)
class PlanetPosition:
    planet: int
    sign: int
    degree_in_sign: float
    absolute_longitude: float
    bhava: int                    # whole sign, RULE HOUSE_001
    bhava_chalita: Optional[int]
    nakshatra: int                # 1-27
    pada: int                     # 1-4
    nakshatra_lord: int
    nakshatra_remaining_degrees: float


@dataclass
class ChartContext:
    """Everything known about one chart. Computed once, reused everywhere."""
    # Provenance
    julian_day: float
    ayanamsha_mode: str
    ayanamsha_value: float
    engine_info: dict

    # Core geometry
    lagna_sign: int
    lagna_degree_in_sign: float
    lagna_nakshatra: Tuple[int, int, int]     # (nakshatra, pada, lord)
    positions: Dict[int, PlanetPosition]      # 0..8

    # Sign / house maps
    sign_lords: List[int]
    house_sign: Dict[int, int]                # house 1-12 -> sign index
    house_lord: Dict[int, int]                # house 1-12 -> planet
    planets_in_sign: Dict[int, List[int]]
    houses_owned: Dict[int, List[int]]        # planet -> houses owned

    # Divisional charts
    varga_positions: Dict[int, Dict[Any, adapter.RawPosition]]

    # State
    retrograde: List[int]
    stationary: List[int]
    combust: List[int]                        # RULE COMBUST_001 (authoritative here)
    combust_pyjhora: List[int]                # PyJHora's verdict, reported for comparison
    speed_info: Dict[int, Tuple[float, ...]]
    graha_yuddha: List[Tuple[int, int, int]]

    # Drishti (from PyJHora)
    aspected_signs: Dict[int, List[int]]
    aspected_houses: Dict[int, List[int]]
    aspected_planets: Dict[int, List[int]]
    aspecting_planets: Dict[int, List[int]]   # inverted: who aspects this planet

    # Bhava Chalita (reported separately from the whole-sign frame)
    bhava_chalita_cusps: List[dict]

    # Strength
    shadbala: Optional[dict]
    shadbala_error: Optional[str]

    # Raw handle for engines that need PyJHora's own house/planet string list
    house_to_planets: List[str]

    warnings: List[str] = field(default_factory=list)

    # ---- convenience -------------------------------------------------------
    def sign_of(self, planet: int) -> int:
        return self.positions[planet].sign

    def bhava_of(self, planet: int) -> int:
        return self.positions[planet].bhava

    def house_from(self, reference_sign: int, target_sign: int) -> int:
        """1-based count of signs from ``reference_sign`` to ``target_sign``."""
        return ((target_sign - reference_sign) % 12) + 1

    def house_from_planet(self, reference_planet: int, target_planet: int) -> int:
        return self.house_from(self.sign_of(reference_planet), self.sign_of(target_planet))

    def lord_of_sign(self, sign: int) -> int:
        return self.sign_lords[sign % 12]

    def planets_in_house(self, house: int) -> List[int]:
        return list(self.planets_in_sign.get(self.house_sign[house], []))

    def is_retrograde(self, planet: int) -> bool:
        return planet in self.retrograde

    def is_combust(self, planet: int) -> bool:
        return planet in self.combust

    def varga_sign(self, planet: int, factor: int) -> Optional[int]:
        chart = self.varga_positions.get(factor)
        if not chart or planet not in chart:
            return None
        return chart[planet].sign

    def varga_degree(self, planet: int, factor: int) -> Optional[float]:
        chart = self.varga_positions.get(factor)
        if not chart or planet not in chart:
            return None
        return chart[planet].degree_in_sign


def build_chart_context(jd: float, place: adapter.BirthPlace,
                        ayanamsha_mode: str) -> ChartContext:
    raw = adapter.calculate_chart(jd, place, ayanamsha_mode, pr.VARGA_FACTORS)

    lagna = raw.positions[LAGNA]
    lagna_sign = lagna.sign

    positions: Dict[int, PlanetPosition] = {}
    for planet in pr.ALL_PLANETS:
        rp = raw.positions.get(planet)
        if rp is None:
            raise adapter.PyJHoraError(
                f"PyJHora returned no position for planet id {planet}")
        abs_long = rp.absolute_longitude
        nak, pada, remaining = adapter.get_nakshatra(abs_long)
        positions[planet] = PlanetPosition(
            planet=planet,
            sign=rp.sign,
            degree_in_sign=rp.degree_in_sign,
            absolute_longitude=abs_long,
            bhava=((rp.sign - lagna_sign) % 12) + 1,          # RULE HOUSE_001
            bhava_chalita=raw.bhava_chalita_house.get(planet),
            nakshatra=nak,
            pada=pada,
            nakshatra_lord=pr.nakshatra_lord(nak),
            nakshatra_remaining_degrees=remaining,
        )

    lagna_nak, lagna_pada, _ = adapter.get_nakshatra(lagna.absolute_longitude)

    house_sign = {h: (lagna_sign + h - 1) % 12 for h in range(1, 13)}
    house_lord = {h: pr.SIGN_LORDS[s] for h, s in house_sign.items()}

    planets_in_sign: Dict[int, List[int]] = {s: [] for s in range(12)}
    for planet, pos in positions.items():
        planets_in_sign[pos.sign].append(planet)

    houses_owned: Dict[int, List[int]] = {}
    for planet in pr.ALL_PLANETS:
        houses_owned[planet] = sorted(
            h for h, lord in house_lord.items() if lord == planet)

    # Invert Graha Drishti so each planet knows who aspects it.
    aspecting: Dict[int, List[int]] = {p: [] for p in pr.ALL_PLANETS}
    for source, targets in raw.aspected_planets.items():
        for target in targets:
            if target in aspecting and source not in aspecting[target]:
                aspecting[target].append(source)
    for p in aspecting:
        aspecting[p].sort()

    return ChartContext(
        julian_day=raw.julian_day,
        ayanamsha_mode=raw.ayanamsha_mode,
        ayanamsha_value=raw.ayanamsha_value,
        engine_info=adapter.engine_info(raw.ayanamsha_mode),
        lagna_sign=lagna_sign,
        lagna_degree_in_sign=lagna.degree_in_sign,
        lagna_nakshatra=(lagna_nak, lagna_pada, pr.nakshatra_lord(lagna_nak)),
        positions=positions,
        sign_lords=list(pr.SIGN_LORDS),
        house_sign=house_sign,
        house_lord=house_lord,
        planets_in_sign=planets_in_sign,
        houses_owned=houses_owned,
        varga_positions=raw.varga_positions,
        retrograde=raw.retrograde,
        stationary=raw.stationary,
        combust=combustion_engine.combust_planets(
            {p: pos.absolute_longitude for p, pos in positions.items()},
            raw.retrograde),
        combust_pyjhora=raw.combust,
        speed_info=raw.speed_info,
        graha_yuddha=raw.graha_yuddha,
        aspected_signs=raw.aspected_signs,
        aspected_houses=raw.aspected_houses,
        aspected_planets=raw.aspected_planets,
        aspecting_planets=aspecting,
        bhava_chalita_cusps=raw.bhava_chalita_cusps,
        shadbala=raw.shadbala,
        shadbala_error=raw.shadbala_error,
        house_to_planets=raw.house_to_planets,
        warnings=list(raw.warnings),
    )
