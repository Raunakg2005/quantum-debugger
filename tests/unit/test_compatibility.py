"""
Cross-Version Compatibility Tests
==================================

Test library works across Python 3.9, 3.10, 3.11, 3.12
"""

import pytest
import sys
import platform

def test_python_version_supported():
    """Ensure Python version is supported"""
    version = sys.version_info
    assert version >= (3, 9), f"Python {version.major}.{version.minor} not supported (need 3.9+)"
    assert version < (4, 0), f"Python {version.major}.{version.minor} not tested"
    print(f"Running on Python {version.major}.{version.minor}.{version.micro}")


def test_platform_detection():
    """Test platform detection"""
    os_name = platform.system()
    assert os_name in ['Windows', 'Linux', 'Darwin'], f"Unknown OS: {os_name}"
    print(f"Running on: {os_name}")


def test_required_packages_available():
    """Test all required dependencies are available"""
    required = ['numpy', 'scipy', 'pytest']
    
    for package in required:
        try:
            __import__(package)
            print(f"  ✓ {package} available")
        except ImportError:
            pytest.fail(f"Required package '{package}' not available")


def test_numpy_version_compatibility():
    """Test numpy version is compatible"""
    import numpy as np
    version = [int(x) for x in np.__version__.split('.')[:2]]
    
    assert version >= [1, 20], f"NumPy {np.__version__} too old (need 1.20+)"
    print(f"NumPy version: {np.__version__}")


def test_scipy_version_compatibility():
    """Test scipy version is compatible"""
    import scipy
    version = [int(x) for x in scipy.__version__.split('.')[:2]]
    
    assert version >= [1, 7], f"SciPy {scipy.__version__} too old (need 1.7+)"
    print(f"SciPy version: {scipy.__version__}")


def test_qml_import_in_clean_env():
    """Test QML module can be imported"""
    try:
        from quantum_debugger import qml
        print(f"  ✓ quantum_debugger.qml imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import QML: {e}")


def test_all_submodules_importable():
    """Test all QML submodules can be imported"""
    submodules = [
        'quantum_debugger.qml.gates',
        'quantum_debugger.qml.algorithms',
        'quantum_debugger.qml.hamiltonians',
        'quantum_debugger.qml.optimizers',
        'quantum_debugger.qml.ansatz',
        'quantum_debugger.qml.training',
    ]
    
    for module in submodules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError as e:
            pytest.fail(f"Failed to import {module}: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
