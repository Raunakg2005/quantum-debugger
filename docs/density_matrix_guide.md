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

## Coherence measures

Superposition is a resource, and coherence measures quantify how much of it a state
holds in the computational basis:

```python
import numpy as np
from quantum_debugger.density_matrix import DensityMatrix, phase_damping

plus = DensityMatrix(state_vector=np.array([1, 1]) / np.sqrt(2))
plus.l1_coherence()                  # 1.0  -- sum of off-diagonal magnitudes
plus.relative_entropy_coherence()    # 1.0  -- S(diag rho) - S(rho), in bits

plus.apply_channel(phase_damping(1.0), [0])
plus.l1_coherence()                  # 0.0  -- dephasing kills coherence
```

- `l1_coherence()` — the sum of `|rho_ij|` over off-diagonal entries; 0 for any
  diagonal (incoherent) state, up to `2**n - 1` for a maximally coherent state.
- `relative_entropy_coherence()` — the distance to the nearest incoherent state,
  `S(diag rho) - S(rho)`; a Bell state and `|+>` each carry exactly 1 bit.

## Mixed-state entanglement (negativity)

Entanglement entropy only measures entanglement for *pure* states. For a general
mixed `rho`, the **negativity** — built from the Peres-Horodecki partial transpose —
certifies and quantifies entanglement:

```python
import numpy as np
from quantum_debugger.density_matrix import DensityMatrix

bell = DensityMatrix(state_vector=np.array([1, 0, 0, 1]) / np.sqrt(2))
bell.negativity([0])               # 0.5  -- max for a two-qubit state
bell.logarithmic_negativity([0])   # 1.0  bit

# Werner state: entangled iff p > 1/3
p = 0.5
rho = p * bell.rho + (1 - p) * np.eye(4) / 4
DensityMatrix(rho=rho).negativity([0])   # 0.125 == max(0, (3p-1)/4)
```

- `partial_transpose(qubits)` — transpose the indices of a subsystem only.
- `negativity(qubits)` — `(||rho^{T_A}||_1 - 1)/2`; `> 0` certifies entanglement
  across the cut (exact for 2×2 and 2×3 systems by the PPT criterion).
- `logarithmic_negativity(qubits)` — `log2(2N + 1)`, an entanglement monotone and an
  upper bound on distillable entanglement.

## Total correlations (quantum mutual information)

The quantum mutual information `I(A:B) = S(A) + S(B) - S(AB)` captures *all*
correlations across a cut — classical and quantum together:

```python
import numpy as np
from quantum_debugger.density_matrix import DensityMatrix

bell = DensityMatrix(state_vector=np.array([1, 0, 0, 1]) / np.sqrt(2))
bell.mutual_information([0])        # 2.0 bits -- maximal for a qubit pair

rho = np.zeros((4, 4)); rho[0, 0] = rho[3, 3] = 0.5   # classical (|00> or |11>)
DensityMatrix(rho=rho).mutual_information([0])         # 1.0 bit
```

A Bell pair carries 2 bits (twice its 1 bit of entanglement, reflecting both
classical and quantum correlation); a classically correlated mixture carries 1 bit;
a product state carries 0.

## Quantum discord: correlation beyond entanglement

Entanglement is not the whole story of quantum correlation. **Discord** measures
the part of the mutual information that no local measurement can extract
classically:

```python
import numpy as np
from quantum_debugger.density_matrix import DensityMatrix, quantum_discord
from quantum_debugger.algorithms import bell_diagonal_state

bell = DensityMatrix(state_vector=np.array([1, 0, 0, 1]) / np.sqrt(2))
quantum_discord(bell)          # 1.0 -- maximal

# A SEPARABLE Werner state (F = 0.4, zero negativity):
dm = DensityMatrix(rho=bell_diagonal_state(0.4, 0.2, 0.2, 0.2))
dm.negativity([0])             # 0.0   -- no entanglement
quantum_discord(dm)            # 0.049 -- but genuinely quantum correlation!
```

`D = S(B) - S(AB) + min over measurements of the average conditional entropy`,
optimized over the Bloch sphere. Verified against Luo's closed form for
Bell-diagonal states; for pure states it reduces exactly to the entanglement
entropy, and for classical mixtures it vanishes.

## T1, T2, and why T2 <= 2 T1

Every real qubit's datasheet lists `T1` (energy relaxation) and `T2` (coherence).
They are not independent:

