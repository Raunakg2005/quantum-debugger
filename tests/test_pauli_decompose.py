"""Tests for Pauli decomposition of Hermitian operators."""

import numpy as np
import pytest

from quantum_debugger.algorithms import (
    pauli_decompose,
    hamiltonian_matrix,
    pauli_term_matrix,
    fermi_hubbard_hamiltonian,
    hopping_hamiltonian,
    variational_ground_state,
)


class TestReconstruction:
    @pytest.mark.parametrize("n", [1, 2, 3])
    def test_random_hermitian_roundtrip(self, n):
        rng = np.random.default_rng(n)
        M = rng.normal(size=(2**n, 2**n)) + 1j * rng.normal(size=(2**n, 2**n))
        H = M + M.conj().T
        terms = pauli_decompose(H)
        assert np.allclose(hamiltonian_matrix(terms, n), H, atol=1e-10)

    def test_coefficients_are_real(self):
        H = fermi_hubbard_hamiltonian(2, t=1.0, u=2.0)
        for coeff, _ in pauli_decompose(H):
            assert isinstance(coeff, float)

    def test_single_pauli_recovered(self):
        # Decomposing a pure Pauli string returns just that term.
        H = pauli_term_matrix("XZ")
        terms = pauli_decompose(H)
        assert len(terms) == 1
        assert abs(terms[0][0] - 1.0) < 1e-12 and terms[0][1] == "XZ"

    def test_identity_component(self):
        H = 2.5 * np.eye(4, dtype=complex)
        terms = dict((p, c) for c, p in pauli_decompose(H))
        assert abs(terms["II"] - 2.5) < 1e-12


class TestChemistryViaVQE:
    def test_vqe_recovers_hubbard_dimer(self):
        H = fermi_hubbard_hamiltonian(2, t=1.0, u=3.0)
        terms = pauli_decompose(H)
        res = variational_ground_state(terms, layers=4, restarts=6)
        exact = np.linalg.eigvalsh(H).real.min()
        assert abs(res["energy"] - exact) < 1e-6

    def test_vqe_recovers_hopping_ground(self):
        H = hopping_hamiltonian(3, t=1.0)
        terms = pauli_decompose(H)
        res = variational_ground_state(terms, layers=4, restarts=6)
        assert abs(res["energy"] - np.linalg.eigvalsh(H).real.min()) < 1e-6

    def test_decomposition_preserves_spectrum(self):
        H = fermi_hubbard_hamiltonian(2, t=1.2, u=1.7)
        terms = pauli_decompose(H)
        assert np.allclose(
            np.linalg.eigvalsh(hamiltonian_matrix(terms, 4)),
            np.linalg.eigvalsh(H),
            atol=1e-10,
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
