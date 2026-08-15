"""The single boundary between this application and PyJHora.

Nothing outside this module may import ``jhora``. Every function here was
verified against the installed PyJHora 4.8.7 source before being written; see
``docs/PYJHORA_MAPPING.md``.

PyJHora keeps ayanamsha as global module state, so all entry points that depend
on it are serialised behind a lock and the mode is re-applied on every call.
"""
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

from jhora import const, utils
from jhora._package_info import version as _PYJHORA_VERSION
from jhora.horoscope.chart import charts, house, strength
from jhora.panchanga import drik

PYJHORA_VERSION: str = _PYJHORA_VERSION
EPHEMERIS_NAME = "Swiss Ephemeris (pyswisseph) via PyJHora"

# PyJHora mutates process-global ayanamsha state; guard every calculation.
_LOCK = threading.RLock()

AVAILABLE_AYANAMSHA_MODES: List[str] = list(const.available_ayanamsa_modes.keys())
DEFAULT_AYANAMSHA_MODE = "LAHIRI"

# --- Lunar node type -------------------------------------------------------
#
# Traditional Parashari practice and the Indian ephemeris tradition compute
# Rahu and Ketu as MEAN nodes. PyJHora 4.8.7 ships with true nodes enabled
# (const._use_true_nodes_for_rahu_ketu = True), so the setting is applied
# explicitly at import rather than inherited, and is reported with every chart.
#
# Both switches are required: const.set_node_mode rebinds the Swiss Ephemeris
# body ids, and drik.set_planet_list rebuilds the module-level planet table that
# the position and retrogression routines read.
USE_TRUE_NODES = False


def _apply_node_mode(use_true: bool) -> None:
    const.set_node_mode(use_true)
    drik.set_planet_list(set_rahu_ketu_as_true_nodes=use_true)


_apply_node_mode(USE_TRUE_NODES)


def node_type_label() -> str:
    return ("True nodes (Rahu/Ketu osculating)" if const._use_true_nodes_for_rahu_ketu
            else "Mean nodes (Rahu/Ketu), traditional Parashari practice")

_ASC = const._ascendant_symbol  # 'L'


class PyJHoraError(RuntimeError):
    """Raised when PyJHora cannot complete a calculation."""


# ---------------------------------------------------------------------------
# Value objects
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class BirthPlace:
    name: str
    latitude: float
    longitude: float
    timezone_offset_hours: float


@dataclass(frozen=True)
class RawPosition:
    """A body's position in one chart. ``planet`` is 0..8 or 'L' for the Lagna."""
    planet: Any
    sign: int
    degree_in_sign: float

    @property
    def absolute_longitude(self) -> float:
        return (self.sign * 30.0 + self.degree_in_sign) % 360.0


@dataclass
class RawChart:
    """Everything PyJHora produces for one birth moment, in plain structures."""
    julian_day: float
    ayanamsha_mode: str
    ayanamsha_value: float
    positions: Dict[Any, RawPosition]                     # D1
    varga_positions: Dict[int, Dict[Any, RawPosition]]    # factor -> positions
    house_to_planets: List[str]
    retrograde: List[int]
    stationary: List[int]
    combust: List[int]
    speed_info: Dict[int, Tuple[float, ...]]
    graha_yuddha: List[Tuple[int, int, int]]
    aspected_signs: Dict[int, List[int]]
    aspected_houses: Dict[int, List[int]]
    aspected_planets: Dict[int, List[int]]
    bhava_chalita_house: Dict[Any, int]
    bhava_chalita_cusps: List[dict]
    shadbala: Optional[dict]
    shadbala_error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _apply_ayanamsha(mode: str) -> None:
    if mode not in const.available_ayanamsa_modes:
        raise PyJHoraError(f"Unsupported ayanamsha mode: {mode}")
    drik.set_ayanamsa_mode(mode)


def _to_positions(raw: Sequence) -> Dict[Any, RawPosition]:
    """Normalise PyJHora's ``[[planet,(sign,deg)], ...]`` into a dict.

    PyJHora returns a tuple for the rasi chart and a list for varga charts, so
    both are handled.
    """
    out: Dict[Any, RawPosition] = {}
    for entry in raw:
        planet, pos = entry[0], entry[1]
        sign, deg = int(pos[0]), float(pos[1])
        out[planet] = RawPosition(planet=planet, sign=sign, degree_in_sign=deg)
    return out


