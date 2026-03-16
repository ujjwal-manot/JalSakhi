"""FastAPI application and route definitions for JalSakhi."""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.api.config import get_settings
from backend.api.database import Base, engine, get_db
from backend.api.models import (
    Alert,
    ContaminantReading,
    Device,
    Severity,
    TestResult,
)
from backend.api.schemas import (
    AlertCreate,
    AlertSchema,
    ContaminantReadingSchema,
    DeviceRegistration,
    DeviceSchema,
    HeatmapPoint,
    StatsResponse,
    TestResponse,
    TestSubmission,
    WHO_LIMITS,
)

settings = get_settings()


# ── Lifespan ─────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# ── CORS middleware ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ───────────────────────────────────────────────────────────────
@app.get("/health")
def health_check() -> dict:
    """Liveness probe."""
    return {"status": "ok"}


# ── Helpers ──────────────────────────────────────────────────────────────

def _check_exceeds_who(symbol: str, value: float, unit: str) -> bool:
    """Return True when a reading exceeds the WHO guideline."""
    limit, limit_unit = WHO_LIMITS[symbol]
    measured = _normalise_to_limit_unit(value, unit, limit_unit)
    return measured > limit


def _normalise_to_limit_unit(value: float, from_unit: str, to_unit: str) -> float:
    """Convert between mg/L and ppb so comparison uses the same unit."""
    if from_unit == to_unit:
        return value
    if from_unit == "mg/L" and to_unit == "ppb":
        return value * 1000.0
    if from_unit == "ppb" and to_unit == "mg/L":
        return value / 1000.0
    return value


# ── Devices ──────────────────────────────────────────────────────────────

