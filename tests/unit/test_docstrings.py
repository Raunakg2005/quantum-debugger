"""
Docstring Tests for QML Module
===============================

Tests all code examples in docstrings to ensure documentation accuracy.
"""

import doctest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_docstring_tests():
    """Run all docstring tests in the QML module"""

    print("=" * 70)
    print(" Running Docstring Tests")
    print("=" * 70)

    modules_to_test = [
        "quantum_debugger.qml.gates.parameterized",
        "quantum_debugger.qml.algorithms.vqe",
        "quantum_debugger.qml.algorithms.qaoa",
        "quantum_debugger.qml.hamiltonians.molecular",
        "quantum_debugger.qml.optimizers",
        "quantum_debugger.qml.utils.gradients",
    ]

    total_failures = 0
    total_tests = 0

    for module_name in modules_to_test:
        print(f"\nTesting: {module_name}")
        try:
            module = __import__(module_name, fromlist=[""])
            result = doctest.testmod(module, verbose=False)

            total_tests += result.attempted
            total_failures += result.failed

            if result.failed == 0:
                print(f"  ✓ {result.attempted} tests passed")
            else:
                print(f"  ✗ {result.failed}/{result.attempted} tests failed")

        except ImportError as e:
            print(f"  ⚠ Could not import: {e}")

    print("\n" + "=" * 70)
    print(f" Summary: {total_tests - total_failures}/{total_tests} tests passed")
    print("=" * 70)

    return total_failures == 0


if __name__ == "__main__":
    success = run_docstring_tests()
    sys.exit(0 if success else 1)
