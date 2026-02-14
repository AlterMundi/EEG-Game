/**
 * Neurofeedback Focus Game - Charts & Visualizations
 * Light theme canvas charts — lavender / mint palette
 */

// Palette shared with game
const CHART_COLORS = {
    bg: '#FDFBFF',
    grid: 'rgba(212, 196, 245, 0.25)',
    axis: '#D4C4F5',
    text: '#9B8AB8',
    title: '#6B5A8E',
    line1: '#9B7EDC',
    line2: '#6BC4A0',
    fill1: 'rgba(155, 126, 220, 0.18)',
    threshold: 'rgba(107, 196, 160, 0.45)',
    thresholdText: '#6BC4A0',
};

// ==================== RESULTS CHART ====================
function drawResultsChart(session) {
    const canvas = document.getElementById('resultsChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = 280;

    const w = canvas.width;
    const h = canvas.height;
    const pad = 52;

    // Background
    ctx.fillStyle = CHART_COLORS.bg;
    ctx.fillRect(0, 0, w, h);

    // Title
    ctx.fillStyle = CHART_COLORS.title;
    ctx.font = '600 14px Quicksand, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Focus Over Time', w / 2, 22);

    // Axes
    ctx.strokeStyle = CHART_COLORS.axis;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(pad, pad - 6);
    ctx.lineTo(pad, h - pad);
    ctx.lineTo(w - pad + 6, h - pad);
    ctx.stroke();

    // Axis labels
    ctx.fillStyle = CHART_COLORS.text;
    ctx.font = '500 10px Nunito, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Time', w / 2, h - 12);

    ctx.save();
    ctx.translate(14, h / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('Focus Score', 0, 0);
    ctx.restore();

    // Grid + Y labels
    ctx.strokeStyle = CHART_COLORS.grid;
    ctx.lineWidth = 0.8;
    for (let i = 0; i <= 10; i++) {
        const y = pad + (h - pad * 2) * (i / 10);
        ctx.beginPath();
        ctx.moveTo(pad, y);
        ctx.lineTo(w - pad, y);
        ctx.stroke();

        ctx.fillStyle = CHART_COLORS.text;
        ctx.textAlign = 'right';
        ctx.font = '500 10px Nunito, sans-serif';
        ctx.fillText((100 - i * 10).toString(), pad - 8, y + 4);
    }

    if (!session.scores || session.scores.length === 0) return;

    const xScale = (w - pad * 2) / (session.scores.length - 1 || 1);
    const yScale = (h - pad * 2) / 100;

    // Line
    ctx.strokeStyle = CHART_COLORS.line1;
    ctx.lineWidth = 2.5;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    ctx.beginPath();

    session.scores.forEach((score, i) => {
        const x = pad + i * xScale;
        const y = h - pad - score * yScale;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Fill under line
    ctx.lineTo(pad + (session.scores.length - 1) * xScale, h - pad);
    ctx.lineTo(pad, h - pad);
    ctx.closePath();

    const grad = ctx.createLinearGradient(0, pad, 0, h - pad);
    grad.addColorStop(0, CHART_COLORS.fill1);
    grad.addColorStop(1, 'rgba(155, 126, 220, 0.02)');
    ctx.fillStyle = grad;
    ctx.fill();

    // Threshold line (70)
    const tY = h - pad - 70 * yScale;
    ctx.strokeStyle = CHART_COLORS.threshold;
    ctx.setLineDash([5, 6]);
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(pad, tY);
    ctx.lineTo(w - pad, tY);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.fillStyle = CHART_COLORS.thresholdText;
    ctx.font = '600 10px Nunito, sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText('High Focus', w - pad + 6, tY + 4);
}

// ==================== COMPARISON CHART ====================
function drawComparisonChart(baselineSession, postTherapySession) {
    const canvas = document.getElementById('comparisonChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = 360;

    const w = canvas.width;
    const h = canvas.height;
    const pad = 52;

    // Background
    ctx.fillStyle = CHART_COLORS.bg;
    ctx.fillRect(0, 0, w, h);

    // Title
    ctx.fillStyle = CHART_COLORS.title;
    ctx.font = '600 14px Quicksand, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Baseline vs Post-Therapy', w / 2, 22);

    // Axes
    ctx.strokeStyle = CHART_COLORS.axis;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(pad, pad - 6);
    ctx.lineTo(pad, h - pad);
    ctx.lineTo(w - pad + 6, h - pad);
    ctx.stroke();

    // Grid + labels
    ctx.strokeStyle = CHART_COLORS.grid;
    ctx.lineWidth = 0.8;
    for (let i = 0; i <= 10; i++) {
        const y = pad + (h - pad * 2) * (i / 10);
        ctx.beginPath();
        ctx.moveTo(pad, y);
        ctx.lineTo(w - pad, y);
        ctx.stroke();

        ctx.fillStyle = CHART_COLORS.text;
        ctx.textAlign = 'right';
        ctx.font = '500 10px Nunito, sans-serif';
        ctx.fillText((100 - i * 10).toString(), pad - 8, y + 4);
    }

    const maxLen = Math.max(baselineSession.scores.length, postTherapySession.scores.length);
    if (maxLen === 0) return;

    const xScale = (w - pad * 2) / (maxLen - 1 || 1);
    const yScale = (h - pad * 2) / 100;

    // Baseline
    drawLine(ctx, baselineSession.scores, xScale, yScale, CHART_COLORS.line1, pad, h - pad);

    // Post-therapy
    drawLine(ctx, postTherapySession.scores, xScale, yScale, CHART_COLORS.line2, pad, h - pad);

    // Legend
    drawLegend(ctx, w - 160, 46, [
        { color: CHART_COLORS.line1, label: 'Baseline' },
        { color: CHART_COLORS.line2, label: 'Post-Therapy' },
    ]);
}

function drawLine(ctx, scores, xScale, yScale, color, padL, baseY) {
    if (!scores || scores.length === 0) return;

    ctx.strokeStyle = color;
    ctx.lineWidth = 2.5;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    ctx.beginPath();

    scores.forEach((score, i) => {
        const x = padL + i * xScale;
        const y = baseY - score * yScale;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.stroke();
}

function drawLegend(ctx, x, y, items) {
    ctx.font = '600 11px Nunito, sans-serif';
    ctx.textAlign = 'left';

    items.forEach((item, i) => {
        const iy = y + i * 22;

        // Pill-shaped swatch
        ctx.fillStyle = item.color;
        ctx.beginPath();
        ctx.roundRect(x, iy - 6, 18, 10, 5);
        ctx.fill();

        ctx.fillStyle = CHART_COLORS.title;
        ctx.fillText(item.label, x + 24, iy + 2);
    });
}

// Export
window.drawResultsChart = drawResultsChart;
window.drawComparisonChart = drawComparisonChart;
