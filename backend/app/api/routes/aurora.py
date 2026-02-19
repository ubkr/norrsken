"""Aurora data API endpoints"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from ...models.aurora import AuroraResponse
from ...services.aggregator import aggregator
from ...config import settings
from ...utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1/aurora", tags=["aurora"])


@router.get("/sources", response_model=AuroraResponse)
async def get_aurora_sources(
    lat: Optional[float] = Query(None, ge=-90, le=90, description="Latitude"),
    lon: Optional[float] = Query(None, ge=-180, le=180, description="Longitude")
):
    """
    Get aurora data from all available sources for comparison.

    Returns data from NOAA, Auroras.live, and Aurora Space.
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

        aurora_data = await aggregator.fetch_aurora_data(lat, lon)
        return aurora_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching aurora sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))
