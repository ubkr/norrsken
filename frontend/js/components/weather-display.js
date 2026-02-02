/**
 * Weather data display component
 */

export class WeatherDisplay {
    constructor() {
        this.containerEl = document.getElementById('weatherData');
    }

    /**
     * Update the weather data display
     * @param {Object} weatherData - Weather data from API
     */
    update(weatherData) {
        const { primary, secondary } = weatherData;

        let html = '';

        // Primary source
        html += this.renderSource(primary, 'Primary');

        // Secondary source
        if (secondary) {
            html += '<hr class="source-divider">';
            html += this.renderSource(secondary, 'Secondary');
        }

        this.containerEl.innerHTML = html;
    }

    /**
     * Render a single source
     * @param {Object} source - Source data
     * @param {string} label - Source label
     */
    renderSource(source, label) {
        const {
            source: name,
            cloud_cover,
            visibility_km,
            precipitation_mm,
            temperature_c,
            last_updated
        } = source;

        const updateTime = new Date(last_updated).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });

        let html = `
            <div class="source-section">
                <span class="source-tag">${label}: ${this.formatSourceName(name)}</span>
                <div class="data-item">
                    <span class="data-label">Cloud Cover</span>
                    <span class="data-value">${cloud_cover.toFixed(1)}%</span>
                </div>
                <div class="data-item">
                    <span class="data-label">Visibility</span>
                    <span class="data-value">${visibility_km.toFixed(1)} km</span>
                </div>
                <div class="data-item">
                    <span class="data-label">Precipitation</span>
                    <span class="data-value">${precipitation_mm.toFixed(1)} mm</span>
                </div>
        `;

        if (temperature_c !== null) {
            html += `
                <div class="data-item">
                    <span class="data-label">Temperature</span>
                    <span class="data-value">${temperature_c.toFixed(1)}°C</span>
                </div>
            `;
        }

        html += `
                <div class="data-item">
                    <span class="data-label">Updated</span>
                    <span class="data-value">${updateTime}</span>
                </div>
            </div>
        `;

        return html;
    }

    /**
     * Format source name for display
     * @param {string} name - Source name
     */
    formatSourceName(name) {
        const names = {
            'smhi': 'SMHI',
            'open_meteo': 'Open-Meteo'
        };
        return names[name] || name;
    }
}
