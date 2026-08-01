# Error mitigation II

A second, deeper layer of quantum error mitigation on top of the ZNE guide: richer zero-noise
extrapolation models and unitary folding, probabilistic error cancellation via the Pauli
transfer matrix, Clifford data regression, virtual distillation, symmetry verification,
classical shadows, readout unfolding, Pauli twirling, and dynamical decoupling. Each method is
checked against an exactly-computed noiseless expectation or an analytic overhead.

All functions live under `quantum_debugger.algorithms.<module>`.

## Zero-noise extrapolation & unitary folding

- `zne_extrapolation.richardson_extrapolate(scales, values)`,
  `polynomial_extrapolate(scales, values, degree)`, `exponential_extrapolate(...)`,
  `adaptive_extrapolate(...)` — model-select among linear/quadratic/exponential.
- `unitary_folding.fold_global(unitary, num_folds)` (`G -> G(G†G)^k`, exactly equal to `G` in the
  noiseless limit), `noise_scale_factor(num_folds)` (`2k+1`), `fold_gate_sequence(...)`.

```python
from quantum_debugger.algorithms.zne_extrapolation import richardson_extrapolate
from quantum_debugger.algorithms.unitary_folding import noise_scale_factor
richardson_extrapolate([1, 2, 3], [0.80, 0.66, 0.54])   # -> 0.96  (zero-noise value)
noise_scale_factor(2)                                    # -> 5     (odd amplification 2k+1)
```

## Probabilistic error cancellation (PTM)

PEC inverts a noise channel with a quasi-probability decomposition; the Pauli transfer matrix
makes this exact for Pauli/depolarizing channels.

- `pec_ptm.channel_ptm(kraus_ops)`, `invert_channel_ptm(ptm)`, `pauli_quasiprobabilities(ptm)`,
  `pec_sampling_overhead(ptm)`, `pec_mitigate_ptm(noisy_rho, noise_kraus, observable)`,
  `depolarizing_overhead(p)`.
- `pec.depolarizing_coeffs(p)`, `invert_pauli_channel(coeffs)`, `pec_mitigate(...)`.

## Learning-based & post-selection methods

- `cdr.fit_cdr_model(noisy, ideal)`, `apply_cdr(model, noisy_value)`, `cdr_mitigate(...)` —
  Clifford data regression.
- `virtual_distillation.virtual_distillation(rho, observable, m)` — the `Tr(O ρ^m)/Tr(ρ^m)`
  estimator that suppresses incoherent error.
- `symmetry_verification.symmetry_project(rho, symmetry, sector)`,
  `symmetry_verified_expectation(...)` — post-select onto a symmetry sector.
- `classical_shadows.collect_shadows(state, shots)`, `estimate_observable(shadows, pauli)`,
  `shadow_estimates(...)` — many observables from one measurement set.

```python
from quantum_debugger.algorithms.classical_shadows import shadow_estimates
est = shadow_estimates([0.5**0.5, 0.5**0.5], {"Z": [1.0, -1.0]}, shots=4000, seed=0)
# estimates <Z> ~ 0 for |+>, from randomized single-shot snapshots
```

## Readout correction, twirling & dynamical decoupling

- `readout_advanced.calibrate_assignment_matrix(...)`, `tensored_assignment_matrix(...)`,
  `iterative_bayesian_unfolding(...)`, `constrained_readout_mitigate(...)`;
  `readout_mitigation.assignment_matrix(...)`, `mitigate_readout(...)`.
- `pauli_twirling.pauli_twirl(kraus_ops)` — tailor coherent error into a Pauli channel.
- `dynamical_decoupling.cpmg_sequence(n)`, `udd_sequence(n)`, `xy4_sequence(reps)`,
  `dd_coherence(pulse_times, sigma)`, `suppression_order(pulse_times)`.

## What this is verified against

- ZNE/folding: the exact zero-noise expectation and the analytic `2k+1` amplification;
  `fold_global` is bit-exactly `G` with no noise.
- PEC/PTM: the inverse-channel identity and the closed-form depolarizing overhead.
- CDR / virtual distillation / symmetry verification: the exact ideal expectation value.
- Classical shadows: convergence to exact Pauli expectations.
- Dynamical decoupling: analytic filter-function suppression orders.
