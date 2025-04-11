from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics.texture import Texture
from kivy.clock import Clock
import cv2
import numpy as np
import os

Builder.load_file(os.path.join(os.path.dirname(__file__), 'dashboard.kv'))

class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super(DashboardScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        
        # Result display
        self.result_image = Image(size_hint=(1, 0.7))
        self.layout.add_widget(self.result_image)
        
        # Buttons
        btn_layout = BoxLayout(size_hint=(1, 0.15))
        self.capture_btn = Button(text="Capture Signature")
        self.capture_btn.bind(on_press=self.capture_signature)
        btn_layout.add_widget(self.capture_btn)
        
        self.guide_btn = Button(text="User Guide")
        self.guide_btn.bind(on_press=self.go_to_guide)
        btn_layout.add_widget(self.guide_btn)
        
        self.layout.add_widget(btn_layout)
        
        # Result label
        self.result_label = Label(size_hint=(1, 0.15))
        self.layout.add_widget(self.result_label)
        
        self.add_widget(self.layout)
        
        # Initialize camera
        self.camera = Camera(resolution=(640, 480), play=True)
        self.capture_mode = False
        try:
              self.camera = Camera(resolution=(640, 480), play=True)
              self.camera.bind(on_texture=self.on_camera_frame)
        except Exception as e:
              print(f"Camera initialization failed: {e}")
              self.camera = None
              self.capture_btn.disabled = True
              self.result_label.text = "Camera not available"
    
    def go_to_guide(self, instance):
        self.manager.current = 'guide'
    
    def capture_signature(self, instance):
          if not self.capture_mode:
                if self.camera is None:
                       self.show_file_chooser()
                       return
          if not self.capture_mode:
            self.capture_mode = True
            self.layout.remove_widget(self.result_image)
            self.layout.add_widget(self.camera, index=0)
            self.capture_btn.text = "Take Photo"
          else:
            # Save the camera image
            texture = self.camera.texture
            w, h = texture.size
            buffer = texture.pixels
            image_data = np.frombuffer(buffer, dtype=np.uint8)
            image_data = image_data.reshape((h, w, 4))
            image_data = cv2.cvtColor(image_data, cv2.COLOR_RGBA2BGR)
            
            # Process the image
            self.process_image(image_data)
            
            # Switch back to result view
            self.layout.remove_widget(self.camera)
            self.layout.add_widget(self.result_image, index=0)
            self.capture_mode = False
            self.capture_btn.text = "Capture Signature"
            
    def show_file_chooser(self):
         from kivy.uix.filechooser import FileChooserListView
         content = FileChooserListView()
         popup = Popup(title="Select signature image", content=content, size_hint=(0.9, 0.9))
         content.bind(on_submit=lambda x, file, _: self.process_selected_file(file, popup))
         popup.open()

def process_selected_file(self, file_path, popup):
    popup.dismiss()
    try:
        image = cv2.imread(file_path)
        if image is not None:
            self.process_image(image)
        else:
            raise ValueError("Could not read image")
    except Exception as e:
        self.result_label.text = f"Error: {str(e)}"
    def process_image(self, image_data):
        # Here you would call your detection and verification models
        # This is a placeholder for the actual processing
        
        # For demo purposes, we'll just display the image with a mock result
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
            self.result_label.text = f"Authentic Signature (Confidence: {confidence:.2f})"
            self.result_label.color = (0, 1, 0, 1)  # Green
        else:
            self.result_label.text = f"Potential Forgery (Confidence: {1-confidence:.2f})"
            self.result_label.color = (1, 0, 0, 1)  # Red