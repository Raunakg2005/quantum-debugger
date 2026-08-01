# Continuous-variable & bosonic quantum computing

Quantum information in infinite-dimensional bosonic modes: Gaussian states and their covariance
matrices, the symplectic group of Gaussian unitaries, Wigner and Husimi quasiprobability
functions, boson sampling (matrix permanents and Hong-Ou-Mandel interference), and bosonic
error-correcting (cat) codes. Each routine is checked against a symplectic invariant, an exact
permanent, or a parity closed form.

All functions live under `quantum_debugger.algorithms.<module>`.

## Gaussian states & the symplectic group

A Gaussian state is fully described by its covariance matrix; Gaussian unitaries act as
symplectic transforms `σ -> S σ S^T`.

- `gaussian_states.vacuum_covariance(n_modes)`, `thermal_covariance(n_bar)`,
  `squeezed_covariance(r, phi)`, `symplectic_eigenvalues(cov)`, `purity_gaussian(cov)`,
  `gaussian_entropy(cov)`, `is_physical_covariance(cov)`.
- `symplectic.is_symplectic(S)`, `beamsplitter_symplectic(theta)`, `squeezing_symplectic(r)`,
  `two_mode_squeezing_symplectic(r)`, `phase_rotation_symplectic(phi)`, `apply_symplectic(cov, S)`.

```python
from quantum_debugger.algorithms.symplectic import is_symplectic, beamsplitter_symplectic
from quantum_debugger.algorithms.gaussian_states import purity_gaussian, vacuum_covariance, thermal_covariance
is_symplectic(beamsplitter_symplectic(0.5))     # -> True   (a valid Gaussian unitary)
purity_gaussian(vacuum_covariance(1))           # -> 1.0    (vacuum is pure)
round(purity_gaussian(thermal_covariance(1.0)), 4)   # -> 0.3333  (thermal is mixed)
```

## Wigner & Husimi functions

- `wigner.wigner_point(rho, alpha, cutoff)`, `wigner_grid(...)`, `wigner_integral(...)` (`= 1`),
  `wigner_negativity(...)` (nonclassicality), `husimi_q(rho, alpha, cutoff)`.

## Boson sampling

The output probabilities of a linear-optical network are matrix permanents — #P-hard, the basis
of boson-sampling hardness.

- `boson_sampling.permanent(A)` (Ryser's formula), `boson_sampling_probability(U, in, out)`,
  `beamsplitter_unitary(theta)`, `hong_ou_mandel(theta)`.

```python
import numpy as np
from quantum_debugger.algorithms.boson_sampling import hong_ou_mandel
hong_ou_mandel(np.pi / 4)    # -> {'coincidence': 0.0, 'bunching': 1.0}  (perfect two-photon bunching)
```

## Bosonic (cat) codes

- `bosonic_codes.cat_state(alpha, parity, cutoff)`, `cat_code_words(alpha, cutoff)`,
  `parity_operator(cutoff)`, `parity_expectation(state)`, `photon_loss(state)`,
  `loss_flips_parity(alpha)` — single-photon loss flips the cat-code parity, the error syndrome.

## What this is verified against

- Gaussian states: the symplectic condition `S Ω S^T = Ω`, Williamson eigenvalues, and the
  purity `1/prod ν_k` (`1` for vacuum, `1/(2n̄+1)` for thermal).
- Wigner: the phase-space integral normalizes to 1.
- Boson sampling: the permanent via Ryser's formula; the 50:50 HOM dip to zero coincidence.
- Cat codes: single-photon loss exactly flips photon-number parity.
