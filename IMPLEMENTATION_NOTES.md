# Implementation Notes

## Implementation Status

This project is implemented as a Python FastAPI backend with a vanilla JavaScript/HTML/CSS frontend.

### Completed Features

1. **Backend (FastAPI)**
    - REST API endpoints:
       - `/api/v1/prediction/current` (supports optional `lat` and `lon` query parameters)
       - `/api/v1/prediction/forecast` (supports optional `lat` and `lon` query parameters)
       - `/api/v1/aurora/sources` (supports optional `lat` and `lon` query parameters)
       - `/api/v1/weather/sources` (supports optional `lat` and `lon` query parameters)
       - `/api/v1/health`
      - For `/api/v1/aurora/sources` and `/api/v1/weather/sources`, latitude and longitude must be provided as a pair (supplying only one returns HTTP 422). Prediction endpoints (`/api/v1/prediction/current`, `/api/v1/prediction/forecast`) accept `lat` and `lon` independently, and each omitted value defaults to the configured location.
    - Multi-source aggregation with fallback logic
    - In-memory caching:
       - Aurora TTL: 5 minutes
       - Weather TTL: 30 minutes
    - Correlation and visibility scoring pipeline
    - Moon Phase Penalty:
       - Moon phase penalty incorporated into visibility score using the `ephem` library
       - Formula: `Moon_Factor = Illumination × max(0, sin(Moon_Elevation))` — deducts 0–15 pts
       - Location-aware: moon elevation computed for the user's selected coordinates
       - When moon is below horizon, penalty is 0 regardless of illumination
    - NOAA grid interpolation using bilinear interpolation

2. **Frontend (Vanilla JS/HTML/CSS)**
      - Dark-themed responsive UI
      - Visibility score card and source data cards
      - Visibility score breakdown includes both moon penalty and sun/daylight penalty, including twilight phase and sun elevation
      - 24-hour forecast chart (Chart.js)
      - Auto-refresh every 5 minutes
      - Location picker flow:
       - `settings-modal.js`
       - `map-selector.js` (Leaflet)
       - `location-manager.js` (reverse geocoding, warning when outside Sweden, and persistence in browser `localStorage` under `aurora_location`)
    - `location-manager.js` localStorage handling includes:
       - availability detection before use
       - try/catch protection for read/write/remove operations
       - strict ISO-8601 timestamp validation for stored entries
       - automatic discard of entries older than 30 days
    - `api.js` sends the selected user coordinates to all backend data calls (`prediction/current`, `prediction/forecast`, `aurora/sources`, `weather/sources`)
    - Reusable tooltips component (`tooltip.js`)
    - Modular CSS structure:
       - `css/tokens.css`
       - `css/base.css`
       - `css/layout.css`
       - `css/main.css`
       - `css/components/score.css`
       - `css/components/data-cards.css`
       - `css/components/chart.css`
       - `css/components/modal.css`

3. **Testing**
    - Unit tests:
       - `backend/tests/test_correlation.py` (11 tests)
       - `backend/tests/test_geo.py`
       - `backend/tests/test_metno_client.py`
    - Live API test script:
       - `test_live_apis.py`

## Data Source Status

### Aurora Sources (in fallback order)
1. NOAA SWPC (primary)
2. Auroras.live (secondary)

### Weather Sources (in fallback order)
1. Met.no (primary)
2. SMHI (secondary)
3. Open-Meteo (tertiary)

### Current Operational Status
- NOAA SWPC: working
- Met.no: working
- Auroras.live: returning HTTP 500 errors
- SMHI: returning HTML instead of expected JSON

## Quick Start

### 1. Install Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start Backend

```bash
./start-backend.sh
```

Or manually:

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend URLs:
- http://localhost:8000
- http://localhost:8000/docs

### 3. Start Frontend

```bash
./start-frontend.sh
```

Or manually:

```bash
cd frontend
python3 -m http.server 3000
```

Frontend URL:
- http://localhost:3000

## Testing

### Run Unit Tests

```bash
cd backend
source venv/bin/activate
PYTHONPATH=/Users/bjarne/project/norrsken/backend pytest tests/ -v
```

