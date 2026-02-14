/**
 * Neurofeedback Focus Game - Game Visualization
 * Canvas-based ball game — light, organic, chill aesthetic
 */

// ==================== GAME STATE ====================
const game = {
    canvas: null,
    ctx: null,
    ball: {
        x: 0,
        y: 0,
        targetY: 0,
        radius: 22,
        glowRadius: 0,
    },
    score: 0,
    peakScore: 0,
    particles: [],
    time: 0,
    animationFrame: null
};

// Palette (matches CSS theme)
const PALETTE = {
    bgTop: '#F5F0FF',
    bgBot: '#EDE5FF',
    ballFill: '#B89EE8',
    ballGlow: 'rgba(155, 126, 220, 0.35)',
    pathFill: 'rgba(212, 196, 245, 0.25)',
    pathEdge: 'rgba(212, 196, 245, 0.4)',
    zoneHigh: 'rgba(168, 230, 206, 0.25)',
    zoneMedGreen: 'rgba(168, 230, 206, 0.12)',
    lineHigh: 'rgba(107, 196, 160, 0.45)',
    lineMed: 'rgba(200, 175, 100, 0.35)',
    particleColors: ['#D4C4F5', '#C0ADF0', '#A8E6CE', '#9B7EDC', '#7DD4B3'],
    textMuted: '#BBA8D9',
};

// ==================== INITIALIZATION ====================
function initGame() {
    game.canvas = document.getElementById('gameCanvas');
    game.ctx = game.canvas.getContext('2d');

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    game.ball.x = game.canvas.width / 2;
    game.ball.y = game.canvas.height - 100;
    game.ball.targetY = game.ball.y;
    game.time = 0;

    animate();
}

function resizeCanvas() {
    const container = game.canvas.parentElement;
    game.canvas.width = container.clientWidth;
    game.canvas.height = 460;
}

// ==================== UPDATE ====================
function updateGame(concentrationScore) {
    game.score = concentrationScore;

    if (concentrationScore > game.peakScore) {
        game.peakScore = concentrationScore;
        document.getElementById('peakScore').textContent = Math.round(game.peakScore);
    }

    document.getElementById('concentrationDisplay').textContent = Math.round(concentrationScore);

    const maxY = game.canvas.height - 50;
    const minY = 50;
    game.ball.targetY = maxY - ((concentrationScore / 100) * (maxY - minY));

    // Spawn particles when focusing
    if (concentrationScore >= 65 && Math.random() < 0.35) {
        createParticles(game.ball.x, game.ball.y);
    }

    updateGameTip(concentrationScore);
}

function updateGameTip(score) {
    const tipEl = document.getElementById('gameTip');
    if (score >= 70) {
        tipEl.innerHTML = '🌿 <span>Beautiful focus — you\'re in the flow!</span>';
    } else if (score >= 40) {
        tipEl.innerHTML = '☁️ <span>Gently settling in… keep going</span>';
    } else {
        tipEl.innerHTML = '🫧 <span>Breathe and let your mind settle</span>';
    }
}

// ==================== PARTICLES ====================
function createParticles(x, y) {
    for (let i = 0; i < 3; i++) {
        game.particles.push({
            x: x + (Math.random() - 0.5) * 40,
            y: y + (Math.random() - 0.5) * 20,
            vx: (Math.random() - 0.5) * 1.5,
            vy: -Math.random() * 2 - 0.5,
            radius: Math.random() * 5 + 3,
            color: PALETTE.particleColors[Math.floor(Math.random() * PALETTE.particleColors.length)],
            alpha: 0.8,
            life: 70
        });
    }
}

function updateParticles() {
    game.particles = game.particles.filter(p => {
        p.x += p.vx;
        p.y += p.vy;
        p.vy -= 0.01; // gently float upward
        p.alpha -= 0.012;
        p.radius *= 0.997;
        p.life--;
        return p.life > 0 && p.alpha > 0;
    });
}

function drawParticles() {
    game.particles.forEach(p => {
        game.ctx.save();
        game.ctx.globalAlpha = p.alpha;
        game.ctx.fillStyle = p.color;
        game.ctx.beginPath();
        game.ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        game.ctx.fill();
        game.ctx.restore();
    });
}

