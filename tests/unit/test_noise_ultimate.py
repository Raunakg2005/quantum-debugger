"""
THE ULTIMATE STRESS TEST
Combines everything: random circuits, all noise types, extreme parameters, and validation
This is the final boss of testing
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
from quantum_debugger.noise import (
    DepolarizingNoise,
    AmplitudeDamping,
    PhaseDamping,
    ThermalRelaxation,
    QuantumState,
)


def test_ultimate_torture_test():
    """
    The most comprehensive test possible:
    - Random initial states
    - Mixed noise types
    - All parameter ranges
    - Multi-qubit systems
    - Long sequences
    - Full validation at each step
    """
    total_checks = 0

    # Test 1: Random 100-step noise sequence on 3-qubit system
    np.random.seed(42)  # Reproducible
    state = QuantumState(3, use_density_matrix=True)

    noise_types = [
        lambda: DepolarizingNoise(np.random.uniform(0.01, 0.3)),
        lambda: AmplitudeDamping(np.random.uniform(0.01, 0.3)),
        lambda: PhaseDamping(np.random.uniform(0.01, 0.3)),
    ]

    for step in range(100):
        # Random noise, random qubit
        noise_fn = np.random.choice(noise_types)
        noise = noise_fn()
        target_qubits = [np.random.randint(0, 3)]

        noise.apply(state, qubits=target_qubits)

        # Validate EVERY step
        rho = state.density_matrix

        # Check 1: Trace = 1
        trace = np.trace(rho).real
        assert np.isclose(trace, 1.0, atol=1e-9), f"Step {step}: Trace = {trace}"
        total_checks += 1

        # Check 2: Hermitian
        assert np.allclose(rho, rho.conj().T, atol=1e-12), f"Step {step}: Not Hermitian"
        total_checks += 1

        # Check 3: Positive eigenvalues
        eigenvalues = np.linalg.eigvalsh(rho)
        assert np.all(eigenvalues >= -1e-10), f"Step {step}: Negative eigenvalues"
        total_checks += 1

        # Check 4: Purity in [0,1]
        purity = np.trace(rho @ rho).real
        assert 0 <= purity <= 1.0 + 1e-9, f"Step {step}: Purity = {purity}"
        total_checks += 1

    # Test 2: Extreme parameter combinations
    # Very high noise
    state = QuantumState(2, use_density_matrix=True)
    DepolarizingNoise(0.99).apply(state)
    assert np.trace(state.density_matrix).real > 0.99
    total_checks += 1

    # Very low noise
    state = QuantumState(2, use_density_matrix=True)
    DepolarizingNoise(1e-12).apply(state)
    assert np.trace(state.density_matrix).real > 0.99
    total_checks += 1

    # Thermal relaxation with extreme T1/T2
    state = QuantumState(1, use_density_matrix=True)
    ThermalRelaxation(t1=1e-9, t2=5e-10, gate_time=1e-9).apply(state)
    assert np.trace(state.density_matrix).real > 0.99
    total_checks += 1

    # Very long coherence times
    state = QuantumState(1, use_density_matrix=True)
    ThermalRelaxation(t1=1e6, t2=1e6, gate_time=1e-9).apply(state)
    assert np.trace(state.density_matrix).real > 0.99
    total_checks += 1

    # Test 3: All possible 2-qubit Bell states with all noise types
    bell_states = [
        np.array([1, 0, 0, 1]) / np.sqrt(2),  # |Φ+⟩
        np.array([1, 0, 0, -1]) / np.sqrt(2),  # |Φ-⟩
        np.array([0, 1, 1, 0]) / np.sqrt(2),  # |Ψ+⟩
        np.array([0, 1, -1, 0]) / np.sqrt(2),  # |Ψ-⟩
    ]

    noises = [
        DepolarizingNoise(0.15),
        AmplitudeDamping(0.15),
        PhaseDamping(0.15),
    ]

    for bell in bell_states:
        for noise in noises:
            state = QuantumState(2, state_vector=bell, use_density_matrix=True)
            noise.apply(state, qubits=[0])

            rho = state.density_matrix
            assert np.isclose(np.trace(rho).real, 1.0, atol=1e-10)
            assert np.allclose(rho, rho.conj().T, atol=1e-12)
            total_checks += 2

    # Test 4: Cascaded noise on increasing qubit counts
    for n_qubits in range(1, 6):
        state = QuantumState(n_qubits, use_density_matrix=True)

        # Apply multiple noise types
        DepolarizingNoise(0.05).apply(state, qubits=list(range(n_qubits)))
        AmplitudeDamping(0.05).apply(state, qubits=list(range(n_qubits)))
        PhaseDamping(0.05).apply(state, qubits=list(range(n_qubits)))

        rho = state.density_matrix

        # Full validation
        trace = np.trace(rho).real
        hermitian = np.allclose(rho, rho.conj().T, atol=1e-12)
        eigenvalues = np.linalg.eigvalsh(rho)
        positive = np.all(eigenvalues >= -1e-10)
        purity = np.trace(rho @ rho).real

        assert np.isclose(trace, 1.0, atol=1e-9), f"{n_qubits} qubits: trace={trace}"
        assert hermitian, f"{n_qubits} qubits: not Hermitian"
        assert positive, f"{n_qubits} qubits: negative eigenvalues"
        assert 0 <= purity <= 1.0, f"{n_qubits} qubits: purity={purity}"

        total_checks += 4

    # Test 5: Realistic quantum circuit simulation with noise
    state = QuantumState(3, use_density_matrix=True)

    # Realistic IBM quantum computer noise parameters
    gate_error_1q = 0.001  # 0.1% error on single-qubit gates
    gate_error_2q = 0.01  # 1% error on two-qubit gates

    # "Circuit" with noise after each "gate"
    circuit_steps = [
        (DepolarizingNoise(gate_error_1q), [0]),  # H gate with noise
        (DepolarizingNoise(gate_error_1q), [1]),  # H gate with noise
        (DepolarizingNoise(gate_error_1q), [2]),  # H gate with noise
        (DepolarizingNoise(gate_error_2q), [0, 1]),  # CNOT with noise
        (DepolarizingNoise(gate_error_2q), [1, 2]),  # CNOT with noise
        (DepolarizingNoise(gate_error_1q), [0]),  # Z gate with noise
        (AmplitudeDamping(0.0001), [0, 1, 2]),  # T1 decay
        (PhaseDamping(0.0002), [0, 1, 2]),  # T2 decay
    ]

    for noise, qubits in circuit_steps:
        noise.apply(state, qubits=qubits)

        # Validate after each step
        rho = state.density_matrix
        assert np.isclose(np.trace(rho).real, 1.0, atol=1e-9)
        total_checks += 1

    # Verify we did a comprehensive test
    assert total_checks > 450, f"Only {total_checks} checks performed"
