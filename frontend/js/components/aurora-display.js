/**
 * Aurora data display component
 */

export class AuroraDisplay {
    constructor() {
        this.containerEl = document.getElementById('auroraData');
    }

    /**
     * Update the aurora data display
     * @param {Object} auroraData - Aurora data from API
     */
    update(auroraData) {
        const { primary, secondary, tertiary } = auroraData;

        let html = '';

        // Primary source
        html += this.renderSource(primary, 'Primary');

        // Secondary source
        if (secondary) {
            html += '<hr class="source-divider">';
            html += this.renderSource(secondary, 'Secondary');
        }

        // Tertiary source
        if (tertiary) {
            html += '<hr class="source-divider">';
            html += this.renderSource(tertiary, 'Tertiary');
        }

        this.containerEl.innerHTML = html;
    }

    /**
     * Render a single source
     * @param {Object} source - Source data
     * @param {string} label - Source label
     */
    renderSource(source, label) {
        const { source: name, kp_index, probability, last_updated } = source;

        const updateTime = new Date(last_updated).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });

        let html = `
            <div class="source-section">
                <span class="source-tag">${label}: ${this.formatSourceName(name)}</span>
                <div class="data-item">
                    <span class="data-label">KP Index</span>
                    <span class="data-value">${kp_index.toFixed(1)}</span>
                </div>
        `;

        if (probability !== null) {
            html += `
                <div class="data-item">
                    <span class="data-label">Probability</span>
                    <span class="data-value">${probability.toFixed(1)}%</span>
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
            'noaa_swpc': 'NOAA SWPC',
            'auroras_live': 'Auroras.live',
            'aurora_space': 'Aurora Space'
        };
        return names[name] || name;
    }
}
