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
    def from_circuit(cls, circuit, max_bond: int = None) -> "MPS":
        """
        Run a :class:`QuantumCircuit` on the MPS engine, starting from ``|0...0>``.
        Single-qubit gates are applied exactly; two-qubit gates use the long-range
        SWAP path (any connectivity), truncating the bond to ``max_bond``. Three-or-more
        qubit gates must be decomposed first (e.g. via ``toffoli_gates`` / ``mcx_gates``).

        For low-entanglement circuits this runs at scales the dense simulator cannot.
        """
        mps = cls.zero_state(circuit.num_qubits, max_bond=max_bond)
        for gate in circuit.gates:
            qubits = list(gate.qubits)
            if len(qubits) == 1:
                mps.apply_single(gate.matrix, qubits[0])
            elif len(qubits) == 2:
                a, b = qubits
                G = np.asarray(gate.matrix, dtype=complex)
                if a < b:
                    mps.apply_two_long_range(G, a, b)
                else:
                    # Gate indexed on |a, b> = |higher, lower>; re-index to |lower, higher>.
                    mps.apply_two_long_range(_SWAP @ G @ _SWAP, b, a)
            else:
                raise NotImplementedError(
                    "MPS.from_circuit handles 1- and 2-qubit gates; decompose larger "
                    "gates first (e.g. toffoli_gates / mcx_gates)."
                )
        return mps

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

    def apply_two_long_range(self, gate, qubit_a: int, qubit_b: int) -> "MPS":
        """
        Apply a two-qubit ``gate`` to any pair ``(qubit_a, qubit_b)``, not just
        neighbours: SWAP the qubits together with a ladder of nearest-neighbour SWAPs,
        apply the gate, then SWAP back. The gate is indexed on ``|qubit_a, qubit_b>``
        with ``qubit_a`` the lower index (as for :meth:`apply_two`).
        """
        a, b = qubit_a, qubit_b
        if a > b:
            raise ValueError("qubit_a must be < qubit_b")
        if b == a + 1:
            return self.apply_two(gate, a)
        swap = _SWAP
        # Move qubit b down to a+1.
        for i in range(b - 1, a, -1):
            self.apply_two(swap, i)
        self.apply_two(gate, a)
        # Move it back.
        for i in range(a + 1, b):
            self.apply_two(swap, i)
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

    def expectation_pauli(self, pauli_string: str) -> float:
        """
        Expectation ``<psi|P|psi>`` of a full Pauli string ``P`` (``pauli_string[q]`` in
        ``I/X/Y/Z`` acts on qubit ``q``), by ``O(n * chi^3)`` contraction -- so any
        multi-qubit observable is measurable on a large MPS with no dense state.
        """
        paulis = {
            "I": np.eye(2, dtype=complex),
            "X": np.array([[0, 1], [1, 0]], dtype=complex),
            "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
            "Z": np.array([[1, 0], [0, -1]], dtype=complex),
        }
        ops = {i: paulis[p] for i, p in enumerate(pauli_string) if p != "I"}
        return float(np.real(self._environment_scan(ops) / self._environment_scan({})))

    def energy(self, terms) -> float:
        """
        Expectation ``<psi|H|psi>`` of a Hamiltonian given as ``(coefficient,
        pauli_string)`` terms (the format of ``pauli_decompose`` / the VQE solver),
        summed by contraction. Lets any Hamiltonian -- molecular, Fermi-Hubbard, spin
        -- be evaluated on a large MPS.
        """
        return float(sum(coeff * self.expectation_pauli(p) for coeff, p in terms))

    def correlation(self, obs_a, qubit_a: int, obs_b, qubit_b: int) -> float:
        """
        Two-point correlation ``<psi| O_a O_b |psi>`` for single-qubit operators on
        ``qubit_a`` and ``qubit_b`` (contraction, no dense state).
        """
        ops = {qubit_a: np.asarray(obs_a, dtype=complex),
               qubit_b: np.asarray(obs_b, dtype=complex)}
        return float(np.real(self._environment_scan(ops) / self._environment_scan({})))

    # --- operators & reduced states ----------------------------------------

    def apply_mpo(self, mpo, max_bond: int = None) -> "MPS":
        """
        Apply a matrix product operator ``mpo`` (list of rank-4 ``W`` tensors) to this
        MPS, returning ``H|psi>`` as a new MPS whose bond dimension is multiplied by the
        MPO bond dimension (optionally recompressed to ``max_bond``).
        """
        tensors = []
        for A, W in zip(self.tensors, mpo):
            cl, _, cr = A.shape
            Dl, _, _, Dr = W.shape
            T = np.einsum("lir,DoiE->lDorE", A, np.asarray(W, dtype=complex))
            tensors.append(T.reshape(cl * Dl, 2, cr * Dr))
        result = MPS(tensors, max_bond)
        if max_bond is not None:
            result = result.compress(max_bond)
        return result

    def expectation_mpo(self, mpo) -> float:
        """``<psi|H|psi>`` for an MPO, delegating to :func:`quantum_debugger.mpo.mpo_expectation`."""
        from .mpo import mpo_expectation

        return mpo_expectation(self, mpo)

    def single_qubit_rdm(self, qubit: int) -> np.ndarray:
        """
        Reduced density matrix of one ``qubit`` -- built from its Pauli expectations
        ``rho = (I + <X>X + <Y>Y + <Z>Z)/2`` by contraction, so it scales to large
        systems with no dense state.
        """
        paulis = {
            "X": np.array([[0, 1], [1, 0]], dtype=complex),
            "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
            "Z": np.array([[1, 0], [0, -1]], dtype=complex),
        }
        rho = np.eye(2, dtype=complex)
        for lab, P in paulis.items():
            rho = rho + self.expectation(P, qubit) * P
        return rho / 2

    def entanglement_spectrum(self, bond: int) -> np.ndarray:
        """
        The Schmidt coefficients (singular values, descending) across ``bond`` -- the
        full entanglement spectrum, of which :meth:`entanglement_entropy` is a summary.
        """
        return np.sqrt(np.sort(self._schmidt_squared(bond))[::-1])

    def two_qubit_rdm(self, qubit_a: int, qubit_b: int) -> np.ndarray:
        """
        Reduced density matrix of two qubits, assembled from their 16 two-qubit Pauli
        expectations ``(1/4) sum_{P,Q} <P_a Q_b> P (x) Q`` -- scalable, matching the
        dense partial trace. The pair is returned in sorted (little-endian) order.
        """
        a, b = (qubit_a, qubit_b) if qubit_a < qubit_b else (qubit_b, qubit_a)
        paulis = [
            np.eye(2, dtype=complex),
            np.array([[0, 1], [1, 0]], dtype=complex),
            np.array([[0, -1j], [1j, 0]], dtype=complex),
            np.array([[1, 0], [0, -1]], dtype=complex),
        ]
        rho = np.zeros((4, 4), dtype=complex)
        for pi, P in enumerate(paulis):
            for qi, Q in enumerate(paulis):
                if pi == 0 and qi == 0:
                    c = 1.0
                elif pi == 0:
                    c = self.expectation(Q, b)
                elif qi == 0:
                    c = self.expectation(P, a)
                else:
                    c = self.correlation(P, a, Q, b)
                rho = rho + c * np.kron(Q, P)
        return rho / 4

    def mutual_information(self, qubit_a: int, qubit_b: int) -> float:
        """
        Quantum mutual information ``I(a:b) = S(a) + S(b) - S(ab)`` between two qubits
        (bits), from their reduced density matrices -- total correlation across the pair.
        """
        def vn(rho):
            vals = np.linalg.eigvalsh(rho).real
            vals = vals[vals > 1e-12]
            return float(-np.sum(vals * np.log2(vals)))

        s_a = vn(self.single_qubit_rdm(qubit_a))
        s_b = vn(self.single_qubit_rdm(qubit_b))
        s_ab = vn(self.two_qubit_rdm(qubit_a, qubit_b))
        return s_a + s_b - s_ab

    def concurrence(self, qubit_a: int, qubit_b: int) -> float:
        """
        Wootters concurrence between two qubits (from their reduced density matrix) --
        the pairwise entanglement, 0 for a product pair and 1 for a Bell pair.
        """
        from .density_matrix import DensityMatrix

        return DensityMatrix(rho=self.two_qubit_rdm(qubit_a, qubit_b)).concurrence()

    def schmidt_gap(self, bond: int) -> float:
        """
        Gap between the two largest squared Schmidt values across ``bond`` -- an order
        parameter that closes at a quantum phase transition. 1 for a product cut.
        """
        s2 = np.sort(self._schmidt_squared(bond))[::-1]
        return float(s2[0] - (s2[1] if len(s2) > 1 else 0.0))

    def bloch_vector(self, qubit: int) -> np.ndarray:
        """Bloch vector ``(<X>, <Y>, <Z>)`` of one ``qubit`` (contraction, no dense state)."""
        paulis = {
            "X": np.array([[0, 1], [1, 0]], dtype=complex),
            "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
            "Z": np.array([[1, 0], [0, -1]], dtype=complex),
        }
        return np.array([self.expectation(P, qubit) for P in paulis.values()])

    def purity_profile(self) -> list:
        """Single-qubit purity ``Tr(rho_i^2)`` on every site (1 = pure, 0.5 = maximally
        mixed) -- a local measure of how entangled each qubit is with the rest."""
        out = []
        for q in range(self.n):
            r = self.single_qubit_rdm(q)
            out.append(float(np.real(np.trace(r @ r))))
        return out

    def total_magnetization(self, observable) -> float:
        """Sum of ``<O_i>`` over all qubits for a single-qubit ``observable``."""
        return float(sum(self.magnetization_profile(observable)))

    def amplitude(self, bits) -> complex:
        """The amplitude ``<bits|psi>`` for a computational-basis string (qubit ``i`` =
        ``bits[i]``), by contracting the fixed-bit tensor slices -- ``O(n·chi^2)``, no
        dense state."""
        v = np.ones(1, dtype=complex)
        for i, b in enumerate(bits):
            v = v @ self.tensors[i][:, int(b), :]
        return complex(v[0])

    def probability(self, bits) -> float:
        """Born probability ``|<bits|psi>|^2`` of a computational-basis outcome."""
        return float(abs(self.amplitude(bits)) ** 2)

    def most_probable(self, shots: int = 2000, seed: int = 0):
        """
        The most probable computational-basis outcome, estimated from ``shots`` samples
        (returns the bitstring and its exact Born probability).
        """
        counts = self.sample(shots, seed)
        best = max(counts, key=counts.get)
        return {"bitstring": best, "probability": self.probability([int(c) for c in best])}

    def structure_factor(self, observable, momentum: float) -> float:
        """
        Static structure factor ``S(k) = (1/n) sum_{i,j} e^{i k (i-j)} <O_i O_j>`` at
        wavevector ``momentum`` -- the Fourier transform of the spatial correlations,
        peaking at the ordering wavevector.
        """
        O = np.asarray(observable, dtype=complex)
        n = self.n
        total = 0.0 + 0j
        for i in range(n):
            for j in range(n):
                cij = self.expectation(O @ O, i) if i == j else self.correlation(O, i, O, j)
                total += np.exp(1j * momentum * (i - j)) * cij
        return float(np.real(total) / n)

    # --- construction helpers ----------------------------------------------

    @classmethod
    def from_product(cls, single_qubit_states, max_bond: int = None) -> "MPS":
        """
        Product-state MPS from a list of single-qubit amplitude pairs ``[a, b]`` per
        qubit (each normalized). All bond dimensions are 1.
        """
        tensors = []
        for s in single_qubit_states:
            v = np.asarray(s, dtype=complex)
            v = v / np.linalg.norm(v)
            tensors.append(v.reshape(1, 2, 1))
        return cls(tensors, max_bond)

    @classmethod
    def from_bitstring(cls, bits, max_bond: int = None) -> "MPS":
        """Computational-basis-state MPS ``|bits>`` from a bit sequence (qubit ``i`` =
        ``bits[i]``, little-endian). All bond dimensions 1."""
        tensors = []
        for b in bits:
            t = np.zeros((1, 2, 1), dtype=complex)
            t[0, int(b), 0] = 1.0
            tensors.append(t)
        return cls(tensors, max_bond)

    @classmethod
    def random(cls, n: int, bond: int = 4, seed: int = 0, max_bond: int = None) -> "MPS":
        """
        A random MPS on ``n`` qubits with bond dimension ``bond`` (bonds taper to 1 at
        the ends). Normalized. Useful for testing and benchmarking.
        """
        rng = np.random.default_rng(seed)
        tensors = []
        chi_left = 1
        for i in range(n):
            chi_right = 1 if i == n - 1 else min(bond, 2 ** (i + 1), 2 ** (n - i - 1))
            t = rng.normal(size=(chi_left, 2, chi_right)) + 1j * rng.normal(
                size=(chi_left, 2, chi_right)
            )
            tensors.append(t)
            chi_left = chi_right
        m = cls(tensors, max_bond)
        m.tensors[0] = m.tensors[0] / m.norm()
        return m

    # --- linear algebra on MPS ---------------------------------------------

    def add(self, other: "MPS", normalize: bool = True) -> "MPS":
        """
        Sum of two MPS by the direct-sum-of-bonds construction: the result represents
        ``|self> + |other>`` (normalized by default). Bond dimensions add.
        """
        if other.n != self.n:
            raise ValueError("MPS add requires equal qubit counts")
        n = self.n
        tensors = []
        for k in range(n):
            A, B = self.tensors[k], other.tensors[k]
            al, _, ar = A.shape
            bl, _, br = B.shape
            if k == 0:
                T = np.concatenate([A, B], axis=2)
            elif k == n - 1:
                T = np.concatenate([A, B], axis=0)
            else:
                T = np.zeros((al + bl, 2, ar + br), dtype=complex)
                T[:al, :, :ar] = A
                T[al:, :, ar:] = B
            tensors.append(T)
        result = MPS(tensors, self.max_bond)
        if normalize:
            result.tensors[0] = result.tensors[0] / result.norm()
        return result

    def compress(self, max_bond: int) -> "MPS":
        """
        Recompress the MPS to bond dimension ``max_bond`` by an SVD roundtrip
        (canonicalize, truncate). Returns a new MPS; the truncation fidelity to the
        original is ``|<compressed|self>|^2``.
        """
        sv = self.to_statevector()
        return MPS.from_statevector(sv, max_bond=max_bond)

    def truncation_error(self, max_bond: int) -> float:
        """
        Weight lost when the MPS is compressed to bond dimension ``max_bond``:
        ``1 - |<compressed|self>|^2``. Zero when the state already fits (a GHZ at
        ``max_bond >= 2``); grows as more of the entanglement spectrum is discarded.
        """
        return float(max(0.0, 1.0 - self.fidelity(self.compress(max_bond))))

    def normalize(self) -> "MPS":
        """Rescale the MPS to unit norm in place (folding the scale into the first
        tensor). Returns ``self``."""
        nrm = self.norm()
        if nrm > 1e-300:
            self.tensors[0] = self.tensors[0] / nrm
        return self

    # --- readout extensions ------------------------------------------------

    def magnetization_profile(self, observable) -> list:
        """``<O_i>`` on every qubit for a single-qubit ``observable`` (e.g. Z)."""
        O = np.asarray(observable, dtype=complex)
        return [self.expectation(O, q) for q in range(self.n)]

    def correlation_profile(self, obs_a, obs_b, ref: int = 0) -> list:
        """``<O_a(ref) O_b(j)>`` versus site ``j`` -- a spatial correlation function."""
        A = np.asarray(obs_a, dtype=complex)
        B = np.asarray(obs_b, dtype=complex)
        out = []
        for j in range(self.n):
            if j == ref:
                out.append(self.expectation(A @ B, j))
            else:
                out.append(self.correlation(A, ref, B, j))
        return out

    def variance(self, terms) -> float:
        """
        Energy variance ``<H^2> - <H>^2`` of a Pauli-sum Hamiltonian ``terms`` -- zero
        iff the MPS is an exact eigenstate (a convergence check for DMRG/imaginary TEBD).
        """
        from .algorithms.hamiltonian_simulation import hamiltonian_matrix, pauli_decompose

        H = hamiltonian_matrix(terms, self.n)
        H2_terms = pauli_decompose(H @ H)
        e = self.energy(terms)
        return float(self.energy(H2_terms) - e**2)

    def renyi_entropy(self, bond: int, alpha: float = 2.0) -> float:
        """
        Renyi-``alpha`` entanglement entropy across ``bond`` (bits). ``alpha -> 1`` is the
        von Neumann entropy (:meth:`entanglement_entropy`); ``alpha = 2`` is the
        collision entropy ``-log2 sum lambda^4``.
        """
        # Recover the Schmidt values on this bond from the canonicalized entropy sweep.
        lam2 = self._schmidt_squared(bond)
        lam2 = lam2[lam2 > 1e-14]
        if abs(alpha - 1.0) < 1e-9:
            return float(-np.sum(lam2 * np.log2(lam2)))
        return float(np.log2(np.sum(lam2**alpha)) / (1 - alpha))

    def _schmidt_squared(self, bond: int) -> np.ndarray:
        """Squared Schmidt coefficients across ``bond`` (from canonicalization)."""
        T = [t.copy() for t in self.tensors]
        n = len(T)
        for i in range(n - 1, 0, -1):
            chi_l, d, chi_r = T[i].shape
            U, S, Vh = np.linalg.svd(T[i].reshape(chi_l, d * chi_r), full_matrices=False)
            T[i] = Vh.reshape(len(S), d, chi_r)
            T[i - 1] = np.tensordot(T[i - 1], U * S, axes=(2, 0))
        carry = T[0]
        for i in range(n - 1):
            chi_l, d, chi_r = carry.shape
            U, S, Vh = np.linalg.svd(carry.reshape(chi_l * d, chi_r), full_matrices=False)
            S = S / np.linalg.norm(S)
            if i == bond:
                return S**2
            carry = np.tensordot(np.diag(S) @ Vh, T[i + 1], axes=(1, 0))
        return np.array([1.0])


# Convenience gate matrices (little-endian two-qubit gates).
CNOT = GateLibrary.CNOT
H = GateLibrary.H
_SWAP = np.array(
    [[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=complex
)
