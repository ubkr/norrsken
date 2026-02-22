"""Tests for weather visibility patching in aggregator."""
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.models.weather import WeatherData
from app.services.aggregator import DataAggregator
from app.services import aggregator as aggregator_module


class StubWeatherClient:
    def __init__(self, source_name: str, data: WeatherData):
        self._source_name = source_name
        self._data = data

    @property
    def source_name(self) -> str:
        return self._source_name

    async def fetch_data(self, lat: float, lon: float) -> WeatherData:
        return self._data


def _weather(source: str, visibility_km):
    return WeatherData(
        source=source,
        cloud_cover=20.0,
        visibility_km=visibility_km,
        precipitation_mm=0.0,
        temperature_c=1.0,
        last_updated=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_primary_visibility_patched_from_secondary(monkeypatch):
    aggregator = DataAggregator()
    aggregator.weather_clients = [
        StubWeatherClient("met_no", _weather("met_no", None)),
        StubWeatherClient("smhi", _weather("smhi", 12.5)),
        StubWeatherClient("open_meteo", _weather("open_meteo", 9.0)),
    ]

    monkeypatch.setattr(aggregator_module.cache, "get", AsyncMock(return_value=None))
    monkeypatch.setattr(aggregator_module.cache, "set", AsyncMock(return_value=None))

    response = await aggregator.fetch_weather_data(55.7, 13.4)

    assert response.primary.source == "met_no"
    assert response.primary.visibility_km == 12.5


@pytest.mark.asyncio
async def test_primary_visibility_patched_from_tertiary_when_secondary_missing(monkeypatch):
    aggregator = DataAggregator()
    aggregator.weather_clients = [
        StubWeatherClient("met_no", _weather("met_no", None)),
        StubWeatherClient("smhi", _weather("smhi", None)),
        StubWeatherClient("open_meteo", _weather("open_meteo", 8.0)),
    ]

    monkeypatch.setattr(aggregator_module.cache, "get", AsyncMock(return_value=None))
    monkeypatch.setattr(aggregator_module.cache, "set", AsyncMock(return_value=None))

    response = await aggregator.fetch_weather_data(55.7, 13.4)

    assert response.primary.source == "met_no"
    assert response.primary.visibility_km == 8.0


@pytest.mark.asyncio
async def test_primary_visibility_not_patched_when_present(monkeypatch):
    aggregator = DataAggregator()
    aggregator.weather_clients = [
        StubWeatherClient("met_no", _weather("met_no", 11.0)),
        StubWeatherClient("smhi", _weather("smhi", 18.0)),
        StubWeatherClient("open_meteo", _weather("open_meteo", 7.0)),
    ]

    monkeypatch.setattr(aggregator_module.cache, "get", AsyncMock(return_value=None))
    monkeypatch.setattr(aggregator_module.cache, "set", AsyncMock(return_value=None))

    response = await aggregator.fetch_weather_data(55.7, 13.4)

    assert response.primary.source == "met_no"
    assert response.primary.visibility_km == 11.0


@pytest.mark.asyncio
async def test_primary_visibility_remains_none_when_all_sources_missing(monkeypatch):
    aggregator = DataAggregator()
    aggregator.weather_clients = [
        StubWeatherClient("met_no", _weather("met_no", None)),
        StubWeatherClient("smhi", _weather("smhi", None)),
        StubWeatherClient("open_meteo", _weather("open_meteo", None)),
    ]

    monkeypatch.setattr(aggregator_module.cache, "get", AsyncMock(return_value=None))
    monkeypatch.setattr(aggregator_module.cache, "set", AsyncMock(return_value=None))

    response = await aggregator.fetch_weather_data(55.7, 13.4)

    assert response.primary.source == "met_no"
    assert response.primary.visibility_km is None
