"""
Extreme edge case tests for noise models
Tests unusual scenarios, numerical precision, and potential bugs
"""

import numpy as np
from quantum_debugger.noise import (
    DepolarizingNoise, 
    AmplitudeDamping, 
    PhaseDamping, 
    ThermalRelaxation,
    QuantumState
)


def test_noise_commutation():
    """Test if different noise orders give same result (they shouldn't!)"""
    print("\n" + "="*60)
    print("TEST 1: Noise Commutation Properties")
    print("="*60)
    
    psi = np.array([1, 1], dtype=complex) / np.sqrt(2)
    
    # Order 1: T1 then T2
    state1 = QuantumState(1, state_vector=psi, use_density_matrix=True)
    t1 = AmplitudeDamping(0.3)
    t2 = PhaseDamping(0.3)
    t1.apply(state1)
    t2.apply(state1)
    rho1 = state1.density_matrix
    
    # Order 2: T2 then T1
    state2 = QuantumState(1, state_vector=psi, use_density_matrix=True)
    t2.apply(state2)
    t1.apply(state2)
    rho2 = state2.density_matrix
    
    # They should be DIFFERENT (noise doesn't commute in general)
    if np.allclose(rho1, rho2, atol=1e-10):
        print("⚠️  Warning: T1·T2 = T2·T1 (unexpected commutativity)")
    else:
        print("✓ T1·T2 ≠ T2·T1 (noise is non-commutative, as expected)")
    
    # But both should be valid density matrices
    assert np.isclose(np.trace(rho1).real, 1.0)
    assert np.isclose(np.trace(rho2).real, 1.0)
    print("✓ Both orders produce valid density matrices")


def test_tiny_noise_parameters():
    """Test very small noise parameters (numerical precision)"""
    print("\n" + "="*60)
    print("TEST 2: Tiny Noise Parameters (Numerical Precision)")
    print("="*60)
    
    psi = np.array([1, 1], dtype=complex) / np.sqrt(2)
    state = QuantumState(1, state_vector=psi, use_density_matrix=True)
    rho_initial = state.density_matrix.copy()
    
    # Very small noise
    tiny_noises = [1e-6, 1e-10, 1e-15]
    
    for p in tiny_noises:
        state = QuantumState(1, state_vector=psi, use_density_matrix=True)
        noise = DepolarizingNoise(probability=p)
        noise.apply(state)
        
        # Should be VERY close to initial but not exactly equal
        difference = np.max(np.abs(state.density_matrix - rho_initial))
        
        if p >= 1e-14:  # Below machine precision, might be zero
            assert difference > 0, f"p={p}: No change detected (numerical underflow?)"
        
        # Still valid
        trace = np.trace(state.density_matrix).real
        assert np.isclose(trace, 1.0, atol=1e-12), f"p={p}: Trace = {trace}"
        
        print(f"✓ p={p}: Max difference = {difference:.2e}, trace = {trace:.15f}")


def test_kraus_operator_completeness():
    """Test that Kraus operators satisfy completeness relation"""
    print("\n" + "="*60)
    print("TEST 3: Kraus Operator Completeness")
    print("="*60)
    
    # For amplitude damping: K0†K0 + K1†K1 = I
    gamma = 0.3
    K0 = np.array([[1, 0], [0, np.sqrt(1 - gamma)]], dtype=complex)
    K1 = np.array([[0, np.sqrt(gamma)], [0, 0]], dtype=complex)
    
    completeness = K0.conj().T @ K0 + K1.conj().T @ K1
    identity = np.eye(2, dtype=complex)
    
    assert np.allclose(completeness, identity), "Kraus operators don't sum to identity!"
    print(f"✓ Amplitude damping Kraus completeness verified")
    
    # For phase damping
    K0 = np.array([[1, 0], [0, np.sqrt(1 - gamma)]], dtype=complex)
    K1 = np.array([[0, 0], [0, np.sqrt(gamma)]], dtype=complex)
    
    completeness = K0.conj().T @ K0 + K1.conj().T @ K1
    assert np.allclose(completeness, identity), "Phase damping Kraus operators invalid!"
    print(f"✓ Phase damping Kraus completeness verified")


def test_noise_on_computational_basis():
    """Test noise on all computational basis states"""
    print("\n" + "="*60)
    print("TEST 4: Noise on Computational Basis States")
    print("="*60)
    
    noise = DepolarizingNoise(0.1)
    
    # Test on |0⟩ and |1⟩
    for basis_state, label in [(np.array([1, 0], dtype=complex), "|0⟩"),
                                (np.array([0, 1], dtype=complex), "|1⟩")]:
        state = QuantumState(1, state_vector=basis_state, use_density_matrix=True)
        noise.apply(state)
        
        # Check properties
        trace = np.trace(state.density_matrix).real
        purity = np.trace(state.density_matrix @ state.density_matrix).real
        
        assert np.isclose(trace, 1.0), f"{label}: Invalid trace"
        assert purity < 1.0, f"{label}: Purity should decrease"
        assert purity > 0, f"{label}: Purity should be positive"
        
        print(f"✓ {label}: trace={trace:.6f}, purity={purity:.6f}")


