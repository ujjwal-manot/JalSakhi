"""SQLAlchemy 2.0 ORM models for JalSakhi."""

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from backend.api.database import Base


class SourceType(str, enum.Enum):
    """Water source classification."""
    TAP = "tap"
    BOREWELL = "borewell"
    HANDPUMP = "handpump"
    OPENWELL = "openwell"
    RIVER = "river"


class Confidence(str, enum.Enum):
    """Measurement confidence level."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    RETEST = "RETEST"


class Severity(str, enum.Enum):
    """Alert severity level."""
    WARNING = "warning"
    CRITICAL = "critical"


class Device(Base):
    """Registered field-testing device."""

    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    hardware_id = Column(String(64), unique=True, nullable=False, index=True)
    firmware_version = Column(String(32), nullable=False)
    registered_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    test_results = relationship("TestResult", back_populates="device")


class TestResult(Base):
    """Single water quality test submission."""

    __test__ = False  # prevent pytest from collecting this as a test class
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    source_type = Column(Enum(SourceType), nullable=False)
    tester_name = Column(String(128), nullable=False)
    temperature = Column(Float, nullable=True)
    ph = Column(Float, nullable=True)
    tds = Column(Float, nullable=True)
    raw_voltammogram = Column(JSON, nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    device = relationship("Device", back_populates="test_results")
    contaminant_readings = relationship(
        "ContaminantReading", back_populates="test_result"
    )


class ContaminantReading(Base):
    """Individual contaminant measurement within a test."""

    __tablename__ = "contaminant_readings"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("test_results.id"), nullable=False)
    symbol = Column(String(8), nullable=False)  # NH3, Pb, As, NO3, Fe
    value = Column(Float, nullable=False)
    unit = Column(String(8), nullable=False)  # mg/L or ppb
    exceeds_who_limit = Column(Boolean, nullable=False)
    confidence = Column(Enum(Confidence), nullable=False)

    test_result = relationship("TestResult", back_populates="contaminant_readings")


class Alert(Base):
    """Contamination alert for a location."""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String(256), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    contaminant = Column(String(8), nullable=False)
    value = Column(Float, nullable=False)
    severity = Column(Enum(Severity), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    resolved_at = Column(DateTime, nullable=True)