def julian_day(year: int, month: int, day: int,
               hour: int, minute: int, second: int) -> float:
    """Julian Day for a local civil date/time. The Place carries the offset."""
    return utils.julian_day_number(drik.Date(year, month, day), (hour, minute, second))


def make_place(place: BirthPlace):
    return drik.Place(place.name, place.latitude, place.longitude,
                      place.timezone_offset_hours)


# ---------------------------------------------------------------------------
# Individual capabilities
# ---------------------------------------------------------------------------
def get_ayanamsha_value(jd: float, mode: str) -> float:
    with _LOCK:
        _apply_ayanamsha(mode)
        return float(drik.get_ayanamsa_value(jd))


def get_planet_positions(jd: float, place: BirthPlace, mode: str) -> Dict[Any, RawPosition]:
    with _LOCK:
        _apply_ayanamsha(mode)
        return _to_positions(charts.rasi_chart(jd, make_place(place)))


def get_divisional_chart(jd: float, place: BirthPlace, mode: str,
                         factor: int) -> Dict[Any, RawPosition]:
    with _LOCK:
        _apply_ayanamsha(mode)
        raw = charts.divisional_chart(jd, make_place(place),
                                      divisional_chart_factor=factor)
        return _to_positions(raw)


def get_nakshatra(absolute_longitude: float) -> Tuple[int, int, float]:
    """(nakshatra 1-27, pada 1-4, remaining degrees) from ``drik.nakshatra_pada``."""
    nak, pada, remainder = drik.nakshatra_pada(absolute_longitude % 360.0)
    return int(nak), int(pada), float(remainder)


def get_retrograde_status(jd: float, place: BirthPlace, mode: str) -> List[int]:
    """Speed-based retrogression. PyJHora's own docstring names this the
    accurate source, in preference to the positional approximation in ``charts``."""
    with _LOCK:
        _apply_ayanamsha(mode)
        return [int(p) for p in drik.planets_in_retrograde(jd, make_place(place))]


def get_stationary_status(jd: float, place: BirthPlace, mode: str) -> List[int]:
    with _LOCK:
        _apply_ayanamsha(mode)
        try:
            return [int(p) for p in drik.planets_in_stationary(jd, make_place(place))]
        except Exception:
            return []


def get_speed_info(jd: float, place: BirthPlace, mode: str) -> Dict[int, Tuple[float, ...]]:
    with _LOCK:
        _apply_ayanamsha(mode)
        raw = drik.planets_speed_info(jd, make_place(place))
        return {int(k): tuple(float(x) for x in v) for k, v in raw.items()}


def get_combustion_status(positions_raw: Sequence) -> List[int]:
    return [int(p) for p in charts.planets_in_combustion(positions_raw)]


def get_planetary_war(jd: float, place: BirthPlace, mode: str) -> List[Tuple[int, int, int]]:
    with _LOCK:
        _apply_ayanamsha(mode)
        return [(int(a), int(b), int(c))
                for a, b, c in drik.planets_in_graha_yudh(jd, make_place(place))]


def get_aspects(house_to_planets: List[str]):
    """Graha Drishti. Returns (signs, houses, planets) aspected by each planet."""
    arp, ahp, app = house.graha_drishti_from_chart(house_to_planets)
    signs = {int(p): [int(x) for x in v] for p, v in arp.items() if p != _ASC}
    houses = {int(p): [int(x) for x in v] for p, v in ahp.items() if p != _ASC}
    planets = {int(p): [int(x) for x in v] for p, v in app.items() if p != _ASC}
    return signs, houses, planets


def get_house_positions(jd: float, place: BirthPlace, mode: str):
    """Bhava Chalita from PyJHora. Reported alongside whole-sign, never merged."""
    with _LOCK:
        _apply_ayanamsha(mode)
        p = make_place(place)
        occupancy = {k: int(v) for k, v in charts.bhava_houses(jd, p).items()}
        cusps = []
        for idx, entry in enumerate(charts.bhava_chart(jd, p), start=1):
            sign, (start, mid, end), occupants = entry
            cusps.append({
                "house": idx,
                "sign": int(sign),
                "start": float(start) % 360.0,
                "cusp": float(mid) % 360.0,
                "end": float(end) % 360.0,
                "occupants": [o for o in occupants if o != _ASC],
                "has_lagna": _ASC in occupants,
            })
        return occupancy, cusps


