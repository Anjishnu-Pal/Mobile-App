"""
P4A build hook to fix pyjnius Python 3 compatibility issues.
Patches the pyjnius Cython source to remove Python 2 'long' type references.
"""

import os
import re


def patch_pyjnius_source(build_ctx):
    """Patch pyjnius source to be Python 3 compatible."""
    # Find the pyjnius recipe
    pyjnius_dir = None
    
    # Search in build other_builds
    build_base = build_ctx.build_dir
    search_paths = [
        os.path.join(build_base, 'other_builds', 'pyjnius'),
        os.path.join(build_ctx.build_dir, '..', 'other_builds', 'pyjnius'),
    ]
    
    for path in search_paths:
        if os.path.exists(path):
            pyjnius_dir = path
            break
    
    if not pyjnius_dir:
        # Try to find it in .buildozer
        for root, dirs, files in os.walk(os.path.expanduser('~/.buildozer')):
            if 'pyjnius_utils.pxi' in files or 'jnius.pyx' in files:
                pyjnius_dir = root
                break
    
    if not pyjnius_dir:
        print("WARNING: Could not find pyjnius directory to patch")
        return
    
    # Patch jnius_utils.pxi
    utils_file = os.path.join(pyjnius_dir, 'jnius', 'jnius_utils.pxi')
    if os.path.exists(utils_file):
        print(f"Patching {utils_file}")
        with open(utils_file, 'r') as f:
            content = f.read()
        
        # Replace "isinstance(arg, long)" with "False" (long never happens in Python 3)
        # or replace entire check with int-only check
        original_content = content
        
        # Pattern: isinstance(arg, long)
        content = re.sub(
            r'isinstance\s*\(\s*arg\s*,\s*long\s*\)',
            'False',
            content
        )
        
        # Also fix: (isinstance(arg, long) and ...)
        content = re.sub(
            r'\(\s*isinstance\s*\(\s*arg\s*,\s*long\s*\)\s*and\s+([^)]+)\)',
            r'False',
            content
        )
        
        if content != original_content:
            with open(utils_file, 'w') as f:
                f.write(content)
            print(f"Successfully patched {utils_file}")
        else:
            print(f"No changes made to {utils_file}")
    
    # Patch jnius.pyx if needed
    pyx_file = os.path.join(pyjnius_dir, 'jnius', 'jnius.pyx')
    if os.path.exists(pyx_file):
        print(f"Checking {pyx_file}")
        with open(pyx_file, 'r') as f:
            content = f.read()
        
        original_content = content
        
        # Add Python 3 compatibility directive at the top
        if 'cython: language_level' not in content:
            # Add language level directive
            content = '# cython: language_level=3\n' + content
        
        if content != original_content:
            with open(pyx_file, 'w') as f:
                f.write(content)
            print(f"Added compatibility directive to {pyx_file}")


# Entry point for p4a hook
def run(build_ctx):
    """Main entry point for the build hook."""
    print("Running p4a_build_hook.py...")
    patch_pyjnius_source(build_ctx)
