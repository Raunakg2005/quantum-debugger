# Changelog

All notable changes to QuantumDebugger will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.2] - 2025-12-22

### Added
- **Complete pytest migration**: All 200 legacy script-style tests converted to pytest format
- **Hardware profiles extended**: AWS Braket, Azure Quantum provider support
- **2025 hardware updates**: IBM Heron, Google Willow, IonQ Forte profiles
- **Advanced backend tests**: 8 edge case and performance tests
- **GPU backend support**: CuPy backend availability testing
- **Enhanced test coverage**: 656 comprehensive tests (all passing ✅)

### Changed
- Migrated all legacy test files from script execution to pytest format
- Updated test structure for better CI/CD compatibility
- Enhanced backend validation with 6 comprehensive backend tests
- Improved hardware profile testing (18 tests total)

### Fixed
- Test suite compatibility issues
- Backend detection for GPU/CuPy
- Hardware profile version tracking

### Documentation
- Updated README.md with v0.4.2 features and test count
- Added comprehensive testing section in README
- Created FINAL_TEST_SUMMARY.md with complete 656 test breakdown
- Fixed all documentation links (tutorials, examples, LICENSE)
- Updated version numbers across all files

### Testing
- **656 total tests** (all passing ✅)
- All script-style tests converted to pytest
- Complete test coverage documentation

## [0.4.1] - 2024-12-XX

### Added
- Additional QML features and optimizations
- Performance improvements

## [0.4.0] - 2024-12-XX

### Added
- **Quantum Machine Learning Module**
- Parameterized gates (RX, RY, RZ with trainable parameters)
- VQE algorithm for molecular chemistry
- QAOA for combinatorial optimization
- Training framework with 4 optimizers (Adam, SGD, SPSA, RMSprop)
- Gradient computation (parameter shift rule, finite differences)
- 316 comprehensive tests
- 3 tutorials, 4 example scripts

### Changed
- Enhanced circuit profiling
- Improved state visualization

## [0.3.0] - 2024-12-XX

### Added
- Realistic noise models (4 types)
- Hardware profiles (IBM, Google, IonQ, Rigetti)
- Qiskit Aer validation
- 89 new tests

## [0.2.0] - 2024-XX-XX

### Added
- Bidirectional circuit conversion with Qiskit
- CP gate support
- 12-qubit support

## [0.1.1] - 2024-12-03

### Fixed
- Fixed SWAP gate matrix for little-endian qubit ordering
- Fixed CNOT gate matrix for little-endian qubit ordering
- Fixed Toffoli gate matrix for little-endian qubit ordering
- Fixed entanglement detection for Bell states
- Rewrote multi-qubit gate expansion algorithm using tensor products

### Added
- 69 comprehensive tests (100% pass rate)
- Test suites: quickstart, advanced, comprehensive, extreme, validation, production, edge cases
- Numerical stability tests (100+ consecutive operations)
- Quantum mechanics validation tests
- Production readiness tests

### Changed
- Improved gate expansion algorithm for better accuracy
- Enhanced test coverage to 69 tests across 7 test suites

## [0.1.0] - 2024-11-30

### Added
- Initial release
- Core quantum state representation
- 15+ quantum gates (H, X, Y, Z, S, T, RX, RY, RZ, PHASE, CNOT, CZ, SWAP, Toffoli)
- Step-through debugger with breakpoints
- Circuit profiler with optimization suggestions
- State visualization tools
- Bloch sphere representation
- Support for up to 15 qubits
- Example circuits and demos
- Comprehensive documentation
