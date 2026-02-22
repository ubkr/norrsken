"""Visibility scoring algorithm"""
from datetime import datetime, timezone

from ..models.aurora import AuroraData
from ..models.weather import WeatherData
from ..models.prediction import VisibilityScore, VisibilityBreakdown, MoonData, SunData
from ..utils.moon import calculate_moon_penalty
from ..utils.sun import calculate_sun_penalty


def _min_kp_for_lat(lat: float) -> float:
    """Return the minimum KP index required for aurora visibility at the given latitude.
    Uses the approximation that the aurora oval's equatorward boundary is ~65°N at KP=0
    and moves ~3° south per KP unit."""
    return max(0.0, (65.0 - abs(lat)) / 3.0)


def calculate_visibility_score(
    aurora: AuroraData,
    weather: WeatherData,
    lat: float = 55.7,
    lon: float = 13.4,
) -> VisibilityScore:
    """
    Calculate aurora visibility score (0-100) based on aurora activity and weather conditions.

    Scoring breakdown:
    - Aurora activity (40%): KP index scaled for the given latitude
    - Cloud cover (30%): Less clouds = better visibility
    - Visibility (20%): Higher visibility = better
    - Precipitation (10%): No precipitation = better

    Args:
        aurora: Aurora forecast data
        weather: Weather forecast data

    Returns:
        VisibilityScore with total score, breakdown, and recommendation
    """
    # Aurora activity score (0-40 points)
    # Minimum KP for visibility depends on latitude
    min_kp = _min_kp_for_lat(lat)
    kp = aurora.kp_index
    if kp < min_kp:
        aurora_score = (kp / max(min_kp, 1.0)) * 10  # 0-10 points below threshold
    else:
        aurora_score = 10 + ((kp - min_kp) / max(9.0 - min_kp, 1.0)) * 30

    aurora_score = min(40, max(0, aurora_score))

    # Cloud cover score (0-30 points)
    # Lower cloud cover = higher score
    cloud_pct = weather.cloud_cover
    if cloud_pct < 25:  # < 2/8 oktas
        cloud_score = 30
    elif cloud_pct < 50:  # < 4/8 oktas
        cloud_score = 20
    elif cloud_pct < 75:  # < 6/8 oktas
        cloud_score = 10
    else:  # Heavy clouds
        cloud_score = 0

    # Visibility score (0-20 points)
    # Some sources (e.g. Met.no compact) do not provide measured visibility.
    # Fall back to a neutral middle-ground value of 15 km so missing data
    # lands in the true middle bucket (>10 km => 15 points).
    vis_km = weather.visibility_km if weather.visibility_km is not None else 15.0
    if vis_km > 20:
        vis_score = 20
    elif vis_km > 10:
        vis_score = 15
    elif vis_km > 5:
        vis_score = 10
    else:
        vis_score = 5

    # Precipitation score (0-10 points)
    precip = weather.precipitation_mm
    if precip == 0:
        precip_score = 10
    elif precip < 1:
        precip_score = 5
    else:
        precip_score = 0

    now_utc = datetime.now(timezone.utc)
    moon_data = calculate_moon_penalty(lat, lon, dt=now_utc)
    sun_data = calculate_sun_penalty(lat, lon, dt=now_utc)

    # Total score
    total_score = max(
        0.0,
        round(
            aurora_score
            + cloud_score
            + vis_score
            + precip_score
            - moon_data["penalty_pts"]
            - sun_data["penalty_pts"],
            1,
        ),
    )

    # Generate recommendation
    recommendation = get_recommendation(total_score, kp, cloud_pct, lat)
    if sun_data["twilight_phase"] == "daylight":
        recommendation = "It is currently daylight. Aurora borealis is not visible during the day."
    elif sun_data["twilight_phase"] == "civil_twilight":
        recommendation = "Civil twilight — the sky is too bright for aurora viewing. Wait until full darkness."

    return VisibilityScore(
        total_score=total_score,
        breakdown=VisibilityBreakdown(
            aurora=round(aurora_score, 1),
            clouds=round(cloud_score, 1),
            visibility=round(vis_score, 1),
            precipitation=round(precip_score, 1),
            moon=MoonData(
                illumination=moon_data["illumination"],
                elevation_deg=moon_data["elevation_deg"],
                penalty_pts=moon_data["penalty_pts"],
            ),
            sun=SunData(
                elevation_deg=sun_data["elevation_deg"],
                twilight_phase=sun_data["twilight_phase"],
                penalty_pts=sun_data["penalty_pts"],
            ),
        ),
        recommendation=recommendation
    )


def get_recommendation(score: float, kp_index: float, cloud_cover: float, lat: float = 55.7) -> str:
    """
    Generate human-readable recommendation based on score and conditions.

    Minimum required KP depends on latitude.
    No outdoor suggestion is made if KP is below the latitude threshold, regardless of weather.

    Args:
        score: Total visibility score (0-100)
        kp_index: KP index (0-9)
        cloud_cover: Cloud cover percentage (0-100)
        lat: Latitude used to compute minimum required KP threshold

    Returns:
        Recommendation string
    """
    min_kp = _min_kp_for_lat(lat)

    if kp_index < min_kp:
        if score >= 60:
            return f"Weather conditions are excellent, but aurora activity is too low for your current location (KP < {min_kp:.1f}). Not worth going outside yet - wait for stronger activity."
        elif score >= 40:
            return f"Aurora activity too low for your current location (KP < {min_kp:.1f}). Aurora viewing not possible regardless of weather."
        else:
            return f"Aurora activity too low (KP < {min_kp:.1f}) and weather conditions unfavorable. Aurora viewing not possible."

    if score >= 80:
        return f"Excellent conditions! Aurora is active (KP ≥ {min_kp:.1f}) and weather is clear. Great chance to see aurora - get outside!"
    elif score >= 60:
        if cloud_cover > 50:
            return f"Good aurora activity (KP ≥ {min_kp:.1f}), but moderate cloud cover may reduce visibility. Worth checking outside if clouds break."
        else:
            return f"Good conditions! Aurora is active (KP ≥ {min_kp:.1f}) and weather is favorable. Worth checking outside."
    elif score >= 40:
        if cloud_cover > 75:
            return f"Aurora is active (KP ≥ {min_kp:.1f}), but heavy cloud cover will likely block visibility. Not recommended unless skies clear."
        else:
            return f"Fair conditions. Aurora is active (KP ≥ {min_kp:.1f}) but conditions are marginal. May be visible in dark areas."
    elif score >= 20:
        return f"Aurora is active (KP ≥ {min_kp:.1f}), but weather conditions are poor. Aurora viewing not recommended."
    else:
        return "Very poor conditions. Aurora viewing not recommended."
