"""
Matrix Product State simulator (breaking the exponential wall)

A matrix product state writes an ``n``-qubit amplitude as a chain of small tensors,

    psi(s_0, s_1, ..., s_{n-1}) = A[0]^{s_0} A[1]^{s_1} ... A[n-1]^{s_{n-1}},

where each ``A[i]`` has shape ``(chi_left, 2, chi_right)``. The bond dimension ``chi``
is 1 for a product state and grows with entanglement, but for the low-entanglement
states that obey an area law it stays *bounded* -- so an MPS stores the state in
``O(n * chi^2)`` numbers instead of ``2^n``. That is what lets this engine simulate
tens or hundreds of qubits where the dense state-vector simulator cannot.

Gates are applied by local tensor contraction; two-qubit gates are followed by an SVD
that re-splits the pair and truncates the bond back to ``max_bond`` (the controlled
approximation at the heart of DMRG/TEBD). Single-qubit gates and expectation values
are exact. Qubit ``i`` is MPS site ``i`` (little-endian, matching the rest of the
library).
"""

import numpy as np

from .core.gates import GateLibrary


class MPS:
    """Matrix product state on ``n`` qubits with maximum bond dimension ``max_bond``."""

    def __init__(self, tensors, max_bond=None):
        self.tensors = tensors
        self.n = len(tensors)
        self.max_bond = max_bond

    # --- construction -------------------------------------------------------

    @classmethod
    def zero_state(cls, n: int, max_bond: int = None) -> "MPS":
        """The ``|0...0>`` product state (all bond dimensions 1)."""
        tensors = []
        for _ in range(n):
            t = np.zeros((1, 2, 1), dtype=complex)
            t[0, 0, 0] = 1.0
            tensors.append(t)
        return cls(tensors, max_bond)

    @classmethod
    def from_statevector(cls, state_vector, max_bond: int = None, tol: float = 1e-12) -> "MPS":
        """
        Exact MPS for a dense ``state_vector`` via sequential SVD (truncated to
        ``max_bond`` if given). Qubit ``i`` becomes site ``i`` (little-endian).
        """
        psi = np.asarray(state_vector, dtype=complex)
        psi = psi / np.linalg.norm(psi)
        n = int(round(np.log2(len(psi))))
        # Reorder axes so site 0 = qubit 0 (numpy reshape puts qubit 0 as the LSB axis).
        tensor = psi.reshape([2] * n).transpose(list(range(n - 1, -1, -1)))
        remainder = tensor.reshape(1, 2**n)

        tensors = []
        chi_left = 1
        for i in range(n):
            remainder = remainder.reshape(chi_left * 2, 2 ** (n - i - 1))
            U, S, Vh = np.linalg.svd(remainder, full_matrices=False)
            keep = S > tol
            if max_bond is not None:
                keep[max_bond:] = False
            U, S, Vh = U[:, keep], S[keep], Vh[keep, :]
            chi_right = len(S)
            tensors.append(U.reshape(chi_left, 2, chi_right))
            remainder = np.diag(S) @ Vh
            chi_left = chi_right
        return cls(tensors, max_bond)

    # --- readout ------------------------------------------------------------

    def to_statevector(self) -> np.ndarray:
        """Contract the MPS back into a dense little-endian state vector."""
        psi = self.tensors[0]
        for t in self.tensors[1:]:
            psi = np.tensordot(psi, t, axes=(psi.ndim - 1, 0))
        psi = psi.reshape([2] * self.n)  # axes are sites 0..n-1 = qubits 0..n-1
        psi = psi.transpose(list(range(self.n - 1, -1, -1)))  # back to little-endian
        return psi.reshape(-1)

    def bond_dimensions(self) -> list:
        """The bond dimension on each of the ``n-1`` links."""
        return [t.shape[2] for t in self.tensors[:-1]]

    def max_bond_dimension(self) -> int:
        dims = self.bond_dimensions()
        return max(dims) if dims else 1

    def _environment_scan(self, ops: dict) -> complex:
        """
        Contract ``<psi| (prod_i O_i) |psi>`` by sweeping left environments in
        ``O(n * chi^3)`` -- never forming the dense state. ``ops`` maps a site index to
        a 2x2 operator (identity elsewhere).
        """
        eye = np.eye(2, dtype=complex)
        E = np.ones((1, 1), dtype=complex)  # (bra bond, ket bond)
        for i, A in enumerate(self.tensors):
            Op = ops.get(i, eye)
            tmp = np.einsum("lm,msr->lsr", E, A)          # ket contracted
            tmp = np.einsum("ts,lsr->ltr", Op, tmp)       # apply operator
            E = np.einsum("lta,ltr->ar", np.conj(A), tmp)  # bra contracted
        return complex(E[0, 0])

    def norm(self) -> float:
        """The state norm ``sqrt(<psi|psi>)`` via tensor contraction (no dense vector)."""
        return float(np.sqrt(np.real(self._environment_scan({}))))

    # --- gates --------------------------------------------------------------

    def apply_single(self, gate, qubit: int) -> "MPS":
        """Apply a single-qubit gate to ``qubit`` (exact, local contraction)."""
        U = np.asarray(gate, dtype=complex)
        t = self.tensors[qubit]
        self.tensors[qubit] = np.tensordot(U, t, axes=(1, 1)).transpose(1, 0, 2)
        return self

    def apply_two(self, gate, qubit: int) -> "MPS":
        """
        Apply a two-qubit ``gate`` (4x4) to the neighbouring pair ``(qubit, qubit+1)``,
        then re-split by SVD and truncate the bond to ``max_bond``. The gate is indexed
        as acting on ``|q, q+1>`` with qubit the lower (little-endian) index.
        """
        i = qubit
        A, B = self.tensors[i], self.tensors[i + 1]
        chi_l, chi_r = A.shape[0], B.shape[2]
        # Merge the pair: (chi_l, 2, 2, chi_r).
        theta = np.tensordot(A, B, axes=(2, 0))
        # Apply the gate on the two physical legs. The dense 4x4 gate is indexed in
        # little-endian pair order (qubit i = LSB), so reshaping gives G[hi, lo, hi, lo];
        # transpose (1,0,3,2) puts it in (lo=i, hi=i+1) order to match theta's legs.
        G = np.asarray(gate, dtype=complex).reshape(2, 2, 2, 2).transpose(1, 0, 3, 2)
        theta = np.einsum("abcd,lcdr->labr", G, theta)
        # Re-split via SVD across the bond.
        mat = theta.reshape(chi_l * 2, 2 * chi_r)
        U, S, Vh = np.linalg.svd(mat, full_matrices=False)
        keep = S > 1e-14
        if self.max_bond is not None:
            keep[self.max_bond:] = False
        U, S, Vh = U[:, keep], S[keep], Vh[keep, :]
        chi_new = len(S)
        self.tensors[i] = U.reshape(chi_l, 2, chi_new)
        self.tensors[i + 1] = (np.diag(S) @ Vh).reshape(chi_new, 2, chi_r)
        return self

    def expectation(self, observable, qubit: int) -> float:
        """
        Expectation ``<psi|O|psi>`` of a single-qubit observable on ``qubit``, via
        ``O(n * chi^3)`` tensor contraction -- works for hundreds of qubits without
        ever building the dense state. Normalized by ``<psi|psi>``.
        """
        O = np.asarray(observable, dtype=complex)
        num = self._environment_scan({qubit: O})
        den = self._environment_scan({})
        return float(np.real(num / den))

    def overlap(self, other: "MPS") -> complex:
        """
        Inner product ``<other|self>`` of two MPS on the same number of qubits, by
        sweeping the double-layer contraction in ``O(n * chi^3)`` -- no dense state.
        """
        if other.n != self.n:
            raise ValueError("MPS overlap requires equal qubit counts")
        E = np.ones((1, 1), dtype=complex)  # (bra bond, ket bond)
        for A, B in zip(other.tensors, self.tensors):
            # E[a,b], B[b,s,b'] -> tmp[a,s,b'] ; then conj(A)[a,s,a'] -> E'[a',b']
            tmp = np.einsum("ab,bsr->asr", E, B)
            E = np.einsum("asx,asr->xr", np.conj(A), tmp)
        return complex(E[0, 0])

    def fidelity(self, other: "MPS") -> float:
        """State fidelity ``|<other|self>|^2 / (||self||^2 ||other||^2)`` to another MPS."""
        ov = abs(self.overlap(other)) ** 2
        return float(ov / (self.norm() ** 2 * other.norm() ** 2))

    def bond_entropies(self) -> list:
        """
        Entanglement entropy (bits) across each of the ``n-1`` bonds, from the Schmidt
        spectrum obtained by canonicalizing the MPS (a right-to-left SVD sweep to
        right-canonical form, then a left-to-right SVD sweep reading off the singular
        values). Scales to large ``n`` -- no dense state. The maximum over bonds is the
        state's peak bipartite entanglement.
        """
        T = [t.copy() for t in self.tensors]
        n = len(T)
        for i in range(n - 1, 0, -1):
            chi_l, d, chi_r = T[i].shape
            U, S, Vh = np.linalg.svd(T[i].reshape(chi_l, d * chi_r), full_matrices=False)
            T[i] = Vh.reshape(len(S), d, chi_r)
            T[i - 1] = np.tensordot(T[i - 1], U * S, axes=(2, 0))

        entropies = []
        carry = T[0]
        for i in range(n - 1):
            chi_l, d, chi_r = carry.shape
            U, S, Vh = np.linalg.svd(carry.reshape(chi_l * d, chi_r), full_matrices=False)
            S = S / np.linalg.norm(S)
            s2 = S**2
            s2 = s2[s2 > 1e-14]
            entropies.append(float(-np.sum(s2 * np.log2(s2))))
            carry = np.tensordot(np.diag(S) @ Vh, T[i + 1], axes=(1, 0))
        return entropies

    def entanglement_entropy(self, bond: int) -> float:
        """Entanglement entropy (bits) across ``bond`` (the cut between sites
        ``0..bond`` and ``bond+1..n-1``)."""
        return self.bond_entropies()[bond]

    def sample(self, shots: int, seed: int = 0) -> dict:
        """
        Draw ``shots`` computational-basis measurement outcomes from the MPS by exact
        sequential conditional sampling -- ``O(shots * n * chi^2)``, with no dense
        state. Returns a dict mapping bitstring (character ``i`` = qubit ``i``) to its
        count; the distribution is the exact Born rule.
        """
        n = self.n
        rng = np.random.default_rng(seed)
        # Right environments R[i] = <tail_i|tail_i> as a (bond, bond) matrix.
        R = [None] * (n + 1)
        R[n] = np.ones((1, 1), dtype=complex)
        for i in range(n - 1, -1, -1):
            A = self.tensors[i]
            R[i] = np.einsum("asr,rt,bst->ab", A, R[i + 1], np.conj(A))

        counts = {}
        for _ in range(shots):
            left = np.ones(1, dtype=complex)  # ket boundary after the fixed prefix
            bits = []
            for i in range(n):
                A = self.tensors[i]
                amp0 = left @ A[:, 0, :]
                amp1 = left @ A[:, 1, :]
                p0 = float(np.real(np.conj(amp0) @ R[i + 1] @ amp0))
                p1 = float(np.real(np.conj(amp1) @ R[i + 1] @ amp1))
                if rng.random() < p0 / (p0 + p1):
                    left, b = amp0, "0"
                else:
                    left, b = amp1, "1"
                bits.append(b)
            key = "".join(bits)
            counts[key] = counts.get(key, 0) + 1
        return counts

    def correlation(self, obs_a, qubit_a: int, obs_b, qubit_b: int) -> float:
        """
        Two-point correlation ``<psi| O_a O_b |psi>`` for single-qubit operators on
        ``qubit_a`` and ``qubit_b`` (contraction, no dense state).
        """
        ops = {qubit_a: np.asarray(obs_a, dtype=complex),
               qubit_b: np.asarray(obs_b, dtype=complex)}
        return float(np.real(self._environment_scan(ops) / self._environment_scan({})))


# Convenience gate matrices (little-endian two-qubit gates).
CNOT = GateLibrary.CNOT
H = GateLibrary.H
