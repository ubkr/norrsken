"""Weather data API endpoints"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from ...models.weather import WeatherResponse
from ...services.aggregator import aggregator
from ...config import settings
from ...utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1/weather", tags=["weather"])


@router.get("/sources", response_model=WeatherResponse)
async def get_weather_sources(
    lat: Optional[float] = Query(None, ge=-90, le=90, description="Latitude"),
    lon: Optional[float] = Query(None, ge=-180, le=180, description="Longitude")
):
    """
    Get weather data from all available sources for comparison.

    Returns data from SMHI and Open-Meteo.
    """
    try:
        has_lat = lat is not None
        has_lon = lon is not None

        if has_lat != has_lon:
            raise HTTPException(
                status_code=422,
                detail="lat and lon must be provided together, or omitted together"
            )

        if not has_lat and not has_lon:
            lat = settings.location_lat
            lon = settings.location_lon

        weather_data = await aggregator.fetch_weather_data(lat, lon)
        return weather_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching weather sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))
