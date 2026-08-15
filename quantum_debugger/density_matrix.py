"""
Density-Matrix Simulator (open quantum systems)

Simulate mixed states and noise: apply unitary gates *and* Kraus noise channels to a
density matrix ``rho``, take partial traces, and read out purity, populations,
expectation values, and state fidelity. Where the state-vector simulator tracks a
pure state, this tracks the full ``rho`` so decoherence and mixing are exact.

Qubit ordering matches the rest of the library (qubit 0 = least significant).
"""

import numpy as np

from .core.quantum_state import apply_gate_tensor
from .core.gates import GateLibrary

_I = np.eye(2, dtype=complex)
_X = GateLibrary.X
_Y = GateLibrary.Y
_Z = GateLibrary.Z
_P0 = np.array([[1, 0], [0, 0]], dtype=complex)
_P1 = np.array([[0, 0], [0, 1]], dtype=complex)


def _embed(op, targets, n):
    """Full 2**n operator applying ``op`` to ``targets`` (reuses the tensor engine)."""
    dim = 2**n
    op = np.asarray(op, dtype=complex)
    emb = np.zeros((dim, dim), dtype=complex)
    for j in range(dim):
        col = np.zeros(dim, dtype=complex)
        col[j] = 1.0
        emb[:, j] = apply_gate_tensor(np, col, op, list(targets), n)
    return emb


def _matrix_sqrt(mat):
    """Principal square root of a Hermitian PSD matrix (via eigendecomposition)."""
    vals, vecs = np.linalg.eigh(mat)
    vals = np.clip(vals.real, 0.0, None)
    return (vecs * np.sqrt(vals)) @ vecs.conj().T


