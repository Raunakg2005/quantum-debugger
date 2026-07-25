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

## Quantum Spectroscopy (Arbitrary-Operator QPE)

Estimate the eigenphase of any unitary, or the eigenvalue of any Hermitian
operator, with phase estimation on a supplied eigenstate -- verified against
classical diagonalization.

```python
import numpy as np
from quantum_debugger.algorithms import unitary_eigenphase, hermitian_eigenvalue

# Eigenphase of a unitary (|1> is the eigenstate of P(2*pi*0.375)).
P = np.array([[1, 0], [0, np.exp(2j * np.pi * 0.375)]], dtype=complex)
unitary_eigenphase(P, [0, 1], n_counting=8)["phase"]        # 0.375

# Eigenvalue of a Hermitian operator (quantum spectroscopy).
H = np.array([[2.0, 0.5], [0.5, 1.0]], dtype=complex)
evals, evecs = np.linalg.eigh(H)
hermitian_eigenvalue(H, evecs[:, 0], n_counting=10)["eigenvalue"]   # ~0.793
```

## Deutsch, Bernstein-Vazirani & Deutsch-Jozsa

```python
from quantum_debugger.algorithms import deutsch

# Deutsch's algorithm (1985): constant vs balanced 1-bit function in ONE query.
deutsch(lambda x: 0)        # -> "constant"
deutsch(lambda x: x)        # -> "balanced"

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

## Entanglement Swapping

Entangle two qubits that have never interacted -- the primitive behind quantum
repeaters. Two independent Bell pairs (qubits 0-1 and 2-3) are prepared; a Bell
measurement on the inner qubits (1, 2) plus X/Z feedforward leaves the outer
qubits (0, 3) in the Bell state `|Phi+>`.

```python
from quantum_debugger.algorithms import entanglement_swap

entanglement_swap()["fidelity"]   # 1.0  -- qubits 0 and 3 are now maximally entangled
```

## Superdense Coding

The dual of teleportation: send two classical bits by transmitting a single
qubit (half of a pre-shared Bell pair).

```python
from quantum_debugger.algorithms import superdense_coding

superdense_coding((1, 0))["decoded"]   # (1, 0) -- both bits recovered
```

## Entanglement Distillation (BBPSSW)

Real channels deliver *noisy* Bell pairs. Distillation converts two noisy pairs
into one better pair using only local operations and classical communication —
the primitive behind quantum repeaters:

```python
from quantum_debugger.algorithms import bbpssw_distill, distillation_rounds

r = bbpssw_distill(0.7)        # two Werner pairs of fidelity 0.7
r["fidelity"]                  # 0.7353 -- the kept pair is better
r["success_probability"]       # 0.68   -- kept iff the two measurements agree
r["analytic"]                  # matches the Bennett et al. closed form exactly

distillation_rounds(0.7, 0.99)["rounds"]   # rounds of 2-to-1 to reach F = 0.99
```

Each party CNOTs their half of pair 1 onto their half of pair 2, both measure
pair 2, and they keep pair 1 iff the outcomes agree. `F = 1/2` is the threshold:
above it every round improves the pair, below it distillation only makes things
worse — matching exactly the Werner state's entanglement threshold (checked via
negativity).

### DEJMPS: distilling any Bell-diagonal state

BBPSSW assumes Werner inputs. The **DEJMPS** protocol (Deutsch et al., 1996) adds
local `Rx(±pi/2)` rotations before the bilateral CNOTs and handles *any*
Bell-diagonal state — converging faster because it never throws the noise
asymmetry away:

```python
from quantum_debugger.algorithms import dejmps_distill, dejmps_rounds

# All the noise concentrated in one Bell component (fidelity still 0.7):
r = dejmps_distill((0.7, 0.3, 0.0, 0.0))
r["fidelity"]              # 0.845  -- vs 0.735 for BBPSSW at the same F!
r["coefficients"]          # all four output Bell weights, == the exact recurrence

