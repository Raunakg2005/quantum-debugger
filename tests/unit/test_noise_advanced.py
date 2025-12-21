"""
Advanced stress tests for noise models
Tests edge cases, numerical stability, and complex scenarios
"""

import pytest
import numpy as np
from quantum_debugger.noise import (
    DepolarizingNoise, 
    AmplitudeDamping, 
    PhaseDamping, 
    ThermalRelaxation,
    QuantumState
)


def test_extreme_noise_probabilities():
    """Test edge cases: p=0 (no noise) and p=1 (maximum noise)"""
    # p=0 should do nothing
    state = QuantumState(1, use_density_matrix=True)
    rho_initial = state.density_matrix.copy()
    noise = DepolarizingNoise(probability=0.0)
    noise.apply(state)
    assert np.allclose(state.density_matrix, rho_initial)
    
    # p=1 should maximally depolarize
    state = QuantumState(1, use_density_matrix=True)
    noise = DepolarizingNoise(probability=1.0)
    noise.apply(state)
    purity = np.trace(state.density_matrix @ state.density_matrix).real
    assert purity < 0.6


def test_multi_qubit_noise():
    """Test noise on multi-qubit states"""
    # 3-qubit GHZ state
    state = QuantumState(3, use_density_matrix=True)
    psi = np.zeros(8, dtype=complex)
    psi[0] = 1/np.sqrt(2)  # |000⟩
    psi[7] = 1/np.sqrt(2)  # |111⟩
    state.density_matrix = np.outer(psi, psi.conj())
    
    initial_purity = np.trace(state.density_matrix @ state.density_matrix).real
    
    # Apply noise to all qubits
    noise = DepolarizingNoise(probability=0.05)
    noise.apply(state, qubits=[0, 1, 2])
    
    final_purity = np.trace(state.density_matrix @ state.density_matrix).real
    trace = np.trace(state.density_matrix).real
    
    assert final_purity < initial_purity
    assert np.isclose(trace, 1.0)
    assert np.allclose(state.density_matrix, state.density_matrix.conj().T)


def test_noise_composition():
    """Test applying multiple noise channels in sequence"""
    psi = np.array([1, 1], dtype=complex) / np.sqrt(2)
    state = QuantumState(1, state_vector=psi, use_density_matrix=True)
    
    rho_initial = state.density_matrix.copy()
    
    # Apply T1, then T2 noise
    t1_noise = AmplitudeDamping(gamma=0.2)
    t2_noise = PhaseDamping(gamma=0.2)
    
    t1_noise.apply(state)
    rho_after_t1 = state.density_matrix.copy()
    
    t2_noise.apply(state)
    rho_final = state.density_matrix
    
    # All three stages should be different
    assert not np.allclose(rho_initial, rho_after_t1, atol=1e-10)
    assert not np.allclose(rho_after_t1, rho_final, atol=1e-10)
    
    # Trace should still be 1
    trace = np.trace(rho_final).real
    assert np.isclose(trace, 1.0)


def test_thermal_relaxation_t1_t2_constraint():
    """Test T2 <= 2*T1 constraint"""
    # Valid: T2 = T1
    noise = ThermalRelaxation(t1=100e-6, t2=100e-6, gate_time=1e-6)
    
    # Valid: T2 = 2*T1
    noise = ThermalRelaxation(t1=100e-6, t2=200e-6, gate_time=1e-6)
    
    # Invalid: T2 > 2*T1
    with pytest.raises(ValueError):
        noise = ThermalRelaxation(t1=100e-6, t2=250e-6, gate_time=1e-6)


def test_density_matrix_properties():
    """Test that density matrices maintain physical properties"""
    state = QuantumState(2, use_density_matrix=True)
    
    # Apply various noises
    noises = [
        DepolarizingNoise(0.2),
        AmplitudeDamping(0.3),
        PhaseDamping(0.15)
    ]
    
    for noise in noises:
        noise.apply(state, qubits=[0])
        rho = state.density_matrix
        
        # 1. Hermitian
        assert np.allclose(rho, rho.conj().T)
        
        # 2. Trace = 1
        trace = np.trace(rho).real
        assert np.isclose(trace, 1.0, atol=1e-10)
        
        # 3. Positive semi-definite
        eigenvalues = np.linalg.eigvalsh(rho)
        assert np.all(eigenvalues >= -1e-10)
        
        # 4. Purity <= 1
        purity = np.trace(rho @ rho).real
        assert purity <= 1.0 + 1e-10


