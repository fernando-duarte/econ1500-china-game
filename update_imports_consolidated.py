#!/usr/bin/env python
"""
Script to update all imports from china_growth_game to economic_model_py.
This consolidated script combines the functionality of update_imports.py and update_imports2.py.
"""

import os
import re
import argparse
import sys

def update_imports_in_file(file_path, old_module='china_growth_game', new_module='economic_model_py', verbose=False):
    """
    Update imports in a single file.
    
    Args:
        file_path: Path to the file to update
        old_module: The module name to replace
        new_module: The new module name
        verbose: Whether to print detailed information
        
    Returns:
        bool: True if changes were made, False otherwise
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Method 1: Regex-based replacement for specific import patterns
        updated_content = re.sub(
            rf'from {old_module}\.', 
            f'from {new_module}.', 
            content
        )
        updated_content = re.sub(
            rf'import {old_module}\.', 
            f'import {new_module}.', 
            updated_content
        )
        updated_content = re.sub(
            rf'@patch\(\'{old_module}\.', 
            f'@patch(\'{new_module}.', 
            updated_content
        )
        
        # Method 2: Simple string replacement for any remaining occurrences
        # This catches any other references to the old module name
        if old_module in updated_content:
            updated_content = updated_content.replace(old_module, new_module)
        
        # Write back if changes were made
        if content != updated_content:
            with open(file_path, 'w') as f:
                f.write(updated_content)
            return True
        return False
    except Exception as e:
        if verbose:
            print(f"Error updating {file_path}: {e}", file=sys.stderr)
        return False

def update_imports_in_directory(directory, old_module='china_growth_game', new_module='economic_model_py', 
                               file_extensions=('.py',), verbose=False):
    """
    Update imports in all files with specified extensions in a directory and its subdirectories.
    
    Args:
        directory: Directory to search for files
        old_module: The module name to replace
        new_module: The new module name
        file_extensions: Tuple of file extensions to process
        verbose: Whether to print detailed information
        
    Returns:
        int: Number of files updated
    """
    count = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in file_extensions):
                file_path = os.path.join(root, file)
                if update_imports_in_file(file_path, old_module, new_module, verbose):
                    print(f"Updated imports in {file_path}")
                    count += 1
                elif verbose:
                    print(f"No changes needed in {file_path}")
    return count

def main():
    """Main function to parse arguments and run the import updater."""
    parser = argparse.ArgumentParser(description='Update module imports in Python files.')
    parser.add_argument('directory', nargs='?', default='economic_model_py',
                        help='Directory to process (default: economic_model_py)')
    parser.add_argument('--old-module', default='china_growth_game',
                        help='Old module name to replace (default: china_growth_game)')
    parser.add_argument('--new-module', default='economic_model_py',
                        help='New module name (default: economic_model_py)')
    parser.add_argument('--extensions', default='.py', 
                        help='Comma-separated list of file extensions to process (default: .py)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Print verbose output')
    
    args = parser.parse_args()
    
    # Convert extensions string to tuple
    extensions = tuple(ext.strip() for ext in args.extensions.split(','))
    
    # Run the update
    count = update_imports_in_directory(
        args.directory, 
        args.old_module, 
        args.new_module, 
        extensions,
        args.verbose
    )
    
    print(f"Updated imports in {count} files")

if __name__ == "__main__":
    main()
