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
