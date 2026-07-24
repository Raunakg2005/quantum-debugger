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

## Continuous-time evolution (Lindblad master equation)

Kraus channels apply noise in discrete jumps; `evolve_lindblad` instead evolves
`rho` in *continuous time* under the Lindblad master equation

```
d rho / dt = -i [H, rho] + sum_k ( L_k rho L_k† - ½ {L_k†L_k, rho} )
```

with a Hamiltonian `H` and collapse (jump) operators `{L_k}`. It is solved exactly
by exponentiating the Liouvillian superoperator — there is no time-step error.

```python
import numpy as np
from quantum_debugger.density_matrix import DensityMatrix

sigma_minus = np.array([[0, 1], [0, 0]], dtype=complex)   # |1> -> |0>
gamma = 0.7                                                # relaxation rate

dm = DensityMatrix(state_vector=np.array([0, 1]))          # start in |1>
dm.evolve_lindblad(np.zeros((2, 2)), [np.sqrt(gamma) * sigma_minus], time=1.3)
dm.rho[1, 1].real         # 0.4025... == exp(-gamma * t)   (T1 relaxation)
```

Common uses:
- **T1 relaxation** — collapse operator `√γ σ_-`; excited population decays `e^{-γt}`.
- **T2 dephasing** — collapse operator `√κ σ_z`; coherences decay `e^{-2κt}` while
  populations are untouched.
- **Closed system** — pass no collapse operators to recover unitary (Rabi) evolution.

Long-time relaxation drives the qubit to its ground state `|0><0|`; the evolution
preserves `Tr(rho) = 1` throughout.

## Channel representations (Choi matrix, CPTP check)

Beyond scalar fidelities, a channel has a full operator representation — the **Choi
matrix** `J = sum_k |K_k>> <<K_k|` (column-stacked vectorization). It is positive
semidefinite iff the channel is completely positive, and its rank is the minimal
number of Kraus operators.

```python
from quantum_debugger.density_matrix import (
    depolarizing, choi_matrix, is_cptp, kraus_rank,
)

is_cptp(depolarizing(0.3))        # True  -- completely positive & trace preserving
kraus_rank(depolarizing(0.3))     # 4     -- full depolarizing needs 4 Kraus ops
kraus_rank([X])                   # 1     -- a unitary is Kraus rank 1
is_cptp([0.5 * I])                # False -- shrinks the trace, not TP
```

- `choi_matrix(kraus)` — the `d² × d²` Jamiolkowski image; the identity channel's
  Choi is rank-1 and proportional to the maximally entangled state.
- `is_cptp(kraus)` — checks CP (Choi PSD) **and** TP (`sum_k K_k† K_k = I`).
- `kraus_rank(kraus)` — the Kraus rank; 1 for unitaries, larger for noisier channels.
