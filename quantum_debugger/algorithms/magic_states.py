"""
Magic states and distillation.

Transversal gates on a stabilizer code are cheap but never universal (Eastin-Knill), so
the non-Clifford resource is injected from **magic states** -- the ``T`` state
``|A> = (|0> + e^{i pi/4}|1>)/sqrt2`` and its cousins. Real magic states are noisy; magic
state *distillation* consumes many noisy copies to yield fewer, cleaner ones. The
canonical 15-to-1 (Reed-Muller / Bravyi-Kitaev) routine takes 15 copies at error ``p`` and
outputs one at ``~35 p^3`` -- *cubic* suppression, so a few rounds reach arbitrarily low
error as long as ``p`` is below the protocol's threshold ``1/sqrt(35) ~ 0.169``.

This module provides the magic states, the stabilizer overlap that quantifies their
"magic", and the analytic distillation error model, verified for cubic suppression and its
break-even threshold.
"""

import numpy as np

_T_PHASE = np.exp(1j * np.pi / 4)


def t_state() -> np.ndarray:
    """The ``T`` magic state ``|A> = (|0> + e^{i pi/4}|1>)/sqrt(2)`` (an eigenstate of the
    ``T H`` rotation), the resource that injects a logical ``T`` gate."""
    return np.array([1, _T_PHASE], dtype=complex) / np.sqrt(2)


def h_magic_state() -> np.ndarray:
    """The ``H``-type magic state ``|H> = cos(pi/8)|0> + sin(pi/8)|1>`` -- an eigenstate of
    the Hadamard, used for Hadamard-eigenbasis distillation."""
    return np.array([np.cos(np.pi / 8), np.sin(np.pi / 8)], dtype=complex)


def stabilizer_states_1q():
    """The six single-qubit stabilizer (Pauli-eigen) states -- the 'free' states of the
    stabilizer resource theory that magic states lie outside of."""
    return [
        np.array([1, 0], dtype=complex), np.array([0, 1], dtype=complex),
        np.array([1, 1], dtype=complex) / np.sqrt(2),
        np.array([1, -1], dtype=complex) / np.sqrt(2),
        np.array([1, 1j], dtype=complex) / np.sqrt(2),
        np.array([1, -1j], dtype=complex) / np.sqrt(2),
    ]


def stabilizer_fidelity(state) -> float:
    """
    Maximum overlap ``max_s |<s|psi>|^2`` of a single-qubit ``state`` with any stabilizer
    state -- a magic monotone proxy: 1 for a stabilizer state, ``cos^2(pi/8) ~ 0.854`` for
    the ``T`` state (its distance from the stabilizer octahedron).
    """
    psi = np.asarray(state, dtype=complex); psi = psi / np.linalg.norm(psi)
    return float(max(abs(np.vdot(s / np.linalg.norm(s), psi)) ** 2 for s in stabilizer_states_1q()))


def distillation_15to1_error(p: float) -> float:
    """
    Leading-order output error of the 15-to-1 magic-state distillation routine,
    ``p_out = 35 p^3``. Cubic in the input error ``p`` -- the source of the protocol's
    power.
    """
    return 35.0 * p ** 3


def distillation_threshold() -> float:
    """Break-even input error of 15-to-1 distillation, ``p_th = 1/sqrt(35) ~ 0.169``: below
    it ``p_out < p`` and iterating drives the error to zero."""
    return float(1.0 / np.sqrt(35.0))


def distillation_rounds_to_target(p: float, target: float) -> int:
    """
    Number of 15-to-1 distillation rounds needed to reach output error ``<= target`` from
    input error ``p`` (each round applies ``p -> 35 p^3``). Returns ``-1`` if ``p`` is above
    the threshold (distillation diverges).
    """
    if p >= distillation_threshold():
        return -1
    rounds = 0
    while p > target and rounds < 100:
        p = distillation_15to1_error(p)
        rounds += 1
    return rounds