def test_numerical_stability():
    """Test numerical stability over many operations"""
    state = QuantumState(2, use_density_matrix=True)
    noise = DepolarizingNoise(probability=0.01)
    
    # Apply noise 100 times
    for i in range(100):
        noise.apply(state, qubits=[0])
    
    rho = state.density_matrix
    
    # Check all properties still hold
    trace = np.trace(rho).real
    hermitian = np.allclose(rho, rho.conj().T)
    eigenvalues = np.linalg.eigvalsh(rho)
    positive = np.all(eigenvalues >= -1e-10)
    purity = np.trace(rho @ rho).real
    
    assert np.isclose(trace, 1.0, atol=1e-8)
    assert hermitian
    assert positive
    assert purity <= 1.0 + 1e-8


def test_amplitude_damping_decay_rate():
    """Test that amplitude damping follows expected decay"""
    psi = np.array([0, 1], dtype=complex)
    
    gammas = [0.0, 0.25, 0.5, 0.75, 1.0]
    
    for gamma in gammas:
        state = QuantumState(1, state_vector=psi, use_density_matrix=True)
        noise = AmplitudeDamping(gamma=gamma)
        noise.apply(state)
        
        p1 = state.density_matrix[1, 1].real
        p0 = state.density_matrix[0, 0].real
        
        # Expected: p1 = (1-γ), p0 = γ
        expected_p1 = 1 - gamma
        expected_p0 = gamma
        
        assert np.isclose(p1, expected_p1, atol=1e-10)
        assert np.isclose(p0, expected_p0, atol=1e-10)


def test_phase_damping_coherence_decay():
    """Test that phase damping decays off-diagonal elements correctly"""
    psi = np.array([1, 1], dtype=complex) / np.sqrt(2)
    
    gammas = [0.0, 0.25, 0.5, 0.75, 1.0]
    
    for gamma in gammas:
        state = QuantumState(1, state_vector=psi, use_density_matrix=True)
        
        initial_coherence = abs(state.density_matrix[0, 1])
        
        noise = PhaseDamping(gamma=gamma)
        noise.apply(state)
        
        final_coherence = abs(state.density_matrix[0, 1])
        
        # Expected: coherence decays by sqrt(1-γ)
        expected_coherence = initial_coherence * np.sqrt(1 - gamma)
        
        assert np.isclose(final_coherence, expected_coherence, atol=1e-10)
        
        # Populations should be preserved
        p0 = state.density_matrix[0, 0].real
        p1 = state.density_matrix[1, 1].real
        assert np.isclose(p0, 0.5, atol=1e-10)
        assert np.isclose(p1, 0.5, atol=1e-10)


def test_zero_noise_is_identity():
    """Test that zero noise doesn't change the state"""
    # Complex multi-qubit state
    state = QuantumState(2, use_density_matrix=True)
    psi = np.array([0.5, 0.5, 0.5, 0.5], dtype=complex)
    state.density_matrix = np.outer(psi, psi.conj())
    rho_initial = state.density_matrix.copy()
    
    # Apply zero noise
    noises = [
        DepolarizingNoise(0.0),
        AmplitudeDamping(0.0),
        PhaseDamping(0.0)
    ]
    
    for noise in noises:
        state.density_matrix = rho_initial.copy()
        noise.apply(state)
        assert np.allclose(state.density_matrix, rho_initial, atol=1e-15)


def test_maximum_noise_limits():
    """Test behavior at maximum noise (p=1, γ=1)"""
    # Amplitude damping with γ=1: |1⟩ → |0⟩ completely
    psi = np.array([0, 1], dtype=complex)
    state = QuantumState(1, state_vector=psi, use_density_matrix=True)
    noise = AmplitudeDamping(gamma=1.0)
    noise.apply(state)
    
    p0 = state.density_matrix[0, 0].real
    p1 = state.density_matrix[1, 1].real
    
    assert np.isclose(p0, 1.0, atol=1e-10)
    assert np.isclose(p1, 0.0, atol=1e-10)
    
    # Phase damping with γ=1: destroys all coherence
    psi = np.array([1, 1], dtype=complex) / np.sqrt(2)
    state = QuantumState(1, state_vector=psi, use_density_matrix=True)
    noise = PhaseDamping(gamma=1.0)
    noise.apply(state)
    
    coherence = abs(state.density_matrix[0, 1])
    assert np.isclose(coherence, 0.0, atol=1e-10)

    
    # p=0 should do nothing
    state = QuantumState(1, use_density_matrix=True)
    rho_initial = state.density_matrix.copy()
    noise = DepolarizingNoise(probability=0.0)
    noise.apply(state)
    assert np.allclose(state.density_matrix, rho_initial), "p=0 should not change state"
    print("✓ p=0: No change (correct)")
    
    # p=1 should maximally depolarize
    state = QuantumState(1, use_density_matrix=True)
    noise = DepolarizingNoise(probability=1.0)
    noise.apply(state)
    # Should approach maximally mixed state
    purity = np.trace(state.density_matrix @ state.density_matrix).real
    print(f"✓ p=1: Purity = {purity:.4f} (highly mixed)")
    assert purity < 0.6, f"p=1 should heavily mix the state, got purity {purity}"


