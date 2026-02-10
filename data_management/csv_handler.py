"""
CSV data handler for persistent storage
"""

import csv
import os
from datetime import datetime
from pathlib import Path
from typing import List
from data_management.sensor_data import SensorReading


class CSVHandler:
    """Handles reading and writing sensor data to CSV files"""
    
    def __init__(self, storage_path: str = './sensor_data'):
        """Initialize CSV handler"""
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Create daily CSV file names
        self.current_date = datetime.now().date()
        self.csv_file = self.storage_path / f"sensor_data_{self.current_date}.csv"
        
        # Initialize CSV file if it doesn't exist
        self._initialize_csv_file()
    
    def _initialize_csv_file(self):
        """Create CSV file with headers if it doesn't exist"""
        if not self.csv_file.exists():
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['timestamp', 'temperature', 'ph', 'glucose']
                )
                writer.writeheader()
    
    def save_sensor_reading(self, data: dict) -> bool:
        """Save a single sensor reading to CSV"""
        try:
            # Check if we need to create a new daily file
            today = datetime.now().date()
            if today != self.current_date:
                self.current_date = today
                self.csv_file = self.storage_path / f"sensor_data_{self.current_date}.csv"
                self._initialize_csv_file()
            
            with open(self.csv_file, 'a', newline='') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['timestamp', 'temperature', 'ph', 'glucose']
                )
                writer.writerow({
                    'timestamp': data.get('timestamp', datetime.now().isoformat()),
                    'temperature': data.get('temperature', 0),
                    'ph': data.get('ph', 7.0),
                    'glucose': data.get('glucose', 0)
                })
            return True
        except Exception as e:
            print(f"Error saving sensor reading: {e}")
            return False
    
    def load_sensor_readings(self, date=None) -> List[dict]:
        """Load sensor readings from CSV"""
        try:
            if date is None:
                date = datetime.now().date()
            
            csv_file = self.storage_path / f"sensor_data_{date}.csv"
            
            if not csv_file.exists():
                return []
            
            readings = []
            with open(csv_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    readings.append({
                        'timestamp': datetime.fromisoformat(row['timestamp']),
                        'temperature': float(row['temperature']),
                        'ph': float(row['ph']),
                        'glucose': float(row['glucose'])
                    })
            return readings
        except Exception as e:
            print(f"Error loading sensor readings: {e}")
            return []
    
    def load_all_readings(self) -> List[dict]:
        """Load all sensor readings from all CSV files"""
        all_readings = []
        try:
            for csv_file in sorted(self.storage_path.glob('sensor_data_*.csv')):
                with open(csv_file, 'r', newline='') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        all_readings.append({
                            'timestamp': datetime.fromisoformat(row['timestamp']),
                            'temperature': float(row['temperature']),
                            'ph': float(row['ph']),
                            'glucose': float(row['glucose'])
                        })
        except Exception as e:
            print(f"Error loading all readings: {e}")
        
        return all_readings
    
    def export_all_data(self, readings: List[SensorReading], filename: str = None) -> str:
        """Export all readings to a named CSV file"""
        try:
            if filename is None:
                filename = f"sensor_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            export_path = self.storage_path / filename
            
            with open(export_path, 'w', newline='') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['timestamp', 'temperature', 'ph', 'glucose']
                )
                writer.writeheader()
                
                for reading in readings:
                    writer.writerow({
                        'timestamp': reading.timestamp.isoformat(),
                        'temperature': reading.temperature,
                        'ph': reading.ph,
                        'glucose': reading.glucose
                    })
            
            return str(export_path)
        except Exception as e:
            print(f"Error exporting data: {e}")
            return ""
    
    def get_storage_path(self) -> str:
        """Get the storage directory path"""
        return str(self.storage_path)
    
    def get_available_dates(self) -> List[str]:
        """Get list of dates with available data"""
        dates = []
        try:
            for csv_file in sorted(self.storage_path.glob('sensor_data_*.csv')):
                # Extract date from filename
                date_str = csv_file.stem.replace('sensor_data_', '')
                dates.append(date_str)
        except Exception as e:
            print(f"Error getting available dates: {e}")
        
        return dates
