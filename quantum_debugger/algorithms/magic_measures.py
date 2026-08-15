"""
Magic (non-stabilizerness): the stabilizer Renyi entropy

Clifford circuits are classically simulable; "magic" is the resource that takes a
computation beyond them. The stabilizer 2-Renyi entropy (Leone, Oliviero & Hamma,
Phys. Rev. Lett. 128, 050402, 2022) quantifies it directly from Pauli expectation
values: for an n-qubit pure state with ``d = 2^n``,

    M_2 = -log2( sum_P <psi|P|psi>^4 / d ),

summing over all ``4^n`` Pauli strings. Properties (all verified here):

  * ``M_2 = 0`` iff the state is a stabilizer state;
  * invariant under any Clifford unitary;
  * additive over tensor products;
  * ``M_2(|T>) = log2(4/3)`` for the T-magic state -- the fuel of
    :mod:`magic_state` injection.
"""

import itertools

import numpy as np

from ..stabilizer import stabilizer_to_pauli_matrix as _pauli


def stabilizer_renyi_entropy(state_vector) -> float:
    """
    The stabilizer 2-Renyi entropy ``M_2`` of a pure n-qubit state (n small --
    the sum runs over all ``4^n`` Pauli strings). 0 for stabilizer states,
    ``log2(4/3) ~ 0.415`` for the single-qubit T-magic state, additive over
    tensor products, Clifford-invariant.
    """
    psi = np.asarray(state_vector, dtype=complex)
    psi = psi / np.linalg.norm(psi)
    n = int(round(np.log2(len(psi))))
    d = 2**n

    total = 0.0
    for labels in itertools.product("IXYZ", repeat=n):
        P = _pauli(1, "".join(labels))
        exp = float(np.real(psi.conj() @ P @ psi))
        total += exp**4
    return float(-np.log2(total / d))


def magic_of_t_states(count: int) -> dict:
    """
    Magic of ``count`` T states in parallel: ``M_2(|T>^{x k}) = k log2(4/3)``
    (additivity). Returns dict with ``computed`` (from the full ``4^n`` Pauli sum)
    and ``analytic`` (``count * log2(4/3)``).
    """
    t = np.array([1, np.exp(1j * np.pi / 4)], dtype=complex) / np.sqrt(2)
    state = np.array([1.0], dtype=complex)
    for _ in range(count):
        state = np.kron(state, t)
    return {
        "computed": stabilizer_renyi_entropy(state),
        "analytic": count * np.log2(4 / 3),
    }
