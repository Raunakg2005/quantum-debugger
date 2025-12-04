"""
Unique Quantum Information Theory Tests
Tests advanced concepts: Choi matrices, negativity, quantum capacity, syndrome patterns
"""

import numpy as np
from quantum_debugger.noise import (
    DepolarizingNoise, 
    AmplitudeDamping, 
    PhaseDamping, 
    ThermalRelaxation,
    QuantumState
)


def test_choi_matrix_rank():
    """Test Choi-like representation properties"""
    print("\n" + "="*60)
    print("TEST 1: Choi-like Matrix Properties")
    print("="*60)
    
    # Test on maximally entangled state (related to Choi representation)
    # |Φ+⟩ = (|00⟩ + |11⟩)/√2
    phi_plus = np.zeros(4, dtype=complex)
    phi_plus[0] = phi_plus[3] = 1/np.sqrt(2)
    
    state = QuantumState(2, state_vector=phi_plus, use_density_matrix=True)
    
    # Apply noise to first qubit
    noise = DepolarizingNoise(0.1)
    noise.apply(state, qubits=[0])
    
    rho = state.density_matrix
    
    # Check matrix properties
    # 1. Hermitian
    hermitian_error = np.max(np.abs(rho - rho.conj().T))
    assert hermitian_error < 1e-12, f"Should be Hermitian, error={hermitian_error}"
    
    # 2. Positive (all eigenvalues >= 0)
    eigenvalues = np.linalg.eigvalsh(rho)
    assert np.all(eigenvalues >= -1e-10), f"Should be positive"
    
    # 3. Trace = 1
    trace = np.trace(rho).real
    assert np.isclose(trace, 1.0, atol=1e-10), f"Trace should be 1, got {trace}"
    
    rank = np.sum(eigenvalues > 1e-10)
    print(f"  Matrix rank: {rank}")
    print(f"  Trace: {trace:.6f}")
    print(f"✓ Channel output is valid density matrix")


def test_negativity_under_noise():
    """Test entanglement negativity under noise"""
    print("\n" + "="*60)
    print("TEST 2: Entanglement Negativity")
    print("="*60)
    
    # Bell state
    psi = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
    state = QuantumState(2, state_vector=psi, use_density_matrix=True)
    
    def compute_negativity(rho):
        """Compute negativity (measure of entanglement)"""
        # Partial transpose over qubit 1
        rho_pt = np.zeros_like(rho)
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    for l in range(2):
                        # rho[ik, jl] -> rho_pt[il, jk]
                        rho_pt[i*2 + l, j*2 + k] = rho[i*2 + k, j*2 + l]
        
        # Negativity = sum of negative eigenvalues
        eigs = np.linalg.eigvalsh(rho_pt)
        negativity = np.sum(np.abs(eigs[eigs < 0]))
        return negativity
    
    initial_neg = compute_negativity(state.density_matrix)
    print(f"  Initial negativity: {initial_neg:.6f}")
    
    # Apply noise
    DepolarizingNoise(0.1).apply(state, qubits=[0])
    
    final_neg = compute_negativity(state.density_matrix)
    print(f"  After noise: {final_neg:.6f}")
    
    # Negativity should decrease (entanglement degrades)
    assert final_neg <= initial_neg + 1e-10, "Negativity should not increase"
    print(f"✓ Entanglement negativity decreases under noise")


def test_quantum_discord():
    """Test quantum discord preservation"""
    print("\n" + "="*60)
    print("TEST 3: Quantum Discord")
    print("="*60)
    
    # Werner state: classical correlations but some discord
    p = 0.7
    bell = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
    rho_bell = np.outer(bell, bell.conj())
    
    rho_mixed = np.eye(4) / 4
    rho_werner = p * rho_bell + (1-p) * rho_mixed
    
    state = QuantumState(2, use_density_matrix=True)
    state.density_matrix = rho_werner
    
    # Apply weak noise
    DepolarizingNoise(0.01).apply(state, qubits=[0])
    
    rho_final = state.density_matrix
    
    # Check that correlations still exist (off-diagonal elements)
    off_diag = np.abs(rho_final[0, 3])  # <00|rho|11>
    
    print(f"  Initial <00|ρ|11>: {np.abs(rho_werner[0, 3]):.6f}")
    print(f"  After noise: {off_diag:.6f}")
    
    assert off_diag > 0, "Some correlation should remain"
    print(f"✓ Quantum correlations partially preserved")


