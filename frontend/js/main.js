/**
 * Main application entry point
 */

import { APIClient } from './api.js';
import { VisibilityScoreDisplay } from './components/visibility-score.js';
import { AuroraDisplay } from './components/aurora-display.js';
import { WeatherDisplay } from './components/weather-display.js';
import { ForecastChart } from './components/forecast-chart.js';
import { LocationManager } from './location-manager.js';
import { SettingsModal } from './components/settings-modal.js';

class App {
    constructor() {
        this.api = new APIClient();
        this.scoreDisplay = new VisibilityScoreDisplay();
        this.auroraDisplay = new AuroraDisplay();
        this.weatherDisplay = new WeatherDisplay();
        this.forecastChart = new ForecastChart();
        this.locationManager = new LocationManager();
        this.settingsModal = new SettingsModal(this.locationManager);

        this.lastUpdateEl = document.getElementById('lastUpdate');
        this.locationDisplayEl = document.getElementById('locationDisplay');
        this.refreshInterval = 5 * 60 * 1000; // 5 minutes
        this.lastSuccessfulLoad = null;
    }

    /**
     * Initialize the application
     */
    async init() {
        console.log('Initializing Aurora Visibility app...');

        // Set up settings button
        const settingsBtn = document.getElementById('settingsBtn');
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => {
                this.settingsModal.open();
            });
        }

        // Listen for location changes
        window.addEventListener('locationChanged', () => {
            console.log('Location changed, reloading data...');
            this.loadData();
        });

        // Update location display
        this.updateLocationDisplay();

        // Load initial data
        await this.loadData();

        // Set up auto-refresh
        setInterval(() => this.loadData(), this.refreshInterval);
        setInterval(() => this.checkDataFreshness(), 60 * 1000);

        console.log('App initialized. Auto-refresh every 5 minutes.');
    }

    /**
     * Load all data from API
     */
    async loadData() {
        try {
            console.log('Fetching data from API...');

            // Get current location
            const location = this.locationManager.getLocation();
            console.log('Using location:', location);

            // Fetch current prediction
            const prediction = await this.api.getCurrentPrediction(location.lat, location.lon);
            console.log('Current prediction:', prediction);

            // Update UI components
            this.scoreDisplay.update(prediction.visibility_score);
            this.auroraDisplay.update(prediction.aurora);
            this.weatherDisplay.update(prediction.weather);

            // Update last update time and location display
            this.updateLastUpdateTime();
            this.updateLocationDisplay();

            // Fetch and update forecast
            const forecast = await this.api.getForecast(24, location.lat, location.lon);
            console.log('Forecast data:', forecast);
            this.forecastChart.update(forecast.forecast);

            this.lastSuccessfulLoad = Date.now();
            this.checkDataFreshness();

            console.log('Data loaded successfully.');

        } catch (error) {
            console.error('Error loading data:', error);
            this.showError(error.message);
        }
    }

    /**
     * Update the last update timestamp
     */
    updateLastUpdateTime() {
        const now = new Date();
        this.lastUpdateEl.textContent = now.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }

    /**
     * Check whether loaded data is stale and update timestamp indicator
     */
    checkDataFreshness() {
        if (!this.lastUpdateEl) return;

        const isStale = this.lastSuccessfulLoad && (Date.now() - this.lastSuccessfulLoad > 10 * 60 * 1000);

        if (isStale) {
            this.lastUpdateEl.classList.add('stale-data');
            this.lastUpdateEl.setAttribute('data-stale', 'true');
        } else {
            this.lastUpdateEl.classList.remove('stale-data');
            this.lastUpdateEl.removeAttribute('data-stale');
        }
    }

    /**
     * Update location display in header
     */
    updateLocationDisplay() {
        if (!this.locationDisplayEl) return;

        const location = this.locationManager.getLocation();
        this.locationDisplayEl.textContent = `${location.name} (${location.lat.toFixed(1)}°N, ${location.lon.toFixed(1)}°E)`;
    }

    /**
     * Show error message to user
     * @param {string} message - Error message
     */
    showError(message) {
        const recommendationEl = document.getElementById('recommendation');
        recommendationEl.textContent = `Error: ${message}`;
        recommendationEl.style.color = 'var(--danger)';
    }
}

// Start the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const app = new App();
    app.init();
});