// ==================== DRAWING ====================
function draw() {
    const ctx = game.ctx;
    const w = game.canvas.width;
    const h = game.canvas.height;
    game.time += 0.01;

    // --- background gradient (light) ---
    const bgGrad = ctx.createLinearGradient(0, 0, 0, h);
    bgGrad.addColorStop(0, PALETTE.bgTop);
    bgGrad.addColorStop(1, PALETTE.bgBot);
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, w, h);

    // --- soft vertical guide path ---
    const pathW = 110;
    const pathGrad = ctx.createLinearGradient(0, 0, 0, h);
    pathGrad.addColorStop(0, PALETTE.zoneHigh);
    pathGrad.addColorStop(0.5, PALETTE.pathFill);
    pathGrad.addColorStop(1, 'rgba(212, 196, 245, 0.08)');
    ctx.fillStyle = pathGrad;

    // Rounded path
    const px = w / 2 - pathW / 2;
    ctx.beginPath();
    ctx.roundRect(px, 10, pathW, h - 20, 20);
    ctx.fill();

    // Path edges
    ctx.strokeStyle = PALETTE.pathEdge;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.roundRect(px, 10, pathW, h - 20, 20);
    ctx.stroke();

    // --- zone lines (subtle, dashed) ---
    ctx.setLineDash([6, 8]);
    ctx.lineWidth = 1;

    // High focus line
    const highY = h * 0.3;
    ctx.strokeStyle = PALETTE.lineHigh;
    ctx.beginPath();
    ctx.moveTo(px + 10, highY);
    ctx.lineTo(px + pathW - 10, highY);
    ctx.stroke();

    // Medium focus line
    const medY = h * 0.6;
    ctx.strokeStyle = PALETTE.lineMed;
    ctx.beginPath();
    ctx.moveTo(px + 10, medY);
    ctx.lineTo(px + pathW - 10, medY);
    ctx.stroke();

    ctx.setLineDash([]);

    // --- smooth ball movement (lerp) ---
    game.ball.y += (game.ball.targetY - game.ball.y) * 0.08;

    // --- ball glow ---
    const glowStrength = Math.min(game.score / 100, 1);
    const glowSize = 30 + glowStrength * 30;
    const glowGrad = ctx.createRadialGradient(
        game.ball.x, game.ball.y, game.ball.radius * 0.5,
        game.ball.x, game.ball.y, glowSize
    );
    glowGrad.addColorStop(0, `rgba(155, 126, 220, ${0.15 + glowStrength * 0.2})`);
    glowGrad.addColorStop(0.6, `rgba(168, 230, 206, ${0.08 + glowStrength * 0.1})`);
    glowGrad.addColorStop(1, 'rgba(155, 126, 220, 0)');
    ctx.fillStyle = glowGrad;
    ctx.beginPath();
    ctx.arc(game.ball.x, game.ball.y, glowSize, 0, Math.PI * 2);
    ctx.fill();

    // --- ball body ---
    const ballGrad = ctx.createRadialGradient(
        game.ball.x - 6, game.ball.y - 6, 0,
        game.ball.x, game.ball.y, game.ball.radius
    );

    // Color-shift based on score: lavender → mint green
    if (game.score >= 70) {
        ballGrad.addColorStop(0, '#C4E8D7');
        ballGrad.addColorStop(1, '#7DD4B3');
    } else if (game.score >= 40) {
        ballGrad.addColorStop(0, '#D4C4F5');
        ballGrad.addColorStop(1, '#B89EE8');
    } else {
        ballGrad.addColorStop(0, '#E0D4F5');
        ballGrad.addColorStop(1, '#C0ADF0');
    }

    ctx.fillStyle = ballGrad;
    ctx.beginPath();
    ctx.arc(game.ball.x, game.ball.y, game.ball.radius, 0, Math.PI * 2);
    ctx.fill();

    // Ball highlight (glassy)
    const hlGrad = ctx.createRadialGradient(
        game.ball.x - 7, game.ball.y - 8, 0,
        game.ball.x, game.ball.y, game.ball.radius
    );
    hlGrad.addColorStop(0, 'rgba(255, 255, 255, 0.65)');
    hlGrad.addColorStop(0.5, 'rgba(255, 255, 255, 0.15)');
    hlGrad.addColorStop(1, 'rgba(255, 255, 255, 0)');
    ctx.fillStyle = hlGrad;
    ctx.beginPath();
    ctx.arc(game.ball.x, game.ball.y, game.ball.radius, 0, Math.PI * 2);
    ctx.fill();

    // --- soft ball shadow ---
    ctx.fillStyle = 'rgba(155, 126, 220, 0.08)';
    ctx.beginPath();
    ctx.ellipse(game.ball.x, game.ball.y + game.ball.radius + 8,
        game.ball.radius * 0.7, 4, 0, 0, Math.PI * 2);
    ctx.fill();

    // --- particles ---
    drawParticles();
}

// ==================== ANIMATION LOOP ====================
function animate() {
    draw();
    updateParticles();
    game.animationFrame = requestAnimationFrame(animate);
}

// Export
window.initGame = initGame;
window.updateGame = updateGame;
