# Quantum complexity & advantage

*Why* quantum computers help — the complexity theory behind quantum speedups. This guide covers
Boolean-function complexity measures and their hierarchy, Fourier analysis on the Boolean cube,
query complexity and the provable oracle separations (Deutsch-Jozsa, Simon, Grover, parity),
communication complexity with quantum fingerprinting, and the containment order of complexity
classes (`P ⊆ BPP ⊆ BQP ⊆ PP ⊆ PSPACE`). Every measure is verified by brute force or against its
closed form.

All functions live under `quantum_debugger.algorithms.<module>`.

## Boolean-function complexity

The measures obey `s(f) ≤ bs(f) ≤ C(f) ≤ D(f)` and `deg(f) ≤ D(f)` — verified exhaustively.

- `boolean_complexity.truth_table(f, n)`, `max_sensitivity(tt, n)`, `block_sensitivity(tt, n)`,
  `certificate_complexity(tt, n)`, `decision_tree_complexity(tt, n)`, `polynomial_degree(tt, n)`,
  `sensitivity_hierarchy_holds(tt, n)`.

```python
from quantum_debugger.algorithms.boolean_complexity import (
    truth_table, max_sensitivity, decision_tree_complexity, sensitivity_hierarchy_holds)
maj = truth_table(lambda b: 1 if sum(b) >= 2 else 0, 3)   # 3-bit majority
max_sensitivity(maj, 3), decision_tree_complexity(maj, 3)   # -> (2, 3)
sensitivity_hierarchy_holds(maj, 3)                          # -> True   (s ≤ bs ≤ C ≤ D)
```

## Fourier analysis on the cube

- `fourier_analysis.fourier_coefficients(tt, n)`, `parseval(tt, n)` (`= 1`),
  `influence(tt, n, i)`, `total_influence(tt, n)`, `noise_stability(tt, n, rho)`,
  `degree_from_fourier(tt, n)`, `fourier_weight_above_degree(tt, n, k)`, `to_pm1(tt)`.

```python
from quantum_debugger.algorithms.fourier_analysis import parseval
from quantum_debugger.algorithms.boolean_complexity import truth_table
maj = truth_table(lambda b: 1 if sum(b) >= 2 else 0, 3)
round(parseval(maj, 3), 6)   # -> 1.0   (Parseval: total Fourier weight is 1)
```

## Query complexity & separations

- `query_complexity.deutsch_jozsa_queries(n)` (1 vs `2^{n-1}+1`), `simon_queries(n)`,
  `grover_queries(N)` (`⌈(π/4)√N⌉` vs `N`), `parity_queries(n)`, `quantum_speedup(counts)`,
  `grover_is_optimal(N, q)`, `is_exponential_separation(queries_fn)`,
  `polynomial_method_bound(degree)`.

```python
from quantum_debugger.algorithms.query_complexity import grover_queries, deutsch_jozsa_queries
grover_queries(256)          # -> {'quantum': 13, 'classical': 256}   (quadratic speedup)
deutsch_jozsa_queries(10)    # -> {'quantum': 1, 'classical': 513}    (exponential)
```

## Communication complexity & complexity classes

- `communication_complexity.equality_deterministic(n)`, `equality_randomized(n)`,
  `quantum_fingerprint_length(n)`, `equality_exponential_saving(n)`,
  `inner_product_complexity(n)`, `disjointness_complexity(n)`, `has_quantum_advantage(counts)`.
- `complexity_classes.known_containments()`, `contains(bigger, smaller)`, `problem_class(problem)`,
  `in_bqp(problem)`, `is_open_separation(a, b)`, `hierarchy_is_consistent()`.

```python
from quantum_debugger.algorithms.complexity_classes import hierarchy_is_consistent, contains
hierarchy_is_consistent()        # -> True
contains("PSPACE", "BQP")        # -> True   (BQP ⊆ PSPACE is proven)
```

## What this is verified against

- Boolean measures: brute-force computation and the exhaustively-checked hierarchy
  `s ≤ bs ≤ C ≤ D`, `deg ≤ D`.
- Fourier: Parseval's identity (`= 1`) and the influence/degree relations.
- Query complexity: the closed-form separations (DJ/Simon exponential, Grover `Θ(√N)`, parity ×2).
- Classes: the containment DAG is a consistent partial order (reflexive, transitive, acyclic).
