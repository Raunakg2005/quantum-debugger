"""
Quantum contextuality: the Peres-Mermin magic square

Nine two-qubit Pauli observables arranged in a 3x3 grid:

        XI   IX   XX
        IZ   ZI   ZZ
        XZ   ZX   YY

Every row and every column is a mutually commuting triple, so its three
observables can be measured *jointly*. The row products are all ``+I`` and the
column products are ``+I, +I, -I`` -- so the product of the measured outcomes in
any context is fixed by the operators alone, for ANY state.

The magic: a classical (non-contextual) assignment of pre-existing values +/-1 to
the nine observables cannot satisfy all six constraints -- the product of the three
row constraints is +1 while the product of the three column constraints is -1, yet
both multiply the same nine values. Brute force over all 2^9 assignments shows at
most 5 of 6 constraints can hold. Quantum mechanics satisfies all 6, on every
state, deterministically -- measurement outcomes cannot be pre-existing values
independent of the measurement context (Kochen-Specker theorem, 2-qubit proof).
"""

import itertools

import numpy as np

from ..stabilizer import stabilizer_to_pauli_matrix as _pauli

_SQUARE = [
    ["XI", "IX", "XX"],
    ["IZ", "ZI", "ZZ"],
    ["XZ", "ZX", "YY"],
]

# +1 for each row; the third column multiplies to -I.
_ROW_SIGNS = [1, 1, 1]
_COL_SIGNS = [1, 1, -1]


def _mat(label: str) -> np.ndarray:
    return _pauli(1, label)


def mermin_peres_square() -> dict:
    """
    Verify the algebraic structure of the magic square directly:

      * every row and column is a mutually commuting triple;
      * each row's operator product is ``+I``; the columns give ``+I, +I, -I``.

    Returns dict with ``square`` (the labels), ``row_signs``, ``col_signs``,
    ``all_contexts_commute``, and ``products_verified``.
    """
    eye = np.eye(4, dtype=complex)
    commute = True
    products_ok = True

    contexts = [(_SQUARE[r], _ROW_SIGNS[r]) for r in range(3)]
    contexts += [([_SQUARE[r][c] for r in range(3)], _COL_SIGNS[c]) for c in range(3)]

    for labels, sign in contexts:
        mats = [_mat(s) for s in labels]
        for A, B in itertools.combinations(mats, 2):
            if not np.allclose(A @ B, B @ A, atol=1e-12):
                commute = False
        prod = mats[0] @ mats[1] @ mats[2]
        if not np.allclose(prod, sign * eye, atol=1e-12):
            products_ok = False

    return {
        "square": [row[:] for row in _SQUARE],
        "row_signs": list(_ROW_SIGNS),
        "col_signs": list(_COL_SIGNS),
        "all_contexts_commute": commute,
        "products_verified": products_ok,
    }


def classical_assignment_maximum() -> dict:
    """
    Brute-force every non-contextual assignment of +/-1 values to the nine
    observables and count how many of the six product constraints each satisfies.

    Returns dict with ``max_satisfied`` (= 5: no assignment meets all six) and
    ``total_assignments`` (512). The parity obstruction: the six constraints
    multiply to -1 but each value appears in them exactly twice.
    """
    best = 0
    for bits in itertools.product([1, -1], repeat=9):
        v = np.array(bits).reshape(3, 3)
        sat = 0
        for r in range(3):
            if v[r, 0] * v[r, 1] * v[r, 2] == _ROW_SIGNS[r]:
                sat += 1
        for c in range(3):
            if v[0, c] * v[1, c] * v[2, c] == _COL_SIGNS[c]:
                sat += 1
        best = max(best, sat)
    return {"max_satisfied": best, "total_assignments": 512}


def quantum_context_measurement(
    state_vector, context: str, index: int, seed: int = 0
) -> dict:
    """
    Jointly measure one context (``context`` = ``"row"`` or ``"col"``, ``index`` in
    0..2) of the magic square on an arbitrary 2-qubit state, by sequential
    projective measurement of its three commuting observables.

    The product of the three +/-1 outcomes ALWAYS equals the context's fixed sign --
    deterministic for every state and every random branch -- which is what no
    non-contextual value assignment can reproduce across all six contexts.

    Returns dict with ``outcomes``, ``product``, and ``expected_sign``.
    """
    if context == "row":
        labels, sign = _SQUARE[index], _ROW_SIGNS[index]
    elif context == "col":
        labels, sign = [_SQUARE[r][index] for r in range(3)], _COL_SIGNS[index]
    else:
        raise ValueError("context must be 'row' or 'col'")

    psi = np.asarray(state_vector, dtype=complex)
    psi = psi / np.linalg.norm(psi)
    rng = np.random.default_rng(seed)

    outcomes = []
    for label in labels:
        M = _mat(label)
        eye = np.eye(4, dtype=complex)
        P_plus = (eye + M) / 2
        p_plus = float(np.real(psi.conj() @ P_plus @ psi))
        if rng.random() < p_plus:
            outcomes.append(1)
            psi = P_plus @ psi
        else:
            outcomes.append(-1)
            psi = (eye - P_plus) @ psi
        psi = psi / np.linalg.norm(psi)

    return {
        "outcomes": outcomes,
        "product": int(np.prod(outcomes)),
        "expected_sign": sign,
    }
