"""Geographic utilities for grid interpolation"""
from typing import Tuple
import math


def bilinear_interpolation(
    grid: list[list[float]],
    lat: float,
    lon: float,
    lat_min: float = -90.0,
    lat_max: float = 90.0,
    lon_min: float = -180.0,
    lon_max: float = 180.0
) -> float:
    """
    Perform bilinear interpolation on a 2D grid.

    Args:
        grid: 2D array where grid[lat_idx][lon_idx] contains values
        lat: Target latitude
        lon: Target longitude
        lat_min: Minimum latitude of grid (default -90)
        lat_max: Maximum latitude of grid (default 90)
        lon_min: Minimum longitude of grid (default -180)
        lon_max: Maximum longitude of grid (default 180)

    Returns:
        Interpolated value at (lat, lon)
    """
    # Calculate grid dimensions
    lat_steps = len(grid)
    lon_steps = len(grid[0]) if lat_steps > 0 else 0

    # Convert lat/lon to grid coordinates
    # NOAA grid: latitude goes from 90 to -90, longitude from -180 to 180
    lat_grid_pos = (lat_max - lat) / (lat_max - lat_min) * (lat_steps - 1)
    lon_grid_pos = (lon - lon_min) / (lon_max - lon_min) * (lon_steps - 1)

    # Get surrounding grid indices
    lat_idx0 = int(math.floor(lat_grid_pos))
    lat_idx1 = min(lat_idx0 + 1, lat_steps - 1)
    lon_idx0 = int(math.floor(lon_grid_pos))
    lon_idx1 = min(lon_idx0 + 1, lon_steps - 1)

    # Clamp indices
    lat_idx0 = max(0, min(lat_idx0, lat_steps - 1))
    lon_idx0 = max(0, min(lon_idx0, lon_steps - 1))

    # Get fractional parts
    lat_frac = lat_grid_pos - lat_idx0
    lon_frac = lon_grid_pos - lon_idx0

    # Get four corner values
    v00 = grid[lat_idx0][lon_idx0]
    v01 = grid[lat_idx0][lon_idx1]
    v10 = grid[lat_idx1][lon_idx0]
    v11 = grid[lat_idx1][lon_idx1]

    # Bilinear interpolation
    v0 = v00 * (1 - lon_frac) + v01 * lon_frac
    v1 = v10 * (1 - lon_frac) + v11 * lon_frac
    result = v0 * (1 - lat_frac) + v1 * lat_frac

    return result


def get_grid_indices(lat: float, lon: float) -> Tuple[int, int]:
    """
    Get grid indices for NOAA 360x181 grid.

    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)

    Returns:
        Tuple of (lat_index, lon_index)
    """
    # NOAA grid: 181 latitude steps (90 to -90), 360 longitude steps (-180 to 180)
    lat_idx = int(90 - lat)
    lon_idx = int(lon + 180)

    # Clamp to valid range
    lat_idx = max(0, min(lat_idx, 180))
    lon_idx = max(0, min(lon_idx, 359))

    return (lat_idx, lon_idx)
