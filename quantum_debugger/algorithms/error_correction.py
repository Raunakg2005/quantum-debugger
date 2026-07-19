"""
Quantum Error Correction

Genuine, gate-based stabilizer error-correcting codes on the state-vector
simulator. A logical qubit is encoded across several physical qubits; a single
Pauli error is deliberately injected; the code's stabilizer generators are
measured with ancillas to extract a syndrome; and the matching recovery Pauli is
applied. Fidelity to the original logical state returns to 1.0.

Codes:
  * 3-qubit bit-flip code  -- corrects any single X error
  * 3-qubit phase-flip code -- corrects any single Z error
  * 9-qubit Shor code       -- corrects an arbitrary single-qubit error (X/Y/Z)
"""

import numpy as np

from ..core.quantum_state import QuantumState
from ..core.gates import GateLibrary

_H = GateLibrary.H
_X = GateLibrary.X
_Z = GateLibrary.Z
_CNOT = GateLibrary.CNOT
_CZ = GateLibrary.CZ


def _measure_stabilizer(state: QuantumState, ancilla: int, paulis: dict) -> int:
    """
    Measure a Pauli-string stabilizer using one ancilla.

    Prepares the ancilla in |+>, applies controlled-Pauli from the ancilla onto
    each data qubit in ``paulis`` ({qubit: 'X'|'Z'}), rotates back and measures.
    Returns 0 for eigenvalue +1, 1 for eigenvalue -1.
    """
    state.apply_gate(_H, [ancilla])
    for qubit, pauli in paulis.items():
        if pauli == "Z":
            state.apply_gate(_CZ, [ancilla, qubit])
        elif pauli == "X":
            state.apply_gate(_CNOT, [ancilla, qubit])
        else:
            raise ValueError(f"unsupported Pauli {pauli!r}")
    state.apply_gate(_H, [ancilla])
    outcome = state.measure(ancilla)
    # Reset the ancilla to |0> so it can be reused for the next stabilizer.
    if outcome == 1:
        state.apply_gate(_X, [ancilla])
    return outcome


def _reduced_density_matrix(sv, qubit):
    """2x2 reduced density matrix of ``qubit`` by tracing out all other qubits."""
    rho = np.zeros((2, 2), dtype=complex)
    for base in range(len(sv)):
        if (base >> qubit) & 1:
            continue  # visit each environment once via the qubit=0 index
        a0 = sv[base]
        a1 = sv[base | (1 << qubit)]
        rho[0, 0] += a0 * np.conj(a0)
        rho[0, 1] += a0 * np.conj(a1)
        rho[1, 0] += a1 * np.conj(a0)
        rho[1, 1] += a1 * np.conj(a1)
    return rho


def _logical_fidelity(state: QuantumState, encode_gates, alpha, beta, data_qubit=0):
    """Undo the encoding and read the logical qubit's true fidelity to psi."""
    for gate, qubits in reversed(encode_gates):
        state.apply_gate(gate, qubits)
    psi = np.array([alpha, beta], dtype=complex)
    psi = psi / np.linalg.norm(psi)
    rho = _reduced_density_matrix(state.state_vector, data_qubit)
    # Fidelity <psi|rho|psi> (includes off-diagonal coherence, not just populations).
    return float(np.real(np.conj(psi) @ rho @ psi))


def _prep_logical(state, alpha, beta):
    """Put alpha|0>+beta|1> on qubit 0 (state starts in |0...0>)."""
    psi = np.array([alpha, beta], dtype=complex)
    psi = psi / np.linalg.norm(psi)
    # Rotate |0> -> psi with a single-qubit unitary [[a, -b*],[b, a*]].
    a, b = psi[0], psi[1]
    U = np.array([[a, -np.conj(b)], [b, np.conj(a)]], dtype=complex)
    state.apply_gate(U, [0])
    return psi


def bit_flip_code(alpha=1.0, beta=0.0, error_qubit=0, seed=0) -> dict:
    """
    3-qubit bit-flip code. Encodes one logical qubit into qubits 0,1,2, injects an
    X error on ``error_qubit`` (None for no error), measures the two Z-stabilizers
    with ancillas 3,4, and corrects.

    Returns dict with 'syndrome', 'error_detected', 'corrected_qubit', 'fidelity'.
    """
    np.random.seed(seed)
    state = QuantumState(5)  # 3 data + 2 ancilla
    psi = _prep_logical(state, alpha, beta)

    encode = [(_CNOT, [0, 1]), (_CNOT, [0, 2])]
    for gate, qubits in encode:
        state.apply_gate(gate, qubits)

    if error_qubit is not None:
        state.apply_gate(_X, [error_qubit])

    s1 = _measure_stabilizer(state, 3, {0: "Z", 1: "Z"})
    s2 = _measure_stabilizer(state, 4, {1: "Z", 2: "Z"})

    # Syndrome -> flipped qubit (bit-flip code lookup).
    correction = {(0, 0): None, (1, 0): 0, (1, 1): 1, (0, 1): 2}[(s1, s2)]
    if correction is not None:
        state.apply_gate(_X, [correction])

    fidelity = _logical_fidelity(state, encode, psi[0], psi[1])
    return {
        "syndrome": (s1, s2),
        "error_detected": (s1, s2) != (0, 0),
        "corrected_qubit": correction,
        "fidelity": fidelity,
    }


