"""
Density-Matrix Simulator (open quantum systems)

Simulate mixed states and noise: apply unitary gates *and* Kraus noise channels to a
density matrix ``rho``, take partial traces, and read out purity, populations,
expectation values, and state fidelity. Where the state-vector simulator tracks a
pure state, this tracks the full ``rho`` so decoherence and mixing are exact.

Qubit ordering matches the rest of the library (qubit 0 = least significant).
"""

import numpy as np

from .core.quantum_state import apply_gate_tensor
from .core.gates import GateLibrary

_I = np.eye(2, dtype=complex)
_X = GateLibrary.X
_Y = GateLibrary.Y
_Z = GateLibrary.Z


def _embed(op, targets, n):
    """Full 2**n operator applying ``op`` to ``targets`` (reuses the tensor engine)."""
    dim = 2**n
    op = np.asarray(op, dtype=complex)
    emb = np.zeros((dim, dim), dtype=complex)
    for j in range(dim):
        col = np.zeros(dim, dtype=complex)
        col[j] = 1.0
        emb[:, j] = apply_gate_tensor(np, col, op, list(targets), n)
    return emb


def _matrix_sqrt(mat):
    """Principal square root of a Hermitian PSD matrix (via eigendecomposition)."""
    vals, vecs = np.linalg.eigh(mat)
    vals = np.clip(vals.real, 0.0, None)
    return (vecs * np.sqrt(vals)) @ vecs.conj().T


class DensityMatrix:
    """Density-matrix state of ``n`` qubits."""

    def __init__(self, n=None, rho=None, state_vector=None):
        if rho is not None:
            self.rho = np.asarray(rho, dtype=complex)
            self.n = int(round(np.log2(self.rho.shape[0])))
        elif state_vector is not None:
            sv = np.asarray(state_vector, dtype=complex)
            sv = sv / np.linalg.norm(sv)
            self.rho = np.outer(sv, sv.conj())
            self.n = int(round(np.log2(len(sv))))
        else:
            dim = 2**n
            self.rho = np.zeros((dim, dim), dtype=complex)
            self.rho[0, 0] = 1.0  # |0...0><0...0|
            self.n = n

    # --- evolution ---------------------------------------------------------

    def apply_unitary(self, U, qubits):
        """Apply a unitary ``U`` to ``qubits``: rho -> U rho U-dagger."""
        emb = _embed(U, qubits, self.n)
        self.rho = emb @ self.rho @ emb.conj().T
        return self

    def apply_channel(self, kraus_ops, qubits):
        """Apply a Kraus channel {K_i} to ``qubits``: rho -> sum_i K_i rho K_i-dagger."""
        new = np.zeros_like(self.rho)
        for K in kraus_ops:
            emb = _embed(K, qubits, self.n)
            new += emb @ self.rho @ emb.conj().T
        self.rho = new
        return self

    # --- readout -----------------------------------------------------------

    def purity(self) -> float:
        """Tr(rho^2): 1 for a pure state, down to 1/2**n for the maximally mixed state."""
        return float(np.real(np.trace(self.rho @ self.rho)))

    def von_neumann_entropy(self) -> float:
        """
        Von Neumann entropy ``S = -Tr(rho log2 rho)`` in bits: 0 for a pure state, up to
        ``n`` for the maximally mixed state.
        """
        vals = np.linalg.eigvalsh(self.rho).real
        vals = vals[vals > 1e-12]
        return float(-np.sum(vals * np.log2(vals)))

    def entanglement_entropy(self, qubits) -> float:
        """
        Entanglement entropy of the ``qubits`` subsystem: the von Neumann entropy of its
        reduced density matrix. For a pure global state this measures entanglement across
        the cut (0 = product, 1 bit = a maximally entangled qubit pair).
        """
        return self.partial_trace(qubits).von_neumann_entropy()

    def probabilities(self) -> np.ndarray:
        """Computational-basis populations (the diagonal of rho)."""
        return np.real(np.diag(self.rho))

    def expectation(self, observable) -> float:
        """Expectation Tr(rho O) of a Hermitian observable given as a full matrix."""
        return float(
            np.real(np.trace(self.rho @ np.asarray(observable, dtype=complex)))
        )

    def fidelity(self, other) -> float:
        """
        State fidelity to ``other`` (a DensityMatrix or a pure state vector).

        Uses Uhlmann's fidelity ``(Tr sqrt(sqrt(rho) sigma sqrt(rho)))**2``.
        """
        if isinstance(other, DensityMatrix):
            sigma = other.rho
        else:
            sv = np.asarray(other, dtype=complex)
            sv = sv / np.linalg.norm(sv)
            sigma = np.outer(sv, sv.conj())
        sqrt_rho = _matrix_sqrt(self.rho)
        inner = _matrix_sqrt(sqrt_rho @ sigma @ sqrt_rho)
        return float(np.real(np.trace(inner)) ** 2)

    def partial_trace(self, keep) -> "DensityMatrix":
        """Reduced density matrix on ``keep`` qubits, tracing out the rest."""
        keep = sorted(keep)
        n = self.n
        traced = [q for q in range(n) if q not in keep]
        dim_k = 2 ** len(keep)
        red = np.zeros((dim_k, dim_k), dtype=complex)
        for i in range(2**n):
            for j in range(2**n):
                if all(((i >> q) & 1) == ((j >> q) & 1) for q in traced):
                    ri = sum(((i >> keep[m]) & 1) << m for m in range(len(keep)))
                    rj = sum(((j >> keep[m]) & 1) << m for m in range(len(keep)))
                    red[ri, rj] += self.rho[i, j]
        return DensityMatrix(rho=red)


# --- standard single-qubit Kraus channels ---------------------------------


def bit_flip(p: float):
    """Bit-flip channel: X with probability p."""
    return [np.sqrt(1 - p) * _I, np.sqrt(p) * _X]


def phase_flip(p: float):
    """Phase-flip channel: Z with probability p."""
    return [np.sqrt(1 - p) * _I, np.sqrt(p) * _Z]


def depolarizing(p: float):
    """Depolarizing channel: rho -> (1-p) rho + p I/2."""
    return [
        np.sqrt(1 - 3 * p / 4) * _I,
        np.sqrt(p / 4) * _X,
        np.sqrt(p / 4) * _Y,
        np.sqrt(p / 4) * _Z,
    ]


def amplitude_damping(gamma: float):
    """Amplitude damping (T1): |1> decays to |0> with rate gamma."""
    return [
        np.array([[1, 0], [0, np.sqrt(1 - gamma)]], dtype=complex),
        np.array([[0, np.sqrt(gamma)], [0, 0]], dtype=complex),
    ]


def phase_damping(gamma: float):
    """Phase damping (T2): loss of coherence without energy loss."""
    return [
        np.array([[1, 0], [0, np.sqrt(1 - gamma)]], dtype=complex),
        np.array([[0, 0], [0, np.sqrt(gamma)]], dtype=complex),
    ]
