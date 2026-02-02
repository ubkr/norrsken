#!/usr/bin/env python3
"""
Test script to verify live API connections.
This is a standalone script to test real data sources.
"""
import asyncio
import sys
sys.path.insert(0, 'backend')

from backend.app.services.aurora.noaa_client import NOAAClient
from backend.app.services.aurora.auroras_live import AurorasLiveClient
from backend.app.services.weather.smhi_client import SMHIClient
from backend.app.services.weather.openmeteo_client import OpenMeteoClient
from backend.app.services.correlation import calculate_visibility_score


async def test_aurora_sources():
    """Test aurora data sources"""
    print("Testing Aurora Data Sources...")
    print("-" * 50)

    lat, lon = 55.7, 13.4

    # NOAA
    print("\n1. NOAA SWPC:")
    try:
        client = NOAAClient()
        data = await client.fetch_data(lat, lon)
        print(f"   ✓ KP Index: {data.kp_index}")
        print(f"   ✓ Probability: {data.probability}%")
        print(f"   ✓ Updated: {data.last_updated}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Auroras.live
    print("\n2. Auroras.live:")
    try:
        client = AurorasLiveClient()
        data = await client.fetch_data(lat, lon)
        print(f"   ✓ KP Index: {data.kp_index}")
        if data.probability:
            print(f"   ✓ Probability: {data.probability}%")
        print(f"   ✓ Updated: {data.last_updated}")
    except Exception as e:
        print(f"   ✗ Error: {e}")


async def test_weather_sources():
    """Test weather data sources"""
    print("\n\nTesting Weather Data Sources...")
    print("-" * 50)

    lat, lon = 55.7, 13.4

    # SMHI
    print("\n1. SMHI:")
    try:
        client = SMHIClient()
        data = await client.fetch_data(lat, lon)
        print(f"   ✓ Cloud Cover: {data.cloud_cover}%")
        print(f"   ✓ Visibility: {data.visibility_km} km")
        print(f"   ✓ Precipitation: {data.precipitation_mm} mm")
        print(f"   ✓ Temperature: {data.temperature_c}°C")
        print(f"   ✓ Updated: {data.last_updated}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Open-Meteo
    print("\n2. Open-Meteo:")
    try:
        client = OpenMeteoClient()
        data = await client.fetch_data(lat, lon)
        print(f"   ✓ Cloud Cover: {data.cloud_cover}%")
        print(f"   ✓ Visibility: {data.visibility_km} km")
        print(f"   ✓ Precipitation: {data.precipitation_mm} mm")
        print(f"   ✓ Temperature: {data.temperature_c}°C")
        print(f"   ✓ Updated: {data.last_updated}")
    except Exception as e:
        print(f"   ✗ Error: {e}")


async def test_visibility_calculation():
    """Test visibility score calculation"""
    print("\n\nTesting Visibility Calculation...")
    print("-" * 50)

    lat, lon = 55.7, 13.4

    try:
        # Fetch data - use working APIs
        aurora_client = NOAAClient()
        weather_client = OpenMeteoClient()  # Using Open-Meteo since SMHI is unavailable

        aurora_data = await aurora_client.fetch_data(lat, lon)
        weather_data = await weather_client.fetch_data(lat, lon)

        # Calculate score
        score = calculate_visibility_score(aurora_data, weather_data)

        print(f"\n✓ Total Score: {score.total_score}/100")
        print(f"  - Aurora: {score.breakdown.aurora}/40")
        print(f"  - Clouds: {score.breakdown.clouds}/30")
        print(f"  - Visibility: {score.breakdown.visibility}/20")
        print(f"  - Precipitation: {score.breakdown.precipitation}/10")
        print(f"\n✓ Recommendation: {score.recommendation}")

    except Exception as e:
        print(f"\n✗ Error: {e}")


async def main():
    """Run all tests"""
    print("=" * 50)
    print("LIVE API CONNECTION TEST")
    print("=" * 50)

    await test_aurora_sources()
    await test_weather_sources()
    await test_visibility_calculation()

    print("\n" + "=" * 50)
    print("TEST COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
