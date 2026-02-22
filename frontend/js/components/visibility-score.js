/**
 * Visibility score display component
 */

export class VisibilityScoreDisplay {
    constructor() {
        this.scoreValueEl = document.getElementById('scoreValue');
        this.scoreRingEl = document.getElementById('scoreRingFill');
        this.recommendationEl = document.getElementById('recommendation');
        this.scoreCardEl = document.getElementById('scoreCard');

        // Breakdown elements
        this.auroraBarEl = document.getElementById('auroraBar');
        this.auroraValueEl = document.getElementById('auroraValue');
        this.cloudsBarEl = document.getElementById('cloudsBar');
        this.cloudsValueEl = document.getElementById('cloudsValue');
        this.visibilityBarEl = document.getElementById('visibilityBar');
        this.visibilityValueEl = document.getElementById('visibilityValue');
        this.precipitationBarEl = document.getElementById('precipitationBar');
        this.precipitationValueEl = document.getElementById('precipitationValue');
        this.moonPenaltyBarEl = document.getElementById('moonPenaltyBar');
        this.moonPenaltyValueEl = document.getElementById('moonPenaltyValue');
        this.sunPenaltyBarEl = document.getElementById('sunPenaltyBar');
        this.sunPenaltyValueEl = document.getElementById('sunPenaltyValue');
    }

    /**
     * Update the visibility score display
     * @param {Object} visibilityScore - Visibility score data
     */
    update(visibilityScore) {
        const { total_score, breakdown, recommendation } = visibilityScore;

        // Update total score
        this.scoreValueEl.textContent = Math.round(total_score);

        if (this.scoreRingEl) {
            const circumference = 326.73;
            const offset = circumference - (total_score / 100) * circumference;
            this.scoreRingEl.style.strokeDashoffset = offset;
        }

        // Update recommendation
        this.recommendationEl.textContent = recommendation;

        // Update card background based on score
        this.updateCardStyle(total_score);

        // Update breakdown
        this.updateBreakdown('aurora', breakdown.aurora, 40);
        this.updateBreakdown('clouds', breakdown.clouds, 30);
        this.updateBreakdown('visibility', breakdown.visibility, 20);
        this.updateBreakdown('precipitation', breakdown.precipitation, 10);

        if (breakdown.moon && this.moonPenaltyBarEl && this.moonPenaltyValueEl) {
            const penalty = breakdown.moon.penalty_pts;
            const pct = Math.round((penalty / 15) * 100);
            this.moonPenaltyBarEl.style.width = `${pct}%`;
            const illuminationPct = Math.round(breakdown.moon.illumination * 100);
            this.moonPenaltyValueEl.textContent = `-${penalty.toFixed(1)} pts (${illuminationPct}% lit, ${breakdown.moon.elevation_deg.toFixed(0)}° alt)`;
        } else if (this.moonPenaltyBarEl && this.moonPenaltyValueEl) {
            this.moonPenaltyBarEl.style.width = '0%';
            this.moonPenaltyValueEl.textContent = '-0 pts';
        }

        if (breakdown.sun && this.sunPenaltyBarEl && this.sunPenaltyValueEl) {
            const penalty = breakdown.sun.penalty_pts;
            const pct = Math.round((penalty / 50) * 100);
            this.sunPenaltyBarEl.style.width = `${pct}%`;
            const phase = breakdown.sun.twilight_phase.replace(/_/g, ' ');
            const elev = breakdown.sun.elevation_deg.toFixed(0);
            const sign = breakdown.sun.elevation_deg >= 0 ? '+' : '';
            this.sunPenaltyValueEl.textContent = `-${penalty.toFixed(1)} pts (${phase}, ${sign}${elev}°)`;
        } else if (this.sunPenaltyBarEl && this.sunPenaltyValueEl) {
            this.sunPenaltyBarEl.style.width = '0%';
            this.sunPenaltyValueEl.textContent = '-0 pts';
        }
    }

    /**
     * Update a single breakdown item
     * @param {string} name - Breakdown item name
     * @param {number} value - Current value
     * @param {number} max - Maximum value
     */
    updateBreakdown(name, value, max) {
        const barEl = this[`${name}BarEl`];
        const valueEl = this[`${name}ValueEl`];

        const percentage = (value / max) * 100;
        barEl.style.width = `${percentage}%`;
        valueEl.textContent = `${Math.round(value)}/${max}`;
    }

    /**
     * Update card style based on score
     * @param {number} score - Total score
     */
    updateCardStyle(score) {
        // Remove existing score classes
        this.scoreCardEl.classList.remove('score-excellent', 'score-good', 'score-fair', 'score-poor');

        // Add appropriate class
        if (score >= 80) {
            this.scoreCardEl.classList.add('score-excellent');
        } else if (score >= 60) {
            this.scoreCardEl.classList.add('score-good');
        } else if (score >= 40) {
            this.scoreCardEl.classList.add('score-fair');
        } else {
            this.scoreCardEl.classList.add('score-poor');
        }
    }
}
