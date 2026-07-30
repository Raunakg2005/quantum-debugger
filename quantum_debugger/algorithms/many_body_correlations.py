"""
Correlation functions of many-body states.

The connected two-point function ``C(i,j) = <O_i O_j> - <O_i><O_j>`` is the basic
probe of order and correlations. Its exponential decay defines the **correlation
length** ``xi`` (which diverges at criticality), and its Fourier transform is the
**structure factor** ``S(k)`` measured in scattering experiments -- peaked at ``k=0``
for a ferromagnet and ``k=pi`` for an antiferromagnet. All three are computed directly
from the state vector (little-endian, qubit 0 = least significant) and verified against
exactly known states.
"""

import numpy as np

_PAULI = {
    "I": np.eye(2, dtype=complex),
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
}


def _num_qubits(state) -> int:
    return int(round(np.log2(len(state))))


def _embed(op, i, n):
    """Embed single-qubit ``op`` on qubit ``i`` (qubit 0 = LSB = last kron factor)."""
    mats = [op if q == i else np.eye(2, dtype=complex) for q in range(n)]
    out = np.array([[1.0]], dtype=complex)
    for m in reversed(mats):  # little-endian
        out = np.kron(out, m)
    return out


def expectation(state, op, i) -> float:
    """Single-site expectation ``<psi| op_i |psi>`` (op is 'X'/'Y'/'Z' or a 2x2 matrix)."""
    psi = np.asarray(state, dtype=complex)
    O = _PAULI[op] if isinstance(op, str) else np.asarray(op, dtype=complex)
    return float(np.real(np.vdot(psi, _embed(O, i, _num_qubits(psi)) @ psi)))


def connected_correlation(state, i, j, op="Z") -> float:
    """
    Connected two-point function ``<O_i O_j> - <O_i><O_j>`` for a single-site operator
    ``op``. Zero for a product state, and (for ``op='Z'``) equal to 1 on a GHZ state --
    the direct measure of correlations beyond the mean field.
    """
    psi = np.asarray(state, dtype=complex)
    n = _num_qubits(psi)
    O = _PAULI[op] if isinstance(op, str) else np.asarray(op, dtype=complex)
    OiOj = _embed(O, i, n) @ _embed(O, j, n)
    joint = np.real(np.vdot(psi, OiOj @ psi))
    return float(joint - expectation(psi, op, i) * expectation(psi, op, j))


def correlation_length(state, op="Z", ref: int = 0) -> float:
    """
    Correlation length ``xi`` from a least-squares fit of ``log|C(ref, ref+r)|`` versus
    ``r`` (``C`` the connected function). Small for weakly correlated states and larger as
    a critical point is approached. Returns ``0.0`` when correlations vanish (product
    state) or ``inf`` when they do not decay.
    """
    psi = np.asarray(state, dtype=complex)
    n = _num_qubits(psi)
    rs, logs = [], []
    for r in range(1, n - ref):
        c = abs(connected_correlation(psi, ref, ref + r, op))
        if c > 1e-12:
            rs.append(r)
            logs.append(np.log(c))
    if len(rs) < 2:
        return 0.0
    slope = np.polyfit(rs, logs, 1)[0]
    if slope >= -1e-9:
        return float("inf")
    return float(-1.0 / slope)


def structure_factor(state, k: float, op="Z", connected: bool = False) -> float:
    """
    Static structure factor ``S(k) = (1/N) sum_{i,j} e^{i k (i-j)} <O_i O_j>`` -- the
    Fourier probe of spatial order. With ``connected=False`` (default) it uses the full
    correlator and shows the Bragg peak of an ordered state: ``k=0`` for a ferromagnet,
    ``k=pi`` for an antiferromagnet. With ``connected=True`` it uses the connected
    correlator (fluctuations only). Verified against the ferro/antiferro limits.
    """
    psi = np.asarray(state, dtype=complex)
    n = _num_qubits(psi)
    O = _PAULI[op] if isinstance(op, str) else np.asarray(op, dtype=complex)
    total = 0.0
    for i in range(n):
        for j in range(n):
            if connected:
                cij = connected_correlation(psi, i, j, op)
            else:
                cij = np.real(np.vdot(psi, (_embed(O, i, n) @ _embed(O, j, n)) @ psi))
            total += np.cos(k * (i - j)) * cij
    return float(total / n)
