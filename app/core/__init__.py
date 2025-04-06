"""
Core detection and verification modules

Exposes:
- SignatureDetector: For locating signatures in documents
- SignatureVerifier: For comparing against reference signatures
- StampOCR: For extracting text from stamps/seals
"""

__all__ = ["SignatureDetector", "SignatureVerifier", "StampOCR"]

from .detection import SignatureDetector
from .verification import SignatureVerifier
from .ocr import StampOCR

# Initialize models with lazy loading
_models_initialized = False

def initialize_models():
    """Lazy initialization of models to save memory"""
    global _models_initialized
    if not _models_initialized:
        from transformers import logging as transformers_logging
        transformers_logging.set_verbosity_error()
        _models_initialized = True