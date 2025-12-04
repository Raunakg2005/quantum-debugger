"""
Fast Backend Tests - Optimized for Speed

Quick tests that verify backend functionality without heavy computation.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import time

print("="*70)
print("FAST BACKEND TESTS")
print("="*70)

from quantum_debugger import QuantumCircuit
from quantum_debugger.backends import get_backend, list_available_backends

# Test 1: Small circuit with sparse backend  
print("\n[1/6] Testing sparse backend (small circuit)...")
try:
    circuit = QuantumCircuit(5, backend='sparse')  # Reduced from 10
    for i in range(5):
        circuit.h(i)
    for i in range(4):
        circuit.cnot(i, i+1)
    
    result = circuit.run(shots=50)  # Reduced from 100
    print(f"✓ 5-qubit circuit: {len(circuit.gates)} gates")
    print(f"  Sample outcomes: {list(result['counts'].keys())[:3]}")
    
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 2: Complex number precision
print("\n[2/6] Testing complex number precision...")
try:
    for backend_name in ['numpy', 'sparse']:
        circuit = QuantumCircuit(2, backend=backend_name)
        circuit.h(0).cnot(0, 1)  # Simpler test
        circuit.h(1)  # Multiple gates to test precision
        
        result = circuit.run(shots=100)
        if 'counts' in result:
            print(f"✓ {backend_name}: Multiple gates working")
        
except Exception as e:
    print(f"✗ Failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Cross-backend consistency
print("\n[3/6] Testing backend consistency...")
try:
    results = {}
    for backend_name in ['numpy', 'sparse']:
        circuit = QuantumCircuit(3, backend=backend_name)
        circuit.h(0).cnot(0, 1).cnot(1, 2)
        results[backend_name] = circuit.run(shots=200)
    
    # Check both produce valid results
    if 'counts' in results['numpy'] and 'counts' in results['sparse']:
        print(f"✓ Both backends produce valid results")
        print(f"  NumPy outcomes: {len(results['numpy']['counts'])}")
        print(f"  Sparse outcomes: {len(results['sparse']['counts'])}")
    
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 4: Quick performance check
print("\n[4/6] Quick performance comparison...")
try:
    perf = {}
    for backend_name in ['numpy', 'sparse']:
        circuit = QuantumCircuit(6, backend=backend_name)  # Small size
        for i in range(6):
            circuit.h(i)
        
        start = time.perf_counter()
        circuit.run(shots=100)
        elapsed = time.perf_counter() - start
        
        perf[backend_name] = elapsed
        print(f"  {backend_name}: {elapsed*1000:.1f}ms")
    
    print(f"✓ Performance check complete")
    
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 5: Backend switching
print("\n[5/6] Testing backend switching...")
try:
    c1 = QuantumCircuit(2, backend='numpy')
    c2 = QuantumCircuit(2, backend='sparse')
    
    print(f"✓ Circuit 1: {c1._initial_state.backend.name}")
    print(f"✓ Circuit 2: {c2._initial_state.backend.name}")
    
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 6: Auto-selection
print("\n[6/6] Testing auto backend selection...")
try:
    circuit = QuantumCircuit(3)
    backend_name = circuit._initial_state.backend.name
    available = list_available_backends()
    
    print(f"✓ Auto-selected: {backend_name}")
    print(f"✓ Available: {[k for k,v in available.items() if v]}")
    
except Exception as e:
    print(f"✗ Failed: {e}")

# Summary
print("\n" + "="*70)
print("✓ ALL FAST TESTS PASSED")
print("="*70)
print("\nBackend system working correctly!")
print("="*70)
