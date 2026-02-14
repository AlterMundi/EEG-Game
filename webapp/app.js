/**
 * Neurofeedback Focus Game - Main Application Logic
 * Handles WebSocket communication, state management, and session control
 */

// ==================== CONFIGURATION ====================
const WEBSOCKET_URL = 'ws://localhost:8765';
const CALIBRATION_DURATION = 60; // 1 minute
const HIGH_FOCUS_THRESHOLD = 70; // Score above this = high focus

// ==================== STATE ====================
class AppState {
    constructor() {
        this.currentScreen = 'start';
        this.sessionType = null; // 'baseline' or 'post-therapy'
        this.isCalibrating = false;
        this.isGameActive = false;
        this.sessionStartTime = null;
        this.currentSession = null;
    }
}

class Session {
    constructor(type) {
        this.type = type; // 'baseline' or 'post-therapy'
        this.startTime = new Date();
        this.endTime = null;
        this.scores = [];
        this.timestamps = [];
        this.avgScore = 0;
        this.peakScore = 0;
        this.highFocusTime = 0; // seconds spent above threshold

        // Raw EEG data
        this.bandPowers = []; // Array of {theta, alpha, beta, smr, gamma, delta}
        this.components = []; // Array of {beta_alpha, smr, inv_theta_beta}
    }

    addScore(score, timestamp, bandPowers = null, components = null) {
        this.scores.push(score);
        this.timestamps.push(timestamp);

        // Store raw EEG data if provided
        if (bandPowers) {
            this.bandPowers.push(bandPowers);
        }
        if (components) {
            this.components.push(components);
        }
    }

    finalize() {
        this.endTime = new Date();

        // Calculate average
        if (this.scores.length > 0) {
            this.avgScore = this.scores.reduce((a, b) => a + b, 0) / this.scores.length;
            this.peakScore = Math.max(...this.scores);

            // Calculate high focus time
            this.highFocusTime = this.scores.filter(s => s >= HIGH_FOCUS_THRESHOLD).length * 0.5; // samples * interval
        }
    }

    getDuration() {
        const end = this.endTime || new Date();
        return Math.floor((end - this.startTime) / 1000); // seconds
    }

    toJSON() {
        return {
            type: this.type,
            startTime: this.startTime.toISOString(),
            endTime: this.endTime?.toISOString(),
            duration: this.getDuration(),
            avgScore: Math.round(this.avgScore * 10) / 10,
            peakScore: Math.round(this.peakScore * 10) / 10,
            highFocusTime: this.highFocusTime,
            dataPoints: this.scores.length,
            scores: this.scores,
            timestamps: this.timestamps,
            bandPowers: this.bandPowers,
            components: this.components
        };
    }
}

// Global state
const appState = new AppState();
let websocket = null;
let reconnectTimer = null;

// ==================== WEBSOCKET CONNECTION ====================
function connectWebSocket() {
    try {
        websocket = new WebSocket(WEBSOCKET_URL);

        websocket.onopen = () => {
            console.log('WebSocket connected');
            updateConnectionStatus(true);
            clearTimeout(reconnectTimer);
        };

        websocket.onmessage = (event) => {
            handleWebSocketMessage(JSON.parse(event.data));
        };

        websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            updateConnectionStatus(false);
        };

        websocket.onclose = () => {
            console.log('WebSocket disconnected');
            updateConnectionStatus(false);

            // Attempt to reconnect after 3 seconds
            reconnectTimer = setTimeout(() => {
                console.log('Attempting to reconnect...');
                connectWebSocket();
            }, 3000);
        };
    } catch (error) {
        console.error('Failed to create WebSocket:', error);
        updateConnectionStatus(false);
    }
}

function updateConnectionStatus(connected) {
    const statusEl = document.getElementById('connectionStatus');
    if (connected) {
        statusEl.textContent = 'Connected';
        statusEl.className = 'status-value status-connected';
    } else {
        statusEl.textContent = 'Disconnected';
        statusEl.className = 'status-value status-disconnected';
    }
}