dejmps_rounds((0.7, 0.3, 0.0, 0.0), 0.99)["rounds"]   # fewer rounds than BBPSSW
```

The 4-qubit circuit reproduces the four-coefficient DEJMPS recurrence to machine
precision, and on Werner inputs it reduces exactly to BBPSSW — the two protocols
agree where their domains overlap.

## Noisy Entanglement Swapping & Repeater Chains

Distillation's partner primitive. A middle node holding halves of two noisy pairs
performs a Bell measurement, splicing them into one long-distance pair between
parties that never interacted:

```python
from quantum_debugger.algorithms import entanglement_swap_noisy, repeater_chain

entanglement_swap_noisy(0.9, 0.9)["fidelity"]   # 0.8133 = F1*F2 + (1-F1)(1-F2)/3
entanglement_swap_noisy(0.7, 0.6)["fidelity"]   # 0.46 -- SEPARABLE! (< 1/2)

r = repeater_chain(0.9, links=8)                # 8 links, 7 swaps
r["fidelity"]                                   # decays toward 1/4 (fully mixed)
r["entangled"]                                  # False -- chain too long
```

Two striking exact results: swapping two *entangled* pairs can produce a
*separable* pair (0.7 and 0.6 above), and an n-link chain's fidelity decays
geometrically toward 1/4. That is why real repeaters interleave the two
primitives: swap to extend distance, distill (`bbpssw_distill`) to restore
fidelity — and the tests confirm one round of BBPSSW rescues a degraded chain.

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

## Grover Adaptive Minimization

Find the input minimizing a cost function using Grover search as a subroutine
(Durr-Hoyer). Each round marks the states beating the current best and uses Grover
(with a randomized iteration count, BBHT-style) to sample one, ratcheting the
threshold down to the global minimum with O(sqrt(N)) expected queries.

```python
from quantum_debugger.algorithms import grover_minimize

r = grover_minimize(lambda x: (x - 11) ** 2, n_qubits=4)
r["argmin"]          # 11
r["min_value"]       # 0
r["found_optimum"]   # True  (matches the brute-force minimum)
```

The randomized iteration count is essential -- a fixed "optimal" count over-rotates
and stalls when more than half the states are marked (the early rounds).

## Multi-Controlled-X Synthesis

Decompose Toffoli (CCX) and general n-controlled-X gates into the elementary
`H / T / T-dagger / CNOT` set. The n-control MCX uses a ladder of Toffolis with
`n_controls - 1` clean ancillas (returned to `|0>`).

```python
from quantum_debugger.algorithms import toffoli_gates, mcx_gates, apply_gates
from quantum_debugger.core.quantum_state import QuantumState

# Toffoli on qubits (control 0, control 1, target 2) as H/T/CNOT.
gates = toffoli_gates(0, 1, 2)

# 4-controlled X: controls 0-3, target 4, ancillas 5-7.
gates = mcx_gates(controls=[0, 1, 2, 3], target=4, ancillas=[5, 6, 7])
apply_gates(QuantumState(8), gates)   # flips qubit 4 iff qubits 0-3 are all 1
```

`fredkin_gates(control, a, b)` decomposes the controlled-SWAP (swap `a`, `b` iff
`control` is 1) into a Toffoli sandwiched by two CNOTs.

All decompositions are exact (verified against the ideal CCX / CSWAP / MCX action
for every control input, with ancillas restored to `|0>`).

## Grover-Based Constraint / SAT Solver

Use Grover's search to find an input satisfying an arbitrary boolean predicate. The
predicate defines the marked set; Grover amplifies it and returns the most likely
satisfying assignment (verified classically).

```python
from quantum_debugger.algorithms import grover_solve

# Find the unique x with x == 5 on 3 bits.
r = grover_solve(lambda x: x == 5, n_qubits=3)
r["solution"]               # 5
r["bits"]                   # [1, 0, 1]  (qubit 0 = LSB)
r["success_probability"]    # > 0.9

# Any constraint works, e.g. "exactly two bits set".
grover_solve(lambda x: bin(x).count("1") == 2, n_qubits=4)["satisfies"]   # True
```

## Variational Ground-State Solver (VQE)

A self-contained hardware-efficient VQE for any Pauli-sum Hamiltonian. A layered
`RY + CNOT` ansatz is optimized (gradient-based BFGS by default) to minimize the
energy; the result is checked against the exact ground energy (smallest eigenvalue).

```python
from quantum_debugger.algorithms import (
    variational_ground_state, tfim_hamiltonian, heisenberg_hamiltonian,
)

