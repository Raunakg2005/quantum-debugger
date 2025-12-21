"""
Comprehensive Integration Tests for Circuit Noise Simulation

Tests the complete integration of noise models with quantum circuits,
including hardware profiles, composite noise, and realistic scenarios.
"""

import pytest
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
    IONQ_ARIA_2025,
    get_hardware_profile
)


def test_basic_noise_application():
    """Test basic noise reduces fidelity"""
    # Create Bell state circuit
    qc = QuantumCircuit(2, noise_model=DepolarizingNoise(0.05))
    qc.h(0).cnot(0, 1)
    
    results = qc.run(shots=100)
    fidelity = results['fidelity']
    
    # Check that noise reduces fidelity
    assert fidelity < 1.0
    assert fidelity > 0.5


def test_multi_gate_circuit_with_noise():
    """Test multi-gate circuit shows accumulated noise"""
    noise = DepolarizingNoise(0.01)
    
    # Short circuit (2 gates)
    qc_short = QuantumCircuit(1, noise_model=noise)
    qc_short.h(0).x(0)
    results_short = qc_short.run(shots=100)
    
    # Long circuit (10 gates) 
    qc_long = QuantumCircuit(1, noise_model=noise)
    for _ in range(10):
        qc_long.h(0)
    results_long = qc_long.run(shots=100)
    
    fidelity_short = results_short['fidelity']
    fidelity_long = results_long['fidelity']
    
    # Longer circuit should have more noise accumulation
    assert fidelity_long < fidelity_short


def test_hardware_profile_comparison():
    """Test different hardware profiles show different fidelities"""
    # Create same circuit with different hardware
    def create_grover_circuit(noise_model=None):
        qc = QuantumCircuit(2, noise_model=noise_model)
        # Simple Grover-like circuit
        qc.h(0).h(1)
        qc.cz(0, 1)
        qc.h(0).h(1)
        return qc
    
    # Test each hardware profile
    results = {}
    for name, profile in [
        ('IBM', IBM_PERTH_2025),
        ('Google', GOOGLE_SYCAMORE_2025),
        ('IonQ', IONQ_ARIA_2025)
    ]:
        qc = create_grover_circuit(noise_model=profile.noise_model)
        res = qc.run(shots=100)
        results[name] = res['fidelity']
    
    # IonQ should have best fidelity (lowest error rates)
    assert results['IonQ'] >= results['IBM']
    assert results['IonQ'] >= results['Google']


def test_composite_noise():
    """Test composite noise combines multiple sources"""
    # Create composite noise (thermal + depolarizing)
    thermal = ThermalRelaxation(t1=100e-6, t2=80e-6, gate_time=50e-9)
    depol = DepolarizingNoise(0.005)
    composite = CompositeNoise([thermal, depol])
    
    # Test with single noise vs composite
    qc_single = QuantumCircuit(2, noise_model=depol)
    qc_single.h(0).cnot(0, 1)
    results_single = qc_single.run(shots=100)
    
    qc_composite = QuantumCircuit(2, noise_model=composite)
    qc_composite.h(0).cnot(0, 1)
    results_composite = qc_composite.run(shots=100)
    
    fidelity_single = results_single['fidelity']
    fidelity_composite = results_composite['fidelity']
    
    # Composite should have lower fidelity (more noise)
    assert fidelity_composite < fidelity_single


def test_noise_free_vs_noisy():
    """Test noise-free mode still works (backward compatibility)"""
    # Noise-free circuit
    qc_clean = QuantumCircuit(2)
    qc_clean.h(0).cnot(0, 1)
    results_clean = qc_clean.run(shots=1000)
    
    # Noisy circuit
    qc_noisy = QuantumCircuit(2, noise_model=DepolarizingNoise(0.1))
    qc_noisy.h(0).cnot(0, 1)
    results_noisy = qc_noisy.run(shots=1000)
    
    # Noise-free Bell state should only have |00⟩ and |11⟩ outcomes
    total_clean = sum(results_clean['counts'].values())
    valid_outcomes = results_clean['counts'].get('00', 0) + results_clean['counts'].get('11', 0)
    purity = valid_outcomes / total_clean
    
    assert purity > 0.99
    
    # Noisy should have reduced fidelity
    assert 'fidelity' in results_noisy
    assert results_noisy['fidelity'] < 1.0
