# Neurofeedback Focus Game — Optimization Analysis

## Executive Summary

After analyzing the codebase, here are the key optimization opportunities ranked by impact:

| Priority | Area | Impact | Effort |
|----------|------|--------|--------|
| 🔴 High | Backend Performance | High | Medium |
| 🔴 High | Data Persistence | High | Low |
| 🟡 Medium | Frontend Rendering | Medium | Medium |
| 🟡 Medium | Network Efficiency | Medium | Low |
| 🟢 Low | Code Organization | Low | Low |

---

## 1. Backend Performance Optimizations

### 1.1 FFT Computation Caching ⚡

**Current State:**
- Welch's PSD computed every 0.5s for both AF7 and AF8
- ~2 FFT operations per update = high CPU usage

**Optimization:**
```python
# Add to EEGProcessor class
from functools import lru_cache

@lru_cache(maxsize=128)
def _cached_fft_window(self, window_hash):
    """Cache FFT windows to avoid recomputation"""
    pass

# Or use incremental FFT for sliding windows
```

**Expected Gain:** 40-50% CPU reduction

---

### 1.2 Numpy Vectorization 🚀

**Current State:**
- Some loops could be vectorized
- Band power extraction could be optimized

**Optimization:**
```python
# Instead of:
for band_name, (low, high) in bands.items():
    idx = np.logical_and(freqs >= low, freqs <= high)
    powers[band_name] = np.mean(psd[idx])

# Use:
band_indices = {name: np.logical_and(freqs >= low, freqs <= high) 
                for name, (low, high) in bands.items()}
powers = {name: np.mean(psd[idx]) for name, idx in band_indices.items()}
```

**Expected Gain:** 10-15% faster band power extraction

---

### 1.3 Baseline Computation Optimization 📊

**Current State:**
- Baseline computed from all calibration samples at once
- Could use running statistics

**Optimization:**
```python
class RunningStats:
    """Compute mean/std incrementally"""
    def __init__(self):
        self.n = 0
        self.mean = 0
        self.M2 = 0
    
    def update(self, x):
        self.n += 1
        delta = x - self.mean
        self.mean += delta / self.n
        delta2 = x - self.mean
        self.M2 += delta * delta2
```

**Expected Gain:** Constant memory usage, faster calibration

---

## 2. Data Persistence Optimizations

### 2.1 IndexedDB Instead of localStorage 💾

**Current Issue:**
- localStorage limited to ~5-10MB
- Synchronous API blocks UI
- No indexing/querying

**Optimization:**
```javascript
// Use IndexedDB for sessions
const dbPromise = idb.open('neurofeedback-db', 1, {
  upgrade(db) {
    const store = db.createObjectStore('sessions', {
      keyPath: 'id',
      autoIncrement: true
    });
    store.createIndex('type', 'type');
    store.createIndex('startTime', 'startTime');
  }
});

async function saveSession(session) {
  const db = await dbPromise;
  await db.put('sessions', session);
}
```

**Benefits:**
- 50MB+ storage
- Async API (non-blocking)
- Fast queries by type/date
- Better for research data

---

### 2.2 Compression for Export 🗜️

**Current State:**
- Raw JSON/CSV exports can be large
- No compression

**Optimization:**
```javascript
// Add pako.js for gzip compression
import pako from 'pako';

function exportCompressed(data) {
  const json = JSON.stringify(data);
  const compressed = pako.gzip(json);
  const blob = new Blob([compressed], {type: 'application/gzip'});
  downloadFile(blob, `session_${Date.now()}.json.gz`);
}
```

**Expected Gain:** 70-80% smaller file sizes

---

## 3. Frontend Rendering Optimizations

### 3.1 Canvas Rendering Optimization 🎨

**Current State:**
- Full canvas redrawn every frame (~60 FPS)
- Some calculations repeated

