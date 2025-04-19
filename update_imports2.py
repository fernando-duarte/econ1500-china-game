#!/usr/bin/env python
"""
Script to update all imports from china_growth_game to economic_model_py.
"""

import os

def update_imports_in_file(file_path):
    """Update imports in a single file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Replace imports
        updated_content = content.replace('china_growth_game', 'economic_model_py')
        
        # Write back if changes were made
        if content != updated_content:
            with open(file_path, 'w') as f:
                f.write(updated_content)
            return True
        return False
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def update_imports_in_directory(directory):
    """Update imports in all Python files in a directory and its subdirectories."""
    count = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if update_imports_in_file(file_path):
                    print(f"Updated imports in {file_path}")
                    count += 1
    return count

if __name__ == "__main__":
    # Update imports in the economic_model_py directory
    count = update_imports_in_directory('economic_model_py')
    print(f"Updated imports in {count} files")
