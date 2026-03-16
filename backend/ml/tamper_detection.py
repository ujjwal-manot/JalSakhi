"""Server-side data integrity checks for water quality submissions.

Detects suspicious or fraudulent test submissions using statistical
analysis against regional baselines and physical/chemical constraints.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

import numpy as np


# ---------------------------------------------------------------------------
# Immutable data classes
# ---------------------------------------------------------------------------

class TamperFlag(str, Enum):
    """Categories of suspicious activity."""

    IDENTICAL_READINGS = "identical_readings"
    IMPOSSIBLE_CHEMISTRY = "impossible_chemistry"
    EXTREME_OUTLIER = "extreme_outlier"
    EXCESSIVE_FREQUENCY = "excessive_frequency"
    PHYSICALLY_IMPOSSIBLE = "physically_impossible"


@dataclass(frozen=True)
class TestSubmission:
    """Incoming test submission to check."""
    __test__ = False

    device_id: int
    timestamp: datetime
    latitude: float
    longitude: float
    ph: Optional[float]
    tds: Optional[float]
    contaminant_values: dict[str, float]  # symbol -> value


@dataclass(frozen=True)
class TestResult:
    """Historical test result for regional comparison."""
    __test__ = False

    device_id: int
    timestamp: datetime
    latitude: float
    longitude: float
    ph: Optional[float]
    tds: Optional[float]
    contaminant_values: dict[str, float]


@dataclass(frozen=True)
class FlagDetail:
    """A single tamper flag with explanation."""

    flag: TamperFlag
    confidence: float  # 0.0 to 1.0
    description: str


@dataclass(frozen=True)
class TamperReport:
    """Complete tamper analysis result."""

    is_suspicious: bool
    flags: tuple[FlagDetail, ...]
    overall_confidence: float  # 0.0 (clean) to 1.0 (certainly tampered)
    recommendation: str


# ---------------------------------------------------------------------------
# Physical / chemical constraints
# ---------------------------------------------------------------------------

# Physically impossible value ranges (value must be non-negative)
_PHYSICAL_LIMITS: dict[str, tuple[float, float]] = {
    "NH3": (0.0, 50.0),   # mg/L — above 50 is unrealistic for drinking water
    "Pb": (0.0, 500.0),   # ppb
    "As": (0.0, 500.0),   # ppb
    "NO3": (0.0, 500.0),  # mg/L
    "Fe": (0.0, 100.0),   # mg/L
}

# Chemical impossibility rules: conditions that cannot co-exist
_IMPOSSIBLE_CHEMISTRY: list[dict[str, object]] = [
    {
        "description": "Very low pH (<3) with high ammonia (>2 mg/L) is chemically implausible in natural water",
        "check": lambda ph, contaminants, tds=None: (
            ph is not None
            and ph < 3.0
            and contaminants.get("NH3", 0.0) > 2.0
        ),
    },
    {
        "description": "pH exactly 7.00 with TDS=0 and contaminants present suggests fabricated data",
        "check": lambda ph, contaminants, tds=None: (
            ph is not None
            and abs(ph - 7.0) < 0.005
            and tds is not None
            and tds == 0.0
            and any(v > 0 for v in contaminants.values())
        ),
    },
]

_OUTLIER_STD_THRESHOLD = 4.0
_MAX_TESTS_PER_DAY = 20
_IDENTICAL_VALUE_TOLERANCE = 1e-9


# ---------------------------------------------------------------------------
# TamperDetector
# ---------------------------------------------------------------------------

class TamperDetector:
    """Detects suspicious test submissions using statistical analysis."""

    def check_submission(
        self,
        submission: TestSubmission,
        regional_history: list[TestResult],
    ) -> TamperReport:
        """Run all tamper checks and return aggregated report.

        Checks performed:
        1. Identical readings (copy-paste fraud)
        2. Impossible chemistry
        3. Extreme outliers vs regional baseline (>4 std dev)
        4. Excessive test frequency (>20/day from one device)
        5. Physically impossible values (negative, extreme)

        Parameters
        ----------
        submission : TestSubmission
            The incoming test to evaluate.
        regional_history : list[TestResult]
            Recent test results from the same region.

        Returns
        -------
        TamperReport
            Immutable report with flags and recommendation.
        """
        all_flags: list[FlagDetail] = []

        all_flags.extend(_check_physically_impossible(submission))
        all_flags.extend(_check_impossible_chemistry(submission))
        all_flags.extend(_check_identical_readings(submission, regional_history))
        all_flags.extend(
            _check_extreme_outliers(submission, regional_history)
        )
        all_flags.extend(
            _check_excessive_frequency(submission, regional_history)
        )

        if not all_flags:
            return TamperReport(
                is_suspicious=False,
                flags=(),
                overall_confidence=0.0,
                recommendation="Submission appears legitimate.",
            )

        overall = min(
            1.0,
            sum(f.confidence for f in all_flags) / max(len(all_flags), 1),
        )
        is_suspicious = overall > 0.3 or any(f.confidence > 0.7 for f in all_flags)

        if overall > 0.7:
            recommendation = "REJECT: High probability of tampered data."
        elif overall > 0.4:
            recommendation = "REVIEW: Moderate suspicion — manual review recommended."
        else:
            recommendation = "FLAG: Low-level anomaly detected, likely acceptable."

        return TamperReport(
            is_suspicious=is_suspicious,
            flags=tuple(all_flags),
            overall_confidence=float(round(overall, 4)),
            recommendation=recommendation,
        )


# ---------------------------------------------------------------------------
# Individual check functions (pure)
# ---------------------------------------------------------------------------

def _check_physically_impossible(
    submission: TestSubmission,
) -> list[FlagDetail]:
    """Check for physically impossible values."""
    flags: list[FlagDetail] = []

    # pH range
    if submission.ph is not None and (submission.ph < 0 or submission.ph > 14):
        flags.append(
            FlagDetail(
                flag=TamperFlag.PHYSICALLY_IMPOSSIBLE,
                confidence=1.0,
                description=f"pH value {submission.ph} is outside valid range [0, 14].",
            )
        )

    # TDS cannot be negative
    if submission.tds is not None and submission.tds < 0:
        flags.append(
            FlagDetail(
                flag=TamperFlag.PHYSICALLY_IMPOSSIBLE,
                confidence=1.0,
                description=f"TDS value {submission.tds} is negative.",
            )
        )

    # Contaminant physical ranges
    for symbol, value in submission.contaminant_values.items():
        if value < 0:
            flags.append(
                FlagDetail(
                    flag=TamperFlag.PHYSICALLY_IMPOSSIBLE,
                    confidence=1.0,
                    description=f"{symbol} value {value} is negative.",
                )
            )
        limits = _PHYSICAL_LIMITS.get(symbol)
        if limits and value > limits[1]:
            flags.append(
                FlagDetail(
                    flag=TamperFlag.PHYSICALLY_IMPOSSIBLE,
                    confidence=0.9,
                    description=(
                        f"{symbol} value {value} exceeds plausible maximum "
                        f"({limits[1]})."
                    ),
                )
            )

    return flags


def _check_impossible_chemistry(
    submission: TestSubmission,
) -> list[FlagDetail]:
    """Check for chemically impossible combinations."""
    flags: list[FlagDetail] = []

    for rule in _IMPOSSIBLE_CHEMISTRY:
        check_fn = rule["check"]
        try:
            if submission.tds is not None:
                triggered = check_fn(
                    submission.ph,
                    submission.contaminant_values,
                    submission.tds,
                )
            else:
                triggered = check_fn(
                    submission.ph,
                    submission.contaminant_values,
                )
        except TypeError:
            triggered = False

        if triggered:
            flags.append(
                FlagDetail(
                    flag=TamperFlag.IMPOSSIBLE_CHEMISTRY,
                    confidence=0.8,
                    description=str(rule["description"]),
                )
            )

    return flags


def _check_identical_readings(
    submission: TestSubmission,
    history: list[TestResult],
) -> list[FlagDetail]:
    """Detect copy-paste fraud: identical contaminant vectors."""
    if not history or not submission.contaminant_values:
        return []

    sub_values = submission.contaminant_values
    identical_count = 0

    for result in history:
        if result.device_id != submission.device_id:
            continue
        if not result.contaminant_values:
            continue
        if set(result.contaminant_values.keys()) != set(sub_values.keys()):
            continue

        all_match = all(
            abs(result.contaminant_values.get(k, -999) - v) < _IDENTICAL_VALUE_TOLERANCE
            for k, v in sub_values.items()
        )
        if all_match:
            identical_count += 1

    if identical_count >= 3:
        return [
            FlagDetail(
                flag=TamperFlag.IDENTICAL_READINGS,
                confidence=min(0.95, 0.5 + identical_count * 0.1),
                description=(
                    f"Found {identical_count} identical readings from the same "
                    f"device — possible copy-paste fraud."
                ),
            )
        ]
    return []


def _check_extreme_outliers(
    submission: TestSubmission,
    history: list[TestResult],
) -> list[FlagDetail]:
    """Detect values >4 std deviations from regional baseline."""
    if len(history) < 5:
        return []

    flags: list[FlagDetail] = []

    for symbol, value in submission.contaminant_values.items():
        regional_values = [
            r.contaminant_values[symbol]
            for r in history
            if symbol in r.contaminant_values
        ]
        if len(regional_values) < 5:
            continue

        arr = np.array(regional_values, dtype=np.float64)
        mean = float(np.mean(arr))
        std = float(np.std(arr, ddof=1))

        if std < 1e-12:
            continue

        z_score = abs(value - mean) / std
        if z_score > _OUTLIER_STD_THRESHOLD:
            flags.append(
                FlagDetail(
                    flag=TamperFlag.EXTREME_OUTLIER,
                    confidence=min(0.95, 0.5 + (z_score - 4.0) * 0.1),
                    description=(
                        f"{symbol}={value} is {z_score:.1f} std devs from "
                        f"regional mean ({mean:.4f} +/- {std:.4f})."
                    ),
                )
            )

    return flags


def _check_excessive_frequency(
    submission: TestSubmission,
    history: list[TestResult],
) -> list[FlagDetail]:
    """Detect >20 tests per day from a single device."""
    if not history:
        return []

    submission_date = submission.timestamp.date()
    same_day_count = sum(
        1
        for r in history
        if r.device_id == submission.device_id
        and r.timestamp.date() == submission_date
    )

    if same_day_count >= _MAX_TESTS_PER_DAY:
        return [
            FlagDetail(
                flag=TamperFlag.EXCESSIVE_FREQUENCY,
                confidence=min(0.95, 0.6 + (same_day_count - 20) * 0.02),
                description=(
                    f"Device {submission.device_id} has submitted "
                    f"{same_day_count} tests today (limit: {_MAX_TESTS_PER_DAY})."
                ),
            )
        ]
    return []