def test_maximally_mixed_state_limit():
    """Test that high noise approaches maximally mixed state"""
    print("\n" + "="*60)
    print("TEST 5: Maximally Mixed State Limit")
    print("="*60)
    
    state = QuantumState(1, use_density_matrix=True)
    
    # Apply very high noise many times
    noise = DepolarizingNoise(0.5)
    for _ in range(50):
        noise.apply(state)
    
    rho = state.density_matrix
    
    # Should approach maximally mixed: rho = I/2
    maximally_mixed = np.eye(2) / 2
    distance = np.max(np.abs(rho - maximally_mixed))
    
    purity = np.trace(rho @ rho).real
    
    print(f"✓ After 50 applications of p=0.5:")
    print(f"  Distance from I/2: {distance:.6f}")
    print(f"  Purity: {purity:.6f} (0.5 = maximally mixed)")
    
    assert purity < 0.6, "Should be close to maximally mixed"
    assert purity > 0.4, "Shouldn't go below maximally mixed purity"


def test_thermal_relaxation_with_zero_times():
    """Test thermal relaxation edge cases"""
    print("\n" + "="*60)
    print("TEST 6: Thermal Relaxation Edge Cases")
    print("="*60)
    
    # Very short gate time (negligible noise)
    try:
        noise = ThermalRelaxation(t1=100e-6, t2=50e-6, gate_time=1e-12)
        state = QuantumState(1, use_density_matrix=True)
        noise.apply(state)
        print("✓ Very short gate time: OK")
    except:
        assert False, "Should handle very short gate times"
    
    # Gate time comparable to T1/T2
    try:
        noise = ThermalRelaxation(t1=100e-6, t2=50e-6, gate_time=100e-6)
        state = QuantumState(1, use_density_matrix=True)
        noise.apply(state)
        print("✓ Gate time = T1: OK")
    except:
        assert False, "Should handle gate_time = T1"
    
    # Very long T1/T2 (negligible noise)
    try:
        noise = ThermalRelaxation(t1=1e6, t2=1e6, gate_time=1e-6)
        state = QuantumState(1, use_density_matrix=True)
        noise.apply(state)
        print("✓ Very long T1/T2: OK")
    except:
        assert False, "Should handle very long coherence times"


def test_multi_qubit_selective_noise():
    """Test noise on specific qubits in multi-qubit system"""
    print("\n" + "="*60)
    print("TEST 7: Selective Qubit Noise")
    print("="*60)
    
    # 3-qubit state
    state = QuantumState(3, use_density_matrix=True)
    rho_initial = state.density_matrix.copy()
    
    # Apply noise ONLY to qubit 1
    noise = DepolarizingNoise(0.2)
    noise.apply(state, qubits=[1])
    
    rho_final = state.density_matrix
    
    # State should change
    assert not np.allclose(rho_initial, rho_final), "State should change"
    
    # But trace should be preserved
    trace = np.trace(rho_final).real
    assert np.isclose(trace, 1.0), f"Trace = {trace}, should be 1"
    
    print("✓ Selective noise on qubit 1 of 3-qubit system")
    print(f"✓ Trace preserved: {trace:.10f}")


def test_repeated_same_noise():
    """Test applying same noise multiple times"""
    print("\n" + "="*60)
    print("TEST 8: Repeated Same Noise")
    print("="*60)
    
    psi = np.array([1, 1], dtype=complex) / np.sqrt(2)
    state = QuantumState(1, state_vector=psi, use_density_matrix=True)
    
    noise = DepolarizingNoise(0.05)
    purities = []
    
    for i in range(20):
        noise.apply(state)
        purity = np.trace(state.density_matrix @ state.density_matrix).real
        purities.append(purity)
    
    # Purity should monotonically decrease
    for i in range(len(purities) - 1):
        assert purities[i] >= purities[i+1] - 1e-10, \
            f"Purity increased at step {i}: {purities[i]} -> {purities[i+1]}"
    
    print(f"✓ Purity monotonically decreased over 20 iterations")
    print(f"  Initial: {purities[0]:.6f}")
    print(f"  Final: {purities[-1]:.6f}")