def test_multi_qubit_noise():
    """Test noise on multi-qubit states"""
    print("\n" + "="*60)
    print("TEST 2: Multi-Qubit Noise")
    print("="*60)
    
    # 3-qubit GHZ state
    state = QuantumState(3, use_density_matrix=True)
    psi = np.zeros(8, dtype=complex)
    psi[0] = 1/np.sqrt(2)  # |000⟩
    psi[7] = 1/np.sqrt(2)  # |111⟩
    state.density_matrix = np.outer(psi, psi.conj())
    
    initial_purity = np.trace(state.density_matrix @ state.density_matrix).real
    
    # Apply noise to all qubits
    noise = DepolarizingNoise(probability=0.05)
    noise.apply(state, qubits=[0, 1, 2])
    
    final_purity = np.trace(state.density_matrix @ state.density_matrix).real
    trace = np.trace(state.density_matrix).real
    
    assert final_purity < initial_purity, "Purity should decrease"
    assert np.isclose(trace, 1.0), f"Trace should be 1, got {trace}"
    assert np.allclose(state.density_matrix, state.density_matrix.conj().T), "Should be Hermitian"
    
    print(f"✓ 3-qubit GHZ: Purity {initial_purity:.4f} → {final_purity:.4f}")
    print(f"✓ Trace preserved: {trace:.6f}")
    print(f"✓ Hermitian: ✓")


def test_noise_composition():
    """Test applying multiple noise channels in sequence"""
    print("\n" + "="*60)
    print("TEST 3: Noise Composition")
    print("="*60)
    
    # Start with superposition |+⟩ (sensitive to both T1 and T2)
    psi = np.array([1, 1], dtype=complex) / np.sqrt(2)
    state = QuantumState(1, state_vector=psi, use_density_matrix=True)
    
    rho_initial = state.density_matrix.copy()
    
    # Apply T1, then T2 noise
    t1_noise = AmplitudeDamping(gamma=0.2)
    t2_noise = PhaseDamping(gamma=0.2)
    
    t1_noise.apply(state)
    rho_after_t1 = state.density_matrix.copy()
    
    t2_noise.apply(state)
    rho_final = state.density_matrix
    
    # All three stages should be different
    assert not np.allclose(rho_initial, rho_after_t1, atol=1e-10), "T1 should modify state"
    assert not np.allclose(rho_after_t1, rho_final, atol=1e-10), "T2 should further modify state"
    
    # Trace should still be 1
    trace = np.trace(rho_final).real
    assert np.isclose(trace, 1.0), f"Trace should be 1 after composition, got {trace}"
    
    print("✓ Initial → T1 → T2: All stages different")
    print(f"✓ Final trace: {trace:.6f}")


def test_thermal_relaxation_t1_t2_constraint():
    """Test T2 <= 2*T1 constraint"""
    print("\n" + "="*60)
    print("TEST 4: Thermal Relaxation Constraints")
    print("="*60)
    
    # Valid: T2 = T1
    try:
        noise = ThermalRelaxation(t1=100e-6, t2=100e-6, gate_time=1e-6)
        print("✓ T2 = T1: Valid")
    except ValueError:
        assert False, "T2 = T1 should be valid"
    
    # Valid: T2 = 2*T1
    try:
        noise = ThermalRelaxation(t1=100e-6, t2=200e-6, gate_time=1e-6)
        print("✓ T2 = 2*T1: Valid")
    except ValueError:
        assert False, "T2 = 2*T1 should be valid"
    
    # Invalid: T2 > 2*T1
    try:
        noise = ThermalRelaxation(t1=100e-6, t2=250e-6, gate_time=1e-6)
        assert False, "Should have raised ValueError for T2 > 2*T1"
    except ValueError:
        print("✓ T2 > 2*T1: Correctly rejected")


