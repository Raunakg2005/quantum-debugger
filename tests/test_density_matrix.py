"""Tests for the density-matrix (open quantum systems) simulator."""

import numpy as np
import pytest

from quantum_debugger.density_matrix import (
    DensityMatrix,
    bit_flip,
    phase_flip,
    depolarizing,
    amplitude_damping,
    phase_damping,
    pauli_channel,
)
from quantum_debugger.core.gates import GateLibrary

_H = GateLibrary.H
_X = GateLibrary.X
_CNOT = GateLibrary.CNOT


class TestBasics:
    def test_pure_state_purity_one(self):
        dm = DensityMatrix(1)
        dm.apply_unitary(_H, [0])
        assert np.isclose(dm.purity(), 1.0)

    def test_probabilities(self):
        dm = DensityMatrix(2)
        dm.apply_unitary(_X, [1])  # |10> (qubit1=1)
        probs = dm.probabilities()
        assert np.isclose(probs[0b10], 1.0)

    def test_apply_unitary_matches_state_vector(self):
        from quantum_debugger.core.quantum_state import QuantumState

        st = QuantumState(2)
        st.apply_gate(_H, [0])
        st.apply_gate(_CNOT, [0, 1])
        dm = DensityMatrix(2)
        dm.apply_unitary(_H, [0])
        dm.apply_unitary(_CNOT, [0, 1])
        sv = st.state_vector
        assert np.allclose(dm.rho, np.outer(sv, sv.conj()))


class TestPartialTrace:
    def test_bell_reduced_is_maximally_mixed(self):
        dm = DensityMatrix(2)
        dm.apply_unitary(_H, [0])
        dm.apply_unitary(_CNOT, [0, 1])
        red = dm.partial_trace([0])
        assert np.isclose(red.purity(), 0.5)
        assert np.allclose(red.probabilities(), [0.5, 0.5])


class TestChannels:
    def test_depolarizing_full_gives_maximally_mixed(self):
        dm = DensityMatrix(1)
        dm.apply_unitary(_H, [0])
        dm.apply_channel(depolarizing(1.0), [0])
        assert np.isclose(dm.purity(), 0.5)

    def test_depolarizing_purity_decreases(self):
        purities = []
        for p in (0.0, 0.25, 0.5, 1.0):
            dm = DensityMatrix(1, state_vector=np.array([1, 1]) / np.sqrt(2))
            dm.apply_channel(depolarizing(p), [0])
            purities.append(dm.purity())
        assert purities[0] > purities[1] > purities[2] > purities[3]
        assert np.isclose(purities[0], 1.0) and np.isclose(purities[3], 0.5)

    def test_amplitude_damping_decays_excited_state(self):
        dm = DensityMatrix(1)
        dm.apply_unitary(_X, [0])  # |1>
        dm.apply_channel(amplitude_damping(1.0), [0])
        assert np.allclose(dm.probabilities(), [1.0, 0.0])  # fully decayed to |0>

    def test_bit_flip_and_phase_flip_are_valid_channels(self):
        for ch in (bit_flip(0.3), phase_flip(0.3), phase_damping(0.4)):
            total = sum(K.conj().T @ K for K in ch)
            assert np.allclose(total, np.eye(2))  # trace-preserving

    def test_pauli_channel(self):
        ch = pauli_channel(0.1, 0.05, 0.15)
        assert np.allclose(sum(K.conj().T @ K for K in ch), np.eye(2))
        # A pure Z channel at p=0.5 fully dephases |+>.
        dm = DensityMatrix(1, state_vector=np.array([1, 1]) / np.sqrt(2))
        dm.apply_channel(pauli_channel(0, 0, 0.5), [0])
        assert np.isclose(dm.purity(), 0.5)