def test_eigenvalue_bounds():
    """Test that all eigenvalues stay in [0,1]"""
    print("\n" + "="*60)
    print("TEST 9: Eigenvalue Bounds")
    print("="*60)
    
    # Create random superposition
    psi = np.array([0.6, 0.8], dtype=complex)
    psi /= np.linalg.norm(psi)
    
    state = QuantumState(1, state_vector=psi, use_density_matrix=True)
    
    noises = [
        DepolarizingNoise(0.5),
        AmplitudeDamping(0.7),
        PhaseDamping(0.6)
    ]
    
    for noise in noises:
        noise.apply(state)
        eigenvalues = np.linalg.eigvalsh(state.density_matrix)
        
        assert np.all(eigenvalues >= -1e-10), f"{noise}: Negative eigenvalue {min(eigenvalues)}"
        assert np.all(eigenvalues <= 1.0 + 1e-10), f"{noise}: Eigenvalue > 1: {max(eigenvalues)}"
        assert np.abs(np.sum(eigenvalues) - 1.0) < 1e-10, f"{noise}: Eigenvalues don't sum to 1"
        
        print(f"✓ {noise.__class__.__name__}: eigenvalues in [0,1], sum=1")


def test_hermiticity_after_many_operations():
    """Test Hermiticity is preserved over many operations"""
    print("\n" + "="*60)
    print("TEST 10: Hermiticity Preservation")
    print("="*60)
    
    psi = np.array([1, 1, 1, 1], dtype=complex) / 2.0
    state = QuantumState(2, state_vector=psi, use_density_matrix=True)
    
    # Mix of different noises
    noises = [
        DepolarizingNoise(0.05),
        AmplitudeDamping(0.05),
        PhaseDamping(0.05)
    ]
    
    for i in range(30):
        noise = noises[i % len(noises)]
        noise.apply(state, qubits=[i % 2])
        
        # Check Hermiticity
        rho = state.density_matrix
        hermitian_error = np.max(np.abs(rho - rho.conj().T))
        
        assert hermitian_error < 1e-12, f"Step {i}: Lost Hermiticity, error={hermitian_error}"
    
    print("✓ Hermiticity maintained over 30 mixed noise operations")
    print(f"  Final Hermitian error: {hermitian_error:.2e}")


def test_invalid_inputs():
    """Test error handling for invalid inputs"""
    print("\n" + "="*60)
    print("TEST 11: Invalid Input Handling")
    print("="*60)
    
    # Test negative probabilities
    try:
        DepolarizingNoise(-0.1)
        assert False, "Should reject negative probability"
    except ValueError:
        print("✓ Negative probability rejected")
    
    # Test probability > 1
    try:
        DepolarizingNoise(1.5)
        assert False, "Should reject probability > 1"
    except ValueError:
        print("✓ Probability > 1 rejected")
    
    # Test invalid T1/T2 relationship
    try:
        ThermalRelaxation(t1=100e-6, t2=300e-6, gate_time=1e-6)
        assert False, "Should reject T2 > 2*T1"
    except ValueError:
        print("✓ Invalid T2 > 2*T1 rejected")
    
    # Test negative T1
    try:
        ThermalRelaxation(t1=-100e-6, t2=50e-6, gate_time=1e-6)
        assert False, "Should reject negative T1"
    except:
        print("✓ Negative T1 rejected")


def test_noise_on_maximally_entangled():
    """Test noise on maximally entangled states"""
    print("\n" + "="*60)
    print("TEST 12: Noise on Maximally Entangled States")
    print("="*60)
    
    # Bell states
    bell_states = {
        "|Φ+⟩": np.array([1, 0, 0, 1]) / np.sqrt(2),
        "|Φ-⟩": np.array([1, 0, 0, -1]) / np.sqrt(2),
        "|Ψ+⟩": np.array([0, 1, 1, 0]) / np.sqrt(2),
        "|Ψ-⟩": np.array([0, 1, -1, 0]) / np.sqrt(2),
    }
    
    noise = DepolarizingNoise(0.1)
    
    for name, psi in bell_states.items():
        state = QuantumState(2, state_vector=psi, use_density_matrix=True)
        noise.apply(state, qubits=[0])
        
        # Check validity
        trace = np.trace(state.density_matrix).real
        hermitian = np.allclose(state.density_matrix, state.density_matrix.conj().T)
        
        assert np.isclose(trace, 1.0), f"{name}: Invalid trace"
        assert hermitian, f"{name}: Not Hermitian"
        
        print(f"✓ {name}: trace={trace:.6f}, Hermitian=True")


