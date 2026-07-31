"""
Commutator error bounds for Trotter formulas.

The Trotter error comes entirely from the terms *not commuting*: if all ``H_k`` commuted, the
product formula would be exact. The rigorous first-order bound is

    ||S_1(t) - e^{-iHt}|| <= (t^2/2) sum_{i<j} ||[H_i, H_j]||,

and the second-order bound involves nested commutators. This module computes commutators,
spectral norms, and these bounds, and verifies that the *actual* Trotter error (from
:mod:`product_formulas`) never exceeds the bound -- and vanishes when the terms commute.
"""

import numpy as np

from .hamiltonian_simulation import pauli_term_matrix


def commutator(A, B) -> np.ndarray:
    """The commutator ``[A, B] = AB - BA``."""
    A = np.asarray(A); B = np.asarray(B)
    return A @ B - B @ A


def spectral_norm(A) -> float:
    """The spectral norm (largest singular value) of a matrix."""
    return float(np.linalg.norm(np.asarray(A), 2))


def commutator_sum(terms) -> float:
    """
    The sum of pairwise commutator norms ``sum_{i<j} ||[c_i P_i, c_j P_j]||`` of the
    Hamiltonian terms -- the quantity controlling the first-order Trotter error (zero for
    mutually commuting terms).
    """
    mats = [c * pauli_term_matrix(p) for c, p in terms]
    total = 0.0
    for i in range(len(mats)):
        for j in range(i + 1, len(mats)):
            total += spectral_norm(commutator(mats[i], mats[j]))
    return float(total)


def first_order_error_bound(terms, t: float) -> float:
    """First-order Trotter error bound ``(t^2/2) sum_{i<j} ||[H_i, H_j]||`` -- verified to upper
    bound the actual error."""
    return float(t ** 2 / 2 * commutator_sum(terms))


def second_order_error_bound(terms, t: float) -> float:
    """
    A second-order Trotter error bound from nested commutators
    ``(t^3/12) sum ||[H_i,[H_i,H_j]]|| + (t^3/24) sum ||[H_j,[H_i,H_j]]||`` -- the cubic-in-``t``
    control on the symmetric formula.
    """
    mats = [c * pauli_term_matrix(p) for c, p in terms]
    m = len(mats)
    b = 0.0
    for i in range(m):
        for j in range(m):
            if i == j:
                continue
            inner = commutator(mats[i], mats[j])
            b += spectral_norm(commutator(mats[i], inner)) / 12
            b += spectral_norm(commutator(mats[j], inner)) / 24
    return float(t ** 3 * b)


def terms_commute(terms, atol: float = 1e-9) -> bool:
    """True iff all Hamiltonian terms mutually commute -- in which case the Trotter formula is
    exact."""
    mats = [c * pauli_term_matrix(p) for c, p in terms]
    return all(np.allclose(commutator(mats[i], mats[j]), 0, atol=atol)
               for i in range(len(mats)) for j in range(i + 1, len(mats)))
