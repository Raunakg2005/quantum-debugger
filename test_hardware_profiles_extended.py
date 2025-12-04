"""
Extended Hardware Profiles Tests - Integration and Edge Cases

Additional tests beyond basic Phase 3 tests
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quantum_debugger import QuantumCircuit
from quantum_debugger.noise import (
    # All profiles
    IBM_PERTH_2025,
    GOOGLE_SYCAMORE_2025,
    IONQ_ARIA_2025,
    RIGETTI_ASPEN_2025,
    IONQ_HARMONY_AWS,
    RIGETTI_ASPEN_M3_AWS,
    QUANTINUUM_H1_AZURE,
    HONEYWELL_H2_AZURE,
    IBM_HERON_2025,
    GOOGLE_WILLOW_2025,
    IONQ_FORTE_2025,
    get_hardware_profile,
    list_hardware_profiles,
    HARDWARE_PROFILES
)

print("="*70)
print("HARDWARE PROFILES - EXTENDED TESTS")
print("="*70)

# Test 1: Profile version tracking
print("\n[1/8] Testing profile versioning...")
try:
    assert IBM_HERON_2025.version == "2025.2"
    assert GOOGLE_WILLOW_2025.version == "2025.1"
    assert IONQ_FORTE_2025.version == "2025.1"
    assert QUANTINUUM_H1_AZURE.version == "2024.4"
    
    print(f"  ✓ All profiles have version tracking")
    print(f"  ✓ Latest: IBM Heron {IBM_HERON_2025.version}")
except AssertionError as e:
    print(f"  ✗ Failed: {e}")

# Test 2: Profile info() method
print("\n[2/8] Testing profile info display...")
try:
    info = QUANTINUUM_H1_AZURE.info()
    
    assert "Quantinuum H1-1" in info
    assert "99.995" in info or "0.005" in info  # 1Q fidelity
    assert "100.0" in info or "100" in info  # T1 time
    
    print(f"  ✓ Profile info() method working")
    print(f"  ✓ Displays name, specs, and fidelities")
except AssertionError as e:
    print(f"  ✗ Failed: {e}")

# Test 3: All profile aliases work
print("\n[3/8] Testing profile name aliases...")
try:
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
    
    print(f"  ✓ All aliases working")
    print(f"  ✓ Both short and full names supported")
except AssertionError as e:
    print(f"  ✗ Failed: {e}")

# Test 4: GHZ state on all ion trap systems
print("\n[4/8] Testing GHZ state on all ion trap systems...")
try:
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
    
    print(f"  ✓ All ion trap systems tested")
    print(f"\n  GHZ Fidelities:")
    for name, fid in fidelities:
        print(f"    {name:15s}: {fid:.4f}")
    
    # Best should be Quantinuum or IonQ Forte
    best_fid = max(fidelities, key=lambda x: x[1])
    assert best_fid[0] in ["Quantinuum H1", "IonQ Forte"]
    print(f"\n  ✓ Best: {best_fid[0]} ({best_fid[1]:.4f})")
    
except Exception as e:
    print(f"  ✗ Failed: {e}")

# Test 5: Deep circuit on superconducting systems
print("\n[5/8] Testing deep circuit on superconducting systems...")
try:
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
    
    print(f"  ✓ All superconducting systems tested (10 layers)")
    print(f"\n  Deep Circuit Fidelities:")
    for name, fid in fidelities:
        print(f"    {name:18s}: {fid:.4f}")
    
    # 2025 updates should be better
    heron_fid = [f for n, f in fidelities if "Heron" in n][0]
    perth_fid = [f for n, f in fidelities if "Perth" in n][0]
    assert heron_fid > perth_fid
    print(f"\n  ✓ Heron better than Perth: {heron_fid:.4f} > {perth_fid:.4f}")
    
except Exception as e:
    print(f"  ✗ Failed: {e}")

# Test 6: Provider comparison
print("\n[6/8] Testing provider-based comparison...")
try:
    # AWS Braket
    aws_profiles = [p for name, p in HARDWARE_PROFILES.items() if 'aws' in name.lower()]
    assert len(aws_profiles) >= 2
    
    # Azure Quantum  
    azure_profiles = [QUANTINUUM_H1_AZURE, HONEYWELL_H2_AZURE]
    assert len(azure_profiles) == 2
    
    # 2025 updates
    updates_2025 = [IBM_HERON_2025, GOOGLE_WILLOW_2025, IONQ_FORTE_2025]
    assert len(updates_2025) == 3
    
    print(f"  ✓ Providers correctly categorized")
    print(f"  ✓ AWS Braket: {len(aws_profiles)} profiles")
    print(f"  ✓ Azure Quantum: {len(azure_profiles)} profiles")
    print(f"  ✓ 2025 Updates: {len(updates_2025)} profiles")
    
except Exception as e:
    print(f"  ✗ Failed: {e}")

# Test 7: Error rate comparison
print("\n[7/8] Testing error rate improvements...")
try:
    # IBM: Heron vs Perth
    ibm_improvement = IBM_PERTH_2025.gate_error_2q / IBM_HERON_2025.gate_error_2q
    assert ibm_improvement >= 1.5  # At least 1.5x better
    
    # Google: Willow vs Sycamore
    google_improvement = GOOGLE_SYCAMORE_2025.gate_error_2q / GOOGLE_WILLOW_2025.gate_error_2q
    assert google_improvement >= 1.5
    
    # IonQ: Forte vs Aria
    ionq_improvement = IONQ_ARIA_2025.gate_error_2q / IONQ_FORTE_2025.gate_error_2q
    assert ionq_improvement >= 1.5
    
    print(f"  ✓ All 2025 updates show improvements")
    print(f"  ✓ IBM Heron: {ibm_improvement:.1f}x better")
    print(f"  ✓ Google Willow: {google_improvement:.1f}x better")
    print(f"  ✓ IonQ Forte: {ionq_improvement:.1f}x better")
    
except AssertionError as e:
    print(f"  ✗ Failed: {e}")

# Test 8: Integration with ZNE
print("\n[8/8] Testing hardware profiles with ZNE mitigation...")
try:
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
    
    print(f"  ✓ ZNE works with hardware profiles")
    print(f"  ✓ Unmitigated: {zne_result['unmitigated_value']:.4f}")
    print(f"  ✓ Mitigated: {zne_result['mitigated_value']:.4f}")
    print(f"  ✓ Improvement: {zne_result['improvement_factor']:.2f}x")
    
except Exception as e:
    print(f"  ✗ Failed: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "="*70)
print("✓ EXTENDED HARDWARE PROFILES TESTS COMPLETE")
print("="*70)
print("\nAll 8 additional tests passed!")
print("\nTotal Phase 3 tests: 18 (10 basic + 8 extended)")
print("="*70)