class TestEntropy:
    def test_pure_state_zero_entropy(self):
        dm = DensityMatrix(1)
        dm.apply_unitary(_H, [0])
        assert np.isclose(dm.von_neumann_entropy(), 0.0, atol=1e-9)

    def test_maximally_mixed_entropy(self):
        dm = DensityMatrix(1)
        dm.apply_unitary(_H, [0])
        dm.apply_channel(depolarizing(1.0), [0])
        assert np.isclose(dm.von_neumann_entropy(), 1.0)

    def test_bell_entanglement_entropy_is_one_bit(self):
        dm = DensityMatrix(2)
        dm.apply_unitary(_H, [0])
        dm.apply_unitary(_CNOT, [0, 1])
        assert np.isclose(dm.von_neumann_entropy(), 0.0, atol=1e-9)  # global pure
        assert np.isclose(dm.entanglement_entropy([0]), 1.0)  # maximally entangled

    def test_product_state_no_entanglement(self):
        dm = DensityMatrix(2)
        dm.apply_unitary(_H, [0])
        assert np.isclose(dm.entanglement_entropy([0]), 0.0, atol=1e-9)


class TestMeasurement:
    def test_bell_sample_only_correlated(self):
        dm = DensityMatrix(2)
        dm.apply_unitary(_H, [0])
        dm.apply_unitary(_CNOT, [0, 1])
        counts = dm.sample(500, seed=1)
        assert set(counts) <= {"00", "11"}
        assert len(counts) == 2

    def test_measure_collapses_and_correlates(self):
        dm = DensityMatrix(2)
        dm.apply_unitary(_H, [0])
        dm.apply_unitary(_CNOT, [0, 1])
        rng = np.random.default_rng(0)
        assert dm.measure(0, rng) == dm.measure(1, rng)  # GHZ/Bell correlation

    def test_measure_deterministic_after_damping(self):
        dm = DensityMatrix(1)
        dm.apply_unitary(_X, [0])
        dm.apply_channel(amplitude_damping(1.0), [0])  # -> |0>
        assert dm.measure(0, np.random.default_rng(5)) == 0


class TestFidelity:
    def test_fidelity_identical_and_orthogonal(self):
        dm = DensityMatrix(1, state_vector=np.array([1, 1]) / np.sqrt(2))
        assert np.isclose(dm.fidelity(np.array([1, 1]) / np.sqrt(2)), 1.0)
        assert np.isclose(dm.fidelity(np.array([1, 0])), 0.5)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestChannelMetrics:
    def test_identity_is_perfect(self):
        from quantum_debugger.density_matrix import (
            process_fidelity,
            average_gate_fidelity,
        )

        I = np.eye(2, dtype=complex)
        assert abs(process_fidelity([I]) - 1.0) < 1e-12
        assert abs(average_gate_fidelity([I]) - 1.0) < 1e-12

    @pytest.mark.parametrize("p", [0.0, 0.1, 0.3, 0.5, 1.0])
    def test_depolarizing_average_fidelity(self, p):
        # Exact: average gate fidelity of the depolarizing channel is 1 - p/2.
        from quantum_debugger.density_matrix import average_gate_fidelity

        assert abs(average_gate_fidelity(depolarizing(p)) - (1 - p / 2)) < 1e-12

    def test_pauli_x_error_is_one_third(self):
        from quantum_debugger.density_matrix import average_gate_fidelity

        X = np.array([[0, 1], [1, 0]], dtype=complex)
        assert abs(average_gate_fidelity([X]) - 1 / 3) < 1e-12

    def test_fidelity_to_target_unitary(self):
        # A channel that IS the target unitary has process fidelity 1 to it.
        from quantum_debugger.density_matrix import process_fidelity

        H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
        assert abs(process_fidelity([H], target=H) - 1.0) < 1e-12
        # X measured against identity: orthogonal, process fidelity 0.
        X = np.array([[0, 1], [1, 0]], dtype=complex)
        assert abs(process_fidelity([X])) < 1e-12

    def test_bit_flip_matches_depolarizing_form(self):
        # bit_flip(p): F_process = 1 - p, F_avg = (2(1-p)+1)/3.
        from quantum_debugger.density_matrix import (
            process_fidelity,
            average_gate_fidelity,
        )

        p = 0.2
        assert abs(process_fidelity(bit_flip(p)) - (1 - p)) < 1e-12
        assert abs(average_gate_fidelity(bit_flip(p)) - (2 * (1 - p) + 1) / 3) < 1e-12


