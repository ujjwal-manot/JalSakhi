"""Pydantic v2 schemas for request/response validation."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# WHO limits (mg/L unless noted)
# ---------------------------------------------------------------------------
WHO_LIMITS: dict[str, tuple[float, str]] = {
    "NH3": (0.5, "mg/L"),
    "Pb": (10.0, "ppb"),
    "As": (10.0, "ppb"),
    "NO3": (50.0, "mg/L"),
    "Fe": (0.3, "mg/L"),
}

VALID_SYMBOLS = set(WHO_LIMITS.keys())


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class SourceType(str, Enum):
    TAP = "tap"
    BOREWELL = "borewell"
    HANDPUMP = "handpump"
    OPENWELL = "openwell"
    RIVER = "river"


class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    RETEST = "RETEST"


class Severity(str, Enum):
    WARNING = "warning"
    CRITICAL = "critical"


# ---------------------------------------------------------------------------
# Contaminant
# ---------------------------------------------------------------------------
class ContaminantReadingInput(BaseModel):
    """Input for a single contaminant reading."""

    symbol: str = Field(..., description="Contaminant symbol (NH3/Pb/As/NO3/Fe)")
    value: float = Field(..., ge=0, description="Measured value")
    unit: str = Field(..., description="Unit of measurement (mg/L or ppb)")
    confidence: Confidence

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        if v not in VALID_SYMBOLS:
            raise ValueError(
                f"Invalid contaminant symbol '{v}'. Must be one of: {', '.join(sorted(VALID_SYMBOLS))}"
            )
        return v

    @field_validator("unit")
    @classmethod
    def validate_unit(cls, v: str) -> str:
        if v not in ("mg/L", "ppb"):
            raise ValueError("Unit must be 'mg/L' or 'ppb'")
        return v


class ContaminantReadingSchema(BaseModel):
    """Full contaminant reading response."""

    id: int
    test_id: int
    symbol: str
    value: float
    unit: str
    exceeds_who_limit: bool
    confidence: Confidence

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Test result
# ---------------------------------------------------------------------------
class TestSubmission(BaseModel):
    """Input schema for submitting a water quality test."""

    device_id: int
    timestamp: datetime
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    source_type: SourceType
    tester_name: str = Field(..., min_length=1, max_length=128)
    temperature: Optional[float] = None
    ph: Optional[float] = Field(None, ge=0, le=14)
    tds: Optional[float] = Field(None, ge=0)
    raw_voltammogram: Optional[list[list[float]]] = None
    contaminant_readings: list[ContaminantReadingInput] = Field(default_factory=list)


class TestResponse(BaseModel):
    """Full test result response."""

    id: int
    device_id: int
    timestamp: datetime
    latitude: float
    longitude: float
    source_type: SourceType
    tester_name: str
    temperature: Optional[float] = None
    ph: Optional[float] = None
    tds: Optional[float] = None
    raw_voltammogram: Optional[list[list[float]]] = None
    created_at: datetime
    contaminant_readings: list[ContaminantReadingSchema] = Field(default_factory=list)

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Heatmap
# ---------------------------------------------------------------------------
class HeatmapQuery(BaseModel):
    """Query parameters for heatmap data."""

    lat_min: float = Field(..., ge=-90, le=90)
    lat_max: float = Field(..., ge=-90, le=90)
    lng_min: float = Field(..., ge=-180, le=180)
    lng_max: float = Field(..., ge=-180, le=180)
    contaminant: Optional[str] = None

    @field_validator("contaminant")
    @classmethod
    def validate_contaminant(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_SYMBOLS:
            raise ValueError(
                f"Invalid contaminant '{v}'. Must be one of: {', '.join(sorted(VALID_SYMBOLS))}"
            )
        return v


class HeatmapPoint(BaseModel):
    """A single point for map rendering."""

    latitude: float
    longitude: float
    contaminant: str
    value: float
    unit: str
    exceeds_who_limit: bool
    source_type: SourceType
    timestamp: datetime


# ---------------------------------------------------------------------------
# Alert
# ---------------------------------------------------------------------------
class AlertCreate(BaseModel):
    """Input schema for creating an alert."""

    location_name: str = Field(..., min_length=1, max_length=256)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    contaminant: str
    value: float = Field(..., ge=0)
    severity: Severity
    message: str = Field(..., min_length=1)

    @field_validator("contaminant")
    @classmethod
    def validate_contaminant(cls, v: str) -> str:
        if v not in VALID_SYMBOLS:
            raise ValueError(
                f"Invalid contaminant '{v}'. Must be one of: {', '.join(sorted(VALID_SYMBOLS))}"
            )
        return v


class AlertSchema(BaseModel):
    """Full alert response."""

    id: int
    location_name: str
    latitude: float
    longitude: float
    contaminant: str
    value: float
    severity: Severity
    message: str
    created_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Device
# ---------------------------------------------------------------------------
class DeviceRegistration(BaseModel):
    """Input schema for registering a device."""

    hardware_id: str = Field(..., min_length=1, max_length=64)
    firmware_version: str = Field(..., min_length=1, max_length=32)


class DeviceSchema(BaseModel):
    """Full device response."""

    id: int
    hardware_id: str
    firmware_version: str
    registered_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------
class StatsResponse(BaseModel):
    """District overview statistics."""

    total_tests: int
    unsafe_sources: int
    active_testers: int
