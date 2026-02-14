# Data Export Format Guide

## Overview

The neurofeedback game now exports **comprehensive raw EEG data** along with the calculated concentration score. This allows you to perform advanced analysis on your brain activity patterns.

## CSV Export Format

When you click "Export CSV" after a session, you'll get a file with **10 columns** of data:

### Column Headers
```csv
Timestamp, Concentration Score, Delta, Theta, Alpha, SMR, Beta, Gamma, Beta/Alpha, SMR Power, Inv Theta/Beta
```

### Column Descriptions

#### 1. **Timestamp** (ISO 8601 format)
- When the sample was recorded
- Example: `2026-02-14T05:30:15.234Z`

#### 2. **Concentration Score** (0-100)
- Your computed focus level
- Normalized to personal baseline
- Higher = better focus

#### 3-8. **Raw EEG Band Powers** (μV²)
Power spectral density for each frequency band:

- **Delta** (0.5-4 Hz): Deep sleep, unconscious processes
- **Theta** (4-8 Hz): Meditation, creativity, memory
- **Alpha** (8-13 Hz): Relaxation, closed eyes, calm
- **SMR** (12-15 Hz): Sensorimotor rhythm, focused calm
- **Beta** (13-30 Hz): Active thinking, concentration, alertness
- **Gamma** (30-44 Hz): Peak cognitive processing

#### 9-11. **Concentration Components** (normalized)
The three weighted metrics that comprise your concentration score:

- **Beta/Alpha Ratio**: Engagement index (50% weight)
  - Higher = more engaged/less relaxed
  
- **SMR Power**: Focus marker (30% weight)
  - Higher = sustained attention
  
- **Inv Theta/Beta**: Executive control (20% weight)
  - Higher = less mind-wandering

## JSON Export Format

The JSON export contains **all session data** in structured format:

```json
{
  "type": "baseline",
  "startTime": "2026-02-14T05:30:00.000Z",
  "endTime": "2026-02-14T05:35:00.000Z",
  "duration": 300,
  "avgScore": 52.3,
  "peakScore": 78.9,
  "highFocusTime": 45,
  "dataPoints": 600,
  
  "scores": [45.2, 47.8, 51.3, ...],
  "timestamps": ["2026-02-14T05:30:00.000Z", ...],
  
  "bandPowers": [
    {
      "delta": 125.45,
      "theta": 89.23,
      "alpha": 156.78,
      "smr": 98.12,
      "beta": 234.56,
      "gamma": 67.89
    },
    ...
  ],
  
  "components": [
    {
      "beta_alpha_ratio": 1.496,
      "smr_power": 98.12,
      "inv_theta_beta": 2.628
    },
    ...
  ]
}
```

## Example Analysis Use Cases

### 1. Analyze Frequency Band Trends
```python
import pandas as pd
import matplotlib.pyplot as plt

# Load CSV
df = pd.read_csv('neurofeedback_baseline_2026-02-14.csv')

# Plot all bands over time
plt.figure(figsize=(12, 6))
plt.plot(df['Alpha'], label='Alpha')
plt.plot(df['Beta'], label='Beta')
plt.plot(df['Theta'], label='Theta')
plt.plot(df['SMR'], label='SMR')
plt.legend()
plt.title('EEG Band Powers Over Time')
plt.show()
```

### 2. Correlate Components with Score
```python
# See which component correlates most with your score
correlation = df[['Beta/Alpha', 'SMR Power', 'Inv Theta/Beta']].corrwith(df['Concentration Score'])
print(correlation)
```

### 3. Compare Baseline vs Post-Therapy Band Changes
```python
baseline = pd.read_csv('session_baseline.csv')
post = pd.read_csv('session_post_therapy.csv')

# Calculate average band powers
baseline_avg = baseline[['Delta', 'Theta', 'Alpha', 'SMR', 'Beta', 'Gamma']].mean()
post_avg = post[['Delta', 'Theta', 'Alpha', 'SMR', 'Beta', 'Gamma']].mean()

# Show changes
changes = ((post_avg - baseline_avg) / baseline_avg * 100)
print("Band Power Changes:")
print(changes)
```

### 4. Export to Research Tools
The CSV format is compatible with:
- **MATLAB / Octave**: `data = csvread('file.csv', 1, 0);`
- **R**: `data <- read.csv('file.csv')`
- **Excel / Google Sheets**: Import directly
- **Python Pandas**: `df = pd.read_csv('file.csv')`

## Technical Notes

### Sampling
- Data points collected every **0.5 seconds**
- Each point represents **~4 seconds** of EEG (1024 samples @ 256 Hz)
- Windows overlap for smooth measurements

### Band Power Units
- All band powers in **μV²** (microvolts squared)
- Calculated via Welch's method (FFT-based PSD)
- Averaged across frontal electrodes (AF7 & AF8)

### Component Normalization
- All components normalized to your **personal baseline**
- Value of 1.0 = at baseline level
- Value > 1.0 = above baseline
- Value < 1.0 = below baseline

### Missing Data
If the system couldn't calculate a metric:
- Values will be `0` in CSV
- Fields may be empty in JSON

## Privacy & Storage

- All data stored **locally** in browser localStorage
- Exports saved to your **Downloads folder**
- **No cloud upload** - your brain data stays private
- Clear localStorage to delete all session history

## Questions?

For more details on the science behind these metrics, see `README.md` section "Scientific Background".

---

**Happy analyzing! 🧠📊**