class TestLindblad:
    _SM = np.array([[0, 1], [0, 0]], dtype=complex)   # sigma_- : |1> -> |0>
    _SZ = np.array([[1, 0], [0, -1]], dtype=complex)
    _H0 = np.zeros((2, 2), dtype=complex)

    @pytest.mark.parametrize("gamma,t", [(0.7, 1.3), (1.0, 0.5), (0.3, 2.0)])
    def test_t1_relaxation_exponential(self, gamma, t):
        # |1> under sigma_- collapse: excited population decays as e^{-gamma t}.
        dm = DensityMatrix(state_vector=np.array([0, 1], dtype=complex))
        dm.evolve_lindblad(self._H0, [np.sqrt(gamma) * self._SM], t)
        assert abs(dm.rho[1, 1].real - np.exp(-gamma * t)) < 1e-9
        assert abs(dm.rho.trace().real - 1.0) < 1e-12

    @pytest.mark.parametrize("kappa,t", [(0.4, 0.9), (0.8, 1.5)])
    def test_t2_dephasing_kills_coherence(self, kappa, t):
        # |+> under sigma_z collapse: coherence decays as (1/2) e^{-2 kappa t}.
        dm = DensityMatrix(state_vector=np.array([1, 1], dtype=complex) / np.sqrt(2))
        dm.evolve_lindblad(self._H0, [np.sqrt(kappa) * self._SZ], t)
        assert abs(abs(dm.rho[0, 1]) - 0.5 * np.exp(-2 * kappa * t)) < 1e-9
        # populations are untouched by pure dephasing
        assert abs(dm.rho[0, 0].real - 0.5) < 1e-9

    def test_unitary_limit_is_rabi(self):
        # No collapse ops -> closed-system Rabi oscillation under H = omega X / 2.
        omega, t = 1.0, 1.1
        dm = DensityMatrix(state_vector=np.array([1, 0], dtype=complex))
        dm.evolve_lindblad(0.5 * omega * np.array([[0, 1], [1, 0]], dtype=complex), [], t)
        assert abs(dm.rho[1, 1].real - np.sin(omega * t / 2) ** 2) < 1e-9

    def test_zero_time_is_identity(self):
        dm = DensityMatrix(state_vector=np.array([1, 1], dtype=complex) / np.sqrt(2))
        before = dm.rho.copy()
        dm.evolve_lindblad(self._SZ, [np.sqrt(0.5) * self._SM], 0.0)
        assert np.allclose(dm.rho, before, atol=1e-12)

    def test_steady_state_is_ground(self):
        # Long relaxation drives any state to |0><0|.
        dm = DensityMatrix(state_vector=np.array([1, 1], dtype=complex) / np.sqrt(2))
        dm.evolve_lindblad(self._H0, [self._SM], 50.0)
        assert abs(dm.rho[0, 0].real - 1.0) < 1e-6


class TestChoiCPTP:
    def test_identity_choi_is_rank_one_maximally_entangled(self):
        from quantum_debugger.density_matrix import choi_matrix, kraus_rank

        I = np.eye(2, dtype=complex)
        J = choi_matrix([I])
        assert kraus_rank([I]) == 1
        # J / d is the maximally entangled Bell state |Omega><Omega|.
        eigs = np.linalg.eigvalsh(J).real
        assert abs(eigs.max() - 2.0) < 1e-9 and abs(eigs[:-1].max()) < 1e-9

    @pytest.mark.parametrize("p", [0.0, 0.1, 0.5, 1.0])
    def test_standard_channels_are_cptp(self, p):
        from quantum_debugger.density_matrix import is_cptp

        assert is_cptp(bit_flip(p))
        assert is_cptp(phase_flip(p))
        assert is_cptp(depolarizing(p))
        assert is_cptp(amplitude_damping(p))

    def test_non_tp_map_rejected(self):
        # A lone shrinking operator is CP but not trace preserving.
        from quantum_debugger.density_matrix import is_cptp

        assert not is_cptp([0.5 * np.eye(2, dtype=complex)])

    def test_kraus_rank_counts_noise(self):
        from quantum_debugger.density_matrix import kraus_rank

        X = np.array([[0, 1], [1, 0]], dtype=complex)
        assert kraus_rank([X]) == 1                 # unitary -> rank 1
        assert kraus_rank(depolarizing(0.3)) == 4   # full depolarizing -> rank 4
        assert kraus_rank(amplitude_damping(0.2)) == 2


