"""
Quantum Arithmetic -- Draper QFT Adder

Add numbers directly in the Fourier basis (Draper, 2000). To compute ``a + b`` one
QFTs the ``a`` register, applies phase rotations proportional to ``b``, then inverse
QFTs -- no carry ancillas required. Two variants:

  * ``qft_add(a, b, n)``       -- add a classical constant ``b`` into ``|a>``
  * ``quantum_adder(a, b, n)`` -- add two quantum registers, ``|a>|b> -> |a+b>|b>``

Both compute ``(a + b) mod 2**n`` and are exact for every input pair.
"""

import numpy as np

from ..core.quantum_state import QuantumState
from ..core.circuit import QuantumCircuit
from ..core.gates import GateLibrary
from .qft import apply_qft, apply_inverse_qft


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