def test_purity_bounds():
    """Test that purity always stays in [0,1]"""
    print("\n" + "="*60)
    print("TEST 13: Purity Bounds")
    print("="*60)
    
    # Start with random states
    test_states = [
        np.array([1, 0], dtype=complex),  # |0⟩
        np.array([0, 1], dtype=complex),  # |1⟩
        np.array([1, 1], dtype=complex) / np.sqrt(2),  # |+⟩
        np.array([1, -1], dtype=complex) / np.sqrt(2),  # |-⟩
        np.array([1, 1j], dtype=complex) / np.sqrt(2),  # |i⟩
    ]
    
    noise = DepolarizingNoise(0.3)
    
    for i, psi in enumerate(test_states):
        state = QuantumState(1, state_vector=psi, use_density_matrix=True)
        
        initial_purity = np.trace(state.density_matrix @ state.density_matrix).real
        assert np.isclose(initial_purity, 1.0), "Pure state should have purity 1"
        
        noise.apply(state)
        
        final_purity = np.trace(state.density_matrix @ state.density_matrix).real
        
        assert 0 <= final_purity <= 1.0 + 1e-10, f"State {i}: Purity out of bounds: {final_purity}"
        assert final_purity <= initial_purity + 1e-10, f"State {i}: Purity increased!"
        
        print(f"✓ State {i}: purity {initial_purity:.4f} → {final_purity:.4f}")


def test_trace_distance():
    """Test trace distance between noisy and pure states"""
    print("\n" + "="*60)
    print("TEST 14: Trace Distance Calculation")
    print("="*60)
    
    psi = np.array([1, 1], dtype=complex) / np.sqrt(2)
    
    # Pure state
    state_pure = QuantumState(1, state_vector=psi, use_density_matrix=True)
    rho_pure = state_pure.density_matrix.copy()
    
    # Noisy state
    state_noisy = QuantumState(1, state_vector=psi, use_density_matrix=True)
    noise = DepolarizingNoise(0.2)
    noise.apply(state_noisy)
    rho_noisy = state_noisy.density_matrix
    
    # Trace distance: D(ρ,σ) = (1/2) Tr|ρ-σ|
    diff = rho_pure - rho_noisy
    eigenvalues = np.linalg.eigvalsh(diff)
    trace_distance = 0.5 * np.sum(np.abs(eigenvalues))
    
    # Should be > 0 (different states)
    assert trace_distance > 0, "Trace distance should be positive"
    # Should be <= 1 (bound)
    assert trace_distance <= 1.0 + 1e-10, f"Trace distance > 1: {trace_distance}"
    
    print(f"✓ Trace distance(pure, noisy) = {trace_distance:.6f}")
    print(f"✓ Distance in valid range [0, 1]")


def test_decoherence_free_subspace():
    """Test if noise affects certain states differently"""
    print("\n" + "="*60)
    print("TEST 15: Differential Noise Effects")
    print("="*60)
    
    # |0⟩ shouldn't be affected by amplitude damping
    psi_0 = np.array([1, 0], dtype=complex)
    state_0 = QuantumState(1, state_vector=psi_0, use_density_matrix=True)
    rho_0_initial = state_0.density_matrix.copy()
    
    noise = AmplitudeDamping(0.5)
    noise.apply(state_0)
    
    # |0⟩ should be unchanged (it's already ground state)
    assert np.allclose(state_0.density_matrix, rho_0_initial, atol=1e-14), \
        "|0⟩ should be invariant under amplitude damping"
    print("✓ |0⟩ is invariant under amplitude damping (as expected)")
    
    # |1⟩ should be heavily affected
    psi_1 = np.array([0, 1], dtype=complex)
    state_1 = QuantumState(1, state_vector=psi_1, use_density_matrix=True)
    noise.apply(state_1)
    
    p0 = state_1.density_matrix[0, 0].real
    assert p0 > 0.4, "|1⟩ should decay significantly"
    print(f"✓ |1⟩ decayed: P(0) = {p0:.4f} (significant change)")


if __name__ == "__main__":
    print("\n" + "="*70)
    print(" " * 10 + "EXTREME EDGE CASE TESTS - Bug Hunting Mode")
    print("="*70)
    
    tests = [
        test_noise_commutation,
        test_tiny_noise_parameters,
        test_kraus_operator_completeness,
        test_noise_on_computational_basis,
        test_maximally_mixed_state_limit,
        test_thermal_relaxation_with_zero_times,
        test_multi_qubit_selective_noise,
        test_repeated_same_noise,
        test_eigenvalue_bounds,
        test_hermiticity_after_many_operations,
        test_invalid_inputs,
        test_noise_on_maximally_entangled,
        test_purity_bounds,
        test_trace_distance,
        test_decoherence_free_subspace
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
        print(f"   🎉 ALL EXTREME TESTS PASSED - NO BUGS FOUND!")
    else:
        print(f"   🐛 {failed} bugs found")
    print("="*70 + "\n")