class DensityMatrix:
    """Density-matrix state of ``n`` qubits."""

    def __init__(self, n=None, rho=None, state_vector=None):
        if rho is not None:
            self.rho = np.asarray(rho, dtype=complex)
            self.n = int(round(np.log2(self.rho.shape[0])))
        elif state_vector is not None:
            sv = np.asarray(state_vector, dtype=complex)
            sv = sv / np.linalg.norm(sv)
            self.rho = np.outer(sv, sv.conj())
            self.n = int(round(np.log2(len(sv))))
        else:
            dim = 2**n
            self.rho = np.zeros((dim, dim), dtype=complex)
            self.rho[0, 0] = 1.0  # |0...0><0...0|
            self.n = n

    # --- evolution ---------------------------------------------------------

    def apply_unitary(self, U, qubits):
        """Apply a unitary ``U`` to ``qubits``: rho -> U rho U-dagger."""
        emb = _embed(U, qubits, self.n)
        self.rho = emb @ self.rho @ emb.conj().T
        return self

    def apply_channel(self, kraus_ops, qubits):
        """Apply a Kraus channel {K_i} to ``qubits``: rho -> sum_i K_i rho K_i-dagger."""
        new = np.zeros_like(self.rho)
        for K in kraus_ops:
            emb = _embed(K, qubits, self.n)
            new += emb @ self.rho @ emb.conj().T
        self.rho = new
        return self

    def evolve_lindblad(self, hamiltonian, collapse_ops=None, time=1.0):
        """
        Evolve ``rho`` for a duration ``time`` under the Lindblad master equation

            d rho / dt = -i [H, rho]
                         + sum_k ( L_k rho L_k-dagger
                                   - 1/2 { L_k-dagger L_k, rho } )

        with Hamiltonian ``H`` and collapse (jump) operators ``{L_k}`` -- the exact
        continuous-time model of decoherence (T1 relaxation, T2 dephasing, ...).

        ``hamiltonian`` and each collapse operator are full ``2**n x 2**n`` matrices.
        The evolution is computed exactly by exponentiating the Liouvillian
        superoperator (no time-stepping error). Returns ``self``.
        """
        from scipy.linalg import expm

        H = np.asarray(hamiltonian, dtype=complex)
        dim = H.shape[0]
        eye = np.eye(dim, dtype=complex)
        cols = [np.asarray(L, dtype=complex) for L in (collapse_ops or [])]

        # Liouvillian in column-stacking convention: vec(A rho B) = (B^T kron A) vec.
        liou = -1j * (np.kron(eye, H) - np.kron(H.T, eye))
        for L in cols:
            LdL = L.conj().T @ L
            liou += (
                np.kron(L.conj(), L)
                - 0.5 * np.kron(eye, LdL)
                - 0.5 * np.kron(LdL.T, eye)
            )

        vec = self.rho.flatten(order="F")
        vec = expm(liou * time) @ vec
        self.rho = vec.reshape((dim, dim), order="F")
        return self

    def measure(self, qubit, rng=None) -> int:
        """
        Projectively measure ``qubit`` in the computational basis, collapsing ``rho``.
        Returns 0 or 1 with the Born-rule probabilities.
        """
        rng = rng or np.random.default_rng()
        proj0 = _embed(_P0, [qubit], self.n)
        p0 = float(np.real(np.trace(proj0 @ self.rho)))
        outcome = 0 if rng.random() < p0 else 1
        proj = proj0 if outcome == 0 else _embed(_P1, [qubit], self.n)
        p = p0 if outcome == 0 else 1 - p0
        self.rho = (proj @ self.rho @ proj) / p
        return outcome

    def sample(self, shots: int, seed: int = 0) -> dict:
        """
        Sample ``shots`` full computational-basis measurement outcomes (non-destructive;
        the outcome distribution is the diagonal of ``rho``). Returns bitstring -> count
        with bit ``q`` = qubit ``q``.
        """
        rng = np.random.default_rng(seed)
        probs = self.probabilities()
        probs = np.clip(probs, 0, None)
        probs = probs / probs.sum()
        draws = rng.choice(len(probs), size=shots, p=probs)
        counts = {}
        for d in draws:
            key = "".join(str((int(d) >> q) & 1) for q in range(self.n))
            counts[key] = counts.get(key, 0) + 1
        return counts

    # --- readout -----------------------------------------------------------

    def purity(self) -> float:
        """Tr(rho^2): 1 for a pure state, down to 1/2**n for the maximally mixed state."""
        return float(np.real(np.trace(self.rho @ self.rho)))

    def von_neumann_entropy(self) -> float:
        """
        Von Neumann entropy ``S = -Tr(rho log2 rho)`` in bits: 0 for a pure state, up to
        ``n`` for the maximally mixed state.
        """
        vals = np.linalg.eigvalsh(self.rho).real
        vals = vals[vals > 1e-12]
        return float(-np.sum(vals * np.log2(vals)))

    def l1_coherence(self) -> float:
        """
        l1-norm of coherence: the sum of the magnitudes of the off-diagonal elements
        of ``rho`` in the computational basis. Zero for any diagonal (incoherent)
        state, 1 for a single-qubit ``|+>``, and up to ``2**n - 1`` for an
        n-qubit maximally coherent state.
        """
        off = self.rho - np.diag(np.diag(self.rho))
        return float(np.sum(np.abs(off)))

    def relative_entropy_coherence(self) -> float:
        """
        Relative entropy of coherence ``C_r = S(diag(rho)) - S(rho)`` in bits: the
        distance to the nearest incoherent state. Zero for a diagonal state, 1 bit for
        ``|+>`` or a Bell state, and equal to the state's basis-population entropy for a
        pure state.
        """
        diag = np.real(np.diag(self.rho))
        diag = diag[diag > 1e-12]
        s_diag = float(-np.sum(diag * np.log2(diag)))
        return s_diag - self.von_neumann_entropy()

    def concurrence(self) -> float:
        """
        Wootters concurrence of a two-qubit state (exact, any mixed state):
        ``C = max(0, l1 - l2 - l3 - l4)`` where ``l_i`` are the square roots of the
        eigenvalues (descending) of ``rho (Y x Y) rho* (Y x Y)``. 0 iff separable,
        1 for a Bell state; for a pure state ``C = 2|ad - bc|``.
        """
        if self.n != 2:
            raise ValueError("concurrence is defined for two-qubit states")
        yy = np.kron(_Y, _Y)
        # Hermitian similar form sqrt(rho) (YY rho* YY) sqrt(rho): same eigenvalues
        # as rho YY rho* YY, but computable with eigvalsh precision.
        sqrt_rho = _matrix_sqrt(self.rho)
        S = sqrt_rho @ (yy @ self.rho.conj() @ yy) @ sqrt_rho
        vals = np.sort(np.linalg.eigvalsh(S).real)[::-1]
        vals[vals < 1e-14] = 0.0  # numerical dust would inflate to ~1e-7 under sqrt
        vals = np.sqrt(vals)
        return float(max(0.0, vals[0] - vals[1] - vals[2] - vals[3]))

    def entanglement_of_formation(self) -> float:
        """
        Entanglement of formation in bits (Wootters, PRL 80, 2245, 1998):
        ``E = h((1 + sqrt(1 - C^2))/2)`` with ``h`` the binary entropy and ``C``
        the concurrence -- the exact cost, in Bell pairs, of preparing the state.
        0 iff separable, 1 for a Bell state.
        """
        C = self.concurrence()
        x = (1 + np.sqrt(max(0.0, 1 - C**2))) / 2
        if x <= 0 or x >= 1:
            return 0.0
        return float(-x * np.log2(x) - (1 - x) * np.log2(1 - x))

    def mutual_information(self, qubits) -> float:
        """
        Quantum mutual information ``I(A:B) = S(A) + S(B) - S(AB)`` in bits, where A is
        ``qubits`` and B is the rest -- the total (classical + quantum) correlation
        across the cut. Zero for a product state, 1 bit for a classically correlated
        pair, and 2 bits for a maximally entangled (Bell) pair.
        """
        rest = [q for q in range(self.n) if q not in qubits]
        s_a = self.partial_trace(qubits).von_neumann_entropy()
        s_b = self.partial_trace(rest).von_neumann_entropy()
        return s_a + s_b - self.von_neumann_entropy()

    def partial_transpose(self, qubits) -> "DensityMatrix":
        """
        Partial transpose of ``rho`` over the given ``qubits`` (subsystem A): transpose
        the row/column indices of those qubits only. The basis of the Peres-Horodecki
        (PPT) separability criterion -- see :meth:`negativity`.
        """
        n = self.n
        T = self.rho.reshape([2] * n + [2] * n)
        for q in qubits:
            T = np.swapaxes(T, q, n + q)
        return DensityMatrix(rho=T.reshape(2**n, 2**n))

    def negativity(self, qubits) -> float:
        """
        Entanglement negativity across the ``qubits`` vs rest bipartition:
        ``N = (||rho^{T_A}||_1 - 1) / 2``, the sum of the magnitudes of the negative
        eigenvalues of the partial transpose. Zero for a PPT (separable for 2x2 / 2x3)
        state; a Bell pair gives 1/2. A positive value certifies entanglement.
        """
        pt = self.partial_transpose(qubits).rho
        pt = (pt + pt.conj().T) / 2
        ev = np.linalg.eigvalsh(pt).real
        return float(np.sum(np.abs(ev[ev < 0])))

    def logarithmic_negativity(self, qubits) -> float:
        """
        Logarithmic negativity ``E_N = log2 ||rho^{T_A}||_1 = log2(2 N + 1)`` in bits:
        an entanglement monotone and an upper bound on distillable entanglement. Zero
        for a PPT state, 1 bit for a Bell pair.
        """
        return float(np.log2(2 * self.negativity(qubits) + 1))

    def entanglement_entropy(self, qubits) -> float:
        """
        Entanglement entropy of the ``qubits`` subsystem: the von Neumann entropy of its
        reduced density matrix. For a pure global state this measures entanglement across
        the cut (0 = product, 1 bit = a maximally entangled qubit pair).
        """
        return self.partial_trace(qubits).von_neumann_entropy()

    def probabilities(self) -> np.ndarray:
        """Computational-basis populations (the diagonal of rho)."""
        return np.real(np.diag(self.rho))

    def expectation(self, observable) -> float:
        """Expectation Tr(rho O) of a Hermitian observable given as a full matrix."""
        return float(
            np.real(np.trace(self.rho @ np.asarray(observable, dtype=complex)))
        )

    def fidelity(self, other) -> float:
        """
        State fidelity to ``other`` (a DensityMatrix or a pure state vector).

        Uses Uhlmann's fidelity ``(Tr sqrt(sqrt(rho) sigma sqrt(rho)))**2``.
        """
        if isinstance(other, DensityMatrix):
            sigma = other.rho
        else:
            sv = np.asarray(other, dtype=complex)
            sv = sv / np.linalg.norm(sv)
            sigma = np.outer(sv, sv.conj())
        sqrt_rho = _matrix_sqrt(self.rho)
        inner = _matrix_sqrt(sqrt_rho @ sigma @ sqrt_rho)
        return float(np.real(np.trace(inner)) ** 2)

    def partial_trace(self, keep) -> "DensityMatrix":
        """Reduced density matrix on ``keep`` qubits, tracing out the rest."""
        keep = sorted(keep)
        n = self.n
        traced = [q for q in range(n) if q not in keep]
        dim_k = 2 ** len(keep)
        red = np.zeros((dim_k, dim_k), dtype=complex)
        for i in range(2**n):
            for j in range(2**n):
                if all(((i >> q) & 1) == ((j >> q) & 1) for q in traced):
                    ri = sum(((i >> keep[m]) & 1) << m for m in range(len(keep)))
                    rj = sum(((j >> keep[m]) & 1) << m for m in range(len(keep)))
                    red[ri, rj] += self.rho[i, j]
        return DensityMatrix(rho=red)


