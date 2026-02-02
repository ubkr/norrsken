from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .api.routes import health, prediction, aurora, weather

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health.router)
app.include_router(prediction.router)
app.include_router(aurora.router)
app.include_router(weather.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Aurora Visibility Prediction API",
        "docs": "/docs",
        "health": "/api/v1/health"
    }
