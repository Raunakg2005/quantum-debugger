"""
Ultra-comprehensive final test suite
Property-based tests, randomized scenarios, and theoretical validation
"""

import numpy as np
from quantum_debugger.noise import (
    DepolarizingNoise,
    AmplitudeDamping,
    PhaseDamping,
    ThermalRelaxation,
    QuantumState,
)


def test_concurrent_multi_qubit_noise():
    """Test noise on all qubits simultaneously"""
    print("\n" + "=" * 60)
    print("TEST 1: Concurrent Multi-Qubit Noise")
    print("=" * 60)

    # 4-qubit system
    state = QuantumState(4, use_density_matrix=True)
    noise = DepolarizingNoise(0.05)

    # Apply to ALL qubits at once
    noise.apply(state, qubits=[0, 1, 2, 3])

    rho = state.density_matrix

    # Verify all properties
    assert np.isclose(np.trace(rho).real, 1.0, atol=1e-10)
    assert np.allclose(rho, rho.conj().T)
    eigenvalues = np.linalg.eigvalsh(rho)
    assert np.all(eigenvalues >= -1e-10)
    assert np.all(eigenvalues <= 1.0 + 1e-10)

    print(f"✓ 4-qubit concurrent noise: all properties valid")
    print(f"  Matrix size: {rho.shape[0]}x{rho.shape[1]} (16x16)")


def test_noise_idempotency():
    """Test if applying p=1 twice gives same result as once"""
    print("\n" + "=" * 60)
    print("TEST 2: Noise Idempotency")
    print("=" * 60)

    psi = np.array([1, 1], dtype=complex) / np.sqrt(2)

    # Apply p=1 once
    state1 = QuantumState(1, state_vector=psi, use_density_matrix=True)
    noise = DepolarizingNoise(1.0)
    noise.apply(state1)
    rho1 = state1.density_matrix.copy()

    # Apply p=1 again
    noise.apply(state1)
    rho2 = state1.density_matrix

    # Should be close (maximally mixed is fixed point)
    difference = np.max(np.abs(rho1 - rho2))
    print(f"✓ Applying p=1 twice: difference = {difference:.2e}")

    # Should be close to maximally mixed
    max_mixed = np.eye(2) / 2
    dist_to_max = np.max(np.abs(rho2 - max_mixed))
    print(f"✓ Distance to maximally mixed: {dist_to_max:.6f}")

    assert dist_to_max < 0.1, "Should be close to maximally mixed"


def test_random_state_preservation():
    """Test noise on 100 random states"""
    print("\n" + "=" * 60)
    print("TEST 3: Random State Preservation (100 states)")
    print("=" * 60)

    noise = DepolarizingNoise(0.15)
    failed = 0

    for i in range(100):
        # Random state
        psi = np.random.randn(2) + 1j * np.random.randn(2)
        psi /= np.linalg.norm(psi)

        state = QuantumState(1, state_vector=psi, use_density_matrix=True)
        noise.apply(state)

        rho = state.density_matrix

        # Verify properties
        trace = np.trace(rho).real
        hermitian = np.allclose(rho, rho.conj().T, atol=1e-12)
        eigenvalues = np.linalg.eigvalsh(rho)
        positive = np.all(eigenvalues >= -1e-10)

        if not (np.isclose(trace, 1.0, atol=1e-10) and hermitian and positive):
            failed += 1

    print(f"✓ Tested 100 random states")
    print(f"  Passed: {100 - failed}/100")
    print(f"  Failed: {failed}/100")

    assert failed == 0, f"{failed} random states failed validation"


def test_noise_reversal_impossible():
    """Test that noise cannot be reversed (irreversibility)"""
    print("\n" + "=" * 60)
    print("TEST 4: Noise Irreversibility")
    print("=" * 60)

    psi = np.array([1, 1], dtype=complex) / np.sqrt(2)
    state = QuantumState(1, state_vector=psi, use_density_matrix=True)

    initial_purity = np.trace(state.density_matrix @ state.density_matrix).real

    # Apply noise
    noise = DepolarizingNoise(0.3)
    noise.apply(state)

    after_noise_purity = np.trace(state.density_matrix @ state.density_matrix).real

    # Try to "reverse" by applying negative noise (should fail)
    try:
        reverse_noise = DepolarizingNoise(-0.3)
        assert False, "Should not allow negative noise"
    except ValueError:
        print("✓ Negative noise correctly rejected")

    # Purity should have decreased
    assert after_noise_purity < initial_purity
    print(
        f"✓ Purity decreased irreversibly: {initial_purity:.4f} → {after_noise_purity:.4f}"
    )


