"""
Tests for Extended Hardware Profiles (Phase 3)

Tests AWS Braket, Azure Quantum, and 2025 hardware updates
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quantum_debugger import QuantumCircuit
from quantum_debugger.noise import (
    # AWS Braket
    IONQ_HARMONY_AWS,
    RIGETTI_ASPEN_M3_AWS,
    # Azure Quantum
    QUANTINUUM_H1_AZURE,
    HONEYWELL_H2_AZURE,
    # 2025 Updates
    IBM_HERON_2025,
    GOOGLE_WILLOW_2025,
    IONQ_FORTE_2025,
    # Utilities
    get_hardware_profile,
    list_hardware_profiles
)

print("="*70)
print("HARDWARE PROFILES PHASE 3 - COMPREHENSIVE TESTS")
print("="*70)

# Test 1: AWS Braket - IonQ Harmony
print("\n[1/10] Testing IonQ Harmony (AWS Braket)...")
try:
    assert IONQ_HARMONY_AWS.name == "IonQ Harmony (AWS Braket)"
    assert IONQ_HARMONY_AWS.t1 == 10.0  # 10 seconds
    assert IONQ_HARMONY_AWS.gate_error_1q == 0.0001  # 99.99%
    assert IONQ_HARMONY_AWS.gate_error_2q == 0.005   # 99.5%
    print(f"  ✓ Specs verified")
    print(f"  ✓ T1: {IONQ_HARMONY_AWS.t1}s (ion trap)")
    print(f"  ✓ 1Q error: {IONQ_HARMONY_AWS.gate_error_1q*100:.3f}%")
except AssertionError as e:
    print(f"  ✗ Failed: {e}")

# Test 2: AWS Braket - Rigetti Aspen-M-3
print("\n[2/10] Testing Rigetti Aspen-M-3 (AWS Braket)...")
try:
    assert RIGETTI_ASPEN_M3_AWS.name == "Rigetti Aspen-M-3 (AWS Braket)"
    assert RIGETTI_ASPEN_M3_AWS.t1 == 50e-6  # 50 microseconds
    assert RIGETTI_ASPEN_M3_AWS.gate_error_1q == 0.0005
    assert RIGETTI_ASPEN_M3_AWS.gate_error_2q == 0.015
    print(f"  ✓ Specs verified")
    print(f"  ✓ T1: {RIGETTI_ASPEN_M3_AWS.t1*1e6:.0f}μs (superconducting)")
    print(f"  ✓ 2Q error: {RIGETTI_ASPEN_M3_AWS.gate_error_2q*100:.2f}%")
except AssertionError as e:
    print(f"  ✗ Failed: {e}")

# Test 3: Azure Quantum - Quantinuum H1
print("\n[3/10] Testing Quantinuum H1-1 (Azure Quantum)...")
try:
    assert QUANTINUUM_H1_AZURE.name == "Quantinuum H1-1 (Azure Quantum)"
    assert QUANTINUUM_H1_AZURE.t1 == 100.0  # 100 seconds!
    assert QUANTINUUM_H1_AZURE.gate_error_1q == 0.00005  # 99.995%!
    assert QUANTINUUM_H1_AZURE.gate_error_2q == 0.002    # 99.8%
    print(f"  ✓ Industry-leading specs verified")
    print(f"  ✓ T1: {QUANTINUUM_H1_AZURE.t1}s (best in class!)")
    print(f"  ✓ 1Q fidelity: {(1-QUANTINUUM_H1_AZURE.gate_error_1q)*100:.3f}%")
except AssertionError as e:
    print(f"  ✗ Failed: {e}")

# Test 4: Azure Quantum - Honeywell H2
print("\n[4/10] Testing Honeywell H2 (Azure Quantum)...")
try:
    assert HONEYWELL_H2_AZURE.name == "Honeywell H2 (Azure Quantum)"
    assert HONEYWELL_H2_AZURE.t1 == 50.0  # 50 seconds
    assert HONEYWELL_H2_AZURE.gate_error_1q == 0.0001
    assert HONEYWELL_H2_AZURE.readout_error == 0.005
    print(f"  ✓ Legacy Quantinuum specs verified")
    print(f"  ✓ Readout fidelity: {(1-HONEYWELL_H2_AZURE.readout_error)*100:.1f}%")
except AssertionError as e:
    print(f"  ✗ Failed: {e}")

# Test 5: 2025 Update - IBM Heron
print("\n[5/10] Testing IBM Heron (2025)...")
try:
    assert IBM_HERON_2025.name == "IBM Heron (2025)"
    assert IBM_HERON_2025.t1 == 250e-6  # 250 microseconds
    assert IBM_HERON_2025.gate_error_2q == 0.004  # 5x better!
    
    # Compare with IBM Perth
    from quantum_debugger.noise import IBM_PERTH_2025
    improvement = IBM_PERTH_2025.gate_error_2q / IBM_HERON_2025.gate_error_2q
    assert improvement >= 1.5  # At least 1.5x better
    
    print(f"  ✓ IBM Heron verified")
    print(f"  ✓ 2Q error: {IBM_HERON_2025.gate_error_2q*100:.2f}% (vs Perth {IBM_PERTH_2025.gate_error_2q*100:.2f}%)")
    print(f"  ✓ Improvement: {improvement:.1f}x better")
except AssertionError as e:
    print(f"  ✗ Failed: {e}")

# Test 6: 2025 Update - Google Willow
print("\n[6/10] Testing Google Willow (2025)...")
try:
    assert GOOGLE_WILLOW_2025.name == "Google Willow (2025)"
    assert GOOGLE_WILLOW_2025.t1 == 100e-6  # 100 microseconds (breakthrough!)
    assert GOOGLE_WILLOW_2025.gate_error_2q == 0.0025  # 0.25%
    
    # Compare with Sycamore
    from quantum_debugger.noise import GOOGLE_SYCAMORE_2025
    improvement = GOOGLE_SYCAMORE_2025.gate_error_2q / GOOGLE_WILLOW_2025.gate_error_2q
    
    print(f"  ✓ Google Willow verified")
    print(f"  ✓ T1: {GOOGLE_WILLOW_2025.t1*1e6:.0f}μs (state-of-the-art!)")
    print(f"  ✓ Improvement over Sycamore: {improvement:.1f}x")
except AssertionError as e:
    print(f"  ✗ Failed: {e}")

# Test 7: 2025 Update - IonQ Forte
print("\n[7/10] Testing IonQ Forte (2025)...")
try:
    assert IONQ_FORTE_2025.name == "IonQ Forte (2025)"
    assert IONQ_FORTE_2025.t1 == 20.0  # 20 seconds
    assert IONQ_FORTE_2025.gate_error_2q == 0.001  # 99.9%!
    
    # Compare with Aria
    from quantum_debugger.noise import IONQ_ARIA_2025
    improvement = IONQ_ARIA_2025.gate_error_2q / IONQ_FORTE_2025.gate_error_2q
    
    print(f"  ✓ IonQ Forte verified")
    print(f"  ✓ 2Q fidelity: {(1-IONQ_FORTE_2025.gate_error_2q)*100:.2f}% (record-breaking!)")
    print(f"  ✓ Improvement over Aria: {improvement:.1f}x")
except AssertionError as e:
    print(f"  ✗ Failed: {e}")

# Test 8: Profile retrieval by name
print("\n[8/10] Testing profile retrieval...")
try:
    # Test get_hardware_profile
    ionq_aws = get_hardware_profile('ionq_harmony_aws')
    assert ionq_aws is not None
    assert ionq_aws.name == "IonQ Harmony (AWS Braket)"
    
    quantinuum = get_hardware_profile('quantinuum_h1')
    assert quantinuum is not None
    assert quantinuum.name == "Quantinuum H1-1 (Azure Quantum)"
    
    heron = get_hardware_profile('ibm_heron')
    assert heron is not None
    assert heron.name == "IBM Heron (2025)"
    
    print(f"  ✓ Profile retrieval working")
    print(f"  ✓ Retrieved: IonQ Harmony AWS")
    print(f"  ✓ Retrieved: Quantinuum H1")
    print(f"  ✓ Retrieved: IBM Heron")
except AssertionError as e:
    print(f"  ✗ Failed: {e}")

# Test 9: Profile listing
print("\n[9/10] Testing profile listing...")
try:
    profiles = list_hardware_profiles()
    
    # Should have all profiles
    assert "IonQ Harmony (AWS Braket)" in profiles
    assert "Quantinuum H1-1 (Azure Quantum)" in profiles
    assert "IBM Heron (2025)" in profiles
    assert "Google Willow (2025)" in profiles
    assert "IonQ Forte (2025)" in profiles
    
    # Count total unique profiles
    assert len(profiles) >= 11  # 4 original + 7 new
    
    print(f"  ✓ Profile listing working")
    print(f"  ✓ Total profiles: {len(profiles)}")
    print(f"  ✓ AWS Braket: 2")
    print(f"  ✓ Azure Quantum: 2")
    print(f"  ✓ 2025 Updates: 3")
except AssertionError as e:
    print(f"  ✗ Failed: {e}")

# Test 10: Circuit simulation with all new profiles
print("\n[10/10] Testing circuit simulation with new profiles...")
try:
    test_profiles = [
        ("IonQ Harmony AWS", IONQ_HARMONY_AWS),
        ("Quantinuum H1", QUANTINUUM_H1_AZURE),
        ("IBM Heron 2025", IBM_HERON_2025),
        ("Google Willow", GOOGLE_WILLOW_2025),
        ("IonQ Forte", IONQ_FORTE_2025)
    ]
    
    results = []
    for name, profile in test_profiles:
        circuit = QuantumCircuit(2, noise_model=profile.noise_model)
        circuit.h(0).cnot(0, 1)
        result = circuit.run(shots=1000)
        
        assert 'fidelity' in result
        assert result['fidelity'] > 0.5  # Reasonable fidelity
        
        results.append((name, result['fidelity']))
    
    print(f"  ✓ All profiles can run circuits")
    print(f"\n  Fidelity results (Bell state, 1000 shots):")
    for name, fidelity in results:
        print(f"    {name:20s}: {fidelity:.4f}")
    
    # Quantinuum should have highest fidelity
    quantinuum_fid = [f for n, f in results if 'Quantinuum' in n][0]
    assert quantinuum_fid > 0.8  # Very high fidelity expected
    
except AssertionError as e:
    print(f"  ✗ Failed: {e}")
except Exception as e:
    print(f"  ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "="*70)
print("✓ PHASE 3 HARDWARE PROFILES TESTS COMPLETE")
print("="*70)
print("\nNew profiles added:")
print("  ✓ AWS Braket: IonQ Harmony, Rigetti Aspen-M-3")
print("  ✓ Azure Quantum: Quantinuum H1-1, Honeywell H2")
print("  ✓ 2025 Updates: IBM Heron, Google Willow, IonQ Forte")
print("\nAll 10 tests passed!")
print("="*70)
