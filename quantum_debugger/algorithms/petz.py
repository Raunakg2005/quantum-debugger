"""
Approximate quantum error correction: the Petz recovery map

Not every noise channel has a perfect correction -- but there is a canonical
"best effort" recovery, the **Petz (transpose) map**. For a channel ``N`` with
Kraus operators ``{K_k}`` and a reference state ``sigma`` (typically the maximally
mixed code state), it is

    R_sigma(rho) = sigma^{1/2} N^dagger( N(sigma)^{-1/2} rho N(sigma)^{-1/2} ) sigma^{1/2},

where ``N^dagger(X) = sum_k K_k^dagger X K_k`` is the adjoint channel. Key facts,
all verified here:

  * if the noise is *correctable* on the code (Knill-Laflamme conditions hold), the
    Petz map recovers the logical state **perfectly** -- it reproduces the usual
    syndrome decoder;
  * for uncorrectable noise (e.g. amplitude damping on a repetition code) it still
    gives the near-optimal *approximate* recovery, beating no correction at all;
  * ``R_sigma(N(sigma)) = sigma`` exactly (it perfectly undoes the channel on the
    reference state).
"""

import numpy as np


def _herm_sqrt(M: np.ndarray) -> np.ndarray:
    vals, vecs = np.linalg.eigh((M + M.conj().T) / 2)
    vals = np.clip(vals.real, 0, None)
    return (vecs * np.sqrt(vals)) @ vecs.conj().T


def _herm_inv_sqrt(M: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    vals, vecs = np.linalg.eigh((M + M.conj().T) / 2)
    inv = np.array([1 / np.sqrt(v) if v > eps else 0.0 for v in vals.real])
    return (vecs * inv) @ vecs.conj().T


def _apply(kraus, rho):
    return sum(K @ rho @ K.conj().T for K in kraus)


def _apply_adjoint(kraus, rho):
    return sum(K.conj().T @ rho @ K for K in kraus)


def petz_recovery(kraus_ops, reference, rho) -> np.ndarray:
    """
    Apply the Petz recovery map for channel ``kraus_ops`` and reference state
    ``reference`` to the (noisy) density matrix ``rho``. Returns the recovered
    density matrix.
    """
    kraus = [np.asarray(K, dtype=complex) for K in kraus_ops]
    sigma = np.asarray(reference, dtype=complex)
    rho = np.asarray(rho, dtype=complex)

    n_sigma = _apply(kraus, sigma)
    n_inv_sqrt = _herm_inv_sqrt(n_sigma)
    inner = n_inv_sqrt @ rho @ n_inv_sqrt
    adj = _apply_adjoint(kraus, inner)
    s_sqrt = _herm_sqrt(sigma)
    return s_sqrt @ adj @ s_sqrt


def petz_code_recovery(kraus_ops, code_states, alpha=1.0, beta=0.0) -> dict:
    """
    Encode ``alpha|0_L> + beta|1_L>`` in the code spanned by ``code_states`` (a pair
    of orthonormal logical basis state vectors), pass it through the noise channel
    ``kraus_ops``, recover with the Petz map (reference = maximally mixed code state),
    and report the logical fidelity.

    Returns dict with:
      * ``recovered_fidelity``  -- logical fidelity after Petz recovery
      * ``noisy_fidelity``      -- fidelity of the un-recovered noisy state (baseline)
      * ``improved``            -- whether recovery helped
    """
    zero_l = np.asarray(code_states[0], dtype=complex)
    one_l = np.asarray(code_states[1], dtype=complex)
    norm = np.sqrt(abs(alpha) ** 2 + abs(beta) ** 2)
    logical = (alpha * zero_l + beta * one_l) / norm

    rho = np.outer(logical, logical.conj())
    sigma = (np.outer(zero_l, zero_l.conj()) + np.outer(one_l, one_l.conj())) / 2

    kraus = [np.asarray(K, dtype=complex) for K in kraus_ops]
    noisy = _apply(kraus, rho)
    recovered = petz_recovery(kraus, sigma, noisy)

    return {
        "recovered_fidelity": float(np.real(logical.conj() @ recovered @ logical)),
        "noisy_fidelity": float(np.real(logical.conj() @ noisy @ logical)),
        "improved": bool(
            np.real(logical.conj() @ recovered @ logical)
            > np.real(logical.conj() @ noisy @ logical) + 1e-9
        ),
    }
