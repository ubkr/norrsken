"""Tests for visibility scoring algorithm"""
import pytest
from datetime import datetime, timezone
from unittest.mock import patch
from app.models.aurora import AuroraData
from app.models.weather import WeatherData
from app.services.correlation import calculate_visibility_score, get_recommendation


def _default_sun_darkness():
    return {"elevation_deg": -30.0, "twilight_phase": "darkness", "penalty_pts": 0.0}


@patch('app.services.correlation.calculate_sun_penalty')
@patch('app.services.correlation.calculate_moon_penalty')
def test_excellent_conditions(mock_moon, mock_sun):
    """Test excellent aurora viewing conditions"""
    mock_moon.return_value = {"illumination": 0.0, "elevation_deg": -30.0, "penalty_pts": 0.0}
    mock_sun.return_value = _default_sun_darkness()
    aurora = AuroraData(
        source="test",
        kp_index=6.0,
        probability=60.0,
        last_updated=datetime.utcnow()
    )
    weather = WeatherData(
        source="test",
        cloud_cover=10.0,  # Clear skies
        visibility_km=25.0,  # Excellent visibility
        precipitation_mm=0.0,  # No rain
        temperature_c=0.0,
        last_updated=datetime.utcnow()
    )

    score = calculate_visibility_score(aurora, weather)

    assert score.total_score >= 80
    assert score.breakdown.aurora > 20  # High aurora score
    assert score.breakdown.clouds == 30  # Full cloud score
    assert score.breakdown.visibility == 20  # Full visibility score
    assert score.breakdown.precipitation == 10  # Full precip score
    assert "excellent" in score.recommendation.lower()


@patch('app.services.correlation.calculate_sun_penalty')
@patch('app.services.correlation.calculate_moon_penalty')
def test_poor_conditions_low_kp(mock_moon, mock_sun):
    """Test poor conditions due to low KP index"""
    mock_moon.return_value = {"illumination": 0.0, "elevation_deg": -30.0, "penalty_pts": 0.0}
    mock_sun.return_value = _default_sun_darkness()
    aurora = AuroraData(
        source="test",
        kp_index=1.0,  # Very low
        probability=5.0,
        last_updated=datetime.utcnow()
    )
    weather = WeatherData(
        source="test",
        cloud_cover=20.0,
        visibility_km=20.0,
        precipitation_mm=0.0,
        temperature_c=5.0,
        last_updated=datetime.utcnow()
    )

    score = calculate_visibility_score(aurora, weather)

    assert score.total_score < 60
    assert score.breakdown.aurora < 15  # Low aurora score
    assert "low" in score.recommendation.lower()


@patch('app.services.correlation.calculate_sun_penalty')
@patch('app.services.correlation.calculate_moon_penalty')
def test_poor_conditions_heavy_clouds(mock_moon, mock_sun):
    """Test poor conditions due to heavy cloud cover"""
    mock_moon.return_value = {"illumination": 0.0, "elevation_deg": -30.0, "penalty_pts": 0.0}
    mock_sun.return_value = _default_sun_darkness()
    aurora = AuroraData(
        source="test",
        kp_index=5.0,
        probability=40.0,
        last_updated=datetime.utcnow()
    )
    weather = WeatherData(
        source="test",
        cloud_cover=90.0,  # Heavy clouds
        visibility_km=20.0,
        precipitation_mm=0.0,
        temperature_c=5.0,
        last_updated=datetime.utcnow()
    )

    score = calculate_visibility_score(aurora, weather)

    assert score.breakdown.clouds == 0  # No cloud score
    assert "cloud" in score.recommendation.lower() or score.total_score < 60


