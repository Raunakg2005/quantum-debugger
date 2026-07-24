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
_P0 = np.array([[1, 0], [0, 0]], dtype=complex)
_P1 = np.array([[0, 0], [0, 1]], dtype=complex)


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

    def measure(self, qubit, rng=None) -> int:
        """
        Projectively measure ``qubit`` in the computational basis, collapsing ``rho``.
        Returns 0 or 1 with the Born-rule probabilities.
        """
        rng = rng or np.random.default_rng()
        proj0 = _embed(_P0, [qubit], self.n)
        p0 = float(np.real(np.trace(proj0 @ self.rho)))
        outcome = 0 if rng.random() < p0 else 1
        proj = proj0 if outcome == 0 else _embed(_P1, [qubit], self.n)
        p = p0 if outcome == 0 else 1 - p0
        self.rho = (proj @ self.rho @ proj) / p
        return outcome

    def sample(self, shots: int, seed: int = 0) -> dict:
        """
        Sample ``shots`` full computational-basis measurement outcomes (non-destructive;
        the outcome distribution is the diagonal of ``rho``). Returns bitstring -> count
        with bit ``q`` = qubit ``q``.
        """
        rng = np.random.default_rng(seed)
        probs = self.probabilities()
        probs = np.clip(probs, 0, None)
        probs = probs / probs.sum()
        draws = rng.choice(len(probs), size=shots, p=probs)
        counts = {}
        for d in draws:
            key = "".join(str((int(d) >> q) & 1) for q in range(self.n))
            counts[key] = counts.get(key, 0) + 1
        return counts

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


def pauli_channel(px: float, py: float, pz: float):
    """
    General single-qubit Pauli channel: apply X/Y/Z with probabilities px/py/pz
    (identity otherwise). Generalizes bit-flip, phase-flip, and depolarizing.
    """
    return [
        np.sqrt(max(0.0, 1 - px - py - pz)) * _I,
        np.sqrt(px) * _X,
        np.sqrt(py) * _Y,
        np.sqrt(pz) * _Z,
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


# --- channel quality metrics ----------------------------------------------


def process_fidelity(kraus_ops, target=None) -> float:
    """
    Entanglement (process) fidelity of a Kraus channel ``{K_i}`` to a target unitary
    ``target`` (default: the identity):

        F_process = (1 / d**2) * sum_i |Tr(target-dagger K_i)|**2

    This is the fidelity between the channel's Choi state and the target's, and it
    equals 1 iff the channel *is* the target unitary. ``d`` is the Hilbert-space
    dimension inferred from the Kraus operators.
    """
    K0 = np.asarray(kraus_ops[0], dtype=complex)
    d = K0.shape[0]
    U = np.eye(d, dtype=complex) if target is None else np.asarray(target, dtype=complex)
    Ud = U.conj().T
    return float(
        sum(abs(np.trace(Ud @ np.asarray(K, dtype=complex))) ** 2 for K in kraus_ops)
        / d**2
    )


def average_gate_fidelity(kraus_ops, target=None) -> float:
    """
    Average gate fidelity of a Kraus channel to ``target`` (default identity),
    averaged uniformly over pure input states. Related to the process fidelity by
    the exact Horodecki/Nielsen identity

        F_avg = (d * F_process + 1) / (d + 1).

    Examples (single qubit, d = 2): a perfect gate gives 1; ``depolarizing(p)`` gives
    ``1 - p/2``; a stray Pauli-X error (``[X]``) gives 1/3.
    """
    K0 = np.asarray(kraus_ops[0], dtype=complex)
    d = K0.shape[0]
    fp = process_fidelity(kraus_ops, target)
    return (d * fp + 1) / (d + 1)
