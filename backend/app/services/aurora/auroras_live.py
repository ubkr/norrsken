"""Auroras.live API client"""
import httpx
from datetime import datetime
from .base import AuroraSourceBase
from ...models.aurora import AuroraData
from ...utils.logger import setup_logger

logger = setup_logger(__name__)


class AurorasLiveClient(AuroraSourceBase):
    """Client for Auroras.live API"""

    BASE_URL = "https://api.auroras.live/v1/"

    @property
    def source_name(self) -> str:
        return "auroras_live"

    async def fetch_data(self, lat: float, lon: float) -> AuroraData:
        """
        Fetch aurora data from Auroras.live.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            AuroraData with KP index and probability
        """
        try:
            params = {
                "type": "all",
                "lat": lat,
                "long": lon
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()

            # Extract KP index
            # API returns real-time KP index
            kp_index = float(data.get("kp", 0))

            # Extract probability if available
            # Note: API structure may vary, adjust based on actual response
            probability = data.get("probability")
            if probability is not None:
                probability = float(probability)

            # Use current time as update time
            last_updated = datetime.utcnow()

            logger.info(
                f"Auroras.live data fetched: KP={kp_index:.1f}, "
                f"Probability={probability} at ({lat}, {lon})"
            )

            return AuroraData(
                source=self.source_name,
                kp_index=round(kp_index, 1),
                probability=round(probability, 1) if probability is not None else None,
                last_updated=last_updated
            )

        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching Auroras.live data: {e}")
            raise Exception(f"Failed to fetch Auroras.live data: {e}")
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Error parsing Auroras.live data: {e}")
            raise Exception(f"Failed to parse Auroras.live data: {e}")