def test_density_matrix_properties():
    """Test that density matrices maintain physical properties"""
    print("\n" + "="*60)
    print("TEST 5: Density Matrix Physical Properties")
    print("="*60)
    
    state = QuantumState(2, use_density_matrix=True)
    
    # Apply various noises
    noises = [
        DepolarizingNoise(0.2),
        AmplitudeDamping(0.3),
        PhaseDamping(0.15)
    ]
    
    for noise in noises:
        noise.apply(state, qubits=[0])
        rho = state.density_matrix
        
        # 1. Hermitian
        assert np.allclose(rho, rho.conj().T), f"{noise} produced non-Hermitian matrix"
        
        # 2. Trace = 1
        trace = np.trace(rho).real
        assert np.isclose(trace, 1.0, atol=1e-10), f"{noise} trace = {trace}, should be 1"
        
        # 3. Positive semi-definite (eigenvalues >= 0)
        eigenvalues = np.linalg.eigvalsh(rho)
        assert np.all(eigenvalues >= -1e-10), f"{noise} has negative eigenvalues: {eigenvalues}"
        
        # 4. Purity <= 1
        purity = np.trace(rho @ rho).real
        assert purity <= 1.0 + 1e-10, f"{noise} purity = {purity} > 1"
        
        print(f"✓ {noise.__class__.__name__}: All properties valid")


def test_numerical_stability():
    """Test numerical stability over many operations"""
    print("\n" + "="*60)
    print("TEST 6: Numerical Stability")
    print("="*60)
    
    state = QuantumState(2, use_density_matrix=True)
    noise = DepolarizingNoise(probability=0.01)
    
    # Apply noise 100 times
    for i in range(100):
        noise.apply(state, qubits=[0])
    
    rho = state.density_matrix
    
    # Check all properties still hold
    trace = np.trace(rho).real
    hermitian = np.allclose(rho, rho.conj().T)
    eigenvalues = np.linalg.eigvalsh(rho)
    positive = np.all(eigenvalues >= -1e-10)
    purity = np.trace(rho @ rho).real
    
    assert np.isclose(trace, 1.0, atol=1e-8), f"Trace drifted to {trace} after 100 steps"
    assert hermitian, "Lost Hermiticity after 100 steps"
    assert positive, f"Negative eigenvalues after 100 steps: {eigenvalues}"
    assert purity <= 1.0 + 1e-8, f"Purity > 1 after 100 steps: {purity}"
    
    print(f"✓ After 100 noise applications:")
    print(f"  Trace: {trace:.10f}")
    print(f"  Hermitian: ✓")
    print(f"  Positive: ✓")
    print(f"  Purity: {purity:.6f}")


def test_amplitude_damping_decay_rate():
    """Test that amplitude damping follows expected decay"""
    print("\n" + "="*60)
    print("TEST 7: Amplitude Damping Decay Rate")
    print("="*60)
    
    # Start in |1⟩
    psi = np.array([0, 1], dtype=complex)
    
    gammas = [0.0, 0.25, 0.5, 0.75, 1.0]
    
    for gamma in gammas:
        state = QuantumState(1, state_vector=psi, use_density_matrix=True)
        noise = AmplitudeDamping(gamma=gamma)
        noise.apply(state)
        
        p1 = state.density_matrix[1, 1].real
        p0 = state.density_matrix[0, 0].real
        
        # Expected: p1 = (1-γ), p0 = γ
        expected_p1 = 1 - gamma
        expected_p0 = gamma
        
        assert np.isclose(p1, expected_p1, atol=1e-10), f"γ={gamma}: P(1) = {p1}, expected {expected_p1}"
        assert np.isclose(p0, expected_p0, atol=1e-10), f"γ={gamma}: P(0) = {p0}, expected {expected_p0}"
        
        print(f"✓ γ={gamma}: P(1)={p1:.4f}, P(0)={p0:.4f} (correct)")


