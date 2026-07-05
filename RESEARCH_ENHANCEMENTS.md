# Research Enhancements for Neurofeedback Game

## Overview

This document outlines feature enhancements specifically designed to improve the app's utility for research and experimental studies.

---

## 1. Participant Management 👤

### 1.1 Participant ID System

**Current Gap:** No way to track individual participants across sessions

**Proposed Solution:**

```javascript
// Participant registration screen
class Participant {
  constructor(id, metadata) {
    this.id = id;  // e.g., "P001" or anonymous hash
    this.name = metadata.name || null;  // Optional
    this.age = metadata.age;
    this.gender = metadata.gender;
    this.handedness = metadata.handedness;
    this.createdAt = new Date().toISOString();
    this.sessionCount = 0;
    this.notes = metadata.notes || '';
  }
}

// Storage
const participants = new Map();

function registerParticipant(metadata) {
  const id = generateParticipantId();  // "P001", "P002", etc.
  const participant = new Participant(id, metadata);
  participants.set(id, participant);
  saveToIndexedDB('participants', participant);
  return id;
}
```

**UI Flow:**
1. **First Launch:** Show participant registration form
2. **Returning User:** Select from participant list or create new
3. **Session Start:** Auto-link session to active participant

**Benefits:**
- Track individual progress over time
- Compare within-subject vs between-subject
- Export participant demographics with data
- Maintain anonymity (optional names)

---

### 1.2 Participant Dashboard

**Features:**
- List all participants with session counts
- View participant history (all sessions)
- Edit participant metadata
- Export participant-specific data
- Delete participant (with confirmation)

**Mock UI:**
```
┌─────────────────────────────────────────┐
│ Participants                      [+New]│
├─────────────────────────────────────────┤
│ P001 - Annie (12 sessions)        [View]│
│ P002 - Anonymous (5 sessions)     [View]│
│ P003 - Test User (2 sessions)     [View]│
└─────────────────────────────────────────┘
```

---

## 2. Experimental Design Features 🔬

### 2.1 Study Protocols

**Problem:** Researchers need standardized protocols

**Solution: Protocol Templates**

```javascript
const protocols = {
  'sound-therapy-study': {
    name: 'Sound Therapy Efficacy Study',
    description: 'Measure focus improvement after binaural beats',
    sessions: [
      { type: 'baseline', duration: 300, label: 'Pre-intervention' },
      // [Intervention happens offline]
      { type: 'post-therapy', duration: 300, label: 'Post-intervention' }
    ],
    instructions: {
      baseline: 'Complete baseline session before listening to audio',
      postTherapy: 'Complete within 5 minutes of finishing audio'
    },
    requiredMetadata: ['intervention_type', 'intervention_duration']
  },
  
  'meditation-training': {
    name: 'Meditation Training Program',
    sessions: [
      { type: 'baseline', duration: 300, label: 'Week 0' },
      { type: 'post-therapy', duration: 300, label: 'Week 1' },
      { type: 'post-therapy', duration: 300, label: 'Week 2' },
      { type: 'post-therapy', duration: 300, label: 'Week 4' }
    ]
  }
};
```

**UI:**
- Select protocol at study start
- Guided workflow (shows next required session)
- Progress tracking (2/4 sessions complete)
- Protocol adherence validation

---

### 2.2 Session Metadata & Notes

**Enhancement: Rich Session Context**

```javascript
class EnhancedSession extends Session {
  constructor(type, participantId, protocol) {
    super(type);
    this.participantId = participantId;
    this.protocol = protocol;
    
    // Pre-session metadata
    this.preSessionState = {
      caffeineIntake: null,      // mg in last 4 hours
      sleepQuality: null,        // 1-5 scale
      stressLevel: null,         // 1-5 scale
      timeOfDay: new Date().getHours(),
      daysSinceLastSession: null
    };
    
    // Post-session feedback
    this.postSessionFeedback = {
      perceivedDifficulty: null,  // 1-5 scale
      mentalFatigue: null,        // 1-5 scale
      notes: ''
    };
    
    // Environmental factors
    this.environment = {
      location: 'lab',  // 'lab', 'home', 'other'
      distractions: null,  // 1-5 scale
      temperature: null,
      lighting: null
    };
  }
}
```

**UI: Pre-Session Questionnaire**
```
Before we begin, a few quick questions:

☕ Caffeine in last 4 hours?
   [None] [1 cup] [2+ cups]

😴 How did you sleep last night?
   [Poor] ⚪⚪⚪⚪⚪ [Excellent]

😰 Current stress level?
   [Low] ⚪⚪⚪⚪⚪ [High]

[Continue to Calibration]
```

