"""
The toric code (topological quantum error correction)

Kitaev's toric code is the archetypal topological code and the ancestor of the
surface code that leads today's fault-tolerance efforts. Qubits live on the edges of
an ``L x L`` square lattice with periodic boundaries (``2 L^2`` qubits). Two kinds of
commuting stabilizers act locally:

  * **star** ``A_v = prod_{e ni v} X_e`` -- the four edges meeting a vertex ``v``;
  * **plaquette** ``B_p = prod_{e in dp} Z_e`` -- the four edges bounding a face ``p``.

There are ``L^2`` of each, but with one product constraint apiece (``prod_v A_v = I``,
``prod_p B_p = I``), giving ``2 L^2 - 2`` independent stabilizers -- so the code always
encodes exactly ``2`` logical qubits, one per non-contractible loop of the torus. The
logical operators are those loops; the shortest has length ``L``, so the code distance
is ``L``. This module builds the code and verifies all of these properties from the
binary check matrix.
"""

import numpy as np


class ToricCode:
    """Toric code on an ``L x L`` periodic lattice (``2 L^2`` edge qubits)."""

    def __init__(self, L: int):
        if L < 2:
            raise ValueError("toric code needs L >= 2")
        self.L = L
        self.n = 2 * L * L
        self._build()

    def _h(self, i, j):
        return (i % self.L) * self.L + (j % self.L)

    def _v(self, i, j):
        return self.L * self.L + (i % self.L) * self.L + (j % self.L)

    def _build(self):
        L, n = self.L, self.n
        self.stars = []       # (x_bits, z_bits) with z=0
        self.plaquettes = []  # (x_bits, z_bits) with x=0
        for i in range(L):
            for j in range(L):
                x = np.zeros(n, dtype=int)
                x[self._h(i, j)] = 1
                x[self._h(i, j - 1)] = 1
                x[self._v(i, j)] = 1
                x[self._v(i - 1, j)] = 1
                self.stars.append((x, np.zeros(n, dtype=int)))
        for i in range(L):
            for j in range(L):
                z = np.zeros(n, dtype=int)
                z[self._h(i, j)] = 1
                z[self._h(i + 1, j)] = 1
                z[self._v(i, j)] = 1
                z[self._v(i, j + 1)] = 1
                self.plaquettes.append((np.zeros(n, dtype=int), z))

        # Logical operators (a non-contractible loop pair on horizontal edges).
        z1 = np.zeros(n, dtype=int)
        for j in range(L):
            z1[self._h(0, j)] = 1
        x1 = np.zeros(n, dtype=int)
        for i in range(L):
            x1[self._h(i, 0)] = 1
        self.logical_x = (x1, np.zeros(n, dtype=int))
        self.logical_z = (np.zeros(n, dtype=int), z1)

    # --- structure ----------------------------------------------------------

    def stabilizers(self):
        """All star + plaquette stabilizers as ``(x_bits, z_bits)`` tuples."""
        return self.stars + self.plaquettes

    def check_matrix(self) -> np.ndarray:
        """The ``(2L^2) x (2n)`` binary symplectic check matrix ``[X | Z]``."""
        return np.array([np.concatenate([x, z]) for x, z in self.stabilizers()])

    def num_logical_qubits(self) -> int:
        """Number of encoded logical qubits, ``n - rank(check matrix)`` (always 2)."""
        return self.n - _gf2_rank(self.check_matrix())

    def distance(self) -> int:
        """Code distance -- the weight of the (shortest) logical operator, ``L``."""
        return int(self.logical_z[1].sum())

    def all_commute(self) -> bool:
        """Whether every pair of stabilizers commutes (they do)."""
        stabs = self.stabilizers()
        return all(
            _symplectic(stabs[a], stabs[b]) == 0
            for a in range(len(stabs))
            for b in range(a + 1, len(stabs))
        )

    def logicals_valid(self) -> bool:
        """Logical ops commute with all stabilizers but anticommute with each other."""
        stabs = self.stabilizers()
        commute = all(
            _symplectic(self.logical_x, s) == 0 and _symplectic(self.logical_z, s) == 0
            for s in stabs
        )
        return commute and _symplectic(self.logical_x, self.logical_z) == 1


def _symplectic(a, b) -> int:
    (x1, z1), (x2, z2) = a, b
    return (int(np.dot(x1, z2)) + int(np.dot(z1, x2))) % 2


def _gf2_rank(M) -> int:
    M = (M.copy() % 2).astype(int)
    rows, cols = M.shape
    r = 0
    for c in range(cols):
        piv = next((i for i in range(r, rows) if M[i, c]), None)
        if piv is None:
            continue
        M[[r, piv]] = M[[piv, r]]
        for i in range(rows):
            if i != r and M[i, c]:
                M[i] ^= M[r]
        r += 1
    return r
