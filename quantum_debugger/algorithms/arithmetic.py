"""
Quantum Arithmetic

Two complementary approaches to addition, plus subtraction and comparison:

  * Fourier basis (Draper, 2000): ``qft_add`` / ``quantum_adder`` -- QFT the
    register, apply phase rotations, inverse QFT. No carry ancillas.
  * Ripple-carry (Cuccaro, 2004): ``ripple_carry_add`` -- MAJ/UMA gates propagate a
    carry, giving the exact sum (with carry-out) using only CNOT/Toffoli.

All routines are exact for every input pair.
"""

import numpy as np

from ..core.quantum_state import QuantumState
from ..core.circuit import QuantumCircuit
from ..core.gates import GateLibrary
from .qft import apply_qft, apply_inverse_qft

_CNOT = GateLibrary.CNOT
_TOFFOLI = GateLibrary.TOFFOLI


def _phase(angle):
    return np.array([[1, 0], [0, np.exp(1j * angle)]], dtype=complex)


def _controlled_phase(angle):
    m = np.eye(4, dtype=complex)
    m[3, 3] = np.exp(1j * angle)
    return m


def _apply_circuit(state, circuit):
    for g in circuit.gates:
        state.apply_gate(g.matrix, g.qubits)


def qft_add(a: int, b: int, n_bits: int) -> int:
    """
    Add a classical constant ``b`` into the register holding ``a`` using the QFT.

    Returns ``(a + b) mod 2**n_bits``.
    """
    state = QuantumState(n_bits)
    sv = np.zeros(2**n_bits, dtype=complex)
    sv[a % (2**n_bits)] = 1.0
    state.state_vector = sv

    qft = QuantumCircuit(n_bits)
    apply_qft(qft)
    _apply_circuit(state, qft)

    # Phase proportional to b on each qubit (Fourier-basis addition).
    for q in range(n_bits):
        state.apply_gate(_phase(2 * np.pi * b * (2**q) / (2**n_bits)), [q])

    iqft = QuantumCircuit(n_bits)
    apply_inverse_qft(iqft)
    _apply_circuit(state, iqft)

    return int(np.argmax(np.abs(state.state_vector) ** 2))


def qft_subtract(a: int, b: int, n_bits: int) -> int:
    """
    Subtract a classical constant ``b`` from ``a`` in the Fourier basis.

    Returns ``(a - b) mod 2**n_bits`` (adding the two's complement of ``b``).
    """
    return qft_add(a, (-b) % (2**n_bits), n_bits)


def quantum_compare(a: int, b: int, n_bits: int) -> dict:
    """
    Compare ``a`` and ``b`` (each in ``0..2**n_bits - 1``) with a QFT subtractor.

    Computes ``(a - b) mod 2**(n_bits + 1)``; the sign bit (bit ``n_bits``) is 0
    iff ``a >= b``.

    Returns dict with 'a_geq_b', 'a_lt_b', and 'difference' (the raw result).
    """
    diff = qft_subtract(a, b, n_bits + 1)
    sign = (diff >> n_bits) & 1
    return {"a_geq_b": sign == 0, "a_lt_b": sign == 1, "difference": diff}


def _maj(state, c, b, a):
    """Cuccaro MAJ gate: compute the majority (carry) into qubit a."""
    state.apply_gate(_CNOT, [a, b])
    state.apply_gate(_CNOT, [a, c])
    state.apply_gate(_TOFFOLI, [c, b, a])


def _uma(state, c, b, a):
    """Cuccaro UMA gate: un-majority and add (inverse of MAJ plus the sum bit)."""
    state.apply_gate(_TOFFOLI, [c, b, a])
    state.apply_gate(_CNOT, [a, c])
    state.apply_gate(_CNOT, [c, b])


def ripple_carry_add(a: int, b: int, n_bits: int) -> int:
    """
    Cuccaro ripple-carry adder: compute the exact sum ``a + b`` (with carry-out).

    Uses a carry ancilla and a carry-out qubit; only CNOT and Toffoli gates. The
    ``b`` register accumulates the sum while ``a`` is restored. Returns the full
    ``(n_bits + 1)``-bit integer ``a + b`` (no modular wrap).
    """
    total = 2 * n_bits + 2
    c = 0
    a_q = [1 + i for i in range(n_bits)]
    b_q = [1 + n_bits + i for i in range(n_bits)]
    z = 1 + 2 * n_bits

    state = QuantumState(total)
    index = 0
    for i in range(n_bits):
        if (a >> i) & 1:
            index |= 1 << a_q[i]
        if (b >> i) & 1:
            index |= 1 << b_q[i]
    sv = np.zeros(2**total, dtype=complex)
    sv[index] = 1.0
    state.state_vector = sv

    _maj(state, c, b_q[0], a_q[0])
    for i in range(1, n_bits):
        _maj(state, a_q[i - 1], b_q[i], a_q[i])
    state.apply_gate(_CNOT, [a_q[n_bits - 1], z])
    for i in range(n_bits - 1, 0, -1):
        _uma(state, a_q[i - 1], b_q[i], a_q[i])
    _uma(state, c, b_q[0], a_q[0])

    out = int(np.argmax(np.abs(state.state_vector) ** 2))
    result = sum(((out >> b_q[i]) & 1) << i for i in range(n_bits))
    result |= ((out >> z) & 1) << n_bits
    return result


def quantum_adder(a: int, b: int, n_bits: int) -> int:
    """
    Add two quantum registers with the Draper adder: ``|a>|b> -> |(a+b) mod 2^n>|b>``.

    Register A is qubits 0..n-1, register B is qubits n..2n-1. Returns the value of
    register A after the addition, i.e. ``(a + b) mod 2**n_bits``.
    """
    n = n_bits
    total = 2 * n
    state = QuantumState(total)
    index = (a % (2**n)) | ((b % (2**n)) << n)
    sv = np.zeros(2**total, dtype=complex)
    sv[index] = 1.0
    state.state_vector = sv

    # QFT on register A only (reversed order to match the analytic-DFT convention).
    a_qubits = list(reversed(range(n)))
    qft = QuantumCircuit(total)
    apply_qft(qft, qubits=a_qubits)
    _apply_circuit(state, qft)

    # Controlled phases: B qubit p (weight 2^p) rotates A qubit q by 2*pi*2^(p+q)/2^n.
    for q in range(n):
        for p in range(n):
            angle = 2 * np.pi * (2 ** (p + q)) / (2**n)
            state.apply_gate(_controlled_phase(angle), [n + p, q])

    iqft = QuantumCircuit(total)
    apply_inverse_qft(iqft, qubits=a_qubits)
    _apply_circuit(state, iqft)

    probs = np.abs(state.state_vector) ** 2
    index = int(np.argmax(probs))
    return index & ((1 << n) - 1)
