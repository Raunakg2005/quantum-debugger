"""
Imaginary-time evolution (cooling to the ground state)

Replacing real time ``t`` with imaginary time ``-i tau`` in the Schrodinger equation
turns unitary evolution into exponential *cooling*:

    |psi(tau)> = e^{-tau H} |psi(0)> / || e^{-tau H} |psi(0)> ||.

Expanding in energy eigenstates, every excited component decays as ``e^{-tau E_k}``
relative to the ground state, so ``|psi(tau)>`` converges to the ground state (as long
as the start has some overlap with it) with the energy decreasing monotonically. This
is the classical engine behind QITE (quantum imaginary-time evolution) and
projector/diffusion Monte Carlo, and a robust alternative to variational ground-state
search -- no optimizer, no local minima. (Because the ground component decays
*slowest*, cooling converges to the ground state whenever the start overlaps it at
all; even a nominally orthogonal start has its ~1e-16 residual ground overlap
re-amplified, so plain imaginary-time evolution targets the ground state, not
excited levels.)
"""

import numpy as np
from scipy.linalg import expm


def imaginary_time_evolution(hamiltonian, initial_state=None, dtau: float = 0.1,
                             steps: int = 200, seed: int = 0) -> dict:
    """
    Cool ``initial_state`` toward the ground state of ``hamiltonian`` by normalized
    imaginary-time evolution.

    ``initial_state`` defaults to a random state (overlapping the ground state with
    probability 1). ``dtau`` is the imaginary-time step and ``steps`` the count.

    Returns dict with:
      * ``energy``           -- final ``<H>`` (converges to the ground energy)
      * ``exact_energy``     -- true ground energy (smallest eigenvalue)
      * ``error``            -- ``|energy - exact_energy|``
      * ``state``            -- the final normalized state vector
      * ``energy_trajectory``-- ``<H>`` after each step (monotonically non-increasing)
    """
    H = np.asarray(hamiltonian, dtype=complex)
    dim = H.shape[0]

    if initial_state is None:
        rng = np.random.default_rng(seed)
        psi = rng.normal(size=dim) + 1j * rng.normal(size=dim)
    else:
        psi = np.asarray(initial_state, dtype=complex)
    psi = psi / np.linalg.norm(psi)

    step = expm(-dtau * H)
    trajectory = [float(np.real(psi.conj() @ H @ psi))]
    for _ in range(steps):
        psi = step @ psi
        psi = psi / np.linalg.norm(psi)
        trajectory.append(float(np.real(psi.conj() @ H @ psi)))

    exact = float(np.linalg.eigvalsh(H).real.min())
    energy = trajectory[-1]
    return {
        "energy": energy,
        "exact_energy": exact,
        "error": abs(energy - exact),
        "state": psi,
        "energy_trajectory": trajectory,
    }
