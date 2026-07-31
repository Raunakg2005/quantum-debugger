"""
Coherence measures -- quantifying superposition as a resource.

Relative to a fixed basis (the "classical" states), coherence is the resource that lets a
state be in a superposition. The resource theory of coherence provides monotones that
cannot increase under incoherent operations:

* **l1-norm coherence** ``C_l1 = sum_{i != j} |rho_ij|`` -- the total off-diagonal weight.
* **Relative entropy of coherence** ``C_rel = S(rho_diag) - S(rho)`` -- the distillable
  coherence, where ``rho_diag`` is the dephased (diagonal) state.
* **Robustness of coherence** -- the minimal mixing with another state that makes the
  result incoherent.

Verified: an incoherent (diagonal) state has zero coherence, and a maximally coherent
state ``|+...+>`` on ``d`` levels gives ``C_l1 = d - 1`` and ``C_rel = log d``.
"""

import numpy as np

from .quantum_entropies import von_neumann_entropy


def dephase(rho) -> np.ndarray:
    """Full dephasing: keep only the diagonal of ``rho`` (the incoherent projection)."""
    rho = np.asarray(rho, dtype=complex)
    return np.diag(np.diag(rho))


def l1_coherence(rho) -> float:
    """
    l1-norm of coherence ``sum_{i != j} |rho_ij|`` -- the summed magnitude of the
    off-diagonal elements. Zero for an incoherent (diagonal) state, ``d - 1`` for a
    maximally coherent pure state on ``d`` levels.
    """
    rho = np.asarray(rho, dtype=complex)
    return float(np.sum(np.abs(rho)) - np.sum(np.abs(np.diag(rho))))


def relative_entropy_of_coherence(rho, base: float = 2.0) -> float:
    """
    Relative entropy of coherence ``S(rho_diag) - S(rho)`` -- the coherence distillable
    from ``rho`` by incoherent operations. Zero for a diagonal state, ``log d`` for a
    maximally coherent pure state.
    """
    return float(von_neumann_entropy(dephase(rho), base) - von_neumann_entropy(rho, base))


def robustness_of_coherence(rho) -> float:
    """
    Robustness of coherence: the minimal ``s >= 0`` such that ``(rho + s tau)/(1+s)`` is
    incoherent for some state ``tau``. For a single qubit it has the closed form
    ``2 |rho_01|`` (twice the off-diagonal magnitude) -- the value returned and verified
    here for qubits.
    """
    rho = np.asarray(rho, dtype=complex)
    if rho.shape[0] == 2:
        return float(2 * abs(rho[0, 1]))
    # general upper bound (equals l1 coherence for pure states): use the l1 value
    return l1_coherence(rho)


def is_incoherent(rho, atol: float = 1e-9) -> bool:
    """True iff ``rho`` is diagonal (incoherent) in the reference basis."""
    rho = np.asarray(rho, dtype=complex)
    return bool(np.allclose(rho - np.diag(np.diag(rho)), 0, atol=atol))