@app.post(
    "/api/v1/devices/register",
    response_model=DeviceSchema,
    status_code=status.HTTP_201_CREATED,
)
def register_device(
    payload: DeviceRegistration,
    db: Session = Depends(get_db),
) -> Device:
    """Register a new field-testing device."""
    existing = (
        db.query(Device).filter(Device.hardware_id == payload.hardware_id).first()
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Device with hardware_id '{payload.hardware_id}' is already registered.",
        )
    device = Device(
        hardware_id=payload.hardware_id,
        firmware_version=payload.firmware_version,
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


# ── Tests ────────────────────────────────────────────────────────────────

@app.post(
    "/api/v1/tests",
    response_model=TestResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_test(
    payload: TestSubmission,
    db: Session = Depends(get_db),
) -> TestResult:
    """Submit a water quality test with contaminant readings."""
    device = db.query(Device).filter(Device.id == payload.device_id).first()
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with id {payload.device_id} not found.",
        )

    test = TestResult(
        device_id=payload.device_id,
        timestamp=payload.timestamp,
        latitude=payload.latitude,
        longitude=payload.longitude,
        source_type=payload.source_type,
        tester_name=payload.tester_name,
        temperature=payload.temperature,
        ph=payload.ph,
        tds=payload.tds,
        raw_voltammogram=payload.raw_voltammogram,
    )
    db.add(test)
    db.flush()  # obtain test.id without committing

    readings = _build_readings(test.id, payload.contaminant_readings)
    db.add_all(readings)
    db.commit()
    db.refresh(test)
    return test


def _build_readings(
    test_id: int,
    inputs: list,
) -> list[ContaminantReading]:
    """Create ContaminantReading rows from validated input (immutable)."""
    return [
        ContaminantReading(
            test_id=test_id,
            symbol=r.symbol,
            value=r.value,
            unit=r.unit,
            exceeds_who_limit=_check_exceeds_who(r.symbol, r.value, r.unit),
            confidence=r.confidence,
        )
        for r in inputs
    ]


@app.get("/api/v1/tests", response_model=list[TestResponse])
def query_tests(
    lat_min: Optional[float] = Query(None, ge=-90, le=90),
    lat_max: Optional[float] = Query(None, ge=-90, le=90),
    lng_min: Optional[float] = Query(None, ge=-180, le=180),
    lng_max: Optional[float] = Query(None, ge=-180, le=180),
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    contaminant: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> list[TestResult]:
    """Query test results with optional region, time, and contaminant filters."""
    q = db.query(TestResult)

    if lat_min is not None and lat_max is not None:
        q = q.filter(TestResult.latitude.between(lat_min, lat_max))
    if lng_min is not None and lng_max is not None:
        q = q.filter(TestResult.longitude.between(lng_min, lng_max))
    if start is not None:
        q = q.filter(TestResult.timestamp >= start)
    if end is not None:
        q = q.filter(TestResult.timestamp <= end)
    if contaminant is not None:
        q = q.join(ContaminantReading).filter(
            ContaminantReading.symbol == contaminant
        )

    return q.order_by(TestResult.created_at.desc()).limit(limit).all()


@app.get("/api/v1/tests/{test_id}", response_model=TestResponse)
def get_test(test_id: int, db: Session = Depends(get_db)) -> TestResult:
    """Return a single test result by ID."""
    test = db.query(TestResult).filter(TestResult.id == test_id).first()
    if test is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test with id {test_id} not found.",
        )
    return test


# ── Heatmap ──────────────────────────────────────────────────────────────

@app.get("/api/v1/heatmap", response_model=list[HeatmapPoint])
def get_heatmap(
    lat_min: float = Query(..., ge=-90, le=90),
    lat_max: float = Query(..., ge=-90, le=90),
    lng_min: float = Query(..., ge=-180, le=180),
    lng_max: float = Query(..., ge=-180, le=180),
    contaminant: Optional[str] = None,
    db: Session = Depends(get_db),
) -> list[dict]:
    """Return contaminant data points for map rendering."""
    q = (
        db.query(ContaminantReading, TestResult)
        .join(TestResult, ContaminantReading.test_id == TestResult.id)
        .filter(
            TestResult.latitude.between(lat_min, lat_max),
            TestResult.longitude.between(lng_min, lng_max),
        )
    )
    if contaminant is not None:
        q = q.filter(ContaminantReading.symbol == contaminant)

    rows = q.all()
    return [
        {
            "latitude": tr.latitude,
            "longitude": tr.longitude,
            "contaminant": cr.symbol,
            "value": cr.value,
            "unit": cr.unit,
            "exceeds_who_limit": cr.exceeds_who_limit,
            "source_type": tr.source_type,
            "timestamp": tr.timestamp,
        }
        for cr, tr in rows
    ]


# ── Alerts ───────────────────────────────────────────────────────────────

@app.get("/api/v1/alerts", response_model=list[AlertSchema])
def list_alerts(db: Session = Depends(get_db)) -> list[Alert]:
    """Return all active (unresolved) alerts."""
    return (
        db.query(Alert)
        .filter(Alert.resolved_at.is_(None))
        .order_by(Alert.created_at.desc())
        .all()
    )


@app.post(
    "/api/v1/alerts",
    response_model=AlertSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_alert(
    payload: AlertCreate,
    db: Session = Depends(get_db),
) -> Alert:
    """Create a contamination alert (from anomaly detection)."""
    alert = Alert(
        location_name=payload.location_name,
        latitude=payload.latitude,
        longitude=payload.longitude,
        contaminant=payload.contaminant,
        value=payload.value,
        severity=payload.severity,
        message=payload.message,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


# ── Stats ────────────────────────────────────────────────────────────────

@app.get("/api/v1/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)) -> dict:
    """District overview: total tests, unsafe sources, active testers."""
    total_tests = db.query(func.count(TestResult.id)).scalar() or 0

    unsafe_sources = (
        db.query(func.count(func.distinct(TestResult.id)))
        .join(ContaminantReading, ContaminantReading.test_id == TestResult.id)
        .filter(ContaminantReading.exceeds_who_limit.is_(True))
        .scalar()
        or 0
    )

    active_testers = (
        db.query(func.count(func.distinct(TestResult.tester_name))).scalar() or 0
    )

    return {
        "total_tests": total_tests,
        "unsafe_sources": unsafe_sources,
        "active_testers": active_testers,
    }
