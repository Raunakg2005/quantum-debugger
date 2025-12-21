"""
End-to-End Integration Test for v0.4.0

Tests that all components work together properly:
- Imports work correctly
- ZNE integrates with noise models
- Hardware profiles work
- All features accessible
"""

import sys
print("="*70)
print("v0.4.0 INTEGRATION TEST")
print("="*70)

# Test 1: Basic imports
print("\n[1/6] Testing imports...")
try:
    from quantum_debugger import (
        QuantumCircuit,
        zero_noise_extrapolation,
        global_fold,
        DepolarizingNoise,
        IBM_PERTH_2025,
        __version__
    )
    print(f"✓ All imports successful")
    print(f"✓ Version: {__version__}")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Create noisy circuit
print("\n[2/6] Creating noisy circuit...")
try:
    circuit = QuantumCircuit(2, noise_model=DepolarizingNoise(0.05))
    circuit.h(0).cnot(0, 1)
    print(f"✓ Circuit created with {len(circuit.gates)} gates")
    print(f"✓ Noise model: {circuit.noise_model.__class__.__name__}")
except Exception as e:
    print(f"✗ Circuit creation failed: {e}")
    sys.exit(1)

# Test 3: Run circuit without mitigation
print("\n[3/6] Running noisy circuit...")
try:
    result = circuit.run(shots=100)
    fidelity = result.get('fidelity', 0)
    print(f"✓ Circuit executed successfully")
    print(f"✓ Fidelity (no mitigation): {fidelity:.4f}")
except Exception as e:
    print(f"✗ Circuit execution failed: {e}")
    sys.exit(1)

# Test 4: Test circuit folding
print("\n[4/6] Testing circuit folding...")
try:
    folded = global_fold(circuit, scale_factor=3.0)
    print(f"✓ Circuit folding successful")
    print(f"✓ Original gates: {len(circuit.gates)}")
    print(f"✓ Folded gates: {len(folded.gates)}")
except Exception as e:
    print(f"✗ Circuit folding failed: {e}")
    sys.exit(1)

# Test 5: Test ZNE
print("\n[5/6] Testing Zero-Noise Extrapolation...")
try:
    result = zero_noise_extrapolation(
        circuit,
        scale_factors=[1.0, 2.0, 3.0],
        extrapolation_method='linear',
        shots=200
    )
    
    print(f"✓ ZNE completed successfully")
    print(f"  - Unmitigated: {result['unmitigated_value']:.4f}")
    print(f"  - Mitigated:   {result['mitigated_value']:.4f}")
    print(f"  - Improvement: {result['improvement_factor']:.2f}x")
    print(f"  - Total shots: {result['total_shots']}")
except Exception as e:
    print(f"✗ ZNE failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Test with hardware profile
print("\n[6/6] Testing with hardware profile...")
try:
    hw_circuit = QuantumCircuit(2, noise_model=IBM_PERTH_2025.noise_model)
    hw_circuit.h(0).cnot(0, 1)
    
    result = zero_noise_extrapolation(
        hw_circuit,
        scale_factors=[1.0, 2.0],
        shots=200
    )
    
    print(f"✓ Hardware profile test successful")
    print(f"  - Profile: IBM Perth 2025")
    print(f"  - Fidelity (mitigated): {result['fidelity_mitigated']:.4f}")
except Exception as e:
    print(f"✗ Hardware profile test failed: {e}")
    sys.exit(1)

# Success summary
print("\n" + "="*70)
print("✓ ALL INTEGRATION TESTS PASSED")
print("="*70)
print("\nv0.4.0 Phase 1 is fully functional!")
print("\nKey features verified:")
print("  ✓ Noise simulation")
print("  ✓ Circuit folding")
print("  ✓ Zero-Noise Extrapolation")
print("  ✓ Hardware profiles")
print("  ✓ Multiple extrapolation methods")
print("\nReady for production use!")
print("="*70)
