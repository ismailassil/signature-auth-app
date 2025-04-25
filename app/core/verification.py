from transformers import SiglipProcessor, SiglipModel
from sklearn.metrics.pairwise import cosine_similarity
import torch
import numpy as np
import os
import cv2
import threading

class SignatureVerifier:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Delay loading processor and model until verification is triggered
        self.processor = None
        self.model = None
        self.reference_embeddings = None
        self.embeddings_loaded = False
        self.reference_embeddings_cache = None
        self.db_last_modified = None

    def initialize_model(self):
        print("[DEBUG] Initializing model...")
        if self.processor is None or self.model is None:
            print("[DEBUG] Loading processor and model...")
            self.processor = SiglipProcessor.from_pretrained("google/siglip-base-patch16-224", use_fast=True)
            self.model = SiglipModel.from_pretrained("google/siglip-base-patch16-224").to(self.device)
            self.model.eval()
            print("[DEBUG] Processor and model loaded.")

        if not self.embeddings_loaded:
            print("[DEBUG] Embeddings not loaded. Starting async loading...")
            self.load_database_embeddings_async()

    def load_database_embeddings_async(self):
        def load_embeddings():
            print("[DEBUG] Starting to load database embeddings...")
            embeddings = {"real": [], "forge": []}
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../db_signatures')
            real_path = os.path.join(db_path, "real")

            if os.path.exists(real_path):
                total_files = len([f for f in os.listdir(real_path) if f.lower().endswith((".png", ".jpg", ".jpeg"))])
                loaded_files = 0

                for file in os.listdir(real_path):
                    if file.lower().endswith((".png", ".jpg", ".jpeg")):
                        file_path = os.path.join(real_path, file)
                        image = cv2.imread(file_path)
                        if image is not None:
                            image = self.correct_image_orientation(image)
                            embedding = self.get_embedding(image)
                            embeddings["real"].append(embedding)

                            # Update reference_embeddings incrementally
                            self.reference_embeddings = embeddings

                            # Increment progress
                            loaded_files += 1
                            progress = (loaded_files / total_files) * 100
                            print(f"[DEBUG] Loading progress: {progress:.2f}%")

            self.reference_embeddings_cache = embeddings
            self.db_last_modified = self.get_db_last_modified_time()
            self.embeddings_loaded = True
            print("[DEBUG] Finished loading database embeddings.")

        # Run the embedding loading in a background thread
        thread = threading.Thread(target=load_embeddings)
        thread.start()

    def get_db_last_modified_time(self):
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../db_signatures')
        return max(os.path.getmtime(os.path.join(root, file))
                   for root, _, files in os.walk(db_path) for file in files)

    def correct_image_orientation(self, image, for_display=False):
        """Correct the orientation of the image if needed."""
        if for_display:
            # Do not rotate the image if it's for display purposes
            return image
        # Rotate the image by 180 degrees for processing
        return cv2.rotate(image, cv2.ROTATE_180)

    def get_embedding(self, image):
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model.get_image_features(**inputs)
        return outputs.cpu().numpy()

    def verify_signature(self, query_image, threshold=0.985):
        # Check if the database has changed
        current_db_modified = self.get_db_last_modified_time()
        if self.db_last_modified != current_db_modified:
            print("[DEBUG] Database has changed. Reloading embeddings...")
            self.load_database_embeddings_async()

        # Wait for embeddings to load if necessary
        if not self.embeddings_loaded:
            raise RuntimeError("Database embeddings are still loading. Please try again later.")

        # Correct the orientation of the query image for processing
        query_image = self.correct_image_orientation(query_image, for_display=False)
        query_embedding = self.get_embedding(query_image)

        if not self.reference_embeddings["real"]:
            raise ValueError("No embeddings found in the 'real' directory. Ensure it contains valid images.")

        # Log similarity scores for debugging
        similarity_scores = [
            cosine_similarity(query_embedding, ref_embedding)[0][0] * 100
            for ref_embedding in self.reference_embeddings["real"]
        ]
        print("Similarity scores:", similarity_scores)

        max_real_similarity = max(similarity_scores) if similarity_scores else 0

        # Debugging logs for thresholds and classification
        print(f"[DEBUG] Max similarity: {max_real_similarity}%")
        print(f"[DEBUG] Threshold: {threshold * 100}%")

        # Determine result based on threshold
        if max_real_similarity >= threshold * 100:
            return "Authentic", f"{max_real_similarity:.2f}%"
        else:
            return "Forged", f"{max_real_similarity:.2f}%"

    def get_loading_progress(self):
        """Returns the progress of loading embeddings as a percentage."""
        if self.reference_embeddings is None:
            return 0  # No progress if embeddings are not initialized

        # Calculate progress based on the number of loaded embeddings
        total_embeddings = len(self.reference_embeddings.get("real", []))
        expected_embeddings = len(os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../db_signatures/real')))

        if expected_embeddings == 0:
            return 100  # Avoid division by zero; assume fully loaded if no files are expected

        progress = (total_embeddings / expected_embeddings) * 100
        return min(progress, 100)  # Cap progress at 100%