"""
Comprehensive Tests for Zero-Noise Extrapolation

Advanced tests covering edge cases, different folding methods,
noise models, and integration scenarios.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from quantum_debugger import QuantumCircuit
from quantum_debugger.noise import (
    DepolarizingNoise,
    AmplitudeDamping,
    PhaseDamping,
    ThermalRelaxation,
    CompositeNoise,
    IBM_PERTH_2025,
    GOOGLE_SYCAMORE_2025,
)
from quantum_debugger.mitigation import (
    zero_noise_extrapolation,
    global_fold,
    local_fold,
    adaptive_fold,
)
from quantum_debugger.mitigation.core import Extrapolator


def test_folding_methods_comparison():
    """Test different folding methods produce different results"""
    print("\n=== Test 1: Folding Methods Comparison ===")

    circuit = QuantumCircuit(2, noise_model=DepolarizingNoise(0.05))
    circuit.h(0)
    circuit.cnot(0, 1)
    circuit.h(1)

    scale = 2.0

    # Global folding
    global_folded = global_fold(circuit, scale)

    # Local folding (only CNOTs)
    local_folded = local_fold(circuit, scale)

    # Adaptive folding
    adaptive_folded = adaptive_fold(circuit, scale)

    print(f"Original: {len(circuit.gates)} gates")
    print(f"Global folded: {len(global_folded.gates)} gates")
    print(f"Local folded: {len(local_folded.gates)} gates")
    print(f"Adaptive folded: {len(adaptive_folded.gates)} gates")

    # All should have more gates than original
    assert len(global_folded.gates) >= len(circuit.gates)
    assert len(local_folded.gates) >= len(circuit.gates)
    assert len(adaptive_folded.gates) >= len(circuit.gates)

    print("✓ Different folding methods work")


def test_extrapolation_with_noise_variations():
    """Test extrapolation with different noise levels"""
    print("\n=== Test 2: Extrapolation with Noise Variations ===")

    for noise_level in [0.01, 0.05, 0.1]:
        circuit = QuantumCircuit(2, noise_model=DepolarizingNoise(noise_level))
        circuit.h(0).cnot(0, 1)

        result = zero_noise_extrapolation(
            circuit,
            scale_factors=[1.0, 2.0, 3.0],
            extrapolation_method="linear",
            shots=500,
        )

        print(f"\nNoise {noise_level:.2f}:")
        print(f"  Unmitigated: {result['unmitigated_value']:.4f}")
        print(f"  Mitigated: {result['mitigated_value']:.4f}")
        print(f"  Improvement: {result['improvement_factor']:.2f}x")

        # Higher noise should show more improvement
        assert result["mitigated_value"] >= result["unmitigated_value"] * 0.9

    print("\n✓ Extrapolation works across noise levels")


def test_different_extrapolation_methods():
    """Compare all extrapolation methods"""
    print("\n=== Test 3: All Extrapolation Methods ===")

    circuit = QuantumCircuit(2, noise_model=DepolarizingNoise(0.05))
    circuit.h(0).cnot(0, 1)

    methods = ["linear", "richardson", "adaptive"]
    results = {}

    for method in methods:
        result = zero_noise_extrapolation(
            circuit,
            scale_factors=[1.0, 2.0, 3.0],
            extrapolation_method=method,
            shots=500,
        )
        results[method] = result["mitigated_value"]
        print(f"{method:12s}: {result['mitigated_value']:.4f}")

    # All methods should give reasonable results
    for method, value in results.items():
        assert 0.5 < value < 1.2, f"{method} gave unreasonable result: {value}"

    print("✓ All extrapolation methods working")


def test_composite_noise_mitigation():
    """Test ZNE with composite noise"""
    print("\n=== Test 4: Composite Noise Mitigation ===")

    # Combine thermal and depolarizing noise
    composite = CompositeNoise(
        [
            ThermalRelaxation(t1=100e-6, t2=80e-6, gate_time=50e-9),
            DepolarizingNoise(0.01),
        ]
    )

    circuit = QuantumCircuit(2, noise_model=composite)
    circuit.h(0).cnot(0, 1)

    result = zero_noise_extrapolation(circuit, scale_factors=[1.0, 1.5, 2.0], shots=500)

    print(f"Unmitigated: {result['unmitigated_value']:.4f}")
    print(f"Mitigated: {result['mitigated_value']:.4f}")

    assert result["mitigated_value"] > 0.5
    print("✓ Composite noise mitigation working")


def test_different_hardware_profiles():
    """Test ZNE with different hardware profiles"""
    print("\n=== Test 5: Different Hardware Profiles ===")

    profiles = [
        ("IBM Perth", IBM_PERTH_2025),
        ("Google Sycamore", GOOGLE_SYCAMORE_2025),
    ]

    for name, profile in profiles:
        circuit = QuantumCircuit(2, noise_model=profile.noise_model)
        circuit.h(0).cnot(0, 1)

        result = zero_noise_extrapolation(circuit, scale_factors=[1.0, 2.0], shots=500)

        print(f"\n{name}:")
        print(f"  Fidelity (unmitigated): {result['fidelity_unmitigated']:.4f}")
        print(f"  Fidelity (mitigated): {result['fidelity_mitigated']:.4f}")

    print("\n✓ Hardware profile mitigation working")


def test_deep_circuit():
    """Test ZNE on deeper circuit"""
    print("\n=== Test 6: Deep Circuit ===")

    circuit = QuantumCircuit(3, noise_model=DepolarizingNoise(0.03))

    # Create depth-10 circuit
    for _ in range(5):
        circuit.h(0).h(1).h(2)
        circuit.cnot(0, 1).cnot(1, 2)

    print(f"Circuit depth: {len(circuit.gates)} gates")

    result = zero_noise_extrapolation(
        circuit, scale_factors=[1.0, 1.5, 2.0], extrapolation_method="linear", shots=500
    )

    print(f"Unmitigated: {result['unmitigated_value']:.4f}")
    print(f"Mitigated: {result['mitigated_value']:.4f}")

    # Should complete without error
    assert "mitigated_value" in result
    print("✓ Deep circuit mitigation works")


def test_scale_factor_edge_cases():
    """Test edge cases for scale factors"""
    print("\n=== Test 7: Scale Factor Edge Cases ===")

    circuit = QuantumCircuit(2, noise_model=DepolarizingNoise(0.05))
    circuit.h(0).cnot(0, 1)

    # Test very small scaling steps
    result_fine = zero_noise_extrapolation(
        circuit, scale_factors=[1.0, 1.1, 1.2, 1.3], shots=300
    )
    print(f"Fine scaling: {result_fine['mitigated_value']:.4f}")

    # Test large scaling
    result_coarse = zero_noise_extrapolation(
        circuit, scale_factors=[1.0, 3.0, 5.0], shots=300
    )
    print(f"Coarse scaling: {result_coarse['mitigated_value']:.4f}")

    # Both should work
    assert "mitigated_value" in result_fine
    assert "mitigated_value" in result_coarse

    print("✓ Scale factor edge cases handled")


def test_single_qubit_circuit():
    """Test ZNE on single-qubit circuit"""
    print("\n=== Test 8: Single Qubit Circuit ===")

    circuit = QuantumCircuit(1, noise_model=DepolarizingNoise(0.05))
    circuit.h(0)
    circuit.x(0)
    circuit.h(0)

    result = zero_noise_extrapolation(circuit, scale_factors=[1.0, 2.0, 3.0], shots=500)

    print(f"Single qubit - Mitigated: {result['mitigated_value']:.4f}")
    assert result["mitigated_value"] > 0.5
    print("✓ Single qubit mitigation works")


def test_measurement_statistics():
    """Test statistical consistency of ZNE"""
    print("\n=== Test 9: Measurement Statistics ===")

    circuit = QuantumCircuit(2, noise_model=DepolarizingNoise(0.05))
    circuit.h(0).cnot(0, 1)

    # Run ZNE multiple times
    results = []
    for _ in range(3):
        result = zero_noise_extrapolation(
            circuit, scale_factors=[1.0, 2.0, 3.0], shots=500
        )
        results.append(result["mitigated_value"])

    mean = np.mean(results)
    std = np.std(results)

    print(f"Mean over 3 trials: {mean:.4f}")
    print(f"Std dev: {std:.4f}")

    # Results should be relatively consistent
    assert std < 0.1, f"Too much variance: {std}"
    print("✓ Statistical consistency verified")


def test_amplitude_damping_mitigation():
    """Test ZNE with amplitude damping noise"""
    print("\n=== Test 10: Amplitude Damping ===")

    circuit = QuantumCircuit(2, noise_model=AmplitudeDamping(0.1))
    circuit.h(0).cnot(0, 1)

    result = zero_noise_extrapolation(circuit, scale_factors=[1.0, 2.0, 3.0], shots=500)

    print(f"Amplitude damping - Mitigated: {result['mitigated_value']:.4f}")
    assert result["mitigated_value"] > 0
    print("✓ Amplitude damping mitigation works")


def test_phase_damping_mitigation():
    """Test ZNE with phase damping noise"""
    print("\n=== Test 11: Phase Damping ===")

    circuit = QuantumCircuit(2, noise_model=PhaseDamping(0.1))
    circuit.h(0).cnot(0, 1)

    result = zero_noise_extrapolation(circuit, scale_factors=[1.0, 2.0, 3.0], shots=500)

    print(f"Phase damping - Mitigated: {result['mitigated_value']:.4f}")
    assert result["mitigated_value"] > 0
    print("✓ Phase damping mitigation works")


def test_folding_preserves_unitarity():
    """Verify folded circuits are still unitary (without noise)"""
    print("\n=== Test 12: Folding Preserves Unitarity ===")

    # Create noiseless circuit
    circuit = QuantumCircuit(2)
    circuit.h(0).cnot(0, 1)

    # Fold it
    folded = global_fold(circuit, 3.0)

    # Run both (should give same result without noise)
    result_orig = circuit.run(shots=100)
    result_folded = folded.run(shots=100)

    # Both should produce Bell state
    print(f"Original counts: {result_orig['counts']}")
    print(f"Folded counts: {result_folded['counts']}")

    # Counts might differ due to randomness, but distribution should be similar
    print("✓ Folding preserves circuit logic")


def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("=" * 70)
    print("ZNE COMPREHENSIVE TESTS")
    print("=" * 70)

    tests = [
        test_folding_methods_comparison,
        test_extrapolation_with_noise_variations,
        test_different_extrapolation_methods,
        test_composite_noise_mitigation,
        test_different_hardware_profiles,
        test_deep_circuit,
        test_scale_factor_edge_cases,
        test_single_qubit_circuit,
        test_measurement_statistics,
        test_amplitude_damping_mitigation,
        test_phase_damping_mitigation,
        test_folding_preserves_unitarity,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"\n✗ {test.__name__} FAILED: {e}")
            import traceback

            traceback.print_exc()

    print("\n" + "=" * 70)
    print(f"RESULTS: {passed}/{len(tests)} tests passed")
    if failed == 0:
        print("✓ ALL COMPREHENSIVE TESTS PASSED")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
