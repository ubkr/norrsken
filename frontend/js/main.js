/**
 * Main application entry point
 */

import { APIClient } from './api.js';
import { VisibilityScoreDisplay } from './components/visibility-score.js';
import { AuroraDisplay } from './components/aurora-display.js';
import { WeatherDisplay } from './components/weather-display.js';
import { ForecastChart } from './components/forecast-chart.js';

class App {
    constructor() {
        this.api = new APIClient();
        this.scoreDisplay = new VisibilityScoreDisplay();
        this.auroraDisplay = new AuroraDisplay();
        this.weatherDisplay = new WeatherDisplay();
        this.forecastChart = new ForecastChart();

        this.lastUpdateEl = document.getElementById('lastUpdate');
        this.refreshInterval = 5 * 60 * 1000; // 5 minutes
    }

    /**
     * Initialize the application
     */
    async init() {
        console.log('Initializing Aurora Visibility app...');

        // Load initial data
        await this.loadData();

        // Set up auto-refresh
        setInterval(() => this.loadData(), this.refreshInterval);

        console.log('App initialized. Auto-refresh every 5 minutes.');
    }

    /**
     * Load all data from API
     */
    async loadData() {
        try {
            console.log('Fetching data from API...');

            // Fetch current prediction
            const prediction = await this.api.getCurrentPrediction();
            console.log('Current prediction:', prediction);

            // Update UI components
            this.scoreDisplay.update(prediction.visibility_score);
            this.auroraDisplay.update(prediction.aurora);
            this.weatherDisplay.update(prediction.weather);

            // Update last update time
            this.updateLastUpdateTime();

            // Fetch and update forecast
            const forecast = await this.api.getForecast(24);
            console.log('Forecast data:', forecast);
            this.forecastChart.update(forecast.forecast);

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