### Run Live API Test Script

```bash
source backend/venv/bin/activate
python3 test_live_apis.py
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Current prediction
curl "http://localhost:8000/api/v1/prediction/current" | python3 -m json.tool

# Current prediction for custom location
curl "http://localhost:8000/api/v1/prediction/current?lat=55.7&lon=13.4" | python3 -m json.tool

# Forecast
curl "http://localhost:8000/api/v1/prediction/forecast?hours=24" | python3 -m json.tool

# Forecast for custom location
curl "http://localhost:8000/api/v1/prediction/forecast?hours=24&lat=55.7&lon=13.4" | python3 -m json.tool

# Aurora source status
curl http://localhost:8000/api/v1/aurora/sources | python3 -m json.tool

# Aurora source status for custom location
curl "http://localhost:8000/api/v1/aurora/sources?lat=55.7&lon=13.4" | python3 -m json.tool

# Weather source status
curl http://localhost:8000/api/v1/weather/sources | python3 -m json.tool

# Weather source status for custom location
curl "http://localhost:8000/api/v1/weather/sources?lat=55.7&lon=13.4" | python3 -m json.tool
```

## Project Structure (simplified)

```text
norrsken/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   │   ├── aurora.py
│   │   │   ├── weather.py
│   │   │   └── prediction.py
│   │   ├── services/
│   │   │   ├── aurora/
│   │   │   │   ├── base.py
│   │   │   │   ├── noaa_client.py
│   │   │   │   ├── auroras_live.py
│   │   │   │   └── aurora_space.py
│   │   │   ├── weather/
│   │   │   │   ├── base.py
│   │   │   │   ├── metno_client.py
│   │   │   │   ├── smhi_client.py
│   │   │   │   └── openmeteo_client.py
│   │   │   ├── correlation.py
│   │   │   ├── cache_service.py
│   │   │   └── aggregator.py
│   │   ├── api/routes/
│   │   │   ├── health.py
│   │   │   ├── prediction.py
│   │   │   ├── aurora.py
│   │   │   └── weather.py
│   │   └── utils/
│   │       ├── geo.py
│   │       ├── logger.py
│   │       ├── moon.py
│   │       └── sun.py
│   ├── tests/
│   │   ├── test_aggregator_visibility.py
│   │   ├── test_correlation.py
│   │   ├── test_geo.py
│   │   └── test_metno_client.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── css/
│   │   ├── main.css
│   │   ├── tokens.css
│   │   ├── base.css
│   │   ├── layout.css
│   │   └── components/
│   │       ├── score.css
│   │       ├── data-cards.css
│   │       ├── chart.css
│   │       └── modal.css
│   └── js/
│       ├── main.js
│       ├── api.js
│       ├── location-manager.js
│       └── components/
│           ├── visibility-score.js
│           ├── aurora-display.js
│           ├── weather-display.js
│           ├── forecast-chart.js
│           ├── settings-modal.js
│           ├── map-selector.js
│           └── tooltip.js
├── start-backend.sh
├── start-frontend.sh
├── test_live_apis.py
├── README.md
├── CLAUDE.md
└── .env
```

## Scoring Algorithm

The visibility score is a sum of positive components minus moon and sun/daylight penalties, capped 0–100.

### Positive Components (max 100 pts)

| Component     | Max pts | Factor |
|---------------|---------|--------|
| Aurora        | 40      | KP index (piecewise: KP<3 → 0–10 pts; KP 3–9 → 10–40 pts) |
| Cloud cover   | 30      | <25% cloud → 30 pts; 25–50% → 20 pts; 50–75% → 10 pts; ≥75% → 0 pts |
| Visibility    | 20      | >20 km → 20 pts; >10 km → 15 pts; >5 km → 10 pts; else → 5 pts |
| Precipitation | 10      | None → 10 pts; <1 mm/h → 5 pts; ≥1 mm/h → 0 pts |

### Moon Phase Penalty (max 15 pts deduction)

Based on Krisciunas & Schaefer (1991) sky-brightness model and common aurora-forecasting practice.

