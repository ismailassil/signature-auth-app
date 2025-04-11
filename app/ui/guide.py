from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.metrics import dp
from textwrap import dedent
import os

class GuideScreen(Screen):
    def __init__(self, **kwargs):
        super(GuideScreen, self).__init__(**kwargs)
        
        # Set background to match dashboard
        Window.clearcolor = (0.95, 0.95, 0.95, 1)
        
        # Main layout with padding
        layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=[dp(30), dp(20), dp(30), dp(20)]
        )
        
        # Header with app name (centered)
        header = Label(
            text="[b]SignatureVerify Pro - User Guide[/b]",
            markup=True,
            font_size='24sp',
            color=(0.2, 0.4, 0.6, 1),
            size_hint=(1, 0.1),
            halign='center'
        )
        header.bind(size=header.setter('text_size'))
        layout.add_widget(header)
        
        # Scrollable content with card-like appearance
        scroll = ScrollView(
            size_hint=(1, 0.8),
            bar_width=dp(10),
            bar_color=(0.3, 0.6, 0.9, 0.5)
        )
        
        # Content container without a white background
        content_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=[dp(25), dp(20)],
            spacing=dp(15)
        )
        content_container.bind(minimum_height=content_container.setter('height'))
        
        # Removed canvas block that added the white rounded rectangle background
        
        # Guide content sections
        sections = [
            {
                "title": "1. How to Use",
                "content": dedent("""
                    - Tap [b]"Capture Signature"[/b] to take a photo of the signature
                    - Position the signature clearly in the frame
                    - Tap [b]"Take Photo"[/b] to capture the image
                    - The app will analyze and verify the signature
                """).strip()
            },
            {
                "title": "2. Understanding Results",
                "content": dedent("""
                    - [color=00AA00]Green result[/color] means the signature is likely authentic
                    - [color=FF3333]Red result[/color] means the signature may be forged
                    - Confidence score shows how certain the system is (0-1 scale)
                """).strip()
            },
            {
                "title": "3. Best Practices",
                "content": dedent("""
                    - Ensure good lighting when capturing signatures
                    - Capture on a clean, contrasting background
                    - Hold the camera steady for clear images
                    - For best results, compare against known authentic samples
                """).strip()
            }
        ]
        
        for section in sections:
            # Section title (centered)
            title = Label(
                text=f"[size=20][b]{section['title']}[/b][/size]",
                markup=True,
                size_hint_y=None,
                height=dp(40),
                halign='center',
                color=(0.2, 0.2, 0.2, 1)
            )
            title.bind(size=title.setter('text_size'))
            content_container.add_widget(title)
            
            # Section content (left aligned)
            content = Label(
                text=section['content'],
                markup=True,
                size_hint_y=None,
                text_size=(Window.width - dp(80), None),
                halign='left',
                valign='top',
                padding=[dp(15), 0, dp(15), dp(10)],
                color=(0.3, 0.3, 0.3, 1)
            )
            content.bind(texture_size=lambda lbl, val: setattr(lbl, 'height', val[1]))
            content_container.add_widget(content)
        
        scroll.add_widget(content_container)
        layout.add_widget(scroll)
        
        # Styled back button (centered by default)
        back_btn = Button(
            text="Back to Dashboard",
            size_hint=(1, 0.1),
            background_normal='',
            background_color=(0.3, 0.6, 0.9, 1),
            color=(1, 1, 1, 1),
            font_size='18sp',
            bold=True
        )
        back_btn.bind(on_press=self.go_to_dashboard)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def go_to_dashboard(self, instance):
        self.manager.current = 'dashboard'