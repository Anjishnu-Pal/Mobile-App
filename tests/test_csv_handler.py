"""
Unit tests for CSVHandler module
"""

import unittest
import tempfile
import os
from datetime import datetime
from data_management.csv_handler import CSVHandler


class TestCSVHandler(unittest.TestCase):
    """Test CSVHandler class"""
    
    def setUp(self):
        """Create temporary directory for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.csv_handler = CSVHandler(self.temp_dir)
    
    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_save_reading(self):
        """Test saving a single reading"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'temperature': 36.5,
            'ph': 7.0,
            'glucose': 100
        }
        result = self.csv_handler.save_sensor_reading(data)
        self.assertTrue(result)
    
    def test_load_readings(self):
        """Test loading readings"""
        # Save some data
        for i in range(3):
            self.csv_handler.save_sensor_reading({
                'timestamp': datetime.now().isoformat(),
                'temperature': 36.0 + i,
                'ph': 7.0,
                'glucose': 100
            })
        
        # Load and verify
        readings = self.csv_handler.load_sensor_readings()
        self.assertEqual(len(readings), 3)
    
    def test_get_available_dates(self):
        """Test getting available dates"""
        self.csv_handler.save_sensor_reading({
            'timestamp': datetime.now().isoformat(),
            'temperature': 36.5,
            'ph': 7.0,
            'glucose': 100
        })
        
        dates = self.csv_handler.get_available_dates()
        self.assertGreater(len(dates), 0)


if __name__ == '__main__':
    unittest.main()
