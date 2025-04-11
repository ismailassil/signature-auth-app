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

# Builder.load_file(os.path.join(os.path.dirname(__file__), 'dashboard.kv'))

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
        
        # Buttons layout (centered at the bottom)
        self.btn_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=200,  # Adjust height as needed
			spacing=15,
			padding=[0, 10, 0, 10],
			pos_hint={'center_x': 0.5, 'center_y': 0.2}  # Position near bottom
        )
        
        # Status label
        self.result_label = Label(
            text="Awaiting result...",
            size_hint=(1, 0.1),
            color=(0.3, 0.3, 0.3, 1),
            font_size='16sp'
        )
        self.result_label.bind(size=self.update_result_label_canvas, pos=self.update_result_label_canvas)

        # Add widgets that don't depend on image
        self.layout.add_widget(self.btn_layout)
        self.layout.add_widget(self.result_label)
        
        self.add_widget(self.layout)

        # Initialize UI components (buttons)
        self.initialize_ui_components()
        
        # Store the uploaded image
        self.query_image = None

    def initialize_ui_components(self):
        """Initialize UI components with rounded buttons"""
        self.btn_layout.clear_widgets()

        # Define buttons
        capture_btn = self.create_rounded_button("Capture with Camera", self.capture_with_camera)
        upload_btn = self.create_rounded_button("Upload Image", self.show_file_chooser)
        verify_btn = self.create_rounded_button("Verify with DB", self.verify_against_database)
        guide_btn = self.create_rounded_button("User Guide", self.go_to_guide)

        # Add buttons to the layout in the desired order
        for btn in [capture_btn, upload_btn, verify_btn, guide_btn]:
            self.btn_layout.add_widget(btn)

        # Add the small "About" button at the top-right corner
        about_btn = Button(
            text="?",
            size_hint=(None, None),
            size=(40, 40),  # Small size
            background_normal='',
            background_color=(0.3, 0.6, 0.9, 1),
            color=(1, 1, 1, 1),
            font_size='18sp',
            pos_hint={'right': 1, 'top': 1}  # Absolute positioning
        )
        about_btn.bind(on_press=self.show_about_popup)

        # Add the "About" button to the screen
        self.add_widget(about_btn)

    def create_rounded_button(self, text, callback, size_hint=(1, None), height=50):
        """Helper to create a button with rounded corners"""
        btn = Button(
            text=text,
            size_hint=size_hint,
            height=height,
            background_normal='',
            background_color=(0.3, 0.6, 0.9, 1),
            color=(1, 1, 1, 1),
            font_size='18sp'
        )
        btn.bind(pos=self.update_button_canvas, size=self.update_button_canvas)
        btn.bind(on_press=callback)
        return btn

    def update_button_canvas(self, instance, value):
        """Update the canvas to draw a rounded rectangle behind the button."""
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*instance.background_color)  # Use the button's background color
            r = instance.height * 0.5 if instance.height else 25  # Radius is 50% of height
            RoundedRectangle(pos=instance.pos, size=instance.size, radius=[(r, r)] * 4)

    def verify_against_database(self, instance):
        if self.query_image is None:
            self.result_label.text = "Please upload an image first."
            self.result_label.color = (1, 0, 0, 1)
            return

        from kivy.clock import Clock
        import threading
        loading_popup = self.create_loading_popup()
        loading_popup.open()

        def worker():
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                from app.core.verification import SignatureVerifier
                import os
                verifier = SignatureVerifier()
                threshold = 0.85
                query_embedding = verifier.get_embedding(self.query_image)
                max_similarity = 0.0

                db_folder = os.path.join(os.getcwd(), "db_signatures")
                if not os.path.exists(db_folder):
                    result_text = f"Database folder not found: {db_folder}"
                    result_color = (1, 0, 0, 1)
                else:
                    for file in os.listdir(db_folder):
                        if file.lower().endswith((".png", ".jpg", ".jpeg")):
                            file_path = os.path.join(db_folder, file)
                            ref_image = cv2.imread(file_path)
                            if ref_image is None:
                                continue
                            ref_embedding = verifier.get_embedding(ref_image)
                            similarity = cosine_similarity(query_embedding, ref_embedding)[0][0]
                            if similarity > max_similarity:
                                max_similarity = similarity

                    if max_similarity > threshold:
                        self.result_label.text = f"Authenticated from DB (Max similarity: {max_similarity:.2f})"
                        self.result_label.color = (0, 0.7, 0, 1)  # Green for success
                    else:
                        self.result_label.text = f"Not authenticated from DB (Max similarity: {max_similarity:.2f})"
                        self.result_label.color = (1, 0, 0, 1)  # Red for failure
            except Exception as e:
                result_text = f"Verification error: {str(e)}"
                result_color = (1, 0, 0, 1)

            def update_ui(dt):
                self.result_label.text = result_text
                self.result_label.color = result_color
                loading_popup.dismiss()
            Clock.schedule_once(update_ui)

        threading.Thread(target=worker).start()

    def create_loading_popup(self):
        """Creates a custom loading popup with centered text and minimized height"""
        from kivy.uix.modalview import ModalView
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.image import Image
        from kivy.graphics import Color, RoundedRectangle
        from os.path import join, dirname

        modal = ModalView(size_hint=(1, 1), background_color=(0, 0, 0, 0.5))
        loading_layout = BoxLayout(orientation='vertical',
                                   padding=20,
                                   spacing=10,
                                   size_hint=(0.4, 0.2),
                                   pos_hint={'center_x': 0.5, 'center_y': 0.5})
        with loading_layout.canvas.before:
            Color(1, 1, 1, 1)
            rect = RoundedRectangle(size=loading_layout.size, pos=loading_layout.pos, radius=[20])
        loading_layout.bind(pos=lambda instance, value: setattr(rect, 'pos', value))
        loading_layout.bind(size=lambda instance, value: setattr(rect, 'size', value))
            
        loading_label = Label(text="Searching database...", font_size='20sp',
                              color=(0, 0, 0, 1),
                              halign='center',
                              valign='middle',
                              size_hint_y=None,
                              height=40)
        loading_label.bind(size=loading_label.setter('text_size'))
        
        loader_path = join(dirname(__file__), '..', 'assets', 'loader.gif')
        spinner = Image(source=loader_path, anim_delay=0.1,
                        size_hint=(1, None), height=40)

        loading_layout.add_widget(loading_label)
        loading_layout.add_widget(spinner)
        modal.add_widget(loading_layout)
        return modal

    def show_file_chooser(self, *args):
        from kivy.uix.filechooser import FileChooserListView
        import os
        content = BoxLayout(orientation='vertical')
        # Set the initial path to the user's home directory
        home_dir = os.path.expanduser('~')
        file_chooser = FileChooserListView(path=home_dir, filters=['*.png', '*.jpg', '*.jpeg'])
        
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

            self.query_image = image  # store the uploaded image for later use
            
            # Display the image as before
            image_data = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h, w, _ = image_data.shape
            buf = image_data.tobytes()
            texture = Texture.create(size=(w, h), colorfmt='rgb')
            texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
            self.result_image.texture = texture

        except Exception as e:
            self.show_error_popup(f"Error: {str(e)}")

    def go_to_guide(self, instance):
        self.manager.current = 'guide'

    def process_image(self, image_data):
        try:
            # (Existing processing code if needed)
            self.query_image = image_data
            image_data = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
            h, w, _ = image_data.shape
            buf = image_data.tobytes()
            texture = Texture.create(size=(w, h), colorfmt='rgb')
            texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
            self.result_image.texture = texture
            is_authentic = True  # Your logic here
            confidence = 0.92    # Your logic here
            
            if is_authentic:
                self.result_label.text = f"Authentic (Confidence: {confidence:.2f})"
                self.result_label.color = (0, 0.7, 0, 1)
            else:
                self.result_label.text = f"Potential Forgery (Confidence: {1-confidence:.2f})"
                self.result_label.color = (1, 0, 0, 1)
        except Exception as e:
            self.result_label.text = f"Processing error: {str(e)}"
            self.result_label.color = (1, 0, 0, 1)

    def show_error_popup(self, error_message):
        """Displays an error popup with a dismiss button centered at the bottom."""
        from kivy.uix.modalview import ModalView
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.graphics import Color, RoundedRectangle

        # Create the modal view
        modal = ModalView(size_hint=(0.8, 0.4), background_color=(0, 0, 0, 0.5))

        # Main layout for the popup
        layout = BoxLayout(orientation='vertical', spacing=20, padding=20)

        # Error message label
        error_label = Label(
            text=error_message,
            font_size='18sp',
            color=(1, 0, 0, 1),
            halign='center',
            valign='middle',
            size_hint=(1, 0.6)
        )
        error_label.bind(size=error_label.setter('text_size'))

        # Dismiss button (X) at the top-right corner
        dismiss_btn = Button(
            text="X",
            size_hint=(None, None),
            size=(40, 40),
            background_normal='',
            background_color=(1, 0, 0, 1),
            color=(1, 1, 1, 1),
            font_size='16sp'
        )
        dismiss_btn.bind(on_press=modal.dismiss)

        # Centered button at the bottom
        centered_btn = Button(
            text="Dismiss",
            size_hint=(0.5, None),
            height=50,
            background_normal='',
            background_color=(0.3, 0.6, 0.9, 1),
            color=(1, 1, 1, 1),
            font_size='18sp'
        )
        centered_btn.bind(on_press=modal.dismiss)

        # Add the dismiss button and error label to a top layout
        top_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
        top_layout.add_widget(Label(size_hint=(1, 1)))  # Spacer
        top_layout.add_widget(dismiss_btn)

        # Add widgets to the main layout
        layout.add_widget(top_layout)
        layout.add_widget(error_label)
        layout.add_widget(centered_btn)

        # Add the layout to the modal and open it
        modal.add_widget(layout)
        modal.open()

    def capture_with_camera(self, instance):
        """Capture an image using the camera."""
        try:
            # Initialize the camera
            camera = Camera(play=True, resolution=(640, 480))
            popup = Popup(
                title="Capture Image",
                size_hint=(0.9, 0.9)
            )

            # Add a capture button
            capture_btn = Button(
                text="Capture",
                size_hint=(1, 0.1),
                background_normal='',
                background_color=(0.3, 0.6, 0.9, 1),
                color=(1, 1, 1, 1),
                font_size='18sp'
            )

            def capture_image(*args):
                texture = camera.texture
                if texture:
                    # Convert the texture to an image
                    image_data = np.frombuffer(texture.pixels, np.uint8).reshape(
                        texture.height, texture.width, 4
                    )
                    self.process_image(image_data)
                popup.dismiss()

            capture_btn.bind(on_press=capture_image)

            # Add the camera and button to the popup
            popup.content = BoxLayout(orientation='vertical')
            popup.content.add_widget(camera)
            popup.content.add_widget(capture_btn)

            popup.open()
        except Exception as e:
            self.show_error_popup(f"Error initializing camera: {str(e)}")

    def update_result_label_canvas(self, instance, value):
        """Update the background of the result label."""
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(0.9, 0.9, 0.9, 1)  # Light gray background
            RoundedRectangle(pos=instance.pos, size=instance.size, radius=[10])

    def show_about_popup(self, instance):
        """Show a popup with the creators of the app."""
        from kivy.uix.modalview import ModalView
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button

        # Create the modal view with a white background
        modal = ModalView(size_hint=(0.8, 0.4), background_color=(1, 1, 1, 1))

        # Main layout for the popup
        layout = BoxLayout(orientation='vertical', spacing=20, padding=20)

        # Add a label with the creators' information
        creators_label = Label(
            text="[b]Creators:[/b]\n- Mohamed FAKRI\n- Amine TABI",
            markup=True,
			font_size='18sp',
            color=(1, 1, 1, 1),  # Black text
            halign='left',
            valign='middle',
            size_hint=(1, 0.8)
        )
        creators_label.bind(size=creators_label.setter('text_size'))

        # Add a dismiss button
        dismiss_btn = Button(
            text="Close",
            size_hint=(0.5, None),
            height=50,
            background_normal='',
            background_color=(0.3, 0.6, 0.9, 1),
            color=(1, 1, 1, 1),
            font_size='18sp'
        )
        dismiss_btn.bind(on_press=modal.dismiss)

        # Add widgets to the layout
        layout.add_widget(creators_label)
        layout.add_widget(dismiss_btn)

        # Add the layout to the modal and open it
        modal.add_widget(layout)
        modal.open()