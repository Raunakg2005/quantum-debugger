# Quantum Algorithms Library

`quantum_debugger.algorithms` provides textbook quantum algorithms as
first-class, tested functions built on the state-vector simulator. Every
algorithm is genuinely gate-based and verified against its known outcome.

```python
from quantum_debugger.algorithms import (
    qft, grover_search, estimate_phase,
    bernstein_vazirani, deutsch_jozsa,
    quantum_walk, quantum_counting, amplitude_estimation,
)
```

## Quantum Fourier Transform

`qft(n_qubits, inverse=False)` returns a circuit implementing the QFT, which
matches the analytic discrete Fourier transform matrix.

```python
from quantum_debugger.algorithms import qft, qft_matrix

circuit = qft(3)                 # QFT on 3 qubits
inverse = qft(3, inverse=True)   # inverse QFT
```

You can also append a QFT to part of a larger register with
`apply_qft(circuit, qubits=...)` / `apply_inverse_qft(...)`.

## Grover's Search

Find marked states in an unstructured space of size `N = 2**n_qubits` in about
`(pi/4) * sqrt(N/M)` iterations.

```python
result = grover_search(n_qubits=3, marked_states=5)
result["best_state"]            # 5
result["success_probability"]   # ~0.94
```

`marked_states` may be a single index or a list. `grover(n_qubits, marked)`
returns the raw circuit if you want to run/inspect it yourself.

## Quantum Phase Estimation

Estimate the phase of an eigenvalue `e^{2*pi*i*phi}`. The demo estimates the
phase of the gate `P(theta)` (eigenstate `|1>`):

```python
import numpy as np
result = estimate_phase(2 * np.pi * 0.25, n_counting=4)
result["phase"]   # 0.25
```

## Bernstein-Vazirani & Deutsch-Jozsa

```python
bernstein_vazirani("1011")           # -> [1, 1, 0, 1]  (recovered in one query)

from quantum_debugger.algorithms import constant_oracle, balanced_oracle
deutsch_jozsa(constant_oracle(1), n=3)   # -> "constant"
deutsch_jozsa(balanced_oracle(3), n=3)   # -> "balanced"
```

## Quantum Walk

A discrete-time coined walk on a cycle. Unlike a classical random walk it
spreads *ballistically* (std ~ steps rather than sqrt(steps)).

```python
result = quantum_walk(n_position_qubits=5, steps=16)
result["std"]            # ~7.5  (classical would be ~4)
result["distribution"]   # probability per site
```

## Amplitude Estimation & Counting

Estimate the number of marked states without knowing it in advance.

```python
# QPE-based counting
quantum_counting(n_qubits=4, marked=[1, 5, 9], n_counting=5)["estimated_count"]  # ~3

# Maximum-likelihood amplitude estimation (QPE-free, more accurate)
amplitude_estimation(4, marked=[1, 5, 9])["estimated_count"]  # ~3.0
```

## Amplitude Amplification

Grover generalized to any state preparation `A` (Grover is the case `A = H^n`).

```python
from quantum_debugger.algorithms import amplitude_amplification
from quantum_debugger.core.circuit import QuantumCircuit

A = QuantumCircuit(3)
for q in range(3):
    A.ry(0.6, q)                              # |111> has a tiny amplitude here
result = amplitude_amplification(A, marked=[7])
result["initial_probability"]   # ~0.001
result["success_probability"]   # ~1.0
```

## Iterative Phase Estimation

Single-ancilla, bit-by-bit phase estimation (only 2 qubits total).

```python
from quantum_debugger.algorithms import iterative_phase_estimation
import numpy as np

iterative_phase_estimation(2 * np.pi * 0.375, n_bits=4)["phase"]   # 0.375
```

## Swap Test

Estimate the squared overlap `|<psi|phi>|^2` between two states with one ancilla
and controlled-SWAP gates.

```python
from quantum_debugger.algorithms import swap_test

swap_test(psi, phi)["overlap"]   # |<psi|phi>|^2
```

## HHL -- Quantum Linear Systems

Solve `A x = b` for a Hermitian `A`. The solution register ends up in the state
`|x> proportional to A^{-1} |b>`.

```python
import numpy as np
from quantum_debugger.algorithms import hhl

A = np.array([[1.5, 0.5], [0.5, 1.5]])   # eigenvalues 1 and 2
result = hhl(A, b=[1, 0], n_clock=3)
result["fidelity"]        # ~1.0 vs the classical A^-1 b
result["solution"]        # normalized |x>
```

## Quantum Teleportation

Move an unknown single-qubit state from one qubit to another using a shared Bell
pair and two classical bits (the X/Z feedforward corrections).

```python
import numpy as np
from quantum_debugger.algorithms import teleport

psi = np.array([0.6, 0.8], dtype=complex)
result = teleport(psi)
result["fidelity"]      # ~1.0  (qubit 2 now holds psi)
result["measurement"]   # the two Bell-measurement bits
```

