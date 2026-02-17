/**
 * 24-hour forecast chart component
 */

export class ForecastChart {
    constructor() {
        this.canvas = document.getElementById('forecastChart');
        this.chart = null;
    }

    getCssVariable(tokenName, fallback = '') {
        const value = getComputedStyle(document.documentElement)
            .getPropertyValue(tokenName)
            .trim();
        return value || fallback;
    }

    hexToRgba(hex, alpha) {
        const normalized = hex.replace('#', '').trim();
        if (!/^[0-9a-fA-F]{6}$/.test(normalized)) {
            return hex;
        }

        const red = parseInt(normalized.slice(0, 2), 16);
        const green = parseInt(normalized.slice(2, 4), 16);
        const blue = parseInt(normalized.slice(4, 6), 16);
        return `rgba(${red}, ${green}, ${blue}, ${alpha})`;
    }

    /**
     * Initialize the chart
     * @param {Array} forecastData - Array of forecast items
     */
    init(forecastData) {
        if (this.chart) {
            this.chart.destroy();
        }

        const colorStatusExcellent = this.getCssVariable('--color-status-excellent', '#00ffc8');
        const colorStatusGood = this.getCssVariable('--color-status-good', '#a6ff00');
        const colorStatusFair = this.getCssVariable('--color-status-fair', '#ffcc00');
        const colorStatusPoor = this.getCssVariable('--color-status-poor', '#ff3366');
        const colorSeriesLine = this.getCssVariable('--color-accent-tertiary', '#00b3ff');
        const colorSeriesFill = this.hexToRgba(colorSeriesLine, 0.15);
        const colorTickText = this.getCssVariable('--color-text-secondary', '#8e9bb3');
        const colorAxisBorder = this.getCssVariable('--border-color', 'rgba(255, 255, 255, 0.1)');
        const colorGrid = this.getCssVariable('--border-color', 'rgba(255, 255, 255, 0.1)');

        const labels = forecastData.map(item => {
            const date = new Date(item.timestamp);
            return date.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit'
            });
        });

        const scores = forecastData.map(item => item.visibility_score);

        // Color points based on score
        const pointColors = scores.map(score => {
            if (score >= 80) return colorStatusExcellent;
            if (score >= 60) return colorStatusGood;
            if (score >= 40) return colorStatusFair;
            return colorStatusPoor;
        });

        this.chart = new Chart(this.canvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Visibility Score',
                    data: scores,
                    borderColor: colorSeriesLine,
                    backgroundColor: colorSeriesFill,
                    pointBackgroundColor: pointColors,
                    pointBorderColor: pointColors,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Score: ${context.parsed.y.toFixed(0)}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        border: {
                            color: colorAxisBorder
                        },
                        ticks: {
                            color: colorTickText
                        },
                        grid: {
                            color: colorGrid
                        }
                    },
                    x: {
                        border: {
                            color: colorAxisBorder
                        },
                        ticks: {
                            color: colorTickText,
                            maxRotation: 45,
                            minRotation: 45
                        },
                        grid: {
                            color: colorGrid
                        }
                    }
                }
            }
        });
    }

    /**
     * Update the chart with new data
     * @param {Array} forecastData - Array of forecast items
     */
    update(forecastData) {
        this.init(forecastData);
    }
}
