# Script to batch-mark legacy test files as "to be converted"
# This helps track which files still need pytest conversion

# Files already confirmed working in pytest format:
# - test_backends.py ✅
# - test_backends_fast.py ✅
# - test_backend_integration.py ✅
# - test_parallel.py ✅
# - test_noise.py ✅
# - test_circuit_noise.py ✅
# Plus 14 more that were already pytest format

# Remaining files to convert (22):
REMAINING_FILES = [
    "test_backend_comprehensive.py",
    "test_backends_advanced.py",
    "test_backends_comprehensive.py",
    "test_circuit_noise_advanced.py",
    "test_circuit_noise_unique.py",
    "test_gpu_quick.py",
    "test_hardware_profiles_extended.py",
    "test_hardware_profiles_phase3.py",
    "test_mitigation_comprehensive.py",
    "test_mitigation_final.py",
    "test_mitigation_observables.py",
    "test_mitigation_zne.py",
    "test_noise_advanced.py",
    "test_noise_extreme.py",
    "test_noise_final.py",
    "test_noise_performance.py",
    "test_noise_quantum_info.py",
    "test_noise_ultimate.py",
    "test_qiskit_complex.py",
    "test_qiskit_extreme.py",
    "test_qiskit_ultra.py",
    "test_qml_threading.py",
]

# Current status: 6 done, 22 remaining
# Strategy: Convert in batches by type (backend, noise, mitigation, etc.)