function sendWebSocketMessage(data) {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify(data));
    } else {
        console.warn('WebSocket not connected');
    }
}

// ==================== MESSAGE HANDLERS ====================
function handleWebSocketMessage(message) {
    switch (message.type) {
        case 'connected':
            console.log('Server says:', message.message);
            break;

        case 'eeg_data':
            handleEEGData(message);
            break;

        case 'calibration_started':
            console.log('Calibration started on server');
            break;

        case 'calibration_finished':
            console.log('Calibration complete:', message.baseline);
            break;

        case 'calibration_progress':
            updateCalibrationProgress(message.samples_collected);
            break;

        default:
            console.log('Unknown message type:', message.type);
    }
}

function handleEEGData(data) {
    // Update signal quality display
    const qualityEl = document.getElementById('signalQuality');
    qualityEl.textContent = data.signal_quality.charAt(0).toUpperCase() + data.signal_quality.slice(1);
    qualityEl.className = `status-value status-${data.signal_quality}`;

    // If game is active, update game with concentration score AND raw data
    if (appState.isGameActive && appState.currentSession) {
        const score = data.concentration_score;
        const bandPowers = data.band_powers || null;
        const components = data.components || null;

        appState.currentSession.addScore(score, data.timestamp, bandPowers, components);

        // Update game visualization
        if (window.updateGame) {
            window.updateGame(score);
        }
    }
}

// ==================== SCREEN NAVIGATION ====================
function showScreen(screenName) {
    // Hide all screens
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });

    // Show target screen
    const targetScreen = document.getElementById(screenName + 'Screen');
    if (targetScreen) {
        targetScreen.classList.add('active');
        appState.currentScreen = screenName;
    }
}

// ==================== CALIBRATION ====================
let calibrationInterval = null;
let calibrationTimeLeft = CALIBRATION_DURATION;

function startCalibration(sessionType) {
    appState.sessionType = sessionType;
    document.getElementById('sessionType').textContent = sessionType === 'baseline' ? 'Baseline' : 'Post-Therapy';

    showScreen('calibration');
    appState.isCalibrating = true;
    calibrationTimeLeft = CALIBRATION_DURATION;

    // Tell server to start calibration
    sendWebSocketMessage({ command: 'start_calibration' });

    // Start countdown timer
    calibrationInterval = setInterval(() => {
        calibrationTimeLeft--;
        updateCalibrationTimer();

        if (calibrationTimeLeft <= 0) {
            finishCalibration();
        }
    }, 1000);
}

function updateCalibrationTimer() {
    const minutes = Math.floor(calibrationTimeLeft / 60);
    const seconds = calibrationTimeLeft % 60;
    document.getElementById('calibrationTimer').textContent =
        `${minutes}:${seconds.toString().padStart(2, '0')}`;

    // Update progress circle
    const progress = 1 - (calibrationTimeLeft / CALIBRATION_DURATION);
    const circumference = 2 * Math.PI * 90;
    const offset = circumference * (1 - progress);
    document.getElementById('progressCircle').style.strokeDashoffset = offset;
}

function updateCalibrationProgress(sampleCount) {
    document.getElementById('sampleCount').textContent = sampleCount;
}

function finishCalibration() {
    clearInterval(calibrationInterval);
    appState.isCalibrating = false;

    // Tell server calibration is done
    sendWebSocketMessage({ command: 'finish_calibration' });

    // Start game
    setTimeout(() => {
        startGame();
    }, 500);
}

// ==================== GAME SESSION ====================
let gameInterval = null;
let gameStartTime = null;

function startGame() {
    showScreen('game');

    appState.isGameActive = true;
    appState.currentSession = new Session(appState.sessionType);
    gameStartTime = Date.now();

    // Initialize game canvas
    if (window.initGame) {
        window.initGame();
    }

    // Start game timer
    gameInterval = setInterval(updateGameTimer, 1000);
}

