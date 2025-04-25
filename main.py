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
import threading
from app.core.verification import SignatureVerifier

# Import screens
from app.ui.dashboard import DashboardScreen
from app.ui.guide import GuideScreen

# Initialize the SignatureVerifier
signature_verifier = SignatureVerifier()

def load_embeddings_in_background():
    print("[DEBUG] Starting embedding loading in a background thread...")
    signature_verifier.initialize_model()
    print("[DEBUG] Embedding loading completed.")

# Start the embedding loading in a separate thread
embedding_thread = threading.Thread(target=load_embeddings_in_background)
embedding_thread.start()

class SignatureAuthApp(App):
    def build(self):
        # Expose the shared signature verifier on the App instance
        self.signature_verifier = signature_verifier
        # Set window size for mobile (will be fullscreen on actual device)
        Window.size = (360, 640)
        
        # Create screen manager
        self.sm = ScreenManager(transition=FadeTransition())
        
        # Add screens
        self.sm.add_widget(DashboardScreen(name='dashboard'))
        self.sm.add_widget(GuideScreen(name='guide'))
        
        return self.sm

if __name__ == "__main__":
    try:
        SignatureAuthApp().run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user. Exiting gracefully...")