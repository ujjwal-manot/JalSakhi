"""Spatial contamination mapping using Ordinary Kriging with IDW fallback.

Generates continuous contamination heatmaps from sparse GPS-tagged test results.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
from numpy.typing import NDArray


# ---------------------------------------------------------------------------
# Immutable data classes
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TestPoint:
    """A single GPS-tagged contaminant reading."""
    __test__ = False

    latitude: float
    longitude: float
    value: float
    contaminant: str = "NH3"


@dataclass(frozen=True)
class HeatmapGrid:
    """Gridded interpolation result."""

    lat_grid: tuple[float, ...]
    lng_grid: tuple[float, ...]
    values: tuple[tuple[float, ...], ...]  # 2-D grid (rows=lat, cols=lng)
    contaminant: str
    method: str  # "kriging" or "idw"


@dataclass(frozen=True)
class Hotspot:
    """A detected contamination hotspot."""

    latitude: float
    longitude: float
    value: float
    contaminant: str
    exceeds_who_limit: bool


# ---------------------------------------------------------------------------
# WHO limits (duplicated here to keep module self-contained)
# ---------------------------------------------------------------------------

WHO_LIMITS: dict[str, float] = {
    "NH3": 0.5,
    "Pb": 10.0,
    "As": 10.0,
    "NO3": 50.0,
    "Fe": 0.3,
}

# Minimum points required for Kriging
_KRIGING_MIN_POINTS = 10


# ---------------------------------------------------------------------------
# ContaminationMapper
# ---------------------------------------------------------------------------

class ContaminationMapper:
    """Generates contamination heatmaps from sparse GPS-tagged test results."""

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    def interpolate(
        self,
        points: list[TestPoint],
        grid_resolution: int = 50,
        contaminant: str = "NH3",
    ) -> HeatmapGrid:
        """Interpolate sparse test points into a continuous gridded surface.

        Uses Ordinary Kriging with a spherical variogram when there are
        enough points (>=10).  Falls back to Inverse Distance Weighting
        for fewer points.

        Parameters
        ----------
        points : list[TestPoint]
            Sparse GPS-tagged readings.
        grid_resolution : int
            Number of grid cells along each axis.
        contaminant : str
            Contaminant symbol to filter on.

        Returns
        -------
        HeatmapGrid
            Immutable gridded result.
        """
        if grid_resolution < 2:
            raise ValueError("grid_resolution must be >= 2")

        filtered = [p for p in points if p.contaminant == contaminant]

        if len(filtered) == 0:
            return _empty_grid(contaminant)

        if len(filtered) == 1:
            return _single_point_grid(filtered[0], contaminant)

        lats = np.array([p.latitude for p in filtered], dtype=np.float64)
        lngs = np.array([p.longitude for p in filtered], dtype=np.float64)
        vals = np.array([p.value for p in filtered], dtype=np.float64)

        lat_grid = np.linspace(lats.min(), lats.max(), grid_resolution)
        lng_grid = np.linspace(lngs.min(), lngs.max(), grid_resolution)

        if len(filtered) >= _KRIGING_MIN_POINTS:
            grid_values, method = _kriging_interpolate(
                lats, lngs, vals, lat_grid, lng_grid,
            )
        else:
            grid_values = _idw_interpolate(lats, lngs, vals, lat_grid, lng_grid)
            method = "idw"

        return HeatmapGrid(
            lat_grid=tuple(float(v) for v in lat_grid),
            lng_grid=tuple(float(v) for v in lng_grid),
            values=tuple(
                tuple(float(v) for v in row) for row in grid_values
            ),
            contaminant=contaminant,
            method=method,
        )

    def get_hotspots(
        self,
        grid: HeatmapGrid,
        who_limit: Optional[float] = None,
        percentile: float = 90,
    ) -> list[Hotspot]:
        """Identify contamination hotspots above WHO limit or percentile.

        Parameters
        ----------
        grid : HeatmapGrid
            Output from ``interpolate``.
        who_limit : float | None
            WHO safe limit.  If None, looked up from internal table.
        percentile : float
            Only values above this percentile are considered hotspots.

        Returns
        -------
        list[Hotspot]
        """
        if not grid.values or not grid.lat_grid:
            return []

        limit = who_limit if who_limit is not None else WHO_LIMITS.get(grid.contaminant, 0.0)
        values_arr = np.array(grid.values, dtype=np.float64)
        threshold = float(np.percentile(values_arr, percentile))

        hotspots: list[Hotspot] = []
        for i, lat in enumerate(grid.lat_grid):
            for j, lng in enumerate(grid.lng_grid):
                val = values_arr[i, j]
                if val >= threshold:
                    hotspots.append(
                        Hotspot(
                            latitude=lat,
                            longitude=lng,
                            value=float(val),
                            contaminant=grid.contaminant,
                            exceeds_who_limit=val > limit,
                        )
                    )

        return hotspots


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _empty_grid(contaminant: str) -> HeatmapGrid:
    """Return an empty heatmap grid."""
    return HeatmapGrid(
        lat_grid=(),
        lng_grid=(),
        values=(),
        contaminant=contaminant,
        method="none",
    )


def _single_point_grid(point: TestPoint, contaminant: str) -> HeatmapGrid:
    """Return a 1x1 grid from a single point."""
    return HeatmapGrid(
        lat_grid=(point.latitude,),
        lng_grid=(point.longitude,),
        values=((point.value,),),
        contaminant=contaminant,
        method="single",
    )


def _kriging_interpolate(
    lats: NDArray[np.float64],
    lngs: NDArray[np.float64],
    vals: NDArray[np.float64],
    lat_grid: NDArray[np.float64],
    lng_grid: NDArray[np.float64],
) -> tuple[NDArray[np.float64], str]:
    """Ordinary Kriging interpolation with spherical variogram.

    Falls back to IDW if pykrige is unavailable or Kriging fails.
    """
    try:
        from pykrige.ok import OrdinaryKriging  # type: ignore[import-untyped]

        ok = OrdinaryKriging(
            lngs,
            lats,
            vals,
            variogram_model="spherical",
            verbose=False,
            enable_plotting=False,
        )
        z_grid, _ = ok.execute("grid", lng_grid, lat_grid)
        # Clamp negative predictions to zero (physical constraint)
        z_grid = np.clip(z_grid, 0.0, None)
        return z_grid, "kriging"
    except Exception:
        # Graceful fallback to IDW
        return _idw_interpolate(lats, lngs, vals, lat_grid, lng_grid), "idw"


def _idw_interpolate(
    lats: NDArray[np.float64],
    lngs: NDArray[np.float64],
    vals: NDArray[np.float64],
    lat_grid: NDArray[np.float64],
    lng_grid: NDArray[np.float64],
    power: float = 2.0,
) -> NDArray[np.float64]:
    """Inverse Distance Weighting interpolation.

    Parameters
    ----------
    power : float
        Distance exponent (higher = more local influence).
    """
    lng_mesh, lat_mesh = np.meshgrid(lng_grid, lat_grid)
    result = np.zeros_like(lng_mesh, dtype=np.float64)

    for i in range(lng_mesh.shape[0]):
        for j in range(lng_mesh.shape[1]):
            dist = np.sqrt(
                (lats - lat_mesh[i, j]) ** 2 + (lngs - lng_mesh[i, j]) ** 2
            )
            # If a grid point coincides with a data point, use its value
            exact = dist < 1e-12
            if np.any(exact):
                result[i, j] = vals[exact][0]
            else:
                weights = 1.0 / (dist ** power)
                result[i, j] = np.sum(weights * vals) / np.sum(weights)

    return result


# ---------------------------------------------------------------------------
# Synthetic test data generator
# ---------------------------------------------------------------------------

def generate_bhagalpur_test_points(
    n: int = 20,
    contaminant: str = "NH3",
    seed: int = 42,
) -> list[TestPoint]:
    """Generate synthetic GPS points around Bhagalpur, Bihar.

    Centre: 25.24N, 86.98E.  Spread ~0.05 degrees (~5 km).
    Ammonia values drawn from log-normal distribution (realistic for
    groundwater contamination).
    """
    rng = np.random.default_rng(seed)
    center_lat, center_lng = 25.24, 86.98
    spread = 0.05

    lats = center_lat + rng.normal(0, spread, size=n)
    lngs = center_lng + rng.normal(0, spread, size=n)
    # Log-normal: median ~0.3 mg/L, some values above WHO limit 0.5
    raw_values = rng.lognormal(mean=-1.2, sigma=0.8, size=n)
    values = np.clip(raw_values, 0.01, 10.0)

    return [
        TestPoint(
            latitude=float(lats[i]),
            longitude=float(lngs[i]),
            value=float(round(values[i], 4)),
            contaminant=contaminant,
        )
        for i in range(n)
    ]