# Transverse-field Ising model on 4 spins.
r = variational_ground_state(tfim_hamiltonian(4, field=1.0))
r["energy"]         # VQE estimate
r["exact_energy"]   # exact ground energy
r["error"]          # ~1e-11 (machine precision)

# Isotropic Heisenberg chain.
variational_ground_state(heisenberg_hamiltonian(4))["error"]   # ~1e-12
```

The gradient-based optimizer reaches the exact ground energy to near machine
precision for TFIM/Heisenberg chains up to ~4 qubits (and ~1e-6 at 5 qubits). The
Hamiltonian uses the same `(coeff, pauli_string)` format as the Trotter module, so
you can pass any spin Hamiltonian. The VQE energy is a variational upper bound on
the true ground energy.

## BB84 Quantum Key Distribution

The first quantum cryptography protocol. Alice encodes random bits in random bases
(Z or X); Bob measures in his own random bases; where the bases agree, the bits
agree -- a shared secret key. An eavesdropper who measures in the wrong basis
disturbs the qubits and injects a detectable ~25% error rate.

```python
from quantum_debugger.algorithms import bb84

clean = bb84(n_bits=128, eavesdropper=False)
clean["qber"]        # 0.0  -- sifted keys match exactly
clean["secure"]      # True

tapped = bb84(n_bits=256, eavesdropper=True)
tapped["qber"]       # ~0.25  -- intercept-resend is detected
tapped["secure"]     # False
```

Every qubit is genuinely prepared and measured on the simulator, so the security
guarantee comes from real measurement back-action.

## Bell / CHSH Inequality Test

Demonstrate quantum nonlocality: a shared Bell pair measured along cleverly chosen
angles violates the classical CHSH bound `|S| <= 2`, reaching Tsirelson's quantum
bound `2 sqrt(2) ~ 2.828`.

```python
from quantum_debugger.algorithms import chsh_value

r = chsh_value()               # default optimal angles
r["S"]                         # 2.828  (= 2 sqrt(2), Tsirelson bound)
r["classical_bound"]           # 2.0
r["violates_classical"]        # True
```

Each party measures `M(theta) = cos(theta) Z + sin(theta) X`; the correlator for
`|Phi+>` is `E(a,b) = cos(a-b)`, and `S = E(a,b) + E(a,b') + E(a',b) - E(a',b')`.

The same nonlocality wins the **CHSH game** (referee sends `(x, y)`, players answer
`(a, b)`, win iff `a XOR b == x AND y`) more often than any classical strategy:

```python
from quantum_debugger.algorithms import chsh_game

g = chsh_game()
g["quantum_win_probability"]     # 0.854  (= cos^2(pi/8))
g["classical_win_probability"]   # 0.75
g["beats_classical"]             # True
```

For three qubits the **GHZ (Mermin) test** gives an all-or-nothing violation: the
Mermin operator `M = XXX - XYY - YXY - YYX` has expectation 4 on the GHZ state, but
any local hidden-variable model is bounded by 2.

### Mixed states: the Horodecki criterion & the entangled-but-local window

For a noisy (mixed) state, what is the best CHSH value *any* measurement choice can
reach? There is an exact answer — `S_max = 2 sqrt(u1 + u2)` from the two largest
eigenvalues of `T^T T`, where `T` is the state's 3x3 Pauli correlation matrix:

```python
from quantum_debugger.algorithms import chsh_maximum, werner_nonlocality

r = werner_nonlocality(0.65)   # a Werner state, fidelity 0.65
r["entangled"]                 # True  -- negativity certifies entanglement
r["nonlocal"]                  # False -- S_max = 1.51 < 2: NO measurement violates CHSH
r["entangled_but_local"]       # True  -- the window 1/2 < F < 0.7803

werner_nonlocality(0.9)["chsh"]    # 2.45  > 2 -- genuinely nonlocal
```

The closed form is verified against brute-force optimization over all four
measurement directions and hits `S = 2` exactly at `F = (1 + 3/sqrt(2))/4`.
The window shows that **entanglement and Bell nonlocality are inequivalent
resources** — some entangled states admit a local hidden-variable model for every
CHSH experiment.

```python
from quantum_debugger.algorithms import mermin_ghz_test

