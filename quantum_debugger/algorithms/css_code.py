"""
CSS codes -- the general Calderbank-Shor-Steane construction.

A CSS code is built from two classical binary parity-check matrices ``Hx`` (X-type
stabilizers) and ``Hz`` (Z-type stabilizers) satisfying the orthogonality condition
``Hx Hz^T = 0 (mod 2)`` -- exactly the condition that every X-stabilizer commutes
with every Z-stabilizer. Then

    n = number of physical qubits (columns),
    k = n - rank(Hx) - rank(Hz)      logical qubits,
    d = min weight of a nontrivial logical operator.

X errors are detected by the Z-checks (``Hz e``) and Z errors by the X-checks
(``Hx e``), so decoding splits into two independent classical problems. This module
provides the constructor, the code parameters, logical operators from the GF(2)
kernels, the distance by exhaustive search (small codes), and a syndrome-lookup
decoder -- each verified against the exact stabilizer/logical structure. The surface
and color codes (see :mod:`surface_code`, :mod:`color_code`) are instances of it.
"""

import itertools

import numpy as np


# --- GF(2) linear algebra ---------------------------------------------------

def gf2_rref(M):
    """Row-reduced echelon form over GF(2); returns (rref, pivot_columns)."""
    A = (np.asarray(M, dtype=np.int8) % 2).copy()
    rows, cols = A.shape
    pivots = []
    r = 0
    for c in range(cols):
        pivot = None
        for i in range(r, rows):
            if A[i, c]:
                pivot = i
                break
        if pivot is None:
            continue
        A[[r, pivot]] = A[[pivot, r]]
        for i in range(rows):
            if i != r and A[i, c]:
                A[i] ^= A[r]
        pivots.append(c)
        r += 1
        if r == rows:
            break
    return A, pivots


def gf2_rank(M) -> int:
    """Rank of a binary matrix over GF(2)."""
    if np.asarray(M).size == 0:
        return 0
    _, pivots = gf2_rref(M)
    return len(pivots)


def gf2_nullspace(M):
    """Basis (list of vectors) for the right null space ``{v : M v = 0}`` over GF(2)."""
    A = np.asarray(M, dtype=np.int8) % 2
    if A.size == 0:
        return []
    rows, cols = A.shape
    R, pivots = gf2_rref(A)
    pivot_set = set(pivots)
    free = [c for c in range(cols) if c not in pivot_set]
    basis = []
    for f in free:
        v = np.zeros(cols, dtype=np.int8)
        v[f] = 1
        for row_i, pc in enumerate(pivots):
            if R[row_i, f]:
                v[pc] = 1
        basis.append(v)
    return basis


def _in_rowspace(v, basis_rref, pivots) -> bool:
    """Is vector ``v`` in the row space whose RREF/pivots are given?"""
    w = (np.asarray(v, dtype=np.int8) % 2).copy()
    for row_i, pc in enumerate(pivots):
        if w[pc]:
            w ^= basis_rref[row_i]
    return not np.any(w)