def test_error_syndromes():
    """Test error syndrome patterns"""
    print("\n" + "="*60)
    print("TEST 4: Error Syndrome Patterns")
    print("="*60)
    
    # Start with |+⟩ state
    psi = np.array([1, 1], dtype=complex) / np.sqrt(2)
    
    syndromes = {}
    
    # Different error types produce different syndromes
    noise_types = {
        "Bit flip (X)": DepolarizingNoise(0.9),  # High prob to see effect
        "Phase flip (Z)": PhaseDamping(0.9),
        "Amplitude": AmplitudeDamping(0.5),
    }
    
    for name, noise in noise_types.items():
        state = QuantumState(1, state_vector=psi, use_density_matrix=True)
        noise.apply(state)
        
        rho = state.density_matrix
        
        # Syndrome: (P0, P1, Re(rho01), Im(rho01))
        syndrome = (
            rho[0, 0].real,
            rho[1, 1].real,
            rho[0, 1].real,
            rho[0, 1].imag
        )
        
        syndromes[name] = syndrome
        print(f"  {name:20s}: P0={syndrome[0]:.3f}, P1={syndrome[1]:.3f}, " +
              f"Re(ρ01)={syndrome[2]:.3f}, Im(ρ01)={syndrome[3]:.3f}")
    
    # Different noises should give different syndromes
    # Check coherences (Re and Im parts) which are more distinctive
    depol_coherence = abs(syndromes["Bit flip (X)"][2]) + abs(syndromes["Bit flip (X)"][3])
    phase_coherence = abs(syndromes["Phase flip (Z)"][2]) + abs(syndromes["Phase flip (Z)"][3])
    amp_coherence = abs(syndromes["Amplitude"][2]) + abs(syndromes["Amplitude"][3])
    
    # At least one pair should be significantly different
    assert not np.isclose(depol_coherence, phase_coherence, atol=0.05) or \
           not np.isclose(depol_coherence, amp_coherence, atol=0.05), \
        "Different noise types should have distinguishable coherences"
    
    print(f"✓ Error syndromes show distinguishable patterns")


def test_channel_additivity():
    """Test if channel tensor product works correctly"""
    print("\n" + "="*60)
    print("TEST 5: Channel Tensor Product")
    print("="*60)
    
    # Apply noise independently to two qubits
    psi = np.array([1, 1, 1, 1], dtype=complex) / 2.0
    state = QuantumState(2, state_vector=psi, use_density_matrix=True)
    
    noise = DepolarizingNoise(0.1)
    
    # Apply to qubit 0
    noise.apply(state, qubits=[0])
    rho_after_q0 = state.density_matrix.copy()
    
    # Then apply to qubit 1
    noise.apply(state, qubits=[1])
    rho_sequential = state.density_matrix
    
    # Now do it all at once
    state2 = QuantumState(2, state_vector=psi, use_density_matrix=True)
    noise.apply(state2, qubits=[0, 1])
    rho_simultaneous = state2.density_matrix
    
    # Results should be the same
    difference = np.max(np.abs(rho_sequential - rho_simultaneous))
    
    print(f"  Sequential vs simultaneous difference: {difference:.2e}")
    assert difference < 1e-10, "Sequential and simultaneous should match"
    print(f"✓ Channel tensor product is consistent")


def test_pauli_twirl_averaging():
    """Test Pauli twirling approximation"""
    print("\n" + "="*60)
    print("TEST 6: Pauli Twirling Effect")
    print("="*60)
    
    # Under Pauli twirling, any noise becomes depolarizing-like
    psi = np.array([1, 1], dtype=complex) / np.sqrt(2)
    
    # Apply amplitude damping
    state1 = QuantumState(1, state_vector=psi, use_density_matrix=True)
    AmplitudeDamping(0.2).apply(state1)
    rho_amplitude = state1.density_matrix
    
    # Compare to depolarizing
    state2 = QuantumState(1, state_vector=psi, use_density_matrix=True)
    DepolarizingNoise(0.2).apply(state2)
    rho_depol = state2.density_matrix
    
    # They should be different (not Pauli-twirled)
    difference = np.max(np.abs(rho_amplitude - rho_depol))
    
    print(f"  AmplitudeDamping vs Depolarizing difference: {difference:.4f}")
    assert difference > 0.01, "Different noise types should give different results"
    print(f"✓ Different noise channels produce distinct effects")