# --- standard single-qubit Kraus channels ---------------------------------


def bit_flip(p: float):
    """Bit-flip channel: X with probability p."""
    return [np.sqrt(1 - p) * _I, np.sqrt(p) * _X]


def phase_flip(p: float):
    """Phase-flip channel: Z with probability p."""
    return [np.sqrt(1 - p) * _I, np.sqrt(p) * _Z]


def depolarizing(p: float):
    """Depolarizing channel: rho -> (1-p) rho + p I/2."""
    return [
        np.sqrt(1 - 3 * p / 4) * _I,
        np.sqrt(p / 4) * _X,
        np.sqrt(p / 4) * _Y,
        np.sqrt(p / 4) * _Z,
    ]


def pauli_channel(px: float, py: float, pz: float):
    """
    General single-qubit Pauli channel: apply X/Y/Z with probabilities px/py/pz
    (identity otherwise). Generalizes bit-flip, phase-flip, and depolarizing.
    """
    return [
        np.sqrt(max(0.0, 1 - px - py - pz)) * _I,
        np.sqrt(px) * _X,
        np.sqrt(py) * _Y,
        np.sqrt(pz) * _Z,
    ]


def amplitude_damping(gamma: float):
    """Amplitude damping (T1): |1> decays to |0> with rate gamma."""
    return [
        np.array([[1, 0], [0, np.sqrt(1 - gamma)]], dtype=complex),
        np.array([[0, np.sqrt(gamma)], [0, 0]], dtype=complex),
    ]


