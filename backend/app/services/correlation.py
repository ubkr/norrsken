"""Visibility scoring algorithm"""
from ..models.aurora import AuroraData
from ..models.weather import WeatherData
from ..models.prediction import VisibilityScore, VisibilityBreakdown


def calculate_visibility_score(aurora: AuroraData, weather: WeatherData) -> VisibilityScore:
    """
    Calculate aurora visibility score (0-100) based on aurora activity and weather conditions.

    Scoring breakdown:
    - Aurora activity (40%): KP index scaled (need KP >= 3 for southern Sweden)
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
    # KP index ranges 0-9; for southern Sweden, KP >= 3 is minimum for visibility
    kp = aurora.kp_index
    if kp < 3:
        # Very low aurora activity
        aurora_score = (kp / 3.0) * 10  # 0-10 points
    else:
        # Good aurora activity, scale 3-9 to 10-40 points
        aurora_score = 10 + ((kp - 3) / 6.0) * 30

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
    vis_km = weather.visibility_km
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

    # Total score
    total = aurora_score + cloud_score + vis_score + precip_score

    # Generate recommendation
    recommendation = get_recommendation(total, kp, cloud_pct)

    return VisibilityScore(
        total_score=round(total, 1),
        breakdown=VisibilityBreakdown(
            aurora=round(aurora_score, 1),
            clouds=round(cloud_score, 1),
            visibility=round(vis_score, 1),
            precipitation=round(precip_score, 1)
        ),
        recommendation=recommendation
    )


def get_recommendation(score: float, kp_index: float, cloud_cover: float) -> str:
    """
    Generate human-readable recommendation based on score and conditions.

    Args:
        score: Total visibility score (0-100)
        kp_index: KP index (0-9)
        cloud_cover: Cloud cover percentage (0-100)

    Returns:
        Recommendation string
    """
    if score >= 80:
        return "Excellent conditions! Great chance to see aurora. Get outside!"
    elif score >= 60:
        return "Good conditions. Worth checking outside if it's dark."
    elif score >= 40:
        if kp_index < 3:
            return "Fair conditions, but aurora activity is low."
        elif cloud_cover > 75:
            return "Fair conditions, but heavy cloud cover may block visibility."
        else:
            return "Fair conditions. Aurora may be visible."
    elif score >= 20:
        if kp_index < 3:
            return "Poor conditions. Aurora activity too low for this latitude."
        else:
            return "Poor conditions. Weather not favorable for aurora viewing."
    else:
        return "Very poor conditions. Aurora viewing not recommended."
