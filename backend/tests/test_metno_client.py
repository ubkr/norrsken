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
    assert data.visibility_km is None
    assert data.precipitation_mm >= 0
    assert data.temperature_c is not None
    assert isinstance(data.last_updated, datetime)