**Benefits:**
- Control for confounding variables
- Identify patterns (e.g., "scores higher in morning")
- Richer dataset for analysis
- Publication-ready data

---

### 2.3 Intervention Tracking

**Problem:** No record of what intervention was used

**Solution:**

```javascript
// After baseline, before post-therapy
function recordIntervention(participantId, intervention) {
  const record = {
    participantId,
    timestamp: new Date().toISOString(),
    type: intervention.type,  // 'binaural_beats', 'meditation', etc.
    duration: intervention.duration,  // minutes
    parameters: intervention.parameters,  // e.g., {frequency: '40Hz'}
    notes: intervention.notes
  };
  
  saveIntervention(record);
}
```

**UI:**
```
┌────────────────────────────────────────┐
│ Baseline session complete! ✓           │
│                                        │
│ Now perform your intervention, then   │
│ return to complete the post-therapy   │
│ session.                               │
│                                        │
│ [Record Intervention Details]         │
└────────────────────────────────────────┘

// Modal:
Intervention Type: [Binaural Beats ▼]
Duration: [20] minutes
Frequency: [40 Hz]
Notes: [___________________________]

[Save & Continue Later]
```

---

## 3. Statistical Analysis Tools 📊

### 3.1 Built-in Statistics

**Current Gap:** Users must export and analyze in R/Python

**Proposed: In-App Analysis**

```javascript
class SessionAnalyzer {
  static compareBaseline(baselineSession, postSession) {
    return {
      // Basic stats
      avgScoreChange: postSession.avgScore - baselineSession.avgScore,
      avgScoreChangePercent: ((postSession.avgScore - baselineSession.avgScore) / baselineSession.avgScore) * 100,
      peakScoreChange: postSession.peakScore - baselineSession.peakScore,
      
      // Statistical tests
      tTest: this.pairedTTest(baselineSession.scores, postSession.scores),
      effectSize: this.cohensD(baselineSession.scores, postSession.scores),
      
      // Band-specific changes
      bandPowerChanges: this.compareBandPowers(baselineSession, postSession),
      
      // Time-series analysis
      trendAnalysis: this.analyzeTrend(postSession.scores),
      
      // Significance
      isSignificant: null  // computed from t-test
    };
  }
  
  static pairedTTest(sample1, sample2) {
    // Implement paired t-test
    const differences = sample1.map((x, i) => sample2[i] - x);
    const mean = differences.reduce((a, b) => a + b) / differences.length;
    const variance = differences.reduce((sum, x) => sum + Math.pow(x - mean, 2), 0) / (differences.length - 1);
    const se = Math.sqrt(variance / differences.length);
    const t = mean / se;
    const df = differences.length - 1;
    const p = this.tDistribution(t, df);
    
    return { t, df, p, significant: p < 0.05 };
  }
  
  static cohensD(sample1, sample2) {
    // Effect size calculation
    const mean1 = sample1.reduce((a, b) => a + b) / sample1.length;
    const mean2 = sample2.reduce((a, b) => a + b) / sample2.length;
    const pooledSD = this.pooledStandardDeviation(sample1, sample2);
    return (mean2 - mean1) / pooledSD;
  }
}
```

**UI: Enhanced Comparison View**
```
┌──────────────────────────────────────────────┐
│ Statistical Analysis                         │
├──────────────────────────────────────────────┤
│ Baseline → Post-Therapy                      │
│                                              │
│ Average Score: 52.3 → 68.7 (+31.4%) ✓        │
│ Peak Score: 78.2 → 89.1 (+13.9%)             │
│                                              │
│ Paired t-test: t(599) = 12.4, p < 0.001 ***  │
│ Effect size (Cohen's d): 0.82 (large)        │
│                                              │
│ ✓ Statistically significant improvement      │
│                                              │
│ Band Power Changes:                          │
│   Beta:  +18.3% ↑                            │
│   Alpha: -12.1% ↓                            │
│   Theta: -8.4% ↓                             │
│                                              │
│ [Export Full Report]                         │
└──────────────────────────────────────────────┘
```

---

### 3.2 Group Analysis

**Feature: Aggregate Multiple Participants**