@patch('app.services.correlation.calculate_sun_penalty')
@patch('app.services.correlation.calculate_moon_penalty')
def test_fair_conditions(mock_moon, mock_sun):
    """Test fair viewing conditions"""
    mock_moon.return_value = {"illumination": 0.0, "elevation_deg": -30.0, "penalty_pts": 0.0}
    mock_sun.return_value = _default_sun_darkness()
    aurora = AuroraData(
        source="test",
        kp_index=4.0,
        probability=30.0,
        last_updated=datetime.utcnow()
    )
    weather = WeatherData(
        source="test",
        cloud_cover=40.0,  # Moderate clouds
        visibility_km=15.0,
        precipitation_mm=0.5,  # Light rain
        temperature_c=3.0,
        last_updated=datetime.utcnow()
    )

    score = calculate_visibility_score(aurora, weather)

    assert 40 <= score.total_score < 80
    assert score.breakdown.precipitation < 10  # Reduced precip score


@patch('app.services.correlation.calculate_sun_penalty')
@patch('app.services.correlation.calculate_moon_penalty')
def test_visibility_score_uses_neutral_fallback_when_visibility_missing(mock_moon, mock_sun):
    """When visibility is missing, correlation should use neutral 15 km fallback (15 points)."""
    mock_moon.return_value = {"illumination": 0.0, "elevation_deg": -30.0, "penalty_pts": 0.0}
    mock_sun.return_value = _default_sun_darkness()
    aurora = AuroraData(
        source="test",
        kp_index=5.0,
        probability=40.0,
        last_updated=datetime.utcnow()
    )
    weather = WeatherData(
        source="test",
        cloud_cover=20.0,
        visibility_km=None,
        precipitation_mm=0.0,
        temperature_c=2.0,
        last_updated=datetime.utcnow()
    )

    score = calculate_visibility_score(aurora, weather)

    assert score.breakdown.visibility == 15


@patch('app.services.correlation.calculate_sun_penalty')
@patch('app.services.correlation.calculate_moon_penalty')
def test_score_boundaries(mock_moon, mock_sun):
    """Test that scores stay within bounds"""
    mock_moon.return_value = {"illumination": 0.0, "elevation_deg": -30.0, "penalty_pts": 0.0}
    mock_sun.return_value = _default_sun_darkness()
    aurora = AuroraData(
        source="test",
        kp_index=9.0,  # Maximum
        probability=100.0,
        last_updated=datetime.utcnow()
    )
    weather = WeatherData(
        source="test",
        cloud_cover=0.0,  # Perfect
        visibility_km=50.0,
        precipitation_mm=0.0,
        temperature_c=0.0,
        last_updated=datetime.utcnow()
    )

    score = calculate_visibility_score(aurora, weather)

    assert 0 <= score.total_score <= 100
    assert 0 <= score.breakdown.aurora <= 40
    assert 0 <= score.breakdown.clouds <= 30
    assert 0 <= score.breakdown.visibility <= 20
    assert 0 <= score.breakdown.precipitation <= 10


@patch('app.services.correlation.calculate_sun_penalty')
@patch('app.services.correlation.calculate_moon_penalty')
def test_recommendation_ranges(mock_moon, mock_sun):
    """Test recommendation generation for different score ranges"""
    mock_moon.return_value = {"illumination": 0.0, "elevation_deg": -30.0, "penalty_pts": 0.0}
    mock_sun.return_value = _default_sun_darkness()
    # Excellent (KP >= 3 required)
    rec = get_recommendation(85, 5.0, 10.0, lat=55.7)
    assert "excellent" in rec.lower()
    assert "kp" in rec.lower()

    # Good with clear skies
    rec = get_recommendation(65, 4.0, 30.0, lat=55.7)
    assert "good" in rec.lower()
    assert "kp" in rec.lower()

    # Good with moderate clouds
    rec = get_recommendation(65, 4.0, 60.0, lat=55.7)
    assert "cloud" in rec.lower()
    assert "kp" in rec.lower()

    # Fair (KP >= 3, marginal weather)
    rec = get_recommendation(45, 3.5, 50.0, lat=55.7)
    assert "fair" in rec.lower() or "marginal" in rec.lower()
    assert "kp" in rec.lower()

    # Fair with heavy clouds
    rec = get_recommendation(45, 3.5, 80.0, lat=55.7)
    assert "cloud" in rec.lower()
    assert "kp" in rec.lower()

    # Poor with active aurora
    rec = get_recommendation(25, 3.5, 70.0, lat=55.7)
    assert "poor" in rec.lower()
    assert "kp" in rec.lower()

    # KP < 3 cases - no outdoor suggestions regardless of score
    rec = get_recommendation(65, 2.0, 10.0, lat=55.7)
    assert "too low" in rec.lower()
    assert "get outside" not in rec.lower()

    rec = get_recommendation(45, 2.5, 30.0, lat=55.7)
    assert "too low" in rec.lower()

    rec = get_recommendation(15, 1.0, 80.0, lat=55.7)
    assert "too low" in rec.lower()


