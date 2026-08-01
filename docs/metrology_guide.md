# Quantum metrology & sensing

Using quantum resources to measure physical parameters more precisely than any classical
strategy: the quantum Fisher information and the Cramér-Rao bound, GHZ/NOON probes reaching the
Heisenberg limit, spin squeezing (the Wineland parameter), multiparameter estimation, and sensing
protocols. Every precision claim is checked against the QFI closed form (`n²` at the Heisenberg
limit, `n` at the standard quantum limit).

All functions live under `quantum_debugger.algorithms.<module>`.

## Quantum Fisher information & the Cramér-Rao bound

- `quantum_metrology.qfi_pure(state, generator)`, `qfi_mixed(rho, generator)`,
  `cramer_rao_bound(qfi, repetitions)`, `heisenberg_limit(n)` (`1/n`),
  `standard_quantum_limit(n)` (`1/sqrt(n)`), `metrological_advantage(n)`, `generator_variance(...)`.

```python
from quantum_debugger.algorithms.quantum_metrology import heisenberg_limit, standard_quantum_limit
heisenberg_limit(4), standard_quantum_limit(4)   # -> (0.25, 0.5)   (1/n  vs  1/sqrt(n))
```

## Probes: GHZ, NOON & product states

An entangled GHZ probe has QFI `n²` (Heisenberg limit); an uncorrelated product probe has QFI `n`.

- `interferometry.ghz_probe(n)`, `ghz_probe_qfi(n)` (`= n²`), `product_probe(n)`,
  `product_probe_qfi(n)` (`= n`), `noon_phase_qfi(N)`, `probe_qfi(state, n)`,
  `ramsey_signal(theta, n, ghz)`, `collective_jz(n)`.

```python
from quantum_debugger.algorithms.interferometry import ghz_probe_qfi, product_probe_qfi
ghz_probe_qfi(4), product_probe_qfi(4)   # -> (16, 4)   (n^2 Heisenberg vs n standard limit)
```

## Spin squeezing

- `spin_squeezing.one_axis_twisting(n, chi_t)` (Wineland `ξ²`), `best_squeezing(n)`.
- `spin_squeezing_metrology.wineland_squeezing_parameter(state, n)`, `one_axis_twisting_state(...)`,
  `is_squeezed(state, n)`, `metrological_gain(xi_squared)`, `coherent_spin_state(n)`,
  `collective_spin(n, axis)`, `best_twisting_squeezing(n)`.

```python
from quantum_debugger.algorithms.spin_squeezing import one_axis_twisting
round(one_axis_twisting(6, chi_t=0.3), 4)   # -> 0.4243   (< 1: metrologically useful squeezing)
```

## Multiparameter estimation & sensing protocols

- `multiparameter_estimation.qfi_matrix(state, generators)`, `cramer_rao_matrix(...)`,
  `total_precision_bound(...)`, `parameter_incompatibility(...)`.
- `sensing_protocols.phase_precision(qfi, shots)`, `frequency_precision(...)`,
  `signal_to_noise(...)`, `is_heisenberg_scaling(qfi_values, n_values)`, `qfi_per_particle(...)`.
- `spectroscopy.unitary_eigenphase(U, eigenstate)`, `hermitian_eigenvalue(H, eigenvector)`;
  `weak_values.weak_value(A, pre, post)`, `weak_value_demo(...)`;
  `geometric_phase.berry_phase_triangle(...)`, `pancharatnam_phase(states)`, `solid_angle(...)`.

## What this is verified against

- QFI: `F_Q = 4 Var(G)` computed exactly; GHZ probe `= n²`, product probe `= n`.
- Precision limits: the `1/n` Heisenberg and `1/sqrt(n)` standard-quantum-limit closed forms.
- Squeezing: the Wineland `ξ² < 1` criterion for metrological gain.
- Weak values / geometric phase: exact weak-measurement pointer shifts; the solid-angle/Berry
  phase relation.
