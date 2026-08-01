"""Quantum optimal control & pulse engineering (v3.2.0) -- verification tests.

Checks GRAPE synthesis (fidelity -> 1), the GRAPE gradient vs finite differences, Lie-algebra
controllability, quantum-speed-limit saturation, and the pulse-area theorem.
"""
import numpy as np
import pytest

from quantum_debugger.algorithms.optimal_control import (
    piecewise_propagator, gate_fidelity, state_fidelity, grape_gradient,
    grape_optimize, grape_state_transfer, control_fluence, pauli,
)
from quantum_debugger.algorithms.controllability import (
    lie_bracket, dla_dimension, is_controllable, su_dimension,
)
from quantum_debugger.algorithms.quantum_speed_limit import (
    energy_uncertainty, mandelstam_tamm_time, margolus_levitin_time,
    quantum_speed_limit_time, orthogonalization_time, saturates_mandelstam_tamm,
)
from quantum_debugger.algorithms.pulse_shapes import (
    square_pulse, gaussian_pulse, gaussian_area, pulse_area, pulse_unitary,
    pi_pulse_amplitude, pi_pulse_is_bit_flip,
)

X = pauli("X")
Y = pauli("Y")
Z = pauli("Z")
H0 = np.zeros((2, 2), dtype=complex)


def test_grape_gradient_matches_finite_difference():
    chams = [X, Y]
    dt = np.pi / 10
    rng = np.random.default_rng(3)
    controls = 0.2 * rng.standard_normal((10, 2))
    g = grape_gradient(H0, controls, chams, dt, X)
    fd = np.zeros_like(controls)
    eps = 1e-6
    for k in range(controls.shape[0]):
        for j in range(2):
            cp, cm = controls.copy(), controls.copy()
            cp[k, j] += eps
            cm[k, j] -= eps
            fp = gate_fidelity(piecewise_propagator(H0, cp, chams, dt), X)
            fm = gate_fidelity(piecewise_propagator(H0, cm, chams, dt), X)
            fd[k, j] = (fp - fm) / (2 * eps)
    assert np.max(np.abs(g - fd)) < 1e-2


def test_grape_synthesizes_x_gate():
    r = grape_optimize(H0, [X, Y], X, n_steps=20, T=np.pi, iterations=400, seed=1)
    assert r["fidelity"] > 0.999


def test_grape_synthesizes_hadamard():
    Had = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
    r = grape_optimize(H0, [X, Y], Had, n_steps=20, T=np.pi, iterations=600, seed=2)
    assert r["fidelity"] > 0.999


def test_grape_state_transfer():
    r = grape_state_transfer(H0, [X, Y], np.array([1, 0], dtype=complex),
                             np.array([0, 1], dtype=complex), n_steps=20, iterations=400, seed=4)
    assert r["fidelity"] > 0.999


def test_control_fluence_positive():
    assert control_fluence(np.array([[1.0, -1.0], [0.5, 0.0]]), 0.1) == pytest.approx(0.225)


def test_lie_bracket():
    assert np.allclose(lie_bracket(X, Z), X @ Z - Z @ X)


def test_qubit_controllable_with_x_z():
    assert dla_dimension([X, Z]) == 3
    assert su_dimension(2) == 3
    assert is_controllable([X, Z], 2)


def test_single_generator_not_controllable():
    assert dla_dimension([Z]) == 1
    assert not is_controllable([Z], 2)


def test_two_qubit_universal_set():
    I = np.eye(2, dtype=complex)
    gens = [np.kron(X, I), np.kron(Z, I), np.kron(I, X), np.kron(I, Z), np.kron(Z, Z)]
    assert dla_dimension(gens) == 15  # su(4)
    assert is_controllable(gens, 4)


def test_mandelstam_tamm_orthogonal():
    # (pi/2)/dE for orthogonality
    assert mandelstam_tamm_time(2.0, overlap=0.0) == pytest.approx(np.pi / 4)


def test_qsl_saturated_by_precession():
    w = 1.7
    H = (w / 2) * Z
    psi0 = np.array([1, 1], dtype=complex) / np.sqrt(2)  # |+>
    assert energy_uncertainty(psi0, H) == pytest.approx(w / 2)
    assert orthogonalization_time(psi0, H) == pytest.approx(np.pi / w, abs=1e-2)
    assert saturates_mandelstam_tamm(psi0, H)


def test_qsl_time_is_tighter_bound():
    w = 1.7
    H = (w / 2) * Z
    psi0 = np.array([1, 1], dtype=complex) / np.sqrt(2)
    t = quantum_speed_limit_time(psi0, H, overlap=0.0)
    assert t == pytest.approx(np.pi / w, abs=1e-6)


def test_pulse_area_theorem():
    assert pi_pulse_is_bit_flip("X")
    assert gate_fidelity(pulse_unitary(np.pi, "X"), X) == pytest.approx(1.0, abs=1e-9)


def test_square_pi_pulse_area():
    env = square_pulse(pi_pulse_amplitude(2.0), 100)
    assert pulse_area(env, 2.0 / 100) == pytest.approx(np.pi, abs=1e-6)


def test_gaussian_area_matches_analytic():
    ts = np.linspace(-6, 6, 6000)
    numeric = pulse_area(gaussian_pulse(ts, 0.0, 0.5, 1.0), 12 / 6000)
    assert numeric == pytest.approx(gaussian_area(0.5, 1.0), abs=1e-2)