def phase_damping(gamma: float):
    """Phase damping (T2): loss of coherence without energy loss."""
    return [
        np.array([[1, 0], [0, np.sqrt(1 - gamma)]], dtype=complex),
        np.array([[0, 0], [0, np.sqrt(gamma)]], dtype=complex),
    ]


# --- T1 / T2 relaxation -----------------------------------------------------


def relaxation_times(gamma1: float, gamma_phi: float = 0.0, probe_time: float = 1.0) -> dict:
    """
    Extract the relaxation time ``T1`` and coherence time ``T2`` of a qubit evolving
    under the Lindblad equation with amplitude damping (rate ``gamma1 > 0``, jump
    operator ``sqrt(gamma1) sigma-``) and pure dephasing (rate ``gamma_phi``, jump
    ``sqrt(gamma_phi/2) sigma_z``), by probing the exact exponential decays of the
    excited population and the coherence of a ``|+>`` state.

    Verifies the fundamental relation of every real qubit's datasheet:

        1/T2 = 1/(2 T1) + 1/T_phi        (so T2 <= 2 T1 always),

    with equality iff there is no pure dephasing.

    Returns dict with ``T1``, ``T2``, ``T_phi`` (``inf`` if ``gamma_phi = 0``),
    ``identity_residual`` (|1/T2 - 1/(2T1) - 1/T_phi|, ~0), and ``t2_le_2t1``.
    """
    if gamma1 <= 0:
        raise ValueError("gamma1 must be > 0")

    sm = np.array([[0, 1], [0, 0]], dtype=complex)  # sigma-: |1> -> |0>
    cols = [np.sqrt(gamma1) * sm]
    if gamma_phi > 0:
        cols.append(np.sqrt(gamma_phi / 2) * _Z)
    H0 = np.zeros((2, 2), dtype=complex)
    t = probe_time

    # T1 probe: |1> population decay.
    dm = DensityMatrix(rho=np.array([[0, 0], [0, 1]], dtype=complex))
    dm.evolve_lindblad(H0, cols, time=t)
    p1 = float(np.real(dm.rho[1, 1]))
    T1 = -t / np.log(p1)

    # T2 probe: |+> coherence decay.
    dm = DensityMatrix(state_vector=np.array([1, 1], dtype=complex) / np.sqrt(2))
    dm.evolve_lindblad(H0, cols, time=t)
    coh = float(2 * abs(dm.rho[0, 1]))
    T2 = -t / np.log(coh)

    T_phi = np.inf if gamma_phi == 0 else 1.0 / gamma_phi
    residual = abs(1 / T2 - 1 / (2 * T1) - (0.0 if T_phi == np.inf else 1 / T_phi))
    return {
        "T1": T1,
        "T2": T2,
        "T_phi": T_phi,
        "identity_residual": residual,
        "t2_le_2t1": T2 <= 2 * T1 + 1e-9,
    }


