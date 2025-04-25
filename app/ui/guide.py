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
                "title": "What the App Does",
                "content": dedent("""
                    - This app verifies the authenticity of handwritten and electronic signatures.
                    - It uses AI to compare uploaded signatures against a database of authentic and forged samples.
                    - The app provides a confidence score to indicate the likelihood of authenticity.
                """).strip()
            },
            {
                "title": "How to Use the App",
                "content": dedent("""
                    1. Launch the app to access the dashboard.
                    2. Click the [b]"Upload Image"[/b] button to select a signature image from your device.
                    3. Ensure the image is in PNG, JPG, or JPEG format.
                    4. Once uploaded, click [b]"Verify with DB"[/b] to start the verification process.
                    5. Wait for the app to display the result: Authentic, Forged, or Unknown, along with a confidence score.
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

        # Remove the rounded corners for the button
        back_btn.canvas.before.clear()
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def go_to_dashboard(self, instance):
        self.manager.current = 'dashboard'