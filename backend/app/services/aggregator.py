"""Multi-source data aggregation with fallbacks"""
from typing import Optional, List
from ..models.aurora import AuroraData, AuroraResponse
from ..models.weather import WeatherData, WeatherResponse
from .aurora.noaa_client import NOAAClient
from .aurora.auroras_live import AurorasLiveClient
from .weather.metno_client import MetNoClient
from .weather.smhi_client import SMHIClient
from .weather.openmeteo_client import OpenMeteoClient
from .cache_service import cache
from ..config import settings
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class DataAggregator:
    """Aggregates data from multiple sources with fallback logic"""

    def __init__(self):
        # Initialize aurora clients
        self.aurora_clients = [
            NOAAClient(),
            AurorasLiveClient()
        ]

        # Initialize weather clients
        self.weather_clients = [
            MetNoClient(),      # Primary - Nordic weather
            SMHIClient(),       # Secondary - Swedish official weather
            OpenMeteoClient()   # Tertiary
        ]

    async def fetch_aurora_data(self, lat: float, lon: float) -> AuroraResponse:
        """
        Fetch aurora data from multiple sources with fallback.

        Tries sources in order:
        1. NOAA SWPC (primary)
        2. Auroras.live (secondary)
        3. Aurora Space (tertiary)

        Uses cache to reduce API calls.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            AuroraResponse with data from available sources

        Raises:
            Exception: If all sources fail
        """
        results: List[Optional[AuroraData]] = []

        for client in self.aurora_clients:
            cache_key = f"aurora_{client.source_name}_{lat}_{lon}"

            # Try cache first
            cached = await cache.get(cache_key)
            if cached:
                logger.info(f"Using cached {client.source_name} aurora data")
                results.append(cached)
                continue

            # Fetch fresh data
            try:
                data = await client.fetch_data(lat, lon)
                results.append(data)

                # Cache the result
                await cache.set(cache_key, data, settings.cache_ttl_aurora)

            except Exception as e:
                logger.warning(f"Failed to fetch from {client.source_name}: {e}")
                results.append(None)

        # Build response with available data
        primary = results[0] if len(results) > 0 else None
        secondary = results[1] if len(results) > 1 else None
        tertiary = results[2] if len(results) > 2 else None

        # If primary failed, promote secondary to primary
        if primary is None and secondary is not None:
            primary = secondary
            secondary = tertiary
            tertiary = None

        if primary is None:
            raise Exception("All aurora data sources failed")

        return AuroraResponse(
            primary=primary,
            secondary=secondary,
            tertiary=tertiary
        )

    async def fetch_weather_data(self, lat: float, lon: float) -> WeatherResponse:
        """
        Fetch weather data from multiple sources with fallback.

        Tries sources in order:
        1. Met.no (primary)
        2. SMHI (secondary)
        3. Open-Meteo (tertiary)

        Uses cache to reduce API calls.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            WeatherResponse with data from available sources

        Raises:
            Exception: If all sources fail
        """
        results: List[Optional[WeatherData]] = []

        for client in self.weather_clients:
            cache_key = f"weather_{client.source_name}_{lat}_{lon}"

            # Try cache first
            cached = await cache.get(cache_key)
            if cached:
                logger.info(f"Using cached {client.source_name} weather data")
                results.append(cached)
                continue

            # Fetch fresh data
            try:
                data = await client.fetch_data(lat, lon)
                results.append(data)

                # Cache the result
                await cache.set(cache_key, data, settings.cache_ttl_weather)

            except Exception as e:
                logger.warning(f"Failed to fetch from {client.source_name}: {e}")
                results.append(None)

        # Build response with available data
        primary = results[0] if len(results) > 0 else None
        secondary = results[1] if len(results) > 1 else None
        tertiary = results[2] if len(results) > 2 else None

        # Promote secondary/tertiary if primary fails
        if primary is None and secondary is not None:
            primary = secondary
            secondary = tertiary
            tertiary = None
        elif primary is None and tertiary is not None:
            primary = tertiary
            tertiary = None

        if primary is None:
            raise Exception("All weather data sources failed")

        # Keep primary source priority for weather conditions, but patch visibility
        # from the best available fallback source when primary has no visibility data.
        if primary.visibility_km is None:
            best_vis = None
            source_name = None
            if secondary is not None and secondary.visibility_km is not None:
                best_vis = secondary.visibility_km
                source_name = secondary.source
            elif tertiary is not None and tertiary.visibility_km is not None:
                best_vis = tertiary.visibility_km
                source_name = tertiary.source

            if best_vis is not None:
                logger.info(f"Patched primary visibility with {source_name} value: {best_vis} km")
                primary = primary.model_copy(update={"visibility_km": best_vis})

        return WeatherResponse(
            primary=primary,
            secondary=secondary,
            tertiary=tertiary
        )


# Global aggregator instance
aggregator = DataAggregator()
