# Quantum thermodynamics

Thermodynamics at the quantum scale: Gibbs states and equilibrium free energy, work and heat in
quenches, the nonequilibrium free energy and entropy production, the Jarzynski equality and Crooks
fluctuation theorem, Landauer's erasure bound, the quantum Otto engine, and passive states with
ergotropy (extractable work). The fluctuation theorems and the second law are verified to hold
*exactly* on small systems.

All functions live under `quantum_debugger.algorithms.<module>`.

## Gibbs states, work & heat

- `quantum_thermodynamics.gibbs_state(H, beta)`, `partition_function(H, beta)`,
  `free_energy(H, beta)`, `internal_energy(rho, H)`, `quench_work(rho, H_i, H_f)`,
  `heat_exchanged(rho_i, rho_f, H)`, `nonequilibrium_free_energy(rho, H, beta)`,
  `heat_capacity(H, beta)`, `thermal_entropy(H, beta)`, `entropy_production(...)`.

## Fluctuation theorems

The Jarzynski equality `⟨e^{-βW}⟩ = e^{-βΔF}` holds for arbitrary driving; Landauer's bound is
`kT ln 2` per erased bit.

- `fluctuation_theorems.two_point_work_distribution(H_i, H_f, beta)`,
  `jarzynski_average(...)`, `free_energy_difference(...)`, `verify_jarzynski(...)`,
  `average_work(...)`, `work_variance(...)`, `dissipated_work(...)`, `crooks_ratio(...)`,
  `landauer_bound(n_bits, temperature)`.

```python
import numpy as np
from quantum_debugger.algorithms.fluctuation_theorems import verify_jarzynski, landauer_bound
H_i, H_f = np.diag([0.0, 1.0]), np.diag([0.0, 2.0])
verify_jarzynski(H_i, H_f, beta=1.0)     # -> True    (⟨e^{-βW}⟩ = e^{-βΔF} exactly)
round(landauer_bound(1, temperature=1.0), 4)   # -> 0.6931   (= ln 2)
```

## The quantum Otto engine

A qubit Otto cycle has efficiency `1 - ω_c/ω_h`, always below the Carnot bound `1 - T_c/T_h`.

- `quantum_otto_cycle.otto_cycle(omega_c, omega_h, T_c, T_h)`, `otto_efficiency(omega_c, omega_h)`,
  `carnot_efficiency(T_c, T_h)`, `is_engine(...)`, `efficiency_below_carnot(...)`.

```python
from quantum_debugger.algorithms.quantum_otto_cycle import otto_efficiency, carnot_efficiency
otto_efficiency(omega_c=1.0, omega_h=2.0)   # -> 0.5    (1 - ω_c/ω_h)
carnot_efficiency(T_c=1.0, T_h=4.0)         # -> 0.75   (the second-law ceiling)
```

## Passive states & ergotropy

- `passive_states.passive_state(rho, H)`, `ergotropy(rho, H)` / `max_extractable_work(...)`,
  `bound_energy(rho, H)`, `is_passive(rho, H)`, `gibbs_is_passive(H, beta)` — a Gibbs state stores
  no extractable work.

```python
import numpy as np
from quantum_debugger.algorithms.passive_states import gibbs_is_passive
gibbs_is_passive(np.diag([0.0, 1.0, 2.0]), beta=0.7)   # -> True   (equilibrium = zero ergotropy)
```

## What this is verified against

- Fluctuation theorems: the Jarzynski equality holds to machine precision; Landauer `= ln 2` at
  `T = 1`.
- Second law: entropy production `≥ 0`, dissipated work `≥ 0`, Otto efficiency `≤` Carnot.
- Passive states: ergotropy `+` bound energy `= ⟨H⟩`; the Gibbs state is exactly passive.
