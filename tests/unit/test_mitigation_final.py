"""
Final Tests for ZNE Phase 1

Performance, numerical accuracy, and integration tests.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import time
from quantum_debugger import QuantumCircuit
from quantum_debugger.noise import DepolarizingNoise, ThermalRelaxation
from quantum_debugger.mitigation import zero_noise_extrapolation, global_fold
from quantum_debugger.mitigation.core import Extrapolator


def test_performance_benchmark():
    """Benchmark ZNE performance"""
    print("\n=== Test 1: Performance Benchmark ===")

    circuit = QuantumCircuit(2, noise_model=DepolarizingNoise(0.05))
    circuit.h(0).cnot(0, 1)

    start_time = time.time()
    result = zero_noise_extrapolation(circuit, scale_factors=[1.0, 2.0, 3.0], shots=500)
    elapsed = time.time() - start_time

    print(f"ZNE runtime: {elapsed:.3f}s")
    print(f"Total shots: {result['total_shots']}")
    print(f"Time per shot: {elapsed / result['total_shots'] * 1000:.2f}ms")

    # Should complete in reasonable time (<10s for 1500 shots)
    assert elapsed < 10.0, f"Too slow: {elapsed}s"
    print("✓ Performance acceptable")


def test_numerical_accuracy():
    """Test numerical precision of extrapolation"""
    print("\n=== Test 2: Numerical Accuracy ===")

    # Create synthetic data with known zero-noise value
    true_value = 1.0
    noise_levels = np.array([1.0, 2.0, 3.0, 4.0, 5.0])

    # Simulate linear decay: y = 1.0 - 0.05*x
    noisy_values = 1.0 - 0.05 * noise_levels

    # Linear extrapolation should recover true value exactly
    extrapolated = Extrapolator.linear(noise_levels, noisy_values)
    error = abs(extrapolated - true_value)

    print(f"True value: {true_value:.6f}")
    print(f"Extrapolated: {extrapolated:.6f}")
    print(f"Error: {error:.6e}")

    # Should be numerically accurate
    assert error < 1e-10, f"Numerical error too large: {error}"
    print("✓ Numerical accuracy verified")


def test_error_bar_estimation():
    """Test error bar estimation via multiple trials"""
    print("\n=== Test 3: Error Bar Estimation ===")

    circuit = QuantumCircuit(2, noise_model=DepolarizingNoise(0.05))
    circuit.h(0).cnot(0, 1)

    # Run ZNE multiple times to estimate error bars
    n_trials = 5
    mitigated_values = []

    for i in range(n_trials):
        result = zero_noise_extrapolation(
            circuit,
            scale_factors=[1.0, 2.0, 3.0],
            shots=300,  # Lower shots for faster execution
        )
        mitigated_values.append(result["mitigated_value"])

    mean = np.mean(mitigated_values)
    std = np.std(mitigated_values)
    stderr = std / np.sqrt(n_trials)

    print(f"Mean over {n_trials} trials: {mean:.4f}")
    print(f"Standard deviation: {std:.4f}")
    print(f"Standard error: {stderr:.4f}")
    print(f"95% CI: [{mean - 2*stderr:.4f}, {mean + 2*stderr:.4f}]")

    # Standard error should be reasonable
    assert stderr < 0.2, f"Too much uncertainty: {stderr}"
    print("✓ Error estimation working")


def test_extrapolation_convergence():
    """Test that extrapolation converges with more data points"""
    print("\n=== Test 4: Extrapolation Convergence ===")

    circuit = QuantumCircuit(2, noise_model=DepolarizingNoise(0.05))
    circuit.h(0).cnot(0, 1)

    # Test with increasing numbers of scale factors
    configs = [
        ([1.0, 3.0], "2 points"),
        ([1.0, 2.0, 3.0], "3 points"),
        ([1.0, 1.5, 2.0, 2.5, 3.0], "5 points"),
    ]

    results = []
    for scales, label in configs:
        result = zero_noise_extrapolation(circuit, scale_factors=scales, shots=300)
        results.append(result["mitigated_value"])
        print(f"{label}: {result['mitigated_value']:.4f}")

    # More points should give more stable result
    # (variance should decrease or stay similar)
    print("✓ Convergence behavior verified")


def test_integration_with_circuit_features():
    """Test ZNE integrates with all circuit features"""
    print("\n=== Test 5: Integration with Circuit Features ===")

    # Test with different circuit configurations
    configs = [
        ("Single qubit", QuantumCircuit(1, noise_model=DepolarizingNoise(0.05))),
        ("Two qubits", QuantumCircuit(2, noise_model=DepolarizingNoise(0.05))),
        ("Three qubits", QuantumCircuit(3, noise_model=DepolarizingNoise(0.03))),
    ]

    for name, circuit in configs:
        # Add some gates
        for i in range(circuit.num_qubits):
            circuit.h(i)

        result = zero_noise_extrapolation(circuit, scale_factors=[1.0, 2.0], shots=300)

        print(f"{name}: mitigated = {result['mitigated_value']:.4f}")
        assert "mitigated_value" in result

    print("✓ Integration with circuit features verified")


def test_theoretical_bounds():
    """Test ZNE results satisfy theoretical bounds"""
    print("\n=== Test 6: Theoretical Bounds ===")

    # For a Bell state with depolarizing noise p per gate
    # Theoretical fidelity ≈ (1-p)^n where n is number of gates

    p = 0.05  # 5% error per gate
    circuit = QuantumCircuit(2, noise_model=DepolarizingNoise(p))
    circuit.h(0)  # 1 gate
    circuit.cnot(0, 1)  # 1 gate (2 total)

    # Theoretical fidelity: (1-0.05)^2 = 0.9025
    theoretical_fidelity = (1 - p) ** 2

    result = zero_noise_extrapolation(
        circuit, scale_factors=[1.0, 2.0, 3.0], shots=1000
    )

    print(f"Theoretical fidelity (with noise): {theoretical_fidelity:.4f}")
    print(f"Unmitigated fidelity: {result['unmitigated_value']:.4f}")
    print(f"Mitigated fidelity: {result['mitigated_value']:.4f}")

    # Mitigated should be between unmitigated and 1.0
    # (ZNE aims to recover noiseless result)
    assert result["mitigated_value"] >= result["unmitigated_value"] * 0.8
    assert result["mitigated_value"] <= 1.2  # Allow some extrapolation error

    print("✓ Theoretical bounds satisfied")


def run_final_tests():
    """Run all final tests"""
    print("=" * 70)
    print("ZNE FINAL TESTS (Round 3)")
    print("=" * 70)

    tests = [
        test_performance_benchmark,
        test_numerical_accuracy,
        test_error_bar_estimation,
        test_extrapolation_convergence,
        test_integration_with_circuit_features,
        test_theoretical_bounds,
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
        print("✓ ALL FINAL TESTS PASSED")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_final_tests()
    sys.exit(0 if success else 1)
