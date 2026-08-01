# Many-body physics

Tools for quantum many-body models and their signatures: topological phases (Kitaev, SSH),
the Fermi-Hubbard model, quantum phase transitions, entanglement dynamics, spatial
correlations, spectral (level) statistics, quench dynamics, out-of-time-order correlators
(scrambling), and thermal (Gibbs) properties. Every routine is checked against an exact result
— an exact diagonalization, an analytic dimer/limit, or a universal reference value.

All functions live under `quantum_debugger.algorithms.<module>`.

## Topological phases: Kitaev chain & SSH model

The Kitaev wire and the Su-Schrieffer-Heeger chain are the canonical 1D topological models,
diagnosed by edge modes and a bulk invariant.

- `kitaev_chain.kitaev_chain_hamiltonian(n, mu, t, delta)` — the BdG Hamiltonian.
- `kitaev_chain.kitaev_ground_degeneracy(n, mu, t, delta)` — ground-state splitting, bulk gap,
  and a topological flag.
- `ssh_model.ssh_hamiltonian(cells, v, w)`, `ssh_winding_number(v, w)`,
  `ssh_zero_modes(cells, v, w)`, `ssh_edge_polarization(cells, v, w)`.

```python
from quantum_debugger.algorithms.kitaev_chain import kitaev_ground_degeneracy
from quantum_debugger.algorithms.ssh_model import ssh_winding_number, ssh_zero_modes

kitaev_ground_degeneracy(6, mu=0.0, t=1.0, delta=1.0)
# -> {'splitting': 5.3e-15, 'bulk_gap': 2.0, 'topological': True, 'nearly_degenerate': True}
kitaev_ground_degeneracy(6, mu=3.0, t=1.0, delta=1.0)['topological']   # -> False

ssh_winding_number(0.5, 1.0), ssh_winding_number(1.0, 0.5)   # -> (1, 0)
ssh_zero_modes(6, v=0.5, w=1.0)                              # -> 2  (a pair of edge modes)
```

The topological phase (`|w| > |v|`, or small `mu`) shows a near-zero ground-state splitting and
a protected pair of edge modes; the trivial phase does not.

## The Fermi-Hubbard model

- `hubbard.fermi_hubbard_hamiltonian(n_sites, t, u, periodic)` — the full second-quantized model.
- `hubbard.hubbard_ground_energy(n_sites, t, u, n_particles, periodic)` — exact ground energy.
- `hubbard.hubbard_dimer_energy(t, u)` — the exactly-solvable half-filled two-site dimer.

```python
from quantum_debugger.algorithms.hubbard import hubbard_dimer_energy
hubbard_dimer_energy(t=1.0, u=0.0)   # -> {'ground_energy': -2.0,  'analytic': -2.0,  ...}
hubbard_dimer_energy(t=1.0, u=4.0)   # -> {'ground_energy': -0.828, 'analytic': -0.828, ...}
```

The numeric ground energy matches the analytic dimer formula `(U - sqrt(U^2 + 16 t^2))/2`.

## Phase transitions, correlations & entanglement dynamics

- `quantum_phase_transition.tfim_critical_field(n)`, `ground_state_fidelity(...)`,
  `fidelity_susceptibility(...)` — locate the TFIM critical point from a fidelity dip.
- `many_body_correlations.connected_correlation(state, i, j, op)`,
  `correlation_length(state, op)`, `structure_factor(state, k, op)`.
- `entanglement_growth.entanglement_growth(hamiltonian, initial_state, region, times)` — track
  entropy growth after a quench.

## Spectral statistics: chaos vs integrability

The mean adjacent-gap ratio `<r>` distinguishes an integrable (Poisson, `<r> ~ 0.386`) spectrum
from a chaotic (GOE, `<r> ~ 0.53`) one.

- `level_statistics.level_spacing_ratio(eigenvalues)`, `classify_spectrum(eigenvalues)`,
  `poisson_reference(...)`, `goe_reference(...)`.

## Quenches, scrambling & thermal states

- `loschmidt.loschmidt_echo(...)`, `rate_function(...)`, `quench_dynamics(...)` — dynamical
  quantum phase transitions.
- `otoc.otoc(hamiltonian, w_op, v_op, times)`, `scrambling_time(...)` — information scrambling.
- `thermal.gibbs_state(hamiltonian, beta)`, `partition_function(...)`,
  `thermal_properties(hamiltonian, beta)`.

## What this is verified against

- Kitaev/SSH: the analytic topological criteria (`|w|>|v|`; the `mu < 2t` phase boundary) and
  exact edge-mode counting.
- Hubbard: the exact two-site dimer formula and small-system exact diagonalization.
- Level statistics: the universal Poisson (`0.386`) and GOE (`0.53`) values of `<r>`.
- Correlations, quenches, OTOC, thermal: direct exact time evolution / exact Gibbs traces.
