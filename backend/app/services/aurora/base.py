"""Base class for aurora data sources"""
from abc import ABC, abstractmethod
from ...models.aurora import AuroraData


class AuroraSourceBase(ABC):
    """Abstract base class for aurora data sources"""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Return the source name"""
        pass

    @abstractmethod
    async def fetch_data(self, lat: float, lon: float) -> AuroraData:
        """
        Fetch aurora data for a specific location.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            AuroraData object

        Raises:
            Exception: If data fetch fails
        """
        pass
