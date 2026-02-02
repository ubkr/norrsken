"""Tests for geographic utilities"""
import pytest
from app.utils.geo import bilinear_interpolation, get_grid_indices


def test_bilinear_interpolation_exact_grid_point():
    """Test interpolation at exact grid point"""
    # Simple 3x3 grid
    grid = [
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
        [7.0, 8.0, 9.0]
    ]

    # Test center point
    result = bilinear_interpolation(
        grid=grid,
        lat=0.0,
        lon=0.0,
        lat_min=-90.0,
        lat_max=90.0,
        lon_min=-180.0,
        lon_max=180.0
    )

    # Should be close to middle value
    assert 4.0 <= result <= 6.0


def test_bilinear_interpolation_corners():
    """Test interpolation at grid corners"""
    grid = [
        [10.0, 20.0],
        [30.0, 40.0]
    ]

    # Top-left corner
    result = bilinear_interpolation(
        grid=grid,
        lat=90.0,
        lon=-180.0,
        lat_min=-90.0,
        lat_max=90.0,
        lon_min=-180.0,
        lon_max=180.0
    )
    assert result == pytest.approx(10.0, abs=0.1)

    # Bottom-right corner
    result = bilinear_interpolation(
        grid=grid,
        lat=-90.0,
        lon=180.0,
        lat_min=-90.0,
        lat_max=90.0,
        lon_min=-180.0,
        lon_max=180.0
    )
    assert result == pytest.approx(40.0, abs=0.1)


def test_bilinear_interpolation_midpoint():
    """Test interpolation between four equal values"""
    grid = [
        [10.0, 10.0],
        [10.0, 10.0]
    ]

    result = bilinear_interpolation(
        grid=grid,
        lat=0.0,
        lon=0.0,
        lat_min=-90.0,
        lat_max=90.0,
        lon_min=-180.0,
        lon_max=180.0
    )

    # All values are 10, so result should be 10
    assert result == pytest.approx(10.0, abs=0.01)


def test_get_grid_indices_sodra_sandby():
    """Test grid indices for Södra Sandby coordinates"""
    lat_idx, lon_idx = get_grid_indices(55.7, 13.4)

    # For 55.7°N, expect lat_idx around 34 (90 - 55.7 ≈ 34.3)
    assert 30 <= lat_idx <= 40

    # For 13.4°E, expect lon_idx around 193 (13.4 + 180 ≈ 193.4)
    assert 190 <= lon_idx <= 200


def test_get_grid_indices_bounds():
    """Test grid indices stay within bounds"""
    # North pole
    lat_idx, lon_idx = get_grid_indices(90.0, 0.0)
    assert 0 <= lat_idx <= 180
    assert 0 <= lon_idx <= 359

    # South pole
    lat_idx, lon_idx = get_grid_indices(-90.0, 0.0)
    assert 0 <= lat_idx <= 180
    assert 0 <= lon_idx <= 359

    # Date line
    lat_idx, lon_idx = get_grid_indices(0.0, 180.0)
    assert 0 <= lat_idx <= 180
    assert 0 <= lon_idx <= 359

    # Prime meridian
    lat_idx, lon_idx = get_grid_indices(0.0, 0.0)
    assert 0 <= lat_idx <= 180
    assert 0 <= lon_idx <= 359
