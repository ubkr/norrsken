# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Application for fetching aurora borealis ("norrsken") visibility predictions for Södra Sandby (outside Lund, Sweden) and correlating them with current weather conditions.

**Location**: Södra Sandby, Skåne län, Sweden
- Coordinates: ~55.7°N, 13.4°E

## Architecture

**Backend**: Python
- Fetches aurora visibility predictions from aurora forecast APIs
- Retrieves current weather data for Södra Sandby
- Correlates aurora predictions with weather conditions (cloud cover, visibility)
- Provides API endpoints for frontend consumption

**Frontend**: HTML/CSS/JavaScript
- Displays current aurora predictions
- Shows weather conditions affecting visibility
- Presents correlation analysis

## Data Sources to Consider

**Aurora Predictions**:
- NOAA Space Weather Prediction Center
- Finnish Meteorological Institute (FMI) aurora forecast
- Auroras.live or similar services

**Weather Data**:
- SMHI (Swedish Meteorological and Hydrological Institute) - primary source for Swedish weather
- OpenWeatherMap or similar APIs

## Documentation Standards

All documentation files (README.md, API docs, etc.) must reflect the **current implementation only**. Never include changelogs, "what changed" sections, or historical implementation notes in documentation. Documentation is always a snapshot of the present state.
