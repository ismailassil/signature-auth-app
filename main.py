from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.clock import Clock
import os

# Import screens
from app.ui.dashboard import DashboardScreen
from app.ui.guide import GuideScreen

class SignatureAuthApp(App):
    def build(self):
        # Set window size for mobile (will be fullscreen on actual device)
        Window.size = (360, 640)
        
        # Create screen manager
        self.sm = ScreenManager(transition=FadeTransition())
        
        # Add screens
        self.sm.add_widget(DashboardScreen(name='dashboard'))
        self.sm.add_widget(GuideScreen(name='guide'))
        
        return self.sm

if __name__ == '__main__':
    SignatureAuthApp().run()