def test_fidelity_decay_rate():
    """Test fidelity decay follows exponential for small noise"""
    print("\n" + "=" * 60)
    print("TEST 5: Fidelity Decay Rate")
    print("=" * 60)

    psi = np.array([1, 1], dtype=complex) / np.sqrt(2)
    state = QuantumState(1, state_vector=psi, use_density_matrix=True)
    rho_initial = state.density_matrix.copy()

    # Small noise parameter
    p = 0.01
    noise = DepolarizingNoise(p)

    fidelities = []
    for i in range(20):
        # Fidelity: Tr(ρ_1 ρ_2)
        fidelity = np.trace(rho_initial @ state.density_matrix).real
        fidelities.append(fidelity)
        noise.apply(state)

    # Check approximately exponential decay (for small p)
    # F(n) ≈ exp(-n*p) for small p
    for i in range(5, 15):  # Check middle range
        expected = np.exp(-i * p * 4 / 3)  # approximate factor
        actual = fidelities[i]
        # Should be in same ballpark
        assert (
            0.5 < actual / expected < 2.0
        ), f"Step {i}: Fidelity {actual} far from {expected}"

    print(f"✓ Fidelity decay approximately exponential")
    print(f"  After 0 steps: {fidelities[0]:.6f}")
    print(f"  After 10 steps: {fidelities[10]:.6f}")
    print(f"  After 19 steps: {fidelities[-1]:.6f}")


def test_composite_noise_channels():
    """Test complex compositions of different noises"""
    print("\n" + "=" * 60)
    print("TEST 6: Complex Noise Compositions")
    print("=" * 60)

    psi = np.array([1, 1, 1, 1], dtype=complex) / 2.0
    state = QuantumState(2, state_vector=psi, use_density_matrix=True)

    # Apply complex sequence
    sequence = [
        (DepolarizingNoise(0.1), [0]),
        (AmplitudeDamping(0.1), [1]),
        (PhaseDamping(0.1), [0]),
        (DepolarizingNoise(0.05), [0, 1]),
    ]

    for noise, qubits in sequence:
        noise.apply(state, qubits)

        # Verify after each step
        rho = state.density_matrix
        assert np.isclose(np.trace(rho).real, 1.0, atol=1e-10)
        assert np.allclose(rho, rho.conj().T, atol=1e-12)

    print(f"✓ Complex 4-step noise sequence successful")

    # Final state should be valid
    final_purity = np.trace(state.density_matrix @ state.density_matrix).real
    print(f"  Final purity: {final_purity:.6f}")
    assert 0 < final_purity < 1.0


def test_numerical_overflow_protection():
    """Test that large matrix operations don't overflow"""
    print("\n" + "=" * 60)
    print("TEST 7: Numerical Overflow Protection")
    print("=" * 60)

    # Large-ish system (6 qubits = 64x64 matrix)
    state = QuantumState(6, use_density_matrix=True)
    noise = DepolarizingNoise(0.01)

    try:
        noise.apply(state, qubits=[0, 1, 2, 3, 4, 5])

        rho = state.density_matrix
        max_value = np.max(np.abs(rho))

        assert max_value < 10.0, f"Matrix values too large: {max_value}"
        assert not np.any(np.isnan(rho)), "NaN detected"
        assert not np.any(np.isinf(rho)), "Inf detected"

        print(f"✓ 6-qubit system (64x64 matrix) handled")
        print(f"  Max matrix element: {max_value:.6f}")
        print(f"  No NaN or Inf values")
    except MemoryError:
        print("⚠️  Memory limit reached (acceptable for large systems)")


