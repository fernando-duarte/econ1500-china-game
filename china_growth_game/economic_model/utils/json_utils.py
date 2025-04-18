"""
JSON utilities for the China Growth Game.

This module provides utilities for handling JSON serialization,
particularly for numpy types.
"""

import json
import numpy as np
from typing import Any, Dict, List, Union
from fastapi.responses import JSONResponse

class NumpyEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that handles numpy types.
    
    This encoder converts numpy types to Python native types:
    - np.integer -> int
    - np.floating -> float
    - np.ndarray -> list
    """
    def default(self, obj: Any) -> Any:
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif hasattr(obj, 'item'):  # For other numpy scalar types
            return obj.item()
        return super(NumpyEncoder, self).default(obj)

class CustomJSONResponse(JSONResponse):
    """
    Custom JSON response class that uses the NumpyEncoder.
    
    This class ensures that all responses from the API can handle numpy types.
    """
    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=NumpyEncoder,
        ).encode("utf-8")

def convert_numpy_values(obj: Any) -> Any:
    """
    Recursively convert numpy values to Python native types for JSON serialization.
    
    Args:
        obj: The object to convert
        
    Returns:
        The converted object with numpy types converted to Python native types
    """
    if isinstance(obj, dict):
        return {key: convert_numpy_values(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_values(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return convert_numpy_values(obj.tolist())
    elif hasattr(obj, 'item'):  # For other numpy scalar types
        return obj.item()
    else:
        return obj

def numpy_safe_json_dumps(obj: Any) -> str:
    """
    Convert an object to a JSON string, handling numpy types.
    
    Args:
        obj: The object to convert
        
    Returns:
        A JSON string representation of the object
    """
    return json.dumps(obj, cls=NumpyEncoder)

def numpy_safe_json_loads(json_str: str) -> Any:
    """
    Parse a JSON string into an object.
    
    Args:
        json_str: The JSON string to parse
        
    Returns:
        The parsed object
    """
    return json.loads(json_str)