m = mermin_ghz_test()
m["quantum_value"]      # 4.0
m["classical_bound"]    # 2.0  (brute-forced over +/-1 assignments)
m["violation_ratio"]    # 2.0
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

### Noisy probes: mixed-state QFI

Real probes decohere. `qfi_mixed` gives the exact Fisher information of any mixed
state via the symmetric-logarithmic-derivative formula:

```python
import numpy as np
from quantum_debugger.algorithms import qfi_mixed

G = np.diag([0.5, -0.5])                       # phase generator Z/2
psi = np.array([1, 1]) / np.sqrt(2)
pure = np.outer(psi, psi.conj())

qfi_mixed(pure, G)                             # 1.0 = 4 Var(G)
qfi_mixed(0.5 * pure + 0.5 * np.eye(2)/2, G)   # 0.5 -- decoherence costs precision
qfi_mixed(np.eye(2) / 2, G)                    # 0.0 -- fully mixed = phase-blind
```

Verified three independent ways: `4 Var(G)` on pure states, `N^2` on a GHZ probe,
and the numerical Bures-fidelity derivative on random mixed states. The quantum
Cramer-Rao bound `delta_phi >= 1/sqrt(F_Q)` then tells you exactly what your noisy
sensor can still resolve.

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

### GHZ vs W: robustness under particle loss

GHZ and W are the two inequivalent classes of 3-qubit entanglement, and losing a
qubit tells them apart *operationally*:

```python
from quantum_debugger.algorithms import loss_robustness

r = loss_robustness(3)
r["ghz_before_loss"]        # 0.5    -- intact GHZ: maximally entangled
r["ghz_pair_negativity"]    # 0.0    -- lose ONE qubit: fully separable!
r["w_pair_negativity"]      # 0.206  == (sqrt(5)-1)/6 -- W survivors stay entangled
```

All of GHZ's entanglement is global — the surviving pair is the classical mixture
`(|00><00| + |11><11|)/2`. The W state spreads its entanglement pairwise, so any
surviving pair keeps negativity `(sqrt((n-2)^2+4) - (n-2))/(2n) > 0` for every n
(exact, verified for n = 3..6). This is why W-type entanglement is preferred when
qubit loss is the dominant error.

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

Subtraction and comparison reuse the same Fourier-basis machinery:

```python
from quantum_debugger.algorithms import qft_subtract, quantum_compare

qft_subtract(5, 8, n_bits=4)       # 13   -- (5 - 8) mod 16
quantum_compare(9, 3, n_bits=4)    # {"a_geq_b": True, "a_lt_b": False, ...}
```

`quantum_compare` computes `(a - b)` with an extra sign bit; the sign bit is 0 iff
`a >= b`. Both are exact for every input pair.

A **ripple-carry adder** (Cuccaro) offers the complementary carry-propagation
approach -- only CNOT and Toffoli gates, and it returns the *exact* sum with the
carry-out (no modular wrap):

```python
from quantum_debugger.algorithms import ripple_carry_add

ripple_carry_add(9, 7, n_bits=4)     # 16   -- exact 5-bit sum with carry-out
ripple_carry_add(15, 15, n_bits=4)   # 30
```

Running that adder in reverse gives a subtractor (`b - a` with a borrow bit):

```python
from quantum_debugger.algorithms import ripple_carry_subtract

ripple_carry_subtract(4, 9, n_bits=4)   # {"result": 5,  "borrow": 0}  (9-4)
ripple_carry_subtract(9, 4, n_bits=4)   # {"result": 11, "borrow": 1}  (4-9 mod 16)
```

Multiplication is done in the Fourier basis too -- `|a>|b>|0> -> |a>|b>|a*b>` via
doubly-controlled phase rotations that add `2^(j+k)` for each pair of set input bits:

```python
from quantum_debugger.algorithms import quantum_multiply

quantum_multiply(7, 6, n_bits=3)     # 42
quantum_multiply(15, 15, n_bits=4)   # 225
```

