"""Tests for measurement-based quantum computation (one-bit teleportation)."""

import numpy as np
import pytest

from quantum_debugger.algorithms import cluster_pair, mbqc_rotation

_H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
_X = np.array([[0, 1], [1, 0]], dtype=complex)


def _rz(t):
    return np.array([[np.exp(-1j * t / 2), 0], [0, np.exp(1j * t / 2)]], dtype=complex)


class TestClusterPair:
    def test_is_stabilized(self):
        # CZ(|+>|+>) is stabilized by X0 Z1 and Z0 X1.
        state = cluster_pair([1, 1])  # |+> input (cluster_pair normalizes)
        from quantum_debugger.stabilizer import stabilizer_to_pauli_matrix as P

        for s in ("XZ", "ZX"):
            assert abs(np.real(np.vdot(state, P(1, s) @ state)) - 1.0) < 1e-9

    def test_normalized(self):
        assert abs(np.linalg.norm(cluster_pair([0.6, 0.8j])) - 1.0) < 1e-12


class TestMBQCRotation:
    @pytest.mark.parametrize("seed", range(20))
    def test_raw_output_matches_byproduct_law(self, seed):
        rng = np.random.default_rng(seed)
        psi = rng.normal(size=2) + 1j * rng.normal(size=2)
        alpha = rng.uniform(0, 2 * np.pi)
        r = mbqc_rotation(psi, alpha, seed=seed, correct=False)
        assert r["fidelity"] > 1 - 1e-9
        ideal = np.linalg.matrix_power(_X, r["outcome"]) @ _H @ _rz(-alpha) @ (
            psi / np.linalg.norm(psi)
        )
        fid = abs(np.vdot(ideal / np.linalg.norm(ideal),
                          r["output"] / np.linalg.norm(r["output"]))) ** 2
        assert fid > 1 - 1e-9

    @pytest.mark.parametrize("seed", range(20))
    def test_corrected_gate_is_deterministic(self, seed):
        # With byproduct correction the map is exactly H Rz(-alpha), regardless of s.
        rng = np.random.default_rng(seed)
        psi = rng.normal(size=2) + 1j * rng.normal(size=2)
        psi = psi / np.linalg.norm(psi)
        alpha = rng.uniform(0, 2 * np.pi)
        r = mbqc_rotation(psi, alpha, seed=seed, correct=True)
        ideal = _H @ _rz(-alpha) @ psi
        fid = abs(np.vdot(ideal, r["output"] / np.linalg.norm(r["output"]))) ** 2
        assert fid > 1 - 1e-9

    def test_alpha_zero_is_hadamard(self):
        # alpha = 0: the corrected gate is exactly H.
        for psi in ([1, 0], [0, 1], [1, 1j]):
            r = mbqc_rotation(psi, 0.0, seed=1, correct=True)
            ideal = _H @ (np.array(psi, dtype=complex) / np.linalg.norm(psi))
            fid = abs(np.vdot(ideal, r["output"] / np.linalg.norm(r["output"]))) ** 2
            assert fid > 1 - 1e-9

    def test_both_outcomes_occur(self):
        outcomes = {mbqc_rotation([1, 0], np.pi / 2, seed=s)["outcome"] for s in range(30)}
        assert outcomes == {0, 1}

    def test_outcome_probabilities_are_half_on_plus(self):
        # For |psi> = |0>, the tilted-basis outcome is unbiased.
        ones = sum(mbqc_rotation([1, 0], 0.7, seed=s)["outcome"] for s in range(400))
        assert 150 < ones < 250  # ~200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
