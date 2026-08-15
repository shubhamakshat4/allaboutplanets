"""REST API. Thin transport layer over the astrology engines."""
from __future__ import annotations

import hashlib
import json
from collections import OrderedDict
from threading import RLock
from typing import Dict, List

from fastapi import APIRouter, HTTPException, Query

from ..astrology import pyjhora_adapter as adapter
from ..astrology import yoga_engine
from ..astrology.chart_calculator import ChartContext, build_chart_context
from ..astrology.planet_analyzer import analyze_planet, planetary_master_table
from ..astrology.rules import planetary_rules as pr
from ..astrology.rules.registry import all_rules
from ..models.schemas import (
    AyanamshaOption, BirthDetails, CalculationSettings, ChartResponse,
    MetaResponse, PlaceSearchResponse, PlaceSearchResult, PlanetAnalysisResponse,
    ResolvedBirthDetails, RuleDoc, RulesResponse, TimezoneResolveRequest,
    TimezoneResolveResponse,
)
from ..services import geocoding

router = APIRouter()

# --- Chart cache -----------------------------------------------------------
# Charts are deterministic, so the id is a hash of the inputs: recalculating the
# same birth details always yields the same id and the same numbers.
_CACHE_LIMIT = 64
_cache: "OrderedDict[str, ChartContext]" = OrderedDict()
_cache_meta: Dict[str, dict] = {}
_cache_lock = RLock()


def _chart_id(details: BirthDetails, offset: float) -> str:
    # The timezone name and whether the offset was explicit are part of the key.
    # They do not change the numbers, but they do change the provenance the UI
    # displays, and a cached chart must never show a source the caller did not use.
    payload = json.dumps({
        "y": details.year, "mo": details.month, "d": details.day,
        "h": details.hour, "mi": details.minute, "s": details.second,
        "lat": round(details.latitude, 6), "lon": round(details.longitude, 6),
        "off": round(offset, 6), "ay": details.ayanamsha_mode,
        "place": details.place_name,
        "tz": details.timezone or "",
        "explicit_off": details.utc_offset_hours is not None,
    }, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]


def _store(chart_id: str, ctx: ChartContext, meta: dict) -> None:
    with _cache_lock:
        _cache[chart_id] = ctx
        _cache_meta[chart_id] = meta
        _cache.move_to_end(chart_id)
        while len(_cache) > _CACHE_LIMIT:
            old, _ = _cache.popitem(last=False)
            _cache_meta.pop(old, None)


def _load(chart_id: str) -> ChartContext:
    with _cache_lock:
        ctx = _cache.get(chart_id)
        if ctx is None:
            raise HTTPException(
                status_code=404,
                detail="This chart is no longer held on the server. "
                       "Regenerate it from the birth details.")
        _cache.move_to_end(chart_id)
        return ctx


# --- Metadata --------------------------------------------------------------
@router.get("/meta", response_model=MetaResponse)
def get_meta() -> MetaResponse:
    return MetaResponse(
        pyjhora_version=adapter.PYJHORA_VERSION,
        ephemeris=adapter.EPHEMERIS_NAME,
        ayanamsha_modes=[
            AyanamshaOption(value=m, label=m.replace("_", " ").title())
            for m in adapter.AVAILABLE_AYANAMSHA_MODES
        ],
        default_ayanamsha=adapter.DEFAULT_AYANAMSHA_MODE,
        planets=[
            {"id": p, "name": pr.PLANET_NAMES[p], "sanskrit": pr.PLANET_SANSKRIT[p],
             "symbol": pr.PLANET_SYMBOLS[p]}
            for p in pr.ALL_PLANETS
        ],
        varga_factors=[
            {"factor": f, "name": pr.VARGA_NAMES[f]} for f in pr.VARGA_FACTORS
        ],
        pyjhora_yoga_module=adapter.get_supported_yogas(),
    )


@router.get("/rules", response_model=RulesResponse)
def get_rules() -> RulesResponse:
    return RulesResponse(rules=[RuleDoc(**r.to_dict()) for r in all_rules()])