class CSSCode:
    """
    CSS code from X-check matrix ``Hx`` and Z-check matrix ``Hz`` (each ``m_i x n`` over
    GF(2)) with ``Hx Hz^T = 0``. Raises if the orthogonality condition fails.
    """

    def __init__(self, Hx, Hz):
        self.Hx = np.asarray(Hx, dtype=np.int8) % 2
        self.Hz = np.asarray(Hz, dtype=np.int8) % 2
        if self.Hx.shape[1] != self.Hz.shape[1]:
            raise ValueError("Hx and Hz must have the same number of columns (qubits)")
        if not self.all_commute():
            raise ValueError("CSS condition violated: Hx Hz^T != 0 (mod 2)")
        self.n = self.Hx.shape[1]

    def all_commute(self) -> bool:
        """True iff every X-stabilizer commutes with every Z-stabilizer (``Hx Hz^T = 0``)."""
        return not np.any((self.Hx @ self.Hz.T) % 2)

    def num_logical_qubits(self) -> int:
        """``k = n - rank(Hx) - rank(Hz)``."""
        return self.Hx.shape[1] - gf2_rank(self.Hx) - gf2_rank(self.Hz)

    def logical_operators(self):
        """
        Representative logical operators as ``(x_logicals, z_logicals)``, each a list of
        length-``n`` GF(2) vectors. X-logicals lie in ``ker(Hz)`` modulo ``rowspace(Hx)``;
        Z-logicals in ``ker(Hx)`` modulo ``rowspace(Hz)``. Returns ``k`` of each.
        """
        return (self._logicals(self.Hz, self.Hx), self._logicals(self.Hx, self.Hz))

    def _logicals(self, H_commute, H_stab):
        # vectors commuting with H_commute (in its kernel), independent modulo rowspace(H_stab)
        kernel = gf2_nullspace(H_commute)
        stab_rref, stab_piv = gf2_rref(H_stab)
        chosen, basis_rref, basis_piv = [], stab_rref.copy(), list(stab_piv)
        for v in kernel:
            if not _in_rowspace(v, basis_rref, basis_piv):
                chosen.append(v)
                # add v to the running span so later picks are independent of it
                stacked = np.vstack([basis_rref, v]) if basis_rref.size else v[None, :]
                basis_rref, basis_piv = gf2_rref(stacked)
        return chosen

    def distance(self) -> int:
        """
        Code distance: the minimum weight of a nontrivial logical operator, by exhaustive
        search over the kernels (feasible for small codes). ``d = min(dx, dz)``.
        """
        dz = self._min_logical_weight(self.Hx, self.Hz)  # Z-type logicals
        dx = self._min_logical_weight(self.Hz, self.Hx)  # X-type logicals
        return min(dx, dz)

    def _min_logical_weight(self, H_commute, H_stab):
        kernel = gf2_nullspace(H_commute)
        stab_rref, stab_piv = gf2_rref(H_stab)
        best = self.Hx.shape[1] + 1
        # enumerate the span of the kernel basis (nontrivial coset reps)
        kb = kernel
        for bits in itertools.product([0, 1], repeat=len(kb)):
            if not any(bits):
                continue
            v = np.zeros(self.Hx.shape[1], dtype=np.int8)
            for b, vec in zip(bits, kb):
                if b:
                    v ^= vec
            if _in_rowspace(v, stab_rref, stab_piv):
                continue  # trivial (a stabilizer)
            w = int(v.sum())
            if 0 < w < best:
                best = w
        return best

    def x_syndrome(self, x_error):
        """Syndrome of an X error: the Z-checks it violates, ``Hz x (mod 2)``."""
        return (self.Hz @ (np.asarray(x_error, dtype=np.int8) % 2)) % 2

    def z_syndrome(self, z_error):
        """Syndrome of a Z error: the X-checks it violates, ``Hx z (mod 2)``."""
        return (self.Hx @ (np.asarray(z_error, dtype=np.int8) % 2)) % 2

    def decode_min_weight(self, x_error, max_weight: int = 2):
        """
        Minimum-weight X correction for the syndrome of ``x_error``, searched over errors
        up to ``max_weight`` (an optimal decoder within that radius). Returns the
        correction vector. A code of distance ``d`` corrects any error of weight
        ``<= (d-1)//2`` this way.
        """
        target = tuple(int(b) for b in self.x_syndrome(x_error))
        for w in range(max_weight + 1):
            for support in itertools.combinations(range(self.n), w):
                e = np.zeros(self.n, dtype=np.int8)
                e[list(support)] = 1
                if tuple(int(b) for b in self.x_syndrome(e)) == target:
                    return e
        raise ValueError("no correction found within max_weight")

    def decode_lookup(self):
        """
        Build a minimum-weight syndrome -> correction table for X errors (using the
        Z-checks). Maps each syndrome to the lowest-weight error producing it -- an
        optimal decoder for small codes. Returns a dict ``{syndrome_tuple: correction}``.
        """
        table = {}
        for w in range(self.n + 1):
            for support in itertools.combinations(range(self.n), w):
                e = np.zeros(self.n, dtype=np.int8)
                e[list(support)] = 1
                s = tuple(int(b) for b in self.x_syndrome(e))
                if s not in table:
                    table[s] = e
            if len(table) == 2 ** self.Hz.shape[0]:
                break
        return table


def css_from_classical(H) -> CSSCode:
    """
    Self-dual CSS code from a single classical parity-check matrix ``H`` that is weakly
    self-dual (``H H^T = 0 mod 2``, i.e. the classical code contains its dual). Then
    ``Hx = Hz = H`` is a valid CSS code with equal X and Z stabilizers -- the family that
    admits a transversal Hadamard (the 2D color codes). ``hamming_check_matrix(3)`` gives
    the Steane code.
    """
    H = np.asarray(H, dtype=np.int8) % 2
    if np.any((H @ H.T) % 2):
        raise ValueError("H is not weakly self-dual (H H^T != 0), no self-dual CSS code")
    return CSSCode(H, H)


def hypergraph_product(H1, H2) -> CSSCode:
    """
    Hypergraph-product (Tillich-Zemor) CSS code from two classical parity-check matrices
    ``H1`` (``m1 x n1``) and ``H2`` (``m2 x n2``):

        Hx = [ H1 (x) I_{n2} | I_{m1} (x) H2^T ]
        Hz = [ I_{n1} (x) H2 | H1^T (x) I_{m2} ]

    on ``n = n1 n2 + m1 m2`` qubits. The construction guarantees ``Hx Hz^T = 0`` for any
    inputs -- the general recipe that turns *any* pair of classical codes into a quantum
    LDPC code. With two repetition codes it yields the planar surface code.
    """
    H1 = np.asarray(H1, dtype=np.int8) % 2
    H2 = np.asarray(H2, dtype=np.int8) % 2
    m1, n1 = H1.shape
    m2, n2 = H2.shape
    Hx = np.hstack([np.kron(H1, np.eye(n2, dtype=np.int8)),
                    np.kron(np.eye(m1, dtype=np.int8), H2.T)]) % 2
    Hz = np.hstack([np.kron(np.eye(n1, dtype=np.int8), H2),
                    np.kron(H1.T, np.eye(m2, dtype=np.int8))]) % 2
    return CSSCode(Hx, Hz)