class TestCoherence:
    def test_plus_state_is_unit_coherent(self):
        dm = DensityMatrix(state_vector=np.array([1, 1], dtype=complex) / np.sqrt(2))
        assert abs(dm.l1_coherence() - 1.0) < 1e-12
        assert abs(dm.relative_entropy_coherence() - 1.0) < 1e-12

    def test_computational_basis_is_incoherent(self):
        dm = DensityMatrix(state_vector=np.array([0, 1], dtype=complex))
        assert abs(dm.l1_coherence()) < 1e-12
        assert abs(dm.relative_entropy_coherence()) < 1e-12

    def test_maximally_mixed_is_incoherent(self):
        dm = DensityMatrix(rho=np.eye(2, dtype=complex) / 2)
        assert abs(dm.l1_coherence()) < 1e-12
        assert abs(dm.relative_entropy_coherence()) < 1e-12

    def test_bell_state_one_bit_of_coherence(self):
        sv = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
        dm = DensityMatrix(state_vector=sv)
        assert abs(dm.l1_coherence() - 1.0) < 1e-12
        assert abs(dm.relative_entropy_coherence() - 1.0) < 1e-12

    def test_dephasing_destroys_coherence(self):
        # Full phase damping on |+> removes all coherence.
        dm = DensityMatrix(state_vector=np.array([1, 1], dtype=complex) / np.sqrt(2))
        dm.apply_channel(phase_damping(1.0), [0])
        assert abs(dm.l1_coherence()) < 1e-12


class TestNegativity:
    def _bell(self):
        sv = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
        return DensityMatrix(state_vector=sv)

    def test_bell_negativity_half(self):
        dm = self._bell()
        assert abs(dm.negativity([0]) - 0.5) < 1e-12
        assert abs(dm.logarithmic_negativity([0]) - 1.0) < 1e-12

    def test_product_state_zero(self):
        dm = DensityMatrix(state_vector=np.array([1, 0, 0, 0], dtype=complex))
        assert abs(dm.negativity([0])) < 1e-12
        assert abs(dm.logarithmic_negativity([0])) < 1e-12

    @pytest.mark.parametrize("p", [0.2, 1 / 3, 0.5, 0.8, 1.0])
    def test_werner_matches_analytic(self, p):
        bell_sv = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
        bell = np.outer(bell_sv, bell_sv.conj())
        rho = p * bell + (1 - p) * np.eye(4, dtype=complex) / 4
        dm = DensityMatrix(rho=rho)
        assert abs(dm.negativity([0]) - max(0.0, (3 * p - 1) / 4)) < 1e-12

    def test_ppt_below_threshold_is_separable(self):
        # A Werner state with p < 1/3 is PPT (zero negativity).
        bell_sv = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
        bell = np.outer(bell_sv, bell_sv.conj())
        rho = 0.25 * bell + 0.75 * np.eye(4, dtype=complex) / 4
        dm = DensityMatrix(rho=rho)
        assert dm.negativity([0]) < 1e-12

    def test_partial_transpose_preserves_trace(self):
        dm = self._bell()
        assert abs(dm.partial_transpose([0]).rho.trace().real - 1.0) < 1e-12


