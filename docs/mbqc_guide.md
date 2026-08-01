# Measurement-based quantum computing

In the one-way (measurement-based) model, computation is driven entirely by adaptive single-qubit
measurements on a fixed, highly-entangled cluster/graph state — no unitary gates at run time. This
guide covers graph states and their stabilizers, local complementation, the one-way teleportation
primitive, byproduct corrections, causal flow, and single- and two-qubit gate realizations. Every
construction is checked against the equivalent circuit-model unitary or the stabilizer definition.

All functions live under `quantum_debugger.algorithms.<module>`.

## Graph & cluster states

A graph state is `∏ CZ_ij |+⟩^n`; its stabilizers are `K_v = X_v ∏_{w~v} Z_w`. Local
complementation gives local-Clifford-equivalent graphs.

- `graph_states.graph_state(edges, n)`, `graph_state_stabilizers(edges, n)`,
  `verify_stabilizers(edges, n)`, `linear_cluster_edges(n)`, `cluster_2d_edges(nx, ny)`,
  `star_graph_edges(n)`, `complete_graph_edges(n)`, `local_complementation(edges, v, n)`,
  `local_clifford_equivalent(...)`, `graph_state_entanglement(edges, n)`.

```python
from quantum_debugger.algorithms.graph_states import verify_stabilizers, linear_cluster_edges
verify_stabilizers(linear_cluster_edges(4), 4)   # -> True   (every K_v fixes the cluster state)
```

## The one-way teleportation primitive

Measuring a qubit of a two-qubit cluster in the X-Y plane teleports it through, applying
`X^outcome H R_z(-φ)` — the building block of one-way computation.

- `one_way_computing.teleport_step(psi, phi, outcome)`, `expected_step_unitary(phi, outcome)`,
  `mbqc_rotation(psi, phis, outcomes)`, `expected_rotation_unitary(...)`,
  `byproduct_operator(outcomes)`, `mbqc_identity(...)`, `measurement_probability(...)`,
  `xy_measurement_states(phi)`.

## Two-qubit gates & the native CZ

The one-way CNOT is `(I⊗H) CZ (I⊗H)`; the native entangler is CZ itself.

- `mbqc_two_qubit.verify_cnot_decomposition()`, `mbqc_cnot(psi2)`, `cnot_decomposition()`,
  `native_cz()`, `mbqc_hadamard(psi)`, `hadamard_is_teleport()`.
- `mbqc.cluster_pair(psi_in)`, `mbqc_rotation(psi_in, alpha, correct)`.

```python
from quantum_debugger.algorithms.mbqc_two_qubit import verify_cnot_decomposition, hadamard_is_teleport
verify_cnot_decomposition()   # -> True   ((I⊗H)·CZ·(I⊗H) == CNOT)
hadamard_is_teleport()        # -> True   (an angle-0 teleport step is exactly H)
```

## Measurement calculus & causal flow

Causal flow guarantees a measurement pattern is deterministically runnable, and its depth is the
parallel run time.

- `measurement_calculus.causal_flow(edges, inputs, outputs, n)`,
  `has_flow(edges, inputs, outputs, n)`, `verify_flow(...)`, `pattern_depth(...)`,
  `measurement_pattern(entangle_edges, measured, outputs, angles)`.

```python
from quantum_debugger.algorithms.measurement_calculus import has_flow
from quantum_debugger.algorithms.graph_states import linear_cluster_edges
has_flow(linear_cluster_edges(4), inputs=[0], outputs=[3], n=4)   # -> True
```

## What this is verified against

- Graph states: the stabilizer generators `K_v` all fix the state.
- Teleportation/gates: the realized operation matched to the circuit-model unitary
  (`H`, `R_z`, and `(I⊗H)CZ(I⊗H) = CNOT`) up to Pauli byproducts.
- Causal flow: the flow conditions verified, guaranteeing deterministic execution.
