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
     * Get KP index interpretation for Södra Sandby (55.7°N)
     * @param {number} kp - KP index value (0-9)
     * @returns {{level: string, description: string, class: string}}
     */
    getKpInterpretation(kp) {
        if (kp >= 7) {
            return {
                level: 'Very High',
                description: 'Strong aurora activity - excellent chance of visibility',
                class: 'kp-very-high'
            };
        } else if (kp >= 5) {
            return {
                level: 'High',
                description: 'Good aurora activity - favorable for viewing',
                class: 'kp-high'
            };
        } else if (kp >= 3) {
            return {
                level: 'Moderate',
                description: 'Sufficient aurora activity - possible to see at this latitude',
                class: 'kp-moderate'
            };
        } else if (kp >= 2) {
            return {
                level: 'Low',
                description: 'Insufficient for this latitude - aurora unlikely',
                class: 'kp-low'
            };
        } else {
            return {
                level: 'Very Low',
                description: 'Too low for this latitude - aurora not visible',
                class: 'kp-very-low'
            };
        }
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

        const kpInterpretation = this.getKpInterpretation(kp_index);

        let html = `
            <div class="source-section">
                <span class="source-tag">${label}: ${this.formatSourceName(name)}</span>
                <div class="data-item">
                    <span class="data-label">
                        KP Index
                        <span class="info-icon" title="KP index measures aurora activity. For Södra Sandby (55.7°N), KP ≥ 3 is required for potential aurora visibility.">ⓘ</span>
                    </span>
                    <span class="data-value">
                        ${kp_index.toFixed(1)}
                        <span class="kp-badge ${kpInterpretation.class}">${kpInterpretation.level}</span>
                    </span>
                </div>
                <div class="kp-description">${kpInterpretation.description}</div>
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