class TestMutualInformation:
    def test_bell_two_bits(self):
        sv = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
        dm = DensityMatrix(state_vector=sv)
        assert abs(dm.mutual_information([0]) - 2.0) < 1e-9

    def test_product_state_zero(self):
        dm = DensityMatrix(state_vector=np.array([1, 0, 0, 0], dtype=complex))
        assert abs(dm.mutual_information([0])) < 1e-9

    def test_classically_correlated_one_bit(self):
        # (|00><00| + |11><11|)/2 : classical correlation, I = 1 bit.
        rho = np.zeros((4, 4), dtype=complex)
        rho[0, 0] = rho[3, 3] = 0.5
        dm = DensityMatrix(rho=rho)
        assert abs(dm.mutual_information([0]) - 1.0) < 1e-9


class TestQuantumDiscord:
    def _luo(self, l):
        # Luo's closed form for Bell-diagonal states (PRA 77, 042303).
        from quantum_debugger.algorithms import bell_diagonal_state

        w1, w2, w3, w4 = l
        c1 = w1 - w2 + w3 - w4
        c2 = -w1 + w2 + w3 - w4
        c3 = w1 + w2 - w3 - w4
        c = max(abs(c1), abs(c2), abs(c3))
        vals = np.linalg.eigvalsh(bell_diagonal_state(*l)).real
        vals = vals[vals > 1e-12]
        s_ab = float(-np.sum(vals * np.log2(vals)))
        C = sum(
            ((1 + s * c) / 2) * np.log2(1 + s * c)
            for s in (+1, -1)
            if 1 + s * c > 1e-12
        )
        return (2 - s_ab) - C

    def test_bell_state_is_one_bit(self):
        from quantum_debugger.density_matrix import quantum_discord

        dm = DensityMatrix(state_vector=np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2))
        assert abs(quantum_discord(dm) - 1.0) < 1e-6

    def test_classical_state_is_zero(self):
        from quantum_debugger.density_matrix import quantum_discord

        rho = np.zeros((4, 4), dtype=complex)
        rho[0, 0] = rho[3, 3] = 0.5
        assert quantum_discord(DensityMatrix(rho=rho)) < 1e-6

    def test_product_state_is_zero(self):
        from quantum_debugger.density_matrix import quantum_discord

        dm = DensityMatrix(state_vector=np.array([1, 1, 1, 1], dtype=complex) / 2)
        assert quantum_discord(dm) < 1e-6

    @pytest.mark.parametrize("seed", range(3))
    def test_matches_luo_closed_form(self, seed):
        from quantum_debugger.density_matrix import quantum_discord
        from quantum_debugger.algorithms import bell_diagonal_state

        rng = np.random.default_rng(seed)
        l = tuple(rng.dirichlet([2, 1, 1, 1]))
        dm = DensityMatrix(rho=bell_diagonal_state(*l))
        assert abs(quantum_discord(dm) - self._luo(l)) < 1e-5

    def test_separable_state_with_discord(self):
        # Werner F = 0.4: zero negativity (separable), nonzero discord.
        from quantum_debugger.density_matrix import quantum_discord
        from quantum_debugger.algorithms import bell_diagonal_state

        l = (0.4, 0.2, 0.2, 0.2)
        dm = DensityMatrix(rho=bell_diagonal_state(*l))
        assert dm.negativity([0]) < 1e-12
        d = quantum_discord(dm)
        assert d > 0.01
        assert abs(d - self._luo(l)) < 1e-5

    def test_pure_state_discord_equals_entanglement_entropy(self):
        from quantum_debugger.density_matrix import quantum_discord

        theta = 0.6
        sv = np.zeros(4, dtype=complex)
        sv[0], sv[3] = np.cos(theta), np.sin(theta)
        dm = DensityMatrix(state_vector=sv)
        assert abs(quantum_discord(dm) - dm.entanglement_entropy([0])) < 1e-6


