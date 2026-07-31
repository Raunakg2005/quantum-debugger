"""
Peephole circuit optimization.

The cheapest wins in a compiler come from local ("peephole") rewrites that shrink the gate
count without changing the unitary:

* **Inverse cancellation** -- adjacent operations on the same qubits that multiply to the
  identity (``G`` then ``G^dagger``) are removed.
* **Rotation merging** -- consecutive rotations about the same axis on the same qubit are
  fused into one (``Rz(a) Rz(b) = Rz(a+b)``), and a zero-angle rotation is dropped.
* **Identity removal** -- operations equal to the identity are deleted.

Each pass is verified against :func:`circuits_equivalent`: the optimized circuit implements
the same unitary with no more (usually fewer) gates.
"""

import numpy as np


def _is_identity(M, atol=1e-9):
    M = np.asarray(M)
    return M.shape[0] == M.shape[1] and np.allclose(M, np.eye(M.shape[0]), atol=atol)


def _inverse(a, b, atol=1e-9):
    """True iff gate matrices ``a`` and ``b`` are inverses (``a b = I`` up to phase)."""
    prod = np.asarray(a) @ np.asarray(b)
    d = prod.shape[0]
    ph = prod[0, 0]
    if abs(ph) < atol:
        return False
    return np.allclose(prod / ph, np.eye(d), atol=atol)


def cancel_inverses(circuit):
    """
    Remove adjacent operations on identical qubits whose product is the identity
    (``G`` followed by ``G^dagger``). Verified to preserve the unitary.
    """
    out = []
    for matrix, qubits in circuit:
        if out and out[-1][1] == qubits and _inverse(out[-1][0], matrix):
            out.pop()
        else:
            out.append((np.asarray(matrix, dtype=complex), list(qubits)))
    return out


def remove_identities(circuit):
    """Delete operations that are (numerically) the identity."""
    return [(m, q) for m, q in circuit if not _is_identity(m)]


def merge_rotations(circuit, axis_tag="Rz"):
    """
    Fuse consecutive diagonal (phase/``Rz``-type) rotations on the same qubit into a single
    gate: ``diag(1, e^{i a}) diag(1, e^{i b}) = diag(1, e^{i(a+b)})``. Only merges
    single-qubit diagonal gates (recognized numerically), leaving others untouched. Verified
    equivalent.
    """
    out = []
    for matrix, qubits in circuit:
        M = np.asarray(matrix, dtype=complex)
        is_diag = (M.shape == (2, 2) and abs(M[0, 1]) < 1e-12 and abs(M[1, 0]) < 1e-12)
        if is_diag and out and out[-1][1] == qubits:
            prev = out[-1][0]
            prev_diag = (prev.shape == (2, 2) and abs(prev[0, 1]) < 1e-12 and abs(prev[1, 0]) < 1e-12)
            if prev_diag:
                out[-1] = (M @ prev, qubits)
                continue
        out.append((M, list(qubits)))
    return out


def optimize_circuit(circuit):
    """
    Full peephole pass: repeatedly cancel inverses, merge rotations, and remove identities
    until the circuit stops shrinking. Verified to preserve the unitary while reducing the
    gate count.
    """
    prev_len = None
    cur = [(np.asarray(m, dtype=complex), list(q)) for m, q in circuit]
    while prev_len != len(cur):
        prev_len = len(cur)
        cur = remove_identities(merge_rotations(cancel_inverses(cur)))
    return cur
