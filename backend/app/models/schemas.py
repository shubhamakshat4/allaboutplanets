"""Pydantic request/response models."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class BirthDetails(BaseModel):
    year: int = Field(..., ge=1, le=9999)
    month: int = Field(..., ge=1, le=12)
    day: int = Field(..., ge=1, le=31)
    hour: int = Field(..., ge=0, le=23)
    minute: int = Field(..., ge=0, le=59)
    second: int = Field(0, ge=0, le=59)

    place_name: str = Field(..., min_length=1, max_length=200)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)

    timezone: Optional[str] = Field(
        None, description="IANA timezone name, e.g. 'Asia/Kolkata'.")
    utc_offset_hours: Optional[float] = Field(
        None, ge=-14.0, le=14.0,
        description="Explicit UTC offset. Overrides the IANA timezone when given.")

    ayanamsha_mode: str = Field("LAHIRI")

    @field_validator("place_name")
    @classmethod
    def _strip(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Place name is required.")
        return v

    def validate_calendar(self) -> None:
        from datetime import date
        try:
            date(self.year, self.month, self.day)
        except ValueError as exc:
            raise ValueError(f"Invalid date: {exc}") from exc


class PlaceSearchResult(BaseModel):
    name: str
    display_name: str
    country: Optional[str] = None
    admin1: Optional[str] = None
    latitude: float
    longitude: float
    timezone: Optional[str] = None
    source: str


class PlaceSearchResponse(BaseModel):
    results: List[PlaceSearchResult]


class TimezoneResolveRequest(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    year: int
    month: int
    day: int
    hour: int = 12
    minute: int = 0
    second: int = 0


class TimezoneResolveResponse(BaseModel):
    timezone: Optional[str]
    utc_offset_hours: Optional[float]
    utc_offset_label: Optional[str]
    resolved: bool
    message: Optional[str] = None


class CalculationSettings(BaseModel):
    engine: str
    pyjhora_version: str
    ephemeris: str
    zodiac_type: str
    ayanamsha_mode: str
    ayanamsha_value: float
    ayanamsha_value_dms: str
    house_system_for_rules: str
    house_system_secondary: str
    node_type: str
    julian_day: float


class ResolvedBirthDetails(BaseModel):
    date_label: str
    time_label: str
    place_name: str
    latitude: float
    longitude: float
    latitude_label: str
    longitude_label: str
    timezone: Optional[str]
    utc_offset_hours: float
    utc_offset_label: str
    timezone_source: str


class ChartResponse(BaseModel):
    chart_id: str
    birth: ResolvedBirthDetails
    settings: CalculationSettings
    lagna: Dict[str, Any]
    planets: List[Dict[str, Any]]
    houses: List[Dict[str, Any]]
    bhava_chalita: List[Dict[str, Any]]
    yogas: List[Dict[str, Any]]
    warnings: List[str] = []


class PlanetAnalysisResponse(BaseModel):
    chart_id: str
    analysis: Dict[str, Any]


class AyanamshaOption(BaseModel):
    value: str
    label: str


class MetaResponse(BaseModel):
    pyjhora_version: str
    ephemeris: str
    ayanamsha_modes: List[AyanamshaOption]
    default_ayanamsha: str
    planets: List[Dict[str, Any]]
    varga_factors: List[Dict[str, Any]]
    pyjhora_yoga_module: Dict[str, Any]


class RuleDoc(BaseModel):
    rule_id: str
    name: str
    description: str
    source: str
    inputs: List[str]
    calculation: str
    output: str


class RulesResponse(BaseModel):
    rules: List[RuleDoc]


class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None
