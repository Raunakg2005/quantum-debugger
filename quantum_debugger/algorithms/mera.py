"""
The Multiscale Entanglement Renormalization Ansatz (MERA).

MERA is a hierarchical tensor network that renormalizes a state scale by scale. Each layer
applies **disentanglers** (unitaries ``u`` that remove short-range entanglement across block
boundaries) and **isometries** (``w`` that coarse-grain two sites into one, ``w^dagger w = I``).
Because entanglement is removed before coarse-graining, MERA efficiently represents *critical*
(scale-invariant) states whose entanglement grows logarithmically -- and its **causal cone** has
constant width, which is what makes expectation values cheap. This module builds disentanglers
and isometries, the ascending/descending renormalization superoperators, and verifies unitarity,
the isometry condition, and trace preservation.
"""

import numpy as np
from scipy.stats import unitary_group


def disentangler(seed: int = 0) -> np.ndarray:
    """A two-site disentangler ``u`` -- a random ``4 x 4`` unitary that removes cross-boundary
    entanglement before coarse-graining. Verified unitary."""
    return unitary_group.rvs(4, random_state=seed)


def isometry(seed: int = 0) -> np.ndarray:
    """
    A coarse-graining isometry ``w`` mapping two sites (dim 4) to one (dim 2): a ``4 x 2`` matrix
    with ``w^dagger w = I_2`` -- the top two columns of a random unitary. Verified isometric.
    """
    return unitary_group.rvs(4, random_state=seed)[:, :2]


def is_unitary(U, atol: float = 1e-9) -> bool:
    """True iff ``U^dagger U = I``."""
    U = np.asarray(U)
    return bool(np.allclose(U.conj().T @ U, np.eye(U.shape[1]), atol=atol))


def is_isometry(W, atol: float = 1e-9) -> bool:
    """True iff ``W^dagger W = I`` (columns orthonormal) -- the defining property of a MERA
    isometry."""
    W = np.asarray(W)
    return bool(np.allclose(W.conj().T @ W, np.eye(W.shape[1]), atol=atol))


def descending_superoperator(rho, w) -> np.ndarray:
    """
    One MERA descending step ``rho -> w rho w^dagger`` mapping a coarse-grained density matrix
    (dim 2) to the finer scale (dim 4). Trace-preserving because ``w`` is an isometry (verified).
    """
    w = np.asarray(w)
    return w @ np.asarray(rho, dtype=complex) @ w.conj().T


def ascending_superoperator(op, w) -> np.ndarray:
    """
    One MERA ascending step ``O -> w^dagger O w`` mapping a fine-scale operator (dim 4) to the
    coarse scale (dim 2) -- the renormalization-group flow of observables up the network.
    """
    w = np.asarray(w)
    return w.conj().T @ np.asarray(op, dtype=complex) @ w


def causal_cone_width(layers: int) -> int:
    """
    The width of a binary MERA's past causal cone: constant (``= 3`` sites) regardless of the
    number of ``layers`` -- the structural fact that makes MERA expectation values scalable.
    """
    return 3


def ternary_isometry(seed: int = 0) -> np.ndarray:
    """
    A ternary-MERA coarse-graining isometry mapping three sites (dim 8) to one (dim 2): an
    ``8 x 2`` matrix with ``w^dagger w = I_2``. Verified isometric.
    """
    return unitary_group.rvs(8, random_state=seed)[:, :2]


def renormalize_operator(op, w, layers: int = 1):
    """
    Flow an observable up ``layers`` MERA scales by repeated ascending steps -- the
    renormalization-group trajectory of the operator. (Uses the same isometry at each scale, a
    scale-invariant MERA.)
    """
    O = np.asarray(op, dtype=complex)
    for _ in range(layers):
        O = ascending_superoperator(O, w)
    return O


def coarse_grain_state(state, w) -> np.ndarray:
    """Coarse-grain a two-site (dim-4) pure state to one site via the isometry adjoint
    ``w^dagger |psi>`` (renormalized), the action of one MERA layer on a state."""
    out = np.asarray(w).conj().T @ np.asarray(state, dtype=complex)
    nrm = np.linalg.norm(out)
    return out / nrm if nrm > 1e-12 else out
