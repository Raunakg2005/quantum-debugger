# Advanced quantum algorithms II

A second layer of quantum algorithms beyond the textbook set: advanced amplitude estimation
(canonical, maximum-likelihood, and iterative), quantum mean estimation, phase-estimation
variants (Kitaev, robust), quantum walks (discrete and continuous time, Szegedy), Grover-based
optimization (Dürr-Høyer), and quantum state discrimination. Each is checked against its
Heisenberg-limited or Helstrom-optimal closed form.

All functions live under `quantum_debugger.algorithms.<module>`.

## Amplitude & mean estimation

Amplitude estimation reaches error `~1/M` in the number of Grover calls — a quadratic speedup
over Monte Carlo's `~1/sqrt(shots)`.

- `amplitude_estimation_advanced.canonical_qae(a_true, n_bits)`,
  `maximum_likelihood_ae(a_true, m_schedule)`, `iterative_ae(a_true, rounds)`,
  `heisenberg_scaling_error(total_grover_calls)`, `classical_monte_carlo_error(shots)`.
- `quantum_mean_estimation.quantum_mean_estimation(f_values, m_schedule)`,
  `monte_carlo_speedup(eps)`, `quantum_samples_for_precision(eps)`.

```python
from quantum_debugger.algorithms.quantum_mean_estimation import monte_carlo_speedup
monte_carlo_speedup(eps=0.01)    # -> 100.0   (quantum needs 1/eps, classical 1/eps^2)
```

## Phase-estimation variants & quantum walks

- `phase_estimation_variants.kitaev_phase_estimation(phase, n_bits)`,
  `robust_phase_estimation(phase, max_k)`, `phase_estimation_error(n_bits)`.
- `quantum_walks.discrete_time_walk_line(steps)`, `continuous_time_walk_operator(adjacency, t)`,
  `szegedy_walk_operator(P)`, `position_variance(distribution)` (ballistic `~t^2` spread),
  `spatial_search_ctqw(adjacency, marked, gamma, time)`.

## Grover optimization & state discrimination

- `grover_optimization.durr_hoyer_minimize(values)`, `grover_adaptive_search(f, n_qubits)`,
  `quantum_minimum_queries(n_items)` (`O(sqrt N)`), `classical_minimum_queries(n_items)` (`N`).
- `discrimination.helstrom_bound(p0, state0, p1, state1)`, `helstrom_measurement(...)`,
  `unambiguous_discrimination(psi0, psi1)`.
- `quantum_counting.quantum_counting(n_qubits, marked, n_counting)`.

```python
import numpy as np
from quantum_debugger.algorithms.discrimination import helstrom_bound
from quantum_debugger.algorithms.grover_optimization import quantum_minimum_queries, classical_minimum_queries
helstrom_bound(0.5, np.array([1,0]), 0.5, np.array([0,1]))   # -> 0.0  (orthogonal => no error)
quantum_minimum_queries(256), classical_minimum_queries(256) # -> (16.0, 256)  (sqrt speedup)
```

## What this is verified against

- Amplitude/mean estimation: the `1/M` Heisenberg scaling vs the `1/sqrt(shots)` Monte-Carlo
  baseline.
- Quantum walks: the ballistic `~t^2` variance (vs diffusive `~t` classically).
- Grover minimization: the `O(sqrt N)` query count against the linear classical bound.
- Discrimination: the Helstrom error bound (`0` for orthogonal states) computed exactly.
