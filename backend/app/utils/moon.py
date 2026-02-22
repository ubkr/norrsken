import ephem
import math
from datetime import datetime, timezone


def calculate_moon_penalty(lat: float, lon: float, dt: datetime = None) -> dict:
    """
    Calculate moon phase penalty contribution to aurora visibility score.

    Uses the ephem library (Jean Meeus algorithm) to compute moon illumination
    and elevation at the given location and time.

    Formula:
        Moon_Factor = Illumination_Fraction * max(0, sin(Moon_Elevation_radians))
        penalty_pts  = min(15, round(Moon_Factor * 15, 1))

    A full moon directly overhead contributes the maximum 15-point deduction.
    When the moon is below the horizon (elevation < 0) the penalty is 0.

    Returns a dict with:
        illumination  – fraction 0.0–1.0 (0 = new moon, 1 = full moon)
        elevation_deg – degrees above (+) or below (-) horizon
        penalty_pts   – points deducted from total score (0–15)
    """
    if dt is None:
        dt = datetime.now(timezone.utc).replace(tzinfo=None)
    else:
        # Ensure UTC naive — ephem does not accept tzinfo-aware datetimes
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)

    observer = ephem.Observer()
    # ephem requires strings for lat/lon; floats would be interpreted as radians
    observer.lat = str(lat)
    observer.lon = str(lon)
    observer.date = dt
    # Disable atmospheric refraction correction for consistency
    observer.pressure = 0

    moon = ephem.Moon()
    moon.compute(observer)

    # moon.phase is illuminated percentage 0.0–100.0
    illumination = moon.phase / 100.0

    # moon.alt is the altitude (elevation) in radians
    elevation_rad = float(moon.alt)
    elevation_deg = math.degrees(elevation_rad)

    moon_factor = illumination * max(0.0, math.sin(elevation_rad))
    penalty_pts = min(15.0, round(moon_factor * 15.0, 1))

    return {
        "illumination": round(illumination, 3),
        "elevation_deg": round(elevation_deg, 1),
        "penalty_pts": penalty_pts,
    }