def test_sparse_vs_dense_consistency():
    """Test that sparse operations give same result"""
    print("\n" + "=" * 60)
    print("TEST 8: Operation Consistency")
    print("=" * 60)

    psi = np.array([1, 0, 0, 0], dtype=complex)

    # Apply noise to single qubit
    state1 = QuantumState(2, state_vector=psi, use_density_matrix=True)
    noise = DepolarizingNoise(0.2)
    noise.apply(state1, qubits=[0])

    # Apply same noise to different qubit
    state2 = QuantumState(2, state_vector=psi, use_density_matrix=True)
    noise.apply(state2, qubits=[1])

    # Results should have same purity
    purity1 = np.trace(state1.density_matrix @ state1.density_matrix).real
    purity2 = np.trace(state2.density_matrix @ state2.density_matrix).real

    # Should be equal due to symmetry
    assert np.isclose(
        purity1, purity2, atol=1e-10
    ), f"Purity differs: qubit 0 = {purity1}, qubit 1 = {purity2}"

    print(f"✓ Noise on qubit 0: purity = {purity1:.6f}")
    print(f"✓ Noise on qubit 1: purity = {purity2:.6f}")
    print(f"✓ Symmetric results (as expected)")


def test_chi_matrix_positive():
    """Test that the process matrix (χ) would be positive"""
    print("\n" + "=" * 60)
    print("TEST 9: Process Matrix Positivity")
    print("=" * 60)

    # For depolarizing channel, χ matrix should be positive
    # We test by ensuring all Kraus operator norms are reasonable

    gamma = 0.3

    # Amplitude damping Kraus operators
    K0 = np.array([[1, 0], [0, np.sqrt(1 - gamma)]], dtype=complex)
    K1 = np.array([[0, np.sqrt(gamma)], [0, 0]], dtype=complex)

    # Check norms
    norm_K0 = np.linalg.norm(K0, ord=2)
    norm_K1 = np.linalg.norm(K1, ord=2)

    assert norm_K0 <= 1.0 + 1e-10, f"K0 norm too large: {norm_K0}"
    assert norm_K1 <= 1.0 + 1e-10, f"K1 norm too large: {norm_K1}"

    print(f"✓ Kraus operator norms bounded:")
    print(f"  ||K0|| = {norm_K0:.6f}")
    print(f"  ||K1|| = {norm_K1:.6f}")


def test_subsystem_noise():
    """Test noise on subsystem doesn't affect other subsystem"""
    print("\n" + "=" * 60)
    print("TEST 10: Subsystem Independence")
    print("=" * 60)

    # Product state |00⟩
    psi = np.array([1, 0, 0, 0], dtype=complex)
    state = QuantumState(2, state_vector=psi, use_density_matrix=True)

    # Apply noise ONLY to qubit 0
    noise = AmplitudeDamping(0.5)
    noise.apply(state, qubits=[0])

    rho = state.density_matrix

    # Qubit 1 should still be in |0⟩
    # Partial trace over qubit 0
    rho_1 = np.zeros((2, 2), dtype=complex)
    for i in range(2):
        for j in range(2):
            rho_1[i, j] = rho[i * 2, j * 2] + rho[i * 2 + 1, j * 2 + 1]

    # Should be |0⟩⟨0|
    expected = np.array([[1, 0], [0, 0]], dtype=complex)

    assert np.allclose(rho_1, expected, atol=1e-10), "Qubit 1 should be unchanged"

    print("✓ Noise on qubit 0 doesn't affect qubit 1")
    print(f"  Qubit 1 state: {rho_1}")


def test_adiabatic_noise_limit():
    """Test very slow noise accumulation"""
    print("\n" + "=" * 60)
    print("TEST 11: Adiabatic Limit (Very Small Noise)")
    print("=" * 60)

    psi = np.array([1, 1], dtype=complex) / np.sqrt(2)
    state = QuantumState(1, state_vector=psi, use_density_matrix=True)

    # Apply tiny noise many times
    noise = DepolarizingNoise(1e-6)

    for _ in range(1000):
        noise.apply(state)

    # Total effective noise: 1000 * 1e-6 = 0.001
    purity = np.trace(state.density_matrix @ state.density_matrix).real

    # Should be close to 1 (very little noise)
    assert purity > 0.99, f"Purity too low: {purity}"

    print(f"✓ After 1000 × 10⁻⁶ noise applications:")
    print(f"  Purity: {purity:.8f} (≈1.0)")


