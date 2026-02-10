"""
Dashboard screen showing live sensor readings
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.progressbar import ProgressBar


class DashboardScreen(BoxLayout):
    """Live dashboard displaying current sensor readings"""
    
    def __init__(self, sensor_interface, sensor_data, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        self.sensor_interface = sensor_interface
        self.sensor_data = sensor_data
        
        # Title
        title = Label(text='Live Sensor Dashboard', size_hint_y=0.15, bold=True, font_size='20sp')
        self.add_widget(title)
        
        # Temperature Card
        temp_layout = BoxLayout(orientation='vertical', size_hint_y=0.25, padding=5)
        temp_layout.canvas.before.clear()
        self.temp_label = Label(text='Temperature\n-- °C', bold=True, font_size='18sp')
        self.temp_bar = ProgressBar(max=50, value=25)
        temp_layout.add_widget(self.temp_label)
        temp_layout.add_widget(self.temp_bar)
        self.add_widget(temp_layout)
        
        # pH Card
        ph_layout = BoxLayout(orientation='vertical', size_hint_y=0.25, padding=5)
        self.ph_label = Label(text='pH Level\n-- ', bold=True, font_size='18sp')
        self.ph_bar = ProgressBar(max=14, value=7)
        ph_layout.add_widget(self.ph_label)
        ph_layout.add_widget(self.ph_bar)
        self.add_widget(ph_layout)
        
        # Glucose Card
        glucose_layout = BoxLayout(orientation='vertical', size_hint_y=0.25, padding=5)
        self.glucose_label = Label(text='Glucose Level\n-- mg/dL', bold=True, font_size='18sp')
        self.glucose_bar = ProgressBar(max=300, value=100)
        glucose_layout.add_widget(self.glucose_label)
        glucose_layout.add_widget(self.glucose_bar)
        self.add_widget(glucose_layout)
        
        # Control buttons
        btn_layout = BoxLayout(size_hint_y=0.15, spacing=5)
        
        start_btn = Button(text='Start Monitoring')
        start_btn.bind(on_press=self.start_monitoring)
        btn_layout.add_widget(start_btn)
        
        stop_btn = Button(text='Stop Monitoring')
        stop_btn.bind(on_press=self.stop_monitoring)
        btn_layout.add_widget(stop_btn)
        
        self.add_widget(btn_layout)
        
        # Schedule updates
        self.update_event = None
    
    def start_monitoring(self, instance):
        """Start monitoring sensors"""
        if self.update_event is None:
            self.update_event = Clock.schedule_interval(self.update_dashboard, 2)
    
    def stop_monitoring(self, instance):
        """Stop monitoring sensors"""
        if self.update_event:
            self.update_event.cancel()
            self.update_event = None
    
    def update_dashboard(self, dt):
        """Update dashboard values"""
        readings = self.sensor_data.get_all_readings()
        if readings:
            latest = readings[-1]
            
            # Update temperature
            self.temp_label.text = f'Temperature\n{latest.temperature:.1f} °C'
            self.temp_bar.value = min(latest.temperature, 50)
            
            # Update pH
            self.ph_label.text = f'pH Level\n{latest.ph:.1f}'
            self.ph_bar.value = min(latest.ph, 14)
            
            # Update Glucose
            self.glucose_label.text = f'Glucose Level\n{latest.glucose:.1f} mg/dL'
            self.glucose_bar.value = min(latest.glucose, 300)
