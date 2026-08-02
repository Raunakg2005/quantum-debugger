# Quantum chaos & scrambling

What separates a chaotic quantum system from an integrable one? This guide covers the statistical
diagnostics: random-matrix theory (the universal spectral statistics of chaos), the spectral form
factor (chaos in the time domain), Krylov complexity (how fast an operator spreads under
evolution), and the eigenstate thermalization hypothesis (why isolated systems thermalize). Every
quantity is checked against a closed form, the exact spectrum, or the exact autocorrelation
function.

All functions live under `quantum_debugger.algorithms.<module>`.

## Random-matrix theory

Chaotic spectra behave like random matrices: level repulsion (the Wigner surmise) rather than the
`e^{-s}` of an integrable spectrum, and a semicircle density.

- `random_matrix.goe_matrix(n)`, `gue_matrix(n)`, `wigner_surmise(s, beta)`,
  `poisson_spacing_pdf(s)`, `semicircle_density(x, R)`, `unfolded_spacings(eigs)`,
  `level_spacing_ratios(eigs)`, `mean_ratio(eigs)`, `surmise_normalization(beta)`, `surmise_mean(beta)`.

```python
import numpy as np
from quantum_debugger.algorithms.random_matrix import goe_matrix, mean_ratio, surmise_normalization
mean_ratio(np.linalg.eigvalsh(goe_matrix(400, seed=1)))   # -> ~0.53   (GOE level repulsion)
surmise_normalization(1)                                   # -> 1.0     (Wigner surmise normalized)
```

## The spectral form factor

The SFF `|Σ_j e^{−iE_j t}|²` starts at `D²`, dips, ramps (level repulsion), and plateaus at `D`.

- `spectral_form_factor.spectral_form_factor(eigs, t)`, `connected_sff(ensemble, t)`, `sff_curve(...)`,
  `sff_at_zero(...)`, `plateau_value(...)`, `long_time_average(...)`, `reaches_plateau(...)`,
  `normalized_sff(...)`.

```python
import numpy as np
from quantum_debugger.algorithms.random_matrix import goe_matrix
from quantum_debugger.algorithms.spectral_form_factor import sff_at_zero, plateau_value, reaches_plateau
e = np.linalg.eigvalsh(goe_matrix(64, seed=3))
sff_at_zero(e), plateau_value(e)     # -> (4096.0, 64)   SFF(0)=D², plateau=D
reaches_plateau(e, 400)              # -> True           late-time average converges to D
```

## Krylov (operator-growth) complexity

The operator Lanczos algorithm turns Heisenberg evolution into a 1D hopping model; the Lanczos
coefficients reconstruct the autocorrelation function exactly.

- `krylov_complexity.lanczos_coefficients(H, O)`, `autocorrelation(H, O, t)`,
  `reconstruct_autocorrelation(bs, t)`, `krylov_complexity(bs, t)`, `krylov_dimension(bs)`,
  `moment(H, O, k)`, `liouvillian(H, O)`, `operator_inner_product(A, B)`.

```python
import numpy as np
from quantum_debugger.algorithms.krylov_complexity import (
    lanczos_coefficients, autocorrelation, reconstruct_autocorrelation)
Z = np.array([[1, 0], [0, -1]], dtype=complex); X = np.array([[0, 1], [1, 0]], dtype=complex)
w = 1.6; H = (w / 2) * Z
bs = lanczos_coefficients(H, X)
bs[0]                                                 # -> 1.6   (b_1 = ω)
round(reconstruct_autocorrelation(bs, 0.7), 5), round(autocorrelation(H, X, 0.7), 5)
# -> (0.43568, 0.43568)   Lanczos reconstruction == exact C(t) = cos(ωt)
```

## Eigenstate thermalization (ETH)

In a chaotic system each energy eigenstate already looks thermal: diagonal matrix elements of a
bounded observable are a smooth function of energy, matching the microcanonical average.

- `eth.eigenbasis(H)`, `observable_matrix(V, O)`, `diagonal_elements(...)`, `offdiagonal_elements(...)`,
  `eigenstate_expectation(...)`, `microcanonical_average(...)`, `eth_diagonal_fluctuation(...)`,
  `eth_offdiagonal_variance(...)`, `eigenstate_matches_microcanonical(...)`, `thermalizes(...)`.

```python
import numpy as np
from quantum_debugger.algorithms.random_matrix import goe_matrix
from quantum_debugger.algorithms.eth import thermalizes
D = 200
O = np.diag([1.0] * (D // 2) + [0.0] * (D // 2)).astype(complex)   # a bounded (projector) observable
thermalizes(goe_matrix(D, seed=5), O, tol=0.1)     # -> True   (eigenstate == microcanonical average)
```

## What this is verified against

- Random matrices: the Wigner surmise normalizes to 1 with mean spacing 1; `<r>` ≈ 0.53 (GOE) vs
  0.386 (Poisson); the semicircle density at 0.
- Spectral form factor: `SFF(0) = D²` exactly, and the late-time average converges to the plateau `D`.
- Krylov complexity: the Lanczos coefficients reconstruct the exact autocorrelation `C(t)`; for a
  single spin `b_1 = ω`, `C(t) = cos(ωt)`, and `K(t)` oscillates.
- ETH: a chaotic eigenstate's expectation matches the microcanonical average, and the diagonal
  fluctuations shrink as the Hilbert space grows.
