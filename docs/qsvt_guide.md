# Quantum signal processing & the QSVT

Quantum signal processing (QSP), qubitization, and the quantum singular value transformation
(QSVT) are a single unifying framework: encode a matrix into a unitary (a *block encoding*),
then apply a polynomial to its singular values by interleaving the encoding with simple phase
rotations. Grover search, Hamiltonian simulation, matrix inversion (HHL), and Gibbs-state
preparation all fall out as special cases. Every transform here is checked against the exact
matrix function computed by dense linear algebra.

All functions live under `quantum_debugger.algorithms.<module>`.

## QSP: polynomials from phase sequences

A length-`d` phase sequence realizes a degree-`d` polynomial `P(x)` as the `<0|U|0>` amplitude
of the QSP unitary. Zero phases give the Chebyshev polynomial `T_d`.

- `qsp.signal_operator(x)`, `qsp.qsp_unitary(phases, x)`, `qsp.qsp_response(phases, xs)`,
  `qsp.chebyshev_via_qsp(degree, xs)`, `qsp.qsp_complementary_response(phases, xs)`.

```python
import numpy as np
from quantum_debugger.algorithms.qsp import chebyshev_via_qsp
xs = np.array([-0.5, 0.0, 0.5])
chebyshev_via_qsp(3, xs)          # -> [ 1.,  0., -1.]
np.cos(3 * np.arccos(xs))         # -> [ 1., -0., -1.]   (== Chebyshev T_3)
```

## Block encoding & qubitization

- `block_encoding.block_encode(matrix)` — embed a Hermitian `A` (`||A|| <= 1`) in the top-left
  block of a unitary; `is_block_encoding(unitary, matrix)`, `top_left_block(unitary, dim)`.
- `block_encoding.qubitization_walk(block_encoding)`, `chebyshev_of_matrix(matrix, degree)`,
  `qsvt_transform(matrix, phases)`, `qsvt_scalar_response(phases, x)`.
- `lcu.lcu_block_encoding(coeffs, unitaries)`, `lcu_matrix(coeffs, unitaries)` — block-encode a
  linear combination of unitaries.

```python
import numpy as np
from quantum_debugger.algorithms.block_encoding import block_encode, is_block_encoding
A = np.array([[1.5, 0.3], [0.3, 1.0]]) / 2.0
is_block_encoding(block_encode(A), A)     # -> True
```

## QSVT matrix functions

Apply a smooth function to the eigenvalues of a Hermitian matrix by choosing the QSP phases that
approximate it. `qsvt_applications` and `matrix_functions` provide ready-made transforms.

- `matrix_functions.matrix_inverse_qsvt(matrix, degree)`,
  `matrix_function_chebyshev(matrix, func, degree)`, `chebyshev_coefficients(func, degree)`,
  `hamiltonian_simulation_qsvt(hamiltonian, time, degree)`, `solve_linear_system_qsvt(A, b)`.
- `qsvt_applications`: `matrix_sqrt_qsvt`, `matrix_inverse_sqrt_qsvt`, `matrix_sign_qsvt`,
  `matrix_exp_qsvt`, `matrix_log_qsvt`, `matrix_power_qsvt`, `pseudo_inverse_qsvt`,
  `ground_state_projector_qsvt`, `gibbs_state_qsvt`, `bandpass_filter_qsvt`.

```python
import numpy as np
from quantum_debugger.algorithms.matrix_functions import matrix_inverse_qsvt
A = np.array([[1.5, 0.3], [0.3, 1.0]])
inv = matrix_inverse_qsvt(A, degree=30)
np.max(np.abs(inv - np.linalg.inv(A)))    # -> ~0.0  (matches the exact inverse)
```

## Chebyshev spectral methods

- `chebyshev_spectral.spectral_moments(matrix, num_moments)`, `trace_of_function(matrix, func)`,
  `density_of_states_kpm(matrix)`, `eigenvalue_count_in_interval(matrix, a, b)`,
  `partition_function_qsvt(hamiltonian, beta)`.

## What this is verified against

- QSP responses vs the exact Chebyshev polynomials `T_d(x) = cos(d·arccos x)`.
- Block encodings vs the definition (`unitary`, correct top-left block).
- Every QSVT matrix function (`inverse`, `sqrt`, `sign`, `exp`, `Gibbs`, …) vs the exact function
  computed by dense eigendecomposition.
- Chebyshev spectral traces/DOS vs exact spectral sums.