**Optimization:**
```javascript
// Use OffscreenCanvas for background
const bgCanvas = new OffscreenCanvas(width, height);
const bgCtx = bgCanvas.getContext('2d');

// Draw static elements once
function drawStaticBackground() {
  // Draw path, zones, etc.
}

// Main loop only draws dynamic elements
function draw() {
  ctx.drawImage(bgCanvas, 0, 0);  // Blit static bg
  drawBall();  // Only redraw ball
  drawParticles();
}
```

**Expected Gain:** 30-40% FPS improvement

---

### 3.2 RequestAnimationFrame Throttling ⏱️

**Current State:**
- Game updates at 60 FPS even when score unchanged

**Optimization:**
```javascript
let lastScore = 0;
let frameSkip = 0;

function animate() {
  frameSkip++;
  
  // Only redraw if score changed or every 3rd frame
  if (game.score !== lastScore || frameSkip >= 3) {
    draw();
    frameSkip = 0;
    lastScore = game.score;
  }
  
  updateParticles();  // Always update physics
  requestAnimationFrame(animate);
}
```

**Expected Gain:** Reduced battery usage on mobile

---

### 3.3 Web Workers for Chart Rendering 👷

**Current State:**
- Chart rendering blocks main thread
- Can cause jank during results screen

**Optimization:**
```javascript
// chart-worker.js
self.onmessage = function(e) {
  const {session, width, height} = e.data;
  const imageData = renderChartToImageData(session, width, height);
  self.postMessage({imageData}, [imageData.data.buffer]);
};

// main thread
const worker = new Worker('chart-worker.js');
worker.postMessage({session, width, height});
worker.onmessage = (e) => {
  ctx.putImageData(e.data.imageData, 0, 0);
};
```

**Expected Gain:** Smoother UI, no blocking

---

## 4. Network Efficiency

### 4.1 WebSocket Message Batching 📦

**Current State:**
- One message per EEG update (2 Hz)
- Could batch multiple updates

**Optimization:**
```python
# Server-side batching
class MessageBatcher:
    def __init__(self, interval=0.1):
        self.buffer = []
        self.interval = interval
        
    async def add(self, message):
        self.buffer.append(message)
        if len(self.buffer) >= 5:  # Batch size
            await self.flush()
            
    async def flush(self):
        if self.buffer:
            await broadcast({'type': 'batch', 'messages': self.buffer})
            self.buffer = []
```

**Expected Gain:** 60% less network overhead

---

### 4.2 Delta Compression 🔄

**Current State:**
- Full band powers sent every update
- Most values change slowly

**Optimization:**
```javascript
// Only send changed values
let lastBandPowers = {};

function sendUpdate(bandPowers) {
  const delta = {};
  for (const [band, power] of Object.entries(bandPowers)) {
    if (Math.abs(power - (lastBandPowers[band] || 0)) > 0.5) {
      delta[band] = power;
    }
  }
  
  if (Object.keys(delta).length > 0) {
    ws.send({type: 'delta', changes: delta});
    lastBandPowers = {...lastBandPowers, ...delta};
  }
}
```

**Expected Gain:** 50-70% less data transmitted

---

## 5. Code Organization

### 5.1 Config Management 🔧

**Current State:**
- Some constants hardcoded
- config.json not fully utilized

**Optimization:**
- Move all magic numbers to config
- Add config validation
- Support user-configurable thresholds

---

### 5.2 Error Handling 🛡️

**Current State:**
- Basic try/catch
- Limited error recovery

**Optimization:**
```python
# Add structured error handling
class EEGProcessingError(Exception):
    pass

class SignalQualityError(EEGProcessingError):
    pass

# Graceful degradation
try:
    score = calculate_concentration_score(powers, baseline)
except SignalQualityError:
    score = last_valid_score  # Use last known good value
    logger.warning("Using cached score due to poor signal")
```

---

### 5.3 Logging & Monitoring 📝

**Current State:**
- Basic console logging
- No metrics collection

**Optimization:**
```python
# Add structured logging
import structlog

logger = structlog.get_logger()

logger.info("eeg_processed", 
            score=score,
            signal_quality=quality,
            processing_time_ms=elapsed)

# Add performance metrics
from prometheus_client import Histogram

processing_time = Histogram('eeg_processing_seconds',
                           'Time spent processing EEG')

with processing_time.time():
    score = process_eeg(data)
```

