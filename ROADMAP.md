# Roadmap

The direction for QuantumDebugger through v1.2. Every feature is genuinely
gate-based and verified against a known outcome (exact diagonalization, an analytic
formula, brute force, or the state-vector simulator) — depth and correctness over a
long list of half-working stubs. Items move as they land; this is intent, not a
contract.

## 0.7.0 — released
A large, genuine quantum-algorithms library (`quantum_debugger.algorithms`): Shor
factoring, Simon, Grover (+ SAT solver + adaptive minimization), QFT, phase
estimation (+ iterative + arbitrary-operator spectroscopy), quantum error correction
(3-qubit + 9-qubit Shor code), a Clifford/stabilizer simulator, Trotter–Suzuki
simulation, a machine-precision VQE ground-state solver, gate decomposition
(ZYZ/ABC/KAK) and multi-controlled synthesis, quantum arithmetic (Fourier +
ripple-carry adders), teleportation / superdense coding / entanglement swapping,
Bell–CHSH & GHZ–Mermin nonlocality, GHZ metrology, BB84 QKD, and state tomography —
alongside the existing QML/QRL suite.

## 0.8.0 — arithmetic, stabilizer completeness & primitives
- Quantum multiplier and ripple-carry subtractor ✅
- Stabilizer simulator: Pauli expectation values, S-dagger, state-vector bridge,
  copy/sample ✅
- Scalable graph / cluster states in the stabilizer engine
- Controlled arithmetic building blocks; more state preparation
- Random Clifford circuit generation

## 0.9.0 — open quantum systems & noise
- Unified density-matrix simulator: apply unitaries and Kraus channels, partial
  trace, purity, fidelity, expectation values
- Noise-channel library (depolarizing, amplitude/phase damping, Pauli, bit/phase
  flip) with verified T1/T2 decay and channel fidelities
- Lindblad / master-equation evolution; noisy QEC logical-error curves; process
  tomography

## 1.0.0 — fault tolerance & advanced QEC (stable-API milestone)
- CSS codes (Steane [[7,1,3]], the 5-qubit perfect code) and surface / toric codes
  at distance 3+
- Syndrome decoders (lookup / minimum-weight matching), logical gates, magic-state
  distillation
- Verified: logical error rate below threshold; arbitrary single-qubit error
  correction on the larger codes

## 1.1.0 — advanced algorithms & applications
- Quantum chemistry: molecular Hamiltonians, a UCCSD-style ansatz, VQE dissociation
  curves checked against exact diagonalization
- Quantum linear algebra: block encoding and quantum singular value transformation
  (QSVT); Hamiltonian simulation via qubitization
- QML advances (quantum kernels / QSVM, quantum Boltzmann machines) and more
  optimization applications (QAOA warm-start, graph coloring, portfolio)

## 1.2.0 — scale, performance & ecosystem
- Tensor-network (MPS) simulator for larger low-entanglement circuits
- Circuit optimization / transpilation passes; OpenQASM 3 import/export
- Performance work (sparse operations, GPU and coverage improvements) and
  benchmarking
