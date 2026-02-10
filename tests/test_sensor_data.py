"""
Unit tests for SensorData module
"""

import unittest
from datetime import datetime
from data_management.sensor_data import SensorData, SensorReading


class TestSensorData(unittest.TestCase):
    """Test SensorData class"""
    
    def setUp(self):
        self.sensor_data = SensorData()
    
    def test_add_reading(self):
        """Test adding a sensor reading"""
        data = {
            'timestamp': datetime.now(),
            'temperature': 36.5,
            'ph': 7.0,
            'glucose': 100
        }
        self.sensor_data.add_reading(data)
        self.assertEqual(len(self.sensor_data.get_all_readings()), 1)
    
    def test_get_recent_readings(self):
        """Test getting recent readings"""
        for i in range(10):
            self.sensor_data.add_reading({
                'temperature': 36.0 + i,
                'ph': 7.0,
                'glucose': 100
            })
        
        recent = self.sensor_data.get_recent_readings(5)
        self.assertEqual(len(recent), 5)
    
    def test_statistics(self):
        """Test statistics calculation"""
        for i in range(5):
            self.sensor_data.add_reading({
                'temperature': 36.0 + i,
                'ph': 7.0,
                'glucose': 100
            })
        
        stats = self.sensor_data.get_statistics()
        self.assertIn('temperature', stats)
        self.assertEqual(stats['temperature']['min'], 36.0)
        self.assertEqual(stats['temperature']['max'], 40.0)
    
    def test_clear_readings(self):
        """Test clearing readings"""
        self.sensor_data.add_reading({'temperature': 36.5, 'ph': 7.0, 'glucose': 100})
        self.assertEqual(len(self.sensor_data.get_all_readings()), 1)
        
        self.sensor_data.clear_readings()
        self.assertEqual(len(self.sensor_data.get_all_readings()), 0)


if __name__ == '__main__':
    unittest.main()
