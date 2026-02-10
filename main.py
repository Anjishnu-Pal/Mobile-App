"""
SensorMonitor: Mobile App for Health Sensor Data Monitoring
Monitors Temperature, pH, and Glucose levels using NHS 3152 sensors
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
import threading

from kivy_app.ui.main_screen import MainScreen
from kivy_app.ui.dashboard import DashboardScreen
from kivy_app.ui.graphs import GraphsScreen
from kivy_app.ui.settings import SettingsScreen
from android_jni.sensor_interface import SensorInterface
from data_management.csv_handler import CSVHandler
from data_management.sensor_data import SensorData


class SensorMonitorApp(App):
    """Main Kivy application for sensor monitoring"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "SensorMonitor - Health Sensor Dashboard"
        self.sensor_interface = None
        self.csv_handler = None
        self.sensor_data = None
        self.data_update_event = None
        
    def build(self):
        """Build the main UI"""
        # Initialize sensor interface and data management
        self.sensor_interface = SensorInterface()
        self.csv_handler = CSVHandler()
        self.sensor_data = SensorData()
        
        # Create main tab panel
        main_layout = TabbedPanel()
        
        # Dashboard Tab
        dashboard_tab = TabbedPanelItem(text='Dashboard')
        dashboard_tab.content = DashboardScreen(
            sensor_interface=self.sensor_interface,
            sensor_data=self.sensor_data
        )
        main_layout.add_widget(dashboard_tab)
        
        # Data View Tab
        data_tab = TabbedPanelItem(text='Data')
        data_tab.content = MainScreen(
            csv_handler=self.csv_handler,
            sensor_data=self.sensor_data
        )
        main_layout.add_widget(data_tab)
        
        # Graphs Tab
        graphs_tab = TabbedPanelItem(text='Graphs')
        graphs_tab.content = GraphsScreen(
            csv_handler=self.csv_handler,
            sensor_data=self.sensor_data
        )
        main_layout.add_widget(graphs_tab)
        
        # Settings Tab
        settings_tab = TabbedPanelItem(text='Settings')
        settings_tab.content = SettingsScreen(
            sensor_interface=self.sensor_interface
        )
        main_layout.add_widget(settings_tab)
        
        # Schedule data updates
        self.data_update_event = Clock.schedule_interval(
            self.update_sensor_data, 5  # Update every 5 seconds
        )
        
        return main_layout
    
    def update_sensor_data(self, dt):
        """Periodically update sensor data"""
        try:
            # Read from sensors via JNI
            data = self.sensor_interface.read_sensor_data()
            
            if data:
                # Store in sensor data object
                self.sensor_data.add_reading(data)
                
                # Save to CSV
                self.csv_handler.save_sensor_reading(data)
                
        except Exception as e:
            print(f"Error updating sensor data: {e}")
    
    def on_stop(self):
        """Stop the app"""
        if self.data_update_event:
            self.data_update_event.cancel()
        return True


if __name__ == '__main__':
    app = SensorMonitorApp()
    app.run()
