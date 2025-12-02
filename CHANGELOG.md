# Changelog

All notable changes to QuantumDebugger will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-12-03

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

## [0.1.0] - 2025-11-30

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
