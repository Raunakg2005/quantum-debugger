"""
Repetition-Code Logical Error Rate

Monte-Carlo demonstration of the central promise of quantum error correction:
below a noise threshold, encoding suppresses errors. A logical bit is encoded in
the 3-qubit repetition code, each physical qubit is flipped independently with
probability ``p``, the syndrome is measured and corrected, and we check whether the
logical bit survived. The logical failure rate follows the analytic
``3 p^2 (1 - p) + p^3`` (the code fails only when two or more qubits flip), which is
below the physical rate ``p`` for all ``p < 1/2``.
"""

import numpy as np

from ..core.quantum_state import QuantumState
from ..core.gates import GateLibrary

_X = GateLibrary.X
_CNOT = GateLibrary.CNOT


def _decode_majority(bits):
    """Majority vote of three measured bits."""
    return 1 if sum(bits) >= 2 else 0


def repetition_code_error_rate(p: float, trials: int = 4000, seed: int = 0) -> dict:
    """
    Estimate the logical error rate of the 3-qubit bit-flip repetition code under an
    independent per-qubit bit-flip channel of strength ``p``.

    Each trial: encode a random logical bit, apply stochastic X errors, measure the
    three qubits, and majority-decode. Genuinely simulated (gates + measurement).

    Returns dict with 'logical_error_rate', 'analytic_rate' (3p^2(1-p)+p^3),
    'physical_rate' (p), and 'below_physical'.
    """
    rng = np.random.default_rng(seed)
    failures = 0
    for _ in range(trials):
        logical = int(rng.integers(2))
        state = QuantumState(3)
        if logical:
            state.apply_gate(_X, [0])
        # Encode: |b> -> |bbb>.
        state.apply_gate(_CNOT, [0, 1])
        state.apply_gate(_CNOT, [0, 2])

        # Independent bit-flip noise on each physical qubit.
        for q in range(3):
            if rng.random() < p:
                state.apply_gate(_X, [q])

        bits = [state.measure(q) for q in range(3)]
        if _decode_majority(bits) != logical:
            failures += 1

    logical_rate = failures / trials
    analytic = 3 * p**2 * (1 - p) + p**3
    return {
        "logical_error_rate": logical_rate,
        "analytic_rate": analytic,
        "physical_rate": p,
        "below_physical": logical_rate < p,
    }
