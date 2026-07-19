"""Tests for BB84 quantum key distribution."""

import pytest

from quantum_debugger.algorithms import bb84


class TestBB84NoEavesdropper:
    @pytest.mark.parametrize("seed", range(5))
    def test_keys_match_and_secure(self, seed):
        r = bb84(n_bits=128, eavesdropper=False, seed=seed)
        assert r["qber"] == 0.0
        assert r["keys_match"]
        assert r["secure"]
        assert r["alice_key"] == r["bob_key"]

    def test_sifted_length_is_about_half(self):
        r = bb84(n_bits=200, eavesdropper=False, seed=1)
        assert 60 < r["sifted_length"] < 140  # ~100 on average


class TestBB84WithEavesdropper:
    @pytest.mark.parametrize("seed", range(5))
    def test_detected(self, seed):
        r = bb84(n_bits=256, eavesdropper=True, seed=seed)
        # Intercept-resend injects ~25% QBER, well above the abort threshold.
        assert r["qber"] > 0.11
        assert not r["secure"]

    def test_qber_near_quarter(self):
        qbers = [bb84(n_bits=400, eavesdropper=True, seed=s)["qber"] for s in range(6)]
        assert 0.18 < sum(qbers) / len(qbers) < 0.32


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
