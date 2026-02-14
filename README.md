# EEG-Game

A Python-based real-time EEG (Electroencephalography) visualization and meditation state detection system using the Muse 2 headband. This project provides tools for receiving, analyzing, and visualizing brainwave data via OSC (Open Sound Control) protocol.

## Overview

This repository contains tools for:
- Real-time EEG signal visualization from Muse 2 devices
- Frequency band analysis (Delta, Theta, Alpha, Beta, Gamma)
- Meditation/transcendent state detection based on Dr. Joe Dispenza's research
- OSC-based data streaming and processing

## Project Structure

```
EEG-Game/
├── EEG/                          # Main EEG analysis scripts
│   ├── osc_receiver.py          # Simple OSC receiver with live EEG visualization
│   ├── dispenza_test.py         # Meditation state detection with overlapped channel view
│   └── dispenza_stacked.py      # Meditation state detection with stacked channel view
├── MindMonitorPython/           # Sample OSC receivers (from Mind Monitor)
│   ├── OSC Receiver.py          # Records EEG data to CSV
│   ├── OSC Receiver Simple.py   # Displays raw EEG data
│   ├── OSC Receiver Audio Feedback.py  # Relative wave visualization with audio feedback
│   ├── bell.mp3                 # Audio feedback sound file
│   └── LICENSE                  # GPL v3 License
└── README.md                    # This file
```

## Features

### Real-time Visualization
- Live plotting of raw EEG signals from all 4 channels (TP9, AF7, AF8, TP10)
- Stacked or overlapped channel views
- Auto-scaling y-axis for optimal signal visibility

### Frequency Band Analysis
- **Delta** (0.5-4 Hz): Deep sleep, unconscious states
- **Theta** (4-8 Hz): Deep meditation, creativity, REM sleep
- **Alpha** (8-13 Hz): Relaxed awareness, light meditation
- **Beta** (13-30 Hz): Active thinking, focus
- **Gamma** (30-44 Hz): Peak concentration, transcendent states

### Meditation State Detection
The `dispenza_*.py` scripts detect potential transcendent meditation states by monitoring:
- Elevated theta power (30%+ above baseline)
- Gamma surges (15%+ above baseline)
- High theta/beta ratio (>2.0)
- Frontal theta coherence (>0.75)

## Requirements

### Hardware
- **Muse 2** EEG headband (or compatible Muse device)
- Computer with Python 3.7+

### Software
- **Mind Monitor** app (iOS/Android) or **Muse Direct** for streaming EEG data via OSC

### Python Dependencies
```bash
pip install numpy scipy matplotlib python-osc
```

Optional (for audio feedback):
```bash
pip install playsound
```

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd EEG-Game
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Muse device:
   - Install Mind Monitor app on your mobile device
   - Connect your Muse 2 headband
   - Configure OSC streaming to your computer's IP address on port 5000

## Usage

### Basic EEG Visualization

Run the simple OSC receiver to visualize raw EEG signals:
```bash
python EEG/osc_receiver.py
```

### Meditation State Detection

For meditation state detection with baseline calibration:

**Stacked channel view:**
```bash
python EEG/dispenza_stacked.py
```

**Overlapped channel view:**
```bash
python EEG/dispenza_test.py
```

**Process:**
1. The script will collect a 30-second baseline (relax, eyes closed, no meditation)
2. After baseline recording, real-time analysis begins
3. The console will display alerts when meditation markers are detected
4. The plot title shows current frequency band powers and ratios

### Recording EEG Data

To record EEG data to CSV:
```bash
python MindMonitorPython/OSC\ Receiver.py
```
- Send Marker #1 to start recording
- Send Marker #2 to stop recording
- Data is saved to `OSC-Python-Recording.csv`

## Configuration

### OSC Settings
- Default IP: `0.0.0.0` (listens on all interfaces)
- Default Port: `5000`
- OSC Path: `/muse/eeg`

### Analysis Parameters
You can adjust thresholds in the `dispenza_*.py` scripts:
```python
THRESHOLDS = {
    'theta_increase_factor': 1.3,    # 30% above baseline
    'gamma_increase_factor': 1.15,    # 15% above baseline
    'theta_beta_ratio': 2.0,          # Higher = deeper meditation
    'theta_coherence': 0.75           # High synchronization
}
```

### Sampling Parameters
- Sampling Rate: 256 Hz (Muse 2 default)
- Window Size: 1024 samples (~4 seconds)
- Update Interval: 1.0 second

## Troubleshooting

### No data received
- Verify Mind Monitor is streaming to the correct IP address and port
- Check firewall settings (port 5000 must be open)
- Ensure Muse headband is properly fitted (check HSI values in Mind Monitor)

### Poor signal quality
- Ensure proper headband fit (all sensors should show good contact)
- Clean sensor contacts with alcohol wipes
- Minimize movement and electrical interference

### Import errors
- Make sure all dependencies are installed: `pip install numpy scipy matplotlib python-osc`
- Use Python 3.7 or higher

## Credits

- **Mind Monitor Python Samples**: The `MindMonitorPython/` directory contains sample code from Mind Monitor (licensed under GPL v3)
- **Meditation Research**: Detection algorithms inspired by Dr. Joe Dispenza's research on transcendent meditation states

## License

- Main project: See LICENSE file (if present)
- MindMonitorPython samples: GPL v3 (see `MindMonitorPython/LICENSE`)

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Disclaimer

This software is for research and educational purposes only. EEG data interpretation should not be used as a substitute for professional medical advice or diagnosis.
