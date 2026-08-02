"""
ZX-calculus rewrite rules, verified against the matrix semantics.

The value of the ZX-calculus is its small, *complete* set of rewrite rules that transform a diagram
without changing the linear map it denotes. This module states the core rules and checks each one as
an exact matrix identity:

* **Spider fusion** -- two connected same-colour spiders merge, their phases adding.
* **Identity** -- a phase-0, two-legged spider is a plain wire.
* **Colour change** -- an X-spider is a Z-spider conjugated by Hadamards on every leg.
* **Copy** -- a Z-spider copies computational-basis states (the ``|0>/|1>`` copy map).
* **pi-commutation** -- an X(pi) pushed through a Z-spider negates the phase and copies to the
  outputs.

Every function returns ``True`` when the rule holds for the given parameters, computed by comparing
the two sides' matrices.
"""

import numpy as np

from .zx_spiders import (
    z_spider_matrix, x_spider_matrix, z_spider_tensor, x_spider_tensor,
    spider_to_matrix, hadamard_matrix,
)

H = hadamard_matrix()


def _kron_all(op, n):
    out = np.eye(1, dtype=complex)
    for _ in range(n):
        out = np.kron(out, op)
    return out


def spider_fusion_z(phase_a, phase_b, atol=1e-9):
    """Z spider fusion on a single wire: ``Z(1,1,a) Z(1,1,b) = Z(1,1,a+b)`` -- phases add."""
    lhs = z_spider_matrix(1, 1, phase_a) @ z_spider_matrix(1, 1, phase_b)
    rhs = z_spider_matrix(1, 1, phase_a + phase_b)
    return bool(np.allclose(lhs, rhs, atol=atol))


def spider_fusion_multi(phase_a, phase_b, atol=1e-9):
    """
    Multi-leg Z fusion: connecting an output of ``Z(1,2,a)`` to the input of ``Z(1,2,b)`` yields a
    single ``Z(1,3,a+b)`` spider (three outputs). Checked by contraction.
    """
    A = z_spider_tensor(1, 2, phase_a)      # [in, o1, o2]
    B = z_spider_tensor(1, 2, phase_b)      # [in, o3, o4]
    fused = np.einsum('a b w, w c d -> a b c d', A, B)   # connect o2->in of B
    lhs = spider_to_matrix(fused, 1, 3)
    rhs = z_spider_matrix(1, 3, phase_a + phase_b)
    return bool(np.allclose(lhs, rhs, atol=atol))


def spider_fusion_x(phase_a, phase_b, atol=1e-9):
    """X spider fusion: ``X(1,1,a) X(1,1,b) = X(1,1,a+b)``."""
    lhs = x_spider_matrix(1, 1, phase_a) @ x_spider_matrix(1, 1, phase_b)
    rhs = x_spider_matrix(1, 1, phase_a + phase_b)
    return bool(np.allclose(lhs, rhs, atol=atol))


def identity_rule(atol=1e-9):
    """A phase-0 two-legged spider is the identity wire: ``Z(1,1,0) = X(1,1,0) = I``."""
    return bool(np.allclose(z_spider_matrix(1, 1, 0.0), np.eye(2), atol=atol)
                and np.allclose(x_spider_matrix(1, 1, 0.0), np.eye(2), atol=atol))


def color_change_rule(n_in, n_out, phase, atol=1e-9):
    """Colour change: ``X(m,n,alpha) = H^{⊗n} Z(m,n,alpha) H^{⊗m}`` -- Hadamards on every leg swap the
    spider colour."""
    lhs = x_spider_matrix(n_in, n_out, phase)
    rhs = _kron_all(H, n_out) @ z_spider_matrix(n_in, n_out, phase) @ _kron_all(H, n_in)
    return bool(np.allclose(lhs, rhs, atol=atol))


def copy_rule(atol=1e-9):
    """
    The copy rule: the ``Z(1,2,0)`` spider copies computational-basis states, ``|0> -> |00>`` and
    ``|1> -> |11>`` -- it is the classical COPY (GHZ) map.
    """
    C = z_spider_matrix(1, 2, 0.0)
    return bool(np.allclose(C[:, 0], [1, 0, 0, 0], atol=atol)
                and np.allclose(C[:, 1], [0, 0, 0, 1], atol=atol))


def pi_copy_rule(n_out=2, alpha=0.7, atol=1e-9):
    """
    The pi-commutation (copy) rule: an ``X(pi)`` on the input of ``Z(1, n, alpha)`` equals
    ``Z(1, n, -alpha)`` with an ``X(pi)`` on every output -- the Z-phase flips sign and the red
    pi copies to all legs. Holds up to the global phase ``e^{i alpha}`` (ZX rules preserve the map
    only up to a scalar), which this check accounts for.
    """
    X_pi = x_spider_matrix(1, 1, np.pi)
    lhs = z_spider_matrix(1, n_out, alpha) @ X_pi
    rhs = _kron_all(X_pi, n_out) @ z_spider_matrix(1, n_out, -alpha)
    idx = np.unravel_index(np.argmax(np.abs(rhs)), rhs.shape)
    if abs(rhs[idx]) < atol:
        return False
    scale = lhs[idx] / rhs[idx]
    return bool(np.isclose(abs(scale), 1.0, atol=atol) and np.allclose(lhs, scale * rhs, atol=atol))


def hopf_rule(atol=1e-9):
    """
    The Hopf rule: a Z-spider and an X-spider connected by *two* wires decouple into a product of
    disconnected spiders (up to a scalar). Checked via the doubled-edge contraction being
    rank-1 (a product state), i.e. proportional to the outer product of the two boundary spiders.
    """
    Z = z_spider_tensor(1, 2, 0.0)          # [in, w1, w2]
    X = x_spider_tensor(2, 1, 0.0)          # [w1, w2, out]
    doubled = np.einsum('a i j, i j b -> a b', Z, X)   # connect both wires
    # Hopf law: the result is a rank-1 (disconnected) map
    return bool(np.linalg.matrix_rank(doubled, tol=1e-9) == 1)
