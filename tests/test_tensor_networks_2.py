"""
Tests for the 2.7.0 tensor-networks suite: contraction cost/ordering, PEPS, MERA, and
entanglement scaling. Verified by round-tripping to the exact state vector and against
closed forms.
"""

import numpy as np
import pytest

from quantum_debugger.algorithms.tensor_contraction import (
    contract_pair, pairwise_cost, contract_chain, matrix_chain_left_cost,
    matrix_chain_optimal_cost, matrix_chain_optimal_order, contraction_speedup,
    svd_bond_truncation)
from quantum_debugger.algorithms.peps import (
    product_peps, bond_dimension, is_product_peps, contract_2x2,
    cluster_peps_statevector, cluster_state_reference)
from quantum_debugger.algorithms.mera import (
    disentangler, isometry, is_unitary, is_isometry, descending_superoperator,
    ascending_superoperator, causal_cone_width, ternary_isometry, renormalize_operator)
from quantum_debugger.algorithms.entanglement_scaling import (
    bipartite_entropy, max_entanglement, page_average_entropy, random_state_entropy,
    entanglement_spectrum, renyi2_entropy, is_area_law)


class TestContraction:
    def test_matrix_chain(self):
        dims = [10, 100, 5, 50, 1]
        assert matrix_chain_optimal_cost(dims) <= matrix_chain_left_cost(dims)
        assert contraction_speedup(dims) > 1

    def test_chain_result(self):
        rng = np.random.default_rng(0)
        mats = [rng.normal(size=(3, 4)), rng.normal(size=(4, 2)), rng.normal(size=(2, 5))]
        assert np.allclose(contract_chain(mats), mats[0] @ mats[1] @ mats[2])
        assert pairwise_cost({"a": 2, "b": 3}, {"b": 3, "c": 4}) == 24

    def test_svd_truncation(self):
        rng = np.random.default_rng(1)
        M = rng.normal(size=(4, 4))
        approx, fid = svd_bond_truncation(M, 4)
        assert abs(fid - 1) < 1e-9 and np.allclose(approx, M)
        _, fid2 = svd_bond_truncation(M, 1)
        assert fid2 < 1


class TestPEPS:
    def test_product(self):
        pp = product_peps()
        assert is_product_peps(pp) and bond_dimension(pp) == 1
        psi = contract_2x2(pp)
        assert abs(psi[0] - 1) < 1e-9 and np.allclose(psi[1:], 0)

    def test_cluster(self):
        cp = cluster_peps_statevector(); cr = cluster_state_reference()
        assert np.allclose(cp / np.linalg.norm(cp), cr / np.linalg.norm(cr), atol=1e-9)


class TestMERA:
    def test_unitarity_isometry(self):
        assert is_unitary(disentangler(1))
        assert is_isometry(isometry(2))
        assert is_isometry(ternary_isometry(3))

    def test_trace_preservation(self):
        w = isometry(2)
        rho = np.array([[0.7, 0.1], [0.1, 0.3]], dtype=complex)
        assert abs(np.trace(descending_superoperator(rho, w)) - 1) < 1e-9

    def test_causal_cone_and_rg(self):
        assert causal_cone_width(3) == causal_cone_width(10) == 3
        w = isometry(2)
        O = renormalize_operator(np.eye(4, dtype=complex), w, layers=1)  # one 4->2 coarse-grain
        assert O.shape == (2, 2)


class TestEntanglementScaling:
    def test_product_and_bell(self):
        prod = np.zeros(16, dtype=complex); prod[0] = 1
        bell = np.zeros(4, dtype=complex); bell[0] = bell[3] = 1 / np.sqrt(2)
        assert bipartite_entropy(prod, 2) < 1e-9
        assert abs(bipartite_entropy(bell, 1) - 1) < 1e-9
        assert is_area_law([bipartite_entropy(prod, k) for k in (1, 2, 3)])

    def test_page_value(self):
        for n, na in [(6, 2), (8, 3)]:
            assert abs(random_state_entropy(n, na, samples=20) - page_average_entropy(n, na)) < 0.05

    def test_spectrum_and_renyi(self):
        bell = np.zeros(4, dtype=complex); bell[0] = bell[3] = 1 / np.sqrt(2)
        spec = entanglement_spectrum(bell, 1)
        assert abs(spec.sum() - 1) < 1e-9 and np.allclose(spec, [0.5, 0.5])
        assert abs(renyi2_entropy(bell, 1) - 1) < 1e-9
        assert max_entanglement(3, 8) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