```python
from quantum_debugger.density_matrix import relaxation_times

r = relaxation_times(gamma1=0.5, gamma_phi=0.3)
r["T1"]                  # 2.0     = 1/gamma1
r["T2"]                  # 1.818   -- shorter than 2*T1
r["identity_residual"]   # ~1e-16  : 1/T2 == 1/(2*T1) + 1/T_phi exactly
r["t2_le_2t1"]           # True    -- always

relaxation_times(0.5, 0.0)["T2"]   # 4.0 == 2*T1: no pure dephasing
relaxation_times(0.5, 5.0)         # dephasing-dominated: T2 < T1
```

Both times are extracted from the exact Lindblad evolution (`evolve_lindblad`) —
the excited population decays as `e^{-gamma1 t}` and the `|+>` coherence as
`e^{-(gamma1/2 + gamma_phi) t}`, which is precisely the relation above.

## Concurrence & entanglement of formation

For two qubits, entanglement of a *mixed* state has an exact closed form
(Wootters 1998), via the concurrence:

```python
import numpy as np
from quantum_debugger.density_matrix import DensityMatrix
from quantum_debugger.algorithms import werner_state

bell = DensityMatrix(state_vector=np.array([1, 0, 0, 1]) / np.sqrt(2))
bell.concurrence()                  # 1.0
bell.entanglement_of_formation()    # 1.0 bit -- costs one Bell pair to make

DensityMatrix(rho=werner_state(0.75)).concurrence()   # 0.5  == 2F - 1
DensityMatrix(rho=werner_state(0.45)).concurrence()   # 0.0  -- separable
```

- `concurrence()` — `max(0, l1 - l2 - l3 - l4)` from the eigenvalues of the
  spin-flipped matrix `rho (Y x Y) rho* (Y x Y)`; 0 iff separable, 1 for Bell states,
  `2|ad - bc|` for pure states.
- `entanglement_of_formation()` — `h((1 + sqrt(1 - C^2))/2)` in bits: the number of
  Bell pairs per copy needed to prepare the state by LOCC. Reduces to the
  entanglement entropy on pure states.

Together with `negativity` (any dimensions, but only a bound) and
`quantum_discord` (correlations beyond entanglement), this completes the
two-qubit correlation toolbox.

## Channel capacity: how much quantum information survives?

The coherent information `I_c = S(N(rho)) - S(E)` measures the qubits-per-use a
channel can protect — computed here from first principles (purify the input, send
the system half through the channel, read off the environment entropy):

```python
import numpy as np
from quantum_debugger.algorithms import coherent_information, amplitude_damping_capacity
from quantum_debugger.density_matrix import amplitude_damping

coherent_information(amplitude_damping(0.1), np.diag([0.5, 0.5]))  # 0.706 bits

amplitude_damping_capacity(0.0)["capacity"]    # 1.0  -- noiseless
amplitude_damping_capacity(0.25)["capacity"]   # 0.47 -- degradable regime
amplitude_damping_capacity(0.5)["capacity"]    # 0.0  -- EXACTLY zero from here on
```

The amplitude-damping results match the known closed form `h((1-g)p) - h(gp)`
exactly. The vanishing at `g = 1/2` is forced by no-cloning: there the environment
receives a copy of everything the receiver gets (the channel is antidegradable),
so any surviving quantum capacity would clone. The antisymmetry
`I_c(g) = -I_c(1-g)` is verified too.

## Stinespring dilation: all noise is an environment

Every channel in this module can be written as a *unitary* interaction with an
extra environment that is then thrown away — Stinespring's theorem, made
constructive:

```python
import numpy as np
from quantum_debugger.density_matrix import (
    stinespring_isometry, apply_channel_dilated, depolarizing,
)

V = stinespring_isometry(depolarizing(0.3))   # isometry V: system -> system x env
V.conj().T @ V                                # identity -- trace preserving

rho = np.array([[0.7, 0.3], [0.3, 0.3]], dtype=complex)
apply_channel_dilated(depolarizing(0.3), rho) # == dm.apply_channel(depolarizing(0.3))
```

`V|psi> = sum_k K_k|psi>|k>_env`; tracing out the environment gives back the Kraus
channel exactly (verified for every built-in channel). The dilated global state is
*pure* — decoherence of the system is nothing but entanglement with the
environment, and "measuring" that environment is what the Kraus operators secretly
describe.