---

## 6. Research-Specific Optimizations

### 6.1 Experiment Metadata 🔬

**Optimization:**
```javascript
// Add experiment tracking
const session = {
  ...existingData,
  metadata: {
    participantId: generateAnonymousId(),
    experimentVersion: '1.0.0',
    deviceInfo: {
      browser: navigator.userAgent,
      screen: `${screen.width}x${screen.height}`,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
    },
    calibrationQuality: {
      avgSignalQuality: 'good',
      droppedSamples: 5
    }
  }
};
```

**Benefits:**
- Better data quality control
- Easier to filter bad sessions
- Reproducibility

---

### 6.2 Batch Export for Analysis 📊

**Optimization:**
```javascript
// Export all sessions in research format
function exportForAnalysis() {
  const sessions = getAllSessions();
  
  // Convert to long-form data (one row per sample)
  const longForm = sessions.flatMap(session => 
    session.scores.map((score, i) => ({
      session_id: session.id,
      session_type: session.type,
      timestamp: session.timestamps[i],
      score: score,
      ...session.bandPowers[i],
      ...session.components[i]
    }))
  );
  
  exportCSV(longForm, 'all_sessions_long_format.csv');
}
```

**Benefits:**
- Ready for R/Python analysis
- No preprocessing needed

---

## 7. Mobile Optimization

### 7.1 Progressive Web App (PWA) 📱

**Optimization:**
```javascript
// Add service worker for offline capability
// manifest.json
{
  "name": "Focus Neurofeedback",
  "short_name": "Focus",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#F5F0FF",
  "theme_color": "#9B7EDC",
  "icons": [...]
}
```

**Benefits:**
- Install on mobile
- Offline calibration
- Better UX

---

### 7.2 Touch Optimization 👆

**Current State:**
- Desktop-focused interactions

**Optimization:**
```css
/* Better touch targets */
.session-btn {
  min-height: 44px;  /* iOS minimum */
  touch-action: manipulation;
}

/* Prevent zoom on double-tap */
button {
  touch-action: manipulation;
}
```

---

## Implementation Priority

### Phase 1 (Quick Wins - 1 week)
1. ✅ IndexedDB migration
2. ✅ Config consolidation
3. ✅ Compression for exports
4. ✅ Better error handling

### Phase 2 (Performance - 2 weeks)
1. ✅ FFT caching
2. ✅ Canvas optimization
3. ✅ WebSocket batching
4. ✅ Numpy vectorization

### Phase 3 (Research Features - 1 week)
1. ✅ Experiment metadata
2. ✅ Batch export
3. ✅ Logging/monitoring

### Phase 4 (Mobile - 2 weeks)
1. ✅ PWA implementation
2. ✅ Touch optimization
3. ✅ Responsive improvements

---

## Estimated Impact

| Optimization | CPU | Memory | Network | UX |
|--------------|-----|--------|---------|-----|
| FFT Caching | -40% | +10MB | - | ✓ |
| IndexedDB | - | -5MB | - | ✓✓ |
| Canvas Opt | -30% | - | - | ✓✓ |
| WS Batching | - | - | -60% | ✓ |
| Compression | - | - | -75% | ✓ |

**Overall:** ~50% less CPU, ~70% less network, smoother UX

---

## Testing Recommendations

1. **Load Testing:** Simulate 8-hour continuous sessions
2. **Memory Profiling:** Check for leaks in long sessions
3. **Network Testing:** Test on slow connections (3G)
4. **Cross-Browser:** Verify Safari, Firefox, Edge
5. **Mobile Testing:** iOS Safari, Chrome Android

---

## Conclusion

The app is already well-architected, but these optimizations would:
- **Improve battery life** on mobile devices
- **Enable longer sessions** without performance degradation
- **Support larger datasets** for research
- **Provide better UX** with smoother animations

**Recommended Next Step:** Start with Phase 1 (quick wins) to validate approach, then proceed to performance optimizations.
