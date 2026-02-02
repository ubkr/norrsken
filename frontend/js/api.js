/**
 * API client for backend communication
 */

const API_BASE_URL = 'http://localhost:8000';

export class APIClient {
    /**
     * Fetch current prediction data
     */
    async getCurrentPrediction() {
        const response = await fetch(`${API_BASE_URL}/api/v1/prediction/current`);
        if (!response.ok) {
            throw new Error(`Failed to fetch prediction: ${response.statusText}`);
        }
        return await response.json();
    }

    /**
     * Fetch forecast data
     * @param {number} hours - Number of hours to forecast (default 24)
     */
    async getForecast(hours = 24) {
        const response = await fetch(`${API_BASE_URL}/api/v1/prediction/forecast?hours=${hours}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch forecast: ${response.statusText}`);
        }
        return await response.json();
    }

    /**
     * Fetch aurora sources
     */
    async getAuroraSources() {
        const response = await fetch(`${API_BASE_URL}/api/v1/aurora/sources`);
        if (!response.ok) {
            throw new Error(`Failed to fetch aurora sources: ${response.statusText}`);
        }
        return await response.json();
    }

    /**
     * Fetch weather sources
     */
    async getWeatherSources() {
        const response = await fetch(`${API_BASE_URL}/api/v1/weather/sources`);
        if (!response.ok) {
            throw new Error(`Failed to fetch weather sources: ${response.statusText}`);
        }
        return await response.json();
    }
}