@patch('app.services.correlation.calculate_sun_penalty')
@patch('app.services.correlation.calculate_moon_penalty')
def test_no_outdoor_suggestion_without_aurora(mock_moon, mock_sun):
    """Perfect weather + KP 2.5 should NOT suggest going outside"""
    mock_moon.return_value = {"illumination": 0.0, "elevation_deg": -30.0, "penalty_pts": 0.0}
    mock_sun.return_value = _default_sun_darkness()
    aurora = AuroraData(
        source="test",
        kp_index=2.5,
        probability=10.0,
        last_updated=datetime.utcnow()
    )
    weather = WeatherData(
        source="test",
        cloud_cover=0.0,
        visibility_km=50.0,
        precipitation_mm=0.0,
        temperature_c=0.0,
        last_updated=datetime.utcnow()
    )

    score = calculate_visibility_score(aurora, weather)

    assert "too low" in score.recommendation.lower()
    assert "get outside" not in score.recommendation.lower()
    assert "worth checking" not in score.recommendation.lower()


@patch('app.services.correlation.calculate_sun_penalty')
@patch('app.services.correlation.calculate_moon_penalty')
def test_kp_3_is_minimum_threshold(mock_moon, mock_sun):
    """KP just above the dynamic threshold should be treated as sufficient aurora activity"""
    mock_moon.return_value = {"illumination": 0.0, "elevation_deg": -30.0, "penalty_pts": 0.0}
    mock_sun.return_value = _default_sun_darkness()
    aurora = AuroraData(
        source="test",
        kp_index=3.2,
        probability=20.0,
        last_updated=datetime.utcnow()
    )
    weather = WeatherData(
        source="test",
        cloud_cover=20.0,
        visibility_km=20.0,
        precipitation_mm=0.0,
        temperature_c=2.0,
        last_updated=datetime.utcnow()
    )

    score = calculate_visibility_score(aurora, weather)

    assert "too low" not in score.recommendation.lower()
    assert "active" in score.recommendation.lower() or "possible" in score.recommendation.lower()


@patch('app.services.correlation.calculate_sun_penalty')
@patch('app.services.correlation.calculate_moon_penalty')
def test_moon_penalty_reduces_score(mock_moon, mock_sun):
    """Moon penalty should reduce total score by penalty_pts."""
    mock_moon.return_value = {"illumination": 1.0, "elevation_deg": 45.0, "penalty_pts": 10.6}
    mock_sun.return_value = _default_sun_darkness()
    aurora = AuroraData(source="test", kp_index=5.0, last_updated=datetime.now(timezone.utc))
    weather = WeatherData(
        source="test",
        cloud_cover=0.0,
        visibility_km=30.0,
        precipitation_mm=0.0,
        last_updated=datetime.now(timezone.utc),
    )
    score = calculate_visibility_score(aurora, weather)
    # With KP=5 aurora=20.0, cloud=30, vis=20, precip=10 → base=80.0, penalty=10.6 → total=69.4
    assert score.breakdown.moon.penalty_pts == 10.6
    assert score.total_score == pytest.approx(69.4, abs=0.5)
    assert score.total_score <= 80.0  # always less than base


