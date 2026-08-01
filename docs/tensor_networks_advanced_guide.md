# Tensor networks II — TEBD, PEPS, MERA & entanglement scaling

A second tensor-network layer beyond the MPS guide: time evolution and ground states by TEBD,
2D projected entangled-pair states (PEPS), the multi-scale entanglement renormalization ansatz
(MERA), optimal contraction ordering, and the entanglement-scaling laws (area vs volume) that
say *when* a tensor network is efficient. Each routine is checked against an exact contraction,
a closed form, or exact diagonalization.

All functions live under `quantum_debugger.algorithms.<module>`.

## TEBD: time evolution & imaginary-time ground states

Time-evolving block decimation applies two-site Trotter gates to an MPS, truncating the bond
dimension by SVD. Imaginary time cools toward the ground state.

- `tebd.tebd_tfim(n, time, steps, ...)` — real-time TFIM evolution of an MPS.
- `tebd.imaginary_tebd_ground_state(n, j_coupling, field, ...)` — TFIM ground state; returns the
  energy alongside the exact-diagonalization energy and the error.
- `tebd.tebd_magnetization(...)`, `tfim_mps_energy(mps, ...)`, `tfim_bond_gate(...)`.

```python
from quantum_debugger.algorithms.tebd import imaginary_tebd_ground_state
r = imaginary_tebd_ground_state(8, j_coupling=1.0, field=1.0)
r["energy"], r["exact_energy"], round(r["error"], 5)
# -> (-9.836..., -9.837..., ~1e-3)   TEBD vs exact diagonalization
```

## PEPS and the 2D cluster state

- `peps.product_peps(...)`, `peps.contract_2x2(peps)` — exactly contract a 2x2 PEPS to a state
  vector, `peps.bond_dimension(peps)`, `peps.is_product_peps(peps)`.
- `peps.cluster_peps_statevector()` vs `cluster_state_reference()` — the bond-dimension-2 PEPS of
  the 2x2 cluster state, matched against `H^{⊗4}` followed by `CZ` on the grid edges.

## MERA: isometries, disentanglers & scale invariance

- `mera.isometry(...)`, `ternary_isometry(...)`, `disentangler(...)`, `is_isometry(W)`.
- `mera.ascending_superoperator(op, w)` / `descending_superoperator(rho, w)` — flow operators
  and states between scales; `renormalize_operator(op, w, layers)`.
- `mera.causal_cone_width(layers)` — the past causal cone of a binary MERA is a constant 3 sites.

```python
from quantum_debugger.algorithms.mera import causal_cone_width
causal_cone_width(4)   # -> 3   (constant width => efficient contraction)
```

## Contraction ordering

The order in which a tensor network is contracted changes the cost by orders of magnitude; the
optimal order is a matrix-chain dynamic program.

- `tensor_contraction.matrix_chain_left_cost(dims)`, `matrix_chain_optimal_cost(dims)`,
  `matrix_chain_optimal_order(dims)`, `contraction_speedup(dims)`, `contract_pair(A, B, axes)`.

```python
from quantum_debugger.algorithms.tensor_contraction import (
    matrix_chain_left_cost, matrix_chain_optimal_cost, contraction_speedup)
dims = [10, 100, 5, 50, 1]
matrix_chain_left_cost(dims), matrix_chain_optimal_cost(dims)   # -> (8000, 1750)
round(contraction_speedup(dims), 2)                             # -> 4.57x cheaper
```

## Entanglement scaling: area vs volume law

- `entanglement_scaling.bipartite_entropy(state, n_left)`, `renyi2_entropy(...)`,
  `entanglement_spectrum(...)`, `is_area_law(entropies)`.
- `entanglement_scaling.page_average_entropy(n, n_left)` vs `random_state_entropy(...)` — Page's
  formula for a random pure state; `max_entanglement(n_left, n)`, `volume_law_slope(n)`.
- `schmidt.schmidt_decomposition(state, region)`, `truncation_fidelity(...)`,
  `area_law_compressibility(...)`.

```python
from quantum_debugger.algorithms.entanglement_scaling import page_average_entropy, max_entanglement
round(page_average_entropy(10, 5), 3), max_entanglement(5, 10)   # -> (2.966, 5.0)
```

## What this is verified against

- TEBD ground/real-time energies vs exact diagonalization of the TFIM.
- PEPS: exact contraction matched to the `H + CZ` cluster-state reference.
- MERA: the isometry/unitary identities and the constant causal-cone width.
- Contraction: the matrix-chain dynamic program vs the naive left-to-right cost.
- Entanglement: Page's average-entropy formula vs Haar-random sampling; the 1D area law.
