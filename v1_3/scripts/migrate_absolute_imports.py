#!/usr/bin/env python3
"""
Migration script for converting to absolute imports in AI Camera v1.3

This script updates all Python files to use absolute imports instead of relative imports.

Author: AI Camera Team
Version: 1.3
Date: August 7, 2025
"""

import os
import re
from pathlib import Path
from typing import List, Tuple


def find_python_files(directory: Path) -> List[Path]:
    """Find all Python files in the directory."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    return python_files


def convert_relative_to_absolute_import(file_path: Path) -> Tuple[bool, List[str]]:
    """
    Convert relative imports to absolute imports in a file.
    
    Returns:
        Tuple[bool, List[str]]: (modified, changes_made)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes = []
    
    # Convert relative imports to absolute imports
    # from . import -> from v1_3.src.
    # from .. import -> from v1_3.src.
    # from ... import -> from v1_3.src.
    
    # Pattern for relative imports
    relative_import_patterns = [
        (r'from \. import', 'from v1_3.src import'),
        (r'from \.\. import', 'from v1_3.src import'),
        (r'from \.\.\. import', 'from v1_3.src import'),
        (r'from \.(\w+) import', r'from v1_3.src.\1 import'),
        (r'from \.\.(\w+) import', r'from v1_3.src.\1 import'),
        (r'from \.\.\.(\w+) import', r'from v1_3.src.\1 import'),
    ]
    
    for pattern, replacement in relative_import_patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            changes.append(f"Converted: {pattern} -> {replacement}")
    
    # Convert specific module imports
    module_mapping = {
        'from core.': 'from v1_3.src.core.',
        'from components.': 'from v1_3.src.components.',
        'from services.': 'from v1_3.src.services.',
        'from web.': 'from v1_3.src.web.',
        'from utils.': 'from v1_3.src.core.utils.',
    }
    
    for old_import, new_import in module_mapping.items():
        if old_import in content:
            content = content.replace(old_import, new_import)
            changes.append(f"Converted: {old_import} -> {new_import}")
    
    # Write back if changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, changes
    
    return False, changes


def main():
    """Main migration function."""
    # Get the v1_3/src directory
    script_dir = Path(__file__).parent
    src_dir = script_dir.parent / 'src'
    
    if not src_dir.exists():
        print(f"Error: {src_dir} does not exist")
        return
    
    print(f"Starting migration of {src_dir}")
    
    # Find all Python files
    python_files = find_python_files(src_dir)
    print(f"Found {len(python_files)} Python files")
    
    total_modified = 0
    total_changes = 0
    
    for file_path in python_files:
        print(f"Processing: {file_path.relative_to(src_dir)}")
        modified, changes = convert_relative_to_absolute_import(file_path)
        
        if modified:
            total_modified += 1
            total_changes += len(changes)
            print(f"  ✓ Modified with {len(changes)} changes:")
            for change in changes:
                print(f"    - {change}")
        else:
            print(f"  - No changes needed")
    
    print(f"\nMigration complete!")
    print(f"Files modified: {total_modified}")
    print(f"Total changes: {total_changes}")


if __name__ == '__main__':
    main()