# --- quantum discord --------------------------------------------------------


def quantum_discord(dm: "DensityMatrix", measured_qubit: int = 1, grid: int = 6) -> float:
    """
    Quantum discord ``D_B(rho) = I(A:B) - J_B(rho)`` in bits: the part of the mutual
    information that NO projective measurement on qubit ``measured_qubit`` (side B)
    can extract classically,

        D = S(B) - S(AB) + min_M sum_k p_k S(rho_A | k),

    minimized over all Bloch-sphere projector pairs (grid-seeded Nelder-Mead).
    Zero iff the state is classical-quantum; equals the entanglement entropy for
    pure states; and can be *positive for separable states* -- quantum correlation
    without entanglement (e.g. a Werner state below the F = 1/2 threshold).
    """
    from scipy.optimize import minimize as _minimize

    n = dm.n
    rest = [q for q in range(n) if q != measured_qubit]
    s_b = dm.partial_trace([measured_qubit]).von_neumann_entropy()
    s_ab = dm.von_neumann_entropy()

    def avg_conditional_entropy(angles):
        theta, phi = angles
        nvec = (
            np.sin(theta) * np.cos(phi),
            np.sin(theta) * np.sin(phi),
            np.cos(theta),
        )
        proj = (_I + nvec[0] * _X + nvec[1] * _Y + nvec[2] * _Z) / 2
        total = 0.0
        for P in (proj, _I - proj):
            E = _embed(P, [measured_qubit], n)
            branch = E @ dm.rho @ E
            p = float(np.real(np.trace(branch)))
            if p < 1e-12:
                continue
            rho_a = DensityMatrix(rho=branch / p).partial_trace(rest)
            total += p * rho_a.von_neumann_entropy()
        return total

    best = np.inf
    for theta in np.linspace(0.01, np.pi - 0.01, grid):
        for phi in np.linspace(0.0, 2 * np.pi, grid, endpoint=False):
            res = _minimize(
                avg_conditional_entropy,
                [theta, phi],
                method="Nelder-Mead",
                options={"xatol": 1e-9, "fatol": 1e-12, "maxiter": 300},
            )
            if res.fun < best:
                best = float(res.fun)
    return max(0.0, s_b - s_ab + best)


