from pythonosc import dispatcher
from pythonosc import osc_server
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import threading

# Global variables for data
eeg_data = {ch: [] for ch in ['TP9', 'AF7', 'AF8', 'TP10']}  # Lists for each channel
MAX_POINTS = 2000  # Show ~8 seconds at 256Hz (Muse 2 raw EEG rate)

# Handler for raw EEG (/muse/eeg)
def eeg_handler(address, *args):
    # args: [TP9, AF7, AF8, TP10, AUX] – we ignore AUX
    channels = ['TP9', 'AF7', 'AF8', 'TP10']
    for ch, val in zip(channels, args[:4]):
        eeg_data[ch].append(val)
        if len(eeg_data[ch]) > MAX_POINTS:
            eeg_data[ch].pop(0)  # Keep only last N points

# Set up dispatcher
disp = dispatcher.Dispatcher()
disp.map("/muse/eeg", eeg_handler)

# Start OSC server in a background thread
def start_server():
    server = osc_server.ThreadingOSCUDPServer(("0.0.0.0", 5000), disp)
    print("Listening for OSC on port 5000...")
    server.serve_forever()

thread = threading.Thread(target=start_server, daemon=True)
thread.start()

# Matplotlib setup
fig, ax = plt.subplots()
lines = {}
colors = ['r', 'g', 'b', 'm']
for i, ch in enumerate(eeg_data.keys()):
    lines[ch], = ax.plot([], [], color=colors[i], label=ch)

ax.set_xlim(0, MAX_POINTS)
ax.set_ylim(-1000, 1000)  # Adjust based on typical EEG range (~ -500 to 500 μV)
ax.set_xlabel("Samples")
ax.set_ylabel("Amplitude (μV)")
ax.legend()
ax.grid(True)
ax.set_title("Live Raw EEG from Muse 2")

# Animation update function
def update(frame):
    for ch, line in lines.items():
        y = eeg_data[ch]
        x = range(len(y))
        line.set_data(x, y)
    # Auto-adjust y-limit if needed (optional)
    if any(eeg_data.values()):
        all_vals = np.concatenate(list(eeg_data.values()))
        ax.set_ylim(min(all_vals) - 100, max(all_vals) + 100)
    return list(lines.values())

# Start animation
ani = FuncAnimation(fig, update, interval=50, blit=True)  # Update every 50ms

plt.show()
