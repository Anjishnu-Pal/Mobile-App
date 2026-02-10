"""
JNI Interface for Android sensor communication via NHS 3152 chip using NFC
This interface communicates with native C/C++ code through JNI for NFC data exchange
"""

import json
from datetime import datetime
from typing import Optional, Dict
import random


class SensorInterface:
    """Interface for communicating with NHS 3152 sensor via NFC and JNI"""
    
    def __init__(self):
        self.connected = False
        self.nfc_enabled = False
        self.config = {
            'nfc_mode': True,  # NFC enabled by default
            'nfc_reader_presence_check': 250,  # milliseconds
            'nfc_timeout': 3000,  # milliseconds
            'temp_offset': 0.0,
            'ph_calibration': 7.0,
            'glucose_calibration': 100.0,
            'auto_detect': True,  # Auto-detect NFC tags
        }
        
        # Try to import JNI bridge
        try:
            from android_jni.sensor_bridge import SensorBridge
            self.bridge = SensorBridge()
        except ImportError:
            print("Warning: Running without JNI bridge. Using mock data for testing.")
            self.bridge = None
    
    def connect(self) -> bool:
        """Establish NFC connection to NHS 3152 sensor tag"""
        try:
            if self.bridge:
                result = self.bridge.connect(self.config)
                self.connected = result
                self.nfc_enabled = result
                return result
            else:
                print("JNI bridge not available - running in test mode")
                self.connected = False
                return False
        except Exception as e:
            print(f"Error connecting to NFC: {e}")
            self.connected = False
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from sensor"""
        try:
            if self.bridge:
                self.bridge.disconnect()
            self.connected = False
            return True
        except Exception as e:
            print(f"Error disconnecting: {e}")
            return False
    
    def read_sensor_data(self) -> Optional[Dict]:
        """Read current sensor data from NHS 3152 NFC tag"""
        if not self.connected:
            if not self.connect():
                print("Not connected to NFC reader")
                return self._get_mock_data()  # Return mock data for testing
        
        try:
            if self.bridge:
                # Get sensor data from last NFC tag read
                sensor_data = self.bridge.getSensorReading()
                
                if sensor_data:
                    return {
                        'timestamp': datetime.now().isoformat(),
                        'temperature': sensor_data[0],
                        'ph': sensor_data[1],
                        'glucose': sensor_data[2]
                    }
                else:
                    print("No NFC tag detected - waiting for tag...")
                    return None
            else:
                return self._get_mock_data()
        except Exception as e:
            print(f"Error reading sensor data: {e}")
            return None
    
    def _get_mock_data(self) -> Dict:
        """Return mock sensor data for testing (no hardware)"""
        return {
            'timestamp': datetime.now().isoformat(),
            'temperature': 36.5 + random.uniform(-1, 1),
            'ph': 7.0 + random.uniform(-0.5, 0.5),
            'glucose': 100 + random.randint(-20, 20)
        }
    
    def update_configuration(self, config: Dict) -> bool:
        """Update sensor and NFC configuration"""
        try:
            self.config.update(config)
            if self.bridge and self.connected:
                if 'temp_offset' in config:
                    self.bridge.updateConfig(config)
            return True
        except Exception as e:
            print(f"Error updating configuration: {e}")
            return False
    
    def calibrate_sensors(self) -> bool:
        """
        Calibrate sensors via NFC
        Requires NFC tag to be in read/write range
        """
        try:
            if self.bridge:
                return self.bridge.calibrate()
            return False
        except Exception as e:
            print(f"Error during calibration: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test NFC reader connection and tag detection"""
        try:
            if not self.connected:
                if not self.connect():
                    return False
            
            if self.bridge:
                return self.bridge.testConnection()
            return True
        except Exception as e:
            print(f"Error testing connection: {e}")
            return False
    
    def get_nfc_status(self) -> str:
        """Get NFC reader and tag status"""
        try:
            if self.bridge:
                return self.bridge.getFirmwareVersion()
            return "NFC Bridge Not Available"
        except Exception as e:
            print(f"Error getting NFC status: {e}")
            return "Error"
    
    def enable_nfc_reader_mode(self) -> bool:
        """Enable NFC reader mode for background scanning"""
        try:
            if self.bridge and self.connected:
                # Reader mode is enabled in Java's enableReaderMode()
                self.nfc_enabled = True
                return True
            return False
        except Exception as e:
            print(f"Error enabling NFC reader: {e}")
            return False
    
    def disable_nfc_reader_mode(self) -> bool:
        """Disable NFC reader mode"""
        try:
            if self.bridge:
                # Reader mode is disabled in Java's disableReaderMode()
                self.nfc_enabled = False
                self.disconnect()
                return True
            return False
        except Exception as e:
            print(f"Error disabling NFC reader: {e}")
            return False
    
    def is_nfc_available(self) -> bool:
        """Check if device has NFC hardware"""
        try:
            if self.bridge:
                status = self.get_nfc_status()
                return "Not Connected" not in status and "Error" not in status
            return False
        except Exception as e:
            print(f"Error checking NFC availability: {e}")
            return False
    
    def is_nfc_enabled(self) -> bool:
        """Check if NFC is currently enabled"""
        return self.nfc_enabled
    
    def get_status(self) -> Dict:
        """Get complete sensor and NFC status"""
        return {
            'connected': self.connected,
            'nfc_enabled': self.nfc_enabled,
            'nfc_status': self.get_nfc_status(),
            'config': self.config.copy(),
            'communication_mode': 'NFC'
        }
