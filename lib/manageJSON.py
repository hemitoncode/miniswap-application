import json
import os

def append_to_json(item):
    """
    Append a JSON object to the output file.
    
    Args:
        item (dict): Dictionary containing kit details (name, description, last_known_price, sku)
    """
    filepath = os.path.abspath('output.json')
    
    # Try to load existing data, or start with empty list if file doesn't exist or is invalid
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # File doesn't exist or is empty/invalid - start fresh
        data = []
    
    # Append new item to the data
    data.append(item)
    
    # Write updated data back to the file
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)