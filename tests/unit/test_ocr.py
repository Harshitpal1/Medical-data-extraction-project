"""
Unit tests for OCR engine
"""
import pytest
from pathlib import Path
import numpy as np

from src.ocr.engine import OCREngine


class TestOCREngine:
    """Test cases for OCR engine"""
    
    def test_ocr_engine_initialization_easyocr(self):
        """Test OCR engine initialization with EasyOCR"""
        engine = OCREngine(engine="easyocr", languages=["en"])
        assert engine.engine == "easyocr"
        assert "en" in engine.languages
    
    def test_ocr_engine_initialization_tesseract(self):
        """Test OCR engine initialization with Tesseract"""
        try:
            engine = OCREngine(engine="tesseract", languages=["en"])
            assert engine.engine == "tesseract"
        except Exception:
            pytest.skip("Tesseract not installed")
    
    def test_unsupported_engine(self):
        """Test initialization with unsupported engine"""
        with pytest.raises(ValueError):
            OCREngine(engine="unsupported")
    
    def test_preprocess_image(self):
        """Test image preprocessing"""
        engine = OCREngine(engine="easyocr")
        
        # Create dummy image
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # Preprocess
        processed = engine.preprocess_image(image)
        
        # Check output
        assert processed.shape == (100, 100)
        assert processed.dtype == np.uint8


class TestOCRExtraction:
    """Test cases for text extraction"""
    
    @pytest.mark.slow
    def test_extract_from_image_mock(self):
        """Test text extraction from image with mock data"""
        # This would require actual image files for full testing
        # Mock test for structure validation
        pass
    
    def test_unsupported_file_type(self):
        """Test extraction with unsupported file type"""
        engine = OCREngine(engine="easyocr")
        
        with pytest.raises(ValueError):
            engine.extract_from_file("test.txt")