`quantum_multiply` returns the exact `2*n`-bit product for every input pair.

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

## Repetition-Code Logical Error Rate

The central promise of QEC in one experiment: below a noise threshold, encoding
suppresses errors. A logical bit is encoded in the 3-qubit repetition code, each
physical qubit flips with probability `p`, and majority decoding recovers it. The
logical failure rate follows `3 p^2 (1 - p) + p^3` -- below the physical rate `p`
for every `p < 1/2`.

```python
from quantum_debugger.algorithms import repetition_code_error_rate

r = repetition_code_error_rate(p=0.1, trials=8000)
r["logical_error_rate"]   # ~0.028
r["analytic_rate"]        # 3*0.1^2*0.9 + 0.1^3 = 0.028
r["physical_rate"]        # 0.1
r["below_physical"]       # True
```

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

### The 5-qubit perfect code [[5,1,3]]

The **smallest** code that corrects an arbitrary single-qubit error — smaller than the
9-qubit Shor code. Its four stabilizers give 16 distinct syndromes, exactly matching
the error-free case plus the 15 single-qubit Pauli errors (hence "perfect": none left
over).

```python
from quantum_debugger.algorithms import five_qubit_code, five_qubit_stabilizers

five_qubit_stabilizers()                       # ['XZZXI', 'IXZZX', 'XIXZZ', 'ZXIXZ']

r = five_qubit_code(0.6, 0.8j, error="Y3")     # Y error on qubit 3
r["syndrome"]                                  # the measured 4-bit syndrome
r["correction"]                                # 'Y3' -- decoded exactly
r["fidelity"]                                  # 1.0 for ANY single-qubit error
```

`error` is `"I"` or `"<P><q>"` with `P` in `X/Y/Z` and `q` in `0..4`. Every one of the
15 single-qubit errors is corrected to fidelity 1 for an arbitrary logical input.

### The Steane code [[7,1,3]]

The classic **CSS code**, built from the classical [7,4,3] Hamming code. Its six
stabilizers split into three X-type and three Z-type generators taken from the same
Hamming parity-check matrix — so X and Z errors are detected and decoded
*independently* (a Y error just trips both sets):

```python
from quantum_debugger.algorithms import steane_code, steane_stabilizers

steane_stabilizers()
# ['IIIXXXX', 'IXXIIXX', 'XIXIXIX', 'IIIZZZZ', 'IZZIIZZ', 'ZIZIZIZ']

r = steane_code(0.6, 0.8j, error="Z5")
r["syndrome"]      # Z-type half is (0,0,0): a Z error only trips X-type checks
r["correction"]    # 'Z5'
r["fidelity"]      # 1.0 for ANY single-qubit error
```

The CSS structure is what makes the Steane code the workhorse of fault-tolerance
theory: transversal CNOT, H, and S gates all preserve the code space. Together the
QEC family now spans the 3-qubit repetition codes, the [[5,1,3]] perfect code, the
[[7,1,3]] Steane code, and the 9-qubit Shor code.

### Transversal logical gates

Why the Steane code is fault tolerance's workhorse, demonstrated directly: apply a
physical gate to **all 7 qubits at once** and the *logical* gate happens — no
decoding, and no physical gate ever couples two qubits of the same block (so one
faulty gate cannot spread into an uncorrectable multi-qubit error):

```python
from quantum_debugger.algorithms import steane_transversal, steane_transversal_cnot

steane_transversal("H", 0.6, 0.8j)
# {'logical_action': 'H', 'fidelity': 1.0}

steane_transversal("S", 1.0, 1.0)
# {'logical_action': 'Sdg', 'fidelity': 1.0}   <- transversal S = logical S-DAGGER!

# Bitwise CNOT between two code blocks (14 qubits) = perfect logical CNOT,
# even for entangling inputs: (|0_L> + |1_L>) x |0_L> -> a logical Bell state.
steane_transversal_cnot(control=(1.0, 1.0), target=(1.0, 0.0))
# {'fidelity': 1.0}
```

The S → S-dagger twist is a real property of the code (the `|1_L>` codewords have
Hamming weight ≡ 3 mod 4), and the tests confirm the transversal S matches logical
S-dagger and *not* logical S. The missing gate is T — no distance-3 CSS code has a
transversal T, which is why magic-state distillation exists.

