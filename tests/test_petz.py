"""Tests for the Petz recovery map (approximate quantum error correction)."""

import numpy as np
import pytest

from quantum_debugger.algorithms import petz_recovery, petz_code_recovery

_X = np.array([[0, 1], [1, 0]], dtype=complex)
_K0 = np.array([[1, 0], [0, np.sqrt(0.9)]], dtype=complex)
_K1 = np.array([[0, np.sqrt(0.1)], [0, 0]], dtype=complex)


def _embed(op, q, n=3):
    mats = [op if i == q else np.eye(2, dtype=complex) for i in range(n)]
    out = np.array([[1]], dtype=complex)
    for m in reversed(mats):
        out = np.kron(out, m)
    return out


def _bitflip_channel(p):
    probs = [(1 - p) ** 3, p * (1 - p) ** 2, p * (1 - p) ** 2, p * (1 - p) ** 2]
    tot = sum(probs)
    ops = [np.eye(8, dtype=complex), _embed(_X, 0), _embed(_X, 1), _embed(_X, 2)]
    return [np.sqrt(pr / tot) * E for pr, E in zip(probs, ops)]


def _ad_channel_3(g):
    K0 = np.array([[1, 0], [0, np.sqrt(1 - g)]], dtype=complex)
    K1 = np.array([[0, np.sqrt(g)], [0, 0]], dtype=complex)
    ks = []
    for a in (K0, K1):
        for b in (K0, K1):
            for c in (K0, K1):
                op = np.array([[1]], dtype=complex)
                for m in (c, b, a):
                    op = np.kron(op, m)
                ks.append(op)
    return ks


_Z0 = np.zeros(8, dtype=complex)
_Z0[0] = 1
_Z1 = np.zeros(8, dtype=complex)
_Z1[7] = 1


class TestCorrectableRecovery:
    @pytest.mark.parametrize("alpha,beta", [(1, 0), (0, 1), (0.6, 0.8), (1, 1j)])
    def test_perfect_recovery_of_correctable_errors(self, alpha, beta):
        r = petz_code_recovery(_bitflip_channel(0.1), [_Z0, _Z1], alpha, beta)
        assert abs(r["recovered_fidelity"] - 1.0) < 1e-9
        assert r["improved"]

    def test_matches_syndrome_decoder_at_various_p(self):
        for p in (0.05, 0.2, 0.4):
            r = petz_code_recovery(_bitflip_channel(p), [_Z0, _Z1], 0.6, 0.8)
            assert abs(r["recovered_fidelity"] - 1.0) < 1e-9


class TestApproximateRecovery:
    def test_amplitude_damping_improves(self):
        r = petz_code_recovery(_ad_channel_3(0.1), [_Z0, _Z1], 0.6, 0.8)
        assert r["improved"]
        assert r["recovered_fidelity"] > r["noisy_fidelity"]
        assert r["recovered_fidelity"] < 1.0  # not perfectly correctable

    def test_stronger_damping_lower_fidelity(self):
        f_weak = petz_code_recovery(_ad_channel_3(0.05), [_Z0, _Z1], 0.6, 0.8)[
            "recovered_fidelity"
        ]
        f_strong = petz_code_recovery(_ad_channel_3(0.3), [_Z0, _Z1], 0.6, 0.8)[
            "recovered_fidelity"
        ]
        assert f_strong < f_weak


class TestPetzProperties:
    def test_recovers_reference_channel_output(self):
        # R_sigma(N(sigma)) = sigma exactly.
        kraus = _ad_channel_3(0.2)
        sigma = (np.outer(_Z0, _Z0.conj()) + np.outer(_Z1, _Z1.conj())) / 2
        n_sigma = sum(K @ sigma @ K.conj().T for K in kraus)
        recovered = petz_recovery(kraus, sigma, n_sigma)
        assert np.allclose(recovered, sigma, atol=1e-9)

    def test_recovery_preserves_trace(self):
        kraus = _bitflip_channel(0.15)
        rho = np.outer(_Z0, _Z0.conj())
        noisy = sum(K @ rho @ K.conj().T for K in kraus)
        sigma = (np.outer(_Z0, _Z0.conj()) + np.outer(_Z1, _Z1.conj())) / 2
        rec = petz_recovery(kraus, sigma, noisy)
        assert abs(np.trace(rec).real - 1.0) < 1e-9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
