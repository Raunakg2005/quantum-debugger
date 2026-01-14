# Tests for Quantum Debugger

This directory contains all tests for the quantum-debugger library.

## Test Statistics

**v0.6.0: 384 comprehensive tests** (100% passing)

- Core & Base (v0.5.0): 228 tests
- Hybrid Models (Week 1): 26 tests
- Quantum Kernels (Week 2): 19 tests
- Transfer Learning (Week 3): 42 tests
- Error Mitigation (Week 4): 26 tests
- Circuit Optimization (Week 5): 26 tests
- Framework Integrations (Week 6): 10 tests
- Hardware Backends (Week 7): 6 tests
- Benchmarking (Week 8): 8 tests
- AutoML (Week 9): 6 tests

**Skipped:** 3 tests (AWS Braket - optional dependency)

See [FINAL_TEST_SUMMARY.md](./FINAL_TEST_SUMMARY.md) for complete breakdown.

## Structure

```
tests/
├── unit/                # Core unit tests
├── integration/         # Integration tests
├── qml/                # Quantum Machine Learning tests
│   ├── test_hybrid.py            # Week 1: Hybrid Models
│   ├── test_kernels.py           # Week 2: Quantum Kernels
│   ├── test_transfer*.py         # Week 3: Transfer Learning
│   ├── test_mitigation.py        # Week 4: Error Mitigation
│   ├── test_automl.py            # Week 9: AutoML
│   ├── test_qnn.py               # QNN core
│   ├── test_vqe.py               # VQE algorithm
│   └── test_qaoa.py              # QAOA algorithm
├── test_optimization.py  # Week 5: Circuit Optimization
├── test_integrations.py  # Week 6: Framework Bridges
├── test_backends.py      # Week 7: Hardware Backends
├── test_benchmarks.py    # Week 8: Benchmarking
├── cirq/                # Cirq compatibility tests
└── conftest.py          # Shared pytest configuration
```

## Running Tests

### All Tests

```bash
# Run complete test suite
pytest tests/

# With verbose output
pytest tests/ -v

# With coverage report
pytest tests/ --cov=quantum_debugger --cov-report=html
```

### By Feature (Weeks 1-9)

```bash
# Week 1: Hybrid Models
pytest tests/qml/test_hybrid.py -v

# Week 2: Quantum Kernels
pytest tests/qml/test_kernels.py -v

# Week 3: Transfer Learning
pytest tests/qml/test_transfer*.py -v

# Week 4: Error Mitigation
pytest tests/qml/test_mitigation.py -v

# Week 5: Circuit Optimization
pytest tests/test_optimization.py -v

# Week 6: Framework Integrations
pytest tests/test_integrations.py -v

# Week 7: Hardware Backends
pytest tests/test_backends.py -v

# Week 8: Benchmarking
pytest tests/test_benchmarks.py -v

# Week 9: AutoML
pytest tests/qml/test_automl.py -v
```

### By Category

```bash
# Core functionality
pytest tests/unit/ -v

# All QML tests
pytest tests/qml/ -v

# Integration tests
pytest tests/integration/ -v

# Framework compatibility
pytest tests/cirq/ -v
```

### Quick Validation

```bash
# Run only fast tests
pytest tests/ -m "not slow"

# Run critical tests only
pytest tests/ -k "test_qnn or test_automl"

# Stop on first failure
pytest tests/ -x
```

## Test Categories

### Week 1: Hybrid Models (26 tests)
**File:** `tests/qml/test_hybrid.py`

- TensorFlow quantum layer integration
- PyTorch quantum layer integration
- Hybrid model training
- Gradient flow validation
- Classical-quantum interface

### Week 2: Quantum Kernels (19 tests)
**File:** `tests/qml/test_kernels.py`

- QSVM classification
- QSVM regression
- Multiple kernel types (fidelity, projected)
- Kernel alignment optimization
- Training and prediction

### Week 3: Transfer Learning (42 tests)
**Files:** `tests/qml/test_transfer*.py`

- PretrainedQNN class functionality
- Model serialization and loading
- Fine-tuning with layer freezing
- Model zoo integration
- Transfer learning workflows