### Magic states & T-gate injection

The missing T gate is supplied by **gate teleportation**: consume one pre-prepared
magic state `|A> = T|+>` using only Clifford operations, and the non-Clifford T
happens on the data:

```python
from quantum_debugger.algorithms import t_magic_state, inject_t_gate

t_magic_state()               # (|0> + e^{i pi/4}|1>)/sqrt(2)

r = inject_t_gate(0.6, 0.8j)  # data |psi>, CNOT to |A>, measure, Clifford fix-up
r["fidelity"]                 # 1.0 -- data is exactly T|psi>
r["probability"]              # 0.5 -- either measurement outcome, for ANY input
r["correction"]               # 'S' if outcome was 1 (since S T-dagger = T), else None
```

The circuit: CNOT (control data, target magic), measure the magic qubit. Outcome 0
leaves the data in `T|psi>` directly; outcome 1 leaves `T-dagger|psi>`, fixed by the
Clifford `S`. Both outcomes occur with probability exactly 1/2 — the measurement
reveals nothing about the data. This is why "distilling" high-fidelity `|A>` states
is the dominant cost of universal fault-tolerant quantum computing: every T gate in
an algorithm consumes one.

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

## The Holevo Bound & Accessible Information

Alice encodes classical data in quantum states; Bob measures. The **Holevo
quantity** bounds what any measurement can extract — and for non-orthogonal
states, even that bound is unreachable:

```python
import numpy as np
from quantum_debugger.algorithms import holevo_gap, holevo_bound, accessible_information

r = holevo_gap(np.pi / 4)      # two pure states with overlap cos(pi/4)
r["chi"]                       # 0.601 == h((1+cos)/2) -- the Holevo bound
r["accessible"]                # 0.399 == 1 - h((1+sin)/2) -- best measurement
r["gap"]                       # 0.202 -- information no measurement can reach

# The BB84 ensemble: the eavesdropper's fundamental limit.
bb84 = [np.array([1,0]), np.array([0,1]),
        np.array([1,1])/np.sqrt(2), np.array([1,-1])/np.sqrt(2)]
holevo_bound([0.25]*4, bb84)            # 1.0 exactly
accessible_information([0.25]*4, bb84)  # 0.5 exactly
```

The accessible information is found by genuinely optimizing a projective
measurement over the Bloch sphere and matches Levitin's closed form. The BB84
numbers are the security of quantum key distribution in two lines: the four
states *hold* one bit but surrender only half of it to any single measurement.

## Quantum State Discrimination

Non-orthogonal states cannot be perfectly distinguished — the fact quantum
cryptography is built on. Two optimal strategies, both exact:

```python
import numpy as np
from quantum_debugger.algorithms import (
    helstrom_bound, helstrom_measurement, unambiguous_discrimination,
)

a = np.array([1, 0]); b = np.array([1, 1]) / np.sqrt(2)   # overlap 1/sqrt(2)

# Minimum-error (Helstrom): guess every time, err as little as possible.
helstrom_bound(0.5, a, 0.5, b)               # 0.146 = (1 - sqrt(1 - s^2))/2
helstrom_measurement(0.5, a, 0.5, b)         # explicit optimal measurement hits it

# Unambiguous (IDP): NEVER guess wrong -- pay with inconclusive outcomes.
r = unambiguous_discrimination(a, b)
r["success_probability"]      # 0.293 = 1 - |<a|b>|
r["error_probability"]        # 0.0   -- exactly
r["inconclusive_probability"] # 0.707
```

The Helstrom measurement projects onto the positive part of `p0 rho0 - p1 rho1`
(works for mixed states and unequal priors too); the IDP POVM's conclusive
elements are orthogonal to the *other* state, so a conclusive click is a
guarantee. Certainty costs success rate: `1 - |s|` < the Helstrom success
`(1 + sqrt(1-s^2))/2` for every overlap `s != 0`.

## Optimal Universal Cloning (Buzek-Hillery)

Perfect cloning is impossible — but the *optimal imperfect* cloner is exactly
known, and it is a genuine 3-qubit circuit:

