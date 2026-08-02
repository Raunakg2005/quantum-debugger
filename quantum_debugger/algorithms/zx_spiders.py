"""
ZX-calculus: spiders and their linear maps.

The ZX-calculus is a diagrammatic language for qubit quantum computing. Diagrams are built from two
generators -- **Z-spiders** (green) and **X-spiders** (red) -- each carrying a phase and any number
of input/output legs, connected by wires. A Z-spider with ``m`` inputs, ``n`` outputs and phase
``alpha`` is the linear map

    Z(m, n, alpha) = |0>^{⊗n}<0|^{⊗m} + e^{i alpha} |1>^{⊗n}<1|^{⊗m},

and an X-spider is the same in the ``|+>/|->`` basis, i.e. a Z-spider conjugated by Hadamards on
every leg. Any diagram denotes a matrix, obtained by tensor-contracting the spiders along their
wires -- and the power of the calculus is that a small set of *rewrite rules* transforms diagrams
while provably preserving that matrix.

This module builds the spider tensors and their matrices; :mod:`zx_rewrite`, :mod:`zx_gates`, and
:mod:`phase_gadgets` build on it. Everything is verified against the exact matrix semantics.
"""

import numpy as np

H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)


def hadamard_matrix():
    """The Hadamard matrix -- the ZX Hadamard box that swaps the Z (green) and X (red) colours."""
    return H.copy()


def z_spider_tensor(n_in, n_out, phase=0.0):
    """
    The Z-spider as a rank-``(n_in + n_out)`` tensor of shape ``(2,) * (n_in + n_out)`` (inputs first).
    It is ``1`` on the all-zero leg configuration, ``e^{i phase}`` on the all-one configuration, and
    ``0`` otherwise.
    """
    rank = n_in + n_out
    T = np.zeros((2,) * rank, dtype=complex)
    if rank == 0:
        return np.array(1.0 + np.exp(1j * phase), dtype=complex)
    T[(0,) * rank] = 1.0
    T[(1,) * rank] = np.exp(1j * phase)
    return T


def spider_to_matrix(tensor, n_in, n_out):
    """Reshape a spider tensor (inputs the first ``n_in`` axes, outputs the last ``n_out``) into a
    ``2^{n_out} x 2^{n_in}`` matrix acting inputs -> outputs."""
    tensor = np.asarray(tensor, dtype=complex)
    # move to (outputs..., inputs...) then reshape
    perm = list(range(n_in, n_in + n_out)) + list(range(n_in))
    M = np.transpose(tensor, perm).reshape(2 ** n_out, 2 ** n_in)
    return M


def z_spider_matrix(n_in, n_out, phase=0.0):
    """The Z-spider ``Z(n_in, n_out, phase)`` as a ``2^{n_out} x 2^{n_in}`` matrix."""
    return spider_to_matrix(z_spider_tensor(n_in, n_out, phase), n_in, n_out)


def x_spider_tensor(n_in, n_out, phase=0.0):
    """The X-spider tensor: the Z-spider with a Hadamard applied to every leg (colour change)."""
    T = z_spider_tensor(n_in, n_out, phase)
    rank = n_in + n_out
    for axis in range(rank):
        T = np.tensordot(H, T, axes=([1], [axis]))
        T = np.moveaxis(T, 0, axis)
    return T


def x_spider_matrix(n_in, n_out, phase=0.0):
    """The X-spider ``X(n_in, n_out, phase)`` as a ``2^{n_out} x 2^{n_in}`` matrix."""
    return spider_to_matrix(x_spider_tensor(n_in, n_out, phase), n_in, n_out)


def is_hadamard_self_inverse(atol=1e-9):
    """Verify the Hadamard box is self-inverse: ``H H = I``."""
    return bool(np.allclose(H @ H, np.eye(2), atol=atol))


def green_phase(phase):
    """A single-leg-in, single-leg-out Z (green) phase spider ``Z(1, 1, phase) = diag(1, e^{i
    phase})`` -- a Z-axis rotation up to global phase."""
    return z_spider_matrix(1, 1, phase)


def red_phase(phase):
    """A single-in single-out X (red) phase spider ``X(1, 1, phase)`` -- an X-axis rotation up to
    global phase."""
    return x_spider_matrix(1, 1, phase)
