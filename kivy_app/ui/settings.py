"""
Settings screen for app configuration with NFC support
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox


class SettingsScreen(BoxLayout):
    """Settings screen for app configuration"""
    
    def __init__(self, sensor_interface, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        self.sensor_interface = sensor_interface
        
        # Title
        title = Label(text='NFC Settings & Configuration', size_hint_y=0.1, bold=True, font_size='18sp')
        self.add_widget(title)
        
        # Settings grid
        settings_grid = GridLayout(cols=2, spacing=10, size_hint_y=0.7)
        
        # NFC Mode (Always On)
        settings_grid.add_widget(Label(text='NFC Mode:'))
        nfc_layout = BoxLayout(size_hint_x=1)
        self.nfc_enabled = CheckBox(active=True)
        nfc_layout.add_widget(self.nfc_enabled)
        nfc_layout.add_widget(Label(text='Enabled'))
        settings_grid.add_widget(nfc_layout)
        
        # NFC Reader Presence Check Delay
        settings_grid.add_widget(Label(text='Reader Presence Check (ms):'))
        self.reader_delay_input = TextInput(text='250', multiline=False, input_filter='int')
        settings_grid.add_widget(self.reader_delay_input)
        
        # NFC Timeout
        settings_grid.add_widget(Label(text='NFC Timeout (ms):'))
        self.nfc_timeout_input = TextInput(text='3000', multiline=False, input_filter='int')
        settings_grid.add_widget(self.nfc_timeout_input)
        
        # Auto-detect Tags
        settings_grid.add_widget(Label(text='Auto-detect Tags:'))
        auto_layout = BoxLayout(size_hint_x=1)
        self.auto_detect = CheckBox(active=True)
        auto_layout.add_widget(self.auto_detect)
        auto_layout.add_widget(Label(text='Enabled'))
        settings_grid.add_widget(auto_layout)
        
        # Temperature Unit
        settings_grid.add_widget(Label(text='Temperature Unit:'))
        self.temp_spinner = Spinner(
            text='Celsius',
            values=('Celsius', 'Fahrenheit')
        )
        settings_grid.add_widget(self.temp_spinner)
        
        # Data Storage Path
        settings_grid.add_widget(Label(text='Data Storage Path:'))
        self.path_input = TextInput(text='/sdcard/SensorMonitor/', multiline=False)
        settings_grid.add_widget(self.path_input)
        
        # Calibration Options
        settings_grid.add_widget(Label(text='Temperature Offset (°C):'))
        self.temp_offset_input = TextInput(text='0.0', multiline=False)
        settings_grid.add_widget(self.temp_offset_input)
        
        # pH Calibration Point
        settings_grid.add_widget(Label(text='pH Calibration (neutral):'))
        self.ph_calibration_input = TextInput(text='7.0', multiline=False)
        settings_grid.add_widget(self.ph_calibration_input)
        
        self.add_widget(settings_grid)
        
        # Button layout
        btn_layout = BoxLayout(size_hint_y=0.2, spacing=5)
        
        save_btn = Button(text='Save Settings')
        save_btn.bind(on_press=self.save_settings)
        btn_layout.add_widget(save_btn)
        
        calibrate_btn = Button(text='Calibrate via NFC')
        calibrate_btn.bind(on_press=self.calibrate_sensors)
        btn_layout.add_widget(calibrate_btn)
        
        test_btn = Button(text='Test NFC')
        test_btn.bind(on_press=self.test_connection)
        btn_layout.add_widget(test_btn)
        
        self.add_widget(btn_layout)
    
    def save_settings(self, instance):
        """Save settings"""
        settings = {
            'nfc_mode': self.nfc_enabled.active,
            'nfc_reader_presence_check': int(self.reader_delay_input.text),
            'nfc_timeout': int(self.nfc_timeout_input.text),
            'auto_detect': self.auto_detect.active,
            'temp_unit': self.temp_spinner.text,
            'storage_path': self.path_input.text,
            'temp_offset': float(self.temp_offset_input.text),
            'ph_calibration': float(self.ph_calibration_input.text)
        }
        
        try:
            self.sensor_interface.update_configuration(settings)
            print("✓ NFC settings saved successfully")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def calibrate_sensors(self, instance):
        """Calibrate sensors via NFC tag"""
        try:
            print("Hold NFC tag near device for calibration...")
            result = self.sensor_interface.calibrate_sensors()
            if result:
                print("✓ NFC calibration completed")
            else:
                print("✗ Calibration failed - check NFC tag")
        except Exception as e:
            print(f"Error during calibration: {e}")
    
    def test_connection(self, instance):
        """Test NFC connection"""
        try:
            print("Testing NFC reader connection...")
            
            # Check if NFC is available
            if not self.sensor_interface.is_nfc_available():
                print("✗ NFC hardware not available")
                return
            
            # Test connection
            if self.sensor_interface.test_connection():
                print("✓ NFC reader is active and ready")
                status = self.sensor_interface.get_nfc_status()
                print(f"Status: {status}")
            else:
                print("✗ NFC connection test failed")
                print("Waiting for NFC tag to be detected...")
        except Exception as e:
            print(f"Error testing connection: {e}")

