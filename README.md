# Aurora Visibility Prediction - Södra Sandby

Real-time aurora borealis visibility predictions for Södra Sandby, Sweden (55.7°N, 13.4°E), combining aurora forecasts with local weather conditions.

## Features

- **Real-time visibility scoring (0-100)** based on:
  - Aurora activity (KP index from multiple sources)
  - Cloud cover
  - Visibility distance
  - Precipitation
  - Moon phase/elevation and sun/daylight penalties

- **Multiple data sources** for reliability:
  - Aurora: NOAA SWPC, Auroras.live
  - Weather: Met.no, SMHI, Open-Meteo

- **24-hour forecast** with hourly predictions

- **Auto-refresh** every 5 minutes

- **Location picker** with interactive map modal

## Architecture

**Backend**: Python FastAPI
- Fetches aurora and weather data from multiple APIs
- Calculates visibility scores with weighted algorithm
- Provides REST endpoints for frontend
- In-memory caching to reduce API calls

**Frontend**: HTML/CSS/JavaScript
- Displays current visibility score with breakdown
- Shows data from all sources for comparison
- 24-hour forecast chart using Chart.js
- Responsive design for mobile

## Installation

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file (optional, uses defaults)
cp ../.env.example .env
```

### Frontend

No build step required. Uses vanilla JavaScript with ES modules.

## Running Locally

### Start Backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at:
- **API**: `http://localhost:8000`
- **Docs**: `http://localhost:8000/docs`

### Start Frontend

```bash
cd frontend
python3 -m http.server 3000
```

Visit `http://localhost:3000` in your browser.

## API Endpoints

### `GET /api/v1/prediction/current`
Current prediction with visibility score and all data sources.
Optional query params: `lat`, `lon` (each optional; omitted values use configured default location; supply both to target a custom location).

### `GET /api/v1/prediction/forecast?hours=24`
Hourly predictions for next N hours.
Optional query params: `lat`, `lon` (each optional; omitted values use configured default location; supply both to target a custom location).

### `GET /api/v1/aurora/sources`
Aurora data from all sources for comparison.
Optional query params: `lat`, `lon` (must be provided together; only one returns HTTP 422).

### `GET /api/v1/weather/sources`
Weather data from all sources for comparison.
Optional query params: `lat`, `lon` (must be provided together; only one returns HTTP 422).

### `GET /api/v1/health`
Health check endpoint.

## Visibility Scoring Algorithm

**Total Score: 0-100** (weighted sum)

| Factor | Weight | Criteria |
|--------|--------|----------|
| Aurora Activity | 40% | KP index (need ≥3 for southern Sweden) |
| Cloud Cover | 30% | Lower is better (<25% = full points) |
| Visibility | 20% | Distance (>20km = full points) |
| Precipitation | 10% | None = full points |

### Night Sky Penalties

- **Moon penalty**: up to 15 points
  - `Moon_Factor = Illumination × max(0, sin(Moon_Elevation))`
  - Deducts 0-15 points based on moon illumination and elevation (computed with `ephem`)

- **Sun/daylight penalty**: up to 50 points (based on sun elevation)
  - Daylight (`≥ 0°`): 50 points
  - Civil twilight (`-6° to <0°`): 40 points
  - Nautical twilight (`-12° to <-6°`): 20 points
  - Astronomical twilight (`-18° to <-12°`): 8 points
  - Full darkness (`< -18°`): 0 points

- **Final score**
  - `max(0, positive_sum - moon_penalty - sun_penalty)`

**Score Ranges:**
- 80-100: Excellent - Great chance to see aurora
- 60-79: Good - Worth checking outside
- 40-59: Fair - Aurora may be visible
- 20-39: Poor - Low visibility likely
- 0-19: Very poor - Not recommended

## Data Sources

### Aurora Forecasts

**NOAA SWPC** (Primary)
- 360×181 global grid with 5-minute updates
- Bilinear interpolation for exact coordinates
- API: `https://services.swpc.noaa.gov/json/ovation_aurora_latest.json`

**Auroras.live** (Secondary)
- Direct location-specific data
- Real-time KP index
- API: `https://api.auroras.live/v1/`

### Weather Data

**Met.no** (Primary - Norwegian Meteorological Institute)
- High-resolution Nordic weather forecasts
- Requires User-Agent header
- API: `https://api.met.no/weatherapi/locationforecast/2.0/compact`

**SMHI** (Secondary - Swedish Official)
- 2.5km resolution forecasts
- Cloud cover in oktas (0-8 scale)
- 6-hour updates
- API: SMHI Open Data Meteorological Forecasts

**Open-Meteo** (Tertiary)
- 1-2km resolution
- 10,000 free calls/day
- Hourly updates
- API: `https://api.open-meteo.com/v1/forecast`

## Configuration

Environment variables (`.env`):

```bash
# Location
LOCATION_LAT=55.7
LOCATION_LON=13.4
LOCATION_NAME=Södra Sandby

# Cache TTL (seconds)
CACHE_TTL_AURORA=300      # 5 minutes
CACHE_TTL_WEATHER=1800    # 30 minutes

# Logging
LOG_LEVEL=info
```

## Testing

```bash
cd backend
pytest tests/ -v
```

## Project Structure

```
norrsken/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI entry point
│   │   ├── config.py                  # Settings
│   │   ├── models/                    # Pydantic models
│   │   ├── services/                  # Data clients & logic
│   │   │   ├── aurora/                # Aurora data clients
│   │   │   ├── weather/               # Weather data clients
│   │   │   ├── correlation.py         # Scoring algorithm
│   │   │   ├── cache_service.py       # Caching
│   │   │   └── aggregator.py          # Multi-source fetching
│   │   ├── api/routes/                # API endpoints
│   │   └── utils/                     # Utilities
│   │       ├── geo.py
│   │       ├── logger.py
│   │       ├── moon.py
│   │       └── sun.py
│   └── tests/                         # Unit tests
├── frontend/
│   ├── index.html
│   ├── css/
│   │   ├── tokens.css
│   │   ├── base.css
│   │   ├── layout.css
│   │   ├── main.css
│   │   └── components/
│   │       ├── score.css
│   │       ├── data-cards.css
│   │       ├── chart.css
│   │       └── modal.css
│   └── js/
│       ├── main.js                    # App initialization
│       ├── api.js                     # API client
│       ├── location-manager.js
│       └── components/                # UI components
│           ├── aurora-display.js
│           ├── weather-display.js
│           ├── forecast-chart.js
│           ├── settings-modal.js
│           ├── map-selector.js
│           ├── tooltip.js
│           └── visibility-score.js
└── README.md
```

## License

MIT
