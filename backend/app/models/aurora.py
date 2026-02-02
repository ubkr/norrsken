from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class AuroraData(BaseModel):
    """Aurora forecast data from a single source"""
    source: str = Field(..., description="Data source name (e.g., 'noaa_swpc', 'auroras_live')")
    kp_index: float = Field(..., ge=0, le=9, description="KP index (0-9)")
    probability: Optional[float] = Field(None, ge=0, le=100, description="Aurora probability percentage")
    last_updated: datetime = Field(..., description="Timestamp of last data update")

    class Config:
        json_schema_extra = {
            "example": {
                "source": "noaa_swpc",
                "kp_index": 4.5,
                "probability": 35,
                "last_updated": "2026-02-01T22:25:00Z"
            }
        }


class AuroraResponse(BaseModel):
    """Combined aurora data from multiple sources"""
    primary: AuroraData
    secondary: Optional[AuroraData] = None
    tertiary: Optional[AuroraData] = None
