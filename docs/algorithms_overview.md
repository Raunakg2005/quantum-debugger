# Algorithms Library Overview

`quantum_debugger.algorithms` is a library of genuine, gate-based quantum
algorithms on the state-vector simulator. Every routine is verified against its
known outcome (exact amplitudes, exact factoring, exact eigenvalues, or a matching
analytic curve). This page indexes the whole library; each entry links to a worked
example in the [Algorithms guide](quantum_algorithms_guide).

```python
from quantum_debugger.algorithms import grover_search, shor_factor, trotter_evolve
```

## Search & oracle algorithms

| Function | What it does |
| --- | --- |
| `grover`, `grover_search`, `optimal_iterations` | Grover unstructured search |
| `grover_solve` | Find an input satisfying an arbitrary boolean predicate (SAT) |
| `grover_minimize` | Durr-Hoyer adaptive minimization of a cost function |
| `amplitude_amplification`, `optimal_amplification_iterations` | Grover for any state prep |
| `bernstein_vazirani` | Recover a hidden bit-string in one query |
| `deutsch` | Deutsch's algorithm: constant vs balanced 1-bit function (1 query) |
| `deutsch_jozsa`, `constant_oracle`, `balanced_oracle` | Constant vs balanced (n-bit) |
| `simon`, `simon_oracle` | Hidden XOR-mask (period) finding |

## Fourier, phase estimation & factoring

| Function | What it does |
| --- | --- |
| `qft`, `apply_qft`, `apply_inverse_qft`, `qft_matrix` | Quantum Fourier transform |
| `estimate_phase`, `phase_estimation_circuit` | QPE on the phase gate |
| `iterative_phase_estimation` | Single-ancilla (Kitaev) QPE |
| `unitary_eigenphase`, `hermitian_eigenvalue` | QPE for arbitrary operators (spectroscopy) |
| `period_finding`, `shor_factor` | Shor's algorithm (period finding + factoring) |
| `quantum_counting`, `amplitude_estimation` | Count marked states / estimate amplitude |

## Simulation & chemistry

| Function | What it does |
| --- | --- |
| `trotter_evolve`, `trotter_circuit` | Trotter-Suzuki Hamiltonian simulation |
| `hamiltonian_matrix`, `pauli_term_matrix` | Build a Hamiltonian from Pauli strings |
| `variational_ground_state` | Hardware-efficient VQE ground-state solver |
| `tfim_hamiltonian`, `heisenberg_hamiltonian` | Ready-made spin Hamiltonians |
| `hhl` | Quantum linear-systems solver |
| `quantum_walk` | Discrete-time coined quantum walk |

## Optimization

| Function | What it does |
| --- | --- |
| `solve_maxcut`, `brute_force_maxcut` | QAOA MaxCut solver + exact reference |
| `grover_minimize` | Grover adaptive minimization |

## Error correction & benchmarking

| Function | What it does |
| --- | --- |
| `bit_flip_code`, `phase_flip_code`, `shor_code` | Stabilizer QEC codes |
| `repetition_code_error_rate` | Logical error rate vs the QEC threshold |
| `randomized_benchmarking`, `single_qubit_clifford_group` | Average gate fidelity |

## Circuit synthesis & arithmetic

| Function | What it does |
| --- | --- |
| `zyz_decompose`, `abc_decomposition` | Single-qubit / controlled-U decomposition |
| `kak_decompose`, `canonical_coordinates` | Two-qubit Cartan (KAK) decomposition |
| `toffoli_gates`, `fredkin_gates`, `mcx_gates` | Multi-controlled gate synthesis |
| `qft_add`, `quantum_adder` | Draper QFT adder (constant / two-register) |
| `qft_subtract`, `quantum_compare` | QFT subtractor and comparator |

## Entanglement, protocols & foundations

| Function | What it does |
| --- | --- |
| `ghz_state`, `w_state`, `graph_state` | Canonical entangled-state preparation |
| `teleport`, `superdense_coding`, `entanglement_swap` | Communication protocols |
| `swap_test` | Estimate the overlap of two states |
| `chsh_value`, `chsh_game`, `correlator`, `bell_state` | Bell inequality + nonlocal game |
| `phase_sensitivity`, `parity_signal`, `quantum_fisher_information` | GHZ metrology |
| `bb84` | BB84 quantum key distribution |

## Quantum Singular Value Transformation (QSVT) & Modern Primitives

| Function | What it does |
| --- | --- |
| `qsp_unitary`, `qsp_response`, `chebyshev_via_qsp`, `signal_operator` | Quantum Signal Processing (1-qubit designable polynomials) |
| `block_encode`, `top_left_block`, `is_block_encoding` | Unitary block encoding of arbitrary matrices |
| `qubitization_walk`, `chebyshev_of_matrix` | Qubitization walk realizing matrix Chebyshev polynomials |
| `lcu_block_encoding`, `lcu_matrix` | Linear Combination of Unitaries (PREPARE / SELECT) |
| `qsvt_transform`, `qsvt_scalar_response` | Quantum Singular Value Transformation (eigenvalue-wise polynomial) |
| `hamiltonian_simulation_qsvt`, `matrix_function_chebyshev` | Real-time unitary simulation and smooth Chebyshev matrix functions |
| `solve_linear_system_qsvt`, `matrix_inverse_qsvt` | Quantum linear systems solver ($A x = b$) via polynomial inversion |
| `matrix_sign_qsvt`, `spectral_projector_qsvt` | Matrix sign function and spectral cut projections |
| `matrix_sqrt_qsvt`, `matrix_power_qsvt`, `matrix_exp_qsvt` | Fractional/negative matrix powers and matrix exponentials |
| `ground_state_projector_qsvt`, `gibbs_state_qsvt` | Low-energy ground state filtering and thermal states |
| `spectral_moments`, `density_of_states_kpm` | Kernel Polynomial Method (KPM) moment estimation and DOS |
| `eigenvalue_count_in_interval`, `trace_of_function` | Interval eigenvalue counting and trace estimation |
| `amplitude_amplification_qsvt` | Grover amplitude amplification as scalar QSVT |

See the [QSVT Guide](qsvt_guide) for detailed theory and examples.

## Related modules

- `quantum_debugger.mps.MPS` — Matrix Product State simulator (hundreds of qubits).
- `quantum_debugger.stabilizer.StabilizerSimulator` — Clifford tableau simulator (hundreds of qubits).
- `quantum_debugger.density_matrix.DensityMatrix` — Open quantum systems and Lindblad dynamics.
- `quantum_debugger.tomography.state_tomography` — reconstruct a density matrix.
- `quantum_debugger.qml` — variational QML/QRL (QNN, VQE, QAOA, autoencoder, QCNN,
  policy gradient, DQN, actor-critic, and more).
