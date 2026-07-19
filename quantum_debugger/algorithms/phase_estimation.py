"""
Quantum Phase Estimation (QPE)

Estimates the phase phi of an eigenvalue e^{2*pi*i*phi} of a unitary U, given an
eigenstate. This implementation demonstrates QPE on the phase gate U = P(theta)
whose eigenstate is |1> with eigenphase phi = theta / (2*pi): t counting qubits
are put in superposition, controlled-U^(2^j) rotations imprint the phase, and an
inverse QFT reads it out.
"""

import numpy as np

from ..core.circuit import QuantumCircuit
from .qft import apply_inverse_qft


def phase_estimation_circuit(theta: float, n_counting: int) -> QuantumCircuit:
    """
    Build a QPE circuit for U = P(theta) with eigenstate |1>.

    Qubits 0..n_counting-1 are the counting register; qubit n_counting holds the
    eigenstate. Measuring the counting register gives an integer m with
    phi ~= m / 2**n_counting, i.e. theta ~= 2*pi*m / 2**n_counting.
    """
    n = n_counting + 1
    eig = n_counting
    circuit = QuantumCircuit(n)

    # Prepare the eigenstate |1> and the counting register in superposition.
    circuit.x(eig)
    for q in range(n_counting):
        circuit.h(q)

    # Controlled-U^(2^j): a controlled phase of 2^j * theta on the eigenstate.
    for j in range(n_counting):
        circuit.cp((2**j) * theta, j, eig)

    # Inverse QFT over the counting register (reversed order matches the DFT
    # convention used by this little-endian simulator).
    apply_inverse_qft(circuit, qubits=list(reversed(range(n_counting))))
    return circuit


def estimate_phase(theta: float, n_counting: int) -> dict:
    """
    Run QPE and return the estimated phase.

    Returns:
        dict with 'phase' (estimate of theta/(2*pi) in [0,1)), 'theta_estimate',
        'best_integer' m, and 'probability' of that outcome.
    """
    circuit = phase_estimation_circuit(theta, n_counting)
    probs = circuit.get_statevector().get_probabilities()

    # Marginalize the eigenstate qubit out; keep the counting-register value.
    n_counting_states = 2**n_counting
    counting_probs = np.zeros(n_counting_states)
    for index, p in enumerate(probs):
        counting_probs[index % n_counting_states] += p

    best = int(np.argmax(counting_probs))
    phase = best / n_counting_states
    return {
        "phase": phase,
        "theta_estimate": 2 * np.pi * phase,
        "best_integer": best,
        "probability": float(counting_probs[best]),
    }


def iterative_phase_estimation(theta: float, n_bits: int) -> dict:
    """
    Iterative Quantum Phase Estimation using a single ancilla qubit.

    Reads the phase phi = theta / (2*pi) one bit at a time, from least to most
    significant (Kitaev's scheme), feeding already-measured bits back as a phase
    correction. Uses only 2 qubits total (1 ancilla + 1 eigenstate) regardless of
    the requested precision, unlike standard QPE which needs n_bits counting
    qubits.

    Returns:
        dict with 'phase', 'bits' (MSB first), and 'theta_estimate'.
    """
    from ..core.circuit import QuantumCircuit

    bits = [0] * n_bits  # bits[0] is the most significant (2**-1)

    for k in range(n_bits - 1, -1, -1):  # measure LSB (k=n_bits-1) first
        power = 2**k  # bit k (value 2**-(k+1)) is isolated by applying U^(2**k)

        # Feedback from the already-measured, less-significant bits.
        feedback = 0.0
        for j in range(k + 1, n_bits):
            feedback += bits[j] * 2.0 ** (-(j - k + 1))

        circuit = QuantumCircuit(2)  # qubit 0 = ancilla, qubit 1 = eigenstate
        circuit.x(1)  # eigenstate |1>
        circuit.h(0)
        circuit.cp(power * theta, 0, 1)  # controlled-U^power kicks phase to ancilla
        if feedback:
            circuit.rz(-2 * np.pi * feedback, 0)  # feedback correction
        circuit.h(0)

        probs = circuit.get_statevector().get_probabilities()
        p1 = float(sum(probs[i] for i in range(len(probs)) if (i & 1) == 1))
        bits[k] = 1 if p1 > 0.5 else 0

    phase = sum(bits[i] * 2.0 ** (-(i + 1)) for i in range(n_bits))
    return {
        "phase": phase,
        "bits": bits,
        "theta_estimate": 2 * np.pi * phase,
    }
