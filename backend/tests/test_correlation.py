"""Tests for visibility scoring algorithm"""
import pytest
from datetime import datetime
from app.models.aurora import AuroraData
from app.models.weather import WeatherData
from app.services.correlation import calculate_visibility_score, get_recommendation


def test_excellent_conditions():
    """Test excellent aurora viewing conditions"""
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


def test_poor_conditions_low_kp():
    """Test poor conditions due to low KP index"""
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


def test_poor_conditions_heavy_clouds():
    """Test poor conditions due to heavy cloud cover"""
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


def test_fair_conditions():
    """Test fair viewing conditions"""
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


def test_score_boundaries():
    """Test that scores stay within bounds"""
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


def test_recommendation_ranges():
    """Test recommendation generation for different score ranges"""
    # Excellent
    rec = get_recommendation(85, 5.0, 10.0)
    assert "excellent" in rec.lower()

    # Good
    rec = get_recommendation(65, 4.0, 30.0)
    assert "good" in rec.lower()

    # Fair
    rec = get_recommendation(45, 3.5, 50.0)
    assert "fair" in rec.lower()

    # Poor
    rec = get_recommendation(25, 2.0, 60.0)
    assert "poor" in rec.lower()

    # Very poor
    rec = get_recommendation(15, 1.0, 80.0)
    assert "very poor" in rec.lower() or "poor" in rec.lower()
