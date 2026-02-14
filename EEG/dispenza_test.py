import numpy as np
from scipy.signal import welch, coherence
from pythonosc import dispatcher
from pythonosc import osc_server
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading
import time

# ------------------- CONFIGURATION -------------------
fs = 256                  # Muse 2 sampling rate
MAX_POINTS = 2000         # ~7.8 seconds of data at 256 Hz
WINDOW_SIZE = 1024        # Analysis window (~4 seconds) – good compromise for stability
UPDATE_INTERVAL = 1.0     # How often to analyze (seconds)

# Frequency bands (Hz)
BANDS = {
    'delta': (0.5,  4),
    'theta': (4,    8),
    'alpha': (8,   13),
    'beta':  (13,  30),
    'gamma': (30,  44)
}

# Thresholds – tune these based on your own baseline data!
THRESHOLDS = {
    'theta_increase_factor': 1.3,         # e.g., 30% above baseline
    'gamma_increase_factor': 1.15,        # 15% above baseline
    'theta_beta_ratio': 2.0,              # Higher = deeper meditation
    'theta_coherence': 0.75               # High synchronization
}

# Global data storage
eeg_data = {ch: [] for ch in ['TP9', 'AF7', 'AF8', 'TP10']}
channel_order = ['TP9', 'AF7', 'AF8', 'TP10']  # indices 0,1,2,3

# Baseline (you'll need to record and average this first)
baseline_powers = {band: 0.0 for band in BANDS}  # Will be set later

# ------------------- ANALYSIS FUNCTIONS -------------------
def compute_band_power(signal, fs, low_freq, high_freq):
    """Compute average power in a frequency band using Welch PSD"""
    if len(signal) < fs:  # Not enough data yet
        return 0.0
    freqs, psd = welch(signal, fs=fs, nperseg=fs*2, noverlap=fs//2)
    band_idx = (freqs >= low_freq) & (freqs <= high_freq)
    return np.mean(psd[band_idx]) if np.any(band_idx) else 0.0

def analyze_window():
    """Analyze the most recent WINDOW_SIZE samples"""
    if all(len(eeg_data[ch]) >= WINDOW_SIZE for ch in channel_order):
        # Get latest window (shape: n_channels, n_samples)
        window = np.array([eeg_data[ch][-WINDOW_SIZE:] for ch in channel_order])
        
        # Compute power for each band, averaged across channels
        current_powers = {}
        for band, (low, high) in BANDS.items():
            band_powers = [compute_band_power(window[i], fs, low, high) for i in range(4)]
            current_powers[band] = np.mean(band_powers)
        
        # Ratios
        theta_beta_ratio = current_powers['theta'] / (current_powers['beta'] + 1e-10)
        
        # Theta coherence (frontal: AF7–AF8, indices 1 and 2)
        f, coh = coherence(window[1], window[2], fs=fs, nperseg=fs*2)
        theta_coh_idx = (f >= 4) & (f <= 8)
        theta_coherence = np.mean(coh[theta_coh_idx]) if np.any(theta_coh_idx) else 0.0
        
        # Check for transcendent markers
        messages = []
        if current_powers['theta'] > baseline_powers['theta'] * THRESHOLDS['theta_increase_factor']:
            messages.append(f"↑ Elevated theta ({current_powers['theta']:.2f} vs baseline {baseline_powers['theta']:.2f})")
        if current_powers['gamma'] > baseline_powers['gamma'] * THRESHOLDS['gamma_increase_factor']:
            messages.append(f"↑ Gamma surge ({current_powers['gamma']:.2f} vs baseline {baseline_powers['gamma']:.2f})")
        if theta_beta_ratio > THRESHOLDS['theta_beta_ratio']:
            messages.append(f"High theta/beta ratio: {theta_beta_ratio:.2f}")
        if theta_coherence > THRESHOLDS['theta_coherence']:
            messages.append(f"High theta coherence: {theta_coherence:.2f}")
        
        if messages:
            print(f"[{time.strftime('%H:%M:%S')}] " + " | ".join(messages))
        
        return current_powers, theta_beta_ratio, theta_coherence
    return None, None, None

# ------------------- OSC HANDLER -------------------
def eeg_handler(address, *args):
    channels = ['TP9', 'AF7', 'AF8', 'TP10']
    for ch, val in zip(channels, args[:4]):
        eeg_data[ch].append(val)
        if len(eeg_data[ch]) > MAX_POINTS:
            eeg_data[ch].pop(0)  # Keep only last MAX_POINTS

# ------------------- SERVER SETUP -------------------
disp = dispatcher.Dispatcher()
disp.map("/muse/eeg", eeg_handler)

def start_server():
    server = osc_server.ThreadingOSCUDPServer(("0.0.0.0", 5000), disp)
    print("Listening for OSC on port 5000...")
    server.serve_forever()

thread = threading.Thread(target=start_server, daemon=True)
thread.start()

# ------------------- PLOTTING & LIVE ANALYSIS -------------------
fig, ax = plt.subplots(figsize=(10, 6))
lines = {}
colors = ['r', 'g', 'b', 'm']
for i, ch in enumerate(eeg_data.keys()):
    lines[ch], = ax.plot([], [], color=colors[i], label=ch)
ax.set_xlim(0, MAX_POINTS)
ax.set_ylim(-1000, 1000)
ax.set_xlabel("Samples")
ax.set_ylabel("Amplitude (μV)")
ax.legend()
ax.grid(True)
ax.set_title("Live Raw EEG from Muse 2 – Transcendent State Detection")

def update(frame):
    # Update plot
    for ch, line in lines.items():
        y = eeg_data[ch]
        x = range(len(y))
        line.set_data(x, y)
    
    # Auto-scale y-axis
    if any(eeg_data.values()):
        all_vals = np.concatenate(list(eeg_data.values()))
        ax.set_ylim(min(all_vals) - 100, max(all_vals) + 100)
    
    # Run analysis every UPDATE_INTERVAL seconds
    if frame % int(UPDATE_INTERVAL * 20) == 0:  # ~every second at 50ms interval
        powers, theta_beta, coh = analyze_window()
        if powers:
            title = (f"Live EEG | Theta: {powers['theta']:.2f} | Gamma: {powers['gamma']:.2f} | "
                     f"θ/β: {theta_beta:.2f} | Frontal θ Coh: {coh:.2f}")
            ax.set_title(title)
    
    return list(lines.values())

ani = FuncAnimation(fig, update, interval=50, blit=True)

# Optional: Record baseline first (e.g., 60 seconds of relaxed eyes-closed)
print("Collecting baseline for 30 seconds... Relax, eyes closed.")
time.sleep(30)
for band, (low, high) in BANDS.items():
    powers = [compute_band_power(eeg_data[ch][-WINDOW_SIZE:], fs, low, high) 
              for ch in channel_order]
    baseline_powers[band] = np.mean(powers)
print("Baseline recorded:")
for band, val in baseline_powers.items():
    print(f"  {band}: {val:.2f}")

plt.show()
