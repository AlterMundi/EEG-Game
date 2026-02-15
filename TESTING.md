# Testing Guide

## Quick Start

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
python run_tests.py
```

## Test Structure

```
tests/
├── __init__.py
├── test_backend.py      # Backend unit tests (25 tests)
└── test_frontend.py     # Frontend integration tests (Selenium)
```

## Backend Tests

**Coverage:**
- ✅ Band power calculation (FFT/PSD)
- ✅ Concentration score algorithm
- ✅ Signal quality estimation
- ✅ EEG processor class
- ✅ Data export format
- ✅ WebSocket message structure

**Run:**
```bash
python -m pytest tests/test_backend.py -v
```

## Frontend Tests

**Requirements:**
- WebSocket server running on port 8765
- Web server running on port 8000
- Chrome/Chromium browser installed

**Coverage:**
- ✅ Disclaimer modal
- ✅ Session buttons
- ✅ WebSocket connection
- ✅ localStorage persistence
- ✅ Canvas rendering

**Run:**
```bash
# Start servers first
python websocket_server.py &
cd webapp && python -m http.server 8000 &

# Run tests
python tests/test_frontend.py
```

## Coverage Report

```bash
python -m pytest tests/test_backend.py \
  --cov=websocket_server \
  --cov=osc_simulator \
  --cov-report=html \
  --cov-report=term

# View report
open htmlcov/index.html
```

## Test Cases

### Band Power Calculation
- Pure alpha signal (10 Hz) → high alpha power
- Pure beta signal (20 Hz) → high beta power
- Mixed signals → both bands present
- All bands computed correctly

### Concentration Score
- High beta/low alpha → high score (>50)
- Low beta/high alpha → low score (<50)
- Baseline normalization works
- Score bounded [0, 100]

### Signal Quality
- Clean signal → "good"
- High amplitude → "poor" (artifact)
- Flat line → "poor" (disconnected)
- Moderate noise → "fair"

### EEG Processor
- Buffer management (max 1024 samples)
- Calibration data collection
- Baseline computation
- Proper initialization

## Continuous Integration

Add to `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: python -m pytest tests/test_backend.py -v
```

## Performance Benchmarks

Run benchmarks:
```bash
python -m pytest tests/test_backend.py --benchmark-only
```

Expected performance:
- Band power calculation: <5ms
- Concentration score: <1ms
- Signal quality: <2ms
- Full EEG processing: <10ms

## Debugging Failed Tests

```bash
# Run with verbose output
python -m pytest tests/test_backend.py -vv

# Run specific test
python -m pytest tests/test_backend.py::TestBandPowerCalculation::test_pure_alpha_signal -v

# Drop into debugger on failure
python -m pytest tests/test_backend.py --pdb
```

## Adding New Tests

```python
# tests/test_backend.py

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        """Run before each test"""
        pass
        
    def test_something(self):
        """Test description"""
        result = my_function()
        self.assertEqual(result, expected_value)
```

## Test Data

Synthetic EEG data is generated in tests using:
- Sine waves for specific frequencies
- Random noise for realistic signals
- Edge cases (flat lines, high amplitude)

No real EEG data is included in tests for privacy.
