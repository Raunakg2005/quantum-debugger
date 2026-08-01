"""
Quantum trajectories: the Monte Carlo wavefunction unraveling of the Lindblad equation.

Instead of propagating the density matrix, one can *unravel* the master equation into an ensemble
of stochastic pure-state trajectories (Mølmer-Castin-Dalibard). Each trajectory evolves under the
non-Hermitian effective Hamiltonian

    H_eff = H - (i/2) sum_k L_k^dagger L_k,

which shrinks the norm; the lost norm is the probability that a quantum *jump* ``|psi> -> L_k|psi>``
occurred in that step. Averaging ``|psi><psi|`` over many trajectories reproduces the Lindblad
density matrix exactly in the limit of many runs -- this module verifies that convergence, and is
the basis of how open systems are simulated with pure states (a quadratic memory saving).

Every routine is checked against the deterministic Lindblad evolution in
:mod:`quantum_debugger.algorithms.lindblad`.
"""

import numpy as np

from .lindblad import evolve_lindblad, vectorize, unvectorize


def effective_hamiltonian(H, jump_ops):
    """The non-Hermitian effective Hamiltonian ``H_eff = H - (i/2) sum_k L_k^dagger L_k`` that
    governs the no-jump evolution between quantum jumps."""
    H = np.asarray(H, dtype=complex)
    Heff = H.astype(complex).copy()
    for Lk in jump_ops:
        Lk = np.asarray(Lk, dtype=complex)
        Heff = Heff - 0.5j * (Lk.conj().T @ Lk)
    return Heff


def jump_rates(psi, jump_ops):
    """The instantaneous jump rates ``<psi| L_k^dagger L_k |psi>`` for each channel ``k`` -- the
    (unnormalized) probabilities per unit time of each quantum jump."""
    psi = np.asarray(psi, dtype=complex).ravel()
    rates = []
    for Lk in jump_ops:
        Lk = np.asarray(Lk, dtype=complex)
        v = Lk @ psi
        rates.append(float(np.vdot(v, v).real))
    return np.array(rates)


def quantum_jump_trajectory(H, jump_ops, psi0, t, steps=400, rng=None):
    """
    Simulate a single Monte Carlo wavefunction trajectory to time ``t`` over ``steps`` slices.
    Returns the final (normalized) pure state. Between jumps the state evolves under ``H_eff``;
    at each slice a jump ``|psi> -> L_k|psi>`` fires with probability set by the norm loss.
    """
    from scipy.linalg import expm
    if rng is None:
        rng = np.random.default_rng()
    psi = np.asarray(psi0, dtype=complex).ravel().copy()
    psi = psi / np.linalg.norm(psi)
    dt = t / steps
    Ueff = expm(-1j * effective_hamiltonian(H, jump_ops) * dt)
    ops = [np.asarray(Lk, dtype=complex) for Lk in jump_ops]
    for _ in range(steps):
        rates = jump_rates(psi, ops)
        dp = dt * rates.sum()
        if rng.random() >= dp or dp <= 0.0:
            psi = Ueff @ psi
            psi = psi / np.linalg.norm(psi)
        else:
            k = rng.choice(len(ops), p=rates / rates.sum())
            psi = ops[k] @ psi
            psi = psi / np.linalg.norm(psi)
    return psi


def trajectory_ensemble(H, jump_ops, psi0, t, n_traj=400, steps=200, seed=0):
    """
    Average ``|psi><psi|`` over ``n_traj`` Monte Carlo trajectories -- the stochastic estimate of
    the Lindblad density matrix ``rho(t)``. Converges to :func:`lindblad.evolve_lindblad` as
    ``n_traj -> infinity``.
    """
    rng = np.random.default_rng(seed)
    d = np.asarray(psi0).size
    rho = np.zeros((d, d), dtype=complex)
    for _ in range(n_traj):
        psi = quantum_jump_trajectory(H, jump_ops, psi0, t, steps=steps, rng=rng)
        rho += np.outer(psi, psi.conj())
    return rho / n_traj


def trajectory_lindblad_error(H, jump_ops, psi0, t, n_traj=400, steps=200, seed=0):
    """
    Trace-distance between the trajectory-averaged state and the exact Lindblad state -- the
    Monte Carlo sampling error, which shrinks as ``1/sqrt(n_traj)``.
    """
    rho0 = np.outer(np.asarray(psi0, dtype=complex).ravel(),
                    np.asarray(psi0, dtype=complex).ravel().conj())
    rho_exact = evolve_lindblad(H, jump_ops, rho0, t)
    rho_mc = trajectory_ensemble(H, jump_ops, psi0, t, n_traj=n_traj, steps=steps, seed=seed)
    diff = rho_mc - rho_exact
    return float(0.5 * np.sum(np.abs(np.linalg.eigvalsh(0.5 * (diff + diff.conj().T)))))


def mean_photon_emissions(H, jump_ops, psi0, t, n_traj=200, steps=200, seed=0):
    """
    The mean number of quantum jumps ('photon' emissions) per trajectory -- a directly observable
    counting statistic of the unraveling.
    """
    from scipy.linalg import expm
    rng = np.random.default_rng(seed)
    dt = t / steps
    Ueff = expm(-1j * effective_hamiltonian(H, jump_ops) * dt)
    ops = [np.asarray(Lk, dtype=complex) for Lk in jump_ops]
    total = 0
    for _ in range(n_traj):
        psi = np.asarray(psi0, dtype=complex).ravel().copy()
        psi /= np.linalg.norm(psi)
        for _ in range(steps):
            rates = jump_rates(psi, ops)
            dp = dt * rates.sum()
            if rng.random() >= dp or dp <= 0.0:
                psi = Ueff @ psi
            else:
                k = rng.choice(len(ops), p=rates / rates.sum())
                psi = ops[k] @ psi
                total += 1
            psi /= np.linalg.norm(psi)
    return total / n_traj
