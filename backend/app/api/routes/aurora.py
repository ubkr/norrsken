"""Aurora data API endpoints"""
from fastapi import APIRouter, HTTPException
from ...models.aurora import AuroraResponse
from ...services.aggregator import aggregator
from ...config import settings
from ...utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1/aurora", tags=["aurora"])


@router.get("/sources", response_model=AuroraResponse)
async def get_aurora_sources():
    """
    Get aurora data from all available sources for comparison.

    Returns data from NOAA, Auroras.live, and Aurora Space.
    """
    try:
        lat = settings.location_lat
        lon = settings.location_lon

        aurora_data = await aggregator.fetch_aurora_data(lat, lon)
        return aurora_data

    except Exception as e:
        logger.error(f"Error fetching aurora sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))
