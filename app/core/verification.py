from transformers import SiglipProcessor, SiglipModel
from sklearn.metrics.pairwise import cosine_similarity
import torch
import numpy as np

class SignatureVerifier:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = SiglipProcessor.from_pretrained("microsoft/siglip-base-patch16-224")
        self.model = SiglipModel.from_pretrained("microsoft/siglip-base-patch16-224").to(self.device)
        self.model.eval()
        self.reference_embeddings = {}  # Load your reference signatures here
        
    def get_embedding(self, image):
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model.get_image_features(**inputs)
        return outputs.cpu().numpy()
    
    def verify_signature(self, query_image, reference_id, threshold=0.85):
        query_embedding = self.get_embedding(query_image)
        reference_embedding = self.reference_embeddings.get(reference_id)
        
        if reference_embedding is None:
            return False, 0.0
        
        similarity = cosine_similarity(query_embedding, reference_embedding)[0][0]
        return similarity > threshold, similarity