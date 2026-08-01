# Characterization & benchmarking

Protocols that measure how good a quantum processor actually is: quantum volume (heavy-output
probability), cross-entropy benchmarking (XEB) with the Porter-Thomas distribution, mirror
benchmarking, advanced and interleaved randomized benchmarking, and direct fidelity estimation.
Each metric is checked against its asymptotic closed form or a physical-validity constraint.

All functions live under `quantum_debugger.algorithms.<module>`.

## Quantum volume

A width-`n` square circuit passes if its heavy-output probability exceeds `2/3`; the ideal
random-circuit HOP tends to `(1 + ln 2)/2 ≈ 0.847`.

- `quantum_volume.heavy_outputs(ideal_probs)`, `heavy_output_probability(ideal_probs, samples)`,
  `ideal_heavy_output_probability()`, `quantum_volume_pass(hop, threshold)`,
  `quantum_volume(n_qubits)`.

```python
from quantum_debugger.algorithms.quantum_volume import ideal_heavy_output_probability, quantum_volume_pass
round(ideal_heavy_output_probability(), 4)   # -> 0.8466   ((1 + ln 2)/2)
quantum_volume_pass(0.70)                     # -> True     (above the 2/3 threshold)
```

## Cross-entropy benchmarking (XEB)

- `xeb.linear_xeb_fidelity(ideal_probs, sampled_indices)`,
  `cross_entropy_fidelity(ideal_probs, device_probs)`, `porter_thomas_pdf(p, dim)`,
  `porter_thomas_samples(dim, n)`, `speckle_purity(probs)`.

## Mirror & randomized benchmarking

RB extracts the error-per-Clifford from the exponential decay `A p^m + B`, with SPAM absorbed
into `A, B`.

- `mirror_benchmarking.mirror_survival(layers)`, `mirror_fidelity_decay(layers_list, p)`.
- `randomized_benchmarking_advanced.rb_survival(p, m)`, `fit_rb_decay(m_values, survivals)`,
  `error_per_clifford(p, d)`, `average_gate_fidelity_from_rb(p, d)`,
  `interleaved_rb_gate_error(p_ref, p_interleaved)`.
- `randomized_benchmarking.randomized_benchmarking(...)`, `single_qubit_clifford_group()`.

```python
from quantum_debugger.algorithms.randomized_benchmarking_advanced import (
    error_per_clifford, average_gate_fidelity_from_rb)
error_per_clifford(p=0.99)            # -> 0.005   ((1-p)(d-1)/d)
average_gate_fidelity_from_rb(0.99)   # -> 0.995
```

## Direct fidelity estimation & tomography

- `tomography_dfe.direct_fidelity_estimation(rho, target)`, `pauli_expectations(rho)`,
  `state_tomography(expectations, n_qubits)`, `is_physical_density_matrix(rho)`.

## What this is verified against

- Quantum volume: the `(1 + ln 2)/2` asymptotic HOP and the `2/3` pass threshold.
- XEB: the Porter-Thomas density `D e^{-Dp}` and the linear-XEB fidelity estimator.
- RB: the `A p^m + B` decay and the closed-form error-per-Clifford `(1-p)(d-1)/d`.
- DFE/tomography: reconstruction of exactly-known reference states; physical-density constraints.
