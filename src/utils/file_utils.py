"""
Utility functions for file handling
"""
import os
import hashlib
from pathlib import Path
from typing import Optional
from datetime import datetime
import logging

from config import get_config

logger = logging.getLogger(__name__)
config = get_config()


def allowed_file(filename: str) -> bool:
    """
    Check if file extension is allowed
    
    Args:
        filename: Name of the file
        
    Returns:
        True if extension is allowed
    """
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS


def get_file_extension(filename: str) -> str:
    """
    Get file extension
    
    Args:
        filename: Name of the file
        
    Returns:
        File extension (lowercase)
    """
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''


def generate_unique_filename(filename: str) -> str:
    """
    Generate unique filename using timestamp and hash
    
    Args:
        filename: Original filename
        
    Returns:
        Unique filename
    """
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    file_hash = hashlib.md5(filename.encode()).hexdigest()[:8]
    extension = get_file_extension(filename)
    
    base_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
    base_name = base_name[:50]  # Limit length
    
    return f"{base_name}_{timestamp}_{file_hash}.{extension}"


def save_uploaded_file(file_content: bytes, filename: str) -> Path:
    """
    Save uploaded file to upload directory
    
    Args:
        file_content: File content as bytes
        filename: Original filename
        
    Returns:
        Path to saved file
    """
    try:
        # Generate unique filename
        unique_filename = generate_unique_filename(filename)
        
        # Ensure upload directory exists
        config.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = config.UPLOAD_FOLDER / unique_filename
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        logger.info(f"File saved: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Failed to save file {filename}: {e}")
        raise


def delete_file(file_path: Path) -> bool:
    """
    Delete file from filesystem
    
    Args:
        file_path: Path to file
        
    Returns:
        True if file was deleted
    """
    try:
        if file_path.exists():
            file_path.unlink()
            logger.info(f"File deleted: {file_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to delete file {file_path}: {e}")
        return False


def get_file_size(file_path: Path) -> int:
    """
    Get file size in bytes
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in bytes
    """
    return file_path.stat().st_size if file_path.exists() else 0


def validate_file_size(file_size: int) -> bool:
    """
    Validate if file size is within allowed limit
    
    Args:
        file_size: File size in bytes
        
    Returns:
        True if file size is valid
    """
    return file_size <= config.MAX_FILE_SIZE
