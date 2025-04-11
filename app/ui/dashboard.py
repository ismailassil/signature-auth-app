from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics.texture import Texture
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.window import Window
import cv2
import numpy as np
import os

Builder.load_file(os.path.join(os.path.dirname(__file__), 'dashboard.kv'))
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics.texture import Texture
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.window import Window
import cv2
import numpy as np
import os

Builder.load_file(os.path.join(os.path.dirname(__file__), 'dashboard.kv'))

class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super(DashboardScreen, self).__init__(**kwargs)
        
        # Set background color
        Window.clearcolor = (0.95, 0.95, 0.95, 1)
        
        # Main container
        self.layout = BoxLayout(
            orientation='vertical',
            spacing=20,
            padding=[40, 20, 40, 20]
        )
        
        # Logo area
        logo_layout = BoxLayout(
            size_hint=(1, 0.2),
            orientation='vertical'
        )
        
        logo_label = Label(
            text="[b]SignatureVerify[/b]",
            markup=True,
            font_size='32sp',
            color=(0.2, 0.4, 0.6, 1),
            size_hint=(1, 0.8)
        )
        logo_layout.add_widget(logo_label)
        self.layout.add_widget(logo_layout)
        
        # Image display area
        self.result_image = Image(
            size_hint=(1, 0.4),
            fit_mode='contain'
        )
        self.layout.add_widget(self.result_image)
        
        # Buttons layout (will be populated after camera check)
        self.btn_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.3),
            spacing=15,
            padding=[0, 10, 0, 10]
        )
        
        # Status label
        self.result_label = Label(
            # text="Ready to verify signatures",
            size_hint=(1, 0.1),
            color=(0.3, 0.3, 0.3, 1),
            font_size='16sp'
        )
        
        # Add widgets that don't depend on camera
        self.layout.add_widget(self.btn_layout)
        self.layout.add_widget(self.result_label)
        
        self.add_widget(self.layout)
        
        # Initialize camera and UI based on availability
        self.camera = None
        self.capture_mode = False
        self.initialize_ui_components()
    
    def initialize_ui_components(self):
        """Initialize UI components based on camera availability"""
        # Clear existing buttons
        self.btn_layout.clear_widgets()
        
        # Common buttons
        buttons = [
            {"text": "Upload Signature", "callback": self.show_file_chooser},
            {"text": "User Guide", "callback": self.go_to_guide}
        ]
        
        # Check camera availability
        try:
            self.camera = Camera(resolution=(640, 480), play=True)
            self.camera.bind(on_texture=self.on_camera_frame)
            # Add capture button only if camera is available
            buttons.insert(0, {"text": "Capture Signature", "callback": self.capture_signature})
        except Exception as e:
            print(f"Camera initialization failed: {e}")
            self.camera = None
        
        # Create and add buttons without adding a custom canvas background (blue square)
        for props in buttons:
            btn = Button(
                text=props["text"],
                size_hint=(1, 0.3),
                background_normal='',
                background_color=(0.3, 0.6, 0.9, 1),
                color=(1, 1, 1, 1),
                font_size='18sp',
                bold=True
            )
            btn.bind(on_press=props["callback"])
            self.btn_layout.add_widget(btn)
        
        # Initialize camera
        self.camera = None
        self.capture_mode = False
        self.initialize_camera()
    
    def initialize_camera(self):
        try:
            self.camera = Camera(resolution=(640, 480), play=True)
            self.camera.bind(on_texture=self.on_camera_frame)
        except Exception as e:
            print(f"Camera initialization failed: {e}")
            self.camera = None
            for child in self.layout.children:
                if isinstance(child, Button) and child.text.startswith(""):
                    child.disabled = True
            # self.result_label.text = "Camera not available"
    
    def go_to_guide(self, instance):
        self.manager.current = 'guide'
    
    def capture_signature(self, instance):
        if not self.capture_mode:
            if self.camera is None:
                self.show_file_chooser()
                return
            
            self.capture_mode = True
            self.layout.remove_widget(self.result_image)
            self.layout.add_widget(self.camera, index=len(self.layout.children)-3)
            for child in self.layout.children:
                if isinstance(child, Button) and child.text.startswith(""):
                    child.text = "Take Photo"
        else:
            # Save the camera image
            texture = self.camera.texture
            if texture is None:
                self.result_label.text = "Failed to capture image"
                return
                
            w, h = texture.size
            buffer = texture.pixels
            image_data = np.frombuffer(buffer, dtype=np.uint8)
            image_data = image_data.reshape((h, w, 4))
            image_data = cv2.cvtColor(image_data, cv2.COLOR_RGBA2BGR)
            
            # Fix rotation if needed
            image_data = cv2.rotate(image_data, cv2.ROTATE_180)
            
            # Process the image
            self.process_image(image_data)
            
            # Switch back to result view
            self.layout.remove_widget(self.camera)
            self.layout.add_widget(self.result_image, index=len(self.layout.children)-2)
            self.capture_mode = False
            for child in self.layout.children:
                if isinstance(child, Button) and child.text == "Take Photo":
                    child.text = " Capture Signature"
    
    def show_file_chooser(self, *args):
        from kivy.uix.filechooser import FileChooserListView
        content = BoxLayout(orientation='vertical')
        file_chooser = FileChooserListView(filters=['*.png', '*.jpg', '*.jpeg'])
        
        # Add buttons for better UX
        btn_layout = BoxLayout(size_hint=(1, 0.1))
        cancel_btn = Button(text="Cancel")
        select_btn = Button(text="Select")
        
        def dismiss_popup(*args):
            popup.dismiss()
            
        cancel_btn.bind(on_press=dismiss_popup)
        select_btn.bind(on_press=lambda x: self.process_selected_file(
            file_chooser.selection and file_chooser.selection[0] or '',
            popup
        ))
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(select_btn)
        
        content.add_widget(file_chooser)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title="Select signature image",
            content=content,
            size_hint=(0.9, 0.9)
        )
        popup.open()

    def process_selected_file(self, file_path, popup):
        popup.dismiss()
        try:
            if not file_path.lower().endswith((".png", ".jpg", ".jpeg")):
                raise ValueError("Only PNG/JPG images are allowed.")

            image = cv2.imread(file_path)
            if image is None:
                raise ValueError("Could not read image.")

            if image.shape[0] < 50 or image.shape[1] < 50:
                raise ValueError("Image too small (min 50x50 pixels).")

            self.process_image(image)
        except Exception as e:
            self.result_label.text = f"Error: {str(e)}"
            self.result_label.color = (1, 0, 0, 1)

    def process_image(self, image_data):
        try:
            # Convert and display image
            image_data = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
            h, w, _ = image_data.shape
            buf = image_data.tobytes()
            texture = Texture.create(size=(w, h), colorfmt='rgb')
            texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
            self.result_image.texture = texture
            
            # Mock verification result
            is_authentic = True  # Replace with actual verification
            confidence = 0.92    # Replace with actual confidence
            
            if is_authentic:
                self.result_label.text = f"Authentic (Confidence: {confidence:.2f})"
                self.result_label.color = (0, 0.7, 0, 1)  # Green
            else:
                self.result_label.text = f"Potential Forgery (Confidence: {1-confidence:.2f})"
                self.result_label.color = (1, 0, 0, 1)  # Red
        except Exception as e:
            self.result_label.text = f"Processing error: {str(e)}"
            self.result_label.color = (1, 0, 0, 1)