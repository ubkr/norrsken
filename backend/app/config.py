from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Location
    location_lat: float = 55.7
    location_lon: float = 13.4
    location_name: str = "My Location"

    # Cache TTL (seconds)
    cache_ttl_aurora: int = 300  # 5 minutes
    cache_ttl_weather: int = 1800  # 30 minutes

    # Logging
    log_level: str = "info"

    # API settings
    api_title: str = "Aurora Visibility Prediction API"
    api_version: str = "1.0.0"
    api_description: str = "Predicts aurora borealis visibility for any location"

    # Met.no API
    metno_user_agent: str = "AuroraVisibility/1.0 (contact@example.com)"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
