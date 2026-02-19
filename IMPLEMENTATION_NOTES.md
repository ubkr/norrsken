# Implementation Notes

## Implementation Status

This project is implemented as a Python FastAPI backend with a vanilla JavaScript/HTML/CSS frontend.

### Completed Features

1. **Backend (FastAPI)**
    - REST API endpoints:
       - `/api/v1/prediction/current` (supports optional `lat` and `lon` query parameters)
       - `/api/v1/prediction/forecast`
       - `/api/v1/aurora/sources`
       - `/api/v1/weather/sources`
       - `/api/v1/health`
    - Multi-source aggregation with fallback logic
    - In-memory caching:
       - Aurora TTL: 5 minutes
       - Weather TTL: 30 minutes
    - Correlation and visibility scoring pipeline
    - NOAA grid interpolation using bilinear interpolation

2. **Frontend (Vanilla JS/HTML/CSS)**
    - Dark-themed responsive UI
    - Visibility score card and source data cards
    - 24-hour forecast chart (Chart.js)
    - Auto-refresh every 5 minutes
    - Location picker flow:
       - `settings-modal.js`
       - `map-selector.js` (Leaflet)
       - `location-manager.js` (including reverse geocoding and warning when outside Sweden)
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
3. Aurora Space (tertiary)

### Weather Sources (in fallback order)
1. Met.no (primary)
2. SMHI (secondary)
3. Open-Meteo (tertiary)

### Current Operational Status
- NOAA SWPC: working
- Met.no: working
- Auroras.live: returning HTTP 500 errors
- SMHI: returning HTML instead of expected JSON
- Aurora Space: present as tertiary fallback, not verified

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

# Aurora source status
curl http://localhost:8000/api/v1/aurora/sources | python3 -m json.tool

# Weather source status
curl http://localhost:8000/api/v1/weather/sources | python3 -m json.tool
```

## Project Structure

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
│   │       └── logger.py
│   ├── tests/
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

The weighting is calibrated for latitude 55.7°N (Södra Sandby area).

### NOAA Grid Interpolation

NOAA SWPC aurora grid data is interpolated with bilinear interpolation to estimate values at exact coordinates.

### Aggregation and Caching

- Aurora and weather data are fetched through source-priority fallback chains.
- Cached values are reused according to configured TTLs (aurora: 300s, weather: 1800s).

### Forecast Endpoint Limitation

`/api/v1/prediction/forecast` currently generates synthetic hourly data derived from the current snapshot with hour-based variation.
It does not fetch true hourly forecast data from external API sources.

## Configuration

Current `.env` values:

```bash
LOCATION_LAT=55.7
LOCATION_LON=13.4
LOCATION_NAME=Södra Sandby
CACHE_TTL_AURORA=300
CACHE_TTL_WEATHER=1800
LOG_LEVEL=info
```

## Planned Features

- Push notifications when visibility score > 80
- Historical data tracking and trends
- Progressive Web App (PWA) for mobile
- User-submitted aurora sighting reports
- Moon phase consideration in scoring
- Local webcam integration
- Email/SMS alerts
- Dark sky map overlay
- Social sharing features
- True hourly forecast data from API sources (replace synthetic forecast)