def get_pyjhora_compound_relationships(house_to_planets: List[str]) -> List[List[int]]:
    """PyJHora's own compound-relationship matrix, used to cross-check ours."""
    return house._get_compound_relationships_of_planets(house_to_planets)


def get_shadbala(jd: float, place: BirthPlace, mode: str) -> dict:
    """Full Shadbala with the six-fold breakdown and every sub-component.

    Each list is indexed by planet 0..6 (Sun..Saturn); Shadbala is not defined
    for Rahu and Ketu in PyJHora.
    """
    with _LOCK:
        _apply_ayanamsha(mode)
        p = make_place(place)

        totals = strength.shad_bala(jd, p)
        sthana, kaala, dig, cheshta, naisargika, drik_bala, \
            total_virupa, total_rupa, ratio = totals

        pp_by_varga = {
            d: charts.divisional_chart(jd, p, divisional_chart_factor=d)[:const._pp_count_upto_ketu]
            for d in const.sapthavargaja_factors
        }

        def _seven(values) -> List[float]:
            return [round(float(v), 2) for v in list(values)[:7]]

        sthana_components = {
            "uchcha_bala": _seven(strength._uchcha_bala(pp_by_varga[1])),
            "saptavargaja_bala": _seven(strength._sapthavargaja_bala1(jd, p)),
            "oja_yugma_bala": _seven(strength._ojayugama_bala(pp_by_varga[1], pp_by_varga[9])),
            "kendradi_bala": _seven(strength._kendra_bala(pp_by_varga[1])),
            "drekkana_bala": _seven(strength._dreshkon_bala(pp_by_varga[1])),
        }

        kala_components = {
            "nathonnatha_bala": _seven(strength._nathonnath_bala(jd, p)),
            "paksha_bala": _seven(strength._paksha_bala(jd, p)),
            "tribhaga_bala": _seven(strength._tribhaga_bala(jd, p)),
            "varsha_bala": _seven(strength._abdadhipathi(jd, p)),
            "masa_bala": _seven(strength._masadhipathi(jd, p)),
            "dina_bala": _seven(strength._vaaradhipathi(jd, p)),
            "hora_bala": _seven(strength._hora_bala(jd, p)),
            "ayana_bala": _seven(strength._ayana_bala(jd, p)),
            "yuddha_bala": _seven(strength._yuddha_bala(jd, p)),
        }

        try:
            aspect_matrix = [[round(float(v), 2) for v in row]
                             for row in strength.planet_aspect_relationship_table(
                                 charts.rasi_chart(jd, p))]
        except Exception:
            aspect_matrix = None

        return {
            "sthana_bala": _seven(sthana),
            "sthana_components": sthana_components,
            "dig_bala": _seven(dig),
            "kala_bala": _seven(kaala),
            "kala_components": kala_components,
            "cheshta_bala": _seven(cheshta),
            "naisargika_bala": _seven(naisargika),
            "drik_bala": _seven(drik_bala),
            "drik_bala_aspect_matrix": aspect_matrix,
            "total_virupa": _seven(total_virupa),
            "total_rupa": _seven(total_rupa),
            "required_rupa": [float(v) for v in const.shad_bala_factors],
            "ratio_to_required": _seven(ratio),
        }


def get_supported_yogas() -> dict:
    """PyJHora ships a large yoga module. It is catalogued but not used, because
    it returns verdicts without the per-condition evidence this product requires."""
    return {
        "module": "jhora.horoscope.chart.yoga",
        "used": False,
        "reason": (
            "PyJHora's yoga module returns yoga names without the per-condition "
            "evidence required here. The curated 22-yoga V1 set is evaluated by "
            "this application's own rule engine using PyJHora-derived positions, "
            "lordships, dignity and Graha Drishti."
        ),
    }


