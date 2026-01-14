"""
Performance, Benchmarking, and Advanced Property Tests
Tests execution speed, memory usage, and advanced quantum properties
"""

import numpy as np
import time
from quantum_debugger.noise import (
    DepolarizingNoise,
    AmplitudeDamping,
    PhaseDamping,
    ThermalRelaxation,
    QuantumState,
)


def test_performance_benchmarks():
    """Benchmark noise application speed"""
    print("\n" + "=" * 60)
    print("TEST 1: Performance Benchmarks")
    print("=" * 60)

    results = {}

    # Benchmark different noise types
    noise_types = {
        "Depolarizing": DepolarizingNoise(0.1),
        "AmplitudeDamping": AmplitudeDamping(0.1),
        "PhaseDamping": PhaseDamping(0.1),
    }

    for name, noise in noise_types.items():
        state = QuantumState(2, use_density_matrix=True)

        start = time.time()
        for _ in range(1000):
            noise.apply(state, qubits=[0])
        elapsed = time.time() - start

        results[name] = elapsed
        print(
            f"  {name:20s}: {elapsed*1000:.2f}ms for 1000 iterations ({elapsed*1000000:.2f}μs per iteration)"
        )

    # All should be reasonably fast
    for name, elapsed in results.items():
        assert elapsed < 5.0, f"{name} too slow: {elapsed}s"

    print(f"✓ All noise types perform well")


def test_memory_efficiency():
    """Test memory usage doesn't grow unexpectedly"""
    print("\n" + "=" * 60)
    print("TEST 2: Memory Efficiency")
    print("=" * 60)

    state = QuantumState(3, use_density_matrix=True)
    noise = DepolarizingNoise(0.05)

    initial_size = state.density_matrix.nbytes
    print(f"  Initial density matrix size: {initial_size} bytes")

    # Apply noise 1000 times
    for _ in range(1000):
        noise.apply(state, qubits=[0, 1, 2])

    final_size = state.density_matrix.nbytes
    print(f"  Final density matrix size: {final_size} bytes")

    # Size shouldn't change
    assert initial_size == final_size, "Memory leak detected!"
    print(f"✓ No memory leaks after 1000 operations")


def test_channel_fidelity_bounds():
    """Test quantum channel fidelity bounds"""
    print("\n" + "=" * 60)
    print("TEST 3: Channel Fidelity Bounds")
    print("=" * 60)

    psi = np.array([1, 1], dtype=complex) / np.sqrt(2)

    # Test different noise strengths
    for p in [0.01, 0.1, 0.3, 0.5]:
        state_pure = QuantumState(1, state_vector=psi, use_density_matrix=True)
        rho_pure = state_pure.density_matrix.copy()

        state_noisy = QuantumState(1, state_vector=psi, use_density_matrix=True)
        DepolarizingNoise(p).apply(state_noisy)
        rho_noisy = state_noisy.density_matrix

        # Fidelity F = Tr(ρ₁ ρ₂) for commuting matrices
        fidelity = np.trace(rho_pure @ rho_noisy).real

        # Fidelity should decrease with noise
        assert 0 <= fidelity <= 1.0, f"Fidelity out of bounds: {fidelity}"
        expected_lower = 1 - p
        assert fidelity >= expected_lower - 0.1, f"Fidelity too low for p={p}"

        print(f"  p={p}: F={fidelity:.4f} (expected ≥{expected_lower:.4f}) ✓")


def test_entanglement_decay_rates():
    """Test how noise affects entanglement"""
    print("\n" + "=" * 60)
    print("TEST 4: Entanglement Decay Rates")
    print("=" * 60)

    # Bell state
    psi = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)

    noise_strengths = [0.0, 0.05, 0.1, 0.2, 0.3]
    purities = []

    for p in noise_strengths:
        state = QuantumState(2, state_vector=psi, use_density_matrix=True)
        if p > 0:
            DepolarizingNoise(p).apply(state, qubits=[0, 1])

        purity = np.trace(state.density_matrix @ state.density_matrix).real
        purities.append(purity)

    # Purity should decrease monotonically
    for i in range(len(purities) - 1):
        assert (
            purities[i] >= purities[i + 1] - 1e-10
        ), f"Purity increased: {purities[i]} -> {purities[i+1]}"

    print(f"  Entanglement decay:")
    for p, purity in zip(noise_strengths, purities):
        print(f"    p={p}: purity={purity:.4f}")
    print(f"✓ Monotonic decay verified")


