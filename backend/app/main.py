import os

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .config import settings
from .api.routes import health, prediction, aurora, weather, geocode

FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
)

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
)

# Register routes
app.include_router(health.router)
app.include_router(prediction.router)
app.include_router(aurora.router)
app.include_router(weather.router)
app.include_router(geocode.router)


@app.get("/")
async def root():
    """Serve frontend index page."""
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="frontend")
