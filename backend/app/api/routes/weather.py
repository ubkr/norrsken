"""Weather data API endpoints"""
from fastapi import APIRouter, HTTPException
from ...models.weather import WeatherResponse
from ...services.aggregator import aggregator
from ...config import settings
from ...utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1/weather", tags=["weather"])


@router.get("/sources", response_model=WeatherResponse)
async def get_weather_sources():
    """
    Get weather data from all available sources for comparison.

    Returns data from SMHI and Open-Meteo.
    """
    try:
        lat = settings.location_lat
        lon = settings.location_lon

        weather_data = await aggregator.fetch_weather_data(lat, lon)
        return weather_data

    except Exception as e:
        logger.error(f"Error fetching weather sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))