def test_phase_damping_coherence_decay():
    """Test that phase damping decays off-diagonal elements correctly"""
    print("\n" + "="*60)
    print("TEST 8: Phase Damping Coherence Decay")
    print("="*60)
    
    # Start in |+⟩ = (|0⟩ + |1⟩)/√2
    psi = np.array([1, 1], dtype=complex) / np.sqrt(2)
    
    gammas = [0.0, 0.25, 0.5, 0.75, 1.0]
    
    for gamma in gammas:
        state = QuantumState(1, state_vector=psi, use_density_matrix=True)
        
        initial_coherence = abs(state.density_matrix[0, 1])
        
        noise = PhaseDamping(gamma=gamma)
        noise.apply(state)
        
        final_coherence = abs(state.density_matrix[0, 1])
        
        # Expected: coherence decays by sqrt(1-γ)
        expected_coherence = initial_coherence * np.sqrt(1 - gamma)
        
        assert np.isclose(final_coherence, expected_coherence, atol=1e-10), \
            f"γ={gamma}: coherence = {final_coherence}, expected {expected_coherence}"
        
        # Populations should be preserved
        p0 = state.density_matrix[0, 0].real
        p1 = state.density_matrix[1, 1].real
        assert np.isclose(p0, 0.5, atol=1e-10), f"P(0) should be 0.5, got {p0}"
        assert np.isclose(p1, 0.5, atol=1e-10), f"P(1) should be 0.5, got {p1}"
        
        print(f"✓ γ={gamma}: coherence={final_coherence:.4f} (correct), populations preserved")


def test_zero_noise_is_identity():
    """Test that zero noise doesn't change the state"""
    print("\n" + "="*60)
    print("TEST 9: Zero Noise = Identity")
    print("="*60)
    
    # Complex multi-qubit state
    state = QuantumState(2, use_density_matrix=True)
    psi = np.array([0.5, 0.5, 0.5, 0.5], dtype=complex)
    state.density_matrix = np.outer(psi, psi.conj())
    rho_initial = state.density_matrix.copy()
    
    # Apply zero noise
    noises = [
        DepolarizingNoise(0.0),
        AmplitudeDamping(0.0),
        PhaseDamping(0.0)
    ]
    
    for noise in noises:
        state.density_matrix = rho_initial.copy()
        noise.apply(state)
        assert np.allclose(state.density_matrix, rho_initial, atol=1e-15), \
            f"{noise.__class__.__name__} with p=0 changed the state"
        print(f"✓ {noise.__class__.__name__}(0.0): No change")


def test_maximum_noise_limits():
    """Test behavior at maximum noise (p=1, γ=1)"""
    print("\n" + "="*60)
    print("TEST 10: Maximum Noise Limits")
    print("="*60)
    
    # Amplitude damping with γ=1: |1⟩ → |0⟩ completely
    psi = np.array([0, 1], dtype=complex)
    state = QuantumState(1, state_vector=psi, use_density_matrix=True)
    noise = AmplitudeDamping(gamma=1.0)
    noise.apply(state)
    
    p0 = state.density_matrix[0, 0].real
    p1 = state.density_matrix[1, 1].real
    
    assert np.isclose(p0, 1.0, atol=1e-10), f"γ=1 should give P(0)=1, got {p0}"
    assert np.isclose(p1, 0.0, atol=1e-10), f"γ=1 should give P(1)=0, got {p1}"
    print(f"✓ AmplitudeDamping(γ=1): |1⟩ → |0⟩ completely")
    
    # Phase damping with γ=1: destroys all coherence
    psi = np.array([1, 1], dtype=complex) / np.sqrt(2)
    state = QuantumState(1, state_vector=psi, use_density_matrix=True)
    noise = PhaseDamping(gamma=1.0)
    noise.apply(state)
    
    coherence = abs(state.density_matrix[0, 1])
    assert np.isclose(coherence, 0.0, atol=1e-10), f"γ=1 should destroy coherence, got {coherence}"
    print(f"✓ PhaseDamping(γ=1): Coherence completely destroyed")


if __name__ == "__main__":
    print("\n" + "="*70)
    print(" " * 15 + "ADVANCED NOISE STRESS TESTS")
    print("="*70)
    
    tests = [
        test_extreme_noise_probabilities,
        test_multi_qubit_noise,
        test_noise_composition,
        test_thermal_relaxation_t1_t2_constraint,
        test_density_matrix_properties,
        test_numerical_stability,
        test_amplitude_damping_decay_rate,
        test_phase_damping_coherence_decay,
        test_zero_noise_is_identity,
        test_maximum_noise_limits
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"\n❌ {test.__name__} FAILED:")
            print(f"   {e}")
        except Exception as e:
            failed += 1
            print(f"\n❌ {test.__name__} ERROR:")
            print(f"   {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print(f"   RESULTS: {passed}/{len(tests)} tests passed")
    if failed == 0:
        print(f"   🎉 ALL STRESS TESTS PASSED!")
    else:
        print(f"   ⚠️  {failed} tests failed")
    print("="*70 + "\n")
