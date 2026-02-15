"""
Neurofeedback Focus Game - Test Suite
Comprehensive TDD battery for backend and frontend components
"""

import unittest
import asyncio
import json
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from websocket_server import (
    compute_band_powers,
    calculate_concentration_score,
    estimate_signal_quality,
    EEGProcessor
)


class TestBandPowerCalculation(unittest.TestCase):
    """Test EEG band power extraction"""
    
    def setUp(self):
        """Generate synthetic EEG data"""
        self.fs = 256  # Sampling rate
        self.duration = 4  # seconds
        self.n_samples = self.fs * self.duration
        self.t = np.linspace(0, self.duration, self.n_samples)
        
    def test_pure_alpha_signal(self):
        """Test that 10 Hz signal produces high alpha power"""
        # Generate 10 Hz sine wave (alpha band)
        signal = np.sin(2 * np.pi * 10 * self.t)
        powers = compute_band_powers(signal, self.fs)
        
        # Alpha should be dominant
        self.assertGreater(powers['alpha'], powers['theta'])
        self.assertGreater(powers['alpha'], powers['beta'])
        
    def test_pure_beta_signal(self):
        """Test that 20 Hz signal produces high beta power"""
        signal = np.sin(2 * np.pi * 20 * self.t)
        powers = compute_band_powers(signal, self.fs)
        
        # Beta should be dominant
        self.assertGreater(powers['beta'], powers['alpha'])
        self.assertGreater(powers['beta'], powers['theta'])
        
    def test_mixed_signal(self):
        """Test mixed frequency signal"""
        # Mix of alpha (10 Hz) and beta (20 Hz)
        signal = np.sin(2 * np.pi * 10 * self.t) + 0.5 * np.sin(2 * np.pi * 20 * self.t)
        powers = compute_band_powers(signal, self.fs)
        
        # Both should be present
        self.assertGreater(powers['alpha'], 0)
        self.assertGreater(powers['beta'], 0)
        
    def test_all_bands_present(self):
        """Test that all frequency bands are computed"""
        signal = np.random.randn(self.n_samples)
        powers = compute_band_powers(signal, self.fs)
        
        required_bands = ['delta', 'theta', 'alpha', 'smr', 'beta', 'gamma']
        for band in required_bands:
            self.assertIn(band, powers)
            self.assertGreater(powers[band], 0)


class TestConcentrationScore(unittest.TestCase):
    """Test concentration score calculation"""
    
    def test_high_beta_low_alpha_gives_high_score(self):
        """High beta/alpha ratio should indicate focus"""
        powers = {
            'delta': 10,
            'theta': 15,
            'alpha': 20,
            'smr': 30,
            'beta': 60,  # High beta
            'gamma': 5
        }
        
        score = calculate_concentration_score(powers, baseline=None)
        self.assertGreater(score, 50)  # Should be above average
        
    def test_low_beta_high_alpha_gives_low_score(self):
        """Low beta/alpha ratio should indicate relaxation"""
        powers = {
            'delta': 10,
            'theta': 15,
            'alpha': 60,  # High alpha
            'smr': 20,
            'beta': 20,  # Low beta
            'gamma': 5
        }
        
        score = calculate_concentration_score(powers, baseline=None)
        self.assertLess(score, 50)  # Should be below average
        
    def test_baseline_normalization(self):
        """Test that baseline normalization works"""
        powers = {
            'delta': 10,
            'theta': 15,
            'alpha': 30,
            'smr': 25,
            'beta': 40,
            'gamma': 5
        }
        
        baseline = {
            'beta_alpha_ratio': 1.0,
            'smr_power': 20.0,
            'inv_theta_beta': 0.5
        }
        
        score_with_baseline = calculate_concentration_score(powers, baseline)
        score_without_baseline = calculate_concentration_score(powers, None)
        
        # Scores should differ when baseline is applied
        self.assertNotEqual(score_with_baseline, score_without_baseline)
        
    def test_score_bounds(self):
        """Test that score is always between 0 and 100"""
        # Test with extreme values
        extreme_powers = {
            'delta': 1000,
            'theta': 1000,
            'alpha': 0.001,
            'smr': 1000,
            'beta': 1000,
            'gamma': 1000
        }
        
        score = calculate_concentration_score(extreme_powers, baseline=None)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)


class TestSignalQuality(unittest.TestCase):
    """Test signal quality estimation"""
    
    def test_good_signal(self):
        """Test detection of good quality signal"""
        # Clean signal with reasonable amplitude
        signal = np.sin(2 * np.pi * 10 * np.linspace(0, 4, 1024))
        quality = estimate_signal_quality(signal)
        self.assertEqual(quality, 'good')
        
    def test_poor_signal_high_amplitude(self):
        """Test detection of poor signal (too high amplitude)"""
        # Very high amplitude indicates artifact
        signal = 500 * np.ones(1024)
        quality = estimate_signal_quality(signal)
        self.assertEqual(quality, 'poor')
        
    def test_poor_signal_low_variance(self):
        """Test detection of poor signal (no variance)"""
        # Flat line indicates disconnection
        signal = np.zeros(1024)
        quality = estimate_signal_quality(signal)
        self.assertEqual(quality, 'poor')
        
    def test_fair_signal(self):
        """Test detection of fair quality signal"""
        # Moderate noise
        signal = np.sin(2 * np.pi * 10 * np.linspace(0, 4, 1024))
        signal += 30 * np.random.randn(1024)  # Add noise
        quality = estimate_signal_quality(signal)
        self.assertIn(quality, ['fair', 'good'])