@patch('app.services.correlation.calculate_sun_penalty')
@patch('app.services.correlation.calculate_moon_penalty')
def test_sun_penalty_daylight(mock_moon, mock_sun):
    mock_moon.return_value = {"illumination": 0.0, "elevation_deg": -30.0, "penalty_pts": 0.0}
    mock_sun.return_value = {"elevation_deg": 20.0, "twilight_phase": "daylight", "penalty_pts": 50.0}
    aurora = AuroraData(source="test", kp_index=5.0, last_updated=datetime.now(timezone.utc))
    weather = WeatherData(source="test", cloud_cover=0.0, visibility_km=30.0, precipitation_mm=0.0, last_updated=datetime.now(timezone.utc))

    score = calculate_visibility_score(aurora, weather)

    assert score.total_score == pytest.approx(30.0, abs=0.1)


@patch('app.services.correlation.calculate_sun_penalty')
@patch('app.services.correlation.calculate_moon_penalty')
def test_sun_penalty_civil_twilight(mock_moon, mock_sun):
    mock_moon.return_value = {"illumination": 0.0, "elevation_deg": -30.0, "penalty_pts": 0.0}
    mock_sun.return_value = {"elevation_deg": -2.0, "twilight_phase": "civil_twilight", "penalty_pts": 40.0}
    aurora = AuroraData(source="test", kp_index=5.0, last_updated=datetime.now(timezone.utc))
    weather = WeatherData(source="test", cloud_cover=0.0, visibility_km=30.0, precipitation_mm=0.0, last_updated=datetime.now(timezone.utc))

    score = calculate_visibility_score(aurora, weather)

    assert score.total_score == pytest.approx(40.0, abs=0.1)


@patch('app.services.correlation.calculate_sun_penalty')
@patch('app.services.correlation.calculate_moon_penalty')
def test_sun_penalty_nautical_twilight(mock_moon, mock_sun):
    mock_moon.return_value = {"illumination": 0.0, "elevation_deg": -30.0, "penalty_pts": 0.0}
    mock_sun.return_value = {"elevation_deg": -8.0, "twilight_phase": "nautical_twilight", "penalty_pts": 20.0}
    aurora = AuroraData(source="test", kp_index=5.0, last_updated=datetime.now(timezone.utc))
    weather = WeatherData(source="test", cloud_cover=0.0, visibility_km=30.0, precipitation_mm=0.0, last_updated=datetime.now(timezone.utc))

    score = calculate_visibility_score(aurora, weather)

    assert score.total_score == pytest.approx(60.0, abs=0.1)


@patch('app.services.correlation.calculate_sun_penalty')
@patch('app.services.correlation.calculate_moon_penalty')
def test_sun_penalty_astronomical_twilight(mock_moon, mock_sun):
    mock_moon.return_value = {"illumination": 0.0, "elevation_deg": -30.0, "penalty_pts": 0.0}
    mock_sun.return_value = {"elevation_deg": -15.0, "twilight_phase": "astronomical_twilight", "penalty_pts": 8.0}
    aurora = AuroraData(source="test", kp_index=5.0, last_updated=datetime.now(timezone.utc))
    weather = WeatherData(source="test", cloud_cover=0.0, visibility_km=30.0, precipitation_mm=0.0, last_updated=datetime.now(timezone.utc))

    score = calculate_visibility_score(aurora, weather)

    assert score.total_score == pytest.approx(72.0, abs=0.1)


@patch('app.services.correlation.calculate_sun_penalty')
@patch('app.services.correlation.calculate_moon_penalty')
def test_sun_penalty_darkness(mock_moon, mock_sun):
    mock_moon.return_value = {"illumination": 0.0, "elevation_deg": -30.0, "penalty_pts": 0.0}
    mock_sun.return_value = _default_sun_darkness()
    aurora = AuroraData(source="test", kp_index=5.0, last_updated=datetime.now(timezone.utc))
    weather = WeatherData(source="test", cloud_cover=0.0, visibility_km=30.0, precipitation_mm=0.0, last_updated=datetime.now(timezone.utc))

    score = calculate_visibility_score(aurora, weather)

    assert score.total_score == pytest.approx(80.0, abs=0.1)


