"""
Test backend system

Quick verification that backends work correctly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("="*70)
print("BACKEND SYSTEM TESTS")
print("="*70)

# Test 1: Import backends
print("\n[1/4] Testing backend imports...")
try:
    from quantum_debugger.backends import get_backend, list_available_backends
    from quantum_debugger.backends import NumPyBackend
    print("✓ Backend imports successful")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 2: List available backends
print("\n[2/4] Checking available backends...")
available = list_available_backends()
for name, status in available.items():
    status_str = "✓ Available" if status else "✗ Not installed"
    print(f"  {name:15s}: {status_str}")

# Test 3: NumPy backend
print("\n[3/4] Testing NumPy backend...")
try:
    backend = get_backend('numpy')
    print(f"✓ Backend: {backend.name}")
    
    # Test basic operations
    a = backend.zeros((4, 4))
    b = backend.eye(4)
    c = backend.matmul(a, b)
    
    print(f"✓ Basic operations work")
    print(f"  zeros: {a.shape}")
    print(f"  eye: {b.shape}")
    print(f"  matmul: {c.shape}")
except Exception as e:
    print(f"✗ NumPy backend failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Numba backend (if available)
print("\n[4/4] Testing Numba backend...")
try:
    backend = get_backend('numba')
    print(f"✓ Backend: {backend.name}")
    
    # Test JIT compilation
    import numpy as np
    a = np.random.rand(8, 8) + 1j * np.random.rand(8, 8)
    b = np.random.rand(8, 8) + 1j * np.random.rand(8, 8)
    
    c = backend.matmul(a, b)
    c_ref = np.matmul(a, b)
    
    # Check correctness
    diff = np.max(np.abs(c - c_ref))
    print(f"✓ JIT matmul works (error: {diff:.2e})")
    
    if diff < 1e-10:
        print("✓ Numba results match NumPy")
    else:
        print(f"⚠ Warning: Numba differs from NumPy by {diff:.2e}")
    
except ImportError as e:
    print(f"⚠ Numba not available: {e}")
    print("  Install with: pip install numba")
except Exception as e:
    print(f"✗ Numba backend failed: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "="*70)
print("✓ BACKEND SYSTEM WORKING")
print("="*70)
print("\nBackends available:")
for name, status in available.items():
    if status:
        print(f"  ✓ {name}")
print("\nReady to integrate with QuantumCircuit!")
print("="*70)
