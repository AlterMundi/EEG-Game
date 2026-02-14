"""
WebSocket Server for EEG Neurofeedback Game
Bridges OSC data from Mind Monitor to web clients via WebSocket

This server receives EEG data via OSC, computes a scientifically-backed
concentration score using frontal electrode activity, and broadcasts
real-time metrics to connected web clients.

Concentration Algorithm:
- 50% Beta/Alpha Engagement Index (attention marker)
- 30% SMR Power 12-15 Hz (focus marker)
- 20% Inverted Theta/Beta Ratio (executive control)
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Set
import numpy as np
from scipy.signal import welch
from pythonosc import dispatcher, osc_server
import websockets

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== CONFIGURATION ====================
OSC_IP = "0.0.0.0"
OSC_PORT = 5000
WEBSOCKET_PORT = 8765
SAMPLING_RATE = 256  # Muse 2 sampling rate (Hz)
WINDOW_SIZE = 1024   # ~4 seconds of data for analysis
UPDATE_INTERVAL = 0.5  # Send updates every 0.5 seconds
SMOOTHING_FACTOR = 0.7  # Temporal smoothing (0-1, higher = more smoothing)

# Frequency bands (Hz)
BANDS = {
    'delta': (0.5, 4),
    'theta': (4, 8),
    'alpha': (8, 13),
    'smr': (12, 15),    # Sensorimotor Rhythm
    'beta': (13, 30),
    'gamma': (30, 44)
}

# Concentration score weights
WEIGHTS = {
    'beta_alpha': 0.5,      # Engagement index
    'smr': 0.3,             # Focus marker
    'inv_theta_beta': 0.2   # Executive control
}

# ==================== GLOBAL STATE ====================
eeg_data = {ch: [] for ch in ['TP9', 'AF7', 'AF8', 'TP10']}
frontal_channels = ['AF7', 'AF8']  # Focus on frontal electrodes
baseline_powers = {}
calibration_mode = False
calibration_samples = []
last_concentration_score = 0.0

# WebSocket clients
connected_clients: Set[websockets.WebSocketServerProtocol] = set()

# ==================== EEG ANALYSIS FUNCTIONS ====================

def compute_band_power(signal: np.ndarray, fs: int, low_freq: float, high_freq: float) -> float:
    """Compute average power in a frequency band using Welch's method"""
    if len(signal) < fs:
        return 0.0
    
    try:
        freqs, psd = welch(signal, fs=fs, nperseg=min(len(signal), fs*2), 
                          noverlap=fs//2, scaling='density')
        band_idx = (freqs >= low_freq) & (freqs <= high_freq)
        
        if not np.any(band_idx):
            return 0.0
            
        return np.mean(psd[band_idx])
    except Exception as e:
        logger.error(f"Error computing band power: {e}")
        return 0.0


def analyze_eeg_window() -> Dict:
    """
    Analyze current EEG window and compute concentration metrics
    Returns dict with band powers and concentration score
    """
    global last_concentration_score
    
    # Check if we have enough data
    if not all(len(eeg_data[ch]) >= WINDOW_SIZE for ch in eeg_data.keys()):
        return None
    
    # Get latest window for frontal channels (AF7, AF8)
    frontal_data = [np.array(eeg_data[ch][-WINDOW_SIZE:]) for ch in frontal_channels]
    
    # Compute band powers averaged across frontal channels
    band_powers = {}
    for band, (low, high) in BANDS.items():
        powers = [compute_band_power(signal, SAMPLING_RATE, low, high) 
                 for signal in frontal_data]
        band_powers[band] = np.mean(powers)
    
    # Calculate concentration components
    # 1. Beta/Alpha Engagement Index
    beta_alpha_ratio = band_powers['beta'] / (band_powers['alpha'] + 1e-10)
    
    # 2. SMR Power (normalized)
    smr_power = band_powers['smr']
    
    # 3. Inverted Theta/Beta Ratio (lower theta/beta = better focus)
    theta_beta_ratio = band_powers['theta'] / (band_powers['beta'] + 1e-10)
    inv_theta_beta = 1.0 / (theta_beta_ratio + 1e-10)
    
    # Normalize against baseline if available
    if baseline_powers:
        beta_alpha_ratio = beta_alpha_ratio / (baseline_powers.get('beta_alpha', 1.0) + 1e-10)
        smr_power = smr_power / (baseline_powers.get('smr', 1.0) + 1e-10)
        inv_theta_beta = inv_theta_beta / (baseline_powers.get('inv_theta_beta', 1.0) + 1e-10)
    
    # Composite concentration score (weighted combination)
    raw_score = (
        WEIGHTS['beta_alpha'] * beta_alpha_ratio +
        WEIGHTS['smr'] * smr_power +
        WEIGHTS['inv_theta_beta'] * inv_theta_beta
    )
    
    # Normalize to 0-100 scale (assuming baseline normalized to ~1.0)
    # Values above baseline will be > 50, below baseline < 50
    concentration_score = np.clip(raw_score * 50, 0, 100)
    
    # Apply temporal smoothing to reduce jitter
    concentration_score = (SMOOTHING_FACTOR * last_concentration_score + 
                          (1 - SMOOTHING_FACTOR) * concentration_score)
    last_concentration_score = concentration_score
    
    # Signal quality (based on data variability and range)
    signal_quality = calculate_signal_quality(frontal_data)
    
    return {
        'timestamp': datetime.now().isoformat(),
        'band_powers': {k: float(v) for k, v in band_powers.items()},
        'concentration_score': float(concentration_score),
        'components': {
            'beta_alpha_ratio': float(beta_alpha_ratio),
            'smr_power': float(smr_power),
            'inv_theta_beta': float(inv_theta_beta)
        },
        'signal_quality': signal_quality
    }


def calculate_signal_quality(signals: List[np.ndarray]) -> str:
    """
    Estimate signal quality based on amplitude and variance
    Returns: 'good', 'fair', or 'poor'
    """
    try:
        all_data = np.concatenate(signals)
        std_dev = np.std(all_data)
        amplitude = np.max(np.abs(all_data))
        
        # Good signal: reasonable amplitude and variance
        if 50 < amplitude < 1500 and 10 < std_dev < 500:
            return 'good'
        # Fair signal: moderate quality
        elif 20 < amplitude < 2000 and 5 < std_dev < 800:
            return 'fair'
        else:
            return 'poor'
    except:
        return 'unknown'


def start_calibration():
    """Start baseline calibration period"""
    global calibration_mode, calibration_samples, baseline_powers
    calibration_mode = True
    calibration_samples = []
    baseline_powers = {}
    logger.info("Baseline calibration started")


def finish_calibration():
    """Complete calibration and compute baseline values"""
    global calibration_mode, baseline_powers
    
    if not calibration_samples:
        logger.warning("No calibration data collected")
        calibration_mode = False
        return
    
    # Average all calibration measurements
    baseline_powers = {
        'beta_alpha': np.mean([s['beta_alpha'] for s in calibration_samples]),
        'smr': np.mean([s['smr'] for s in calibration_samples]),
        'inv_theta_beta': np.mean([s['inv_theta_beta'] for s in calibration_samples])
    }
    
    calibration_mode = False
    logger.info(f"Baseline calibration complete: {baseline_powers}")


# ==================== OSC HANDLERS ====================

def eeg_handler(address: str, *args):
    """Handle incoming OSC EEG data"""
    channels = ['TP9', 'AF7', 'AF8', 'TP10']
    
    for ch, val in zip(channels, args[:4]):
        eeg_data[ch].append(float(val))
        
        # Keep buffer size manageable
        if len(eeg_data[ch]) > WINDOW_SIZE * 2:
            eeg_data[ch] = eeg_data[ch][-WINDOW_SIZE:]


# ==================== WEBSOCKET HANDLERS ====================

async def handle_websocket_message(websocket, message: str):
    """Handle incoming WebSocket messages from clients"""
    try:
        data = json.loads(message)
        command = data.get('command')
        
        if command == 'start_calibration':
            start_calibration()
            await websocket.send(json.dumps({
                'type': 'calibration_started',
                'message': 'Baseline calibration initiated'
            }))
            
        elif command == 'finish_calibration':
            finish_calibration()
            await websocket.send(json.dumps({
                'type': 'calibration_finished',
                'baseline': baseline_powers,
                'message': 'Baseline calibration complete'
            }))
            
        elif command == 'reset_baseline':
            baseline_powers.clear()
            await websocket.send(json.dumps({
                'type': 'baseline_reset',
                'message': 'Baseline reset successfully'
            }))
            
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON received: {message}")
    except Exception as e:
        logger.error(f"Error handling message: {e}")


async def websocket_handler(websocket):
    """Handle WebSocket connections"""
    connected_clients.add(websocket)
    client_addr = websocket.remote_address
    logger.info(f"Client connected: {client_addr}")
    
    try:
        # Send welcome message
        await websocket.send(json.dumps({
            'type': 'connected',
            'message': 'Connected to EEG WebSocket server',
            'server_time': datetime.now().isoformat()
        }))
        
        # Listen for client messages
        async for message in websocket:
            await handle_websocket_message(websocket, message)
            
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Client disconnected: {client_addr}")
    finally:
        connected_clients.remove(websocket)


async def broadcast_eeg_data():
    """Periodically analyze EEG and broadcast to all connected clients"""
    global calibration_samples
    
    while True:
        await asyncio.sleep(UPDATE_INTERVAL)
        
        if not connected_clients:
            continue
        
        # Analyze current window
        metrics = analyze_eeg_window()
        
        if metrics is None:
            continue
        
        # If calibrating, store sample instead of broadcasting
        if calibration_mode:
            calibration_samples.append({
                'beta_alpha': metrics['components']['beta_alpha_ratio'],
                'smr': metrics['components']['smr_power'],
                'inv_theta_beta': metrics['components']['inv_theta_beta']
            })
            
            # Send calibration progress
            message = json.dumps({
                'type': 'calibration_progress',
                'samples_collected': len(calibration_samples)
            })
        else:
            # Normal operation - send metrics
            message = json.dumps({
                'type': 'eeg_data',
                **metrics
            })
        
        # Broadcast to all connected clients
        if connected_clients:
            await asyncio.gather(
                *[client.send(message) for client in connected_clients],
                return_exceptions=True
            )


# ==================== OSC SERVER (runs in thread) ====================

def start_osc_server():
    """Start OSC server in background thread"""
    disp = dispatcher.Dispatcher()
    disp.map("/muse/eeg", eeg_handler)
    
    server = osc_server.ThreadingOSCUDPServer((OSC_IP, OSC_PORT), disp)
    logger.info(f"OSC server listening on {OSC_IP}:{OSC_PORT}")
    server.serve_forever()


# ==================== MAIN ====================

async def main():
    """Main entry point"""
    # Start OSC server in background
    import threading
    osc_thread = threading.Thread(target=start_osc_server, daemon=True)
    osc_thread.start()
    
    logger.info(f"Starting WebSocket server on port {WEBSOCKET_PORT}")
    
    # Start WebSocket server and broadcast loop
    async with websockets.serve(websocket_handler, "0.0.0.0", WEBSOCKET_PORT):
        await broadcast_eeg_data()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