# --- channel quality metrics ----------------------------------------------


def process_fidelity(kraus_ops, target=None) -> float:
    """
    Entanglement (process) fidelity of a Kraus channel ``{K_i}`` to a target unitary
    ``target`` (default: the identity):

        F_process = (1 / d**2) * sum_i |Tr(target-dagger K_i)|**2

    This is the fidelity between the channel's Choi state and the target's, and it
    equals 1 iff the channel *is* the target unitary. ``d`` is the Hilbert-space
    dimension inferred from the Kraus operators.
    """
    K0 = np.asarray(kraus_ops[0], dtype=complex)
    d = K0.shape[0]
    U = np.eye(d, dtype=complex) if target is None else np.asarray(target, dtype=complex)
    Ud = U.conj().T
    return float(
        sum(abs(np.trace(Ud @ np.asarray(K, dtype=complex))) ** 2 for K in kraus_ops)
        / d**2
    )


def average_gate_fidelity(kraus_ops, target=None) -> float:
    """
    Average gate fidelity of a Kraus channel to ``target`` (default identity),
    averaged uniformly over pure input states. Related to the process fidelity by
    the exact Horodecki/Nielsen identity

        F_avg = (d * F_process + 1) / (d + 1).

    Examples (single qubit, d = 2): a perfect gate gives 1; ``depolarizing(p)`` gives
    ``1 - p/2``; a stray Pauli-X error (``[X]``) gives 1/3.
    """
    K0 = np.asarray(kraus_ops[0], dtype=complex)
    d = K0.shape[0]
    fp = process_fidelity(kraus_ops, target)
    return (d * fp + 1) / (d + 1)


def choi_matrix(kraus_ops) -> np.ndarray:
    """
    Choi matrix of a Kraus channel: ``J = sum_k |K_k>> <<K_k|`` where ``|K>>`` is the
    column-stacked vectorization of ``K``. This ``d**2 x d**2`` operator is the
    Jamiolkowski image of the channel -- it is positive semidefinite iff the channel
    is completely positive, and its rank equals the minimal number of Kraus operators
    (the Kraus rank). The identity channel gives a rank-1 Choi matrix proportional to
    the maximally entangled state.
    """
    K0 = np.asarray(kraus_ops[0], dtype=complex)
    d = K0.shape[0]
    J = np.zeros((d * d, d * d), dtype=complex)
    for K in kraus_ops:
        v = np.asarray(K, dtype=complex).flatten(order="F").reshape(-1, 1)
        J += v @ v.conj().T
    return J


def is_cptp(kraus_ops, atol: float = 1e-9) -> bool:
    """
    Check that a Kraus channel is completely positive and trace preserving (CPTP):
    the Choi matrix is positive semidefinite (CP) and ``sum_k K_k-dagger K_k = I``
    (TP). Returns ``True`` iff both hold to tolerance ``atol``.
    """
    K0 = np.asarray(kraus_ops[0], dtype=complex)
    d = K0.shape[0]
    tp = sum(np.asarray(K, dtype=complex).conj().T @ np.asarray(K, dtype=complex)
             for K in kraus_ops)
    if not np.allclose(tp, np.eye(d, dtype=complex), atol=atol):
        return False
    eigs = np.linalg.eigvalsh(choi_matrix(kraus_ops)).real
    return bool(eigs.min() > -atol)


