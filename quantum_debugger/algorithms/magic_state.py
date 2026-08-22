"""
Magic states & T-gate injection (gate teleportation)

No distance-3 CSS code has a transversal T gate -- the Clifford group alone is not
universal. Fault-tolerant architectures close the gap with **magic states**: the
non-Clifford T gate is enacted on data using only Clifford operations (CNOT, S,
measurement) plus one copy of the pre-prepared magic state

    |A> = T|+> = (|0> + e^{i pi/4} |1>) / sqrt(2),

consumed in the process. The injection circuit (gate teleportation):

  1. data ``|psi> = a|0> + b|1>`` on qubit 0, magic ``|A>`` on qubit 1;
  2. CNOT (control data, target magic);
  3. measure the magic qubit -- each outcome occurs with probability exactly 1/2,
     revealing nothing about ``|psi>``;
  4. outcome 0: data is already ``T|psi>``. Outcome 1: data is ``T-dagger|psi>``;
     apply the Clifford correction ``S`` (since ``S T-dagger = T``).

Either way the data ends in ``T|psi>`` exactly. This is how fault-tolerant quantum
computers perform non-Clifford gates; distilling high-fidelity ``|A>`` states is the
dominant cost of magic-state-based universal quantum computation.
"""

import numpy as np

from ..core.quantum_state import QuantumState
from ..core.gates import GateLibrary

_T = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=complex)
_S = np.array([[1, 0], [0, 1j]], dtype=complex)


def t_magic_state() -> np.ndarray:
    """The T-magic state ``|A> = T|+> = (|0> + e^{i pi/4}|1>)/sqrt(2)``."""
    return np.array([1, np.exp(1j * np.pi / 4)], dtype=complex) / np.sqrt(2)


def inject_t_gate(alpha=1.0, beta=0.0, seed=None, force_outcome=None) -> dict:
    """
    Enact a T gate on ``alpha|0> + beta|1>`` using only Clifford operations plus one
    consumed T-magic state (gate teleportation).

    ``force_outcome`` (0 or 1) post-selects the magic-qubit measurement to exercise a
    specific branch deterministically; otherwise the outcome is drawn with ``seed``.

    Returns dict with:
      * ``fidelity``    -- of the data qubit to the ideal ``T|psi>`` (1.0, either branch)
      * ``outcome``     -- the magic-qubit measurement result
      * ``probability`` -- Born probability of that outcome (exactly 1/2 for any input)
      * ``correction``  -- ``"S"`` if the Clifford fix-up was applied, else ``None``
    """
    norm = np.sqrt(abs(alpha) ** 2 + abs(beta) ** 2)
    alpha, beta = alpha / norm, beta / norm

    # Qubit 0 = data, qubit 1 = magic (little-endian).
    state = QuantumState(2)
    state.state_vector = np.kron(
        t_magic_state(), np.array([alpha, beta], dtype=complex)
    )

    state.apply_gate(GateLibrary.CNOT, [0, 1])  # control data, target magic

    if force_outcome is None:
        rng = np.random.default_rng(seed)
        p0 = state.get_measurement_probability(1, 0)
        outcome = 0 if rng.random() < p0 else 1
    else:
        outcome = int(force_outcome)
    probability = state.get_measurement_probability(1, outcome)
    state._collapse_state(1, outcome)

    correction = None
    if outcome == 1:
        state.apply_gate(_S, [0])  # S T-dagger = T
        correction = "S"

    # Extract the data qubit (magic qubit is now a definite basis state).
    sv = state.state_vector
    data = np.array([sv[0 + 2 * outcome], sv[1 + 2 * outcome]], dtype=complex)
    data = data / np.linalg.norm(data)

    ideal = _T @ np.array([alpha, beta])
    return {
        "fidelity": float(abs(np.vdot(ideal, data)) ** 2),
        "outcome": outcome,
        "probability": float(probability),
        "correction": correction,
    }
