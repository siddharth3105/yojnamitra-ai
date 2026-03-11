#!/usr/bin/env python3
"""
Code Validation Script for YojnaMitra-AI
Run this before pushing to GitHub to catch errors early
"""

import sys
import py_compile
import os
from pathlib import Path

def validate_python_file(filepath):
    """Validate a single Python file for syntax errors"""
    try:
        py_compile.compile(filepath, doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)

def main():
    """Validate all Python files in the project"""
    
    print("🔍 YojnaMitra-AI Code Validator")
    print("=" * 50)
    
    # List of Python files to validate
    python_files = [
        'yojnamitra_ai.py',
        'auth_components.py',
        'database.py',
        'rag_engine.py',
        's3_storage.py',
        'check_bedrock_models.py'
    ]
    
    all_valid = True
    errors = []
    
    for filepath in python_files:
        if not os.path.exists(filepath):
            print(f"⚠️  {filepath} - NOT FOUND (skipping)")
            continue
            
        is_valid, error = validate_python_file(filepath)
        
        if is_valid:
            print(f"✅ {filepath} - VALID")
        else:
            print(f"❌ {filepath} - SYNTAX ERROR")
            print(f"   Error: {error}")
            all_valid = False
            errors.append((filepath, error))
    
    print("=" * 50)
    
    if all_valid:
        print("✅ ALL FILES VALID - READY TO DEPLOY!")
        return 0
    else:
        print(f"❌ FOUND {len(errors)} ERROR(S) - FIX BEFORE DEPLOYING")
        print("\nErrors Summary:")
        for filepath, error in errors:
            print(f"\n{filepath}:")
            print(f"  {error}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
