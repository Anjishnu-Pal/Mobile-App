#!/usr/bin/env python3
"""
Direct patcher for pyjnius Python 3 compatibility.
Run this before buildozer to patch extracted pyjnius sources.
"""

import os
import re
import sys
import shutil
from pathlib import Path


def find_pyjnius_dirs():
    """Find all pyjnius directories in buildozer cache."""
    dirs = []
    
    # Check .buildozer directory
    buildozer_base = Path.home() / '.buildozer'
    if buildozer_base.exists():
        for root, subdirs, files in os.walk(buildozer_base):
            if 'jnius_utils.pxi' in files or 'jnius.pyx' in files:
                dirs.append(Path(root).parent)
    
    # Also check local .buildozer
    local_buildozer = Path('/workspaces/SensorMonitor/.buildozer')
    if local_buildozer.exists():
        for root, subdirs, files in os.walk(local_buildozer):
            if 'jnius_utils.pxi' in files or 'jnius.pyx' in files:
                dirs.append(Path(root).parent)
    
    return dirs


def patch_pyx_file(filepath):
    """Patch a .pyx or .pxi file to be Python 3 compatible."""
    filepath_str = str(filepath)
    print(f"Patching {filepath_str}...")
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    original = content
    
    # Add language level directive if not present
    if 'cython: language_level' not in content and filepath_str.endswith('.pyx'):
        lines = content.split('\n')
        # Insert after any module docstring
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('"""') or line.strip().startswith("'''"):
                # Find the closing triple quote
                for j in range(i + 1, len(lines)):
                    if '"""' in lines[j] or "'''" in lines[j]:
                        insert_idx = j + 1
                        break
                break
        
        directive = '# cython: language_level=3\n'
        lines.insert(insert_idx, directive)
        content = '\n'.join(lines)
    
    # Fix isinstance(arg, long) - replace with check for int only
    # Pattern 1: Direct isinstance call
    content = re.sub(
        r'\bisinstance\s*\(\s*(\w+)\s*,\s*long\s*\)',
        r'isinstance(\1, int)',  # In Python 3, long is int
        content
    )
    
    # Pattern 2: isinstance with tuple of types including long
    # e.g., isinstance(arg, (int, long)) -> isinstance(arg, (int,))
    content = re.sub(
        r'\bisinstance\s*\(\s*(\w+)\s*,\s*\(\s*int\s*,\s*long\s*\)\s*\)',
        r'isinstance(\1, (int,))',
        content
    )
    
    # Pattern 3: isinstance with tuple including long at different positions
    content = re.sub(
        r',\s*long\s*\)',
        ',)',
        content
    )
    content = re.sub(
        r'\(\s*long\s*,',
        '(int,',
        content
    )
    
    # Pattern 4: long as dictionary key or variable
    # Replace 'long:' with 'int:' in dictionary definitions
    content = re.sub(
        r'\blong\s*:\s*',
        r'int: ',
        content
    )
    
    # Pattern 5: int: 'I', long: 'J', etc. (JNI type codes)
    # In this case, since long doesn't exist in Python 3, we can just remove it or comment it
    # But we need to keep the dictionary valid Cython code
    lines = content.split('\n')
    result_lines = []
    for i, line in enumerate(lines):
        # Look for the pattern: "long: 'J'" in a dictionary
        if re.search(r'\blong\s*:\s*[\'"]J[\'"]', line):
            # Replace long with int for the conversion
            line = re.sub(r'\blong\s*(\s*:\s*)', r'int\1', line)
        result_lines.append(line)
    content = '\n'.join(result_lines)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Patched successfully")
        return True
    else:
        print(f"  - No changes needed")
        return False


def patch_pyjnius_directory(pyjnius_dir):
    """Patch all relevant files in a pyjnius directory."""
    pyjnius_dir = Path(pyjnius_dir)
    print(f"\nProcessing: {pyjnius_dir}")
    
    jnius_dir = pyjnius_dir / 'jnius'
    if not jnius_dir.exists():
        print(f"  WARNING: {jnius_dir} not found")
        return False
    
    patched = False
    
    # Patch .pyx and .pxi files
    for pattern in ['*.pyx', '*.pxi', '*.pxd']:
        for filepath in jnius_dir.glob(pattern):
            if patch_pyx_file(filepath):
                patched = True
    
    return patched


def main():
    """Main entry point."""
    print("=" * 60)
    print("PyJNIus Python 3 Compatibility Patcher")
    print("=" * 60)
    
    dirs = find_pyjnius_dirs()
    
    if not dirs:
        print("\nNo pyjnius directories found in buildozer cache.")
        print("This script should be run after buildozer has downloaded")
        print("the pyjnius recipe but before compilation.")
        print("\nYou can:")
        print("1. Run: pipython < buildozer android debug")
        print("2. Wait for it to extract pyjnius")
        print("3. Then run this script to patch it")
        print("4. Then press Ctrl+C and re-run buildozer")
        return 1
    
    print(f"\nFound {len(dirs)} pyjnius director(ies):\n")
    
    any_patched = False
    for dir_path in dirs:
        if patch_pyjnius_directory(dir_path):
            any_patched = True
    
    print("\n" + "=" * 60)
    if any_patched:
        print("Patching complete! You can now run buildozer.")
    else:
        print("No patching needed.")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