```javascript
function analyzeGroup(participantIds, sessionType) {
  const sessions = participantIds.map(id => 
    getSessionsByParticipant(id, sessionType)
  ).flat();
  
  return {
    n: participantIds.length,
    totalSessions: sessions.length,
    
    // Descriptive stats
    meanAvgScore: mean(sessions.map(s => s.avgScore)),
    sdAvgScore: standardDeviation(sessions.map(s => s.avgScore)),
    
    // Distribution
    histogram: createHistogram(sessions.map(s => s.avgScore)),
    
    // Outliers
    outliers: detectOutliers(sessions),
    
    // Reliability
    cronbachAlpha: calculateReliability(sessions)
  };
}
```

**UI:**
```
┌──────────────────────────────────────────┐
│ Group Analysis (N=15)                    │
├──────────────────────────────────────────┤
│ Baseline Sessions:                       │
│   Mean: 54.2 (SD: 8.7)                   │
│   Range: 38.1 - 71.3                     │
│                                          │
│ Post-Therapy Sessions:                   │
│   Mean: 67.8 (SD: 9.2)                   │
│   Range: 49.2 - 84.1                     │
│                                          │
│ Group Effect:                            │
│   Mean change: +13.6 points              │
│   t(14) = 8.2, p < 0.001 ***             │
│   95% CI: [9.8, 17.4]                    │
│                                          │
│ [View Distribution] [Export SPSS]       │
└──────────────────────────────────────────┘
```

---

## 4. Data Quality & Validation 🎯

### 4.1 Signal Quality Metrics

**Enhancement: Detailed Quality Report**

```javascript
class QualityMetrics {
  constructor(session) {
    this.session = session;
  }
  
  analyze() {
    return {
      // Signal quality over time
      avgSignalQuality: this.calculateAvgQuality(),
      poorSignalPercentage: this.calculatePoorSignalPercent(),
      signalDropouts: this.detectDropouts(),
      
      // Movement artifacts
      artifactCount: this.detectArtifacts(),
      artifactPercentage: this.calculateArtifactPercent(),
      
      // Data completeness
      missingDataPoints: this.countMissing(),
      dataCompleteness: this.calculateCompleteness(),
      
      // Recommendation
      usableForAnalysis: this.isUsable(),
      qualityGrade: this.assignGrade()  // A, B, C, D, F
    };
  }
  
  isUsable() {
    return this.dataCompleteness > 0.95 && 
           this.poorSignalPercentage < 0.15 &&
           this.artifactPercentage < 0.20;
  }
}
```

**UI: Post-Session Quality Report**
```
┌──────────────────────────────────────────┐
│ Session Quality Report                   │
├──────────────────────────────────────────┤
│ Overall Grade: A                         │
│                                          │
│ ✓ Signal Quality: Excellent (98%)       │
│ ✓ Data Completeness: 99.2%              │
│ ⚠ Movement Artifacts: 3 detected        │
│ ✓ Usable for Analysis: Yes              │
│                                          │
│ Recommendations:                         │
│ • Excellent session quality              │
│ • Safe to include in analysis            │
│                                          │
│ [View Details] [Save Session]           │
└──────────────────────────────────────────┘
```

---

### 4.2 Exclusion Criteria

**Feature: Automatic Session Flagging**

```javascript
const exclusionCriteria = {
  poorSignalThreshold: 0.20,  // >20% poor signal
  artifactThreshold: 0.25,     // >25% artifacts
  minDuration: 240,            // <4 minutes
  maxDropouts: 5               // >5 signal dropouts
};

function evaluateSession(session) {
  const quality = new QualityMetrics(session);
  const flags = [];
  
  if (quality.poorSignalPercentage > exclusionCriteria.poorSignalThreshold) {
    flags.push({
      type: 'poor_signal',
      severity: 'high',
      message: 'Excessive poor signal quality'
    });
  }
  
  if (session.duration < exclusionCriteria.minDuration) {
    flags.push({
      type: 'short_duration',
      severity: 'high',
      message: 'Session too short for reliable data'
    });
  }
  
  return {
    includeInAnalysis: flags.filter(f => f.severity === 'high').length === 0,
    flags
  };
}
```

---

## 5. Export & Integration 📤

### 5.1 Research-Ready Export Formats

**Current:** Basic CSV/JSON

**Enhanced:**

```javascript
// BIDS (Brain Imaging Data Structure) format
function exportToBIDS(participant, sessions) {
  return {
    'participants.tsv': generateParticipantsTSV([participant]),
    'participants.json': generateParticipantsJSON([participant]),
    [`sub-${participant.id}/`]: {
      [`ses-baseline/eeg/sub-${participant.id}_ses-baseline_task-focus_eeg.json`]: sessionMetadata,
      [`ses-baseline/eeg/sub-${participant.id}_ses-baseline_task-focus_eeg.tsv`]: sessionData
    }
  };
}

// SPSS format
function exportToSPSS(sessions) {
  // Generate .sav file with proper variable labels
}

// R-ready format
function exportForR(sessions) {
  // Long-form data frame with factors
  return sessions.flatMap(s => 
    s.scores.map((score, i) => ({
      participant_id: s.participantId,
      session_type: s.type,
      time_point: i,
      score: score,
      alpha_power: s.bandPowers[i].alpha,
      // ... all variables
    }))
  );
}
```

