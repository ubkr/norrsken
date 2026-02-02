/**
 * 24-hour forecast chart component
 */

export class ForecastChart {
    constructor() {
        this.canvas = document.getElementById('forecastChart');
        this.chart = null;
    }

    /**
     * Initialize the chart
     * @param {Array} forecastData - Array of forecast items
     */
    init(forecastData) {
        if (this.chart) {
            this.chart.destroy();
        }

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
            if (score >= 80) return 'rgba(129, 201, 149, 1)'; // Green
            if (score >= 60) return 'rgba(138, 180, 248, 1)'; // Blue
            if (score >= 40) return 'rgba(253, 214, 99, 1)'; // Yellow
            return 'rgba(242, 139, 130, 1)'; // Red
        });

        this.chart = new Chart(this.canvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Visibility Score',
                    data: scores,
                    borderColor: 'rgba(138, 180, 248, 1)',
                    backgroundColor: 'rgba(138, 180, 248, 0.1)',
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
                        ticks: {
                            color: '#9aa0a6'
                        },
                        grid: {
                            color: 'rgba(154, 160, 166, 0.1)'
                        }
                    },
                    x: {
                        ticks: {
                            color: '#9aa0a6',
                            maxRotation: 45,
                            minRotation: 45
                        },
                        grid: {
                            color: 'rgba(154, 160, 166, 0.1)'
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
