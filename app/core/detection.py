import torch
from transformers import DetrForObjectDetection, DetrImageProcessor
import cv2
import numpy as np

class SignatureDetector:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
        self.model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50").to(self.device)
        self.model.eval()
        
    def detect_signatures(self, image_path, confidence_threshold=0.9):
        # Load and preprocess image
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Prepare inputs
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        
        # Forward pass
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Process outputs
        target_sizes = torch.tensor([image.shape[:2]]).to(self.device)
        results = self.processor.post_process_object_detection(
            outputs, target_sizes=target_sizes, threshold=0.5
        )[0]
        
        # Filter results
        signatures = []
        for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
            if score > confidence_threshold and label == 1:  # Assuming label 1 is signature
                box = [round(i, 2) for i in box.tolist()]
                signatures.append({
                    "box": box,
                    "score": round(score.item(), 3),
                    "label": self.model.config.id2label[label.item()]
                })
        
        return signatures, image