@patch('app.services.correlation.calculate_sun_penalty')
@patch('app.services.correlation.calculate_moon_penalty')
def test_sun_penalty_score_floor(mock_moon, mock_sun):
    mock_moon.return_value = {"illumination": 0.0, "elevation_deg": -30.0, "penalty_pts": 0.0}
    mock_sun.return_value = {"elevation_deg": 35.0, "twilight_phase": "daylight", "penalty_pts": 50.0}
    aurora = AuroraData(source="test", kp_index=0.0, last_updated=datetime.now(timezone.utc))
    weather = WeatherData(source="test", cloud_cover=100.0, visibility_km=1.0, precipitation_mm=3.0, last_updated=datetime.now(timezone.utc))

    score = calculate_visibility_score(aurora, weather)

    assert score.total_score == 0.0


@patch('app.services.correlation.calculate_sun_penalty')
@patch('app.services.correlation.calculate_moon_penalty')
def test_sun_data_in_breakdown(mock_moon, mock_sun):
    mock_moon.return_value = {"illumination": 0.0, "elevation_deg": -30.0, "penalty_pts": 0.0}
    mock_sun.return_value = {"elevation_deg": -8.0, "twilight_phase": "nautical_twilight", "penalty_pts": 20.0}
    aurora = AuroraData(source="test", kp_index=5.0, last_updated=datetime.now(timezone.utc))
    weather = WeatherData(source="test", cloud_cover=0.0, visibility_km=30.0, precipitation_mm=0.0, last_updated=datetime.now(timezone.utc))

    score = calculate_visibility_score(aurora, weather)

    assert score.breakdown.sun.elevation_deg == -8.0
    assert score.breakdown.sun.twilight_phase == "nautical_twilight"
    assert score.breakdown.sun.penalty_pts == 20.0


@patch('app.services.correlation.calculate_sun_penalty')
@patch('app.services.correlation.calculate_moon_penalty')
def test_daylight_recommendation(mock_moon, mock_sun):
    mock_moon.return_value = {"illumination": 0.0, "elevation_deg": -30.0, "penalty_pts": 0.0}
    mock_sun.return_value = {"elevation_deg": 20.0, "twilight_phase": "daylight", "penalty_pts": 50.0}
    aurora = AuroraData(source="test", kp_index=7.0, last_updated=datetime.now(timezone.utc))
    weather = WeatherData(source="test", cloud_cover=0.0, visibility_km=30.0, precipitation_mm=0.0, last_updated=datetime.now(timezone.utc))

    score = calculate_visibility_score(aurora, weather)

    assert score.recommendation == "It is currently daylight. Aurora borealis is not visible during the day."


@patch('app.services.correlation.calculate_sun_penalty')
@patch('app.services.correlation.calculate_moon_penalty')
def test_civil_twilight_recommendation(mock_moon, mock_sun):
    mock_moon.return_value = {"illumination": 0.0, "elevation_deg": -30.0, "penalty_pts": 0.0}
    mock_sun.return_value = {"elevation_deg": -3.0, "twilight_phase": "civil_twilight", "penalty_pts": 40.0}
    aurora = AuroraData(source="test", kp_index=7.0, last_updated=datetime.now(timezone.utc))
    weather = WeatherData(source="test", cloud_cover=0.0, visibility_km=30.0, precipitation_mm=0.0, last_updated=datetime.now(timezone.utc))

    score = calculate_visibility_score(aurora, weather)

    assert score.recommendation == "Civil twilight — the sky is too bright for aurora viewing. Wait until full darkness."