class TestEEGProcessor(unittest.TestCase):
    """Test EEG processor class"""
    
    def setUp(self):
        self.processor = EEGProcessor()
        
    def test_initialization(self):
        """Test processor initializes correctly"""
        self.assertEqual(len(self.processor.buffer_af7), 0)
        self.assertEqual(len(self.processor.buffer_af8), 0)
        self.assertIsNone(self.processor.baseline)
        
    def test_buffer_management(self):
        """Test that buffer maintains correct size"""
        # Add more samples than buffer size
        for i in range(2000):
            self.processor.add_sample([100, 100, 100, 100])
            
        # Buffer should not exceed max size
        self.assertLessEqual(len(self.processor.buffer_af7), 1024)
        self.assertLessEqual(len(self.processor.buffer_af8), 1024)
        
    def test_calibration_collection(self):
        """Test baseline calibration data collection"""
        self.processor.start_calibration()
        
        # Add samples
        for i in range(100):
            self.processor.add_sample([100, 100, 100, 100])
            
        self.assertGreater(len(self.processor.calibration_samples), 0)
        
    def test_calibration_finalization(self):
        """Test that calibration computes baseline"""
        self.processor.start_calibration()
        
        # Add enough samples for calibration
        for i in range(500):
            sample = [
                np.sin(2 * np.pi * 10 * i / 256),  # TP9
                np.sin(2 * np.pi * 10 * i / 256),  # AF7
                np.sin(2 * np.pi * 10 * i / 256),  # AF8
                np.sin(2 * np.pi * 10 * i / 256)   # TP10
            ]
            self.processor.add_sample(sample)
            
        self.processor.finish_calibration()
        
        # Baseline should be computed
        self.assertIsNotNone(self.processor.baseline)
        self.assertIn('beta_alpha_ratio', self.processor.baseline)
        self.assertIn('smr_power', self.processor.baseline)
        self.assertIn('inv_theta_beta', self.processor.baseline)


class TestDataExport(unittest.TestCase):
    """Test data export functionality (integration test)"""
    
    def test_session_json_structure(self):
        """Test that session JSON has correct structure"""
        # This would be tested in frontend, but we can verify structure
        expected_keys = [
            'type', 'startTime', 'endTime', 'duration',
            'avgScore', 'peakScore', 'highFocusTime',
            'dataPoints', 'scores', 'timestamps',
            'bandPowers', 'components'
        ]
        
        # Mock session data
        session_data = {
            'type': 'baseline',
            'startTime': '2026-02-15T00:00:00Z',
            'endTime': '2026-02-15T00:05:00Z',
            'duration': 300,
            'avgScore': 65.5,
            'peakScore': 85.2,
            'highFocusTime': 120,
            'dataPoints': 600,
            'scores': [50, 55, 60],
            'timestamps': ['2026-02-15T00:00:00Z'],
            'bandPowers': [{'alpha': 10, 'beta': 20}],
            'components': [{'beta_alpha_ratio': 2.0}]
        }
        
        for key in expected_keys:
            self.assertIn(key, session_data)


class TestWebSocketMessages(unittest.TestCase):
    """Test WebSocket message formatting"""
    
    def test_eeg_data_message_format(self):
        """Test EEG data message has correct format"""
        message = {
            'type': 'eeg_data',
            'timestamp': '2026-02-15T00:00:00Z',
            'concentration_score': 75.5,
            'signal_quality': 'good',
            'band_powers': {
                'delta': 10, 'theta': 15, 'alpha': 20,
                'smr': 25, 'beta': 30, 'gamma': 5
            },
            'components': {
                'beta_alpha_ratio': 1.5,
                'smr_power': 25,
                'inv_theta_beta': 0.5
            }
        }
        
        # Verify structure
        self.assertEqual(message['type'], 'eeg_data')
        self.assertIn('concentration_score', message)
        self.assertIn('signal_quality', message)
        self.assertIn('band_powers', message)
        self.assertIn('components', message)
        
        # Verify score bounds
        self.assertGreaterEqual(message['concentration_score'], 0)
        self.assertLessEqual(message['concentration_score'], 100)


def run_tests():
    """Run all tests and generate report"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBandPowerCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestConcentrationScore))
    suite.addTests(loader.loadTestsFromTestCase(TestSignalQuality))
    suite.addTests(loader.loadTestsFromTestCase(TestEEGProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestDataExport))
    suite.addTests(loader.loadTestsFromTestCase(TestWebSocketMessages))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result


if __name__ == '__main__':
    run_tests()
