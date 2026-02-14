# Neurofeedback Game - Detailed Setup Guide

Complete step-by-step instructions for running the neurofeedback game with your Muse 2 headband.

## Table of Contents
1. [Quick Start](#quick-start)
2. [Detailed Hardware Setup](#detailed-hardware-setup)
3. [Mind Monitor Configuration](#mind-monitor-configuration)
4. [Running the Application](#running-the-application)
5. [Your First Session](#your-first-session)
6. [Tips for Best Results](#tips-for-best-results)

## Quick Start

**Prerequisites Check:**
- ✅ Muse 2 headband charged and ready
- ✅ Mind Monitor app installed on phone/tablet
- ✅ Python 3.7+ installed on computer
- ✅ Computer and phone on same Wi-Fi network

**5-Minute Setup:**
```bash
# 1. Install dependencies
cd EEG-Game
pip install -r requirements.txt

# 2. Find your computer's IP address
# Linux/Mac:
ifconfig | grep "inet "
# Windows:
ipconfig

# 3. Configure Mind Monitor (on phone):
#    - Settings → OSC Stream Output
#    - IP: [your computer's IP]
#    - Port: 5000
#    - Enable /muse/eeg stream

# 4. Start backend server
python websocket_server.py

# 5. Start web app (new terminal)
cd webapp
python -m http.server 8000

# 6. Open browser
# Navigate to: http://localhost:8000
```

Done! You should see the game interface.

## Detailed Hardware Setup

### 1. Muse 2 Headband Preparation

**Battery:**
- Charge headband fully before first use
- LED indicator will show charging status
- Full charge = ~4-5 hours of continuous use

**Fitting the Headband:**
1. **Position**: Place headband with logo centered on forehead
2. **Ear sensors**: TP9 and TP10 must rest on skin above/behind ears
3. **Forehead sensors**: AF7 and AF8 must contact forehead (no hair)
4. **Reference sensor**: FPz (center) should touch forehead skin
5. **Tightness**: Should feel snug but comfortable - not loose, not painful

**Sensor Contact Check (in Mind Monitor):**
- All 4 sensors should show **green** (good contact)
- Yellow = fair contact (adjust fit)
- Red/grey = poor contact (clean sensors or refit)

### 2. Mind Monitor App Installation

**iOS:**
```
App Store → Search "Mind Monitor" → Install
Compatible with: iPhone, iPad running iOS 12+
```

**Android:**
```
Google Play Store → Search "Mind Monitor" → Install
Compatible with: Android 8.0+
```

**Cost:** ~$10-15 USD (one-time purchase)

### 3. Network Setup

**Both devices must be on the same network:**

```
Computer Wi-Fi: MyNetwork_5GHz
Phone Wi-Fi:    MyNetwork_5GHz  ← Must match!
```

**Find your computer's IP:**

- **macOS/Linux:**
  ```bash
  ifconfig | grep "inet "
  # Look for: inet 192.168.1.XXX
  ```

- **Windows (PowerShell):**
  ```powershell
  ipconfig
  # Look for: IPv4 Address: 192.168.1.XXX
  ```

**Common IP ranges:**
- Home networks: `192.168.0.XXX` or `192.168.1.XXX`
- If starts with `127.0.0.1`, that's localhost (wrong!)

## Mind Monitor Configuration

### Step-by-Step OSC Setup

1. **Open Mind Monitor** on your phone/tablet

2. **Connect Muse Headband:**
   - Tap "Connect" button
   - Select your Muse device from  list
   - Wait for connection (blue LED on headband)

3. **Check Signal Quality:**
   - Horseshoe indicator at top
   - Adjust fit until all bars are green

4. **Configure OSC Streaming:**
   - Tap ⚙️ **Settings** (gear icon)
   - Scroll to **"OSC Stream Output"**
   - Enable **"OSC Output"** toggle

5. **Set Connection Parameters:**
   ```
   IP Address: [Your computer IP, e.g., 192.168.1.100]
   Port:       5000
   OSC Format: "[Value]" format (default)
   ```

6. **Enable Required Streams:**
   - ✅ **Raw EEG** (`/muse/eeg`) - REQUIRED
   - Optional for debugging:
     - ☑️ Absolute Band Powers (`/muse/elements/*)`)
     - ☑️ Horseshoe (`/muse/elements/horseshoe`)

7. **Start Streaming:**
   - Return to main screen
   - Tap **"Start Streaming"** button
   - You should see EEG waves scrolling on screen

### Verification

Your computer should now receive OSC data on port 5000.

To test:
```bash
python websocket_server.py
```

Look for console output like:
```
OSC server listening on 0.0.0.0:5000
Received EEG data: [-123.45, 67.89, ...]
```

If no data appears:
- Double-check IP address is correct
- Verify port 5000 is not blocked by firewall
- Ensure both devices on same Wi-Fi

## Running the Application

### Method 1: Production Use (with Muse Hardware)

**Terminal 1 - Backend Server:**
```bash
cd /path/to/EEG-Game
python websocket_server.py
```

Expected output:
```
OSC server listening on 0.0.0.0:5000
Starting WebSocket server on port 8765
```

**Terminal 2 - Web App:**
```bash
cd /path/to/EEG-Game/webapp
python -m http.server 8000
```

Expected output:
```
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

**Browser:**
- Open: http://localhost:8000
- Or from another device: http://[computer-ip]:8000

### Method 2: Testing (with Simulator)

**Terminal 1 - Simulator:**
```bash
cd /path/to/EEG-Game
python osc_simulator.py --mode auto --duration 30
```

**Terminal 2 - Backend Server:**
```bash
python websocket_server.py
```

**Terminal 3 - Web App:**
```bash
cd webapp
python -m http.server 8000
```

**Browser:**
- Open: http://localhost:8000
- Game will respond to simulated concentration states

## Your First Session

### 1. Accept Disclaimer

- Read medical disclaimer carefully
- Check "I understand and accept" box
- Click "Continue to App"

### 2. Check Connection Status

Top status bar should show:
- **Connection:** Green "Connected"
- **Signal Quality:** "Good" (may show "Unknown" initially)
- **Session:** "None"

### 3. Select Session Type

**For first-time users:**
- Click **"Baseline Session"**
- This establishes your personal baseline

### 4. Calibration Phase (2 minutes)

**Instructions:**
- Relax and sit comfortably
- Close your eyes (recommended)
- Breathe naturally
- **Don't try to focus or meditate** - just relax

**Why calibration?**
- Establishes your personal "relaxed state" baseline
- All future scores are normalized against this
- Ensures accurate concentration measurements

**What's happening:**
- App collects 240 samples of your brain activity
- Calculates average band powers (theta, alpha, beta, SMR)
- Stores baseline for comparison

### 5. Game Phase (5-10 minutes recommended)

**Gameplay:**
- A ball appears on a vertical path
- **Focus your mind** → Ball rises
- **Relax/mind-wander** → Ball descends

**Tips:**
- Try different mental strategies:
  - Mental math (7 × 13 = ?)
  - Counting backwards from 100 by 7s
  - Visualizing complex shapes
  - Sustained attention on single object
- Note which strategies work best for you

**Visual Feedback:**
- **Lilac particles** appear at scores >70% (peak focus)
- **Zone indicators** on right:
  - 🎯 Peak Focus (70-100%)
  - 😊 Good Focus (40-70%)
  - 😌 Relaxed (0-40%)

**Metrics to watch:**
- **Concentration**: Current score (0-100)
- **Peak**: Highest score achieved
- **Time**: Session duration

### 6. End Session & Results

**When done:**
- Click "End Session" button
- Or let it run for desired duration

**Results Screen shows:**
- 📊 Average Score
- ⭐ Peak Score
- ⏱️ Duration
- 🎯 High Focus Time (time spent >70%)
- 📈 Time-series chart of your session

**Export Data:**
- Click "💾 Export CSV" for spreadsheet analysis
- Click "📄 Export JSON" for programmatic analysis

### 7. Post-Therapy Protocol

1. Complete baseline session (above)
2. Perform your intervention (e.g., sound therapy)
3. Return to app
4. Click "Post-Therapy Session"
5. Repeat calibration & game
6. Compare results!

## Tips for Best Results

### Hardware Tips

**Headband Fit:**
- ✅ All sensors green in Mind Monitor
- ✅ Snug but comfortable
- ✅ Hair away from forehead sensors
- ✅ Ear sensors on bare skin (not over hair or earrings)

**Environment:**
- Minimize electrical interference (turn off nearby devices)
- Quiet room with minimal distractions
- Comfortable temperature
- Good lighting (but not harsh)

**Sensor Maintenance:**
- Clean with alcohol wipes after each use
- Store in case when not in use
- Avoid getting wet (except sensor contacts)

### Software Tips

**Connection:**
- Keep devices close (within 10m) for strong Bluetooth
- Avoid Wi-Fi congestion (fewer devices = better)
- Close unnecessary apps on phone running Mind Monitor

**Session Best Practices:**
- Same time of day for consistent results
- Not immediately after coffee/stimulants
- Not when very tired
- Hydrate well beforehand

### Data Collection Tips

**For research/comparison:**
- Keep sessions same duration (e.g., always 10 min)
- Use same mental focus strategies
- Note any variables (caffeine, sleep, stress)
- Export data immediately after sessions

**Protocol example:**
```
Day 1: Baseline session (10 min)
Day 1: Sound therapy (30 min)
Day 1: Post-therapy session (10 min)
Day 7: Repeat protocol
Day 14: Repeat protocol
→ Compare trends over time
```

## Troubleshooting

### No Connection

**"WebSocket Disconnected":**
```bash
# Check backend is running:
ps aux | grep websocket_server

# If not, restart:
python websocket_server.py
```

**"No EEG Data":**
1. Check Mind Monitor shows green connection
2. Verify IP address in Mind Monitor matches computer
3. Test OSC reception:
   ```bash
   python -m pythonosc.tools.dump_osc 5000
   # Should show incoming OSC messages
   ```

### Poor Signal Quality

**All sensors grey/red:**
- Clean sensor contacts with alcohol wipe
- Moisturize forehead slightly (hand lotion)
- Adjust headband position

**One sensor red:**
- Most common: TP9 or TP10 (ear sensors)
- Ensure sensor touches skin above/behind ear
- Move hair out of the way
- Try slightly tighter fit

### Strange Scores

**Score always 0 or always 100:**
- Calibration may have failed
- Restart session with better sensor contact

**Score too jittery:**
- Normal slight variation is expected
- Large swings may indicate movement/artifacts
- Sit still and relax

**Score doesn't respond to focus:**
- Try different focus strategies
- Some people respond better to visual vs. verbal tasks
- Practice - neurofeedback is a skill that improves!

---

**Need more help?** Check the main README.md or open an issue on GitHub.

Happy focus training! 🧠✨
