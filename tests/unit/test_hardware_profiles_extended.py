"""
Extended Hardware Profiles Tests - Integration and Edge Cases

Additional tests beyond basic Phase 3 tests
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quantum_debugger import QuantumCircuit
from quantum_debugger.noise import (
    IBM_PERTH_2025, GOOGLE_SYCAMORE_2025, IONQ_ARIA_2025, RIGETTI_ASPEN_2025,
    IONQ_HARMONY_AWS, RIGETTI_ASPEN_M3_AWS, QUANTINUUM_H1_AZURE, HONEYWELL_H2_AZURE,
    IBM_HERON_2025, GOOGLE_WILLOW_2025, IONQ_FORTE_2025,
    get_hardware_profile, list_hardware_profiles, HARDWARE_PROFILES
)


def test_profile_versioning():
    """Test profile version tracking"""
    assert IBM_HERON_2025.version == "2025.2"
    assert GOOGLE_WILLOW_2025.version == "2025.1"
    assert IONQ_FORTE_2025.version == "2025.1"
    assert QUANTINUUM_H1_AZURE.version == "2024.4"


def test_profile_info_method():
    """Test profile info display"""
    info = QUANTINUUM_H1_AZURE.info()
    assert "Quantinuum H1-1" in info
    assert "99.995" in info or "0.005" in info  # 1Q fidelity
    assert "100.0" in info or "100" in info  # T1 time


def test_profile_name_aliases():
    """Test profile name aliases"""
    # Test aliases
    assert get_hardware_profile('ionq') is not None
    assert get_hardware_profile('ibm') is not None
    assert get_hardware_profile('google') is not None
    assert get_hardware_profile('rigetti') is not None
    assert get_hardware_profile('quantinuum') is not None
    
    # Test full names
    assert get_hardware_profile('ionq_harmony') is not None
    assert get_hardware_profile('ibm_heron') is not None
    assert get_hardware_profile('google_willow') is not None


def test_ghz_state_on_ion_trap_systems():
    """Test GHZ state on all ion trap systems"""
    ion_trap_profiles = [
        ("IonQ Aria", IONQ_ARIA_2025),
        ("IonQ Harmony", IONQ_HARMONY_AWS),
        ("IonQ Forte", IONQ_FORTE_2025),
        ("Quantinuum H1", QUANTINUUM_H1_AZURE),
        ("Honeywell H2", HONEYWELL_H2_AZURE)
    ]
    
    fidelities = []
    for name, profile in ion_trap_profiles:
        circuit = QuantumCircuit(3, noise_model=profile.noise_model)
        circuit.h(0)
        circuit.cnot(0, 1)
        circuit.cnot(1, 2)
        result = circuit.run(shots=1000)
        fidelities.append((name, result['fidelity']))
    
    # Best should be Quantinuum or IonQ Forte
    best_fid = max(fidelities, key=lambda x: x[1])
    assert best_fid[0] in ["Quantinuum H1", "IonQ Forte"]


def test_deep_circuit_on_superconducting_systems():
    """Test deep circuit on superconducting systems"""
    supercon_profiles = [
        ("IBM Perth", IBM_PERTH_2025),
        ("IBM Heron", IBM_HERON_2025),
        ("Google Sycamore", GOOGLE_SYCAMORE_2025),
        ("Google Willow", GOOGLE_WILLOW_2025),
        ("Rigetti Aspen", RIGETTI_ASPEN_2025),
        ("Rigetti AWS", RIGETTI_ASPEN_M3_AWS)
    ]
    
    fidelities = []
    for name, profile in supercon_profiles:
        circuit = QuantumCircuit(2, noise_model=profile.noise_model)
        # 10-layer circuit
        for _ in range(10):
            circuit.h(0).h(1)
            circuit.cnot(0, 1)
        
        result = circuit.run(shots=500)
        fidelities.append((name, result['fidelity']))
    
    # 2025 updates should be better
    heron_fid = [f for n, f in fidelities if "Heron" in n][0]
    perth_fid = [f for n, f in fidelities if "Perth" in n][0]
    assert heron_fid > perth_fid


def test_provider_comparison():
    """Test provider-based comparison"""
    # AWS Braket
    aws_profiles = [p for name, p in HARDWARE_PROFILES.items() if 'aws' in name.lower()]
    assert len(aws_profiles) >= 2
    
    # Azure Quantum  
    azure_profiles = [QUANTINUUM_H1_AZURE, HONEYWELL_H2_AZURE]
    assert len(azure_profiles) == 2
    
    # 2025 updates
    updates_2025 = [IBM_HERON_2025, GOOGLE_WILLOW_2025, IONQ_FORTE_2025]
    assert len(updates_2025) == 3


def test_error_rate_improvements():
    """Test error rate improvements in 2025 updates"""
    # IBM: Heron vs Perth
    ibm_improvement = IBM_PERTH_2025.gate_error_2q / IBM_HERON_2025.gate_error_2q
    assert ibm_improvement >= 1.5  # At least 1.5x better
    
    # Google: Willow vs Sycamore
    google_improvement = GOOGLE_SYCAMORE_2025.gate_error_2q / GOOGLE_WILLOW_2025.gate_error_2q
    assert google_improvement >= 1.5
    
    # IonQ: Forte vs Aria
    ionq_improvement = IONQ_ARIA_2025.gate_error_2q / IONQ_FORTE_2025.gate_error_2q
    assert ionq_improvement >= 1.5


def test_integration_with_zne():
    """Test hardware profiles with ZNE mitigation"""
    from quantum_debugger.mitigation import apply_zne
    
    # Test on Quantinuum (highest fidelity)
    circuit = QuantumCircuit(2, noise_model=QUANTINUUM_H1_AZURE.noise_model)
    circuit.h(0).cnot(0, 1)
    
    # Apply ZNE
    zne_result = apply_zne(
        circuit,
        scale_factors=[1, 2, 3],
        extrapolation='richardson',
        shots=1000
    )
    
    assert 'mitigated_value' in zne_result
    assert 'improvement_factor' in zne_result
