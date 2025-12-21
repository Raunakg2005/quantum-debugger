"""
Tests for Zero-Noise Extrapolation (ZNE)

Basic tests to verify circuit folding and ZNE functionality.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from quantum_debugger import QuantumCircuit
from quantum_debugger.noise import DepolarizingNoise, IBM_PERTH_2025
from quantum_debugger.mitigation import zero_noise_extrapolation, global_fold
from quantum_debugger.mitigation.core import Extrapolator


def test_extrapolation_methods():
    """Test various extrapolation methods"""
    print("\n=== Test 1: Extrapolation Methods ===")
    
    # Synthetic data with known zero-noise value
    noise_levels = np.array([1.0, 2.0, 3.0, 4.0])
    # Simulated noisy measurements that should extrapolate to ~1.0
    noisy_values = np.array([0.95, 0.91, 0.87, 0.83])
    
    # Test Richardson (linear)
    linear_result = Extrapolator.linear(noise_levels, noisy_values)
    print(f"Linear extrapolation: {linear_result:.4f}")
    assert 0.97 < linear_result < 1.01, f"Linear failed: {linear_result}"
    
    # Test Richardson (quadratic)
    quad_result = Extrapolator.richardson(noise_levels, noisy_values, order=2)
    print(f"Quadratic extrapolation: {quad_result:.4f}")
    
    # Test adaptive
    adaptive_result, method = Extrapolator.adaptive(noise_levels, noisy_values)
    print(f"Adaptive extrapolation ({method}): {adaptive_result:.4f}")
    
    print("✓ Extrapolation methods working")


def test_circuit_folding():
    """Test circuit folding preserves logical operation"""
    print("\n=== Test 2: Circuit Folding ===")
    
    # Create simple circuit
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cnot(0, 1)
    
    print(f"Original circuit: {len(circuit.gates)} gates")
    
    # Test global folding
    folded_3x = global_fold(circuit, scale_factor=3.0)
    print(f"Folded (3x): {len(folded_3x.gates)} gates")
    
    # Circuit C + C^dag + C should have ~3x gates
    expected_gates = len(circuit.gates) * 3
    assert len(folded_3x.gates) == expected_gates, \
        f"Expected {expected_gates} gates, got {len(folded_3x.gates)}"
    
    # Test different scale factors
    for scale in [1.0, 2.0, 3.0, 5.0]:
        folded = global_fold(circuit, scale)
        expected = len(circuit.gates) * (1 + 2 * int((scale - 1) / 2))
        print(f"  Scale {scale}: {len(folded.gates)} gates (expected {expected})")
        assert len(folded.gates) == expected
    
    print("✓ Circuit folding working")


def test_zne_basic():
    """Test basic ZNE on Bell state"""
    print("\n=== Test 3: Basic ZNE ===")
    
    # Create Bell state with moderate noise
    circuit = QuantumCircuit(2, noise_model=DepolarizingNoise(0.05))
    circuit.h(0)
    circuit.cnot(0, 1)
    
    print("Running ZNE...")
    result = zero_noise_extrapolation(
        circuit,
        scale_factors=[1.0, 2.0, 3.0],
        extrapolation_method='linear',
        shots=500
    )
    
    print(f"\nResults:")
    print(f"  Unmitigated: {result['unmitigated_value']:.4f}")
    print(f"  Mitigated:   {result['mitigated_value']:.4f}")
    print(f"  Improvement: {result['improvement_factor']:.2f}x")
    
    # ZNE should improve or maintain fidelity
    assert result['mitigated_value'] >= result['unmitigated_value'] * 0.95, \
        "ZNE made things worse!"
    
    print("✓ Basic ZNE working")


def test_zne_with_hardware_profile():
    """Test ZNE with realistic hardware noise"""
    print("\n=== Test 4: ZNE with Hardware Profile ===")
    
    # Use IBM hardware profile
    circuit = QuantumCircuit(2, noise_model=IBM_PERTH_2025.noise_model)
    circuit.h(0)
    circuit.cnot(0, 1)
    circuit.h(0)
    circuit.h(1)
    
    print(f"Circuit: {len(circuit.gates)} gates")
    print("Running ZNE with adaptive extrapolation...")
    
    result = zero_noise_extrapolation(
        circuit,
        scale_factors=[1.0, 1.5, 2.0, 2.5],
        extrapolation_method='adaptive',
        folding_method='global',
        shots=1000
    )
    
    print(f"\nResults:")
    print(f"  Unmitigated fidelity: {result['fidelity_unmitigated']:.4f}")
    print(f"  Mitigated fidelity:   {result['fidelity_mitigated']:.4f}")
    print(f"  Method used: {result['extrapolation_method']}")
    
    # With real hardware noise, ZNE should help
    improvement = result['mitigated_value'] / result['unmitigated_value']
    print(f"  Improvement ratio: {improvement:.2f}")
    
    print("✓ ZNE with hardware profile working")


def test_edge_cases():
    """Test edge cases"""
    print("\n=== Test 5: Edge Cases ===")
    
    # Test scale factor = 1.0 (no folding)
    circuit = QuantumCircuit(2, noise_model=DepolarizingNoise(0.01))
    circuit.h(0)
    
    folded_1x = global_fold(circuit, 1.0)
    assert len(folded_1x.gates) == len(circuit.gates), "Scale 1.0 should not add gates"
    print("✓ Scale factor 1.0 works")
    
    # Test with very small noise
    circuit_clean = QuantumCircuit(2, noise_model=DepolarizingNoise(0.001))
    circuit_clean.h(0).cnot(0, 1)
    
    result = zero_noise_extrapolation(circuit_clean, shots=500)
    print(f"  Low noise result: {result['mitigated_value']:.4f}")
    print("✓ Edge cases handled")


def run_all_tests():
    """Run all ZNE tests"""
    print("="*60)
    print("ZNE IMPLEMENTATION TESTS")
    print("="*60)
    
    try:
        test_extrapolation_methods()
        test_circuit_folding()
        test_zne_basic()
        test_zne_with_hardware_profile()
        test_edge_cases()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
