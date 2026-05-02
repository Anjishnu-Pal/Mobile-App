#!/usr/bin/env python3
"""
Comprehensive patcher for Python 2 long type in Kivy Cython code.
Patches all .pyx and .pxd files to be Python 3 compatible.
"""

import os
import re
from pathlib import Path


def patch_kivy_cython():
    """Patch all Kivy Cython files for Python 3 compatibility."""
    
    kivy_base = Path('/workspaces/SensorMonitor/.buildozer/android/platform/build-arm64-v8a/build/other_builds/kivy')
    if not kivy_base.exists():
        print("Kivy directory not found")
        return 0
    
    # Find all kivy source files
    kivy_src = None
    for item in kivy_base.rglob('jnius'):
        if item.is_dir() and 'kivy' in str(item.parent):
            kivy_src = item.parent
            break
    
    if not kivy_src:
        for item in kivy_base.rglob('kivy'):
            if item.is_dir() and (item / '__init__.py').exists():
                kivy_src = item
                break
    
    if not kivy_src:
        kivy_src = kivy_base / 'arm64-v8a__ndk_target_21' / 'kivy' / 'kivy'
    
    if not kivy_src.exists():
        print(f"Kivy source not found at {kivy_src}")
        return 0
    
    print(f"Patching Kivy at: {kivy_src}")
    
    patched_files = 0
    
    # Patch all .pyx and .pxd files
    for pattern in ['*.pyx', '*.pxd', '**/*.pyx', '**/*.pxd']:
        for filepath in kivy_src.glob(pattern):
            if patch_file(filepath):
                patched_files += 1
    
    print(f"\nPatched {patched_files} files")
    return patched_files


def patch_file(filepath):
    """Patch a single Cython file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except:
        return False
    
    original = content
    
    # Pattern 1: isinstance(..., long)
    content = re.sub(r'isinstance\s*\(\s*(\w+)\s*,\s*long\s*\)', r'isinstance(\1, int)', content)
    
    # Pattern 2: isinstance(..., (long, ...)) or isinstance(..., (..., long))
    content = re.sub(r'isinstance\s*\(\s*(\w+)\s*,\s*\(\s*long\s*,', r'isinstance(\1, (int,', content)
    content = re.sub(r',\s*long\s*\)', ',)', content)
    
    # Pattern 3: (long, int) -> (int,)
    content = re.sub(r'\(\s*long\s*,\s*int\s*\)', r'(int,)', content)
    content = re.sub(r'\(\s*int\s*,\s*long\s*\)', r'(int,)', content)
    
    # Pattern 4: long: XXX (dictionary keys)
    content = re.sub(r'\blong\s*:', r'int:', content)
    
    # Pattern 5: def __long__(...): - just remove the method since Python 3 doesn't have __long__
    lines = content.split('\n')
    result_lines = []
    skip_next = 0
    for i, line in enumerate(lines):
        if skip_next > 0:
            skip_next -= 1
            continue
        if re.match(r'\s*def\s+__long__\s*\(', line):
            # Skip this method - find the next method or unindented line
            indent_level = len(line) - len(line.lstrip())
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                if next_line.strip() and not next_line.startswith(' ' * (indent_level + 1)):
                    break
                skip_next += 1
                j += 1
            continue
        result_lines.append(line)
    
    content = '\n'.join(result_lines)
    
    if content != original:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ {filepath.name}")
            return True
        except:
            return False
    
    return False


if __name__ == '__main__':
    import sys
    result = patch_kivy_cython()
    sys.exit(0 if result > 0 else 1)
