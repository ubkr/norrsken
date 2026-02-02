"""NOAA Space Weather Prediction Center aurora data client"""
import httpx
from datetime import datetime
from typing import Optional
from .base import AuroraSourceBase
from ...models.aurora import AuroraData
from ...utils.geo import bilinear_interpolation
from ...utils.logger import setup_logger

logger = setup_logger(__name__)


class NOAAClient(AuroraSourceBase):
    """Client for NOAA SWPC aurora forecast data"""

    ENDPOINT = "https://services.swpc.noaa.gov/json/ovation_aurora_latest.json"

    @property
    def source_name(self) -> str:
        return "noaa_swpc"

    async def fetch_data(self, lat: float, lon: float) -> AuroraData:
        """
        Fetch aurora data from NOAA SWPC.

        The API returns a 360x181 grid covering the entire globe.
        Each coordinate contains an aurora probability value (0-100).

        Args:
            lat: Latitude (55.7 for Södra Sandby)
            lon: Longitude (13.4 for Södra Sandby)

        Returns:
            AuroraData with KP index estimate and probability
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.ENDPOINT)
                response.raise_for_status()
                data = response.json()

            # Parse grid data
            coordinates = data.get("coordinates", [])
            if not coordinates:
                raise ValueError("No coordinate data in NOAA response")

            # Extract observation time
            observation_time_str = data.get("Observation Time", "")
            try:
                # Format: "2026-02-01T21:12:00Z"
                last_updated = datetime.strptime(observation_time_str, "%Y-%m-%dT%H:%M:%SZ")
            except (ValueError, TypeError):
                logger.warning(f"Could not parse NOAA timestamp: {observation_time_str}")
                last_updated = datetime.utcnow()

            # Build 2D grid for interpolation
            # NOAA data format: flat list of [lon, lat, aurora_value]
            # Need to reorganize into 2D grid [lat][lon]
            # Grid dimensions: 181 latitudes (-90 to 90), 360 longitudes (0 to 359)
            grid = [[0.0 for _ in range(360)] for _ in range(181)]

            for coord in coordinates:
                lon_val, lat_val, aurora_val = coord[0], coord[1], coord[2]

                # Convert to grid indices
                # Latitude: -90 to 90 maps to indices 180 to 0
                lat_idx = int(90 - lat_val)
                # Longitude: 0 to 359
                lon_idx = int(lon_val) % 360

                # Clamp indices
                lat_idx = max(0, min(180, lat_idx))
                lon_idx = max(0, min(359, lon_idx))

                grid[lat_idx][lon_idx] = aurora_val

            # Perform bilinear interpolation
            probability = bilinear_interpolation(
                grid=grid,
                lat=lat,
                lon=lon,
                lat_min=-90.0,
                lat_max=90.0,
                lon_min=-180.0,
                lon_max=180.0
            )

            # Estimate KP index from probability
            # Rough approximation: probability correlates with KP
            # For southern Sweden (55.7°N), need KP >= 3 for visibility
            kp_index = self._estimate_kp_from_probability(probability, lat)

            logger.info(
                f"NOAA data fetched: KP={kp_index:.1f}, "
                f"Probability={probability:.1f}% at ({lat}, {lon})"
            )

            return AuroraData(
                source=self.source_name,
                kp_index=kp_index,
                probability=round(probability, 1),
                last_updated=last_updated
            )

        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching NOAA data: {e}")
            raise Exception(f"Failed to fetch NOAA aurora data: {e}")
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Error parsing NOAA data: {e}")
            raise Exception(f"Failed to parse NOAA aurora data: {e}")

    def _estimate_kp_from_probability(self, probability: float, lat: float) -> float:
        """
        Estimate KP index from aurora probability and latitude.

        For high latitudes (>60°N), even low KP can show aurora.
        For mid-latitudes (55-60°N), need KP >= 3-4.

        Args:
            probability: Aurora probability percentage (0-100)
            lat: Latitude

        Returns:
            Estimated KP index (0-9)
        """
        # Base KP from probability
        # 0-10%: KP 0-2, 10-30%: KP 3-4, 30-60%: KP 5-6, 60-100%: KP 7-9
        if probability < 10:
            base_kp = probability / 10 * 2  # 0-2
        elif probability < 30:
            base_kp = 2 + (probability - 10) / 20 * 2  # 2-4
        elif probability < 60:
            base_kp = 4 + (probability - 30) / 30 * 2  # 4-6
        else:
            base_kp = 6 + (probability - 60) / 40 * 3  # 6-9

        # Adjust for latitude (southern Sweden needs higher KP)
        if lat < 60:
            # Mid-latitudes: add offset
            lat_adjustment = 0.5
        else:
            lat_adjustment = 0

        kp_index = min(9.0, base_kp + lat_adjustment)
        return round(kp_index, 1)
