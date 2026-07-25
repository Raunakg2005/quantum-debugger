# Matrix Product States: Beyond the Exponential Wall

The dense state-vector simulator stores all `2^n` amplitudes, so it stops around
~25-30 qubits. But most physically interesting states — ground states of local
Hamiltonians, the output of shallow circuits — are only lightly entangled, and a
**matrix product state (MPS)** stores those in `O(n * chi^2)` numbers, where the bond
dimension `chi` measures the entanglement across each cut. That is the difference
between 25 qubits and hundreds.

## The idea

An MPS writes the amplitude as a product of small tensors:

```
psi(s_0, ..., s_{n-1}) = A[0]^{s_0} A[1]^{s_1} ... A[n-1]^{s_{n-1}}
```

Each `A[i]` has shape `(chi_left, 2, chi_right)`. The bond dimension is 1 for a
product state and grows with entanglement — but for area-law states it stays bounded.

## Usage

```python
import numpy as np
from quantum_debugger.mps import MPS
from quantum_debugger.core.gates import GateLibrary

# Build a 100-qubit GHZ state -- 2^100 amplitudes, held at bond dimension 2.
n = 100
mps = MPS.zero_state(n, max_bond=4)
mps.apply_single(GateLibrary.H, 0)
for q in range(n - 1):
    mps.apply_two(GateLibrary.CNOT, q)

mps.max_bond_dimension()                    # 2
Z = np.diag([1, -1]).astype(complex)
mps.correlation(Z, 0, Z, n - 1)             # 1.0 -- the two ends are perfectly correlated
mps.expectation(Z, 50)                      # 0.0 -- each qubit is unbiased
```

## Operations

- `MPS.zero_state(n, max_bond)` / `MPS.from_statevector(psi, max_bond)` — construct
  (the latter by exact sequential SVD).
- `MPS.from_circuit(circuit, max_bond)` — run a `QuantumCircuit` on the MPS engine
  (1- and 2-qubit gates, any connectivity via SWAPs). Matches the state-vector result
  exactly; decompose 3+ qubit gates first. Driving the `MPS` directly (rather than
  through a `QuantumCircuit`, which allocates a dense state) is how you exceed ~25
  qubits.
- `apply_single(gate, qubit)` — exact single-qubit gate.
- `apply_two(gate, qubit)` — neighbouring two-qubit gate, then SVD-truncate the bond
  to `max_bond` (the controlled approximation of DMRG/TEBD).
- `apply_two_long_range(gate, a, b)` — a two-qubit gate on *any* pair, via a SWAP
  ladder (swap together, apply, swap back), so arbitrary connectivity is supported.
- `expectation(O, qubit)`, `correlation(A, i, B, j)`, `expectation_pauli(string)`,
  `norm()` — computed by `O(n * chi^3)` tensor contraction, never forming the dense
  state. `expectation_pauli` measures any multi-qubit Pauli observable (e.g. a
  20-qubit GHZ's `<X^20> = 1`).
- `energy(terms)` — `<psi|H|psi>` for a Hamiltonian in `(coeff, pauli_string)` form
  (the `pauli_decompose`/VQE format), so molecular, Fermi-Hubbard, or spin
  Hamiltonians can be evaluated on a large MPS.
- `sample(shots, seed)` — draw measurement outcomes by exact sequential conditional
  sampling (right environments), `O(shots * n * chi^2)`; the distribution is the exact
  Born rule, verified against the dense state for small systems.
- `bond_entropies()` / `entanglement_entropy(bond)` — the entanglement entropy across
  each cut, from the Schmidt spectrum after canonicalization; matches the dense value
  exactly and scales to large systems (a 60-qubit GHZ's profile is instant).
- `overlap(other)` / `fidelity(other)` — inner product and state fidelity between two
  MPS by `O(n * chi^3)` double-layer contraction, matching the dense inner product.
- `bond_dimensions()`, `max_bond_dimension()` — inspect the entanglement structure.
- `to_statevector()` — contract back to a dense vector (small `n` only).

## Correctness

Every MPS operation is verified against the dense state-vector simulator for small
systems: exact state roundtrip, single- and two-qubit gates (including asymmetric
random unitaries) agreeing to `1e-10`, and expectation values matching exactly. The
bond dimension faithfully tracks entanglement — 1 for product states, 2 for GHZ — and
`apply_two` truncation keeps `chi <= max_bond` so a random deep circuit stays bounded.
The approximation is only invoked when a two-qubit gate would push the bond past
`max_bond`; below that, the MPS is exact.

## TEBD: dynamics on large systems

Time evolution comes for free once you can apply two-site gates: Trotterize
`e^{-iHt}` into nearest-neighbour bond gates and sweep them across the MPS. This is
**TEBD** (time-evolving block decimation):

```python
from quantum_debugger.algorithms import tebd_magnetization

# Quench a 30-qubit Ising chain -- far beyond the dense state vector.
r = tebd_magnetization(n=30, time=0.5, steps=30, field=0.5, max_bond=12)
r["z_profile"]   # <Z_i> on each of the 30 sites
r["max_bond"]    # the bond dimension the entanglement demanded (<= 12)
```

Each Trotter step applies `exp(-i h_{j,j+1} dt)` on the even bonds, then the odd
bonds, with the SVD truncation keeping the bond bounded. It reproduces exact
state-vector evolution to fidelity > 0.9999 on small chains (and improves with finer
steps), while scaling to system sizes the dense engine cannot touch — as long as the
generated entanglement keeps the bond dimension manageable.

## Ground states by imaginary-time TEBD

The same bond-gate machinery finds *ground states*: run TEBD in imaginary time
(`e^{-h*dtau}` instead of `e^{-i*h*dt}`) and the state cools into the ground state —
a DMRG-style variational search that scales to large chains:

```python
from quantum_debugger.algorithms import imaginary_tebd_ground_state

# Small chain: check against exact diagonalization.
imaginary_tebd_ground_state(8, j_coupling=1.0, field=1.0)["error"]   # < 5e-3

# 24-qubit ground state -- beyond any dense diagonalizer.
r = imaginary_tebd_ground_state(24, 1.0, 1.0, dtau=0.05, steps=150, max_bond=12)
r["energy"]   # variational ground energy
r["bond"]     # bond dimension the ground state needed
```

Each step applies `e^{-h_{j,j+1} dtau}` on the bonds and renormalizes; excited
components decay faster than the ground state, so the MPS converges to it. The result
is a strict variational upper bound on the true ground energy, matches exact
diagonalization where that is feasible, and stays accurate as the chain grows (the
energy per site is extensive) — the tensor-network route to many-body ground states.