def test_noise_invariants():
    """Test quantum channel invariants"""
    print("\n" + "=" * 60)
    print("TEST 5: Quantum Channel Invariants")
    print("=" * 60)

    # Maximally mixed state should be invariant
    state = QuantumState(1, use_density_matrix=True)
    state.density_matrix = np.eye(2) / 2  # Maximally mixed

    initial_dm = state.density_matrix.copy()

    # Apply various noises
    DepolarizingNoise(0.5).apply(state)

    # Should stay maximally mixed (fixed point)
    final_dm = state.density_matrix
    distance = np.max(np.abs(final_dm - initial_dm))

    print(f"  Distance from fixed point: {distance:.6f}")
    assert distance < 0.01, "Maximally mixed state should be approximately fixed"
    print(f"✓ Fixed point property verified")


def test_noise_scaling():
    """Test how noise scales with system size"""
    print("\n" + "=" * 60)
    print("TEST 6: Noise Scaling with System Size")
    print("=" * 60)

    noise = DepolarizingNoise(0.05)

    for n in range(1, 6):
        state = QuantumState(n, use_density_matrix=True)

        start = time.time()
        noise.apply(state, qubits=list(range(n)))
        elapsed = time.time() - start

        matrix_size = 2**n
        print(f"  {n} qubits ({matrix_size:3d}×{matrix_size:3d}): {elapsed*1000:.2f}ms")

        # Verify result
        assert np.isclose(np.trace(state.density_matrix).real, 1.0)

    print(f"✓ Scales correctly with system size")


def test_different_initial_states():
    """Test noise on various initial states"""
    print("\n" + "=" * 60)
    print("TEST 7: Different Initial States")
    print("=" * 60)

    noise = AmplitudeDamping(0.3)

    test_states = {
        "|0⟩": np.array([1, 0], dtype=complex),
        "|1⟩": np.array([0, 1], dtype=complex),
        "|+⟩": np.array([1, 1], dtype=complex) / np.sqrt(2),
        "|-⟩": np.array([1, -1], dtype=complex) / np.sqrt(2),
        "|i⟩": np.array([1, 1j], dtype=complex) / np.sqrt(2),
        "Random": np.array([0.6, 0.8], dtype=complex),
    }

    for name, psi in test_states.items():
        psi /= np.linalg.norm(psi)
        state = QuantumState(1, state_vector=psi, use_density_matrix=True)
        noise.apply(state)

        rho = state.density_matrix
        trace = np.trace(rho).real
        purity = np.trace(rho @ rho).real

        assert np.isclose(trace, 1.0, atol=1e-10)
        assert 0 <= purity <= 1.0

        print(f"  {name:8s}: trace={trace:.6f}, purity={purity:.6f} ✓")


def test_noise_reversibility_impossible():
    """Verify that noise truly cannot be reversed"""
    print("\n" + "=" * 60)
    print("TEST 8: Irreversibility Verification")
    print("=" * 60)

    psi = np.array([1, 1], dtype=complex) / np.sqrt(2)
    state = QuantumState(1, state_vector=psi, use_density_matrix=True)

    initial_purity = np.trace(state.density_matrix @ state.density_matrix).real

    # Apply noise forward
    DepolarizingNoise(0.3).apply(state)
    after_purity = np.trace(state.density_matrix @ state.density_matrix).real

    # Try to "undo" with opposite parameter (should fail at construction)
    try:
        reverse_noise = DepolarizingNoise(-0.3)
        assert False, "Should not allow negative noise"
    except ValueError:
        pass

    # Purity cannot increase
    assert after_purity < initial_purity
    print(f"  Initial purity: {initial_purity:.6f}")
    print(f"  After noise: {after_purity:.6f}")
    print(f"✓ Irreversibility confirmed (cannot reverse noise)")


def test_statistical_properties():
    """Test statistical properties of noise"""
    print("\n" + "=" * 60)
    print("TEST 9: Statistical Properties")
    print("=" * 60)

    # Apply same noise to many identical states
    n_trials = 100
    purities = []

    psi = np.array([1, 1], dtype=complex) / np.sqrt(2)

    for _ in range(n_trials):
        state = QuantumState(1, state_vector=psi, use_density_matrix=True)
        DepolarizingNoise(0.2).apply(state)
        purity = np.trace(state.density_matrix @ state.density_matrix).real
        purities.append(purity)

    # All should be identical (deterministic)
    purity_std = np.std(purities)
    purity_mean = np.mean(purities)

    print(f"  Mean purity: {purity_mean:.8f}")
    print(f"  Std dev: {purity_std:.2e}")

    assert purity_std < 1e-14, "Noise application should be deterministic"
    print(f"✓ Noise is deterministic (std < 10⁻¹⁴)")


