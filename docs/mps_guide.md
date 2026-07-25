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
- `apply_single(gate, qubit)` — exact single-qubit gate.
- `apply_two(gate, qubit)` — neighbouring two-qubit gate, then SVD-truncate the bond
  to `max_bond` (the controlled approximation of DMRG/TEBD).
- `expectation(O, qubit)`, `correlation(A, i, B, j)`, `norm()` — computed by
  `O(n * chi^3)` tensor contraction, never forming the dense state.
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