class TestRelaxationTimes:
    @pytest.mark.parametrize("g1,gphi", [(0.5, 0.0), (0.5, 0.3), (1.0, 0.8), (0.2, 2.0)])
    def test_identity_holds(self, g1, gphi):
        from quantum_debugger.density_matrix import relaxation_times

        r = relaxation_times(g1, gphi)
        assert r["identity_residual"] < 1e-9
        assert r["t2_le_2t1"]
        assert abs(r["T1"] - 1 / g1) < 1e-9

    def test_no_dephasing_gives_t2_equals_2t1(self):
        from quantum_debugger.density_matrix import relaxation_times

        r = relaxation_times(0.7, 0.0)
        assert abs(r["T2"] - 2 * r["T1"]) < 1e-9
        assert r["T_phi"] == np.inf

    def test_strong_dephasing_shortens_t2(self):
        from quantum_debugger.density_matrix import relaxation_times

        r = relaxation_times(0.5, 5.0)
        assert r["T2"] < r["T1"]  # dephasing-dominated qubit

    def test_invalid_gamma1_rejected(self):
        from quantum_debugger.density_matrix import relaxation_times

        with pytest.raises(ValueError):
            relaxation_times(0.0)


class TestConcurrence:
    def test_bell_state_is_one(self):
        sv = np.array([1, 0, 0, 1], dtype=complex) / np.sqrt(2)
        dm = DensityMatrix(state_vector=sv)
        assert abs(dm.concurrence() - 1.0) < 1e-9
        assert abs(dm.entanglement_of_formation() - 1.0) < 1e-9

    def test_product_state_is_zero(self):
        dm = DensityMatrix(state_vector=np.array([1, 0, 0, 0], dtype=complex))
        assert dm.concurrence() < 1e-9
        assert dm.entanglement_of_formation() < 1e-9

    @pytest.mark.parametrize("seed", range(5))
    def test_pure_state_formula(self, seed):
        # For pure a|00> + b|01> + c|10> + d|11>: C = 2|ad - bc|.
        rng = np.random.default_rng(seed)
        sv = rng.normal(size=4) + 1j * rng.normal(size=4)
        sv = sv / np.linalg.norm(sv)
        dm = DensityMatrix(state_vector=sv)
        expected = 2 * abs(sv[0] * sv[3] - sv[1] * sv[2])
        assert abs(dm.concurrence() - expected) < 1e-9

    @pytest.mark.parametrize("seed", range(4))
    def test_bell_diagonal_closed_form(self, seed):
        # For Bell-diagonal states: C = max(0, 2*max(lam) - 1).
        from quantum_debugger.algorithms import bell_diagonal_state

        rng = np.random.default_rng(seed)
        lams = rng.dirichlet([2, 1, 1, 1])
        dm = DensityMatrix(rho=bell_diagonal_state(*lams))
        expected = max(0.0, 2 * max(lams) - 1)
        assert abs(dm.concurrence() - expected) < 1e-9

    def test_werner_threshold_at_half(self):
        from quantum_debugger.algorithms import werner_state

        assert DensityMatrix(rho=werner_state(0.45)).concurrence() < 1e-12
        c = DensityMatrix(rho=werner_state(0.75)).concurrence()
        assert abs(c - (2 * 0.75 - 1)) < 1e-9  # 2F - 1 for Werner above 1/2

    def test_partially_entangled_pure_state(self):
        theta = 0.5
        sv = np.zeros(4, dtype=complex)
        sv[0], sv[3] = np.cos(theta), np.sin(theta)
        dm = DensityMatrix(state_vector=sv)
        assert abs(dm.concurrence() - np.sin(2 * theta)) < 1e-9
        # EoF equals the entanglement entropy for pure states.
        assert abs(dm.entanglement_of_formation() - dm.entanglement_entropy([0])) < 1e-9

    def test_wrong_size_rejected(self):
        with pytest.raises(ValueError):
            DensityMatrix(1).concurrence()


