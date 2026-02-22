"""Prediction API endpoints"""
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from typing import List, Optional
from ...models.prediction import (
    PredictionResponse,
    ForecastResponse,
    ForecastItem,
    Location,
)
from ...services.aggregator import aggregator
from ...services.correlation import calculate_visibility_score
from ...config import settings
from ...utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/v1/prediction", tags=["prediction"])


@router.get("/current", response_model=PredictionResponse)
async def get_current_prediction(
    lat: Optional[float] = Query(None, ge=-90, le=90, description="Latitude"),
    lon: Optional[float] = Query(None, ge=-180, le=180, description="Longitude")
):
    """
    Get current aurora visibility prediction with all data sources.

    Returns combined aurora and weather data with visibility score.
    """
    try:
        lat = lat if lat is not None else settings.location_lat
        lon = lon if lon is not None else settings.location_lon

        # Fetch aurora and weather data
        aurora_data = await aggregator.fetch_aurora_data(lat, lon)
        weather_data = await aggregator.fetch_weather_data(lat, lon)

        # Calculate visibility score
        visibility_score = calculate_visibility_score(
            aurora_data.primary,
            weather_data.primary,
            lat=lat,
            lon=lon,
        )

        # Build response
        response = PredictionResponse(
            timestamp=datetime.utcnow(),
            location=Location(
                lat=lat,
                lon=lon,
                name=settings.location_name
            ),
            aurora=aurora_data,
            weather=weather_data,
            visibility_score=visibility_score
        )

        return response

    except Exception as e:
        logger.error(f"Error generating prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast", response_model=ForecastResponse)
async def get_forecast(
    hours: int = Query(default=24, ge=1, le=72, description="Number of hours to forecast"),
    lat: Optional[float] = Query(None, ge=-90, le=90, description="Latitude"),
    lon: Optional[float] = Query(None, ge=-180, le=180, description="Longitude")
):
    """
    Get hourly aurora visibility forecast.

    Note: This is a simplified forecast using current data.
    For production, would fetch actual hourly forecasts from APIs.

    Args:
        hours: Number of hours to forecast (1-72, default 24)

    Returns:
        Array of hourly predictions
    """
    try:
        lat = lat if lat is not None else settings.location_lat
        lon = lon if lon is not None else settings.location_lon

        # Fetch current data
        aurora_data = await aggregator.fetch_aurora_data(lat, lon)
        weather_data = await aggregator.fetch_weather_data(lat, lon)

        # Calculate current visibility score
        current_score = calculate_visibility_score(
            aurora_data.primary,
            weather_data.primary,
            lat=lat,
            lon=lon,
        )

        # Generate forecast items
        # For MVP, we create a simple forecast based on current data
        # In production, would fetch hourly forecasts from weather/aurora APIs
        forecast_items: List[ForecastItem] = []
        now = datetime.utcnow()

        for hour in range(hours):
            timestamp = now + timedelta(hours=hour)

            # Simple variation for demo purposes
            # In production, use actual hourly forecast data
            score_variation = 0
            if 18 <= timestamp.hour <= 23:  # Evening hours better
                score_variation = 5
            elif 0 <= timestamp.hour <= 6:  # Night hours best
                score_variation = 10

            forecast_items.append(ForecastItem(
                timestamp=timestamp,
                visibility_score=min(100, current_score.total_score + score_variation),
                kp_index=aurora_data.primary.kp_index,
                cloud_cover=weather_data.primary.cloud_cover
            ))

        response = ForecastResponse(
            location=Location(
                lat=lat,
                lon=lon,
                name=settings.location_name
            ),
            forecast=forecast_items
        )

        return response

    except Exception as e:
        logger.error(f"Error generating forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))
