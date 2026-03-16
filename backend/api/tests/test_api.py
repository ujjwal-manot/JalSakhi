"""Tests for JalSakhi FastAPI endpoints using httpx AsyncClient."""

import pytest
import pytest_asyncio
from datetime import datetime, timezone
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.api.database import Base, get_db
from backend.api.models import Device, TestResult, ContaminantReading, Alert  # noqa: F401 — register models with Base.metadata
from backend.api.main import app

# ── In-memory test database ─────────────────────────────────────────────
# StaticPool forces all sessions to reuse a single underlying connection so
# tables created by the setup fixture are visible to every subsequent session.
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Create fresh tables for every test."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ── Helpers ──────────────────────────────────────────────────────────────

def _device_payload(hw_id: str = "ESP32-001") -> dict:
    return {"hardware_id": hw_id, "firmware_version": "1.0.0"}


def _test_payload(device_id: int = 1) -> dict:
    return {
        "device_id": device_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "latitude": 26.9,
        "longitude": 75.7,
        "source_type": "borewell",
        "tester_name": "Priya",
        "temperature": 28.5,
        "ph": 7.2,
        "tds": 450.0,
        "contaminant_readings": [
            {"symbol": "Pb", "value": 15.0, "unit": "ppb", "confidence": "HIGH"},
            {"symbol": "Fe", "value": 0.2, "unit": "mg/L", "confidence": "MEDIUM"},
        ],
    }


# ── Device registration ─────────────────────────────────────────────────

@pytest.mark.anyio
async def test_register_device(client: AsyncClient):
    resp = await client.post("/api/v1/devices/register", json=_device_payload())
    assert resp.status_code == 201
    data = resp.json()
    assert data["hardware_id"] == "ESP32-001"
    assert data["firmware_version"] == "1.0.0"
    assert "id" in data


@pytest.mark.anyio
async def test_register_device_duplicate(client: AsyncClient):
    await client.post("/api/v1/devices/register", json=_device_payload())
    resp = await client.post("/api/v1/devices/register", json=_device_payload())
    assert resp.status_code == 409


# ── Submit test result ───────────────────────────────────────────────────

@pytest.mark.anyio
async def test_submit_test(client: AsyncClient):
    await client.post("/api/v1/devices/register", json=_device_payload())
    resp = await client.post("/api/v1/tests", json=_test_payload())
    assert resp.status_code == 201
    data = resp.json()
    assert data["tester_name"] == "Priya"
    assert len(data["contaminant_readings"]) == 2

    # Pb 15 ppb > 10 ppb WHO limit → exceeds
    pb_reading = next(r for r in data["contaminant_readings"] if r["symbol"] == "Pb")
    assert pb_reading["exceeds_who_limit"] is True

    # Fe 0.2 mg/L < 0.3 mg/L WHO limit → safe
    fe_reading = next(r for r in data["contaminant_readings"] if r["symbol"] == "Fe")
    assert fe_reading["exceeds_who_limit"] is False


@pytest.mark.anyio
async def test_submit_test_device_not_found(client: AsyncClient):
    resp = await client.post("/api/v1/tests", json=_test_payload(device_id=999))
    assert resp.status_code == 404


# ── Query tests by region ───────────────────────────────────────────────

@pytest.mark.anyio
async def test_query_tests_by_region(client: AsyncClient):
    await client.post("/api/v1/devices/register", json=_device_payload())
    await client.post("/api/v1/tests", json=_test_payload())

    resp = await client.get(
        "/api/v1/tests",
        params={"lat_min": 26.0, "lat_max": 27.0, "lng_min": 75.0, "lng_max": 76.0},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["latitude"] == 26.9


@pytest.mark.anyio
async def test_query_tests_outside_region(client: AsyncClient):
    await client.post("/api/v1/devices/register", json=_device_payload())
    await client.post("/api/v1/tests", json=_test_payload())

    resp = await client.get(
        "/api/v1/tests",
        params={"lat_min": 10.0, "lat_max": 11.0, "lng_min": 75.0, "lng_max": 76.0},
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 0


# ── Single test detail ───────────────────────────────────────────────────

@pytest.mark.anyio
async def test_get_single_test(client: AsyncClient):
    await client.post("/api/v1/devices/register", json=_device_payload())
    create_resp = await client.post("/api/v1/tests", json=_test_payload())
    test_id = create_resp.json()["id"]

    resp = await client.get(f"/api/v1/tests/{test_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == test_id


@pytest.mark.anyio
async def test_get_single_test_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/tests/999")
    assert resp.status_code == 404


# ── Heatmap ──────────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_heatmap(client: AsyncClient):
    await client.post("/api/v1/devices/register", json=_device_payload())
    await client.post("/api/v1/tests", json=_test_payload())

    resp = await client.get(
        "/api/v1/heatmap",
        params={"lat_min": 26.0, "lat_max": 27.0, "lng_min": 75.0, "lng_max": 76.0},
    )
    assert resp.status_code == 200
    points = resp.json()
    assert len(points) == 2  # Pb + Fe readings
    symbols = {p["contaminant"] for p in points}
    assert symbols == {"Pb", "Fe"}


@pytest.mark.anyio
async def test_heatmap_filter_contaminant(client: AsyncClient):
    await client.post("/api/v1/devices/register", json=_device_payload())
    await client.post("/api/v1/tests", json=_test_payload())

    resp = await client.get(
        "/api/v1/heatmap",
        params={
            "lat_min": 26.0,
            "lat_max": 27.0,
            "lng_min": 75.0,
            "lng_max": 76.0,
            "contaminant": "Pb",
        },
    )
    assert resp.status_code == 200
    points = resp.json()
    assert len(points) == 1
    assert points[0]["contaminant"] == "Pb"


# ── Alerts ───────────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_create_and_list_alerts(client: AsyncClient):
    alert_data = {
        "location_name": "Village Well A",
        "latitude": 26.9,
        "longitude": 75.7,
        "contaminant": "As",
        "value": 25.0,
        "severity": "critical",
        "message": "Arsenic levels exceed WHO limit in Village Well A",
    }
    create_resp = await client.post("/api/v1/alerts", json=alert_data)
    assert create_resp.status_code == 201
    assert create_resp.json()["location_name"] == "Village Well A"

    list_resp = await client.get("/api/v1/alerts")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1


# ── Stats ────────────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_stats(client: AsyncClient):
    await client.post("/api/v1/devices/register", json=_device_payload())
    await client.post("/api/v1/tests", json=_test_payload())

    resp = await client.get("/api/v1/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_tests"] == 1
    assert data["unsafe_sources"] == 1  # Pb exceeds WHO limit
    assert data["active_testers"] == 1


@pytest.mark.anyio
async def test_stats_empty(client: AsyncClient):
    resp = await client.get("/api/v1/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_tests"] == 0
    assert data["unsafe_sources"] == 0
    assert data["active_testers"] == 0


# ── Health check ─────────────────────────────────────────────────────────

@pytest.mark.anyio
async def test_health_check(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
