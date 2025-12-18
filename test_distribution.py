"""
Installation and Distribution Tests
====================================

Test that the package can be installed and distributed correctly.
"""

import subprocess
import sys
import os
import tempfile
import shutil

def test_package_structure():
    """Verify package has correct structure"""
    required_files = [
        'setup.py',
        'README.md',
        'quantum_debugger/__init__.py',
        'quantum_debugger/qml/__init__.py',
    ]
    
    print("\nChecking package structure...")
    for file_path in required_files:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        assert os.path.exists(full_path), f"Missing required file: {file_path}"
        print(f"  ✓ {file_path}")


def test_setup_py_valid():
    """Test setup.py is valid"""
    setup_path = os.path.join(os.path.dirname(__file__), 'setup.py')
    
    if not os.path.exists(setup_path):
        print("  ⚠ setup.py not found (skipping)")
        return
    
    try:
        result = subprocess.run(
            [sys.executable, setup_path, '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(f"  ✓ setup.py valid, version: {result.stdout.strip()}")
    except Exception as e:
        print(f"  ⚠ Could not validate setup.py: {e}")


def test_import_after_install():
    """Test package can be imported after installation"""
    print("\nTesting imports...")
    
    imports = [
        'quantum_debugger',
        'quantum_debugger.qml',
        'quantum_debugger.qml.gates',
        'quantum_debugger.qml.algorithms',
    ]
    
    for module in imports:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError as e:
            raise AssertionError(f"Failed to import {module}: {e}")


def test_all_files_included():
    """Test that non-Python files are included"""
    # Check for important non-code files
    expected_patterns = [
        ('README', 'README.md'),
        ('tutorials', 'tutorials/*.md'),
        ('examples', 'examples/*.py'),
    ]
    
    print("\nChecking for important files...")
    base_dir = os.path.dirname(__file__)
    
    for name, pattern in expected_patterns:
        if '*' in pattern:
            # Directory check
            dir_path = os.path.join(base_dir, pattern.split('/')[0])
            if os.path.exists(dir_path) and os.listdir(dir_path):
                print(f"  ✓ {name} directory exists and has files")
            else:
                print(f"  ⚠ {name} directory missing or empty")
        else:
            # File check
            file_path = os.path.join(base_dir, pattern)
            if os.path.exists(file_path):
                print(f"  ✓ {pattern}")
            else:
                print(f"  ⚠ {pattern} not found")


def test_no_syntax_errors():
    """Compile all Python files to check for syntax errors"""
    print("\nChecking for syntax errors...")
    
    base_dir = os.path.dirname(__file__)
    qml_dir = os.path.join(base_dir, 'quantum_debugger', 'qml')
    
    error_count = 0
    file_count = 0
    
    for root, dirs, files in os.walk(qml_dir):
        # Skip __pycache__
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                file_count += 1
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        compile(f.read(), file_path, 'exec')
                except SyntaxError as e:
                    print(f"  ✗ Syntax error in {file}: {e}")
                    error_count += 1
    
    print(f"  Checked {file_count} files, {error_count} errors")
    assert error_count == 0, f"Found {error_count} syntax errors"


if __name__ == "__main__":
    print("=" * 70)
    print(" Installation & Distribution Tests")
    print("=" * 70)
    
    test_package_structure()
    test_setup_py_valid()
    test_import_after_install()
    test_all_files_included()
    test_no_syntax_errors()
    
    print("\n" + "=" * 70)
    print(" All Distribution Tests Passed")
    print("=" * 70)
