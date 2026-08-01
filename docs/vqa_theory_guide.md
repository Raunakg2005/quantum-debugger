# Variational algorithms & QML theory

The theory behind variational quantum algorithms and quantum machine learning: exact gradients
by the parameter-shift rule, the barren-plateau phenomenon, ansatz expressibility, the quantum
natural gradient (Fubini-Study metric), entangling capability (Meyer-Wallach), and loss-landscape
robustness. Gradients are checked against finite differences, and statistical claims against
Haar-random references.

All functions live under `quantum_debugger.algorithms.<module>`.

## Parameter-shift gradients

The shift rule gives *exact* derivatives of an expectation value from two circuit evaluations —
no finite-difference error.

- `parameter_shift.parameter_shift_gradient(cost_fn, params, index)`,
  `parameter_shift_gradient_all(...)`, `parameter_shift_hessian_diagonal(...)`,
  `finite_difference_gradient(...)` (the numerical reference), `gradient_norm(...)`.

```python
import numpy as np
from quantum_debugger.algorithms.parameter_shift import (
    parameter_shift_gradient, finite_difference_gradient)
f = lambda p: np.cos(p[0])
g_shift = parameter_shift_gradient(f, np.array([0.7]), 0)
g_fd    = finite_difference_gradient(f, np.array([0.7]))[0]
round(g_shift, 5), round(float(g_fd), 5)     # -> (-0.64422, -0.64422)  (== -sin 0.7)
```

## Barren plateaus & cost concentration

Global-cost gradients vanish exponentially in the qubit count for deep random circuits; local
costs are milder.

- `barren_plateaus.gradient_sample_variance(n, layers, obs_diag)`,
  `global_cost_gradient_variance(...)`, `local_cost_gradient_variance(...)`,
  `barren_plateau_scaling(qubit_range, layers)`, `cost_concentration(...)`.

## Expressibility & entangling capability

- `expressibility.frame_potential(n, layers)`, `expressibility_kl(...)`,
  `haar_mean_fidelity(dim)`, `sample_ansatz_fidelities(...)`.
- `entangling_capability.meyer_wallach(state)`, `entangling_capability(n, layers)`,
  `average_entanglement(states)`, `is_product_state(state)`.

```python
import numpy as np
from quantum_debugger.algorithms.entangling_capability import meyer_wallach
meyer_wallach(np.array([1, 0, 0, 1]) / np.sqrt(2))   # -> 1.0   (Bell state, maximally entangled)
meyer_wallach(np.array([1, 0, 0, 0], dtype=float))   # -> 0.0   (product state)
```

## Quantum natural gradient & ansatz utilities

- `quantum_natural_gradient.quantum_geometric_tensor(params, n, layers)`,
  `quantum_fisher_matrix(...)`, `natural_gradient(gradient, metric)`,
  `fubini_study_distance(a, b)`, `effective_quantum_dimension(metric)`.
- `variational_ansatz.hardware_efficient_ansatz(params, n, layers)`,
  `ansatz_num_params(n, layers)`, `ansatz_expectation(...)`, `z_observable(n)`;
  `loss_robustness.loss_robustness(n)`.

## What this is verified against

- Gradients: the parameter-shift rule matched to central finite differences; the shift-rule
  Hessian to second finite differences.
- Barren plateaus: gradient variance shrinking with qubit number (global vs local cost).
- Expressibility: the frame potential approaching the Haar value `1/dim`.
- Entangling capability: Meyer-Wallach `Q = 1` for a Bell state, `0` for a product state.
