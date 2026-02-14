# 🧠 Neurofeedback Focus Game - EEG Training App

A web-based neurofeedback game that integrates with the **Muse 2 EEG headband** to train concentration and focus. Using scientifically-backed brain metrics, this app gamifies mental focus training similar to the Mendi device, allowing you to measure concentration levels before and after sound therapy or other interventions.

![Lilac-themed neurofeedback game](webapp/assets/preview.png)

## ✨ Features

- **Real-time EEG Neurofeedback**: Live concentration score based on frontal cortex activity (AF7 & AF8 electrodes)
- **Scientifically-Backed Metrics**: Composite algorithm using Beta/Alpha ratio, SMR power, and inverted Theta/Beta ratio
- **Gamified Training**: Visual ball-on-path game that responds to your mental focus
- **Session Tracking**: Baseline and post-therapy modes with detailed metrics
- **Data Export**: Export sessions as CSV or JSON for analysis
- **Comparison View**: Compare baseline vs post-therapy sessions to track improvement
- **Beautiful UI**: Calming lilac/purple theme designed to promote focus

## 🎯 How It Works

### EEG Metrics (Scientifically Validated)

This app measures concentration using the same prefrontal cortex activity that fNIRS devices like Mendi target, but with EEG technology:

**Composite Concentration Score = 50% Beta/Alpha + 30% SMR + 20% Inverted Theta/Beta**

- **Beta/Alpha Engagement Index** (50%): Higher ratio = increased attention and mental engagement
- **SMR Power 12-15 Hz** (30%): Validated neurofeedback marker for focused attention
- **Inverted Theta/Beta Ratio** (20%): Lower theta/beta = better executive control and less mind-wandering

These metrics are measured from the frontal electrodes (AF7 & AF8) on the Muse 2, which correspond to prefrontal cortex activity.

## 📋 Requirements

### Hardware
- **Muse 2** EEG headband (or compatible Muse device)
- Computer with Python 3.7+
- Smartphone or tablet running **Mind Monitor** app (iOS/Android)

### Software Dependencies
- Python packages: `numpy`, `scipy`, `python-osc`, `websockets`
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Mind Monitor app for OSC streaming

## 🚀 Quick Start

### 1. Install Python Dependencies

```bash
cd EEG-Game
pip install -r requirements.txt
```

### 2. Configure Mind Monitor

1. Open Mind Monitor app on your phone/tablet
2. Connect your Muse 2 headband
3. Go to Settings → OSC Stream Output
4. Set **Target IP**: Your computer's local IP address (e.g., `192.168.1.100`)
5. Set **Port**: `5000`
6. Enable **Raw EEG** (`/muse/eeg`)
7. Start streaming

### 3. Start the Backend Server

```bash
# Start WebSocket server
python websocket_server.py
```

You should see:
```
OSC server listening on 0.0.0.0:5000
Starting WebSocket server on port 8765
```

### 4. Start the Web App

```bash
# In a new terminal, serve the web app
cd webapp
python -m http.server 8000
```

### 5. Open in Browser

Navigate to: **http://localhost:8000**

1. Accept the medical disclaimer
2. Select session type (Baseline or Post-Therapy)
3. Complete 2-minute calibration
4. Play the game - focus to raise the ball!
5. End session and review metrics
6. Export data for analysis

## 🧪 Testing Without Muse Hardware

Use the included simulator to test the app without a Muse device:

```bash
# Terminal 1: Start simulator
python osc_simulator.py --mode auto --duration 30

# Terminal 2: Start WebSocket server
python websocket_server.py

# Terminal 3: Start web app
cd webapp
python -m http.server 8000
```

The simulator will cycle through low/medium/high focus states every 30 seconds.

## 📖 Usage Guide

### Session Workflow

1. **Baseline Session** (Before Therapy)
   - Select "Baseline Session"
   - Complete calibration (2 min)
   - Play game (5-10 min recommended)
   - Save session data

2. **Therapy/Intervention**
   - Perform your sound therapy or intervention offline
   - (e.g., harmonic resonant surface exposure)

3. **Post-Therapy Session**
   - Select "Post-Therapy Session"
   - Complete calibration (2 min)
   - Play game (same duration as baseline)
   - Save session data

4. **Compare Results**
   - Click "View Past Comparisons"
   - Select baseline and post-therapy sessions
   - View improvement metrics

### Understanding Metrics

- **Concentration Score** (0-100): Composite measure of mental focus
  - 0-40: Relaxed, low focus
  - 40-70: Good concentration
  - 70-100: Peak focus zone
  
- **Peak Score**: Highest concentration achieved during session

- **Average Score**: Mean concentration over entire session

- **High Focus Time**: Duration spent above 70% concentration

### Game Controls

- **No physical controls needed** - control with your mind!
- **Focus** to raise the ball higher
- **Relax** and the ball descends
- Watch for **lilac particle effects** when you hit peak focus (70%+)

