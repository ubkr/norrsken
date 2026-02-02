"""auroraforecast.space API client"""
import httpx
from datetime import datetime
from .base import AuroraSourceBase
from ...models.aurora import AuroraData
from ...utils.logger import setup_logger

logger = setup_logger(__name__)


class AuroraSpaceClient(AuroraSourceBase):
    """Client for auroraforecast.space API"""

    BASE_URL = "https://auroraforecast.space/api"

    @property
    def source_name(self) -> str:
        return "aurora_space"

    async def fetch_data(self, lat: float, lon: float) -> AuroraData:
        """
        Fetch current KP index from auroraforecast.space.

        This is a simple fallback source that provides KP index only.

        Args:
            lat: Latitude (not used by this API)
            lon: Longitude (not used by this API)

        Returns:
            AuroraData with KP index
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.BASE_URL}/kp/now")
                response.raise_for_status()
                data = response.json()

            # Extract KP index
            kp_index = float(data.get("kp", 0))

            # Use current time
            last_updated = datetime.utcnow()

            logger.info(f"Aurora Space data fetched: KP={kp_index:.1f}")

            return AuroraData(
                source=self.source_name,
                kp_index=round(kp_index, 1),
                probability=None,  # This API doesn't provide probability
                last_updated=last_updated
            )

        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching Aurora Space data: {e}")
            raise Exception(f"Failed to fetch Aurora Space data: {e}")
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Error parsing Aurora Space data: {e}")
            raise Exception(f"Failed to parse Aurora Space data: {e}")
