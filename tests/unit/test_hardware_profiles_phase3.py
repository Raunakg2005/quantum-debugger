"""
Hardware Profiles Phase 3 - Cloud Provider Integration

Tests for AWS Braket, Azure Quantum, and 2025 hardware updates
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quantum_debugger import QuantumCircuit
from quantum_debugger.noise import (
    IONQ_HARMONY_AWS, RIGETTI_ASPEN_M3_AWS,
    QUANTINUUM_H1_AZURE, HONEYWELL_H2_AZURE,
    IBM_HERON_2025, GOOGLE_WILLOW_2025, IONQ_FORTE_2025,
    get_hardware_profile, list_hardware_profiles
)


def test_aws_braket_ionq_harmony():
    """Test AWS Braket - IonQ Harmony"""
    profile = IONQ_HARMONY_AWS
    assert profile.name == "IonQ Harmony (AWS Braket)"
    assert profile.version == "2024.4"
    
    circuit = QuantumCircuit(2, noise_model=profile.noise_model)
    circuit.h(0).cnot(0, 1)
    result = circuit.run(shots=1000)
    assert result['fidelity'] > 0.85


def test_aws_braket_rigetti_aspen():
    """Test AWS Braket - Rigetti Aspen-M-3"""
    profile = RIGETTI_ASPEN_M3_AWS
    assert profile.name == "Rigetti Aspen-M-3 (AWS Braket)"
    assert profile.version == "2024.4"
    
    circuit = QuantumCircuit(2, noise_model=profile.noise_model)
    circuit.h(0).cnot(0, 1)
    result = circuit.run(shots=1000)
    assert 'fidelity' in result


def test_azure_quantum_quantinuum_h1():
    """Test Azure Quantum - Quantinuum H1"""
    profile = QUANTINUUM_H1_AZURE
    assert profile.name == "Quantinuum H1-1 (Azure Quantum)"
    assert profile.version == "2024.4"
    
    circuit = QuantumCircuit(2, noise_model=profile.noise_model)
    circuit.h(0).cnot(0, 1)
    result = circuit.run(shots=1000)
    assert result['fidelity'] > 0.95


def test_azure_quantum_honeywell_h2():
    """Test Azure Quantum - Honeywell H2"""  
    profile = HONEYWELL_H2_AZURE
    assert profile.name == "Honeywell H2 (Azure Quantum)"
    
    circuit = QuantumCircuit(2, noise_model=profile.noise_model)
    circuit.h(0).cnot(0, 1)
    result = circuit.run(shots=1000)
    assert result['fidelity'] > 0.90


def test_2025_update_ibm_heron():
    """Test 2025 Update - IBM Heron"""
    profile = IBM_HERON_2025
    assert profile.name == "IBM Heron (2025)"
    assert profile.version == "2025.2"
    
    # Deep circuit to test improved error rates
    circuit = QuantumCircuit(3, noise_model=profile.noise_model)
    for _ in range(5):
        circuit.h(0).h(1).h(2)
        circuit.cnot(0, 1).cnot(1, 2)
    
    result = circuit.run(shots=1000)
    assert result['fidelity'] > 0.70


def test_2025_update_google_willow():
    """Test 2025 Update - Google Willow"""
    profile = GOOGLE_WILLOW_2025
    assert profile.name == "Google Willow (2025)"
    assert profile.version == "2025.1"
    
    # Test with noise
    circuit = QuantumCircuit(3, noise_model=profile.noise_model)
    for _ in range(5):
        circuit.h(0).h(1).h(2)
        circuit.cnot(0, 1).cnot(1, 2)
    
    result = circuit.run(shots=1000)
    assert result['fidelity'] > 0.65


def test_2025_update_ionq_forte():
    """Test 2025 Update - IonQ Forte"""
    profile = IONQ_FORTE_2025
    assert profile.name == "IonQ Forte (2025)"
    assert profile.version == "2025.1"
    
    circuit = QuantumCircuit(3, noise_model=profile.noise_model)
    circuit.h(0).cnot(0, 1).cnot(1, 2)
    result = circuit.run(shots=1000)
    assert result['fidelity'] > 0.92


def test_profile_retrieval_by_name():
    """Test get_hardware_profile function"""
    # Test get_hardware_profile
    ionq = get_hardware_profile('ionq_harmony')
    assert ionq is not None
    assert ionq.name == "IonQ Harmony (AWS Braket)"
    
    quantinuum = get_hardware_profile('quantinuum')
    assert quantinuum is not None
    assert "Quantinuum" in quantinuum.name
    
    ibm = get_hardware_profile('ibm_heron')
    assert ibm is not None
    assert ibm.name == "IBM Heron (2025)"


def test_profile_listing():
    """Test list_hardware_profiles function"""
    profiles = list_hardware_profiles()
    
    # profiles is a list of profile name strings
    assert any("AWS Braket" in name for name in profiles)
    assert any("Azure Quantum" in name for name in profiles)
    assert any("Heron" in name for name in profiles)
    assert any("Willow" in name for name in profiles)
    assert any("Forte" in name for name in profiles)
    
    # Check count
    assert len(profiles) >= 10


def test_circuit_simulation_with_all_new_profiles():
    """Test circuit simulation with all new profiles"""
    new_profiles = [
        IONQ_HARMONY_AWS,
        RIGETTI_ASPEN_M3_AWS,
        QUANTINUUM_H1_AZURE,
        HONEYWELL_H2_AZURE,
        IBM_HERON_2025,
        GOOGLE_WILLOW_2025,
        IONQ_FORTE_2025
    ]
    
    results = []
    for profile in new_profiles:
        circuit = QuantumCircuit(2, noise_model=profile.noise_model)
        circuit.h(0).cnot(0, 1)
        result = circuit.run(shots=500)
        results.append((profile.name, result['fidelity']))
    
    # All should complete successfully
    assert len(results) == 7
    # All should have reasonable fidelity
    assert all(fid > 0.5 for _, fid in results)
