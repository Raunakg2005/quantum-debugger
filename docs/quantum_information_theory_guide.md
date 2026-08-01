# Quantum information & resource theories

Quantitative quantum information: entropies, distinguishability measures, the Holevo bound,
recovery maps, majorization and state convertibility, and the resource theories of coherence,
magic, and entanglement (negativity, concurrence, witnesses, distillation). Every quantity is
checked against a closed form or an exactly-diagonalized reference state.

All functions live under `quantum_debugger.algorithms.<module>`.

## Entropies & distances

- `quantum_entropies.von_neumann_entropy(rho)`, `renyi_entropy(rho, alpha)`,
  `tsallis_entropy(rho, q)`, `quantum_mutual_information(rho_ab, dims)`,
  `conditional_entropy(...)`, `entanglement_entropy_pure(state, dims)`.
- `quantum_distances.trace_distance(rho, sigma)`, `uhlmann_fidelity(...)`, `bures_distance(...)`,
  `bures_angle(...)`, `quantum_relative_entropy(...)`, `fuchs_van_de_graaf(...)`.

```python
import numpy as np
from quantum_debugger.algorithms.quantum_entropies import von_neumann_entropy
from quantum_debugger.algorithms.quantum_distances import trace_distance
von_neumann_entropy(np.eye(2) / 2)                        # -> 1.0  (maximally mixed qubit)
trace_distance(np.eye(2) / 2, np.diag([1.0, 0.0]))       # -> 0.5
```

## Holevo bound, recovery & majorization

- `holevo.holevo_bound(probs, states)`, `accessible_information(...)`,
  `dense_coding_capacity(F)`.
- `petz.petz_recovery(kraus_ops, reference, rho)`, `petz_code_recovery(...)`.
- `majorization.majorizes(x, y)`, `nielsen_convertible(psi, phi, dims)` (Nielsen's LOCC theorem),
  `majorization_entropy_bound(x, y)`.

## Coherence & magic

- `coherence.l1_coherence(rho)`, `relative_entropy_of_coherence(rho)`,
  `robustness_of_coherence(rho)`, `dephase(rho)`, `is_incoherent(rho)`.
- `magic_measures.stabilizer_renyi_entropy(state)`, `magic_of_t_states(count)`.

## Entanglement: measures, negativity, witnesses, distillation

- `entanglement_measures.concurrence(rho)`, `entanglement_of_formation(rho)`, `tangle(rho)`,
  `schmidt_rank(state, dims)`.
- `entanglement_negativity.negativity(rho, dims)`, `logarithmic_negativity(...)`,
  `partial_transpose(...)`, `is_entangled_ppt(...)` (Peres-Horodecki).
- `entanglement_witness.witness_expectation(rho, witness)`, `realignment_criterion(...)`.
- `distillation.werner_state(F)`, `dejmps_distill(lams)`, `bbpssw_distill(F)`,
  `repeater_chain(F, links)`.

```python
import numpy as np
from quantum_debugger.algorithms.entanglement_measures import concurrence
from quantum_debugger.algorithms.entanglement_negativity import negativity
bell = np.outer([1,0,0,1], [1,0,0,1]) / 2.0
concurrence(bell)               # -> 1.0   (maximally entangled)
negativity(bell, dims=(2, 2))   # -> 0.5   (the Bell-state negativity)
```

## What this is verified against

- Entropies/distances: closed forms on maximally-mixed / pure / Bell reference states.
- Holevo, coherence, magic: their definitions computed exactly.
- Entanglement: concurrence `= 1` and negativity `= 1/2` for a Bell state; the PPT / realignment
  criteria against exact partial transposes; distillation against the exact DEJMPS recurrence.
