# Tests for Quantum Debugger

This directory contains all tests for the quantum-debugger library.

## Structure

```
tests/
├── unit/              # Unit tests for individual components
├── integration/       # Integration tests
├── qml/              # Quantum Machine Learning tests  
├── cirq/             # Cirq integration tests
└── conftest.py       # Shared pytest configuration
```

## Running Tests

```bash
# Run all tests
pytest tests/

# Run specific category
pytest tests/unit/
pytest tests/qml/
pytest tests/cirq/

# Run with coverage
pytest tests/ --cov=quantum_debugger --cov-report=html

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/qml/test_vqe.py -v
```

## Test Categories

### Unit Tests (`tests/unit/`)
- Core circuit functionality
- Gate operations
- Debugger features
- Profiling tools

### Integration Tests (`tests/integration/`)
- Multi-component workflows
- End-to-end scenarios
- Hardware integration
- Cross-module interactions

### QML Tests (`tests/qml/`)
- VQE algorithm
- QAOA algorithm
- Training framework
- Optimizers
- Parameterized gates
- Regression tests
- Property-based tests

### Cirq Tests (`tests/cirq/`)
- Basic conversion
- Advanced algorithms
- Edge cases
- Stress tests
- Numerical accuracy

## Test Coverage

**v0.4.2: 656 comprehensive tests** (all passing ✅)

- Core: 441 tests
- QML: 139 tests  
- Converted Legacy: 200 tests
- Qiskit Integration: 15 tests

See [FINAL_TEST_SUMMARY.md](./FINAL_TEST_SUMMARY.md) for complete breakdown.
