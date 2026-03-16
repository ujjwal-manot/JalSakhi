"""Tests for spatial analysis and forecasting modules.

Covers:
- Kriging interpolation (kriging.py)
- IDW fallback
- Hotspot detection
- Temporal forecasting (forecaster.py)
- Tamper detection (tamper_detection.py)

Minimum 15 test functions.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import pytest

from backend.ml.kriging import (
    ContaminationMapper,
    HeatmapGrid,
    Hotspot,
    TestPoint,
    generate_bhagalpur_test_points,
)
from backend.ml.forecaster import (
    ContaminationForecaster,
    ForecastResult,
    TimeSeriesPoint,
    TrendDirection,
)
from backend.ml.tamper_detection import (
    TamperDetector,
    TamperFlag,
    TestResult,
    TestSubmission,
)


# ===================================================================
# Fixtures
# ===================================================================

@pytest.fixture
def mapper() -> ContaminationMapper:
    return ContaminationMapper()


@pytest.fixture
def forecaster() -> ContaminationForecaster:
    return ContaminationForecaster()


@pytest.fixture
def detector() -> TamperDetector:
    return TamperDetector()


@pytest.fixture
def bhagalpur_20() -> list[TestPoint]:
    return generate_bhagalpur_test_points(n=20, contaminant="NH3", seed=42)


@pytest.fixture
def bhagalpur_5() -> list[TestPoint]:
    return generate_bhagalpur_test_points(n=5, contaminant="NH3", seed=99)


def _make_time_series(
    n: int,
    base_value: float = 0.5,
    slope: float = 0.0,
    noise_std: float = 0.05,
    seed: int = 42,
) -> list[TimeSeriesPoint]:
    """Generate synthetic time-series readings."""
    rng = np.random.default_rng(seed)
    base_ts = datetime(2026, 1, 1)
    return [
        TimeSeriesPoint(
            timestamp=base_ts + timedelta(days=i),
            value=max(0.0, base_value + slope * i + rng.normal(0, noise_std)),
        )
        for i in range(n)
    ]


# ===================================================================
# Kriging / IDW interpolation tests
# ===================================================================

class TestKrigingInterpolation:
    """Tests for ContaminationMapper.interpolate."""

    def test_interpolate_with_kriging_method(
        self, mapper: ContaminationMapper, bhagalpur_20: list[TestPoint]
    ) -> None:
        """With 20 points, should use kriging (or IDW fallback if pykrige fails)."""
        grid = mapper.interpolate(bhagalpur_20, grid_resolution=10, contaminant="NH3")
        assert isinstance(grid, HeatmapGrid)
        assert grid.method in ("kriging", "idw")
        assert len(grid.lat_grid) == 10
        assert len(grid.lng_grid) == 10
        assert len(grid.values) == 10
        assert all(len(row) == 10 for row in grid.values)

    def test_interpolate_values_non_negative(
        self, mapper: ContaminationMapper, bhagalpur_20: list[TestPoint]
    ) -> None:
        """All interpolated values must be non-negative."""
        grid = mapper.interpolate(bhagalpur_20, grid_resolution=10, contaminant="NH3")
        for row in grid.values:
            for val in row:
                assert val >= 0.0, f"Negative interpolation value: {val}"

    def test_idw_fallback_with_few_points(
        self, mapper: ContaminationMapper, bhagalpur_5: list[TestPoint]
    ) -> None:
        """With <10 points, should use IDW fallback."""
        grid = mapper.interpolate(bhagalpur_5, grid_resolution=8, contaminant="NH3")
        assert grid.method == "idw"
        assert len(grid.lat_grid) == 8

    def test_empty_points_returns_empty_grid(
        self, mapper: ContaminationMapper
    ) -> None:
        """Empty input should return empty grid."""
        grid = mapper.interpolate([], grid_resolution=10, contaminant="NH3")
        assert grid.lat_grid == ()
        assert grid.values == ()
        assert grid.method == "none"

    def test_single_point_returns_single_grid(
        self, mapper: ContaminationMapper
    ) -> None:
        """Single point should return a 1x1 grid."""
        point = TestPoint(latitude=25.24, longitude=86.98, value=0.6, contaminant="NH3")
        grid = mapper.interpolate([point], grid_resolution=10, contaminant="NH3")
        assert grid.method == "single"
        assert len(grid.lat_grid) == 1
        assert grid.values == ((0.6,),)

    def test_grid_resolution_validation(
        self, mapper: ContaminationMapper
    ) -> None:
        """grid_resolution < 2 should raise ValueError."""
        with pytest.raises(ValueError, match="grid_resolution"):
            mapper.interpolate([], grid_resolution=1, contaminant="NH3")

    def test_contaminant_filtering(
        self, mapper: ContaminationMapper
    ) -> None:
        """Points for wrong contaminant should be ignored."""
        points = [
            TestPoint(25.24, 86.98, 0.5, contaminant="Pb"),
            TestPoint(25.25, 86.99, 0.3, contaminant="Pb"),
        ]
        grid = mapper.interpolate(points, grid_resolution=5, contaminant="NH3")
        assert grid.method == "none"


# ===================================================================
# Hotspot detection tests
# ===================================================================

class TestHotspotDetection:
    """Tests for ContaminationMapper.get_hotspots."""

    def test_hotspots_identified(
        self, mapper: ContaminationMapper, bhagalpur_20: list[TestPoint]
    ) -> None:
        """Should return hotspots above percentile threshold."""
        grid = mapper.interpolate(bhagalpur_20, grid_resolution=10, contaminant="NH3")
        hotspots = mapper.get_hotspots(grid, who_limit=0.5, percentile=90)
        assert isinstance(hotspots, list)
        assert all(isinstance(h, Hotspot) for h in hotspots)
        # 90th percentile on 10x10 grid -> ~10 cells
        assert len(hotspots) > 0
        assert len(hotspots) <= 15  # at most ~10% of 100 cells + tolerance

    def test_hotspot_who_limit_flag(
        self, mapper: ContaminationMapper, bhagalpur_20: list[TestPoint]
    ) -> None:
        """Hotspots should have correct exceeds_who_limit flag."""
        grid = mapper.interpolate(bhagalpur_20, grid_resolution=10, contaminant="NH3")
        hotspots = mapper.get_hotspots(grid, who_limit=0.5, percentile=80)
        for h in hotspots:
            assert h.exceeds_who_limit == (h.value > 0.5)

    def test_hotspots_empty_grid(self, mapper: ContaminationMapper) -> None:
        """Empty grid should return no hotspots."""
        grid = HeatmapGrid((), (), (), "NH3", "none")
        assert mapper.get_hotspots(grid) == []


# ===================================================================
# Forecaster tests
# ===================================================================

class TestForecaster:
    """Tests for ContaminationForecaster."""

    def test_forecast_with_sufficient_data(
        self, forecaster: ContaminationForecaster
    ) -> None:
        """With 30 points, should produce forecast with correct length."""
        readings = _make_time_series(30, base_value=0.5, slope=0.01)
        result = forecaster.forecast(readings, horizon_days=7)
        assert isinstance(result, ForecastResult)
        assert len(result.predictions) == 7
        assert result.method in ("holt_winters", "exponential_smoothing", "linear_trend")

    def test_forecast_linear_fallback(
        self, forecaster: ContaminationForecaster
    ) -> None:
        """With <7 points, should fall back to linear trend."""
        readings = _make_time_series(4, base_value=0.5, slope=0.02)
        result = forecaster.forecast(readings, horizon_days=5)
        assert result.method == "linear_trend"
        assert len(result.predictions) == 5

    def test_forecast_insufficient_data(
        self, forecaster: ContaminationForecaster
    ) -> None:
        """With <2 points, should return empty forecast."""
        readings = _make_time_series(1)
        result = forecaster.forecast(readings, horizon_days=7)
        assert result.method == "insufficient_data"
        assert len(result.predictions) == 0

    def test_forecast_non_negative(
        self, forecaster: ContaminationForecaster
    ) -> None:
        """Forecasted values should be non-negative."""
        readings = _make_time_series(15, base_value=0.1, slope=-0.02)
        result = forecaster.forecast(readings, horizon_days=14)
        for point in result.predictions:
            assert point.predicted >= 0.0
            assert point.lower_bound >= 0.0

    def test_forecast_confidence_intervals(
        self, forecaster: ContaminationForecaster
    ) -> None:
        """Lower bound <= predicted <= upper bound."""
        readings = _make_time_series(20, base_value=1.0, slope=0.01)
        result = forecaster.forecast(readings, horizon_days=7)
        for point in result.predictions:
            assert point.lower_bound <= point.predicted <= point.upper_bound

    def test_detect_rising_trend(
        self, forecaster: ContaminationForecaster
    ) -> None:
        """Strong rising trend should be detected as significant."""
        readings = _make_time_series(30, base_value=0.1, slope=0.05, noise_std=0.01)
        trend = forecaster.detect_trend(readings)
        assert trend.direction == TrendDirection.RISING
        assert trend.is_significant
        assert trend.slope > 0

    def test_detect_stable_trend(
        self, forecaster: ContaminationForecaster
    ) -> None:
        """Flat data with noise should be stable."""
        readings = _make_time_series(30, base_value=1.0, slope=0.0, noise_std=0.5)
        trend = forecaster.detect_trend(readings)
        # With high noise and zero slope, trend may or may not be significant
        # but slope should be close to zero
        assert abs(trend.slope) < 0.1

    def test_detect_trend_insufficient_data(
        self, forecaster: ContaminationForecaster
    ) -> None:
        """With <2 points, should return stable with insufficient data message."""
        readings = _make_time_series(1)
        trend = forecaster.detect_trend(readings)
        assert trend.direction == TrendDirection.STABLE
        assert not trend.is_significant


# ===================================================================
# Tamper detection tests
# ===================================================================

class TestTamperDetection:
    """Tests for TamperDetector."""

    def _make_clean_submission(self) -> TestSubmission:
        return TestSubmission(
            device_id=1,
            timestamp=datetime(2026, 3, 15, 10, 0),
            latitude=25.24,
            longitude=86.98,
            ph=7.2,
            tds=350.0,
            contaminant_values={"NH3": 0.3, "Pb": 5.0},
        )

    def _make_regional_history(self, n: int = 20) -> list[TestResult]:
        rng = np.random.default_rng(42)
        base_ts = datetime(2026, 3, 1)
        return [
            TestResult(
                device_id=rng.integers(1, 5),
                timestamp=base_ts + timedelta(hours=i * 6),
                latitude=25.24 + rng.normal(0, 0.01),
                longitude=86.98 + rng.normal(0, 0.01),
                ph=float(round(7.0 + rng.normal(0, 0.3), 2)),
                tds=float(round(300 + rng.normal(0, 50), 1)),
                contaminant_values={
                    "NH3": float(round(max(0.01, 0.3 + rng.normal(0, 0.1)), 4)),
                    "Pb": float(round(max(0.1, 5.0 + rng.normal(0, 1.0)), 4)),
                },
            )
            for i in range(n)
        ]

    def test_clean_submission_passes(
        self, detector: TamperDetector
    ) -> None:
        """Clean submission should not be flagged."""
        report = detector.check_submission(
            self._make_clean_submission(),
            self._make_regional_history(),
        )
        assert not report.is_suspicious
        assert len(report.flags) == 0

    def test_negative_value_flagged(
        self, detector: TamperDetector
    ) -> None:
        """Negative contaminant value should be flagged as physically impossible."""
        submission = TestSubmission(
            device_id=1,
            timestamp=datetime(2026, 3, 15, 10, 0),
            latitude=25.24,
            longitude=86.98,
            ph=7.0,
            tds=300.0,
            contaminant_values={"NH3": -0.5},
        )
        report = detector.check_submission(submission, [])
        assert report.is_suspicious
        flag_types = {f.flag for f in report.flags}
        assert TamperFlag.PHYSICALLY_IMPOSSIBLE in flag_types

    def test_extreme_outlier_flagged(
        self, detector: TamperDetector
    ) -> None:
        """Value far from regional mean should be flagged."""
        submission = TestSubmission(
            device_id=1,
            timestamp=datetime(2026, 3, 15, 10, 0),
            latitude=25.24,
            longitude=86.98,
            ph=7.0,
            tds=300.0,
            contaminant_values={"NH3": 10.0},  # way above regional ~0.3
        )
        report = detector.check_submission(
            submission, self._make_regional_history()
        )
        assert report.is_suspicious
        flag_types = {f.flag for f in report.flags}
        assert TamperFlag.EXTREME_OUTLIER in flag_types

    def test_excessive_frequency_flagged(
        self, detector: TamperDetector
    ) -> None:
        """>20 tests per day from one device should be flagged."""
        submission = TestSubmission(
            device_id=1,
            timestamp=datetime(2026, 3, 15, 12, 0),
            latitude=25.24,
            longitude=86.98,
            ph=7.0,
            tds=300.0,
            contaminant_values={"NH3": 0.3},
        )
        # 25 tests from device 1 on the same day
        history = [
            TestResult(
                device_id=1,
                timestamp=datetime(2026, 3, 15, 8, 0) + timedelta(minutes=i * 10),
                latitude=25.24,
                longitude=86.98,
                ph=7.0,
                tds=300.0,
                contaminant_values={"NH3": float(round(0.3 + i * 0.001, 4))},
            )
            for i in range(25)
        ]
        report = detector.check_submission(submission, history)
        assert report.is_suspicious
        flag_types = {f.flag for f in report.flags}
        assert TamperFlag.EXCESSIVE_FREQUENCY in flag_types

    def test_impossible_chemistry_flagged(
        self, detector: TamperDetector
    ) -> None:
        """pH <3 with high ammonia should be flagged."""
        submission = TestSubmission(
            device_id=1,
            timestamp=datetime(2026, 3, 15, 10, 0),
            latitude=25.24,
            longitude=86.98,
            ph=2.0,
            tds=300.0,
            contaminant_values={"NH3": 5.0},
        )
        report = detector.check_submission(submission, [])
        flag_types = {f.flag for f in report.flags}
        assert TamperFlag.IMPOSSIBLE_CHEMISTRY in flag_types

    def test_identical_readings_flagged(
        self, detector: TamperDetector
    ) -> None:
        """Multiple identical readings from same device should be flagged."""
        submission = TestSubmission(
            device_id=1,
            timestamp=datetime(2026, 3, 15, 12, 0),
            latitude=25.24,
            longitude=86.98,
            ph=7.0,
            tds=300.0,
            contaminant_values={"NH3": 0.3, "Pb": 5.0},
        )
        # 5 identical readings from same device
        history = [
            TestResult(
                device_id=1,
                timestamp=datetime(2026, 3, 14, 10, 0) + timedelta(hours=i),
                latitude=25.24,
                longitude=86.98,
                ph=7.0,
                tds=300.0,
                contaminant_values={"NH3": 0.3, "Pb": 5.0},
            )
            for i in range(5)
        ]
        report = detector.check_submission(submission, history)
        flag_types = {f.flag for f in report.flags}
        assert TamperFlag.IDENTICAL_READINGS in flag_types

    def test_empty_history_no_crash(
        self, detector: TamperDetector
    ) -> None:
        """Empty regional history should not crash."""
        report = detector.check_submission(
            self._make_clean_submission(), []
        )
        assert isinstance(report.overall_confidence, float)


# ===================================================================
# Data class immutability tests
# ===================================================================

class TestImmutability:
    """Verify frozen dataclasses cannot be mutated."""

    def test_test_point_frozen(self) -> None:
        point = TestPoint(25.24, 86.98, 0.5)
        with pytest.raises(AttributeError):
            point.value = 1.0  # type: ignore[misc]

    def test_heatmap_grid_frozen(self) -> None:
        grid = HeatmapGrid((), (), (), "NH3", "none")
        with pytest.raises(AttributeError):
            grid.method = "idw"  # type: ignore[misc]

    def test_forecast_result_frozen(self) -> None:
        result = ForecastResult(predictions=(), method="test", contaminant="NH3")
        with pytest.raises(AttributeError):
            result.method = "other"  # type: ignore[misc]


# ===================================================================
# Synthetic data generator test
# ===================================================================

class TestSyntheticData:
    """Tests for generate_bhagalpur_test_points."""

    def test_generates_correct_count(self) -> None:
        points = generate_bhagalpur_test_points(n=20)
        assert len(points) == 20

    def test_points_near_bhagalpur(self) -> None:
        points = generate_bhagalpur_test_points(n=100, seed=0)
        lats = [p.latitude for p in points]
        lngs = [p.longitude for p in points]
        assert 25.0 < np.mean(lats) < 25.5
        assert 86.7 < np.mean(lngs) < 87.3

    def test_values_positive(self) -> None:
        points = generate_bhagalpur_test_points(n=50)
        assert all(p.value > 0 for p in points)

    def test_deterministic_with_seed(self) -> None:
        a = generate_bhagalpur_test_points(n=10, seed=123)
        b = generate_bhagalpur_test_points(n=10, seed=123)
        assert [p.value for p in a] == [p.value for p in b]
