"""Open quantum systems & Lindblad dynamics (v3.1.0) -- verification tests.

Each test checks a routine against an exact reference: the analytic amplitude-damping/dephasing
channels, the closed-form steady state, the Lindblad density matrix, and Bloch T1/T2 decay.
"""
import numpy as np
import pytest

from quantum_debugger.algorithms.lindblad import (
    vectorize, unvectorize, lindbladian, lindblad_derivative, evolve_lindblad,
    is_trace_preserving, liouvillian_spectrum, spectral_gap, steady_state,
    amplitude_damping_jump, dephasing_jump,
)
from quantum_debugger.algorithms.quantum_trajectories import (
    effective_hamiltonian, trajectory_lindblad_error, mean_photon_emissions,
)
from quantum_debugger.algorithms.nonmarkovianity import (
    coherence_trace_distance, markovian_coherence, nonmarkovian_coherence,
    blp_measure, is_markovian, revival_count,
)
from quantum_debugger.algorithms.collision_model import (
    thermal_qubit, full_swap_is_one_step, fixed_point_error, thermalize,
)
from quantum_debugger.algorithms.open_qubit import (
    bloch_vector, density_from_bloch, t2_upper_bound, relaxation_times,
    bloch_decay, bloch_decay_matches_lindblad,
)

H0 = np.zeros((2, 2), dtype=complex)


def test_vectorize_roundtrip():
    rho = np.array([[0.6, 0.2 - 0.1j], [0.2 + 0.1j, 0.4]], dtype=complex)
    assert np.allclose(unvectorize(vectorize(rho), 2), rho)


def test_superoperator_matches_direct_derivative():
    g = 0.7
    H = np.array([[0.3, 0.1], [0.1, -0.2]], dtype=complex)
    rho = np.array([[0.6, 0.2 - 0.1j], [0.2 + 0.1j, 0.4]], dtype=complex)
    d_super = unvectorize(lindbladian(H, [amplitude_damping_jump(g)]) @ vectorize(rho), 2)
    d_direct = lindblad_derivative(H, [amplitude_damping_jump(g)], rho)
    assert np.allclose(d_super, d_direct)


def test_amplitude_damping_matches_analytic():
    g, t = 0.7, 1.3
    plus = 0.5 * np.ones((2, 2), dtype=complex)
    rho = evolve_lindblad(H0, [amplitude_damping_jump(g)], plus, t)
    assert rho[1, 1].real == pytest.approx(0.5 * np.exp(-g * t), abs=1e-6)
    assert abs(rho[0, 1]) == pytest.approx(0.5 * np.exp(-g * t / 2), abs=1e-6)
    assert np.trace(rho).real == pytest.approx(1.0, abs=1e-9)


def test_dephasing_matches_analytic():
    g, t = 0.7, 1.3
    plus = 0.5 * np.ones((2, 2), dtype=complex)
    rho = evolve_lindblad(H0, [dephasing_jump(g)], plus, t)
    assert abs(rho[0, 1]) == pytest.approx(0.5 * np.exp(-g * t), abs=1e-6)
    assert rho[1, 1].real == pytest.approx(0.5, abs=1e-9)  # populations unchanged


def test_steady_state_is_ground_state():
    ss = steady_state(H0, [amplitude_damping_jump(0.9)])
    assert np.allclose(ss, np.diag([1.0, 0.0]), atol=1e-6)


def test_liouvillian_spectrum_nonpositive_and_gap():
    ev = liouvillian_spectrum(H0, [amplitude_damping_jump(0.7)])
    assert np.all(ev.real <= 1e-9)
    # AD coherence decays at gamma/2 -- the slowest nonzero mode
    assert spectral_gap(H0, [amplitude_damping_jump(0.7)]) == pytest.approx(0.35, abs=1e-6)


def test_trace_preserving_flag():
    assert is_trace_preserving(H0, [amplitude_damping_jump(0.5), dephasing_jump(0.3)])


def test_effective_hamiltonian_non_hermitian():
    Heff = effective_hamiltonian(H0, [amplitude_damping_jump(1.0)])
    assert not np.allclose(Heff, Heff.conj().T)  # dissipation makes it non-Hermitian


def test_trajectory_ensemble_converges_to_lindblad():
    H = np.array([[0.0, 0.0], [0.0, 1.0]], dtype=complex)
    psi0 = np.array([0.0, 1.0], dtype=complex)
    err = trajectory_lindblad_error(H, [amplitude_damping_jump(0.8)], psi0, 1.0,
                                    n_traj=800, steps=150, seed=1)
    assert err < 0.05


def test_mean_emissions_matches_jump_probability():
    H = np.array([[0.0, 0.0], [0.0, 1.0]], dtype=complex)
    psi0 = np.array([0.0, 1.0], dtype=complex)
    g, t = 0.8, 1.0
    m = mean_photon_emissions(H, [amplitude_damping_jump(g)], psi0, t, n_traj=800, steps=150, seed=2)
    assert m == pytest.approx(1 - np.exp(-g * t), abs=0.05)


def test_blp_trace_distance_equals_coherence():
    ts = np.linspace(0, 6, 400)
    c = markovian_coherence(ts, 1.0)
    assert np.allclose(coherence_trace_distance(c), np.abs(c))


def test_markovian_has_no_backflow():
    ts = np.linspace(0, 6, 400)
    D = coherence_trace_distance(markovian_coherence(ts, 1.0))
    assert blp_measure(D) == pytest.approx(0.0, abs=1e-6)
    assert is_markovian(D)


def test_nonmarkovian_has_backflow():
    ts = np.linspace(0, 6, 400)
    D = coherence_trace_distance(nonmarkovian_coherence(ts, 0.5, 3.0))
    assert blp_measure(D) > 0.1
    assert not is_markovian(D)
    assert revival_count(D) >= 1


def test_full_swap_replaces_system():
    sigma = thermal_qubit(0.8, 1.0)
    assert full_swap_is_one_step(np.diag([1.0, 0.0]).astype(complex), sigma)


def test_partial_swap_fixed_point_is_ancilla():
    sigma = thermal_qubit(0.8, 1.0)
    assert fixed_point_error(np.diag([1.0, 0.0]).astype(complex), sigma, theta=0.3, n=300) < 1e-4


def test_collisions_thermalize_to_gibbs():
    sigma = thermal_qubit(0.8, 1.0)
    final = thermalize(np.diag([1.0, 0.0]).astype(complex), 0.8, 1.0, theta=0.3, n=400)
    assert np.allclose(final, sigma, atol=1e-3)


def test_bloch_roundtrip():
    r = np.array([0.3, -0.4, 0.5])
    assert np.allclose(bloch_vector(density_from_bloch(r)), r)


def test_t2_bound_and_relations():
    assert t2_upper_bound(2.0) == 4.0
    times = relaxation_times(0.5, 0.2)
    assert times["T1"] == pytest.approx(2.0)
    assert times["T2"] == pytest.approx(1.0 / (0.25 + 0.2))


def test_bloch_decay_matches_lindblad():
    assert bloch_decay_matches_lindblad((0.6, 0.3, -0.5), 1.4, 0.5)
    assert bloch_decay_matches_lindblad((0.6, 0.3, -0.5), 1.4, 0.5, 0.3)
