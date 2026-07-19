"""
Quantum communication protocols: teleportation, superdense coding, and
entanglement swapping.

Teleportation moves an unknown qubit state using a shared Bell pair and two
classical bits; superdense coding sends two classical bits using one qubit;
entanglement swapping entangles two qubits that never interacted (the basis of
quantum repeaters).
"""

import numpy as np

from ..core.quantum_state import QuantumState
from ..core.gates import GateLibrary


def _two_qubit_reduced_dm(sv, qa, qb, n):
    """Reduced 4x4 density matrix of qubits (qa, qb), tracing out the rest."""
    rho = np.zeros((4, 4), dtype=complex)
    env_qubits = [q for q in range(n) if q not in (qa, qb)]
    for env in range(2 ** len(env_qubits)):
        # Fixed environment bits; sum over the (qa, qb) subspace.
        base = 0
        for k, q in enumerate(env_qubits):
            if (env >> k) & 1:
                base |= 1 << q
        amps = np.zeros(4, dtype=complex)
        for two in range(4):
            idx = base
            if two & 1:
                idx |= 1 << qa
            if two & 2:
                idx |= 1 << qb
            amps[two] = sv[idx]
        rho += np.outer(amps, amps.conj())
    return rho


def teleport(psi) -> dict:
    """
    Teleport a single-qubit state ``psi`` from qubit 0 to qubit 2.

    Prepares a Bell pair on qubits 1 and 2, performs a Bell measurement on qubits
    0 and 1, and applies the X/Z feedforward corrections to qubit 2 based on the
    measured bits. Returns the fidelity of the teleported qubit to the original.

    Args:
        psi: a length-2 single-qubit state vector

    Returns:
        dict with 'fidelity', 'measurement' (the two measured bits), and
        'teleported_state'.
    """
    psi = np.asarray(psi, dtype=complex)
    psi = psi / np.linalg.norm(psi)

    # 3-qubit state: qubit 0 = psi, qubits 1,2 = |00>.
    init = np.kron(np.array([1.0, 0.0], dtype=complex), np.kron([1.0, 0.0], psi))
    state = QuantumState(3, state_vector=init)

    H, X, Z = GateLibrary.H, GateLibrary.X, GateLibrary.Z
    CNOT = GateLibrary.CNOT

    # Entangle qubits 1 and 2 into a Bell pair.
    state.apply_gate(H, [1])
    state.apply_gate(CNOT, [1, 2])
    # Bell measurement basis on qubits 0 and 1.
    state.apply_gate(CNOT, [0, 1])
    state.apply_gate(H, [0])

    # Measure qubits 0 and 1 (collapses the state).
    m0 = state.measure(0)
    m1 = state.measure(1)

    # Feedforward corrections on qubit 2.
    if m1 == 1:
        state.apply_gate(X, [2])
    if m0 == 1:
        state.apply_gate(Z, [2])

    # Extract qubit 2's (now pure) state and compare to psi.
    sv = state.state_vector
    probs = np.abs(sv) ** 2
    q2 = np.zeros(2, dtype=complex)
    for index in range(8):
        if probs[index] > 1e-12:
            q2[(index >> 2) & 1] += sv[index]
    if np.linalg.norm(q2) > 1e-12:
        q2 = q2 / np.linalg.norm(q2)

    fidelity = float(np.abs(np.vdot(psi, q2)) ** 2)
    return {"fidelity": fidelity, "measurement": (m0, m1), "teleported_state": q2}


def superdense_coding(bits) -> dict:
    """
    Send two classical bits ``(b0, b1)`` using a single qubit and a Bell pair.

    Alice encodes the bits into her half of a Bell pair with I/X/Z/XZ, sends it to
    Bob, who decodes both bits with a Bell measurement.

    Args:
        bits: a pair (b0, b1) of classical bits

    Returns:
        dict with 'sent', 'decoded', and 'success'.
    """
    b0, b1 = int(bits[0]), int(bits[1])
    state = QuantumState(2)  # |00>

    H, X, Z = GateLibrary.H, GateLibrary.X, GateLibrary.Z
    CNOT = GateLibrary.CNOT

    # Shared Bell pair on qubits 0 (Alice) and 1 (Bob).
    state.apply_gate(H, [0])
    state.apply_gate(CNOT, [0, 1])

    # Alice encodes 2 bits onto her qubit 0.
    if b1 == 1:
        state.apply_gate(X, [0])
    if b0 == 1:
        state.apply_gate(Z, [0])

    # Bob decodes with an inverse Bell measurement.
    state.apply_gate(CNOT, [0, 1])
    state.apply_gate(H, [0])

    outcome = state.measure(0), state.measure(1)
    decoded = (outcome[0], outcome[1])
    return {
        "sent": (b0, b1),
        "decoded": decoded,
        "success": decoded == (b0, b1),
    }


def entanglement_swap(seed: int = 0) -> dict:
    """
    Entangle two qubits that never interacted, via entanglement swapping.

    Prepares two independent Bell pairs (qubits 0-1 and 2-3), performs a Bell
    measurement on the inner qubits (1, 2), and applies X/Z feedforward on qubit 3.
    Qubits 0 and 3 -- which have no common history -- end up in the Bell state
    ``|Phi+>``. Returns the fidelity of the (0, 3) pair to ``|Phi+>``.
    """
    np.random.seed(seed)
    state = QuantumState(4)
    H, X, Z = GateLibrary.H, GateLibrary.X, GateLibrary.Z
    CNOT = GateLibrary.CNOT

    # Two independent Bell pairs.
    state.apply_gate(H, [0])
    state.apply_gate(CNOT, [0, 1])
    state.apply_gate(H, [2])
    state.apply_gate(CNOT, [2, 3])

    # Bell measurement on the inner qubits 1 and 2.
    state.apply_gate(CNOT, [1, 2])
    state.apply_gate(H, [1])
    m1 = state.measure(1)
    m2 = state.measure(2)

    # Feedforward on qubit 3 so the (0, 3) pair becomes |Phi+>.
    if m2 == 1:
        state.apply_gate(X, [3])
    if m1 == 1:
        state.apply_gate(Z, [3])

    # Fidelity of qubits (0, 3) to |Phi+> = (|00> + |11>)/sqrt(2).
    rho = _two_qubit_reduced_dm(state.state_vector, 0, 3, 4)
    phi_plus = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
    fidelity = float(np.real(np.conj(phi_plus) @ rho @ phi_plus))
    return {"fidelity": fidelity, "measurement": (m1, m2)}