## Superdense Coding

The dual of teleportation: send two classical bits by transmitting a single
qubit (half of a pre-shared Bell pair).

```python
from quantum_debugger.algorithms import superdense_coding

superdense_coding((1, 0))["decoded"]   # (1, 0) -- both bits recovered
```

## Shor's Algorithm -- Period Finding & Factoring

Quantum phase estimation on the modular-multiplication unitary
`U|y> = |a*y mod N>` recovers the period `r` of `a^x mod N` via a
continued-fraction expansion of the measured phase. With `r`, classical
post-processing (`gcd(a^{r/2} +/- 1, N)`) yields a nontrivial factor of `N`.

```python
from quantum_debugger.algorithms import period_finding, shor_factor

period_finding(7, 15)["period"]        # 4   (7^4 = 1 mod 15)
shor_factor(15, a=7)["factors"]        # (3, 5)
shor_factor(21, a=2)["factors"]        # (3, 7)
```

## Quantum Metrology (Heisenberg-Limited Sensing)

A GHZ probe accumulates phase N times faster than independent qubits, so its
quantum Fisher information scales as `N**2` (the Heisenberg limit) versus `N` for a
product state (the standard quantum limit) -- the best phase uncertainty scales as
`1/N` instead of `1/sqrt(N)`.

```python
from quantum_debugger.algorithms import phase_sensitivity, parity_signal

r = phase_sensitivity(4)
r["qfi_ghz"]            # 16.0  (= N**2, Heisenberg)
r["qfi_product"]       # 4.0   (= N,    standard quantum limit)
r["advantage"]         # 4.0   (= N)
r["delta_phi_ghz"]     # 0.25  (= 1/N)

parity_signal(4, phi)  # cos(4*phi) -- the GHZ interferometer oscillates N x faster
```

## Simon's Algorithm

Recover the hidden XOR mask `s` of a 2-to-1 function (`f(x) = f(y)` iff
`y = x XOR s`) with O(n) quantum queries -- an exponential speedup over the
classical O(2^(n/2)). Each circuit run yields a `y` with `y . s = 0 (mod 2)`;
collecting `n-1` independent constraints and solving the GF(2) null space gives `s`.

```python
from quantum_debugger.algorithms import simon

simon(s=5, n=3)["secret"]         # 5   -- recovers the planted mask

# Or supply your own 2-to-1 function:
simon(n=3, f=lambda x: min(x, x ^ 3))["secret"]   # 3
```

## Entangled State Preparation

Genuine gate-based circuits for the canonical multi-qubit entangled states.

```python
from quantum_debugger.algorithms import ghz_state, w_state, graph_state

ghz_state(4)              # (|0000> + |1111>) / sqrt(2)
w_state(4)                # (|1000> + |0100> + |0010> + |0001>) / 2
graph_state([(0,1),(1,2)], 3)   # cluster/graph state (H on all, CZ per edge)
```

`ghz_state` uses a Hadamard + CNOT chain; `w_state` distributes a single
excitation evenly with a cascade of Givens rotations; `graph_state` is the MBQC
resource state whose stabilizers are `X_i prod_{j~i} Z_j`.

## QAOA MaxCut Solver

An application-level solver that returns an actual MaxCut *solution* -- the node
partition, its cut value, the brute-force optimum, and the approximation ratio --
rather than just an expected cost. Random restarts make it robust.

```python
from quantum_debugger.algorithms import solve_maxcut

graph = [(0, 1), (1, 2), (2, 3), (3, 0)]     # 4-cycle
r = solve_maxcut(graph, p=3, restarts=6)
r["partition"]             # e.g. [1, 0, 1, 0]  -- the two node sets
r["cut_value"]             # 4
r["optimal_cut"]           # 4  (brute-force optimum)
r["approximation_ratio"]   # 1.0
```

`brute_force_maxcut(graph, n)` gives the exact optimum for small graphs.

## Quantum Arithmetic (Draper QFT Adder)

Add numbers directly in the Fourier basis -- QFT the register, apply phase
rotations proportional to the addend, then inverse QFT. No carry ancillas.

```python
from quantum_debugger.algorithms import qft_add, quantum_adder

qft_add(13, 7, n_bits=4)         # 4   -- (13 + 7) mod 16, constant addend
quantum_adder(9, 6, n_bits=4)    # 15  -- adds two quantum registers |a>|b> -> |a+b>|b>
```

Both compute `(a + b) mod 2**n_bits` and are exact for every input pair.

## Randomized Benchmarking

Estimate the average error per Clifford gate independently of state-prep and
measurement (SPAM) errors. Random Clifford sequences are applied, then the single
recovery Clifford that inverts the whole sequence; without noise the qubit returns
to `|0>` exactly. Under a per-gate depolarizing channel of strength `lambda`, the
survival probability decays as `S(m) = A p^m + B` with `p ≈ 1 - lambda`, and the
average gate error is `(1 - p)/2`.

