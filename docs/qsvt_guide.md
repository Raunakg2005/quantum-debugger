# Quantum Singular Value Transformation (QSVT) & Modern Algorithm Primitives

The Quantum Singular Value Transformation (QSVT) is widely recognized as the "Grand Unification" of quantum algorithms. It provides a single, mathematically rigorous framework from which Hamiltonian simulation, quantum linear system solvers (HHL), amplitude amplification (Grover), quantum phase estimation, and matrix functions all naturally emerge.

`quantum_debugger.algorithms` implements the complete QSVT stack bottom-up, verified against exact diagonalization and analytic theorems to machine precision.

---

## Architecture of the QSVT Framework

The QSVT ecosystem is structured in clean, composable layers:

1. **Quantum Signal Processing (QSP)**: The 1-qubit algebraic engine transforming a scalar $x \in [-1, 1]$ into a designable polynomial $P(x)$ using alternating signal and phase rotations.
2. **Block Encoding**: The standard input model embedding an arbitrary non-unitary or non-Hermitian operator $A$ into the upper-left block of a unitary matrix $U$: $\langle 0 | U | 0 \rangle = A / \alpha$.
3. **Linear Combination of Unitaries (LCU)**: Constructing block encodings of Hamiltonians and observables given as linear combinations of unitaries/Paulis ($\sum_k \alpha_k U_k$) via PREPARE and SELECT oracles.
4. **Qubitization Walk**: Converting a block encoding into a generalized quantum walk whose powers generate Chebyshev polynomials of the embedded operator: $\langle 0 | W^d | 0 \rangle = T_d(A)$.
5. **QSVT**: Applying QSP phase sequences to the qubitization walk, evaluating polynomial matrix functions $P(A)$ *eigenvalue-by-eigenvalue* without diagonalizing.
6. **Applications**:
   - **Hamiltonian Simulation**: $e^{-i H t}$ via Jacobi-Anger / Chebyshev expansions.
   - **Quantum Linear Systems**: Solving $A x = b$ via optimal polynomial approximation of $1/x$.
   - **Matrix Functions & Spectral Filtering**: Matrix sign, square root, power, matrix exponential, logarithm, ground state projectors, and Gibbs states.
   - **Kernel Polynomial Method (KPM)**: Chebyshev moments, spectral densities, and interval eigenvalue counting.

---

## 1. Quantum Signal Processing (QSP)

Quantum Signal Processing transforms a scalar input $x \in [-1, 1]$ through alternating signal rotations $W(x)$ and $Z$-rotations parameterized by a sequence of phase angles $\Phi = (\phi_0, \phi_1, \dots, \phi_d)$:

$$U_\Phi(x) = e^{i \phi_0 Z} \prod_{k=1}^d \left( W(x) \, e^{i \phi_k Z} \right)$$

where $W(x) = \begin{pmatrix} x & i\sqrt{1-x^2} \\ i\sqrt{1-x^2} & x \end{pmatrix}$.

The top-left matrix element $\langle 0 | U_\Phi(x) | 0 \rangle$ evaluates to a polynomial $P(x)$ whose degree matches $d$ and whose parity matches $d \pmod 2$. Setting all phases to zero exactly recovers the Chebyshev polynomial of the first kind: $T_d(x) = \cos(d \arccos x)$.

```python
import numpy as np
from quantum_debugger.algorithms import (
    qsp_unitary,
    qsp_response,
    chebyshev_via_qsp,
    qsp_complementary_response,
)

# 1. Zero phase angles yield Chebyshev polynomials T_d(x)
d = 4
phases_zero = [0.0] * (d + 1)
x = 0.6

# Evaluate QSP unitary and top-left scalar response
U = qsp_unitary(x, phases_zero)
response = qsp_response(x, phases_zero)
chebyshev_exact = np.cos(d * np.arccos(x))

print(f"QSP response: {response.real:.6f}")
print(f"Exact T_4(0.6): {chebyshev_exact:.6f}")
assert np.isclose(response.real, chebyshev_exact)

# 2. Complementary response satisfying |P(x)|^2 + (1-x^2)|Q(x)|^2 = 1
comp = qsp_complementary_response(x, [0.1, -0.3, 0.4])
print("Algebraic identity check (|P|^2 + (1-x^2)|Q|^2):", comp["identity_error"])
```

