# Quantum optimization & QAOA theory

Combinatorial optimization on a quantum computer: QUBO/Ising encodings of problems (MaxCut,
vertex cover, number partitioning), the Quantum Approximate Optimization Algorithm (QAOA) and
its energy landscape, adiabatic optimization with the Landau-Zener transition, and quantum
annealing. Every encoding is checked against a brute-force optimum, and every dynamical claim
against exact time evolution.

All functions live under `quantum_debugger.algorithms.<module>`.

## QUBO & Ising encodings

- `qubo.max_cut_qubo(edges, n_nodes)`, `vertex_cover_qubo(...)`, `number_partition_qubo(numbers)`,
  `qubo_energy(Q, x)`, `qubo_to_ising(Q)`, `ising_energy(h, J, s)`,
  `brute_force_qubo(Q)`, `brute_force_ising(h, J)` — the exact optima the encodings are checked against.

```python
from quantum_debugger.algorithms.qubo import max_cut_qubo, brute_force_qubo
Q = max_cut_qubo([(0, 1), (1, 2), (2, 0)], 3)   # triangle
x, energy = brute_force_qubo(Q)
list(map(int, x)), round(float(energy), 1)       # -> ([0, 0, 1], -2.0)  (cuts 2 of 3 edges)
```

## QAOA theory

- `qaoa_theory.cost_diagonal(edges, n)`, `qaoa_state(cost_diag, gammas, betas, n)`,
  `qaoa_expectation(...)`, `optimize_qaoa_p1(edges, n)`, `qaoa_landscape(edges, n)`,
  `cost_layer(...)`, `mixer_layer(...)`.
- `maxcut.brute_force_maxcut(graph, n_nodes)`, `solve_maxcut(graph, p)`.

```python
from quantum_debugger.algorithms.qaoa_theory import optimize_qaoa_p1
r = optimize_qaoa_p1([(0, 1), (1, 2), (2, 0)], 3)
sorted(r.keys())   # -> ['approximation_ratio', 'beta', 'expectation', 'gamma', 'max_cut']
```

## Adiabatic optimization & annealing

The adiabatic theorem sets a runtime `~1/gap_min²`; the Landau-Zener formula gives the diabatic
error of a finite sweep.

- `adiabatic_optimization.interpolating_hamiltonian(H0, H1, s)`, `instantaneous_gap(...)`,
  `minimum_gap(H0, H1)`, `adiabatic_evolve(...)`, `adiabatic_success_probability(...)`,
  `landau_zener_probability(gap, sweep_velocity)`, `adiabatic_runtime_bound(min_gap)`,
  `transverse_field_driver(n)`.
- `quantum_annealing.anneal(ising_h, ising_J, total_time)`, `annealed_solution(...)`,
  `annealing_success_probability(...)`, `spectral_gap_at(...)`.
- `sat_solver.grover_solve(predicate, n_qubits)`, `grover_optimize.grover_minimize(f, n_qubits)`,
  `adiabatic.adiabatic_evolution(h_initial, h_final, total_time)`.

## What this is verified against

- Encodings: `brute_force_qubo` / `brute_force_ising` — the exact optimum by enumeration, and the
  exact QUBO↔Ising conversion.
- QAOA: exact cost expectations on the full state vector.
- Adiabatic/annealing: exact time evolution; the `exp(-π gap²/4v)` Landau-Zener transition
  matched to a two-level sweep simulation; success probability rising toward 1 with runtime.
