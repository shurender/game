import os
import json
import pytest

from game.utils.data_loader import load_json_file, DataLoaderError
from config import DATA_DIR


class TestDataLoader:
    
    def test_load_valid_json(self):
        # Using types.json as a known valid file
        data = load_json_file("types.json")
        assert "types" in data
        assert isinstance(data["types"], list)
        
    def test_load_missing_file(self):
        with pytest.raises(DataLoaderError, match="Data file not found"):
            load_json_file("nonexistent_file_12345.json")
            
    def test_load_invalid_json(self):
        # Create a temporary invalid JSON file
        invalid_file = "invalid_temp.json"
        invalid_path = os.path.join(DATA_DIR, invalid_file)
        
        with open(invalid_path, "w", encoding="utf-8") as f:
            f.write("{ invalid json format ]")
            
        try:
            with pytest.raises(DataLoaderError, match="Failed to parse JSON"):
                load_json_file(invalid_file)
        finally:
            # Clean up
            if os.path.exists(invalid_path):
                os.remove(invalid_path)