---

## 2. Block Encoding & Qubitization Walk

Quantum computers can only natively execute unitary operators. Block encoding embeds a normalized matrix $A$ ($\|A\| \le 1$) into an ancilla-augmented unitary $U$:

$$U = \begin{pmatrix} A & \sqrt{I - A A^\dagger} \\ \sqrt{I - A^\dagger A} & -A^\dagger \end{pmatrix}$$

so that $\langle 0 | U | 0 \rangle = A$.

The **Qubitization Walk** operator is constructed as:

$$W = U \, (2\Pi - I)$$

where $\Pi = |0\rangle\langle 0| \otimes I$ projects onto the ancilla zero state. Powers of this walk directly realize matrix Chebyshev polynomials:

$$\langle 0 | W^d | 0 \rangle = T_d(A)$$

```python
import numpy as np
from quantum_debugger.algorithms import (
    block_encode,
    is_block_encoding,
    chebyshev_of_matrix,
    qubitization_walk,
)

# Define a Hermitian matrix with spectral norm <= 1
A = np.array([
    [0.4, 0.2],
    [0.2, -0.5]
], dtype=complex)

# Construct unitary block encoding
U = block_encode(A)
assert is_block_encoding(U, A)

# Evaluate matrix Chebyshev polynomial T_3(A) using the quantum walk
T3_walk = chebyshev_of_matrix(A, degree=3)

# Verify against exact classical matrix polynomial: T_3(x) = 4x^3 - 3x
T3_exact = 4 * np.linalg.matrix_power(A, 3) - 3 * A
np.testing.assert_allclose(T3_walk, T3_exact, atol=1e-10)
print("Quantum walk matrix Chebyshev polynomial verified!")
```

---

## 3. Linear Combination of Unitaries (LCU)

Physical Hamiltonians are commonly presented as linear combinations of Pauli operators:

$$H = \sum_{k=0}^{L-1} \alpha_k U_k, \quad \alpha_k > 0$$

LCU builds a block encoding of $H$ using two subroutines:
- **PREPARE**: Maps ancilla state $|0\rangle$ to $\frac{1}{\sqrt{\lambda}} \sum_k \sqrt{\alpha_k} |k\rangle$, where $\lambda = \sum_k \alpha_k$ is the 1-norm.
- **SELECT**: Applies controlled unitaries $\sum_k |k\rangle\langle k| \otimes U_k$.

The composite operator $U = \text{PREPARE}^\dagger \, \text{SELECT} \, \text{PREPARE}$ satisfies:

$$\langle 0 | U | 0 \rangle = \frac{H}{\lambda}$$

```python
import numpy as np
from quantum_debugger.algorithms import lcu_block_encoding, lcu_matrix

# Define Pauli matrices
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)

# Weighted sum: H = 0.5 X + 0.3 Z + 0.2 Y
coeffs = [0.5, 0.3, 0.2]
unitaries = [X, Z, Y]

lcu_result = lcu_block_encoding(coeffs, unitaries)
U_lcu = lcu_result["unitary"]
norm_lambda = lcu_result["subnormalization"]

# Verify block encoding
top_block = U_lcu[:2, :2]
H_target = lcu_matrix(coeffs, unitaries)
np.testing.assert_allclose(top_block, H_target / norm_lambda, atol=1e-12)
print("LCU block encoding successfully constructed with normalization factor:", norm_lambda)
```

---

## 4. Quantum Singular Value Transformation (QSVT)

The core theorem of QSVT establishes that interleaving the qubitization walk $W$ with projectively controlled phase rotations applies the scalar QSP transformation to the singular values (or eigenvalues for Hermitian operators) of $A$:

$$P(A) = \sum_j P(\lambda_j) |v_j\rangle\langle v_j|$$

