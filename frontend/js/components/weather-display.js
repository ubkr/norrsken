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
                    <span class="data-label"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9z"/></svg>Cloud Cover</span>
                    <span class="data-value">${cloud_cover.toFixed(1)}%</span>
                </div>
                <div class="data-item">
                    <span class="data-label"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>Visibility</span>
                    <span class="data-value">${visibility_km.toFixed(1)} km</span>
                </div>
                <div class="data-item">
                    <span class="data-label"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="16" y1="13" x2="16" y2="21"/><line x1="8" y1="13" x2="8" y2="21"/><line x1="12" y1="15" x2="12" y2="23"/><path d="M20 16.58A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25"/></svg>Precipitation</span>
                    <span class="data-value">${precipitation_mm.toFixed(1)} mm</span>
                </div>
        `;

        if (temperature_c !== null) {
            html += `
                <div class="data-item">
                    <span class="data-label"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/></svg>Temperature</span>
                    <span class="data-value">${temperature_c.toFixed(1)}°C</span>
                </div>
            `;
        }

        html += `
                <div class="data-item">
                    <span class="data-label"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>Updated</span>
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
