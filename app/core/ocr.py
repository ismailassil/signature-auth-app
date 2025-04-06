from transformers import DonutProcessor, VisionEncoderDecoderModel
import torch
from PIL import Image
import numpy as np
import re

class StampOCR:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load processor and model
        self.processor = DonutProcessor.from_pretrained("naver-clova-ix/donut-base")
        self.model = VisionEncoderDecoderModel.from_pretrained("naver-clova-ix/donut-base").to(self.device)
        
        # Set special tokens for document parsing
        self.processor.tokenizer.add_special_tokens({"additional_special_tokens": ["<s_ocr>"]})
        self.model.config.pad_token_id = self.processor.tokenizer.pad_token_id
        self.model.config.decoder_start_token_id = self.processor.tokenizer.convert_tokens_to_ids(["<s_ocr>"])[0]
        
        self.model.eval()
    
    def preprocess_image(self, image):
        """Convert OpenCV image to PIL and preprocess"""
        if isinstance(image, np.ndarray):
            image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        return image
    
    def extract_text(self, image, prompt="<s_ocr>"):
        """
        Extract text from stamp/seal image
        Args:
            image: Can be either PIL Image or OpenCV/numpy image
            prompt: Task prompt (default is OCR task)
        Returns:
            extracted_text: Cleaned text from the stamp
            raw_output: Raw model output
        """
        # Preprocess image
        image = self.preprocess_image(image)
        
        # Prepare inputs
        pixel_values = self.processor(image, return_tensors="pt").pixel_values.to(self.device)
        
        # Generate output
        decoder_input_ids = self.processor.tokenizer(
            prompt, add_special_tokens=False, return_tensors="pt"
        ).input_ids.to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                pixel_values,
                decoder_input_ids=decoder_input_ids,
                max_length=self.model.decoder.config.max_position_embeddings,
                early_stopping=True,
                pad_token_id=self.processor.tokenizer.pad_token_id,
                eos_token_id=self.processor.tokenizer.eos_token_id,
                use_cache=True,
                num_beams=1,
                bad_words_ids=[[self.processor.tokenizer.unk_token_id]],
                return_dict_in_generate=True,
            )
        
        # Process output
        sequence = self.processor.batch_decode(outputs.sequences)[0]
        sequence = sequence.replace(self.processor.tokenizer.eos_token, "").replace(self.processor.tokenizer.pad_token, "")
        sequence = re.sub(r"<.*?>", "", sequence, count=1).strip()  # Remove first task start token
        
        return sequence, outputs
    
    def clean_stamp_text(self, text):
        """Post-processing for stamp-specific text cleaning"""
        # Remove common stamp artifacts
        text = re.sub(r'[•·∙]', ' ', text)  # Replace bullet points
        text = re.sub(r'\s+', ' ', text).strip()  # Collapse whitespace
        
        # Common stamp text patterns
        patterns = [
            r'(?:seal|stamp|official)\s*[:]?\s*',  # Remove "seal:" prefixes
            r'[©®™]',  # Remove copyright symbols
            r'^\W+|\W+$'  # Remove leading/trailing non-word chars
        ]
        
        for pattern in patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def process_stamp(self, image):
        """Full processing pipeline for stamps"""
        # First pass - general text extraction
        raw_text, _ = self.extract_text(image)
        
        # Second pass - focused on clean text if first pass has low confidence
        if len(raw_text) < 3 or not any(c.isalpha() for c in raw_text):
            focused_crop = self.adjust_crop_for_stamp(image)
            raw_text, _ = self.extract_text(focused_crop)
        
        # Clean and return
        return self.clean_stamp_text(raw_text)
    
    def adjust_crop_for_stamp(self, image):
        """Enhance stamp area by cropping and preprocessing"""
        if isinstance(image, np.ndarray):
            # Convert to PIL for consistency
            image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        # Basic enhancement - focus on center region where stamps often are
        width, height = image.size
        crop_box = (
            width * 0.2,  # left
            height * 0.2,  # top
            width * 0.8,   # right
            height * 0.8   # bottom
        )
        
        return image.crop(crop_box)