```text
Moon_Factor  = Illumination_Fraction × max(0, sin(Moon_Elevation_radians))
moon_penalty = min(15, round(Moon_Factor × 15, 1))
Final_Score  = max(0, Component_Sum − moon_penalty − sun_penalty)
```

- **Illumination fraction**: 0 (new moon) → 1 (full moon), computed by `ephem` (Meeus algorithm)
- **Moon elevation**: real-time altitude for the user's location; negative elevation → 0 penalty
- **Maximum penalty**: 15 pts, occurs only when full moon is directly overhead
- **Rationale**: a strong aurora (KP ≥ 7) yields 40 aurora pts; a 15-pt moonlight penalty still leaves a high total, reflecting that very active aurora remains visible under a full moon

### Sun / Daylight Penalty

Aurora is only visible in darkness, so the sun's position strongly affects practical visibility.
The sun/daylight penalty uses the `ephem` library to compute sun elevation for the user's selected coordinates at the current UTC time.

| Condition | Penalty | `twilight_phase` |
|-----------|---------|------------------|
| Full daylight (sun ≥ 0°) | 50 pts | `daylight` |
| Civil twilight (-6° to 0°) | 40 pts | `civil_twilight` |
| Nautical twilight (-12° to -6°) | 20 pts | `nautical_twilight` |
| Astronomical twilight (-18° to -12°) | 8 pts | `astronomical_twilight` |
| Full darkness (sun < -18°) | 0 pts | `darkness` |

```text
Final_Score = max(0, Component_Sum − moon_penalty − sun_penalty)
```

- **Midnight sun note**: at high latitudes in summer, the sun can remain above the horizon all day, resulting in a constant daylight penalty
- **Time consistency**: a shared UTC timestamp is used for both moon and sun calculations to keep penalties internally consistent

Final score uses a 0–100 scale: positive components sum to at most 100, then moon and sun/daylight penalties are subtracted, and the result is clamped to 0 at the lower bound.

## Known Issues

- SMHI client currently receives HTML instead of expected JSON responses.
- Auroras.live currently returns HTTP 500 responses.

## Key Implementation Details

### Visibility Scoring

The visibility score is calculated on a 0-100 scale using weighted components:
- 40% aurora activity (KP/aurora strength)
- 30% cloud cover
- 20% visibility distance
- 10% precipitation

Component weights are fixed (aurora 40, clouds 30, visibility 20, precipitation 10); latitude affects the aurora KP threshold and scaling within the aurora component, not the weights themselves.

### NOAA Grid Interpolation

NOAA SWPC aurora grid data is interpolated with bilinear interpolation to estimate values at exact coordinates.

### Aggregation and Caching

- Aurora and weather data are fetched through source-priority fallback chains.
- Cached values are reused according to configured TTLs (aurora: 300s, weather: 1800s).

### Multi-user and Stateless Design

The backend holds no per-user session state for location preferences.
Each browser stores its chosen location in localStorage (`aurora_location`) and includes coordinates in API requests.
Multiple simultaneous users with different selected locations are supported because the server processes each request with that request's coordinates.
The environment-configured location (`LOCATION_LAT`, `LOCATION_LON`, `LOCATION_NAME`) is used as a default fallback when coordinates are not provided.

### Forecast Endpoint Limitation

`/api/v1/prediction/forecast` generates synthetic hourly data derived from the current snapshot with hour-based variation.
It does not fetch true hourly forecast data from external API sources.

## Configuration

Current `.env` values:

```bash
LOCATION_LAT=55.7
LOCATION_LON=13.4
LOCATION_NAME=Your City
CACHE_TTL_AURORA=300
CACHE_TTL_WEATHER=1800
LOG_LEVEL=info
```

## Planned Features

- Push notifications when visibility score > 80
- Historical data tracking and trends
- Progressive Web App (PWA) for mobile
- User-submitted aurora sighting reports
- Local webcam integration
- Email/SMS alerts
- Dark sky map overlay
- Social sharing features
- True hourly forecast data from API sources (replace synthetic forecast)
