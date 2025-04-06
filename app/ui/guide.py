from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
import os

class GuideScreen(Screen):
    def __init__(self, **kwargs):
        super(GuideScreen, self).__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical')
        
        # Scrollable guide content
        scroll = ScrollView()
        guide_content = Label(
            text="""
            [b]Signature Authenticity Detection App User Guide[/b]
            
            [size=20]1. How to Use:[/size]
            - Tap "Capture Signature" to take a photo of the signature
            - Position the signature clearly in the frame
            - Tap "Take Photo" to capture the image
            - The app will analyze and verify the signature
            
            [size=20]2. Understanding Results:[/size]
            - [color=00FF00]Green[/color] result means the signature is likely authentic
            - [color=FF0000]Red[/color] result means the signature may be forged
            - Confidence score shows how certain the system is
            
            [size=20]3. Best Practices:[/size]
            - Ensure good lighting when capturing signatures
            - Capture the signature on a clean, contrasting background
            - Hold the camera steady for clear images
            """,
            markup=True,
            size_hint_y=None,
            text_size=(400, None),
            valign='top',
            halign='left',
            padding=(20, 20)
        )
        guide_content.bind(size=guide_content.setter('text_size'))
        scroll.add_widget(guide_content)
        layout.add_widget(scroll)
        
        # Back button
        back_btn = Button(text="Back to Dashboard", size_hint=(1, 0.1))
        back_btn.bind(on_press=self.go_to_dashboard)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def go_to_dashboard(self, instance):
        self.manager.current = 'dashboard'