# --- Geography -------------------------------------------------------------
@router.get("/places", response_model=PlaceSearchResponse)
def search_places(q: str = Query(..., min_length=2, max_length=120)) -> PlaceSearchResponse:
    try:
        results = geocoding.search_places(q)
    except geocoding.GeocodingError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return PlaceSearchResponse(results=[
        PlaceSearchResult(**vars(r)) for r in results
    ])


@router.post("/timezone", response_model=TimezoneResolveResponse)
def resolve_timezone(payload: TimezoneResolveRequest) -> TimezoneResolveResponse:
    tz = geocoding.timezone_for_coordinates(payload.latitude, payload.longitude)
    if tz is None:
        return TimezoneResolveResponse(
            timezone=None, utc_offset_hours=None, utc_offset_label=None,
            resolved=False,
            message="The timezone for these coordinates could not be determined. "
                    "Enter the UTC offset manually.")
    try:
        offset = geocoding.utc_offset_hours(
            tz, payload.year, payload.month, payload.day,
            payload.hour, payload.minute, payload.second)
    except geocoding.TimezoneError as exc:
        return TimezoneResolveResponse(
            timezone=tz, utc_offset_hours=None, utc_offset_label=None,
            resolved=False, message=str(exc))

    return TimezoneResolveResponse(
        timezone=tz,
        utc_offset_hours=offset,
        utc_offset_label=geocoding.format_offset(offset),
        resolved=True,
        message=f"Offset evaluated at the birth instant, so historical "
                f"daylight-saving rules for {tz} are applied.")


# --- Chart -----------------------------------------------------------------
@router.post("/chart", response_model=ChartResponse)
def create_chart(details: BirthDetails) -> ChartResponse:
    try:
        details.validate_calendar()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if details.ayanamsha_mode not in adapter.AVAILABLE_AYANAMSHA_MODES:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported ayanamsha mode '{details.ayanamsha_mode}'. "
                   f"Supported: {', '.join(adapter.AVAILABLE_AYANAMSHA_MODES)}")

    # --- resolve the UTC offset (RULE TIME_001) ---------------------------
    timezone_source: str
    if details.utc_offset_hours is not None:
        offset = float(details.utc_offset_hours)
        timezone_source = "Explicit UTC offset supplied by the user"
    elif details.timezone:
        try:
            offset = geocoding.utc_offset_hours(
                details.timezone, details.year, details.month, details.day,
                details.hour, details.minute, details.second)
        except geocoding.TimezoneError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        timezone_source = (f"IANA timezone '{details.timezone}', offset evaluated "
                           f"at the birth instant")
    else:
        raise HTTPException(
            status_code=422,
            detail="A timezone or an explicit UTC offset is required. "
                   "Nothing is assumed.")

    chart_id = _chart_id(details, offset)

    with _cache_lock:
        cached = _cache.get(chart_id)
    if cached is not None:
        return _build_response(chart_id, cached, _cache_meta[chart_id])

    place = adapter.BirthPlace(
        name=details.place_name,
        latitude=details.latitude,
        longitude=details.longitude,
        timezone_offset_hours=offset,
    )

    jd = adapter.julian_day(details.year, details.month, details.day,
                            details.hour, details.minute, details.second)

    try:
        ctx = build_chart_context(jd, place, details.ayanamsha_mode)
    except adapter.PyJHoraError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=500,
            detail=f"The chart could not be calculated: {exc}") from exc

    meta = {
        "birth": ResolvedBirthDetails(
            date_label=f"{details.day:02d}/{details.month:02d}/{details.year:04d}",
            time_label=f"{details.hour:02d}:{details.minute:02d}:{details.second:02d}",
            place_name=details.place_name,
            latitude=details.latitude,
            longitude=details.longitude,
            latitude_label=_coord_label(details.latitude, "N", "S"),
            longitude_label=_coord_label(details.longitude, "E", "W"),
            timezone=details.timezone,
            utc_offset_hours=offset,
            utc_offset_label=geocoding.format_offset(offset),
            timezone_source=timezone_source,
        ),
    }

    _store(chart_id, ctx, meta)
    return _build_response(chart_id, ctx, meta)


