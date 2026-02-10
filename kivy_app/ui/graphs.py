"""
Graphs screen for data visualization
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from datetime import datetime, timedelta


class GraphsScreen(BoxLayout):
    """Screen for displaying sensor data analysis"""
    
    def __init__(self, csv_handler, sensor_data, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        self.csv_handler = csv_handler
        self.sensor_data = sensor_data
        self.current_graph = None
        
        # Title
        title = Label(text='Sensor Data Analysis', size_hint_y=0.1, bold=True, font_size='18sp')
        self.add_widget(title)
        
        # Data display area with scrolling
        scroll = ScrollView(size_hint_y=0.7)
        self.data_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.data_layout.bind(minimum_height=self.data_layout.setter('height'))
        scroll.add_widget(self.data_layout)
        self.add_widget(scroll)
        
        # Button layout for data selection
        btn_layout = BoxLayout(size_hint_y=0.2, spacing=5)
        
        temp_btn = Button(text='Temperature', size_hint_y=None, height=50)
        temp_btn.bind(on_press=self.show_temperature)
        btn_layout.add_widget(temp_btn)
        
        ph_btn = Button(text='pH Level', size_hint_y=None, height=50)
        ph_btn.bind(on_press=self.show_ph)
        btn_layout.add_widget(ph_btn)
        
        glucose_btn = Button(text='Glucose Level', size_hint_y=None, height=50)
        glucose_btn.bind(on_press=self.show_glucose)
        btn_layout.add_widget(glucose_btn)
        
        all_btn = Button(text='All Data', size_hint_y=None, height=50)
        all_btn.bind(on_press=self.show_all)
        btn_layout.add_widget(all_btn)
        
        self.add_widget(btn_layout)
    
    def show_temperature(self, instance):
        """Display temperature data"""
        readings = self.sensor_data.get_all_readings()
        if not readings:
            self._display_message("No temperature data available")
            return
        
        self.data_layout.clear_widgets()
        header = Label(text='Time | Temperature (°C)', size_hint_y=None, height=40, bold=True)
        self.data_layout.add_widget(header)
        
        for r in readings:
            text = f"{r.timestamp.strftime('%H:%M:%S')} | {r.temperature:.2f}°C"
            label = Label(text=text, size_hint_y=None, height=30)
            self.data_layout.add_widget(label)
    
    def show_ph(self, instance):
        """Display pH data"""
        readings = self.sensor_data.get_all_readings()
        if not readings:
            self._display_message("No pH data available")
            return
        
        self.data_layout.clear_widgets()
        header = Label(text='Time | pH Level', size_hint_y=None, height=40, bold=True)
        self.data_layout.add_widget(header)
        
        for r in readings:
            text = f"{r.timestamp.strftime('%H:%M:%S')} | {r.ph:.2f}"
            label = Label(text=text, size_hint_y=None, height=30)
            self.data_layout.add_widget(label)
    
    def show_glucose(self, instance):
        """Display glucose data"""
        readings = self.sensor_data.get_all_readings()
        if not readings:
            self._display_message("No glucose data available")
            return
        
        self.data_layout.clear_widgets()
        header = Label(text='Time | Glucose (mg/dL)', size_hint_y=None, height=40, bold=True)
        self.data_layout.add_widget(header)
        
        for r in readings:
            text = f"{r.timestamp.strftime('%H:%M:%S')} | {r.glucose:.0f}"
            label = Label(text=text, size_hint_y=None, height=30)
            self.data_layout.add_widget(label)
    
    def show_all(self, instance):
        """Display all sensor data"""
        readings = self.sensor_data.get_all_readings()
        if not readings:
            self._display_message("No sensor data available")
            return
        
        self.data_layout.clear_widgets()
        header = Label(text='Time | Temp (°C) | pH | Glucose (mg/dL)', size_hint_y=None, height=40, bold=True)
        self.data_layout.add_widget(header)
        
        for r in readings:
            text = f"{r.timestamp.strftime('%H:%M:%S')} | {r.temperature:.2f} | {r.ph:.2f} | {r.glucose:.0f}"
            label = Label(text=text, size_hint_y=None, height=30)
            self.data_layout.add_widget(label)
    
    def _display_message(self, message):
        """Display a message in the data layout"""
        self.data_layout.clear_widgets()
        msg_label = Label(text=message, size_hint_y=None, height=50)
        self.data_layout.add_widget(msg_label)