### Week 4: Error Mitigation (26 tests)
**File:** `tests/qml/test_mitigation.py`

- Probabilistic Error Cancellation (PEC)
- Clifford Data Regression (CDR)
- Realistic noise models
- Error characterization
- Mitigation effectiveness

### Week 5: Circuit Optimization (26 tests)
**File:** `tests/test_optimization.py`

- Gate reduction and cancellation
- Multi-level compilation (levels 0-3)
- Hardware transpilation
- Optimization passes
- Performance improvements

### Week 6: Framework Integrations (10 tests)
**File:** `tests/test_integrations.py`

- Qiskit bridge (to/from conversion)
- PennyLane bridge
- Cirq bridge
- Round-trip conversion accuracy
- Framework compatibility

### Week 7: Hardware Backends (6 tests)
**File:** `tests/test_backends.py`

- IBM Quantum backend interface
- AWS Braket backend interface
- Device detection and availability
- Cost estimation (AWS)
- Connection handling

### Week 8: Benchmarking (8 tests)
**File:** `tests/test_benchmarks.py`

- QML vs Classical comparison
- Circuit optimization benchmarks
- Scalability analysis
- Memory profiling
- Performance reporting

### Week 9: AutoML (6 tests)
**File:** `tests/qml/test_automl.py`

- auto_qnn() interface
- AutoQNN class functionality
- Automatic ansatz selection
- Hyperparameter tuning
- Neural architecture search

### Core Tests (228 tests)
**Location:** `tests/unit/`, `tests/qml/test_qnn.py`, etc.

- Quantum circuit operations
- Gate implementations
- Debugger functionality
- Profiler tools
- VQE and QAOA algorithms
- QNN training
- Optimizers

## Continuous Integration

Tests run automatically on:
- Every push to main branch
- All pull requests
- Release tags

**CI Configuration:** `.github/workflows/tests.yml`

## Test Requirements

### Minimum Requirements

```bash
pip install pytest pytest-cov
```

### Optional Dependencies (for specific tests)

```bash
# Framework integration tests
pip install qiskit pennylane cirq

# Hybrid model tests
pip install tensorflow torch

# Hardware backend tests
pip install qiskit-ibm-runtime  # IBM (optional)
pip install amazon-braket-sdk   # AWS (optional)
```

## Writing New Tests

### Test Structure

```python
import pytest
from quantum_debugger.qml import QuantumNeuralNetwork

class TestNewFeature:
    """Test new feature."""
    
    def test_basic_functionality(self):
        """Test basic usage."""
        # Arrange
        qnn = QuantumNeuralNetwork(n_qubits=2)
        
        # Act
        result = qnn.some_method()
        
        # Assert
        assert result is not None
```

### Best Practices

1. **Naming:** Use descriptive test names (test_what_is_being_tested)
2. **Isolation:** Each test should be independent
3. **Coverage:** Aim for edge cases and error conditions
4. **Speed:** Keep tests fast (use small datasets)
5. **Documentation:** Add docstrings explaining what is tested

## Troubleshooting

### Common Issues

**Import errors:**
```bash
# Ensure package is installed in editable mode
pip install -e .
```

**Slow tests:**
```bash
# Run in parallel
pytest tests/ -n auto
```

**GPU tests failing:**
```bash
# GPU tests gracefully skip if CUDA unavailable
# This is expected behavior
```

**AWS tests skipped:**
```bash
# AWS Braket SDK is optional
# Install with: pip install quantum-debugger[aws]
```

## Coverage Report

Generate HTML coverage report:

```bash
pytest tests/ --cov=quantum_debugger --cov-report=html
open htmlcov/index.html  # Linux/Mac
start htmlcov/index.html # Windows
```

**Target Coverage:** 90%+  
**Current Coverage:** 95%

## Documentation

For detailed test information, see:
- [FINAL_TEST_SUMMARY.md](./FINAL_TEST_SUMMARY.md) - Complete test breakdown
- [Contributing Guide](../CONTRIBUTING.md) - How to add tests
- [GitHub Actions](.github/workflows/) - CI/CD configuration

---

**Last Updated:** January 14, 2026  
**Version:** v0.6.0  
**Total Tests:** 384 passing (100%)