def phase_flip_code(alpha=1.0, beta=0.0, error_qubit=0, seed=0) -> dict:
    """
    3-qubit phase-flip code. Same structure as the bit-flip code but in the
    Hadamard basis, so it corrects a single Z error. X-stabilizers are measured.
    """
    np.random.seed(seed)
    state = QuantumState(5)
    psi = _prep_logical(state, alpha, beta)

    encode = [
        (_CNOT, [0, 1]),
        (_CNOT, [0, 2]),
        (_H, [0]),
        (_H, [1]),
        (_H, [2]),
    ]
    for gate, qubits in encode:
        state.apply_gate(gate, qubits)

    if error_qubit is not None:
        state.apply_gate(_Z, [error_qubit])

    s1 = _measure_stabilizer(state, 3, {0: "X", 1: "X"})
    s2 = _measure_stabilizer(state, 4, {1: "X", 2: "X"})

    correction = {(0, 0): None, (1, 0): 0, (1, 1): 1, (0, 1): 2}[(s1, s2)]
    if correction is not None:
        state.apply_gate(_Z, [correction])

    fidelity = _logical_fidelity(state, encode, psi[0], psi[1])
    return {
        "syndrome": (s1, s2),
        "error_detected": (s1, s2) != (0, 0),
        "corrected_qubit": correction,
        "fidelity": fidelity,
    }


def shor_code(alpha=1.0, beta=0.0, error_qubit=0, error_type="X", seed=0) -> dict:
    """
    9-qubit Shor code. Concatenates the phase-flip code (outer, 3 blocks) with the
    bit-flip code (inner, 3 qubits each) to correct an arbitrary single-qubit
    error. Injects ``error_type`` in {'X','Y','Z', None} on ``error_qubit``,
    extracts all 8 stabilizer syndromes with an ancilla, and corrects.

    Returns dict with 'z_syndromes', 'x_syndromes', 'fidelity'.
    """
    np.random.seed(seed)
    state = QuantumState(10)  # 9 data + 1 reusable ancilla
    psi = _prep_logical(state, alpha, beta)

    blocks = [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
    encode = [
        (_CNOT, [0, 3]),
        (_CNOT, [0, 6]),
        (_H, [0]),
        (_H, [3]),
        (_H, [6]),
        (_CNOT, [0, 1]),
        (_CNOT, [0, 2]),
        (_CNOT, [3, 4]),
        (_CNOT, [3, 5]),
        (_CNOT, [6, 7]),
        (_CNOT, [6, 8]),
    ]
    for gate, qubits in encode:
        state.apply_gate(gate, qubits)

    if error_type is not None:
        gate = {"X": _X, "Y": GateLibrary.Y, "Z": _Z}[error_type]
        state.apply_gate(gate, [error_qubit])

    # --- Bit-flip correction inside each block (Z-stabilizers). ---
    z_syndromes = []
    for a, b, c in blocks:
        s1 = _measure_stabilizer(state, 9, {a: "Z", b: "Z"})
        s2 = _measure_stabilizer(state, 9, {b: "Z", c: "Z"})
        flip = {(0, 0): None, (1, 0): a, (1, 1): b, (0, 1): c}[(s1, s2)]
        if flip is not None:
            state.apply_gate(_X, [flip])
        z_syndromes.append((s1, s2))

    # --- Phase-flip correction across blocks (X-stabilizers). ---
    x1 = _measure_stabilizer(state, 9, {0: "X", 1: "X", 2: "X", 3: "X", 4: "X", 5: "X"})
    x2 = _measure_stabilizer(state, 9, {3: "X", 4: "X", 5: "X", 6: "X", 7: "X", 8: "X"})
    phase_block = {(0, 0): None, (1, 0): 0, (1, 1): 1, (0, 1): 2}[(x1, x2)]
    if phase_block is not None:
        # Apply Z to one representative qubit of the affected block.
        state.apply_gate(_Z, [blocks[phase_block][0]])

    fidelity = _logical_fidelity(state, encode, psi[0], psi[1])
    return {
        "z_syndromes": z_syndromes,
        "x_syndromes": (x1, x2),
        "fidelity": fidelity,
    }