@router.get("/chart/{chart_id}", response_model=ChartResponse)
def get_chart(chart_id: str) -> ChartResponse:
    ctx = _load(chart_id)
    return _build_response(chart_id, ctx, _cache_meta[chart_id])


@router.get("/chart/{chart_id}/planet/{planet_id}",
            response_model=PlanetAnalysisResponse)
def get_planet_analysis(chart_id: str, planet_id: int) -> PlanetAnalysisResponse:
    ctx = _load(chart_id)
    if planet_id not in pr.ALL_PLANETS:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown planet id {planet_id}. Valid ids are 0 (Sun) to 8 (Ketu).")
    try:
        analysis = analyze_planet(ctx, planet_id)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=500,
            detail=f"The analysis for this planet could not be produced: {exc}") from exc
    return PlanetAnalysisResponse(chart_id=chart_id, analysis=analysis)


# --- Response assembly -----------------------------------------------------
def _build_response(chart_id: str, ctx: ChartContext, meta: dict) -> ChartResponse:
    yogas = yoga_engine.evaluate_all_yogas(ctx)

    houses: List[dict] = []
    for h in range(1, 13):
        sign = ctx.house_sign[h]
        lord = ctx.house_lord[h]
        occupants = ctx.planets_in_sign.get(sign, [])
        houses.append({
            "house": h,
            "sign": sign,
            "signName": pr.sign_name(sign),
            "signSanskrit": pr.SIGN_SANSKRIT[sign],
            "lord": lord,
            "lordName": pr.planet_name(lord),
            "planets": [
                {"planet": p, "planetName": pr.planet_name(p),
                 "symbol": pr.PLANET_SYMBOLS[p],
                 "degreeDms": pr.to_dms(ctx.positions[p].degree_in_sign),
                 "retrograde": ctx.is_retrograde(p),
                 "combust": ctx.is_combust(p)}
                for p in occupants
            ],
            "hasLagna": h == 1,
        })

    settings = CalculationSettings(
        engine=ctx.engine_info["engine"],
        pyjhora_version=ctx.engine_info["pyjhora_version"],
        ephemeris=ctx.engine_info["ephemeris"],
        zodiac_type=ctx.engine_info["zodiac_type"],
        ayanamsha_mode=ctx.ayanamsha_mode,
        ayanamsha_value=round(ctx.ayanamsha_value, 6),
        ayanamsha_value_dms=pr.to_dms(ctx.ayanamsha_value),
        house_system_for_rules=ctx.engine_info["house_system_for_rules"],
        house_system_secondary=ctx.engine_info["house_system_secondary"],
        node_type=ctx.engine_info["node_type"],
        julian_day=ctx.julian_day,
    )

    return ChartResponse(
        chart_id=chart_id,
        birth=meta["birth"],
        settings=settings,
        lagna={
            "sign": ctx.lagna_sign,
            "signName": pr.sign_name(ctx.lagna_sign),
            "signSanskrit": pr.SIGN_SANSKRIT[ctx.lagna_sign],
            "degree": round(ctx.lagna_degree_in_sign, 6),
            "degreeDms": pr.to_dms(ctx.lagna_degree_in_sign),
            "lord": ctx.house_lord[1],
            "lordName": pr.planet_name(ctx.house_lord[1]),
            "modality": pr.sign_modality(ctx.lagna_sign),
            "nakshatra": pr.NAKSHATRA_NAMES[ctx.lagna_nakshatra[0] - 1],
            "pada": ctx.lagna_nakshatra[1],
            "nakshatraLordName": pr.planet_name(ctx.lagna_nakshatra[2]),
        },
        planets=planetary_master_table(ctx),
        houses=houses,
        bhava_chalita=ctx.bhava_chalita_cusps,
        yogas=yogas,
        warnings=ctx.warnings,
    )


def _coord_label(value: float, positive: str, negative: str) -> str:
    hemisphere = positive if value >= 0 else negative
    return f"{pr.to_dms(abs(value))} {hemisphere}"
