"""Temporal contamination forecasting using exponential smoothing.

Predicts future contaminant levels from historical readings with
confidence intervals.  Uses Holt-Winters (statsmodels) when enough
data is available, with linear-trend fallback for sparse histories.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

import numpy as np
from numpy.typing import NDArray


# ---------------------------------------------------------------------------
# Immutable data classes
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TimeSeriesPoint:
    """A single time-stamped contaminant reading."""

    timestamp: datetime
    value: float


@dataclass(frozen=True)
class ForecastPoint:
    """A single forecasted value with confidence interval."""

    timestamp: datetime
    predicted: float
    lower_bound: float
    upper_bound: float


@dataclass(frozen=True)
class ForecastResult:
    """Complete forecast output."""

    predictions: tuple[ForecastPoint, ...]
    method: str  # "holt_winters", "exponential_smoothing", "linear_trend"
    contaminant: str


class TrendDirection(str, Enum):
    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"


@dataclass(frozen=True)
class TrendAnalysis:
    """Trend detection result."""

    direction: TrendDirection
    slope: float  # units per day
    p_value: float  # statistical significance
    is_significant: bool  # p_value < 0.05
    message: str


# ---------------------------------------------------------------------------
# Minimum data thresholds
# ---------------------------------------------------------------------------

_MIN_POINTS_LINEAR = 2
_MIN_POINTS_EXP_SMOOTHING = 7
_MIN_POINTS_SEASONAL = 30
_CONFIDENCE_Z = 1.96  # 95% confidence


# ---------------------------------------------------------------------------
# ContaminationForecaster
# ---------------------------------------------------------------------------

class ContaminationForecaster:
    """Predicts future contaminant levels from historical readings."""

    def forecast(
        self,
        readings: list[TimeSeriesPoint],
        horizon_days: int = 14,
        contaminant: str = "NH3",
    ) -> ForecastResult:
        """Forecast contaminant levels for the next N days.

        Strategy selection:
        - >= 30 points with periodicity: Holt-Winters with seasonality
        - >= 7 points: Holt-Winters (trend only, no seasonality)
        - >= 2 points: linear trend extrapolation
        - < 2 points: returns empty forecast

        Parameters
        ----------
        readings : list[TimeSeriesPoint]
            Historical readings sorted by time.
        horizon_days : int
            Number of days to forecast.
        contaminant : str
            Contaminant symbol (for labelling).

        Returns
        -------
        ForecastResult
        """
        if horizon_days < 1:
            raise ValueError("horizon_days must be >= 1")

        sorted_readings = sorted(readings, key=lambda r: r.timestamp)

        if len(sorted_readings) < _MIN_POINTS_LINEAR:
            return ForecastResult(
                predictions=(),
                method="insufficient_data",
                contaminant=contaminant,
            )

        values = np.array([r.value for r in sorted_readings], dtype=np.float64)
        timestamps = [r.timestamp for r in sorted_readings]
        last_ts = timestamps[-1]

        future_timestamps = [
            last_ts + timedelta(days=d + 1) for d in range(horizon_days)
        ]

        if len(sorted_readings) >= _MIN_POINTS_EXP_SMOOTHING:
            predictions, method = _exponential_smoothing_forecast(
                values, horizon_days, len(sorted_readings) >= _MIN_POINTS_SEASONAL,
            )
        else:
            predictions, method = _linear_trend_forecast(values, horizon_days)

        # Clamp predictions to non-negative (physical constraint)
        predictions = np.clip(predictions, 0.0, None)

        # Confidence intervals based on historical residual spread
        residual_std = _estimate_residual_std(values)
        lower = np.clip(predictions - _CONFIDENCE_Z * residual_std, 0.0, None)
        upper = predictions + _CONFIDENCE_Z * residual_std

        forecast_points = tuple(
            ForecastPoint(
                timestamp=future_timestamps[i],
                predicted=float(round(predictions[i], 6)),
                lower_bound=float(round(lower[i], 6)),
                upper_bound=float(round(upper[i], 6)),
            )
            for i in range(horizon_days)
        )

        return ForecastResult(
            predictions=forecast_points,
            method=method,
            contaminant=contaminant,
        )

    def detect_trend(
        self,
        readings: list[TimeSeriesPoint],
    ) -> TrendAnalysis:
        """Detect rising/falling/stable trends with statistical significance.

        Uses ordinary least-squares regression of value vs. day-index.
        Significance tested via scipy's t-test on the slope.
        """
        if len(readings) < _MIN_POINTS_LINEAR:
            return TrendAnalysis(
                direction=TrendDirection.STABLE,
                slope=0.0,
                p_value=1.0,
                is_significant=False,
                message="Insufficient data for trend detection.",
            )

        sorted_readings = sorted(readings, key=lambda r: r.timestamp)
        values = np.array([r.value for r in sorted_readings], dtype=np.float64)
        t0 = sorted_readings[0].timestamp
        days = np.array(
            [(r.timestamp - t0).total_seconds() / 86400.0 for r in sorted_readings],
            dtype=np.float64,
        )

        slope, p_value = _linear_regression_with_pvalue(days, values)
        is_significant = p_value < 0.05

        if not is_significant:
            direction = TrendDirection.STABLE
            message = f"No significant trend detected (p={p_value:.4f})."
        elif slope > 0:
            direction = TrendDirection.RISING
            message = (
                f"Rising trend: +{slope:.6f} units/day (p={p_value:.4f})."
            )
        else:
            direction = TrendDirection.FALLING
            message = (
                f"Falling trend: {slope:.6f} units/day (p={p_value:.4f})."
            )

        return TrendAnalysis(
            direction=direction,
            slope=float(round(slope, 8)),
            p_value=float(round(p_value, 6)),
            is_significant=is_significant,
            message=message,
        )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _exponential_smoothing_forecast(
    values: NDArray[np.float64],
    horizon: int,
    try_seasonal: bool,
) -> tuple[NDArray[np.float64], str]:
    """Holt-Winters exponential smoothing via statsmodels.

    Falls back to linear trend if statsmodels is unavailable or fitting
    fails.
    """
    try:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing  # type: ignore[import-untyped]

        if try_seasonal and len(values) >= _MIN_POINTS_SEASONAL:
            # Attempt seasonal decomposition with weekly period
            seasonal_period = min(7, len(values) // 4)
            if seasonal_period >= 2:
                model = ExponentialSmoothing(
                    values,
                    trend="add",
                    seasonal="add",
                    seasonal_periods=seasonal_period,
                    initialization_method="estimated",
                )
                fitted = model.fit(optimized=True)
                forecast = fitted.forecast(horizon)
                return np.array(forecast, dtype=np.float64), "holt_winters"

        # Trend-only exponential smoothing
        model = ExponentialSmoothing(
            values,
            trend="add",
            seasonal=None,
            initialization_method="estimated",
        )
        fitted = model.fit(optimized=True)
        forecast = fitted.forecast(horizon)
        return np.array(forecast, dtype=np.float64), "exponential_smoothing"

    except Exception:
        return _linear_trend_forecast(values, horizon)


def _linear_trend_forecast(
    values: NDArray[np.float64],
    horizon: int,
) -> tuple[NDArray[np.float64], str]:
    """Simple linear extrapolation."""
    n = len(values)
    x = np.arange(n, dtype=np.float64)
    coeffs = np.polyfit(x, values, 1)
    future_x = np.arange(n, n + horizon, dtype=np.float64)
    predictions = np.polyval(coeffs, future_x)
    return predictions, "linear_trend"


def _estimate_residual_std(values: NDArray[np.float64]) -> float:
    """Estimate residual standard deviation from consecutive differences."""
    if len(values) < 2:
        return 0.0
    diffs = np.diff(values)
    return float(np.std(diffs, ddof=1)) if len(diffs) > 1 else float(np.abs(diffs[0]))


def _linear_regression_with_pvalue(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
) -> tuple[float, float]:
    """OLS regression returning (slope, p_value).

    Uses scipy.stats.linregress when available, otherwise a manual
    calculation.
    """
    try:
        from scipy.stats import linregress  # type: ignore[import-untyped]

        result = linregress(x, y)
        return float(result.slope), float(result.pvalue)
    except ImportError:
        pass

    # Manual fallback
    n = len(x)
    if n < 3:
        slope = (y[-1] - y[0]) / max(x[-1] - x[0], 1e-12)
        return float(slope), 0.5  # can't compute p-value with <3 points

    x_mean = np.mean(x)
    y_mean = np.mean(y)
    ss_xx = np.sum((x - x_mean) ** 2)
    ss_xy = np.sum((x - x_mean) * (y - y_mean))

    if ss_xx < 1e-12:
        return 0.0, 1.0

    slope = ss_xy / ss_xx
    intercept = y_mean - slope * x_mean
    y_pred = slope * x + intercept
    residuals = y - y_pred
    ss_res = np.sum(residuals ** 2)
    se_slope = np.sqrt(ss_res / (n - 2) / ss_xx) if n > 2 else 1e-12
    t_stat = slope / max(se_slope, 1e-12)

    # Approximate two-sided p-value from t-distribution
    try:
        from scipy.stats import t as t_dist  # type: ignore[import-untyped]

        p_value = float(2.0 * t_dist.sf(abs(t_stat), n - 2))
    except ImportError:
        # Very rough approximation for large t
        p_value = float(np.exp(-0.5 * t_stat ** 2)) if abs(t_stat) < 10 else 0.0

    return float(slope), p_value
