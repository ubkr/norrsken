from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict
from .aurora import AuroraResponse
from .weather import WeatherResponse


class Location(BaseModel):
    """Geographic location"""
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    name: str = Field(..., description="Location name")


class MoonData(BaseModel):
    """Moon phase and position data used in visibility scoring."""
    illumination: float = Field(..., ge=0.0, le=1.0, description="Moon illumination fraction (0=new, 1=full)")
    elevation_deg: float = Field(..., description="Moon elevation above horizon in degrees")
    penalty_pts: float = Field(..., ge=0.0, le=15.0, description="Score penalty deducted (0–15 pts)")


class SunData(BaseModel):
    """Sun elevation and twilight phase data used in visibility scoring."""
    elevation_deg: float = Field(..., description="Sun elevation above horizon in degrees")
    twilight_phase: str = Field(..., description="Twilight phase: daylight, civil_twilight, nautical_twilight, astronomical_twilight, darkness")
    penalty_pts: float = Field(..., ge=0.0, le=50.0, description="Score penalty deducted (0–50 pts)")


class VisibilityBreakdown(BaseModel):
    """Breakdown of visibility score components"""
    aurora: float = Field(..., ge=0, le=40, description="Aurora activity score (max 40)")
    clouds: float = Field(..., ge=0, le=30, description="Cloud cover score (max 30)")
    visibility: float = Field(..., ge=0, le=20, description="Visibility score (max 20)")
    precipitation: float = Field(..., ge=0, le=10, description="Precipitation score (max 10)")
    moon: MoonData
    sun: SunData


class VisibilityScore(BaseModel):
    """Overall visibility score with breakdown"""
    total_score: float = Field(..., ge=0, le=100, description="Total visibility score (0-100)")
    breakdown: VisibilityBreakdown
    recommendation: str = Field(..., description="Human-readable recommendation")


class PredictionResponse(BaseModel):
    """Complete prediction response"""
    timestamp: datetime = Field(..., description="Prediction timestamp")
    location: Location
    aurora: AuroraResponse
    weather: WeatherResponse
    visibility_score: VisibilityScore


class ForecastItem(BaseModel):
    """Single forecast data point"""
    timestamp: datetime
    visibility_score: float = Field(..., ge=0, le=100)
    kp_index: float = Field(..., ge=0, le=9)
    cloud_cover: float = Field(..., ge=0, le=100)


class ForecastResponse(BaseModel):
    """Array of forecast predictions"""
    location: Location
    forecast: list[ForecastItem]
