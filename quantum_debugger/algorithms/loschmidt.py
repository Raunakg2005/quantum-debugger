"""
Loschmidt echo & dynamical quantum phase transitions

Prepare a state ``|psi_0>`` (often the ground state of one Hamiltonian), then quench
-- evolve it under a *different* Hamiltonian ``H``. The Loschmidt echo

    L(t) = |<psi_0| e^{-i H t} |psi_0>|^2

measures how much of the initial state survives. Its rate function
``lambda(t) = -ln L(t) / N`` (``N`` qubits) is the dynamical analogue of a free
energy, and its non-analytic cusps in time are **dynamical quantum phase
transitions** (DQPTs) -- the echo dips to zero when the evolved state becomes
orthogonal to the start.

Solvable checks reproduced here: an eigenstate never dephases (``L = 1``), and a
two-level superposition ``cos(theta)|0> + sin(theta)|1>`` under a gap ``Delta`` gives

    L(t) = 1 - sin^2(2 theta) sin^2(Delta t / 2),

periodically returning to 1 and dipping to ``cos^2(2 theta)``.
"""

import numpy as np
from scipy.linalg import expm


def loschmidt_echo(hamiltonian, initial_state, times) -> np.ndarray:
    """
    Loschmidt echo ``L(t) = |<psi_0| e^{-i H t} |psi_0>|^2`` for each ``t`` in
    ``times``. Returns an array of echoes in ``[0, 1]``.
    """
    H = np.asarray(hamiltonian, dtype=complex)
    psi0 = np.asarray(initial_state, dtype=complex)
    psi0 = psi0 / np.linalg.norm(psi0)
    return np.array([abs(np.vdot(psi0, expm(-1j * H * t) @ psi0)) ** 2 for t in times])


def rate_function(hamiltonian, initial_state, times, n_qubits=None) -> np.ndarray:
    """
    Dynamical free energy ``lambda(t) = -ln L(t) / N`` (``N`` = ``n_qubits``, inferred
    if omitted). Peaks/cusps mark dynamical quantum phase transitions. ``L = 0`` gives
    ``+inf``.
    """
    H = np.asarray(hamiltonian, dtype=complex)
    if n_qubits is None:
        n_qubits = int(round(np.log2(H.shape[0])))
    L = loschmidt_echo(H, initial_state, times)
    with np.errstate(divide="ignore"):
        return -np.log(L) / n_qubits


def quench_dynamics(
    hamiltonian, initial_state, t_max: float = 10.0, points: int = 200
) -> dict:
    """
    Sample the Loschmidt echo and rate function of a quench over ``[0, t_max]``.

    Returns dict with ``times``, ``echo``, ``rate_function``, ``min_echo`` (the deepest
    dip -- an approach to a DQPT), and ``revival`` (whether the echo returns near 1
    after ``t=0``, a signature of coherent, few-level dynamics).
    """
    times = np.linspace(0, t_max, points)
    echo = loschmidt_echo(hamiltonian, initial_state, times)
    rate = rate_function(hamiltonian, initial_state, times)
    revival = bool(np.any(echo[points // 10 :] > 0.99))
    return {
        "times": times,
        "echo": echo,
        "rate_function": rate,
        "min_echo": float(echo.min()),
        "revival": revival,
    }
