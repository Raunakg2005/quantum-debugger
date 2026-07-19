"""
Clifford / Stabilizer Simulator (Aaronson-Gottesman CHP tableau)

An efficient second simulation engine for Clifford circuits. Instead of storing a
2^n state vector, it tracks the stabilizer group as a binary tableau and updates
it in O(n) per gate / O(n^2) per measurement -- so circuits of *hundreds* of
qubits (GHZ states, stabilizer codes, randomized benchmarking sequences) run
instantly, far beyond the reach of the dense state-vector simulator.

Supported gates: H, S (phase), X, Y, Z, CNOT, CZ, plus single-qubit measurement
in the computational basis (random or deterministic outcomes handled correctly).

Reference: Aaronson & Gottesman, "Improved Simulation of Stabilizer Circuits"
(Phys. Rev. A 70, 052328, 2004).
"""

import numpy as np


class StabilizerSimulator:
    """
    Tableau-based Clifford simulator on ``n`` qubits.

    Rows 0..n-1 are destabilizer generators, rows n..2n-1 are stabilizer
    generators, and row 2n is scratch. Each row stores x/z bit vectors and a phase
    bit r (0 -> +1, 1 -> -1).
    """

    def __init__(self, n: int, seed: int = 0):
        self.n = n
        self._rng = np.random.default_rng(seed)
        m = 2 * n + 1
        self.x = np.zeros((m, n), dtype=np.int8)
        self.z = np.zeros((m, n), dtype=np.int8)
        self.r = np.zeros(m, dtype=np.int8)
        for i in range(n):
            self.x[i, i] = 1  # destabilizer i = X_i
            self.z[n + i, i] = 1  # stabilizer i = Z_i

    # --- Clifford gates -----------------------------------------------------

    def h(self, a: int):
        """Hadamard on qubit a."""
        self.r ^= self.x[:, a] & self.z[:, a]
        self.x[:, a], self.z[:, a] = self.z[:, a].copy(), self.x[:, a].copy()
        return self

    def s(self, a: int):
        """Phase gate S on qubit a."""
        self.r ^= self.x[:, a] & self.z[:, a]
        self.z[:, a] ^= self.x[:, a]
        return self

    def z_gate(self, a: int):
        """Pauli Z on qubit a."""
        self.r ^= self.x[:, a]
        return self

    def x_gate(self, a: int):
        """Pauli X on qubit a."""
        self.r ^= self.z[:, a]
        return self

    def y_gate(self, a: int):
        """Pauli Y on qubit a."""
        self.r ^= self.x[:, a] ^ self.z[:, a]
        return self

    def cnot(self, a: int, b: int):
        """CNOT with control a, target b."""
        self.r ^= self.x[:, a] & self.z[:, b] & (self.x[:, b] ^ self.z[:, a] ^ 1)
        self.x[:, b] ^= self.x[:, a]
        self.z[:, a] ^= self.z[:, b]
        return self

    def cz(self, a: int, b: int):
        """Controlled-Z on qubits a, b (= H(b) CNOT(a,b) H(b))."""
        self.h(b)
        self.cnot(a, b)
        self.h(b)
        return self

    # --- Measurement --------------------------------------------------------

    def _rowsum(self, h: int, i: int):
        """Left-multiply row h by row i (Pauli product), tracking the phase."""
        g = 0
        for j in range(self.n):
            g += _g(self.x[i, j], self.z[i, j], self.x[h, j], self.z[h, j])
        total = 2 * self.r[h] + 2 * self.r[i] + g
        self.r[h] = 1 if (total % 4) else 0
        self.x[h, :] ^= self.x[i, :]
        self.z[h, :] ^= self.z[i, :]

    def measure(self, a: int) -> int:
        """
        Measure qubit ``a`` in the computational basis, collapsing the tableau.
        Returns 0 or 1 (random for an indeterminate outcome, fixed otherwise).
        """
        n = self.n
        p = None
        for i in range(n, 2 * n):
            if self.x[i, a]:
                p = i
                break

        if p is not None:  # random outcome
            for i in range(2 * n):
                if i != p and self.x[i, a]:
                    self._rowsum(i, p)
            # destabilizer p-n <- old stabilizer p; stabilizer p <- Z_a with random sign
            self.x[p - n, :] = self.x[p, :]
            self.z[p - n, :] = self.z[p, :]
            self.r[p - n] = self.r[p]
            self.x[p, :] = 0
            self.z[p, :] = 0
            self.r[p] = int(self._rng.integers(2))
            self.z[p, a] = 1
            return int(self.r[p])

        # deterministic outcome: accumulate into the scratch row 2n
        self.x[2 * n, :] = 0
        self.z[2 * n, :] = 0
        self.r[2 * n] = 0
        for i in range(n):
            if self.x[i, a]:
                self._rowsum(2 * n, i + n)
        return int(self.r[2 * n])

    def measure_all(self) -> list:
        """Measure every qubit (0..n-1) in order."""
        return [self.measure(q) for q in range(self.n)]

    # --- Inspection / verification -----------------------------------------

    def stabilizers(self) -> list:
        """
        Return the n stabilizer generators as (sign, pauli_string) tuples, where
        sign is +1/-1 and pauli_string[q] in {'I','X','Y','Z'} acts on qubit q.
        """
        out = []
        for i in range(self.n, 2 * self.n):
            chars = []
            for j in range(self.n):
                xj, zj = self.x[i, j], self.z[i, j]
                chars.append(
                    {(0, 0): "I", (1, 0): "X", (0, 1): "Z", (1, 1): "Y"}[
                        (int(xj), int(zj))
                    ]
                )
            out.append((-1 if self.r[i] else 1, "".join(chars)))
        return out


def _g(x1, z1, x2, z2):
    """Phase exponent (mod 4) contributed by multiplying two single-qubit Paulis."""
    if x1 == 0 and z1 == 0:
        return 0
    if x1 == 1 and z1 == 1:
        return int(z2) - int(x2)
    if x1 == 1 and z1 == 0:
        return int(z2) * (2 * int(x2) - 1)
    # x1 == 0 and z1 == 1
    return int(x2) * (1 - 2 * int(z2))


def stabilizer_to_pauli_matrix(sign: int, pauli_string: str) -> np.ndarray:
    """Dense operator for a signed Pauli string (qubit 0 = LSB)."""
    single = {
        "I": np.eye(2, dtype=complex),
        "X": np.array([[0, 1], [1, 0]], dtype=complex),
        "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
        "Z": np.array([[1, 0], [0, -1]], dtype=complex),
    }
    mat = np.array([[1.0]], dtype=complex)
    for p in reversed(pauli_string):
        mat = np.kron(mat, single[p])
    return sign * mat