# ---------------------------------------------------------------------------
# Composite entry point
# ---------------------------------------------------------------------------
def calculate_chart(jd: float, place: BirthPlace, mode: str,
                    varga_factors: Sequence[int]) -> RawChart:
    """Run every PyJHora calculation this application needs, once."""
    warnings: List[str] = []

    with _LOCK:
        _apply_ayanamsha(mode)
        jhora_place = make_place(place)

        try:
            raw_d1 = charts.rasi_chart(jd, jhora_place)
        except Exception as exc:  # pragma: no cover - depends on ephemeris data
            raise PyJHoraError(f"PyJHora could not calculate the Rasi chart: {exc}") from exc

        positions = _to_positions(raw_d1)
        house_to_planets = list(utils.get_house_planet_list_from_planet_positions(raw_d1))

        varga_positions: Dict[int, Dict[Any, RawPosition]] = {}
        for factor in varga_factors:
            if factor == 1:
                varga_positions[1] = positions
                continue
            try:
                varga_positions[factor] = _to_positions(
                    charts.divisional_chart(jd, jhora_place, divisional_chart_factor=factor))
            except Exception as exc:
                warnings.append(f"Divisional chart D{factor} unavailable: {exc}")

        ayanamsha_value = float(drik.get_ayanamsa_value(jd))

        try:
            retrograde = [int(p) for p in drik.planets_in_retrograde(jd, jhora_place)]
        except Exception as exc:
            retrograde = []
            warnings.append(f"Retrograde status unavailable: {exc}")

        try:
            stationary = [int(p) for p in drik.planets_in_stationary(jd, jhora_place)]
        except Exception:
            stationary = []

        try:
            combust = [int(p) for p in charts.planets_in_combustion(raw_d1)]
        except Exception as exc:
            combust = []
            warnings.append(f"Combustion status unavailable: {exc}")

        try:
            speed_info = {int(k): tuple(float(x) for x in v)
                          for k, v in drik.planets_speed_info(jd, jhora_place).items()}
        except Exception:
            speed_info = {}

        try:
            graha_yuddha = [(int(a), int(b), int(c))
                            for a, b, c in drik.planets_in_graha_yudh(jd, jhora_place)]
        except Exception as exc:
            graha_yuddha = []
            warnings.append(f"Graha Yuddha unavailable: {exc}")

        aspected_signs, aspected_houses, aspected_planets = get_aspects(house_to_planets)

        try:
            bhava_house, bhava_cusps = get_house_positions(jd, place, mode)
        except Exception as exc:
            bhava_house, bhava_cusps = {}, []
            warnings.append(f"Bhava Chalita unavailable: {exc}")

        shadbala: Optional[dict] = None
        shadbala_error: Optional[str] = None
        try:
            shadbala = get_shadbala(jd, place, mode)
        except Exception as exc:
            shadbala_error = str(exc)
            warnings.append(f"Shadbala unavailable: {exc}")

    return RawChart(
        julian_day=jd,
        ayanamsha_mode=mode,
        ayanamsha_value=ayanamsha_value,
        positions=positions,
        varga_positions=varga_positions,
        house_to_planets=house_to_planets,
        retrograde=retrograde,
        stationary=stationary,
        combust=combust,
        speed_info=speed_info,
        graha_yuddha=graha_yuddha,
        aspected_signs=aspected_signs,
        aspected_houses=aspected_houses,
        aspected_planets=aspected_planets,
        bhava_chalita_house=bhava_house,
        bhava_chalita_cusps=bhava_cusps,
        shadbala=shadbala,
        shadbala_error=shadbala_error,
        warnings=warnings,
    )


def engine_info(mode: str) -> dict:
    return {
        "engine": "PyJHora",
        "pyjhora_version": PYJHORA_VERSION,
        "ephemeris": EPHEMERIS_NAME,
        "zodiac_type": "Sidereal (Nirayana)",
        "ayanamsha_mode": mode,
        "house_system_for_rules": "Whole sign (Rashi) counted from the Lagna sign",
        "house_system_secondary": (
            "Bhava Chalita from PyJHora "
            f"(bhaava_madhya_method={const.bhaava_madhya_method}, "
            "KN Rao / Parashari cusp-15, cusp, cusp+15)"
        ),
        "node_type": node_type_label(),
        "available_ayanamsha_modes": AVAILABLE_AYANAMSHA_MODES,
    }
