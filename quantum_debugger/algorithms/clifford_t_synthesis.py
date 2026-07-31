"""
Clifford+T gate synthesis (Solovay-Kitaev flavour).

Fault-tolerant hardware offers a *discrete* gate set -- typically Clifford + ``T`` -- yet
algorithms call for arbitrary rotations. The Solovay-Kitaev theorem guarantees any
single-qubit unitary can be approximated to precision ``epsilon`` by an ``O(log^c(1/eps))``
length word in that set, because ``{H, T}`` generates a dense subgroup of ``PSU(2)``. This
module realizes the finite version: it enumerates Clifford+T words (deduplicated up to
global phase) into a net and returns the best approximation of a target, tracking the ``T``
count (the fault-tolerant cost metric). Verified: any reachable gate is synthesized exactly
(``Rz(pi/4) = T``, ``Rz(pi/2) = S``, and any Clifford+T word), the net grows with word
length, and every synthesized word uses only Clifford+T gates.
"""

import numpy as np

_H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
_T = np.diag([1, np.exp(1j * np.pi / 4)]).astype(complex)
_S = np.diag([1, 1j]).astype(complex)
_GATES = {"H": _H, "T": _T}


def rz(angle: float) -> np.ndarray:
    """The ``Rz(angle) = diag(e^{-i angle/2}, e^{i angle/2})`` rotation to be synthesized."""
    return np.diag([np.exp(-1j * angle / 2), np.exp(1j * angle / 2)])


def gate_distance(U, V) -> float:
    """
    Distance between single-qubit gates up to global phase:
    ``sqrt(max(0, 1 - |Tr(U^dagger V)/2|^2))`` (a process-fidelity metric, 0 iff equal up to
    phase).
    """
    U = np.asarray(U, dtype=complex); V = np.asarray(V, dtype=complex)
    f = abs(np.trace(U.conj().T @ V)) / 2
    return float(np.sqrt(max(0.0, 1 - f ** 2)))


def t_count(word: str) -> int:
    """Number of ``T`` gates in a Clifford+T word -- the dominant fault-tolerant cost."""
    return word.count("T")


def _phase_key(M):
    """Global-phase-invariant hash key for a 2x2 unitary (round after phase-fixing)."""
    i = int(np.argmax(np.abs(M)))
    M = M / (M.flatten()[i] / abs(M.flatten()[i]))
    return tuple(np.round(M.flatten(), 6))


def enumerate_clifford_t(max_length: int):
    """
    Enumerate Clifford+T words over ``{H, T}`` up to ``max_length`` gates, deduplicated up
    to global phase. Returns a dict ``{phase_key: (word, matrix)}`` -- the finite net from
    which approximations are chosen.
    """
    I = np.eye(2, dtype=complex)
    seen = {_phase_key(I): ("", I)}
    frontier = [("", I)]
    for _ in range(max_length):
        nxt = []
        for w, M in frontier:
            for g, G in _GATES.items():
                nw, nM = w + g, G @ M
                k = _phase_key(nM)
                if k not in seen:
                    seen[k] = (nw, nM)
                    nxt.append((nw, nM))
        frontier = nxt
    return seen


def synthesize(target, max_length: int = 8) -> dict:
    """
    Best Clifford+T approximation of a target single-qubit ``target`` gate among all words up
    to ``max_length``. Returns the ``word``, its ``matrix``, the ``error`` (up to phase), and
    the ``t_count``.
    """
    target = np.asarray(target, dtype=complex)
    best = None
    for w, M in enumerate_clifford_t(max_length).values():
        e = gate_distance(M, target)
        if best is None or e < best["error"]:
            best = {"word": w, "matrix": M, "error": e, "t_count": t_count(w)}
    return best


def synthesize_rz(angle: float, max_length: int = 8) -> dict:
    """Best Clifford+T approximation of ``Rz(angle)`` -- convenience wrapper over
    :func:`synthesize`. Exact (error 0) for multiples of ``pi/4`` (``T`` powers)."""
    return synthesize(rz(angle), max_length)


def is_clifford_t_word(word: str) -> bool:
    """True iff ``word`` uses only the fault-tolerant gate set ``{H, T, S}``."""
    return all(ch in "HTS" for ch in word)
