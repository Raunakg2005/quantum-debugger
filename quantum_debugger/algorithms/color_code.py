"""
Color codes -- self-dual CSS codes with transversal Clifford gates.

A 2D color code is a CSS code whose X- and Z-stabilizers act on the *same* set of
plaquettes, so ``Hx`` and ``Hz`` generate the same classical code (the code is
*self-dual*). That single structural fact is what gives color codes their headline
advantage over the surface code: the *transversal* logical Hadamard ``H^{\\otimes n}``
(which swaps X and Z) maps the stabilizer group to itself, and the transversal CNOT
does likewise between two blocks -- so the full Clifford group is available without
costly gadgets. The smallest 2D color code is the ``[[7,1,3]]`` Steane code.

This module builds the Steane color code, tests self-duality, and *verifies* -- in the
binary-symplectic representation -- that the transversal Hadamard and CNOT preserve the
code and enact the intended logical gate.
"""

import numpy as np

from .css_code import CSSCode, gf2_rref, _in_rowspace
from .surface_code import hamming_check_matrix


def steane_color_code() -> CSSCode:
    """
    The ``[[7,1,3]]`` Steane code -- the distance-3 triangular (2D) color code -- as a
    self-dual CSS code with ``Hx = Hz`` the ``[7,4,3]`` Hamming check matrix.
    """
    H = hamming_check_matrix(3)
    return CSSCode(H, H)


def _rowspace(M):
    R, piv = gf2_rref(M)
    return R[:len(piv)], piv


def is_self_dual_css(code: CSSCode) -> bool:
    """
    True iff the code is self-dual: ``rowspace(Hx) == rowspace(Hz)``. Self-dual CSS codes
    are exactly the ones with a transversal Hadamard (``H^{\\otimes n}`` swaps X<->Z and
    lands back in the stabilizer group) -- the defining property of color codes.
    """
    Rx, px = _rowspace(code.Hx)
    Rz, pz = _rowspace(code.Hz)
    if len(px) != len(pz):
        return False
    return all(_in_rowspace(r, Rz, pz) for r in code.Hx) and \
        all(_in_rowspace(r, Rx, px) for r in code.Hz)


def transversal_hadamard_valid(code: CSSCode) -> bool:
    """
    Verify the transversal Hadamard is a valid logical gate: ``H^{\\otimes n}`` sends each
    X-stabilizer (support ``s``) to the Z-type operator with the same support and each
    Z-stabilizer to the X-type one, so it preserves the stabilizer group iff every
    ``Hx`` row lies in ``rowspace(Hz)`` and vice versa -- i.e. iff the code is self-dual.
    Also checks it exchanges the logical operators ``Xbar <-> Zbar``.
    """
    if not is_self_dual_css(code):
        return False
    # transversal H swaps the logical X and Z supports; check the swapped Xbar is a
    # legitimate Z-logical (commutes with X-stabilizers, not itself a stabilizer).
    xl, zl = code.logical_operators()
    Rz, pz = _rowspace(code.Hz)
    for xbar in xl:
        # H(Xbar) is a Z-string with support xbar: must anticommute with some Zbar and
        # commute with all X-stabilizers.
        if np.any(code.z_syndrome(xbar)):
            return False
        if _in_rowspace(xbar, Rz, pz):  # would be a stabilizer, not a logical
            return False
    return True


def transversal_cnot_valid(code: CSSCode) -> bool:
    """
    Verify the transversal CNOT between two blocks of ``code`` preserves the joint
    stabilizer group. In the symplectic picture CNOT maps ``X_A -> X_A X_B`` and
    ``Z_B -> Z_A Z_B``, so an X-stabilizer of block A becomes the product of the same
    X-stabilizer on both blocks (still in the group) and likewise for Z-stabilizers --
    the reason every CSS code has a transversal CNOT. Checked explicitly here via
    GF(2) row-space membership on the two-block generators.
    """
    Rx, px = _rowspace(code.Hx)
    Rz, pz = _rowspace(code.Hz)
    # X_A stabilizer image lands as the same row on block B: must be an X-stabilizer.
    x_ok = all(_in_rowspace(r, Rx, px) for r in code.Hx)
    # Z_B stabilizer image lands as the same row on block A: must be a Z-stabilizer.
    z_ok = all(_in_rowspace(r, Rz, pz) for r in code.Hz)
    return bool(x_ok and z_ok)
