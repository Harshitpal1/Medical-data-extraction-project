"""
OCR Engine for Medical Document Processing
Supports both Tesseract and EasyOCR
"""
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

import cv2
import numpy as np
from PIL import Image
import pytesseract
import easyocr
from pdf2image import convert_from_path

from config import get_config

logger = logging.getLogger(__name__)
config = get_config()


class OCREngine:
    """OCR Engine for extracting text from medical documents"""
    
    def __init__(self, engine: str = "easyocr", languages: List[str] = None):
        """
        Initialize OCR Engine
        
        Args:
            engine: OCR engine to use ('tesseract' or 'easyocr')
            languages: List of language codes (e.g., ['en'])
        """
        self.engine = engine or config.OCR_ENGINE
        self.languages = languages or config.OCR_LANGUAGES
        self.confidence_threshold = config.OCR_CONFIDENCE_THRESHOLD
        
        if self.engine == "easyocr":
            try:
                self.reader = easyocr.Reader(self.languages, gpu=False)
                logger.info(f"Initialized EasyOCR with languages: {self.languages}")
            except Exception as e:
                logger.error(f"Failed to initialize EasyOCR: {e}")
                raise
        elif self.engine == "tesseract":
            # Check if tesseract is available
            try:
                pytesseract.get_tesseract_version()
                logger.info("Initialized Tesseract OCR")
            except Exception as e:
                logger.error(f"Tesseract not found: {e}")
                raise
        else:
            raise ValueError(f"Unsupported OCR engine: {self.engine}")
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR results
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh)
        
        return denoised
    
    def extract_text_tesseract(
        self, image: np.ndarray
    ) -> Tuple[str, float]:
        """
        Extract text using Tesseract OCR
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Tuple of (extracted text, confidence score)
        """
        try:
            # Get detailed data
            data = pytesseract.image_to_data(
                image, output_type=pytesseract.Output.DICT
            )
            
            # Extract text and calculate average confidence
            text_parts = []
            confidences = []
            
            for i, conf in enumerate(data['conf']):
                if int(conf) > 0:
                    text_parts.append(data['text'][i])
                    confidences.append(int(conf) / 100.0)
            
            text = ' '.join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return text, avg_confidence
            
        except Exception as e:
            logger.error(f"Tesseract extraction failed: {e}")
            return "", 0.0
    
    def extract_text_easyocr(
        self, image: np.ndarray
    ) -> Tuple[str, float]:
        """
        Extract text using EasyOCR
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Tuple of (extracted text, confidence score)
        """
        try:
            results = self.reader.readtext(image)
            
            if not results:
                return "", 0.0
            
            # Extract text and calculate average confidence
            text_parts = []
            confidences = []
            
            for bbox, text, conf in results:
                if conf >= self.confidence_threshold:
                    text_parts.append(text)
                    confidences.append(conf)
            
            text = ' '.join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return text, avg_confidence
            
        except Exception as e:
            logger.error(f"EasyOCR extraction failed: {e}")
            return "", 0.0
    
    def extract_from_image(
        self, image_path: str, preprocess: bool = True
    ) -> Dict[str, any]:
        """
        Extract text from image file
        
        Args:
            image_path: Path to image file
            preprocess: Whether to preprocess the image
            
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Failed to load image: {image_path}")
            
            # Preprocess if requested
            if preprocess:
                image = self.preprocess_image(image)
            
            # Extract text based on engine
            if self.engine == "tesseract":
                text, confidence = self.extract_text_tesseract(image)
            else:
                text, confidence = self.extract_text_easyocr(image)
            
            return {
                "text": text,
                "confidence": confidence,
                "engine": self.engine,
                "source_file": os.path.basename(image_path)
            }
            
        except Exception as e:
            logger.error(f"Failed to extract from image {image_path}: {e}")
            raise
    
    def extract_from_pdf(
        self, pdf_path: str, preprocess: bool = True
    ) -> List[Dict[str, any]]:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            preprocess: Whether to preprocess the images
            
        Returns:
            List of dictionaries with extracted text and metadata for each page
        """
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path)
            
            results = []
            for page_num, image in enumerate(images, start=1):
                # Convert PIL Image to numpy array
                image_np = np.array(image)
                
                # Preprocess if requested
                if preprocess:
                    image_np = self.preprocess_image(image_np)
                
                # Extract text based on engine
                if self.engine == "tesseract":
                    text, confidence = self.extract_text_tesseract(image_np)
                else:
                    text, confidence = self.extract_text_easyocr(image_np)
                
                results.append({
                    "page": page_num,
                    "text": text,
                    "confidence": confidence,
                    "engine": self.engine,
                    "source_file": os.path.basename(pdf_path)
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to extract from PDF {pdf_path}: {e}")
            raise
    
    def extract_from_file(
        self, file_path: str, preprocess: bool = True
    ) -> Dict[str, any]:
        """
        Extract text from file (auto-detect type)
        
        Args:
            file_path: Path to file
            preprocess: Whether to preprocess the images
            
        Returns:
            Dictionary with extracted text and metadata
        """
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            pages = self.extract_from_pdf(file_path, preprocess)
            # Combine all pages
            combined_text = '\n\n'.join([p['text'] for p in pages])
            avg_confidence = sum([p['confidence'] for p in pages]) / len(pages) if pages else 0.0
            
            return {
                "text": combined_text,
                "confidence": avg_confidence,
                "pages": pages,
                "engine": self.engine,
                "source_file": os.path.basename(file_path)
            }
        elif file_ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
            return self.extract_from_image(file_path, preprocess)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
