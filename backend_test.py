import requests
import unittest
import os
import sys
from pathlib import Path

class FileManagerAppTest(unittest.TestCase):
    """Test suite for the File Manager Streamlit application."""
    
    def setUp(self):
        """Set up test environment."""
        # The Streamlit app runs on port 8501 by default
        self.base_url = "http://localhost:8501"
        
    def test_app_is_running(self):
        """Test if the Streamlit app is running and accessible."""
        try:
            response = requests.get(self.base_url)
            self.assertEqual(response.status_code, 200, "Streamlit app is not running")
            print("✅ Streamlit app is running and accessible")
        except requests.exceptions.ConnectionError:
            self.fail("Could not connect to Streamlit app. Make sure it's running on port 8501.")
    
    def test_streamlit_api_endpoints(self):
        """Test Streamlit API endpoints."""
        try:
            # Test the _stcore/health endpoint which Streamlit provides
            response = requests.get(f"{self.base_url}/_stcore/health")
            self.assertEqual(response.status_code, 200, "Streamlit health check failed")
            print("✅ Streamlit health check passed")
        except requests.exceptions.ConnectionError:
            self.fail("Could not connect to Streamlit API endpoints.")

def main():
    """Run the test suite."""
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

if __name__ == "__main__":
    main()