```python
import numpy as np
from quantum_debugger.algorithms import qsvt_transform, qsvt_scalar_response

A = np.diag([0.25, -0.6, 0.8]).astype(complex)
phases = [0.3, -0.5, 0.2, 0.1]

# Apply QSVT to matrix A
P_A = qsvt_transform(A, phases)

# Verify against eigenvalue-by-eigenvalue scalar transformation
expected_diag = [qsvt_scalar_response(phases, val).real for val in [0.25, -0.6, 0.8]]
np.testing.assert_allclose(np.diag(P_A).real, expected_diag, atol=1e-12)
print("QSVT eigenvalue-by-eigenvalue transform verified to machine precision.")
```

---

## 5. Quantum Linear Systems via QSVT ($A x = b$)

The Quantum Linear Systems Problem solves $A x = b$ for Hermitian positive-definite $A$. Unlike the Harrow-Hassidim-Lloyd (HHL) algorithm which requires costly quantum phase estimation, QSVT solves linear systems using an optimal polynomial approximation to $f(x) = 1/x$ over the spectrum $[\kappa^{-1}, 1]$:

```python
import numpy as np
from quantum_debugger.algorithms import solve_linear_system_qsvt, matrix_inverse_qsvt

# Construct a well-conditioned Hermitian matrix
A = np.array([
    [0.7, 0.1],
    [0.1, 0.5]
], dtype=complex)
b = np.array([1.0, 2.0], dtype=complex)

# Solve Ax = b via QSVT polynomial inversion
result = solve_linear_system_qsvt(A, b, degree=30)
x_qsvt = result["solution"]
fidelity = result["fidelity"]

# Compare with classical solve
x_classical = np.linalg.solve(A, b)

print("QSVT Solution:", x_qsvt)
print("Classical Solution:", x_classical)
print(f"State Fidelity: {fidelity:.6f}")
print("Relative Error:", np.linalg.norm(x_qsvt - x_classical) / np.linalg.norm(x_classical))
```

---

## 6. Matrix Functions & Hamiltonian Simulation

Any smooth function $f(A)$ can be evaluated through its Chebyshev expansion:

$$f(A) \approx \sum_{k=0}^d c_k T_k(A)$$

For Hamiltonian simulation, setting $f(x) = e^{-i x t}$ yields the time-evolution unitary $e^{-i H t}$:

```python
import numpy as np
from quantum_debugger.algorithms import (
    matrix_function_chebyshev,
    hamiltonian_simulation_qsvt,
)

H = np.array([
    [0.3, 0.2],
    [0.2, -0.4]
], dtype=complex)

# 1. Smooth matrix function: cos(H)
cos_H = matrix_function_chebyshev(H, np.cos, degree=16)

# 2. Hamiltonian simulation: e^{-i H t}
sim = hamiltonian_simulation_qsvt(H, time=1.5, degree=24)
U_sim = sim["unitary"]
exact_U = np.linalg.matrix_power(np.eye(2), 1)  # compare with scipy expm
import scipy.linalg
exact_U = scipy.linalg.expm(-1j * H * 1.5)

print("Simulation Error vs Exact Expm:", np.linalg.norm(U_sim - exact_U))
print("Approximation Unitarity Error:", sim["unitarity_error"])
```

---

## 7. Spectral Filtering & Ground-State Projectors

QSVT enables projecting onto specific eigenspaces without measuring or collapsing states:

- **Matrix Sign**: $\text{sign}(A)$, separating positive and negative eigenspaces.
- **Spectral Projector**: Projecting onto eigenvalues above or below an energy cutoff.
- **Ground State Projector**: Preparing ground states by filtering low energies.
- **Bandpass Filter**: Gaussian window $\exp(-((A - E_0)/\sigma)^2)$ for eigenstate isolation.