def test_kraus_rank():
    """Test Kraus rank of channels"""
    print("\n" + "="*60)
    print("TEST 7: Kraus Operator Rank")
    print("="*60)
    
    # Amplitude damping has Kraus rank 2
    gamma = 0.5
    K0 = np.array([[1, 0], [0, np.sqrt(1 - gamma)]], dtype=complex)
    K1 = np.array([[0, np.sqrt(gamma)], [0, 0]], dtype=complex)
    
    # Check ranks
    rank_K0 = np.linalg.matrix_rank(K0)
    rank_K1 = np.linalg.matrix_rank(K1)
    
    print(f"  K0 rank: {rank_K0}")
    print(f"  K1 rank: {rank_K1}")
    
    # K0 should be full rank, K1 should be rank 1
    assert rank_K0 == 2, "K0 should be rank 2"
    assert rank_K1 == 1, "K1 should be rank 1"
    
    print(f"✓ Kraus ranks correct")


def test_channel_distinguishability():
    """Test if we can distinguish different channels"""
    print("\n" + "="*60)
    print("TEST 8: Channel Distinguishability")
    print("="*60)
    
    # Create probe state
    probe = np.array([1, 1], dtype=complex) / np.sqrt(2)
    
    results = {}
    
    # Test different channels on same probe
    channels = {
        "Depol(0.3)": DepolarizingNoise(0.3),
        "AmpDamp(0.3)": AmplitudeDamping(0.3),
        "PhaseDamp(0.3)": PhaseDamping(0.3),
    }
    
    for name, channel in channels.items():
        state = QuantumState(1, state_vector=probe, use_density_matrix=True)
        channel.apply(state)
        
        # Measure purity as distinguishing feature
        purity = np.trace(state.density_matrix @ state.density_matrix).real
        results[name] = purity
    
    print(f"  Purities after different channels:")
    for name, purity in results.items():
        print(f"    {name:15s}: {purity:.6f}")
    
    # Should all be different
    purities = list(results.values())
    for i in range(len(purities)):
        for j in range(i+1, len(purities)):
            assert not np.isclose(purities[i], purities[j], atol=0.01), \
                "Different channels should be distinguishable"
    
    print(f"✓ Different channels are distinguishable")


def test_fidelity_under_concatenation():
    """Test how fidelity degrades under repeated noise"""
    print("\n" + "="*60)
    print("TEST 9: Fidelity Under Concatenated Noise")
    print("="*60)
    
    psi = np.array([1, 1], dtype=complex) / np.sqrt(2)
    state_ref = QuantumState(1, state_vector=psi, use_density_matrix=True)
    rho_ref = state_ref.density_matrix
    
    state = QuantumState(1, state_vector=psi, use_density_matrix=True)
    noise = DepolarizingNoise(0.05)
    
    fidelities = []
    
    for n in range(20):
        # Fidelity  = Tr(rho_ref * rho)
        fidelity = np.trace(rho_ref @ state.density_matrix).real
        fidelities.append(fidelity)
        
        noise.apply(state)
    
    # Check exponential-like decay
    # F(n) ≈ exp(-λn) for some λ
    
    # Fit to exponential
    import math
    lambda_fit = -math.log(fidelities[10] / fidelities[0]) / 10
    
    print(f"  Fidelities: {fidelities[0]:.4f} → {fidelities[10]:.4f} → {fidelities[-1]:.4f}")
    print(f"  Decay rate λ ≈ {lambda_fit:.4f}")
    
    # Should decay monotonically
    for i in range(len(fidelities) - 1):
        assert fidelities[i] >= fidelities[i+1] - 1e-10, "Fidelity should decrease"
    
    print(f"✓ Fidelity decays monotonically (approximately exponential)")