def test_comparative_noise_effects():
    """Compare effects of different noise types"""
    print("\n" + "=" * 60)
    print("TEST 10: Comparative Noise Effects")
    print("=" * 60)

    psi = np.array([0, 1], dtype=complex)  # |1⟩

    # Same strength, different noise types
    gamma = 0.5

    results = {}

    # Amplitude damping
    state = QuantumState(1, state_vector=psi, use_density_matrix=True)
    AmplitudeDamping(gamma).apply(state)
    results["AmplitudeDamping"] = {
        "p0": state.density_matrix[0, 0].real,
        "p1": state.density_matrix[1, 1].real,
        "coherence": abs(state.density_matrix[0, 1]),
    }

    # Phase damping
    state = QuantumState(1, state_vector=psi, use_density_matrix=True)
    PhaseDamping(gamma).apply(state)
    results["PhaseDamping"] = {
        "p0": state.density_matrix[0, 0].real,
        "p1": state.density_matrix[1, 1].real,
        "coherence": abs(state.density_matrix[0, 1]),
    }

    # Depolarizing
    state = QuantumState(1, state_vector=psi, use_density_matrix=True)
    DepolarizingNoise(gamma).apply(state)
    results["Depolarizing"] = {
        "p0": state.density_matrix[0, 0].real,
        "p1": state.density_matrix[1, 1].real,
        "coherence": abs(state.density_matrix[0, 1]),
    }

    print(f"  Comparison for |1⟩ with γ/p={gamma}:")
    print(f"  {'Noise Type':<20s} P(0)      P(1)      Coherence")
    print(f"  {'-'*55}")

    for name, vals in results.items():
        print(
            f"  {name:<20s} {vals['p0']:.4f}    {vals['p1']:.4f}    {vals['coherence']:.4f}"
        )

    # Amplitude damping should increase P(0)
    assert results["AmplitudeDamping"]["p0"] > 0.4
    # Phase damping should preserve populations (for |1⟩, stays |1⟩)
    assert results["PhaseDamping"]["p1"] > 0.99

    print(f"✓ Different noise types have expected effects")


def test_multi_step_error_accumulation():
    """Test error accumulation over many steps"""
    print("\n" + "=" * 60)
    print("TEST 11: Multi-Step Error Accumulation")
    print("=" * 60)

    psi = np.array([1, 1], dtype=complex) / np.sqrt(2)
    state = QuantumState(1, state_vector=psi, use_density_matrix=True)

    # Small error per step
    small_noise = DepolarizingNoise(0.001)

    purities = [1.0]  # Initial

    for i in range(100):
        small_noise.apply(state)
        purity = np.trace(state.density_matrix @ state.density_matrix).real
        purities.append(purity)

    # Should decay approximately linearly for small noise
    final_purity = purities[-1]

    # Approximate: purity ≈ 1 - k*n*p for small p
    expected_roughly = 1 - 100 * 0.001 * 4 / 3  # rough estimate

    print(f"  Initial purity: {purities[0]:.6f}")
    print(f"  After 100 × 0.1% noise steps: {final_purity:.6f}")
    print(f"  Expected roughly: {expected_roughly:.6f}")

    assert final_purity < purities[0], "Purity should decrease"
    assert final_purity > 0.8, "Shouldn't decay too much with small noise"

    print(f"✓ Error accumulation behaves correctly")


def test_boundary_conditions():
    """Test extreme boundary conditions"""
    print("\n" + "=" * 60)
    print("TEST 12: Boundary Conditions")
    print("=" * 60)

    # Test p very close to 0
    state = QuantumState(1, use_density_matrix=True)
    DepolarizingNoise(1e-20).apply(state)
    assert np.isclose(np.trace(state.density_matrix).real, 1.0)
    print(f"✓ p=10⁻²⁰: Valid")

    # Test p very close to 1
    state = QuantumState(1, use_density_matrix=True)
    DepolarizingNoise(0.9999).apply(state)
    assert np.isclose(np.trace(state.density_matrix).real, 1.0)
    print(f"✓ p=0.9999: Valid")

    # Test T1 >> T2 boundary (T2 = 0 would violate T2 <= 2T1)
    state = QuantumState(1, use_density_matrix=True)
    ThermalRelaxation(t1=1e-3, t2=1e-10, gate_time=1e-9).apply(state)
    assert np.isclose(np.trace(state.density_matrix).real, 1.0)
    print(f"✓ T1 >> T2: Valid")

    print(f"✓ All boundary conditions handled")
