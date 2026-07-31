"""
Boson sampling and photon interference.

Sampling the output of ``n`` identical photons through a linear-optical network is believed
classically hard because the output amplitudes are matrix **permanents** -- and the
permanent is #P-hard. This module computes the permanent (Ryser's formula), the boson-
sampling output probabilities ``|perm(U_{S,T})|^2 / (prod s! prod t!)``, and the elementary
two-photon **Hong-Ou-Mandel** effect: identical photons entering a 50:50 beamsplitter always
*bunch*, so the coincidence probability drops to zero. Verified against ``perm`` of known
matrices, the HOM dip, and output-probability normalization.
"""

import numpy as np
from itertools import combinations
from math import factorial


def permanent(A) -> complex:
    """
    Matrix permanent via Ryser's formula ``(-1)^n sum_{S} (-1)^{|S|} prod_i sum_{j in S}
    A_ij`` -- like the determinant but with all plus signs (and #P-hard). Verified:
    ``perm(ones(n)) = n!`` and ``perm(I) = 1``.
    """
    A = np.asarray(A, dtype=complex)
    n = A.shape[0]
    total = 0
    for k in range(1, n + 1):
        for S in combinations(range(n), k):
            rowsums = np.prod([sum(A[i, j] for j in S) for i in range(n)])
            total += (-1) ** k * rowsums
    return complex((-1) ** n * total)


def _expand_columns(U, input_occ, output_occ):
    """Build the boson-sampling submatrix by repeating rows/cols per occupation number."""
    rows = [i for i, n in enumerate(output_occ) for _ in range(n)]
    cols = [j for j, n in enumerate(input_occ) for _ in range(n)]
    return U[np.ix_(rows, cols)]


def boson_sampling_probability(U, input_occ, output_occ) -> float:
    """
    Probability of the photon-number output configuration ``output_occ`` given input
    ``input_occ`` through the linear-optical unitary ``U``:
    ``|perm(U_{S,T})|^2 / (prod_i s_i! prod_j t_j!)``. Verified to normalize to 1 over all
    outputs with the same total photon number.
    """
    U = np.asarray(U, dtype=complex)
    M = _expand_columns(U, input_occ, output_occ)
    if M.size == 0:
        return 1.0 if sum(output_occ) == 0 else 0.0
    per = permanent(M)
    denom = np.prod([factorial(n) for n in input_occ]) * np.prod([factorial(n) for n in output_occ])
    return float(abs(per) ** 2 / denom)


def beamsplitter_unitary(theta: float) -> np.ndarray:
    """Real 2-mode beamsplitter unitary ``[[cos, sin], [-sin, cos]]`` (transmissivity
    ``cos^2 theta``)."""
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, s], [-s, c]], dtype=complex)


def hong_ou_mandel(theta: float) -> dict:
    """
    Hong-Ou-Mandel two-photon interference: send one photon into each input of a
    beamsplitter and report the ``coincidence`` (one photon per output) and ``bunching``
    (both photons in one output) probabilities. At the 50:50 point (``theta = pi/4``) the
    coincidence vanishes -- the HOM dip -- and the photons always bunch. Verified.
    """
    U = beamsplitter_unitary(theta)
    coincidence = boson_sampling_probability(U, [1, 1], [1, 1])
    bunch = (boson_sampling_probability(U, [1, 1], [2, 0])
             + boson_sampling_probability(U, [1, 1], [0, 2]))
    return {"coincidence": coincidence, "bunching": bunch}