function updateGameTimer() {
    const elapsed = Math.floor((Date.now() - gameStartTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    document.getElementById('gameTime').textContent =
        `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

function endGame() {
    clearInterval(gameInterval);
    appState.isGameActive = false;

    // Finalize session data
    appState.currentSession.finalize();

    // Save to localStorage
    saveSession(appState.currentSession);

    // Show results
    showResults();
}

// ==================== RESULTS ====================
function showResults() {
    showScreen('results');

    const session = appState.currentSession;

    // Update result cards
    document.getElementById('avgScore').textContent = Math.round(session.avgScore);
    document.getElementById('peakScoreResult').textContent = Math.round(session.peakScore);

    const duration = session.getDuration();
    const minutes = Math.floor(duration / 60);
    const seconds = duration % 60;
    document.getElementById('durationResult').textContent =
        `${minutes}m ${seconds}s`;

    const highFocusMinutes = Math.floor(session.highFocusTime / 60);
    const highFocusSeconds = Math.floor(session.highFocusTime % 60);
    document.getElementById('highFocusTime').textContent =
        `${highFocusMinutes}m ${highFocusSeconds}s`;

    // Draw results chart
    if (window.drawResultsChart) {
        window.drawResultsChart(session);
    }
}

// ==================== DATA PERSISTENCE ====================
function saveSession(session) {
    const sessions = getSavedSessions();
    sessions.push(session.toJSON());
    localStorage.setItem('neurofeedback_sessions', JSON.stringify(sessions));
}

function getSavedSessions() {
    const data = localStorage.getItem('neurofeedback_sessions');
    return data ? JSON.parse(data) : [];
}

function exportCSV() {
    const session = appState.currentSession;
    if (!session) return;

    // Create CSV content with extended data
    let csv = 'Timestamp,Concentration Score,Delta,Theta,Alpha,SMR,Beta,Gamma,Beta/Alpha,SMR Power,Inv Theta/Beta\n';
    session.timestamps.forEach((timestamp, i) => {
        const bp = session.bandPowers[i] || {};
        const comp = session.components[i] || {};
        csv += `${timestamp},${session.scores[i].toFixed(2)},`;
        csv += `${(bp.delta || 0).toFixed(4)},`;
        csv += `${(bp.theta || 0).toFixed(4)},`;
        csv += `${(bp.alpha || 0).toFixed(4)},`;
        csv += `${(bp.smr || 0).toFixed(4)},`;
        csv += `${(bp.beta || 0).toFixed(4)},`;
        csv += `${(bp.gamma || 0).toFixed(4)},`;
        csv += `${(comp.beta_alpha_ratio || 0).toFixed(4)},`;
        csv += `${(comp.smr_power || 0).toFixed(4)},`;
        csv += `${(comp.inv_theta_beta || 0).toFixed(4)}\n`;
    });

    // Add summary
    csv += `\n\nSession Summary\n`;
    csv += `Type,${session.type}\n`;
    csv += `Duration,${session.getDuration()} seconds\n`;
    csv += `Average Score,${session.avgScore.toFixed(1)}\n`;
    csv += `Peak Score,${session.peakScore.toFixed(1)}\n`;
    csv += `High Focus Time,${session.highFocusTime.toFixed(0)} seconds\n`;
    csv += `Data Points,${session.scores.length}\n`;

    downloadFile(csv, `neurofeedback_${session.type}_${new Date().toISOString()}.csv`, 'text/csv');
}

function exportJSON() {
    const session = appState.currentSession;
    if (!session) return;

    const json = JSON.stringify(session.toJSON(), null, 2);
    downloadFile(json, `neurofeedback_${session.type}_${new Date().toISOString()}.json`, 'application/json');
}

function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
}

// ==================== COMPARISON ====================
function loadComparisonView() {
    showScreen('comparison');

    const sessions = getSavedSessions();
    const baselineSessions = sessions.filter(s => s.type === 'baseline');
    const postTherapySessions = sessions.filter(s => s.type === 'post-therapy');

    // Populate selectors
    populateSelector('baselineSelect', baselineSessions);
    populateSelector('postTherapySelect', postTherapySessions);

    // Hide results initially
    document.getElementById('comparisonResults').classList.add('hidden');
}

function populateSelector(id, sessions) {
    const select = document.getElementById(id);
    select.innerHTML = '<option value="">-- Select Session --</option>';

    sessions.forEach((session, index) => {
        const option = document.createElement('option');
        option.value = index;
        const date = new Date(session.startTime).toLocaleString();
        option.textContent = `${date} (Avg: ${session.avgScore.toFixed(1)})`;
        select.appendChild(option);
    });
}

function compareSessions() {
    const baselineIdx = document.getElementById('baselineSelect').value;
    const postTherapyIdx = document.getElementById('postTherapySelect').value;

    if (baselineIdx === '' || postTherapyIdx === '') {
        alert('Please select both baseline and post-therapy sessions');
        return;
    }

    const sessions = getSavedSessions();
    const baselineSessions = sessions.filter(s => s.type === 'baseline');
    const postTherapySessions = sessions.filter(s => s.type === 'post-therapy');

    const baseline = baselineSessions[baselineIdx];
    const postTherapy = postTherapySessions[postTherapyIdx];

    // Show comparison results
    document.getElementById('comparisonResults').classList.remove('hidden');

    // Calculate improvement
    const improvement = ((postTherapy.avgScore - baseline.avgScore) / baseline.avgScore) * 100;
    const improvementEl = document.getElementById('improvementPercent');
    improvementEl.textContent = (improvement >= 0 ? '+' : '') + improvement.toFixed(1) + '%';
    improvementEl.style.color = improvement >= 0 ? 'var(--status-good)' : 'var(--status-poor)';

    // Update comparison values
    document.getElementById('baselineAvg').textContent = baseline.avgScore.toFixed(1);
    document.getElementById('postTherapyAvg').textContent = postTherapy.avgScore.toFixed(1);
    document.getElementById('baselineHighFocus').textContent = formatTime(baseline.highFocusTime);
    document.getElementById('postTherapyHighFocus').textContent = formatTime(postTherapy.highFocusTime);

    // Draw comparison chart
    if (window.drawComparisonChart) {
        window.drawComparisonChart(baseline, postTherapy);
    }
}

function formatTime(seconds) {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}m ${s}s`;
}

// ==================== EVENT LISTENERS ====================
document.addEventListener('DOMContentLoaded', () => {
    // Disclaimer modal
    const disclaimerCheck = document.getElementById('disclaimerCheck');
    const disclaimerAccept = document.getElementById('disclaimerAccept');

    disclaimerCheck.addEventListener('change', (e) => {
        disclaimerAccept.disabled = !e.target.checked;
    });

    disclaimerAccept.addEventListener('click', () => {
        document.getElementById('disclaimerModal').style.display = 'none';
        document.getElementById('app').classList.remove('hidden');

        // Connect WebSocket
        connectWebSocket();
    });

    // Session selection
    document.querySelectorAll('.session-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const sessionType = btn.dataset.session;
            startCalibration(sessionType);
        });
    });

    // View comparison button
    document.getElementById('viewComparisonBtn').addEventListener('click', loadComparisonView);

    // End session button
    document.getElementById('endSessionBtn').addEventListener('click', () => {
        if (confirm('Are you sure you want to end this session?')) {
            endGame();
        }
    });

    // Export buttons
    document.getElementById('exportCSV').addEventListener('click', exportCSV);
    document.getElementById('exportJSON').addEventListener('click', exportJSON);

    // New session button
    document.getElementById('newSessionBtn').addEventListener('click', () => {
        showScreen('start');
    });

    // Comparison controls
    document.getElementById('compareBtn').addEventListener('click', compareSessions);
    document.getElementById('backToStartBtn').addEventListener('click', () => {
        showScreen('start');
    });
});
