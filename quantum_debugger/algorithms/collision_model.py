"""
Collision models: open-system dynamics from repeated ancilla interactions.

A collision model builds dissipation from elementary unitary *collisions*: the system interacts
briefly with a fresh environment ancilla, which is then discarded (traced out). Repeating this
with identical ancillas gives a discrete completely-positive dynamical map whose fixed point is
the ancilla's state -- so a stream of thermal ancillas drives the system to thermal equilibrium.
This is the microscopic, fully-unitary route to the Lindblad equation.

The canonical collision is a *partial swap* ``U = exp(-i theta SWAP)``: at ``theta = pi/2`` it is a
full SWAP (the system instantly becomes the ancilla), and for smaller angles it mixes the two
states gradually. Either way the ancilla state ``sigma`` is the unique fixed point.

Verified: the fixed point of repeated partial-SWAP collisions is exactly the ancilla state;
thermal ancillas drive the system to the Gibbs state; a full SWAP thermalizes in a single step.
"""

import numpy as np

_SWAP = np.array([[1, 0, 0, 0],
                  [0, 0, 1, 0],
                  [0, 1, 0, 0],
                  [0, 0, 0, 1]], dtype=complex)


def partial_swap(theta):
    """The partial-swap collision unitary ``U = exp(-i theta SWAP)``. ``theta = pi/2`` is a full
    SWAP; small ``theta`` gives a weak collision."""
    from scipy.linalg import expm
    return expm(-1j * theta * _SWAP)


def thermal_qubit(beta, omega=1.0):
    """
    Gibbs state of a qubit with energy gap ``omega`` at inverse temperature ``beta``:
    ``diag(1, e^{-beta omega}) / Z``. ``beta -> infinity`` is the ground state ``|0><0|``.
    """
    p = np.exp(-beta * omega)
    Z = 1.0 + p
    return np.diag([1.0 / Z, p / Z]).astype(complex)


def collision_step(rho_sys, rho_anc, U):
    """
    One collision: evolve the joint system-ancilla state under ``U`` and trace out the ancilla.
    Returns the updated (2x2) system density matrix.
    """
    rho_sys = np.asarray(rho_sys, dtype=complex)
    rho_anc = np.asarray(rho_anc, dtype=complex)
    joint = U @ np.kron(rho_sys, rho_anc) @ U.conj().T
    ds = rho_sys.shape[0]
    da = rho_anc.shape[0]
    joint = joint.reshape(ds, da, ds, da)
    return np.trace(joint, axis1=1, axis2=3)


def repeated_collisions(rho0, rho_anc, U, n):
    """Apply ``n`` collisions with fresh copies of ancilla ``rho_anc`` and collision unitary ``U``.
    Returns the trajectory ``[rho_0, rho_1, ..., rho_n]`` of system states."""
    rho = np.asarray(rho0, dtype=complex)
    traj = [rho]
    for _ in range(n):
        rho = collision_step(rho, rho_anc, U)
        traj.append(rho)
    return traj


def thermalize(rho0, beta, omega=1.0, theta=0.3, n=200):
    """
    Drive a qubit toward the Gibbs state ``thermal_qubit(beta, omega)`` by ``n`` partial-swap
    collisions with thermal ancillas. Returns the final system state.
    """
    sigma = thermal_qubit(beta, omega)
    U = partial_swap(theta)
    return repeated_collisions(rho0, sigma, U, n)[-1]


def fixed_point_error(rho0, rho_anc, theta=0.3, n=200):
    """
    Distance from the ancilla state after ``n`` partial-swap collisions -- verified to shrink to 0,
    since the ancilla state is the unique fixed point of the collision map.
    """
    U = partial_swap(theta)
    rho_n = repeated_collisions(rho0, rho_anc, U, n)[-1]
    diff = rho_n - np.asarray(rho_anc, dtype=complex)
    diff = 0.5 * (diff + diff.conj().T)
    return float(0.5 * np.sum(np.abs(np.linalg.eigvalsh(diff))))


def full_swap_is_one_step(rho0, rho_anc, atol=1e-9):
    """Verify that a full SWAP collision (``theta = pi/2``) replaces the system with the ancilla in
    a single step -- the strongest collision."""
    U = partial_swap(np.pi / 2)
    rho1 = collision_step(rho0, rho_anc, U)
    return bool(np.allclose(rho1, np.asarray(rho_anc, dtype=complex), atol=atol))