```python
from quantum_debugger.algorithms import universal_clone

r = universal_clone(0.6, 0.8j)     # clone an arbitrary unknown qubit
r["clone1_fidelity"]               # 0.8333... = 5/6 exactly
r["clone2_fidelity"]               # 0.8333... = 5/6 -- clones identical
r["classical_limit"]               # 2/3 -- best measure-and-prepare strategy
```

The Buzek-Hillery isometry sends `|psi>|0>|0>` to a symmetric 3-qubit state whose
two clone marginals are each `5/6 |psi><psi| + 1/6 |psi_perp><psi_perp|` — the
same fidelity for *every* input (universality, verified on random states). The
gap between 5/6 (quantum) and 2/3 (classical) is another face of the Holevo/
discrimination limits above; the gap between 5/6 and 1 is the no-cloning theorem.

## Contextuality: the Peres-Mermin Magic Square

A stronger statement than Bell violation — provable with operators alone, on
*any* state:

```python
from quantum_debugger.algorithms import (
    mermin_peres_square, classical_assignment_maximum, quantum_context_measurement,
)

mermin_peres_square()["square"]
# [['XI', 'IX', 'XX'], ['IZ', 'ZI', 'ZZ'], ['XZ', 'ZX', 'YY']]
# rows multiply to +I; columns to +I, +I, -I  (verified matrix-by-matrix)

classical_assignment_maximum()["max_satisfied"]   # 5 of 6 -- for ALL 512 assignments

import numpy as np
r = quantum_context_measurement(np.array([1, 1j, -1, 0.5]), "col", 2)
r["outcomes"]   # three +/-1 results (individually random)
r["product"]    # -1 == expected_sign, deterministically, every time
```

The parity obstruction: the six constraints multiply to `-1`, yet each of the nine
values appears in exactly two constraints — so no pre-assigned values can satisfy
them all. Quantum measurements do, on every state, because what an observable
"reveals" depends on which commuting context it is measured in. This is the
Kochen-Specker theorem in its smallest, sharpest form.

## Geometric (Berry) Phase

Take a qubit around a closed loop on the Bloch sphere and it remembers only the
*geometry* — the solid angle enclosed:

```python
from quantum_debugger.algorithms import berry_phase_triangle

r = berry_phase_triangle([1, 0, 0], [0, 1, 0], [0, 0, 1])   # one octant
r["solid_angle"]   # pi/2  -- classical spherical trigonometry (L'Huilier)
r["phase"]         # pi/4  -- quantum spinor overlaps: exactly Omega/2
r["matches"]       # True  -- two independent computations agree
```

The Pancharatnam phase `arg(<n1|n2><n2|n3><n3|n1>)` is gauge invariant (re-phase
any state, nothing changes), flips sign with loop orientation, and vanishes for
degenerate loops. Because it depends on the path and not the timing, it is
naturally robust — the working principle behind holonomic (geometric) quantum
gates.

## Uncertainty Relations

Two rigorous faces of Heisenberg's principle:

```python
import numpy as np
from quantum_debugger.algorithms import robertson_bound, entropic_uncertainty

X = np.array([[0, 1], [1, 0]]); Y = np.array([[0, -1j], [1j, 0]])
Z = np.array([[1, 0], [0, -1]])

r = robertson_bound(X, Y, [1, 0])       # X, Y on |0>
r["product"], r["bound"]                # 1.0, 1.0 -- TIGHT

robertson_bound(X, Y, [1, 1])["bound"]  # 0.0 -- Robertson can degenerate...

e = entropic_uncertainty(X, Z, [1, 0])  # ...the entropic bound cannot:
e["bound"]                              # 1.0 bit for X/Z on ANY state
e["sum"]                                # 1.0 -- equality on an eigenstate
```

Robertson's `dA dB >= |<[A,B]>|/2` is state-dependent and can collapse to a
trivial 0; the Maassen-Uffink bound `H(A) + H(B) >= -log2 c` depends only on the
*bases* — for mutually unbiased qubit measurements it guarantees one full bit of
combined ignorance no matter the state, which is exactly the complementarity that
BB84 turns into security.