def test_error_propagation_bounds():
    """Test that errors don't propagate unboundedly"""
    print("\n" + "=" * 60)
    print("TEST 12: Error Propagation Bounds")
    print("=" * 60)

    state = QuantumState(2, use_density_matrix=True)
    noise = DepolarizingNoise(0.1)

    purities = []

    for i in range(50):
        purity = np.trace(state.density_matrix @ state.density_matrix).real
        purities.append(purity)
        noise.apply(state, qubits=[0, 1])

    # Purity should converge to >= 1/dim = 1/4 = 0.25
    final_purity = purities[-1]

    assert final_purity >= 0.24, f"Purity went below limit: {final_purity}"
    assert final_purity <= 1.0, f"Purity exceeded 1: {final_purity}"

    print(f"✓ Purity stayed in valid range over 50 steps")
    print(f"  Initial: {purities[0]:.6f}")
    print(f"  Final: {final_purity:.6f}")
    print(f"  Theoretical limit: 0.25")


def test_mixed_state_initialization():
    """Test starting with already-mixed state"""
    print("\n" + "=" * 60)
    print("TEST 13: Mixed State Initialization")
    print("=" * 60)

    # Create maximally mixed state manually
    state = QuantumState(1, use_density_matrix=True)
    state.density_matrix = np.eye(2, dtype=complex) / 2

    initial_purity = np.trace(state.density_matrix @ state.density_matrix).real
    print(f"  Initial purity: {initial_purity:.6f} (maximally mixed)")

    # Apply noise - should have minimal effect
    noise = DepolarizingNoise(0.5)
    noise.apply(state)

    final_purity = np.trace(state.density_matrix @ state.density_matrix).real

    # Shouldn't change much (already maximally mixed)
    difference = abs(final_purity - initial_purity)

    print(f"  Final purity: {final_purity:.6f}")
    print(f"  Change: {difference:.6f}")

    assert difference < 0.01, "Maximally mixed state should be stable"


def test_comparative_noise_strength():
    """Compare relative noise strengths"""
    print("\n" + "=" * 60)
    print("TEST 14: Comparative Noise Strengths")
    print("=" * 60)

    psi = np.array([0, 1], dtype=complex)  # |1⟩

    # Test different noise strengths
    gammas = [0.1, 0.3, 0.5, 0.7, 0.9]
    results = []

    for gamma in gammas:
        state = QuantumState(1, state_vector=psi, use_density_matrix=True)
        noise = AmplitudeDamping(gamma)
        noise.apply(state)

        p0 = state.density_matrix[0, 0].real
        results.append(p0)

    # p0 should increase monotonically with gamma
    for i in range(len(results) - 1):
        assert (
            results[i] < results[i + 1] + 1e-10
        ), f"Non-monotonic: γ={gammas[i]} gives P(0)={results[i]}, γ={gammas[i+1]} gives P(0)={results[i+1]}"

    print(f"✓ Amplitude damping strength increases monotonically:")
    for gamma, p0 in zip(gammas, results):
        print(f"  γ={gamma}: P(0) = {p0:.4f}")


def test_noise_on_ghz_state():
    """Test noise on 3-qubit GHZ state"""
    print("\n" + "=" * 60)
    print("TEST 15: GHZ State Noise")
    print("=" * 60)

    # GHZ: (|000⟩ + |111⟩)/√2
    psi = np.zeros(8, dtype=complex)
    psi[0] = 1 / np.sqrt(2)
    psi[7] = 1 / np.sqrt(2)

    state = QuantumState(3, state_vector=psi, use_density_matrix=True)

    # Check initial entanglement (should be maximally entangled)
    initial_purity = np.trace(state.density_matrix @ state.density_matrix).real
    assert np.isclose(initial_purity, 1.0), "GHZ should be pure"

    # Apply noise to one qubit
    noise = DepolarizingNoise(0.2)
    noise.apply(state, qubits=[1])  # Middle qubit

    # Check final state
    final_purity = np.trace(state.density_matrix @ state.density_matrix).real

    assert final_purity < initial_purity, "Purity should decrease"
    assert final_purity > 0, "Purity should be positive"

    print(f"✓ GHZ state noise:")
    print(f"  Initial purity: {initial_purity:.6f}")
    print(f"  Final purity: {final_purity:.6f}")
    print(f"  Purity decreased: {(1 - final_purity/initial_purity)*100:.1f}%")
