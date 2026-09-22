"""Safe JSON data loader with validation and error handling."""
import json
import os
import logging
from typing import Any

from config import DATA_DIR, logger

class DataLoaderError(Exception):
    """Custom exception for data loading errors."""
    pass

def load_json_file(filename: str) -> Any:
    """Safely load and parse a JSON file from the data directory.
    
    Args:
        filename: Name of the JSON file (e.g. 'creatures.json')
        
    Returns:
        The parsed JSON data (dict or list)
        
    Raises:
        DataLoaderError: If file is missing, invalid JSON, or unreadable.
    """
    path = os.path.join(DATA_DIR, filename)
    
    if not os.path.exists(path):
        logger.error(f"Data file missing: {filename}")
        raise DataLoaderError(f"Data file not found: {path}")
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.debug(f"Successfully loaded {filename}")
            return data
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filename}: {e}")
        raise DataLoaderError(f"Failed to parse JSON in {filename}: {e}")
    except Exception as e:
        logger.error(f"Error reading {filename}: {e}")
        raise DataLoaderError(f"Unexpected error reading {filename}: {e}")
