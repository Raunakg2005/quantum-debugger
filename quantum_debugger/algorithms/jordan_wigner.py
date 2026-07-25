"""
The Jordan-Wigner transformation (fermions -> qubits)

Quantum chemistry and the Fermi-Hubbard model are written with fermionic creation
and annihilation operators obeying the anticommutation relations

    {a_i, a_j} = 0,      {a_i, a_j-dagger} = delta_ij.

To simulate them on qubits, the Jordan-Wigner map represents mode ``j`` as

    a_j = (prod_{k<j} Z_k) sigma_j^-,      sigma^- = |0><1|,

where the leading string of ``Z`` operators (the "Jordan-Wigner string") enforces
the fermionic sign under exchange. This module builds these operators, verifies the
anticommutation algebra exactly, and assembles number and hopping operators --
the ingredients for a fermionic Hamiltonian on a quantum computer.

Occupation convention: qubit ``|1>`` = mode occupied, ``|0>`` = empty
(little-endian: mode 0 is the least significant bit).
"""

import numpy as np

_Z = np.array([[1, 0], [0, -1]], dtype=complex)
_SM = np.array([[0, 1], [0, 0]], dtype=complex)  # sigma^- : |1> -> |0>
_I = np.eye(2, dtype=complex)


def _op_on(mats):
    out = np.array([[1]], dtype=complex)
    for m in reversed(mats):  # little-endian: mode 0 = least significant
        out = np.kron(out, m)
    return out


def jw_annihilation(mode: int, n_modes: int) -> np.ndarray:
    """
    Jordan-Wigner annihilation operator ``a_mode`` on ``n_modes`` fermionic modes,
    as a ``2**n_modes x 2**n_modes`` matrix: a ``Z`` string on all lower modes times
    ``sigma^-`` on the target.
    """
    mats = [_Z if k < mode else _SM if k == mode else _I for k in range(n_modes)]
    return _op_on(mats)


def jw_creation(mode: int, n_modes: int) -> np.ndarray:
    """Jordan-Wigner creation operator ``a_mode-dagger``."""
    return jw_annihilation(mode, n_modes).conj().T


def jw_number(mode: int, n_modes: int) -> np.ndarray:
    """Number operator ``n_mode = a_mode-dagger a_mode`` (eigenvalues 0 and 1)."""
    a = jw_annihilation(mode, n_modes)
    return a.conj().T @ a


def jw_total_number(n_modes: int) -> np.ndarray:
    """Total particle-number operator ``sum_j n_j`` -- counts occupied modes."""
    dim = 2**n_modes
    N = np.zeros((dim, dim), dtype=complex)
    for j in range(n_modes):
        N += jw_number(j, n_modes)
    return N


def hopping_hamiltonian(n_modes: int, t: float = 1.0, periodic: bool = False) -> np.ndarray:
    """
    Tight-binding hopping Hamiltonian ``H = -t sum_j (a_j-dagger a_{j+1} + h.c.)`` on a
    chain of ``n_modes`` modes (a ring if ``periodic``). Its single-particle
    eigenvalues are the exact tight-binding band ``-2t cos(k)``.
    """
    dim = 2**n_modes
    H = np.zeros((dim, dim), dtype=complex)
    bonds = n_modes if periodic else n_modes - 1
    for j in range(bonds):
        k = (j + 1) % n_modes
        aj_dag = jw_creation(j, n_modes)
        ak = jw_annihilation(k, n_modes)
        term = aj_dag @ ak
        H += -t * (term + term.conj().T)
    return H


def anticommutation_error(n_modes: int) -> float:
    """
    Maximum violation of ``{a_i, a_j} = 0`` and ``{a_i, a_j-dagger} = delta_ij I``
    over all pairs -- a direct check that the Jordan-Wigner operators are genuinely
    fermionic. Returns ~0 (machine precision).
    """
    dim = 2**n_modes
    a = [jw_annihilation(j, n_modes) for j in range(n_modes)]
    ad = [x.conj().T for x in a]
    err = 0.0
    for i in range(n_modes):
        for j in range(n_modes):
            err = max(err, float(np.max(np.abs(a[i] @ a[j] + a[j] @ a[i]))))
            target = np.eye(dim, dtype=complex) if i == j else 0
            err = max(err, float(np.max(np.abs(a[i] @ ad[j] + ad[j] @ a[i] - target))))
    return err
