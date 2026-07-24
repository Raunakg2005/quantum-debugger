# Density-Matrix Simulator (Open Quantum Systems)

`quantum_debugger.density_matrix.DensityMatrix` tracks the full density matrix `rho`,
so it can model **mixed states and noise** — unlike the pure-state `QuantumCircuit`.
Apply unitary gates *and* Kraus noise channels, take partial traces, and read out
purity, populations, expectation values, and state fidelity.

```python
from quantum_debugger.density_matrix import DensityMatrix, depolarizing, amplitude_damping
from quantum_debugger.core.gates import GateLibrary

dm = DensityMatrix(1)
dm.apply_unitary(GateLibrary.H, [0])     # |+>
dm.purity()                               # 1.0 (still pure)

dm.apply_channel(depolarizing(0.5), [0])  # depolarizing noise
dm.purity()                               # 0.625 (now mixed)
```

## Noise channels

Ready-made single-qubit Kraus channels: `bit_flip(p)`, `phase_flip(p)`,
`depolarizing(p)`, `amplitude_damping(gamma)`, `phase_damping(gamma)`.

```python
# Amplitude damping (T1): the excited state decays to the ground state.
dm = DensityMatrix(1)
dm.apply_unitary(GateLibrary.X, [0])          # |1>
dm.apply_channel(amplitude_damping(1.0), [0])
dm.probabilities()                             # [1.0, 0.0]  -- fully relaxed to |0>
```

You can also pass any custom Kraus operator list to `apply_channel`.

## Entanglement & reduced states

```python
import numpy as np
dm = DensityMatrix(2)
dm.apply_unitary(GateLibrary.H, [0])
dm.apply_unitary(GateLibrary.CNOT, [0, 1])     # Bell state (pure, purity 1)

reduced = dm.partial_trace([0])                # trace out qubit 1
reduced.purity()                               # 0.5 -- maximally mixed (entanglement)

dm.entanglement_entropy([0])                   # 1.0 bit -- maximally entangled
```

## Readout

- `purity()` — `Tr(rho^2)`, 1 for a pure state down to `1/2**n` for maximally mixed.
- `probabilities()` — computational-basis populations.
- `expectation(observable)` — `Tr(rho O)` for a Hermitian matrix `O`.
- `fidelity(other)` — Uhlmann state fidelity to another `DensityMatrix` or a pure
  state vector.
- `partial_trace(keep)` — reduced density matrix on the kept qubits.

## Channel quality metrics

How noisy is a channel? Given its Kraus operators, two standard scalar figures of
merit quantify the deviation from a target unitary (default: the identity):

```python
from quantum_debugger.density_matrix import (
    depolarizing, process_fidelity, average_gate_fidelity,
)

average_gate_fidelity(depolarizing(0.1))        # 0.95  == 1 - p/2
process_fidelity(depolarizing(0.1))             # 0.925 == 1 - 3p/4
```

- `process_fidelity(kraus, target=None)` — the entanglement (process) fidelity
  `(1/d^2) * sum_i |Tr(target† K_i)|^2`; equals 1 iff the channel *is* the target
  unitary.
- `average_gate_fidelity(kraus, target=None)` — the fidelity averaged uniformly over
  pure input states, tied to the process fidelity by the exact identity
  `F_avg = (d·F_process + 1)/(d + 1)`.

A perfect gate scores 1; a stray Pauli-`X` error (`[X]`) scores `1/3` — the textbook
average fidelity of a bit flip over the Bloch sphere. Pass `target=U` to score a
channel against the gate it was meant to implement.
