# Hamiltonian simulation & product formulas

Simulating time evolution `e^{-iHt}` on a quantum computer, with rigorous error control:
Trotter-Suzuki product formulas (first, second, fourth order), qDRIFT randomized compilation,
truncated-Taylor (LCU) simulation, commutator-based Trotter error bounds, and a cost model that
picks the cheapest method. Every approximation is checked against the exact propagator computed
by matrix exponentiation.

All functions live under `quantum_debugger.algorithms.<module>`.

Hamiltonians are given as weighted Pauli-string terms, e.g. `[(-1.0, "ZZI"), (-1.0, "IZZ")]`
(the transverse-field/Ising style used throughout; `vqe_solver.tfim_hamiltonian(n)` builds one).

## Product formulas

- `product_formulas.exact_evolution(terms, t)` — the reference `e^{-iHt}`;
  `first_order_trotter(terms, t, steps)`, `second_order_trotter(...)`, `fourth_order_suzuki(...)`,
  `randomized_trotter(...)`, `trotter_error(terms, t, steps, order)`,
  `error_scaling_slope(terms, t, order)`, `simulate_state(...)`.

```python
from quantum_debugger.algorithms.vqe_solver import tfim_hamiltonian
from quantum_debugger.algorithms.product_formulas import trotter_error
terms = tfim_hamiltonian(3, field=1.0, coupling=1.0)
round(trotter_error(terms, 1.0, steps=2, order=1), 4)   # -> 0.6165
round(trotter_error(terms, 1.0, steps=8, order=1), 4)   # -> 0.1398   (error falls with more steps)
```

## qDRIFT & Taylor simulation

- `qdrift.qdrift_channel(terms, t, N, rho)`, `qdrift_error(...)`, `qdrift_probabilities(terms)`,
  `qdrift_gate_count(lam, t, epsilon)` (independent of the number of terms).
- `taylor_simulation.taylor_series_unitary(H, t, order)`, `taylor_error(H, t, order)`,
  `series_convergence(H, t, orders)`, `taylor_truncation_order(norm_Ht, epsilon)`,
  `hamiltonian_from_terms(terms)`.

## Error bounds & method selection

The first-order Trotter error is upper-bounded by the sum of pairwise commutator norms — a bound
you can compute without the exact propagator.

- `trotter_bounds.first_order_error_bound(terms, t)`, `second_order_error_bound(...)`,
  `commutator_sum(terms)`, `terms_commute(terms)`, `spectral_norm(A)`.
- `simulation_complexity.trotter_first_order_steps(...)`, `qdrift_gate_count(...)`,
  `taylor_gate_count(...)`, `qdrift_beats_trotter(...)`, `cheapest_method(...)`.

```python
from quantum_debugger.algorithms.vqe_solver import tfim_hamiltonian
from quantum_debugger.algorithms.trotter_bounds import first_order_error_bound
from quantum_debugger.algorithms.product_formulas import trotter_error
terms = tfim_hamiltonian(3, field=1.0, coupling=1.0)
bound = first_order_error_bound(terms, 1.0)          # -> 4.0
bound >= trotter_error(terms, 1.0, 2, order=1)       # -> True   (the bound holds)
```

## What this is verified against

- Product formulas: the exact propagator `e^{-iHt}`; the error decreases as `steps^{-order}`.
- qDRIFT / Taylor: trace-distance and spectral-norm error vs the exact evolution; strictly
  decreasing with truncation order.
- Bounds: the commutator-sum bound provably upper-bounds the measured Trotter error.
