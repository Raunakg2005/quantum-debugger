#!/usr/bin/env python3
"""Quick cleanup script for QML warnings"""
import re
from pathlib import Path

def fix_whitespace_file(filepath):
    """Remove trailing whitespace and whitespace-only blank lines"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    for line in lines:
        # Remove trailing whitespace
        line = line.rstrip() + '\n' if line.endswith('\n') else line.rstrip()
        fixed_lines.append(line)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"Fixed whitespace in {filepath}")

# Fix whitespace in data/ files
data_dir = Path('quantum_debugger/qml/data')
for file in ['dataset.py', 'feature_maps.py']:
    fix_whitespace_file(data_dir / file)

print("\nWhitespace cleanup complete!")
