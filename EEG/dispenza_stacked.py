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
MAX_POINTS = 2000         # ~7.8 seconds at 256 Hz
WINDOW_SIZE = 1024        # Analysis window (~4 seconds)
UPDATE_INTERVAL = 1.0     # Analyze every second

# Frequency bands (Hz)
BANDS = {
    'delta': (0.5,  4),
    'theta': (4,    8),
    'alpha': (8,   13),
    'beta':  (13,  30),
    'gamma': (30,  44)
}

# Thresholds – tune these based on your baselines!
THRESHOLDS = {
    'theta_increase_factor': 1.3,
    'gamma_increase_factor': 1.15,
    'theta_beta_ratio': 2.0,
    'theta_coherence': 0.75
}

# Global data storage
eeg_data = {ch: [] for ch in ['TP9', 'AF7', 'AF8', 'TP10']}
channel_order = ['TP9', 'AF7', 'AF8', 'TP10']
colors = ['r', 'g', 'b', 'm']

# Baseline powers
baseline_powers = {band: 0.0 for band in BANDS}

# ------------------- ANALYSIS FUNCTIONS -------------------
def compute_band_power(signal, fs, low_freq, high_freq):
    if len(signal) < fs:
        return 0.0
    freqs, psd = welch(signal, fs=fs, nperseg=fs*2, noverlap=fs//2)
    band_idx = (freqs >= low_freq) & (freqs <= high_freq)
    return np.mean(psd[band_idx]) if np.any(band_idx) else 0.0

def analyze_window():
    if all(len(eeg_data[ch]) >= WINDOW_SIZE for ch in channel_order):
        window = np.array([eeg_data[ch][-WINDOW_SIZE:] for ch in channel_order])
        
        # Compute powers
        current_powers = {}
        for band, (low, high) in BANDS.items():
            band_powers = [compute_band_power(window[i], fs, low, high) for i in range(4)]
            current_powers[band] = np.mean(band_powers)
        
        # Ratios & coherence
        theta_beta_ratio = current_powers['theta'] / (current_powers['beta'] + 1e-10)
        f, coh = coherence(window[1], window[2], fs=fs, nperseg=fs*2)  # AF7-AF8
        theta_coh_idx = (f >= 4) & (f <= 8)
        theta_coherence = np.mean(coh[theta_coh_idx]) if np.any(theta_coh_idx) else 0.0
        
        # Detect markers
        messages = []
        if current_powers['theta'] > baseline_powers['theta'] * THRESHOLDS['theta_increase_factor']:
            messages.append(f"↑ Elevated theta ({current_powers['theta']:.2f})")
        if current_powers['gamma'] > baseline_powers['gamma'] * THRESHOLDS['gamma_increase_factor']:
            messages.append(f"↑ Gamma surge ({current_powers['gamma']:.2f})")
        if theta_beta_ratio > THRESHOLDS['theta_beta_ratio']:
            messages.append(f"High θ/β ratio: {theta_beta_ratio:.2f}")
        if theta_coherence > THRESHOLDS['theta_coherence']:
            messages.append(f"High θ coherence: {theta_coherence:.2f}")
        
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
            eeg_data[ch].pop(0)

# ------------------- SERVER SETUP -------------------
disp = dispatcher.Dispatcher()
disp.map("/muse/eeg", eeg_handler)

def start_server():
    server = osc_server.ThreadingOSCUDPServer(("0.0.0.0", 5000), disp)
    print("Listening for OSC on port 5000... (Connect Muse via Mind Monitor or Muse Direct)")
    server.serve_forever()

thread = threading.Thread(target=start_server, daemon=True)
thread.start()

# ------------------- STACKED PLOTTING SETUP -------------------
fig, axes = plt.subplots(4, 1, figsize=(14, 10), sharex=True, 
                         gridspec_kw={'height_ratios': [1]*4, 'hspace': 0.3})

# Initialize lines
lines = {}
for i, ch in enumerate(channel_order):
    lines[ch], = axes[i].plot([], [], color=colors[i], label=ch)
    axes[i].set_ylabel(ch)
    axes[i].grid(True, alpha=0.4)
    axes[i].tick_params(labelleft=True)
    axes[i].yaxis.set_label_position("right")

axes[-1].set_xlabel("Samples")
fig.suptitle("Live Raw EEG from Muse 2 – Stacked Channels (Dispenza Style)", fontsize=16, y=0.98)

# Hide x-ticks on upper plots
for ax in axes[:-1]:
    ax.tick_params(labelbottom=False)

# ------------------- UPDATE FUNCTION -------------------
def update(frame):
    for i, ch in enumerate(channel_order):
        y = np.array(eeg_data[ch])
        x = np.arange(len(y))
        
        # Plot the data
        lines[ch].set_data(x, y)
        
        # Auto-scale each channel independently (this makes small fluctuations visible!)
        if len(y) > 0:
            ymin = np.min(y)
            ymax = np.max(y)
            margin = (ymax - ymin) * 0.15 if (ymax - ymin) > 0 else 50
            axes[i].set_ylim(ymin - margin, ymax + margin)
    
    # Periodic analysis
    if frame % int(UPDATE_INTERVAL * 20) == 0:  # ~every second
        powers, theta_beta, coh = analyze_window()
        if powers:
            title = (f"Live EEG | Theta: {powers['theta']:.2f} | Gamma: {powers['gamma']:.2f} | "
                     f"θ/β: {theta_beta:.2f} | Frontal θ Coh: {coh:.2f}")
            fig.suptitle(title, fontsize=16)
    
    return list(lines.values())

ani = FuncAnimation(fig, update, interval=50, blit=True)

# ------------------- RECORD BASELINE -------------------
print("Collecting baseline for 30 seconds... Relax, eyes closed, no meditation yet.")
time.sleep(30)
for band, (low, high) in BANDS.items():
    powers = [compute_band_power(eeg_data[ch][-WINDOW_SIZE:], fs, low, high) 
              for ch in channel_order]
    baseline_powers[band] = np.mean(powers) if powers else 0.0
print("Baseline recorded! Starting real-time tracking.")
print("Baseline values:")
for band, val in baseline_powers.items():
    print(f"  {band}: {val:.2f}")

plt.show()