## 🎨 Customization

### Adjust Concentration Algorithm Weights

Edit `websocket_server.py`:

```python
WEIGHTS = {
    'beta_alpha': 0.5,      # Engagement index (default 50%)
    'smr': 0.3,             # Focus marker (default 30%)
    'inv_theta_beta': 0.2   # Executive control (default 20%)
}
```

### Change Calibration Duration

Edit `webapp/app.js`:

```javascript
const CALIBRATION_DURATION = 120; // seconds (default 2 min)
```

### Adjust High Focus Threshold

Edit `webapp/app.js`:

```javascript
const HIGH_FOCUS_THRESHOLD = 70; // score (default 70%)
```

## 📊 Data Export Format

### CSV Export
```csv
Timestamp,Concentration Score
2026-02-14T04:30:00.000Z,45.2
2026-02-14T04:30:00.500Z,47.8
...

Session Summary
Type,baseline
Duration,300 seconds
Average Score,52.3
Peak Score,78.9
High Focus Time,45 seconds
```

### JSON Export
```json
{
  "type": "baseline",
  "startTime": "2026-02-14T04:30:00.000Z",
  "endTime": "2026-02-14T04:35:00.000Z",
  "duration": 300,
  "avgScore": 52.3,
  "peakScore": 78.9,
  "highFocusTime": 45,
  "dataPoints": 600,
  "scores": [45.2, 47.8, ...],
  "timestamps": ["2026-02-14T04:30:00.000Z", ...]
}
```

## 🔧 Troubleshooting

### "WebSocket Disconnected"
- Ensure `websocket_server.py` is running
- Check firewall isn't blocking port 8765
- Refresh browser page

### "No EEG Data Received"
- Verify Mind Monitor is streaming to correct IP and port 5000
- Check Muse headband connection (all sensors green)
- Ensure headband is properly fitted

### "Poor Signal Quality"
- Adjust headband fit (sensors should contact skin)
- Clean sensor contacts with alcohol wipe
- Minimize movement and electrical interference
- Check battery level

### Browser Compatibility Issues
- Use latest Chrome, Firefox, Safari, or Edge
- Enable JavaScript
- Check browser console (F12) for errors

## 📁 Project Structure

```
EEG-Game/
├── websocket_server.py       # Backend WebSocket server
├── osc_simulator.py          # EEG data simulator
├── requirements.txt          # Python dependencies
├── config.json               # Configuration file
├── README.md                 # This file
├── webapp/
│   ├── index.html           # Main HTML structure
│   ├── styles.css           # Lilac theme CSS
│   ├── app.js               # Application logic
│   ├── game.js              # Game visualization
│   └── charts.js            # Data visualization
└── EEG/                     # Original EEG analysis scripts
    ├── osc_receiver.py
    ├── dispenza_test.py
    └── dispenza_stacked.py
```

## 🧬 Scientific Background

### EEG vs fNIRS for Concentration

- **Mendi (fNIRS)**: Measures blood oxygenation in prefrontal cortex during focus tasks
- **This App (EEG)**: Measures electrical activity in prefrontal cortex via AF7 & AF8 electrodes

Both methods target the same brain region and mental state, but EEG provides:
- **Higher temporal resolution** (milliseconds vs seconds)
- **Direct neural activity** (vs indirect hemodynamic response)
- **Multiple validated metrics** (SMR, Beta/Alpha, Theta/Beta ratios)

### Research References

- **Beta/Alpha Ratio**: Validated engagement index for attention (Pope et al., 1995)
- **SMR (12-15 Hz)**: Sensorimotor rhythm associated with focused attention (Sterman, 2000)
- **Theta/Beta Ratio**: Marker for executive control and ADHD (Arns et al., 2013)
- **Frontal Asymmetry**: Prefrontal cortex role in sustained attention (Davidson, 2004)

## ⚠️ Disclaimer

**This application is for personal experimentation and research purposes only.**

This is NOT a medical device and should not be used for diagnosis, treatment, or medical decision-making. The concentration metrics and feedback provided are experimental and not clinically validated.

If you have any medical concerns or conditions, please consult with a qualified healthcare professional.

## 📄 License

- Main project code: MIT License
- MindMonitorPython samples: GPL v3 (see `MindMonitorPython/LICENSE`)

## 🤝 Contributing

Contributions welcome! Please feel free to submit issues or pull requests.

## 💡 Future Enhancements

- Mobile-responsive design for tablets
- Multiple game modes and visualizations
- Sound feedback (audio cues for focus states)
- Advanced analytics (trend detection, correlations)
- Integration with other EEG devices
- Cloud storage for session history
- Multi-user profiles

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review existing GitHub issues
3. Open a new issue with detailed description

---

**Happy Focus Training! 🧘‍♀️🧠✨**

Built with ❤️ using scientifically-validated neurofeedback research
