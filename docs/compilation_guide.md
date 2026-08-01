# Quantum compilation & circuit optimization

The compiler stack that turns an abstract circuit into something a device can run: a small
circuit intermediate representation (IR), peephole optimization passes, qubit routing onto a
limited coupling map, ASAP scheduling, verified gate templates, and commutation analysis. Every
pass is checked to *preserve the circuit unitary* (up to global phase) — correctness is never
traded for a smaller circuit.

All functions live under `quantum_debugger.algorithms.<module>`.

## The circuit IR

- `circuit_ir.op(matrix, qubits)` — build an IR operation; `circuit_unitary(circuit, n_qubits)`,
  `gate_count(circuit)`, `two_qubit_count(circuit)`,
  `circuits_equivalent(c1, c2, n_qubits)` — the correctness oracle every pass is checked against.

## Optimization passes

- `gate_optimization.cancel_inverses(circuit)`, `merge_rotations(circuit, axis_tag)`,
  `remove_identities(circuit)`, `optimize_circuit(circuit)` (the full peephole pass).

```python
from quantum_debugger.algorithms.circuit_ir import op, circuits_equivalent
from quantum_debugger.algorithms.gate_optimization import optimize_circuit
import numpy as np
H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
circuit = [op(H, [0]), op(H, [0])]              # H·H = I
optimized = optimize_circuit(circuit)
circuits_equivalent(circuit, optimized, 1)       # -> True   (unitary preserved)
len(optimized)                                   # -> 0      (cancelled to nothing)
```

## Routing & scheduling

- `qubit_routing.coupling_map(edges, n_qubits)`, `is_executable(circuit, coupling)`,
  `route_linear(circuit, n_qubits)`, `swap_network(perm)`, `permutation_matrix(perm, n_qubits)`.
- `scheduling.asap_layers(circuit, n_qubits)`, `circuit_depth(...)`, `critical_path_length(...)`,
  `circuit_parallelism(...)`, `flatten_layers(layers)`.

## Templates & commutation

Standard decompositions are provided as templates, each verified against its target unitary; the
commutation structure lets passes reorder gates safely.

- `gate_templates.controlled_z_decomposition(...)`, `swap_decomposition(...)`,
  `toffoli_decomposition(...)`, `toffoli_matrix()`, `verify_template(sub, target, n_qubits)`.
- `commutation.operations_commute(op_a, op_b, n_qubits)`, `commutation_graph(circuit, n_qubits)`,
  `commute_forward(circuit, index, n_qubits)`.

```python
from quantum_debugger.algorithms.gate_templates import (
    toffoli_decomposition, toffoli_matrix, verify_template)
sub = toffoli_decomposition(0, 1, 2)             # 6-CNOT Clifford+T template
verify_template(sub, toffoli_matrix(), 3)        # -> True   (matches the CCX unitary)
```

## What this is verified against

- Every optimization/routing pass: `circuits_equivalent` — the composed unitary is unchanged up
  to global phase.
- Templates: `verify_template` matches each decomposition to its exact target unitary (CZ, SWAP,
  Toffoli).
- Scheduling: the ASAP depth equals the critical-path length.
