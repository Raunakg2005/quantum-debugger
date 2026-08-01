# Open quantum systems & Lindblad dynamics

Real quantum systems are never perfectly isolated — coupling to an environment makes them lose
energy (relaxation) and coherence (decoherence). This guide covers the tools for open-system
dynamics: the Lindblad (GKSL) master equation and its Liouvillian superoperator, quantum-trajectory
unravelings, non-Markovianity (memory) measures, collision-model thermalization, and closed-form
qubit T1/T2 relaxation. Every routine is checked against an exact channel, the analytic steady
state, or Bloch decay.

All functions live under `quantum_debugger.algorithms.<module>`.

## The Lindblad master equation

Vectorizing the density matrix turns the master equation into a linear system
`d vec(ρ)/dt = L vec(ρ)`, so the evolution is a matrix exponential `ρ(t) = unvec(e^{Lt} vec ρ₀)`.

- `lindblad.lindbladian(H, jump_ops)`, `evolve_lindblad(H, jump_ops, rho0, t)`,
  `lindblad_derivative(...)`, `dissipator_superoperator(L)`, `apply_dissipator(L, rho)`,
  `vectorize` / `unvectorize`, `left_multiply` / `right_multiply`.
- `lindblad.amplitude_damping_jump(gamma)` (T1) and `dephasing_jump(gamma)` (T2) jump operators.
- `lindblad.steady_state(...)`, `liouvillian_spectrum(...)`, `spectral_gap(...)`,
  `is_trace_preserving(...)`.

```python
import numpy as np
from quantum_debugger.algorithms.lindblad import (
    evolve_lindblad, steady_state, spectral_gap, amplitude_damping_jump)
H = np.zeros((2, 2), dtype=complex)
plus = 0.5 * np.ones((2, 2), dtype=complex)          # |+><+|
rho = evolve_lindblad(H, [amplitude_damping_jump(0.7)], plus, t=1.3)
round(rho[1, 1].real, 4)                              # -> 0.2013   (= 0.5 e^{-γt})
np.allclose(steady_state(H, [amplitude_damping_jump(0.7)]), np.diag([1, 0]))   # -> True
round(spectral_gap(H, [amplitude_damping_jump(0.7)]), 3)   # -> 0.35   (relaxation rate = γ/2)
```

## Quantum trajectories (Monte Carlo wavefunction)

The master equation can be *unraveled* into stochastic pure-state trajectories: the state evolves
under a non-Hermitian effective Hamiltonian punctuated by random quantum jumps. Averaging
`|ψ⟩⟨ψ|` over many trajectories reproduces `ρ(t)`.

- `quantum_trajectories.effective_hamiltonian(H, jump_ops)`, `jump_rates(psi, jump_ops)`,
  `quantum_jump_trajectory(...)`, `trajectory_ensemble(...)`, `trajectory_lindblad_error(...)`,
  `mean_photon_emissions(...)`.

```python
import numpy as np
from quantum_debugger.algorithms.quantum_trajectories import trajectory_lindblad_error
from quantum_debugger.algorithms.lindblad import amplitude_damping_jump
H = np.array([[0, 0], [0, 1]], dtype=complex)
psi0 = np.array([0, 1], dtype=complex)               # excited |1>
err = trajectory_lindblad_error(H, [amplitude_damping_jump(0.8)], psi0, 1.0,
                                n_traj=800, steps=150, seed=1)
round(err, 3)                                        # -> ~0.02   (converges to the exact ρ(t))
```

## Non-Markovianity (memory effects)

Markovian (memoryless) dynamics can only *lose* distinguishability; when the environment feeds
information back, the trace distance revives. The Breuer-Laine-Piilo measure sums that backflow —
zero for Markovian dynamics, positive otherwise.

- `nonmarkovianity.coherence_trace_distance(coherence_values)` (equals `|c(t)|`),
  `markovian_coherence(...)`, `nonmarkovian_coherence(...)`, `blp_measure(...)`,
  `is_markovian(...)`, `revival_count(...)`, `distinguishability_backflow(...)`.

```python
import numpy as np
from quantum_debugger.algorithms.nonmarkovianity import (
    coherence_trace_distance, markovian_coherence, nonmarkovian_coherence,
    blp_measure, revival_count)
ts = np.linspace(0, 6, 400)
blp_measure(coherence_trace_distance(markovian_coherence(ts, 1.0)))          # -> 0.0
D = coherence_trace_distance(nonmarkovian_coherence(ts, 0.5, 3.0))
round(blp_measure(D), 3), revival_count(D)                                    # -> (1.378, 6)
```

## Collision models & thermalization

Dissipation can be built from repeated unitary *collisions* with fresh environment ancillas. The
ancilla state is the unique fixed point — so a stream of thermal ancillas drives the system to the
Gibbs state.

- `collision_model.partial_swap(theta)`, `thermal_qubit(beta, omega)`, `collision_step(...)`,
  `repeated_collisions(...)`, `thermalize(...)`, `fixed_point_error(...)`,
  `full_swap_is_one_step(...)`.

```python
import numpy as np
from quantum_debugger.algorithms.collision_model import thermal_qubit, thermalize
sigma = thermal_qubit(beta=0.8, omega=1.0)
final = thermalize(np.diag([1.0, 0.0]).astype(complex), 0.8, 1.0, theta=0.3, n=400)
np.allclose(final, sigma, atol=1e-3)                 # -> True   (relaxes to the Gibbs state)
```

## Qubit relaxation: T1, T2 and the Bloch picture

For a qubit the dynamics reduces to a closed form: transverse Bloch components decay as `e^{-t/T2}`,
the longitudinal component relaxes as `e^{-t/T1}`, with `1/T2 = 1/(2T1) + 1/Tφ` and `T2 ≤ 2T1`.

- `open_qubit.bloch_vector`, `density_from_bloch`, `t2_from_t1_tphi`, `t2_upper_bound`,
  `relaxation_times(gamma_1, gamma_phi)`, `bloch_decay(...)`, `bloch_decay_matches_lindblad(...)`,
  `purity`.

```python
from quantum_debugger.algorithms.open_qubit import relaxation_times, bloch_decay_matches_lindblad
{k: round(v, 3) for k, v in relaxation_times(0.5, 0.2).items()}
# -> {'T1': 2.0, 'T_phi': 5.0, 'T2': 2.222}
bloch_decay_matches_lindblad((0.6, 0.3, -0.5), t=1.4, gamma_1=0.5, gamma_phi=0.3)   # -> True
```

## What this is verified against

- Lindblad evolution: the exact amplitude-damping / dephasing channels; the analytic steady state
  `|0⟩⟨0|`; every Liouvillian eigenvalue with `Re ≤ 0`; trace preservation.
- Trajectories: the ensemble average converges to the exact `ρ(t)` (trace distance < 0.05); mean
  emissions match `1 − e^{−γt}`.
- Non-Markovianity: the `|+⟩/|−⟩` trace distance equals `|c(t)|`; Markovian decay scores 0, a
  reviving coherence scores positive backflow.
- Collision models: the ancilla state is the exact fixed point; thermal ancillas reach the Gibbs
  state.
- Qubit relaxation: the closed-form Bloch decay matches the exact Lindblad evolution.
