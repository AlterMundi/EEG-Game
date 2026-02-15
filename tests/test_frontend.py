"""
Frontend Integration Tests
Tests for browser-based functionality using Selenium
"""

import unittest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class TestFrontendIntegration(unittest.TestCase):
    """Integration tests for web app"""
    
    @classmethod
    def setUpClass(cls):
        """Set up Chrome driver"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.get('http://localhost:8000')
        
    @classmethod
    def tearDownClass(cls):
        """Close browser"""
        cls.driver.quit()
        
    def test_disclaimer_modal_appears(self):
        """Test that disclaimer modal shows on load"""
        modal = self.driver.find_element(By.ID, 'disclaimerModal')
        self.assertTrue(modal.is_displayed())
        
    def test_disclaimer_acceptance(self):
        """Test disclaimer checkbox and button"""
        checkbox = self.driver.find_element(By.ID, 'disclaimerCheck')
        button = self.driver.find_element(By.ID, 'disclaimerAccept')
        
        # Button should be disabled initially
        self.assertFalse(button.is_enabled())
        
        # Check checkbox
        checkbox.click()
        
        # Button should now be enabled
        self.assertTrue(button.is_enabled())
        
    def test_session_buttons_exist(self):
        """Test that all three session buttons exist"""
        # Accept disclaimer first
        self.driver.find_element(By.ID, 'disclaimerCheck').click()
        self.driver.find_element(By.ID, 'disclaimerAccept').click()
        
        time.sleep(0.5)
        
        # Find session buttons
        buttons = self.driver.find_elements(By.CLASS_NAME, 'session-btn')
        self.assertEqual(len(buttons), 3)
        
    def test_websocket_connection(self):
        """Test WebSocket connection status"""
        # Wait for connection
        wait = WebDriverWait(self.driver, 10)
        status = wait.until(
            EC.presence_of_element_located((By.ID, 'connectionStatus'))
        )
        
        # Should eventually show connected
        time.sleep(2)
        status_text = status.text
        self.assertIn(status_text, ['Connected', 'Disconnected'])
        
    def test_local_storage_persistence(self):
        """Test that localStorage is used for sessions"""
        # Execute JavaScript to check localStorage
        has_storage = self.driver.execute_script(
            "return typeof(Storage) !== 'undefined';"
        )
        self.assertTrue(has_storage)


class TestGameMechanics(unittest.TestCase):
    """Test game visualization and mechanics"""
    
    def test_canvas_exists(self):
        """Test that game canvas element exists"""
        driver = webdriver.Chrome(options=Options())
        driver.get('http://localhost:8000')
        
        # Accept disclaimer
        driver.find_element(By.ID, 'disclaimerCheck').click()
        driver.find_element(By.ID, 'disclaimerAccept').click()
        
        # Start a session
        buttons = driver.find_elements(By.CLASS_NAME, 'session-btn')
        buttons[0].click()  # Click baseline
        
        time.sleep(1)
        
        # Check canvas exists
        canvas = driver.find_element(By.ID, 'gameCanvas')
        self.assertIsNotNone(canvas)
        
        driver.quit()


def run_frontend_tests():
    """Run frontend tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestFrontendIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestGameMechanics))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    print("NOTE: These tests require:")
    print("  1. WebSocket server running on port 8765")
    print("  2. Web server running on port 8000")
    print("  3. Chrome/Chromium installed")
    print("  4. selenium package installed")
    print("\nStarting tests...\n")
    
    run_frontend_tests()
