"""
Hamiltonian Simulation via Trotter-Suzuki Product Formulas

Simulate time evolution ``exp(-i H t)|psi>`` for a Hamiltonian given as a sum of
weighted Pauli strings, using genuine 1- and 2-qubit gates. Each term
``exp(-i theta P)`` is realized with the standard basis-change + CNOT-ladder + RZ
circuit; the full evolution is the Trotter product of the per-term evolutions.

A Hamiltonian is a list of ``(coefficient, pauli_string)`` pairs, where
``pauli_string[q]`` in {'I','X','Y','Z'} acts on qubit ``q`` (qubit 0 = LSB, the
same little-endian convention as the rest of the library). Example (transverse
field Ising on 3 qubits):

    H = [(1.0, "ZZI"), (1.0, "IZZ"), (0.5, "XII"), (0.5, "IXI"), (0.5, "IIX")]
"""

import numpy as np
from scipy.linalg import expm

from ..core.quantum_state import QuantumState
from ..core.gates import GateLibrary

_H = GateLibrary.H
_CNOT = GateLibrary.CNOT
_RX = GateLibrary.RX
_RZ = GateLibrary.RZ

_PAULI = {
    "I": np.eye(2, dtype=complex),
    "X": GateLibrary.X,
    "Y": GateLibrary.Y,
    "Z": GateLibrary.Z,
}


def pauli_term_matrix(pauli_string: str) -> np.ndarray:
    """Full 2^n x 2^n operator for a Pauli string (qubit 0 = LSB)."""
    # Little-endian: qubit 0 is the least significant, i.e. the last kron factor.
    mat = np.array([[1.0]], dtype=complex)
    for pauli in reversed(pauli_string):
        mat = np.kron(mat, _PAULI[pauli])
    return mat


def hamiltonian_matrix(terms, n_qubits: int) -> np.ndarray:
    """Assemble the dense Hamiltonian matrix from weighted Pauli strings."""
    dim = 2**n_qubits
    H = np.zeros((dim, dim), dtype=complex)
    for coeff, pauli in terms:
        assert len(pauli) == n_qubits, "pauli string length must equal n_qubits"
        H += coeff * pauli_term_matrix(pauli)
    return H


def _append_pauli_exp(gates, pauli_string, angle):
    """Append gates realizing exp(-i * angle * P) for a single Pauli string P."""
    active = [q for q, p in enumerate(pauli_string) if p != "I"]
    if not active:
        return  # identity term -> global phase, unobservable

    # Basis-change each active qubit into the Z basis.
    for q in active:
        if pauli_string[q] == "X":
            gates.append((_H, [q]))
        elif pauli_string[q] == "Y":
            gates.append((_RX(np.pi / 2), [q]))

    # CNOT ladder to accumulate parity onto the last active qubit.
    for i in range(len(active) - 1):
        gates.append((_CNOT, [active[i], active[i + 1]]))

    # exp(-i angle Z) on the parity qubit.
    gates.append((_RZ(2 * angle), [active[-1]]))

    # Uncompute the ladder and basis changes.
    for i in reversed(range(len(active) - 1)):
        gates.append((_CNOT, [active[i], active[i + 1]]))
    for q in active:
        if pauli_string[q] == "X":
            gates.append((_H, [q]))
        elif pauli_string[q] == "Y":
            gates.append((_RX(-np.pi / 2), [q]))


def trotter_circuit(terms, time, steps=1, order=1):
    """
    Build the gate list for a Trotterized evolution ``exp(-i H t)``.

    Args:
        terms: list of (coeff, pauli_string)
        time: total evolution time
        steps: number of Trotter steps (higher = smaller error)
        order: 1 (first-order) or 2 (symmetric second-order Suzuki)

    Returns:
        list of (gate_matrix, qubits) to apply in order.
    """
    dt = time / steps
    gates = []
    if order == 1:
        for _ in range(steps):
            for coeff, pauli in terms:
                _append_pauli_exp(gates, pauli, coeff * dt)
    elif order == 2:
        # Symmetric split: half sweep forward, half sweep reversed.
        for _ in range(steps):
            for coeff, pauli in terms:
                _append_pauli_exp(gates, pauli, coeff * dt / 2)
            for coeff, pauli in reversed(terms):
                _append_pauli_exp(gates, pauli, coeff * dt / 2)
    else:
        raise ValueError("order must be 1 or 2")
    return gates


def trotter_evolve(terms, time, initial_state=None, steps=10, order=2):
    """
    Evolve a state under ``exp(-i H t)`` with a Trotter product formula and report
    the fidelity to the exact evolution.

    Args:
        terms: list of (coeff, pauli_string)
        time: total evolution time
        initial_state: optional length-2^n state vector (default |0...0>)
        steps: Trotter steps
        order: 1 or 2

    Returns:
        dict with 'state' (final state vector), 'exact' (exact evolved state),
        and 'fidelity' = |<exact|trotter>|^2.
    """
    n = len(terms[0][1])
    dim = 2**n
    if initial_state is None:
        psi0 = np.zeros(dim, dtype=complex)
        psi0[0] = 1.0
    else:
        psi0 = np.asarray(initial_state, dtype=complex)
        psi0 = psi0 / np.linalg.norm(psi0)

    state = QuantumState(n, state_vector=psi0.copy())
    for gate, qubits in trotter_circuit(terms, time, steps, order):
        state.apply_gate(gate, qubits)
    trotter_state = state.state_vector

    H = hamiltonian_matrix(terms, n)
    exact_state = expm(-1j * H * time) @ psi0

    fidelity = float(np.abs(np.vdot(exact_state, trotter_state)) ** 2)
    return {"state": trotter_state, "exact": exact_state, "fidelity": fidelity}
