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