```python
from quantum_debugger.algorithms import randomized_benchmarking

r = randomized_benchmarking(depolarizing=0.03, shots=80)
r["p"]              # ~0.97   (= 1 - lambda)
r["average_error"]  # ~0.015  (= lambda / 2)
r["survival"]       # decaying survival probability per sequence length
```

`single_qubit_clifford_group()` returns the 24 single-qubit Clifford unitaries.
With `depolarizing=0`, every sequence survives with probability 1.0, confirming the
recovery-Clifford inversion is exact.

## Gate Decomposition / Synthesis

Break arbitrary unitaries into elementary rotations and CNOTs. Every routine is
self-verifying -- the returned pieces reconstruct the input to machine precision.

```python
import numpy as np
from quantum_debugger.algorithms import (
    zyz_decompose, abc_decomposition, kak_decompose, canonical_coordinates,
)

# Any 1-qubit gate as U = e^{i a} RZ(b) RY(c) RZ(d).
H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
d = zyz_decompose(H)
d["reconstruction_error"]      # ~1e-16

# ABC form: lets a controlled-U be built from CNOTs + single-qubit gates (ABC = I).
abc_decomposition(H)["abc_is_identity"]   # ~1e-16

# Two-qubit Cartan (KAK): U = (A1 ⊗ A0) · exp(i(a XX + b YY + c ZZ)) · (B1 ⊗ B0).
CNOT = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex)
k = kak_decompose(CNOT)
k["coefficients"]              # (~pi/4, 0, 0)  -- CNOT's interaction content
k["reconstruction_error"]      # ~1e-16

# Weyl-chamber coordinates capture a gate's entangling power.
canonical_coordinates(CNOT)    # ~ (pi/4, 0, 0)
```

The KAK routine uses the magic basis plus a deterministic nested joint
diagonalization, so it is robust even for degenerate gates (SWAP, iSWAP, pure
local gates) -- verified to reconstruct 1000/1000 random SU(4) unitaries.

## Hamiltonian Simulation (Trotter-Suzuki)

Simulate time evolution `exp(-i H t)|psi>` for a Hamiltonian written as a sum of
weighted Pauli strings, using genuine 1- and 2-qubit gates (basis change +
CNOT-ladder + RZ per term). Higher Trotter order and more steps reduce the error;
the result is checked against the exact matrix exponential.

```python
from quantum_debugger.algorithms import trotter_evolve

# Transverse-field Ising model on 3 qubits.
H = [(1.0, "ZZI"), (1.0, "IZZ"), (0.5, "XII"), (0.5, "IXI"), (0.5, "IIX")]

trotter_evolve(H, time=1.0, steps=4,  order=1)["fidelity"]   # ~0.98
trotter_evolve(H, time=1.0, steps=4,  order=2)["fidelity"]   # ~0.9999 (order 2 wins)
trotter_evolve(H, time=1.0, steps=50, order=2)["fidelity"]   # ~1.0
```

`pauli_string[q]` (one of `I/X/Y/Z`) acts on qubit `q`. `trotter_circuit(...)`
returns the raw gate list, and `hamiltonian_matrix(terms, n)` builds the dense
operator if you want to inspect it.

## Quantum Error Correction

Genuine, gate-based stabilizer codes. A logical qubit is encoded across several
physical qubits, a Pauli error is injected, the code's stabilizer generators are
measured with ancillas to extract a *syndrome*, and the matching recovery Pauli
is applied. The logical fidelity returns to 1.0.

```python
from quantum_debugger.algorithms import bit_flip_code, phase_flip_code, shor_code

# 3-qubit bit-flip code: corrects any single X error.
bit_flip_code(0.6, 0.8, error_qubit=1)["syndrome"]    # (1, 1) -> qubit 1 flipped
bit_flip_code(0.6, 0.8, error_qubit=1)["fidelity"]    # 1.0

# 3-qubit phase-flip code: same idea in the Hadamard basis, corrects a Z error.
phase_flip_code(0.6, 0.8, error_qubit=2)["fidelity"]  # 1.0

# 9-qubit Shor code: corrects an ARBITRARY single-qubit error (X, Y, or Z).
shor_code(0.6, 0.8, error_qubit=4, error_type="Y")["fidelity"]   # 1.0
```

The syndrome is extracted by measuring each stabilizer with an ancilla
(`|0> -> H -> controlled-Pauli string -> H -> measure`), so no error information
leaks about the encoded amplitudes -- exactly as real QEC requires.

## State Tomography

Reconstruct the density matrix of a small (<= 3 qubit) state from simulated
Pauli measurements.

```python
from quantum_debugger.tomography import state_tomography
from quantum_debugger.core.circuit import QuantumCircuit

qc = QuantumCircuit(2)
qc.h(0); qc.cnot(0, 1)
result = state_tomography(qc.get_statevector().state_vector, shots=8000)
result["density_matrix"]   # reconstructed 4x4 rho
result["fidelity"]          # ~1.0 vs the true Bell state
```
