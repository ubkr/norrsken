/**
 * Weather data display component
 */

export class WeatherDisplay {
    constructor() {
        this.containerEl = document.getElementById('weatherData');
    }

    /**
     * Update the weather data display with side-by-side comparison
     * @param {Object} weatherData - Weather data from API
     */
    update(weatherData) {
        if (!weatherData) {
            this.containerEl.innerHTML = '<p class="loading">No weather data</p>';
            return;
        }
        const { primary, secondary } = weatherData;

        const formatTime = (isoString) => {
            if (!isoString) return '--:--';
            return new Date(isoString).toLocaleTimeString('en-US', {
                hour: '2-digit', minute: '2-digit'
            });
        };

        const formatVal = (val, unit, fixed = 1) =>
            val !== null && val !== undefined ? `${val.toFixed(fixed)}${unit}` : '--';

        const p = primary || {};
        const s = secondary || {};
        const hasSecondary = !!s.source;

        const icons = {
            cloud: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9z"/></svg>',
            vis:   '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>',
            precip:'<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><line x1="16" y1="13" x2="16" y2="21"/><line x1="8" y1="13" x2="8" y2="21"/><line x1="12" y1="15" x2="12" y2="23"/><path d="M20 16.58A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25"/></svg>',
            temp:  '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/></svg>',
            time:  '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>'
        };

        const secCol = hasSecondary ? `<div class="wg-head source-tag">${this.formatSourceName(s.source)}</div>` : '';

        const row = (icon, label, pVal, sVal) => `
            <div class="wg-label">${icon} ${label}</div>
            <div class="wg-value">${pVal}</div>
            ${hasSecondary ? `<div class="wg-value">${sVal}</div>` : ''}
        `;

        const html = `
            <div class="weather-grid${hasSecondary ? '' : ' weather-grid--single'}">
                <div class="wg-head-empty"></div>
                <div class="wg-head source-tag">${this.formatSourceName(p.source)}</div>
                ${secCol}
                ${row(icons.cloud,  'Cloud Cover',   formatVal(p.cloud_cover, '%', 0),       formatVal(s.cloud_cover, '%', 0))}
                ${row(icons.vis,    'Visibility',    formatVal(p.visibility_km, ' km'),       formatVal(s.visibility_km, ' km'))}
                ${row(icons.precip, 'Precipitation', formatVal(p.precipitation_mm, ' mm'),    formatVal(s.precipitation_mm, ' mm'))}
                ${row(icons.temp,   'Temperature',   formatVal(p.temperature_c, '°C'),        formatVal(s.temperature_c, '°C'))}
                ${row(icons.time,   'Updated',       formatTime(p.last_updated),              formatTime(s.last_updated))}
            </div>
        `;

        this.containerEl.innerHTML = html;
    }

    /**
     * Format source name for display
     * @param {string} name - Source name
     */
    formatSourceName(name) {
        const names = {
            'smhi': 'SMHI',
            'open_meteo': 'Open-Meteo',
            'met_no': 'MET.NO'
        };
        return names[name] || name || '—';
    }
}