def kraus_rank(kraus_ops, atol: float = 1e-9) -> int:
    """
    Minimal number of Kraus operators needed to represent the channel -- the rank of
    its Choi matrix. A unitary channel has Kraus rank 1; noise increases it.
    """
    eigs = np.linalg.eigvalsh(choi_matrix(kraus_ops)).real
    return int(np.sum(eigs > atol))


def process_tomography(apply_fn) -> np.ndarray:
    """
    Reconstruct the Choi matrix of an unknown single-qubit channel from its action on
    a set of probe states -- quantum process tomography by linear inversion.

    ``apply_fn(rho) -> rho`` is a black box implementing the channel (any callable
    that maps a 2x2 density matrix to its output). The channel is probed on the four
    informationally-complete inputs ``|0>, |1>, |+>, |+i>``; the off-diagonal image
    ``N(|0><1|)`` is recovered by linear combination, and the Choi matrix is assembled
    as ``J = sum_{ij} |i><j| x N(|i><j|)``.

    Returns the ``4x4`` Choi matrix, identical (for a Kraus channel) to
    :func:`choi_matrix` -- so a channel can be fully characterized through its
    input/output behavior alone.
    """
    rho00 = np.array([[1, 0], [0, 0]], dtype=complex)
    rho11 = np.array([[0, 0], [0, 1]], dtype=complex)
    rho_plus = np.array([[0.5, 0.5], [0.5, 0.5]], dtype=complex)
    rho_iplus = np.array([[0.5, -0.5j], [0.5j, 0.5]], dtype=complex)

    N00 = np.asarray(apply_fn(rho00), dtype=complex)
    N11 = np.asarray(apply_fn(rho11), dtype=complex)
    Npp = np.asarray(apply_fn(rho_plus), dtype=complex)
    Nii = np.asarray(apply_fn(rho_iplus), dtype=complex)

    # |0><1| = |+><+| + i|+i><+i| - (1+i)/2 (|0><0| + |1><1|), and N is linear.
    N01 = Npp + 1j * Nii - (1 + 1j) / 2 * (N00 + N11)
    N10 = N01.conj().T
    images = {(0, 0): N00, (1, 1): N11, (0, 1): N01, (1, 0): N10}

    J = np.zeros((4, 4), dtype=complex)
    for (i, j), Nij in images.items():
        E = np.zeros((2, 2), dtype=complex)
        E[i, j] = 1
        J += np.kron(E, Nij)
    return J


def stinespring_isometry(kraus_ops) -> np.ndarray:
    """
    Stinespring dilation of a Kraus channel: the isometry ``V`` (shape
    ``(d * m, d)``, ``m`` = environment dimension padded to the Kraus count) with

        V |psi> = sum_k (K_k |psi>) x |k>_env,

    so that the channel is ``N(rho) = Tr_env(V rho V-dagger)``. Stinespring's theorem:
    every physical channel is a unitary interaction with an environment that is then
    discarded. ``V-dagger V = sum_k K_k-dagger K_k = I`` exactly when the channel is
    trace preserving. See :func:`apply_channel_dilated`.
    """
    K = [np.asarray(k, dtype=complex) for k in kraus_ops]
    d = K[0].shape[0]
    m = 1
    while m < len(K):
        m *= 2
    V = np.zeros((m * d, d), dtype=complex)
    for k, Kk in enumerate(K):
        V[k * d : (k + 1) * d, :] = Kk
    return V


def apply_channel_dilated(kraus_ops, rho) -> np.ndarray:
    """
    Apply a Kraus channel the "dilated" way -- via its Stinespring isometry followed
    by tracing out the environment -- and return the output density matrix. Equals
    :meth:`DensityMatrix.apply_channel` exactly; this is the constructive proof that
    the Kraus and system-environment pictures of noise coincide.
    """
    rho = np.asarray(rho, dtype=complex)
    V = stinespring_isometry(kraus_ops)
    d = rho.shape[0]
    m = V.shape[0] // d
    big = V @ rho @ V.conj().T
    out = np.zeros((d, d), dtype=complex)
    for e in range(m):
        out += big[e * d : (e + 1) * d, e * d : (e + 1) * d]
    return out
