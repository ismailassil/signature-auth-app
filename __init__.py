"""
Signature Authenticity Detection App

A mobile application for detecting and verifying signature authenticity using:
- DETR for signature localization
- SigLIP for signature verification
- Donut for stamp text extraction
"""

__version__ = "1.0.0"
__all__ = ["core", "ui"]

# Import key components for easier access
from .core.detection import SignatureDetector
from .core.verification import SignatureVerifier
from .core.ocr import StampOCR

# Initialize logger
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Signature Auth App package initialized")