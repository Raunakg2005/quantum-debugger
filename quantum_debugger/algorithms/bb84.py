"""
BB84 Quantum Key Distribution

The first quantum cryptography protocol (Bennett & Brassard, 1984). Alice encodes
random bits in randomly chosen bases (Z or X); Bob measures in his own random
bases. Where their bases agree, their bits agree -- a shared secret key. An
eavesdropper who measures in the wrong basis disturbs the state, injecting a
detectable ~25% error rate into the sifted key.

Every qubit is genuinely prepared and measured on the state-vector simulator, so
the security guarantee emerges from real measurement back-action, not a model.
"""

import numpy as np

from ..core.quantum_state import QuantumState
from ..core.gates import GateLibrary

_H = GateLibrary.H
_X = GateLibrary.X


def _prepare(bit: int, basis: int) -> QuantumState:
    """Prepare a qubit: bit in {0,1}, basis 0=Z (|0>/|1>), 1=X (|+>/|->)."""
    state = QuantumState(1)
    if bit:
        state.apply_gate(_X, [0])
    if basis:  # X basis
        state.apply_gate(_H, [0])
    return state


def _measure(state: QuantumState, basis: int) -> int:
    """Measure a qubit in the given basis (0=Z, 1=X)."""
    if basis:  # rotate X basis into Z before measuring
        state.apply_gate(_H, [0])
    return state.measure(0)


def bb84(n_bits: int = 64, eavesdropper: bool = False, seed: int = 0) -> dict:
    """
    Run the BB84 protocol over ``n_bits`` qubits.

    Args:
        n_bits: number of qubits Alice sends
        eavesdropper: if True, Eve does an intercept-resend attack in a random basis
        seed: RNG seed

    Returns:
        dict with 'sifted_length', 'qber' (error rate on the sifted key),
        'keys_match', 'alice_key', 'bob_key', and 'secure' (qber below threshold).
    """
    rng = np.random.default_rng(seed)
    alice_bits = rng.integers(2, size=n_bits)
    alice_bases = rng.integers(2, size=n_bits)
    bob_bases = rng.integers(2, size=n_bits)
    eve_bases = rng.integers(2, size=n_bits)

    bob_results = np.zeros(n_bits, dtype=int)
    for i in range(n_bits):
        state = _prepare(int(alice_bits[i]), int(alice_bases[i]))
        if eavesdropper:
            # Eve intercepts, measures in her basis, and resends what she got.
            eve_bit = _measure(state, int(eve_bases[i]))
            state = _prepare(eve_bit, int(eve_bases[i]))
        bob_results[i] = _measure(state, int(bob_bases[i]))

    # Sifting: keep positions where Alice and Bob used the same basis.
    keep = alice_bases == bob_bases
    alice_key = alice_bits[keep]
    bob_key = bob_results[keep]

    sifted = int(keep.sum())
    errors = int(np.sum(alice_key != bob_key))
    qber = errors / sifted if sifted else 0.0

    return {
        "sifted_length": sifted,
        "qber": qber,
        "keys_match": bool(errors == 0),
        "alice_key": alice_key.tolist(),
        "bob_key": bob_key.tolist(),
        "secure": qber < 0.11,  # standard BB84 abort threshold ~11%
    }
