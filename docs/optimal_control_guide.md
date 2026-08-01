# Quantum optimal control & pulse engineering

Gates are not fundamental — they are *engineered* by shaping control fields applied to a physical
system. This guide covers the tools for that: piecewise-constant control propagators and GRAPE
(gradient-ascent pulse engineering) for synthesizing a target gate, the dynamical-Lie-algebra test
for whether a system is controllable at all, the quantum speed limits that bound how fast any gate
can run, and the pulse-area theorem behind the standard pulse shapes. Every routine is verified
against a synthesized fidelity, an exact Lie-algebra dimension, a saturated speed-limit bound, or a
rotation unitary.

All functions live under `quantum_debugger.algorithms.<module>`.

## GRAPE: synthesizing a gate from control pulses

With a Hamiltonian `H(t) = H₀ + Σⱼ uⱼ(t) Hⱼ` and piecewise-constant controls, the propagator is a
product of slice exponentials; GRAPE climbs the gate-fidelity landscape using the analytic gradient.

- `optimal_control.piecewise_propagator(H0, controls, control_hams, dt)`,
  `control_hamiltonian(...)`, `slice_propagators(...)`.
- `optimal_control.gate_fidelity(U, target)`, `state_fidelity(psi, target)`.
- `optimal_control.grape_gradient(...)`, `grape_optimize(...)`, `grape_state_transfer(...)`,
  `control_fluence(...)`, `pauli(label)`.

```python
import numpy as np
from quantum_debugger.algorithms.optimal_control import grape_optimize, pauli
H0 = np.zeros((2, 2), dtype=complex)
Hadamard = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
result = grape_optimize(H0, [pauli("X"), pauli("Y")], Hadamard, n_steps=20, iterations=600, seed=2)
round(result["fidelity"], 4)     # -> 1.0   (pulse synthesized to gate fidelity > 0.999)
```

## Controllability: can the target even be reached?

A system is operator controllable iff the control operators generate the full Lie algebra `su(d)`
(dimension `d²−1`) under commutation.

- `controllability.lie_bracket(A, B)`, `lie_closure(generators)`, `dla_dimension(generators)`,
  `su_dimension(d)`, `u_dimension(d)`, `is_controllable(generators, d)`, `gate_reachable(...)`.

```python
from quantum_debugger.algorithms.controllability import dla_dimension, is_controllable
from quantum_debugger.algorithms.optimal_control import pauli
dla_dimension([pauli("X"), pauli("Z")]), is_controllable([pauli("X"), pauli("Z")], 2)
# -> (3, True)    {X, Z} generate su(2) (since [X,Z] ~ Y)
dla_dimension([pauli("Z")]), is_controllable([pauli("Z")], 2)
# -> (1, False)   a single generator is not controllable
```

## Quantum speed limits

There is a minimum time to reach an orthogonal state: the Mandelstam-Tamm bound `(π/2)/ΔE` and the
Margolus-Levitin bound `(π/2)/E`. A resonant qubit precession *saturates* the bound (ℏ = 1).

- `quantum_speed_limit.mean_energy(...)`, `energy_variance(...)`, `energy_uncertainty(...)`.
- `quantum_speed_limit.mandelstam_tamm_time(delta_E, overlap)`, `margolus_levitin_time(...)`,
  `quantum_speed_limit_time(psi0, H, overlap)`, `evolution_overlap(...)`,
  `orthogonalization_time(...)`, `saturates_mandelstam_tamm(...)`.

```python
import numpy as np
from quantum_debugger.algorithms.quantum_speed_limit import (
    orthogonalization_time, mandelstam_tamm_time, energy_uncertainty, saturates_mandelstam_tamm)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
w = 1.7
H = (w / 2) * Z
psi0 = np.array([1, 1], dtype=complex) / np.sqrt(2)         # |+>
round(orthogonalization_time(psi0, H), 4)                   # -> 1.848  (= π/w)
round(mandelstam_tamm_time(energy_uncertainty(psi0, H)), 4) # -> 1.848  (the bound)
saturates_mandelstam_tamm(psi0, H)                          # -> True   (time-optimal)
```

## Pulse shapes & the pulse-area theorem

For a resonant drive the rotation angle equals the pulse *area* — a shape-independent statement, so
an area-π pulse is a bit-flip.

- `pulse_shapes.square_pulse(...)`, `gaussian_pulse(...)`, `drag_pulse(...)`, `pulse_area(...)`,
  `gaussian_area(...)`, `rotation_from_area(...)`, `pi_pulse_amplitude(...)`, `pulse_unitary(...)`,
  `square_pulse_unitary(...)`, `pi_pulse_is_bit_flip(...)`.

```python
import numpy as np
from quantum_debugger.algorithms.pulse_shapes import (
    square_pulse, pi_pulse_amplitude, pulse_area, pulse_unitary, gaussian_area)
env = square_pulse(pi_pulse_amplitude(2.0), 100)
round(pulse_area(env, 2.0 / 100), 4)          # -> 3.1416   (area π, any shape)
round(gaussian_area(0.5, 1.0), 4)             # -> 1.2533   (= amp·σ·√(2π))
from quantum_debugger.algorithms.optimal_control import gate_fidelity, pauli
gate_fidelity(pulse_unitary(np.pi, "X"), pauli("X"))   # -> 1.0   (area-π X pulse == X gate)
```

## What this is verified against

- GRAPE: the synthesized gate fidelity reaches `> 0.999` for X and Hadamard; the analytic gradient
  matches finite differences.
- Controllability: exact Lie-algebra dimensions — `{X, Z}` → `su(2)` (dim 3), a single generator
  → dim 1, full local control plus `ZZ` → `su(4)` (dim 15).
- Speed limits: the actual orthogonalization time of a qubit precession equals the Mandelstam-Tamm
  bound `(π/2)/ΔE` (saturation).
- Pulse shapes: an area-π pulse equals the Pauli-X gate; the Gaussian area matches `amp·σ·√(2π)`.
