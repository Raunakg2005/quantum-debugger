"""
Oracle-based quantum algorithms: Bernstein-Vazirani and Deutsch-Jozsa.

Both use phase kickback from an ancilla prepared in |->: a single oracle query
reveals a global property of a hidden Boolean function that would take many
classical queries.
"""

from typing import Callable, List, Union

import numpy as np

from ..core.circuit import QuantumCircuit


def bernstein_vazirani_circuit(secret: Union[str, List[int]]) -> QuantumCircuit:
    """
    Build the Bernstein-Vazirani circuit for a hidden string ``secret``.

    The oracle computes f(x) = secret . x (mod 2). One query recovers ``secret``.
    ``secret`` is given least-significant-bit first (bit i -> qubit i).
    """
    bits = [int(b) for b in secret]
    n = len(bits)
    circuit = QuantumCircuit(n + 1)  # n query qubits + 1 ancilla
    ancilla = n

    # Ancilla in |->.
    circuit.x(ancilla)
    circuit.h(ancilla)
    # Query register in superposition.
    for q in range(n):
        circuit.h(q)

    # Oracle: CNOT(query_i, ancilla) for each secret bit set.
    for q in range(n):
        if bits[q]:
            circuit.cnot(q, ancilla)

    for q in range(n):
        circuit.h(q)
    return circuit


def bernstein_vazirani(secret: Union[str, List[int]]) -> List[int]:
    """Run Bernstein-Vazirani and return the recovered secret string (LSB first)."""
    bits = [int(b) for b in secret]
    n = len(bits)
    circuit = bernstein_vazirani_circuit(secret)
    probs = circuit.get_statevector().get_probabilities()
    outcome = int(np.argmax(probs))
    return [(outcome >> q) & 1 for q in range(n)]


def deutsch_jozsa_circuit(
    oracle: Callable[[QuantumCircuit, List[int], int], None], n: int
) -> QuantumCircuit:
    """
    Build a Deutsch-Jozsa circuit for an ``n``-bit function.

    ``oracle(circuit, query_qubits, ancilla)`` must append the phase oracle for a
    Boolean function that is promised to be either constant or balanced.
    """
    circuit = QuantumCircuit(n + 1)
    ancilla = n

    circuit.x(ancilla)
    circuit.h(ancilla)
    for q in range(n):
        circuit.h(q)

    oracle(circuit, list(range(n)), ancilla)

    for q in range(n):
        circuit.h(q)
    return circuit


def deutsch_jozsa(
    oracle: Callable[[QuantumCircuit, List[int], int], None], n: int
) -> str:
    """
    Run Deutsch-Jozsa and classify the function.

    Returns:
        'constant' if the query register measures all-zeros, else 'balanced'.
    """
    circuit = deutsch_jozsa_circuit(oracle, n)
    probs = circuit.get_statevector().get_probabilities()
    # Probability the query register (low n bits) is all zeros, over the ancilla.
    n_states = 2**n
    query_zero_prob = sum(
        probs[index] for index in range(len(probs)) if (index % n_states) == 0
    )
    return "constant" if query_zero_prob > 0.5 else "balanced"


def constant_oracle(bit: int = 0) -> Callable:
    """A constant oracle f(x) = bit (does nothing, or flips the ancilla)."""

    def oracle(circuit, query, ancilla):
        if bit:
            circuit.x(ancilla)

    return oracle


def balanced_oracle(n: int) -> Callable:
    """A balanced oracle f(x) = x_0 XOR x_1 XOR ... (CNOT each query -> ancilla)."""

    def oracle(circuit, query, ancilla):
        for q in query:
            circuit.cnot(q, ancilla)

    return oracle
