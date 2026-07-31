"""
Trotter-Suzuki product formulas for Hamiltonian simulation.

To simulate ``e^{-iHt}`` for ``H = sum_k H_k`` (a sum of easy-to-exponentiate terms, e.g.
weighted Pauli strings), a **product formula** approximates the exponential of the sum by a
product of exponentials of the terms:

* **First order (Lie-Trotter)** ``S_1(t) = prod_k e^{-i H_k t}`` -- error ``O(t^2/r)`` in ``r``
  steps.
* **Second order (Strang)** ``S_2(t) = prod_k e^{-i H_k t/2} prod_{k rev} e^{-i H_k t/2}`` --
  error ``O(t^3/r^2)``.
* **Fourth order (Suzuki)** built recursively from ``S_2`` -- error ``O(t^5/r^4)``.

Each is assembled as a dense unitary and its error against the exact ``e^{-iHt}`` is measured,
verifying the advertised order of accuracy (the error's slope in a log-log step scan).
"""

import numpy as np
from scipy.linalg import expm

from .hamiltonian_simulation import pauli_term_matrix, hamiltonian_matrix


def _term_matrices(terms, n):
    return [(coeff, pauli_term_matrix(p)) for coeff, p in terms]


def exact_evolution(terms, t: float) -> np.ndarray:
    """The exact propagator ``e^{-iHt}`` for the Hamiltonian ``H = sum coeff * Pauli`` -- the
    reference every product formula is compared to."""
    n = len(terms[0][1])
    return expm(-1j * hamiltonian_matrix(terms, n) * t)


def first_order_trotter(terms, t: float, steps: int = 1) -> np.ndarray:
    """First-order (Lie-Trotter) product formula ``[prod_k e^{-i H_k t/r}]^r`` -- error
    ``O(t^2/r)``, verified against the exact evolution."""
    n = len(terms[0][1])
    mats = _term_matrices(terms, n)
    dt = t / steps
    step = np.eye(2 ** n, dtype=complex)
    for coeff, M in mats:
        step = expm(-1j * coeff * M * dt) @ step
    return np.linalg.matrix_power(step, steps)


def second_order_trotter(terms, t: float, steps: int = 1) -> np.ndarray:
    """Second-order symmetric (Strang) formula -- forward half-sweep then reversed half-sweep,
    error ``O(t^3/r^2)``."""
    n = len(terms[0][1])
    mats = _term_matrices(terms, n)
    dt = t / steps
    step = np.eye(2 ** n, dtype=complex)
    for coeff, M in mats:
        step = expm(-1j * coeff * M * dt / 2) @ step
    for coeff, M in reversed(mats):
        step = expm(-1j * coeff * M * dt / 2) @ step
    return np.linalg.matrix_power(step, steps)


def _s2(mats, n, dt):
    step = np.eye(2 ** n, dtype=complex)
    for coeff, M in mats:
        step = expm(-1j * coeff * M * dt / 2) @ step
    for coeff, M in reversed(mats):
        step = expm(-1j * coeff * M * dt / 2) @ step
    return step


def fourth_order_suzuki(terms, t: float, steps: int = 1) -> np.ndarray:
    """
    Fourth-order Suzuki formula ``S_4 = S_2(p dt)^2 S_2((1-4p) dt) S_2(p dt)^2`` with
    ``p = 1/(4 - 4^{1/3})``, built recursively from the second-order formula -- error
    ``O(t^5/r^4)``.
    """
    n = len(terms[0][1])
    mats = _term_matrices(terms, n)
    dt = t / steps
    p = 1.0 / (4 - 4 ** (1 / 3))
    a = _s2(mats, n, p * dt)
    b = _s2(mats, n, (1 - 4 * p) * dt)
    s4 = a @ a @ b @ a @ a
    return np.linalg.matrix_power(s4, steps)


def trotter_error(terms, t: float, steps: int, order: int = 1) -> float:
    """
    Spectral-norm error ``||S(t) - e^{-iHt}||`` of the order-``order`` product formula (1, 2, or
    4) with ``steps`` Trotter steps -- the quantity whose scaling with ``steps`` certifies the
    order.
    """
    U = {1: first_order_trotter, 2: second_order_trotter, 4: fourth_order_suzuki}[order](terms, t, steps)
    return float(np.linalg.norm(U - exact_evolution(terms, t), 2))


def randomized_trotter(terms, t: float, steps: int, seed: int = 0) -> np.ndarray:
    """
    First-order Trotter with a *random term ordering* in each step -- randomizing the order
    cancels leading error terms in expectation, often beating fixed-order Trotter. Returns the
    (single random-instance) propagator; verified to approximate ``e^{-iHt}`` and improve with
    step count.
    """
    rng = np.random.default_rng(seed)
    n = len(terms[0][1])
    mats = _term_matrices(terms, n)
    dt = t / steps
    U = np.eye(2 ** n, dtype=complex)
    for _ in range(steps):
        order = rng.permutation(len(mats))
        for k in order:
            coeff, M = mats[k]
            U = expm(-1j * coeff * M * dt) @ U
    return U


def simulate_state(terms, t: float, steps: int, order: int, initial_state=None):
    """
    Apply the order-``order`` product formula to a state and return the fidelity to the exact
    evolution ``|<exact|approx>|^2``. Verified to approach 1 as ``steps`` grows.
    """
    n = len(terms[0][1])
    if initial_state is None:
        psi0 = np.zeros(2 ** n, dtype=complex); psi0[0] = 1.0
    else:
        psi0 = np.asarray(initial_state, dtype=complex)
    U = {1: first_order_trotter, 2: second_order_trotter, 4: fourth_order_suzuki}[order](terms, t, steps)
    approx = U @ psi0
    exact = exact_evolution(terms, t) @ psi0
    return float(abs(np.vdot(exact, approx)) ** 2)


def error_scaling_slope(terms, t: float, order: int, step_range=(2, 4, 8, 16)) -> float:
    """
    Log-log slope of the Trotter error versus the number of steps -- approximately ``-order``
    (``-1`` first order, ``-2`` second, ``-4`` fourth). The direct verification of a formula's
    order of accuracy.
    """
    steps = np.array(step_range, dtype=float)
    errs = np.array([trotter_error(terms, t, int(r), order) for r in step_range])
    return float(np.polyfit(np.log(steps), np.log(errs), 1)[0])
