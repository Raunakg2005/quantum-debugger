"""
Tests for the 1.5.0 quantum-information suite: distinguishability measures, entropies,
coherence, entanglement measures, majorization, and entanglement witnesses. Verified
against Bell / Werner / product states and closed forms.
"""

import numpy as np
import pytest

from quantum_debugger.algorithms.quantum_distances import (
    trace_distance, uhlmann_fidelity, bures_distance, bures_angle,
    hilbert_schmidt_distance, fuchs_van_de_graaf, quantum_relative_entropy)
from quantum_debugger.algorithms.quantum_entropies import (
    von_neumann_entropy, renyi_entropy, tsallis_entropy, conditional_entropy,
    quantum_mutual_information, entanglement_entropy_pure)
from quantum_debugger.algorithms.coherence import (
    l1_coherence, relative_entropy_of_coherence, robustness_of_coherence, is_incoherent)
from quantum_debugger.algorithms.entanglement_measures import (
    concurrence, entanglement_of_formation, tangle, schmidt_coefficients, schmidt_rank)
from quantum_debugger.algorithms.majorization import (
    majorizes, nielsen_convertible, majorization_entropy_bound)
from quantum_debugger.algorithms.entanglement_witness import (
    witness_expectation, bell_witness, realignment_norm, realignment_criterion)

BELL = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
RHO_BELL = np.outer(BELL, BELL.conj())
RHO_PROD = np.zeros((4, 4), dtype=complex); RHO_PROD[0, 0] = 1
MIXED4 = np.eye(4) / 4


def _dm(psi):
    psi = np.asarray(psi, dtype=complex)
    return np.outer(psi, psi.conj())


class TestDistances:
    def test_trace_distance(self):
        assert abs(trace_distance(_dm([1, 0]), _dm([0, 1])) - 1) < 1e-9
        assert trace_distance(_dm([1, 0]), _dm([1, 0])) < 1e-9

    def test_fidelity(self):
        assert uhlmann_fidelity(_dm([1, 0]), _dm([0, 1])) < 1e-9
        assert abs(uhlmann_fidelity(_dm([1, 1] / np.sqrt(2)), _dm([1, 0])) - 0.5) < 1e-6

    def test_fuchs_van_de_graaf(self):
        rng = np.random.default_rng(0)
        for _ in range(20):
            a = rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2)); ra = a @ a.conj().T; ra /= np.trace(ra)
            b = rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2)); rb = b @ b.conj().T; rb /= np.trace(rb)
            r = fuchs_van_de_graaf(ra, rb)
            assert r["lower"] - 1e-9 <= r["trace_distance"] <= r["upper"] + 1e-9

    def test_relative_entropy(self):
        assert quantum_relative_entropy(_dm([1, 1] / np.sqrt(2)), _dm([1, 1] / np.sqrt(2))) < 1e-9
        assert abs(quantum_relative_entropy(_dm([1, 0]), np.eye(2) / 2) - 1) < 1e-6
        assert quantum_relative_entropy(_dm([1, 1] / np.sqrt(2)), np.eye(2) / 2) >= -1e-9

    def test_metrics_nonneg(self):
        assert bures_distance(_dm([1, 0]), _dm([0, 1])) >= 0
        assert 0 <= bures_angle(_dm([1, 0]), _dm([0, 1])) <= np.pi / 2 + 1e-9
        assert hilbert_schmidt_distance(_dm([1, 0]), _dm([0, 1])) > 0


class TestEntropies:
    def test_von_neumann(self):
        assert von_neumann_entropy(_dm([1, 0])) < 1e-9
        assert abs(von_neumann_entropy(np.eye(2) / 2) - 1) < 1e-9

    def test_renyi_limits(self):
        rho = np.diag([0.6, 0.3, 0.1])
        assert abs(renyi_entropy(rho, 1.0001) - von_neumann_entropy(rho)) < 1e-2
        assert abs(renyi_entropy(rho, 1e-4) - np.log2(3)) < 1e-2

    def test_tsallis_limit(self):
        rho = np.eye(2) / 2
        assert abs(tsallis_entropy(rho, 1.0001) - von_neumann_entropy(rho, base=np.e)) < 1e-2

    def test_bell_correlations(self):
        assert abs(conditional_entropy(RHO_BELL, (2, 2)) + 1) < 1e-6
        assert abs(quantum_mutual_information(RHO_BELL, (2, 2)) - 2) < 1e-6

    def test_entanglement_entropy_pure(self):
        assert abs(entanglement_entropy_pure(BELL, (2, 2)) - 1) < 1e-9
        assert entanglement_entropy_pure([1, 0, 0, 0], (2, 2)) < 1e-9


class TestCoherence:
    def test_l1(self):
        assert abs(l1_coherence(_dm([1, 1] / np.sqrt(2))) - 1) < 1e-9
        assert l1_coherence(np.eye(2) / 2) < 1e-9

    def test_relative_entropy_of_coherence(self):
        d = 3; maxcoh = np.ones((d, d), dtype=complex) / d
        assert abs(relative_entropy_of_coherence(maxcoh) - np.log2(3)) < 1e-6
        assert relative_entropy_of_coherence(np.eye(2) / 2) < 1e-9

    def test_robustness_and_incoherent(self):
        assert abs(robustness_of_coherence(_dm([1, 1] / np.sqrt(2))) - 1) < 1e-9
        assert is_incoherent(np.eye(2) / 2)


class TestEntanglementMeasures:
    def test_concurrence(self):
        assert abs(concurrence(RHO_BELL) - 1) < 1e-9
        assert concurrence(RHO_PROD) < 1e-9

    def test_werner_threshold(self):
        for p in (0.2, 0.5, 1.0):
            rw = p * RHO_BELL + (1 - p) * MIXED4
            assert abs(concurrence(rw) - max(0, (3 * p - 1) / 2)) < 1e-6

    def test_eof_and_tangle(self):
        assert abs(entanglement_of_formation(RHO_BELL) - 1) < 1e-6
        assert abs(tangle(RHO_BELL) - 1) < 1e-9

    def test_schmidt(self):
        assert schmidt_rank(BELL, (2, 2)) == 2
        assert schmidt_rank([1, 0, 0, 0], (2, 2)) == 1


class TestMajorization:
    def test_majorizes(self):
        assert majorizes([0.7, 0.3], [0.5, 0.5])       # peaked majorizes flat
        assert not majorizes([0.5, 0.5], [0.7, 0.3])

    def test_nielsen(self):
        less = np.array([np.sqrt(0.8), 0, 0, np.sqrt(0.2)], dtype=complex)
        assert nielsen_convertible(BELL, less, (2, 2))       # max -> less: OK
        assert not nielsen_convertible(less, BELL, (2, 2))   # less -> max: forbidden

    def test_entropy_bound(self):
        assert majorization_entropy_bound([0.7, 0.3], [0.5, 0.5])


class TestWitnesses:
    def test_bell_witness(self):
        W = bell_witness(0)
        assert witness_expectation(RHO_BELL, W) < 0      # detects entanglement
        assert witness_expectation(MIXED4, W) >= -1e-9   # non-negative on separable

    def test_realignment(self):
        assert abs(realignment_norm(RHO_BELL, (2, 2)) - 2) < 1e-9
        assert realignment_criterion(RHO_BELL, (2, 2))
        assert not realignment_criterion(MIXED4, (2, 2))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