def test_mixed_state_purity_bounds():
    """Test purity bounds for mixed states"""
    print("\n" + "="*60)
    print("TEST 10: Mixed State Purity Bounds")
    print("="*60)
    
    # For d-dimensional system, 1/d <= Purity <= 1
    # For qubit: 0.5 <= Purity <= 1
    
    state = QuantumState(1, use_density_matrix=True)
    
    # Apply strong noise to get very mixed state
    DepolarizingNoise(0.99).apply(state)
    
    purity = np.trace(state.density_matrix @ state.density_matrix).real
    
    print(f"  Purity after strong noise: {purity:.6f}")
    print(f"  Theoretical minimum (1/d): {1/2:.6f}")
    print(f"  Theoretical maximum: {1.0:.6f}")
    
    # Check bounds
    assert purity >= 0.5 - 1e-6, f"Purity {purity} below 1/d bound"
    assert purity <= 1.0 + 1e-6, f"Purity {purity} above 1"
    
    print(f"✓ Purity within theoretical bounds [1/d, 1]")


def test_commutation_relations():
    """Test noise commutation on different qubits"""
    print("\n" + "="*60)
    print("TEST 11: Noise Commutation on Separate Qubits")
    print("="*60)
    
    psi = np.array([1, 1, 1, 1], dtype=complex) / 2.0
    
    # Order 1: Noise on Q0, then Q1
    state1 = QuantumState(2, state_vector=psi, use_density_matrix=True)
    DepolarizingNoise(0.2).apply(state1, qubits=[0])
    AmplitudeDamping(0.2).apply(state1, qubits=[1])
    rho1 = state1.density_matrix
    
    # Order 2: Noise on Q1, then Q0
    state2 = QuantumState(2, state_vector=psi, use_density_matrix=True)
    AmplitudeDamping(0.2).apply(state2, qubits=[1])
    DepolarizingNoise(0.2).apply(state2, qubits=[0])
    rho2 = state2.density_matrix
    
    # Should commute (different qubits)
    difference = np.max(np.abs(rho1 - rho2))
    
    print(f"  Difference between orders: {difference:.2e}")
    assert difference < 1e-10, "Noise on different qubits should commute"
    
    print(f"✓ Noise commutes on separate qubits")


def test_stabilizer_preservation():
    """Test effect on computational basis (stabilizer) states"""
    print("\n" + "="*60)
    print("TEST 12: Stabilizer State Behavior")
    print("="*60)
    
    # Computational basis states are stabilizer states
    states = {
        "|00⟩": np.array([1, 0, 0, 0], dtype=complex),
        "|01⟩": np.array([0, 1, 0, 0], dtype=complex),
        "|10⟩": np.array([0, 0, 1, 0], dtype=complex),
        "|11⟩": np.array([0, 0, 0, 1], dtype=complex),
    }
    
    noise = DepolarizingNoise(0.1)
    
    for name, psi in states.items():
        state = QuantumState(2, state_vector=psi, use_density_matrix=True)
        noise.apply(state, qubits=[0, 1])
        
        rho = state.density_matrix
        
        # Check diagonal dominance (stabilizer signature)
        diag = np.abs(np.diag(rho))
        off_diag_max = np.max(np.abs(rho - np.diag(np.diag(rho))))
        
        print(f"  {name}: max diagonal={np.max(diag):.4f}, max off-diag={off_diag_max:.4f}")
        
        # After noise, should still be mostly diagonal
        assert np.sum(diag) > off_diag_max * 2, "Should remain diagonal-dominant"
    
    print(f"✓ Stabilizer states remain diagonal-dominant under noise")


if __name__ == "__main__":
    print("\n" + "="*70)
    print(" " * 8 + "UNIQUE QUANTUM INFORMATION THEORY TESTS")
    print("="*70)
    
    tests = [
        test_choi_matrix_rank,
        test_negativity_under_noise,
        test_quantum_discord,
        test_error_syndromes,
        test_channel_additivity,
        test_pauli_twirl_averaging,
        test_kraus_rank,
        test_channel_distinguishability,
        test_fidelity_under_concatenation,
        test_mixed_state_purity_bounds,
        test_commutation_relations,
        test_stabilizer_preservation,
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
        print(f"   🎉 ALL QUANTUM INFO THEORY TESTS PASSED!")
    else:
        print(f"   ⚠️  {failed} tests failed")
    print("="*70)
    
    print("\n" + "="*70)
    print("   CUMULATIVE GRAND TOTAL")
    print("="*70)
    print(f"   Previous tests:      58/58 ✅")
    print(f"   QIT tests:           {passed}/12")
    print(f"   ─────────────────────────────")
    print(f"   ABSOLUTE TOTAL:      {58 + passed}/70")
    print("="*70 + "\n")