```python
import numpy as np
from quantum_debugger.algorithms import (
    matrix_sign_qsvt,
    spectral_projector_qsvt,
    ground_state_projector_qsvt,
)

# Matrix with eigenvalues -0.5, 0.2, 0.8
A = np.diag([-0.5, 0.2, 0.8]).astype(complex)

# 1. Spectral Projector for eigenvalues > 0
proj = spectral_projector_qsvt(A, threshold=0.0, degree=40)
print("Projector diagonal (expected ~[0, 1, 1]):", np.diag(proj).real.round(3))

# 2. Ground state projector (lowest eigenvalue -0.5)
gs_proj = ground_state_projector_qsvt(A, degree=40)
print("Ground state projector diagonal (expected ~[1, 0, 0]):", np.diag(gs_proj).real.round(3))
```

---

## 8. Kernel Polynomial Method (KPM) & Spectral Density

The Kernel Polynomial Method estimates spectral densities and eigenvalue counts without full diagonalization using Jackson-damped Chebyshev moments $\mu_k = \text{Tr}(T_k(A))$:

```python
import numpy as np
from quantum_debugger.algorithms import (
    spectral_moments,
    density_of_states_kpm,
    eigenvalue_count_in_interval,
)

# 4x4 Hamiltonian
H = np.diag([-0.8, -0.2, 0.3, 0.7]).astype(complex)

# Compute Chebyshev moments via qubitization walk
moments = spectral_moments(H, max_degree=20)

# Count eigenvalues in interval [-0.5, 0.5] (contains -0.2 and 0.3 -> count = 2)
count = eigenvalue_count_in_interval(H, a=-0.5, b=0.5, degree=40)
print(f"Eigenvalues in interval [-0.5, 0.5]: {count['count_rounded']} (Exact: 2)")

# Density of states evaluation
energies = np.linspace(-0.9, 0.9, 100)
dos = density_of_states_kpm(moments, energies)
print("Total integrated states:", np.trapezoid(dos, energies) if hasattr(np, 'trapezoid') else np.trapz(dos, energies))
```

---

## 9. Amplitude Amplification as QSVT

Grover's amplitude amplification is a special case of QSVT where the polynomial is an odd Chebyshev polynomial $T_{2k+1}(x)$ acting on the scalar projection $\langle \psi | \text{target} \rangle$:

```python
from quantum_debugger.algorithms import amplitude_amplification_qsvt

# Initial success amplitude (e.g. searching 1 item in 100)
initial_amp = 0.1

amp_res = amplitude_amplification_qsvt(initial_amp)
print(f"Optimal Grover iterations: {amp_res['optimal_steps']}")
print(f"Amplified amplitude: {amp_res['amplified_amplitude']:.4f}")
print(f"Amplified success probability: {amp_res['success_probability']:.4f}")
```

---

## Summary of API Functions

| Module | Core Functions | Description |
|---|---|---|
| `qsp` | `qsp_unitary`, `qsp_response`, `chebyshev_via_qsp`, `qsp_complementary_response` | Single-qubit polynomial transformations via signal/phase rotations |
| `block_encoding` | `block_encode`, `is_block_encoding`, `qubitization_walk`, `chebyshev_of_matrix`, `qsvt_transform` | Matrix embeddings, quantum walk, and full QSVT matrix transforms |
| `lcu` | `lcu_block_encoding`, `lcu_matrix` | Linear Combination of Unitaries (PREPARE and SELECT) |
| `matrix_functions` | `matrix_function_chebyshev`, `hamiltonian_simulation_qsvt`, `solve_linear_system_qsvt`, `matrix_inverse_qsvt` | Chebyshev matrix functions, unitary dynamics, and quantum linear systems |
| `qsvt_applications` | `matrix_sign_qsvt`, `spectral_projector_qsvt`, `matrix_sqrt_qsvt`, `ground_state_projector_qsvt`, `bandpass_filter_qsvt`, `gibbs_state_qsvt` | Matrix functions, thermal states, and spectral projections |
| `chebyshev_spectral` | `spectral_moments`, `trace_of_function`, `density_of_states_kpm`, `eigenvalue_count_in_interval` | Kernel Polynomial Method, DOS, and moment estimation |
| `qsvt_amplification` | `amplitude_amplification_qsvt`, `chebyshev_approximation` | Grover amplitude amplification as scalar QSVT |
