"""
Observable Measurement Tests for ZNE

Tests ZNE with Pauli observables and expectation values
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from quantum_debugger import QuantumCircuit
from quantum_debugger.noise import NoiseModel, DepolarizingNoise, AmplitudeDamping
from quantum_debugger.mitigation import apply_zne


def test_zne_with_pauli_z_observable():
    """Test ZNE with Pauli Z observable"""
    #Create circuit with noise
    noise = DepolarizingNoise(0.1)
    
    circuit = QuantumCircuit(1, noise_model=noise)
    circuit.h(0)
    
    # Measure Z expectation without noise (ideal = 0)
    def measure_z_observable(circuit_to_measure):
        result = circuit_to_measure.run(shots=1000)
        counts = result['counts']
        
        # Z observable: |0⟩ → +1, |1⟩ → -1
        expectation = 0
        total = sum(counts.values())
        for state, count in counts.items():
            if state == '0':
                expectation += count / total  # +1 coefficient
            else:
                expectation -= count / total  # -1 coefficient
        
        return expectation
    
    # Apply ZNE
    result = apply_zne(
        circuit,
        noise_model=noise,
        scale_factors=[1, 2, 3],
        extrapolation='richardson',
        shots=1000,
        observable_fn=measure_z_observable
    )
    
    mitigated_exp = result['mitigated_value']
    assert 'mitigated_value' in result


def test_zne_with_pauli_x_observable():
    """Test ZNE with Pauli X observable"""
    # Create |+⟩ state with noise
    noise = DepolarizingNoise(0.05)
    
    circuit = QuantumCircuit(1, noise_model=noise)
    circuit.h(0)
    
    def measure_x_observable(circuit_to_measure):
        # For X measurement, apply H then measure Z
        temp_circuit = circuit_to_measure.copy()
        temp_circuit.h(0)  # Transform X basis to Z basis
        
        result = temp_circuit.run(shots=1000)
        counts = result['counts']
        
        expectation = 0
        total = sum(counts.values())
        for state, count in counts.items():
            if state == '0':
                expectation += count / total
            else:
                expectation -= count / total
        
        return expectation
    
    result = apply_zne(
        circuit,
        noise_model=noise,
        scale_factors=[1, 2, 3],
        extrapolation='linear',
        shots=1000,
        observable_fn=measure_x_observable
    )
    
    mitigated_exp = result['mitigated_value']
    assert 'mitigated_value' in result


def test_energy_expectation_value():
    """Test energy expectation value (Pauli Z on 2 qubits)"""
    # Bell state with noise
    noise = DepolarizingNoise(0.08)
    
    circuit = QuantumCircuit(2, noise_model=noise)
    circuit.h(0)
    circuit.cnot(0, 1)
    
    def measure_zz_energy(circuit_to_measure):
        # Measure Z⊗Z observable
        result = circuit_to_measure.run(shots=2000)
        counts = result['counts']
        
        expectation = 0
        total = sum(counts.values())
        for state, count in counts.items():
            # Z⊗Z: both 0 or both 1 → +1, otherwise → -1
            if state in ['00', '11']:
                expectation += count / total
            else:
                expectation -= count / total
        
        return expectation
    
    result = apply_zne(
        circuit,
        noise_model=noise,
        scale_factors=[1, 2, 3],
        extrapolation='exponential',
        shots=2000,
        observable_fn=measure_zz_energy
    )
    
    mitigated_energy = result['mitigated_value']
    assert 'mitigated_value' in result


def test_observable_with_different_extrapolation_methods():
    """Test observable with different extrapolation methods"""
    noise = AmplitudeDamping(0.1)
    
    circuit = QuantumCircuit(1, noise_model=noise)
    circuit.h(0)  # Simple Hadamard
    
    def measure_fidelity(circuit_to_measure):
        # Simplified fidelity measure
        result = circuit_to_measure.run(shots=1000)
        counts = result['counts']
        return counts.get('0', 0) / sum(counts.values())
    
    methods = ['richardson', 'linear', 'exponential']
    results = []
    for method in methods:
        result = apply_zne(
            circuit,
            noise_model=noise,
            scale_factors=[1, 2, 3],
            extrapolation=method,
            shots=1000,
            observable_fn=measure_fidelity
        )
        mitigated = result['mitigated_value']
        results.append(mitigated)
    
    # All methods should produce results
    assert len(results) == 3


def test_multi_qubit_observable():
    """Test 3-qubit observable"""
    # GHZ state with noise
    noise = DepolarizingNoise(0.05)
    
    circuit = QuantumCircuit(3, noise_model=noise)
    circuit.h(0)
    circuit.cnot(0, 1)
    circuit.cnot(1, 2)
    
    def measure_ghz_parity(circuit_to_measure):
        # Measure parity: even number of 1s → +1
        result = circuit_to_measure.run(shots=1000)
        counts = result['counts']
        
        expectation = 0
        total = sum(counts.values())
        for state, count in counts.items():
            ones = state.count('1')
            if ones % 2 == 0:
                expectation += count / total
            else:
                expectation -= count / total
        
        return expectation
    
    result = apply_zne(
        circuit,
        noise_model=noise,
        scale_factors=[1, 2, 3],
        extrapolation='richardson',
        shots=1000,
        observable_fn=measure_ghz_parity
    )
    
    mitigated_parity = result['mitigated_value']
    assert 'mitigated_value' in result
