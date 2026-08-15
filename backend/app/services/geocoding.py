"""Place and timezone resolution (RULE GEO_001, RULE TIME_001).

PyJHora's bundled place database is not shipped with the wheel, so resolution
uses the Open-Meteo geocoding API (no key required). Every result is fully
overridable by the user, and a failure is reported as a failure rather than
being replaced by a guess.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import requests

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
REQUEST_TIMEOUT = 8.0


class GeocodingError(RuntimeError):
    pass


class TimezoneError(RuntimeError):
    pass


@dataclass
class PlaceResult:
    name: str
    display_name: str
    country: Optional[str]
    admin1: Optional[str]
    latitude: float
    longitude: float
    timezone: Optional[str]
    source: str = "Open-Meteo Geocoding API"


def search_places(query: str, limit: int = 10) -> List[PlaceResult]:
    query = (query or "").strip()
    if len(query) < 2:
        return []

    try:
        response = requests.get(
            GEOCODE_URL,
            params={"name": query, "count": limit, "language": "en", "format": "json"},
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": "PlanetaryStatusAnalyzer/1.0"},
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise GeocodingError(
            "The geocoding service could not be reached. Enter the latitude, "
            "longitude and timezone manually to continue."
        ) from exc
    except ValueError as exc:
        raise GeocodingError("The geocoding service returned an unreadable response.") from exc

    results: List[PlaceResult] = []
    for item in payload.get("results") or []:
        parts = [item.get("name"), item.get("admin1"), item.get("country")]
        display = ", ".join(p for p in parts if p)
        results.append(PlaceResult(
            name=item.get("name") or query,
            display_name=display or query,
            country=item.get("country"),
            admin1=item.get("admin1"),
            latitude=float(item["latitude"]),
            longitude=float(item["longitude"]),
            timezone=item.get("timezone"),
        ))
    return results


_tz_finder = None


def timezone_for_coordinates(latitude: float, longitude: float) -> Optional[str]:
    """IANA timezone name for a coordinate pair, or None if undeterminable."""
    global _tz_finder
    try:
        if _tz_finder is None:
            from timezonefinder import TimezoneFinder
            _tz_finder = TimezoneFinder()
        return _tz_finder.timezone_at(lat=latitude, lng=longitude)
    except Exception:
        return None


def utc_offset_hours(timezone_name: str, year: int, month: int, day: int,
                     hour: int, minute: int, second: int) -> float:
    """RULE TIME_001.

    The offset is evaluated AT the birth instant, so historical daylight-saving
    rules and zone changes are honoured rather than assuming today's offset.
    """
    try:
        zone = ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, ValueError, KeyError) as exc:
        raise TimezoneError(
            f"Unknown timezone '{timezone_name}'. Provide a valid IANA timezone "
            f"name (for example 'Asia/Kolkata') or an explicit UTC offset."
        ) from exc

    try:
        local = datetime(year, month, day, hour, minute, second, tzinfo=zone)
    except ValueError as exc:
        raise TimezoneError(f"Invalid date or time: {exc}") from exc

    offset = local.utcoffset()
    if offset is None:
        raise TimezoneError(
            f"The UTC offset for '{timezone_name}' at the given instant could not "
            f"be determined."
        )
    return offset.total_seconds() / 3600.0


def format_offset(hours: float) -> str:
    sign = "+" if hours >= 0 else "-"
    total_minutes = int(round(abs(hours) * 60))
    return f"UTC{sign}{total_minutes // 60:02d}:{total_minutes % 60:02d}"
