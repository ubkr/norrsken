"""SMHI (Swedish Meteorological and Hydrological Institute) weather client"""
import httpx
from datetime import datetime
from typing import Optional, Dict, Any
from .base import WeatherSourceBase
from ...models.weather import WeatherData
from ...utils.logger import setup_logger

logger = setup_logger(__name__)


class SMHIClient(WeatherSourceBase):
    """Client for SMHI weather forecast data"""

    BASE_URL = "https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2"

    @property
    def source_name(self) -> str:
        return "smhi"

    async def fetch_data(self, lat: float, lon: float) -> WeatherData:
        """
        Fetch weather data from SMHI.

        SMHI provides 2.5km resolution weather forecasts for Sweden.
        Cloud cover is given in oktas (0-8 scale).

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            WeatherData with cloud cover, visibility, precipitation
        """
        try:
            # Build URL
            url = f"{self.BASE_URL}/geotype/point/lon/{lon}/lat/{lat}/data.json"

            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url)
                response.raise_for_status()

                # Check if response is actually JSON
                content_type = response.headers.get('content-type', '')
                if 'application/json' not in content_type and 'text/json' not in content_type:
                    raise ValueError(f"SMHI returned non-JSON content: {content_type}")

                data = response.json()

            # Get the first timeseries entry (current/nearest forecast)
            timeseries = data.get("timeSeries", [])
            if not timeseries:
                raise ValueError("No timeseries data in SMHI response")

            current = timeseries[0]

            # Parse timestamp
            valid_time_str = current.get("validTime", "")
            try:
                last_updated = datetime.fromisoformat(valid_time_str.replace("Z", "+00:00"))
            except ValueError:
                logger.warning(f"Could not parse SMHI timestamp: {valid_time_str}")
                last_updated = datetime.utcnow()

            # Extract parameters
            params = {p["name"]: p["values"][0] for p in current.get("parameters", [])}

            # Cloud cover: use total cloud cover mean (tcc_mean) in oktas (0-8)
            # Convert to percentage: (oktas / 8) * 100
            tcc = params.get("tcc_mean", 4)  # Total cloud cover mean (default to 4 octas = 50%)
            cloud_cover_pct = (tcc / 8.0) * 100

            # Visibility in km
            visibility_km = params.get("vis", 10)  # Default 10km if missing

            # Precipitation category (pcat): 0=none, 1=snow, 2=snow/rain, 3=rain, 4=drizzle, 5=freezing rain, 6=freezing drizzle
            # Precipitation mean (pmean): mm/h
            pcat = params.get("pcat", 0)
            pmean = params.get("pmean", 0)  # Precipitation in mm/h

            # Temperature
            temperature_c = params.get("t", None)

            logger.info(
                f"SMHI data fetched: Cloud={tcc}/8 oktas ({cloud_cover_pct:.1f}%), "
                f"Vis={visibility_km}km, Precip={pmean}mm/h at ({lat}, {lon})"
            )

            return WeatherData(
                source=self.source_name,
                cloud_cover=round(cloud_cover_pct, 1),
                visibility_km=visibility_km,
                precipitation_mm=pmean,
                temperature_c=temperature_c,
                last_updated=last_updated
            )

        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching SMHI data: {e}")
            raise Exception(f"Failed to fetch SMHI weather data: {e}")
        except (KeyError, IndexError, ValueError, TypeError) as e:
            logger.error(f"Error parsing SMHI data: {e}")
            raise Exception(f"Failed to parse SMHI weather data: {e}")
