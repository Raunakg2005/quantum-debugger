"""
Tests for quantum noise models
"""

import numpy as np
from quantum_debugger.noise import DepolarizingNoise, AmplitudeDamping, PhaseDamping, QuantumState


def test_depolarizing_noise_reduces_purity():
    """Depolarizing noise should reduce state purity"""
    # Create pure state
    state = QuantumState(1, use_density_matrix=True)
    
    # Check initial purity (should be 1 for pure state)
    initial_purity = np.trace(state.density_matrix @ state.density_matrix).real
    assert np.isclose(initial_purity, 1.0), f"Initial purity should be 1, got {initial_purity}"
    
    # Apply depolarizing noise
    noise = DepolarizingNoise(probability=0.1)
    noise.apply(state)
    
    # Check final purity (should be < 1)
    final_purity = np.trace(state.density_matrix @ state.density_matrix).real
    assert final_purity < initial_purity, f"Purity should decrease, got {initial_purity} -> {final_purity}"
    assert final_purity > 0, f"Purity should be positive, got {final_purity}"
    print(f"✓ Depolarizing noise reduced purity from {initial_purity:.4f} to {final_purity:.4f}")


def test_amplitude_damping_decay():
    """Amplitude damping should cause |1⟩ to decay toward |0⟩"""
    # Start in |1⟩ state
    psi = np.array([0, 1], dtype=complex)
    state = QuantumState(1, state_vector=psi, use_density_matrix=True)
    
    # Initial: should be in |1⟩
    rho = state.density_matrix
    p1_initial = rho[1, 1].real
    assert np.isclose(p1_initial, 1.0), f"Should start in |1⟩, got P(1)={p1_initial}"
    
    # Apply amplitude damping
    noise = AmplitudeDamping(gamma=0.3)
    noise.apply(state)
    
    # Final: |1⟩ population should decrease
    rho = state.density_matrix
    p1_final = rho[1, 1].real
    p0_final = rho[0, 0].real
    
    assert p1_final < p1_initial, f"|1⟩ population should decrease: {p1_initial} -> {p1_final}"
    assert np.isclose(p0_final + p1_final, 1.0), f"Probabilities should sum to 1: {p0_final + p1_final}"
    print(f"✓ Amplitude damping: P(1) decreased from {p1_initial:.4f} to {p1_final:.4f}")


def test_phase_damping_preserves_populations():
    """Phase damping should preserve populations but reduce coherence"""
    # Create superposition |+⟩ = (|0⟩ + |1⟩)/√2
    psi = np.array([1, 1], dtype=complex) / np.sqrt(2)
    state = QuantumState(1, state_vector=psi, use_density_matrix=True)
    
    # Initial populations
    rho_initial = state.density_matrix
    p0_initial = rho_initial[0, 0].real
    p1_initial = rho_initial[1, 1].real
    coherence_initial = abs(rho_initial[0, 1])
    
    # Apply phase damping
    noise = PhaseDamping(gamma=0.5)
    noise.apply(state)
    
    # Final populations
    rho_final = state.density_matrix
    p0_final = rho_final[0, 0].real
    p1_final = rho_final[1, 1].real
    coherence_final = abs(rho_final[0, 1])
    
    # Populations should be preserved
    assert np.isclose(p0_initial, p0_final, atol=1e-10), f"P(0) should be preserved"
    assert np.isclose(p1_initial, p1_final, atol=1e-10), f"P(1) should be preserved"
    
    # Coherence should decrease
    assert coherence_final < coherence_initial, f"Coherence should decrease"
    print(f"✓ Phase damping preserved populations, reduced coherence from {coherence_initial:.4f} to {coherence_final:.4f}")


def test_noise_probability_bounds():
    """Noise probabilities should be in valid range [0, 1]"""
    # Valid probabilities
    DepolarizingNoise(0.0)
    DepolarizingNoise(0.5)
    DepolarizingNoise(1.0)
    
    # Invalid probabilities should raise
    try:
        DepolarizingNoise(-0.1)
        assert False, "Should have raised ValueError for negative probability"
    except ValueError:
        pass  # Expected
    
    try:
        DepolarizingNoise(1.5)
        assert False, "Should have raised ValueError for probability > 1"
    except ValueError:
        pass  # Expected
    
    print("✓ Noise probability bounds validated")


def test_depolarizing_noise_bell_state():
    """Test depolarizing noise on Bell state"""
    # Create Bell state manually with density matrix
    state = QuantumState(2, use_density_matrix=True)
    
    # Bell state: (|00⟩ + |11⟩)/√2
    psi = np.zeros(4, dtype=complex)
    psi[0] = 1/np.sqrt(2)  # |00⟩
    psi[3] = 1/np.sqrt(2)  # |11⟩
    state.density_matrix = np.outer(psi, psi.conj())
    
    # Apply noise to both qubits
    noise = DepolarizingNoise(probability=0.05)
    noise.apply(state, qubits=[0, 1])
    
    # Density matrix should still be Hermitian
    rho = state.density_matrix
    assert np.allclose(rho, rho.conj().T), "Density matrix should be Hermitian"
    
    # Trace should be 1
    trace = np.trace(rho).real
    assert np.isclose(trace, 1.0), f"Trace should be 1, got {trace}"
    
    print(f"✓ Depolarizing noise on Bell state maintains valid density matrix")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("   NOISE SIMULATION TESTS - Phase 1")
    print("="*60 + "\n")
    
    try:
        test_depolarizing_noise_reduces_purity()
        test_amplitude_damping_decay()
        test_phase_damping_preserves_populations()
        test_noise_probability_bounds()
        test_depolarizing_noise_bell_state()
        
        print("\n" + "="*60)
        print(f"   ✅ All 5 noise tests PASSED!")
        print("="*60 + "\n")
    except Exception as e:
        print(f"\n❌ Test failed with error:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