---

### 5.2 API for External Tools

**Feature: REST API for Integration**

```javascript
// Enable researchers to pull data programmatically
const api = {
  '/api/participants': {
    GET: () => getAllParticipants(),
    POST: (data) => createParticipant(data)
  },
  
  '/api/participants/:id/sessions': {
    GET: (id) => getSessionsByParticipant(id)
  },
  
  '/api/sessions/:id': {
    GET: (id) => getSession(id),
    DELETE: (id) => deleteSession(id)
  },
  
  '/api/export': {
    POST: (params) => exportData(params.format, params.filter)
  }
};

// Python client example
"""
import requests

# Fetch all baseline sessions
response = requests.get('http://localhost:8000/api/sessions?type=baseline')
sessions = response.json()

# Export to pandas
import pandas as pd
df = pd.DataFrame(sessions)
"""
```

---

## 6. Gamification for Engagement 🎮

### 6.1 Progress Tracking

**Feature: Personal Bests & Achievements**

```javascript
const achievements = {
  'first_session': {
    name: 'Getting Started',
    description: 'Complete your first session',
    icon: '🌱'
  },
  'high_score_70': {
    name: 'Focus Master',
    description: 'Achieve average score above 70',
    icon: '⭐'
  },
  'streak_7': {
    name: 'Week Warrior',
    description: 'Complete sessions 7 days in a row',
    icon: '🔥'
  },
  'improvement_20': {
    name: 'Progress Champion',
    description: 'Improve by 20+ points from baseline',
    icon: '📈'
  }
};
```

**UI:**
```
┌──────────────────────────────────────────┐
│ Your Progress                            │
├──────────────────────────────────────────┤
│ Personal Best: 84.2                      │
│ Total Sessions: 12                       │
│ Current Streak: 5 days 🔥                │
│                                          │
│ Recent Achievements:                     │
│ ⭐ Focus Master (unlocked!)              │
│ 📈 Progress Champion (unlocked!)         │
│                                          │
│ Next Goal:                               │
│ 🔥 Week Warrior (2 more days)            │
└──────────────────────────────────────────┘
```

---

### 6.2 Leaderboard (Optional)

**For group studies:**

```javascript
// Anonymous leaderboard
function getLeaderboard(studyId) {
  const participants = getStudyParticipants(studyId);
  return participants
    .map(p => ({
      id: p.anonymousId,  // P001, P002, etc.
      avgImprovement: calculateAvgImprovement(p),
      sessionCount: p.sessionCount
    }))
    .sort((a, b) => b.avgImprovement - a.avgImprovement);
}
```

---

## 7. Implementation Priority

### High Priority (Research Critical)
1. ✅ **Participant ID system** - Essential for tracking
2. ✅ **Session metadata** - Control for confounds
3. ✅ **Quality metrics** - Data validation
4. ✅ **Enhanced exports** - Analysis-ready data

### Medium Priority (Nice to Have)
5. ✅ **Study protocols** - Standardization
6. ✅ **Built-in statistics** - Quick feedback
7. ✅ **Intervention tracking** - Complete record

### Low Priority (Future)
8. ✅ **Group analysis** - Multi-participant studies
9. ✅ **API integration** - Advanced workflows
10. ✅ **Gamification** - Engagement (if needed)

---

## Summary

These enhancements transform the app from a **personal tool** into a **research platform**:

| Feature | Impact | Complexity |
|---------|--------|------------|
| Participant Management | 🔴 Critical | Low |
| Session Metadata | 🔴 Critical | Low |
| Quality Metrics | 🔴 Critical | Medium |
| Statistical Analysis | 🟡 High | Medium |
| Study Protocols | 🟡 High | Medium |
| Enhanced Exports | 🟡 High | Low |
| Group Analysis | 🟢 Medium | High |
| API | 🟢 Medium | High |

**Recommended Next Steps:**
1. Implement participant management (1-2 days)
2. Add session metadata questionnaires (1 day)
3. Build quality metrics dashboard (2 days)
4. Enhance export formats (1 day)

This would make the app **publication-ready** for research studies! 🎓
