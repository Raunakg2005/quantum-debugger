"""
Dynamical decoupling (Hahn spin echo)

Where a decoherence-free subspace exploits a *spatial* symmetry of the noise, the
spin echo exploits a *temporal* one: noise that is (quasi-)static over one
experimental shot. A qubit with a random (shot-to-shot) detuning ``phi ~ N(0,
sigma^2)`` acquires the phase ``exp(-i phi Z / 2)`` over the shot, so the
ensemble-averaged coherence of ``|+>`` decays to ``exp(-sigma^2 / 2)``.

Hahn's 1950 trick: evolve for half the time, apply an X pulse, evolve the other
half. The phase accumulated after the flip *cancels* the phase before it,

    U(phi/2) X U(phi/2) = X        for every realization phi,

so the echoed coherence is EXACTLY 1 at any noise strength -- but only when the
noise is correlated across the shot. If the detuning re-randomizes between the two
halves ("fast" noise), the two phases are independent, nothing cancels, and the
echo provably gives no advantage (``exp(-sigma^2 / 2)``, same as free evolution).

All channels here are genuine ensemble averages of unitaries (Gauss-Hermite
quadrature), verified against these closed forms.
"""

import numpy as np
from numpy.polynomial.hermite import hermgauss

_X = np.array([[0, 1], [1, 0]], dtype=complex)


def _u_z(phi):
    """Free evolution exp(-i phi Z / 2)."""
    return np.diag([np.exp(-1j * phi / 2), np.exp(1j * phi / 2)])


def spin_echo(sigma: float, static: bool = True, nodes: int = 41) -> dict:
    """
    Ensemble-averaged dephasing of a ``|+>`` qubit at noise strength ``sigma``, with
    and without a Hahn echo (X pulse at mid-evolution).

    ``static=True`` models quasi-static noise (one detuning per shot, total phase
    variance ``sigma^2``); ``static=False`` re-randomizes the detuning between the
    two halves (independent phases of variance ``sigma^2 / 2`` each).

    Returns dict with:
      * ``no_echo``           -- surviving coherence fraction without the echo
      * ``echo``              -- with the echo
      * ``no_echo_analytic``  -- ``exp(-sigma^2 / 2)`` (either noise type)
      * ``echo_analytic``     -- 1.0 for static noise, ``exp(-sigma^2 / 2)`` for fast
    """
    xs, ws = hermgauss(nodes)
    weights = ws / np.sqrt(np.pi)
    plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
    rho0 = np.outer(plus, plus.conj())

    no_echo = np.zeros((2, 2), dtype=complex)
    echo = np.zeros((2, 2), dtype=complex)

    if static:
        phis = np.sqrt(2) * sigma * xs  # phi ~ N(0, sigma^2)
        for phi, w in zip(phis, weights):
            U_free = _u_z(phi)
            no_echo += w * (U_free @ rho0 @ U_free.conj().T)
            U_echo = _u_z(phi / 2) @ _X @ _u_z(phi / 2)
            echo += w * (U_echo @ rho0 @ U_echo.conj().T)
        echo_analytic = 1.0
    else:
        # Two independent half-phases, each ~ N(0, sigma^2 / 2).
        half = np.sqrt(2) * (sigma / np.sqrt(2)) * xs
        for p1, w1 in zip(half, weights):
            for p2, w2 in zip(half, weights):
                w = w1 * w2
                U_free = _u_z(p2) @ _u_z(p1)
                no_echo += w * (U_free @ rho0 @ U_free.conj().T)
                U_echo = _u_z(p2) @ _X @ _u_z(p1)
                echo += w * (U_echo @ rho0 @ U_echo.conj().T)
        echo_analytic = float(np.exp(-(sigma**2) / 2))

    return {
        "no_echo": float(2 * abs(no_echo[0, 1])),
        "echo": float(2 * abs(echo[0, 1])),
        "no_echo_analytic": float(np.exp(-(sigma**2) / 2)),
        "echo_analytic": echo_analytic,
    }


def echo_state_fidelity(sigma: float, alpha=1.0, beta=1.0, nodes: int = 41) -> float:
    """
    Fidelity of an arbitrary qubit ``alpha|0> + beta|1>`` after quasi-static
    dephasing WITH a Hahn echo, relative to the noise-free echoed state ``X|psi>``.
    Exactly 1 for any ``sigma``: the echo commutes the noise away shot by shot.
    """
    norm = np.sqrt(abs(alpha) ** 2 + abs(beta) ** 2)
    psi = np.array([alpha, beta], dtype=complex) / norm
    rho0 = np.outer(psi, psi.conj())

    xs, ws = hermgauss(nodes)
    weights = ws / np.sqrt(np.pi)
    phis = np.sqrt(2) * sigma * xs
    out = np.zeros((2, 2), dtype=complex)
    for phi, w in zip(phis, weights):
        U = _u_z(phi / 2) @ _X @ _u_z(phi / 2)
        out += w * (U @ rho0 @ U.conj().T)

    ideal = _X @ psi
    # Pure target: F = <ideal| rho |ideal> exactly (no matrix square roots).
    return float(np.real(ideal.conj() @ out @ ideal))
