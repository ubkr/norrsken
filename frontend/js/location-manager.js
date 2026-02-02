/**
 * LocationManager - Manages user location preferences with localStorage persistence
 */

const DEFAULT_LOCATION = {
    lat: 55.7,
    lon: 13.4,
    name: "Södra Sandby, Sweden"
};

const SWEDEN_BOUNDS = {
    minLat: 55.0,
    maxLat: 69.5,
    minLon: 10.5,
    maxLon: 24.5
};

const STORAGE_KEY = 'aurora_location';

export class LocationManager {
    constructor() {
        this.currentLocation = this.loadLocation();
    }

    /**
     * Get current location (from storage or default)
     */
    getLocation() {
        return { ...this.currentLocation };
    }

    /**
     * Save location to localStorage and emit change event
     */
    saveLocation(lat, lon, name) {
        // Validate coordinates
        if (lat < -90 || lat > 90 || lon < -180 || lon > 180) {
            throw new Error('Invalid coordinates');
        }

        const location = {
            lat,
            lon,
            name: name || `Custom Location (${lat.toFixed(2)}°, ${lon.toFixed(2)}°)`,
            timestamp: new Date().toISOString()
        };

        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(location));
            this.currentLocation = location;

            // Emit custom event for location change
            window.dispatchEvent(new CustomEvent('locationChanged', {
                detail: location
            }));

            return true;
        } catch (error) {
            console.error('Failed to save location to localStorage:', error);
            return false;
        }
    }

    /**
     * Clear saved location and revert to default
     */
    clearLocation() {
        try {
            localStorage.removeItem(STORAGE_KEY);
            this.currentLocation = { ...DEFAULT_LOCATION };

            window.dispatchEvent(new CustomEvent('locationChanged', {
                detail: this.currentLocation
            }));

            return true;
        } catch (error) {
            console.error('Failed to clear location:', error);
            return false;
        }
    }

    /**
     * Load location from localStorage or return default
     */
    loadLocation() {
        try {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (!stored) {
                return { ...DEFAULT_LOCATION };
            }

            const location = JSON.parse(stored);

            // Validate structure
            if (!this.isValidLocation(location)) {
                console.warn('Invalid location data in localStorage, using default');
                return { ...DEFAULT_LOCATION };
            }

            return location;
        } catch (error) {
            console.error('Failed to load location from localStorage:', error);
            return { ...DEFAULT_LOCATION };
        }
    }

    /**
     * Check if location data has valid structure
     */
    isValidLocation(location) {
        return location &&
               typeof location.lat === 'number' &&
               typeof location.lon === 'number' &&
               typeof location.name === 'string' &&
               location.lat >= -90 && location.lat <= 90 &&
               location.lon >= -180 && location.lon <= 180;
    }

    /**
     * Check if coordinates are outside Sweden
     */
    isOutsideSweden(lat, lon) {
        return lat < SWEDEN_BOUNDS.minLat ||
               lat > SWEDEN_BOUNDS.maxLat ||
               lon < SWEDEN_BOUNDS.minLon ||
               lon > SWEDEN_BOUNDS.maxLon;
    }

    /**
     * Get default location
     */
    static getDefaultLocation() {
        return { ...DEFAULT_LOCATION };
    }
}