class TestStinespringDilation:
    @pytest.mark.parametrize("channel", ["depol", "ad", "pd", "bf", "phaseflip"])
    def test_dilation_reproduces_channel(self, channel):
        from quantum_debugger.density_matrix import (
            apply_channel_dilated, depolarizing, amplitude_damping,
            phase_damping, bit_flip, phase_flip,
        )

        kr = {
            "depol": depolarizing(0.3), "ad": amplitude_damping(0.4),
            "pd": phase_damping(0.5), "bf": bit_flip(0.25), "phaseflip": phase_flip(0.15),
        }[channel]
        rho = np.array([[0.7, 0.3 - 0.2j], [0.3 + 0.2j, 0.3]], dtype=complex)
        direct = DensityMatrix(rho=rho.copy())
        direct.apply_channel(kr, [0])
        assert np.allclose(apply_channel_dilated(kr, rho), direct.rho, atol=1e-12)

    @pytest.mark.parametrize("channel", ["depol", "ad", "pd"])
    def test_isometry_is_trace_preserving(self, channel):
        from quantum_debugger.density_matrix import (
            stinespring_isometry, depolarizing, amplitude_damping, phase_damping,
        )

        kr = {"depol": depolarizing(0.3), "ad": amplitude_damping(0.4),
              "pd": phase_damping(0.5)}[channel]
        V = stinespring_isometry(kr)
        assert np.allclose(V.conj().T @ V, np.eye(2), atol=1e-12)

    def test_unitary_dilation_rank_one(self):
        # A unitary channel dilates to itself (env dimension 1).
        from quantum_debugger.density_matrix import stinespring_isometry

        H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
        V = stinespring_isometry([H])
        assert V.shape == (2, 2)
        assert np.allclose(V, H)

    def test_purification_view(self):
        # The dilated global state is pure (an environment purifies the noise).
        from quantum_debugger.density_matrix import stinespring_isometry, depolarizing

        psi = np.array([1, 0], dtype=complex)
        V = stinespring_isometry(depolarizing(0.5))
        big = np.outer(V @ psi, (V @ psi).conj())
        assert abs(np.trace(big @ big).real - 1.0) < 1e-9  # purity 1


class TestProcessTomography:
    def _apply(self, kraus):
        def f(rho):
            dm = DensityMatrix(rho=np.array(rho, dtype=complex))
            dm.apply_channel(kraus, [0])
            return dm.rho
        return f

    @pytest.mark.parametrize("channel", ["depol", "ad", "pd", "bf"])
    def test_recovers_true_choi(self, channel):
        from quantum_debugger.density_matrix import (
            process_tomography, choi_matrix, depolarizing,
            amplitude_damping, phase_damping, bit_flip,
        )

        kr = {"depol": depolarizing(0.3), "ad": amplitude_damping(0.4),
              "pd": phase_damping(0.5), "bf": bit_flip(0.2)}[channel]
        J = process_tomography(self._apply(kr))
        assert np.allclose(J, choi_matrix(kr), atol=1e-9)

    def test_identity_channel(self):
        from quantum_debugger.density_matrix import process_tomography, choi_matrix

        J = process_tomography(lambda r: r)
        assert np.allclose(J, choi_matrix([np.eye(2, dtype=complex)]), atol=1e-9)

    def test_reconstructed_choi_is_cptp(self):
        from quantum_debugger.density_matrix import process_tomography, amplitude_damping

        J = process_tomography(self._apply(amplitude_damping(0.3)))
        # CP: positive semidefinite; TP: partial trace over output = I.
        assert np.linalg.eigvalsh(J).min() > -1e-9
        ptrace = J.reshape(2, 2, 2, 2).trace(axis1=1, axis2=3)
        assert np.allclose(ptrace, np.eye(2), atol=1e-9)

    def test_unitary_channel_recovered(self):
        from quantum_debugger.density_matrix import process_tomography, choi_matrix

        H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
        J = process_tomography(lambda r: H @ np.array(r, dtype=complex) @ H.conj().T)
        assert np.allclose(J, choi_matrix([H]), atol=1e-9)
