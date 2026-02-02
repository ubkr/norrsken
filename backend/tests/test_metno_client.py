"""Tests for Met.no weather client"""
import pytest
from datetime import datetime
from app.services.weather.metno_client import MetNoClient


@pytest.mark.asyncio
async def test_metno_fetch_data():
    """Test Met.no data fetching"""
    client = MetNoClient()
    data = await client.fetch_data(55.7, 13.4)

    assert data.source == "met_no"
    assert 0 <= data.cloud_cover <= 100
    assert data.visibility_km > 0
    assert data.precipitation_mm >= 0
    assert data.temperature_c is not None
    assert isinstance(data.last_updated, datetime)


def test_visibility_estimation():
    """Test fog-based visibility estimation"""
    client = MetNoClient()

    # Excellent visibility (0-20% fog)
    assert client._estimate_visibility_from_fog(0) == 50.0
    assert client._estimate_visibility_from_fog(15) == 50.0

    # Good visibility (20-50% fog)
    assert client._estimate_visibility_from_fog(25) == 20.0
    assert client._estimate_visibility_from_fog(40) == 20.0

    # Moderate visibility (50-80% fog)
    assert client._estimate_visibility_from_fog(60) == 5.0
    assert client._estimate_visibility_from_fog(75) == 5.0

    # Poor visibility (80-100% fog)
    assert client._estimate_visibility_from_fog(90) == 1.0
    assert client._estimate_visibility_from_fog(100) == 1.0


def test_visibility_estimation_edge_cases():
    """Test visibility estimation at boundary values"""
    client = MetNoClient()

    # Test boundary conditions
    assert client._estimate_visibility_from_fog(19.9) == 50.0
    assert client._estimate_visibility_from_fog(20.0) == 20.0
    assert client._estimate_visibility_from_fog(49.9) == 20.0
    assert client._estimate_visibility_from_fog(50.0) == 5.0
    assert client._estimate_visibility_from_fog(79.9) == 5.0
    assert client._estimate_visibility_from_fog(80.0) == 1.0
