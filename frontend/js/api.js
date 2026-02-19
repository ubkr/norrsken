/**
 * API client for backend communication
 */

const API_BASE_URL = 'http://localhost:8000';

export class APIClient {
    /**
     * Validate coordinates before calling backend
     * @param {number} lat - Latitude
     * @param {number} lon - Longitude
     */
    validateCoordinates(lat, lon) {
        if (!Number.isFinite(lat) || !Number.isFinite(lon)) {
            throw new Error('Valid lat/lon are required for API calls');
        }
    }

    /**
     * Build query string with coordinates and extra params
     * @param {number} lat - Latitude
     * @param {number} lon - Longitude
     * @param {Object} params - Additional query parameters
     */
    buildQueryString(lat, lon, params = {}) {
        const searchParams = new URLSearchParams();

        Object.entries(params).forEach(([key, value]) => {
            if (value !== null && value !== undefined) {
                searchParams.append(key, value);
            }
        });

        searchParams.append('lat', lat);
        searchParams.append('lon', lon);

        const queryString = searchParams.toString();
        return queryString ? `?${queryString}` : '';
    }

    /**
      * Fetch current prediction data
      * Note: lat and lon are required and must be finite numbers.
      * This call throws if lat or lon is not a finite number.
      * @param {number} lat - Required latitude
      * @param {number} lon - Required longitude
      * @throws {Error} If lat or lon is missing or not finite
      */
    async getCurrentPrediction(lat, lon) {
        this.validateCoordinates(lat, lon);
        const queryString = this.buildQueryString(lat, lon);
        const url = `${API_BASE_URL}/api/v1/prediction/current${queryString}`;
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Failed to fetch prediction: ${response.statusText}`);
        }
        return await response.json();
    }

    /**
      * Fetch forecast data
      * @param {number} hours - Number of hours to forecast (default 24)
      * Note: lat and lon are required and must be finite numbers.
      * This call throws if lat or lon is not a finite number.
      * @param {number} lat - Required latitude
      * @param {number} lon - Required longitude
      * @throws {Error} If lat or lon is missing or not finite
      */
    async getForecast(hours = 24, lat, lon) {
        this.validateCoordinates(lat, lon);
        const queryString = this.buildQueryString(lat, lon, { hours });
        const url = `${API_BASE_URL}/api/v1/prediction/forecast${queryString}`;
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Failed to fetch forecast: ${response.statusText}`);
        }
        return await response.json();
    }

    /**
      * Fetch aurora sources
      * Note: lat and lon are required and must be finite numbers.
      * This call throws if lat or lon is not a finite number.
      * @param {number} lat - Required latitude
      * @param {number} lon - Required longitude
      * @throws {Error} If lat or lon is missing or not finite
      */
    async getAuroraSources(lat, lon) {
        this.validateCoordinates(lat, lon);
        const queryString = this.buildQueryString(lat, lon);
        const response = await fetch(`${API_BASE_URL}/api/v1/aurora/sources${queryString}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch aurora sources: ${response.statusText}`);
        }
        return await response.json();
    }

    /**
      * Fetch weather sources
      * Note: lat and lon are required and must be finite numbers.
      * This call throws if lat or lon is not a finite number.
      * @param {number} lat - Required latitude
      * @param {number} lon - Required longitude
      * @throws {Error} If lat or lon is missing or not finite
      */
    async getWeatherSources(lat, lon) {
        this.validateCoordinates(lat, lon);
        const queryString = this.buildQueryString(lat, lon);
        const response = await fetch(`${API_BASE_URL}/api/v1/weather/sources${queryString}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch weather sources: ${response.statusText}`);
        }
        return await response.json();
    }
}
