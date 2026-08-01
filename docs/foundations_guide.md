# Quantum foundations & nonlocality

The experiments and inequalities that separate quantum mechanics from any local-hidden-variable
theory: the CHSH/Bell inequality and Tsirelson's bound, PR boxes and the no-signaling principle,
multiparty Mermin inequalities, EPR steering, device-independent randomness certification,
Kochen-Specker contextuality, and uncertainty relations. Bounds are checked by brute force over
local strategies and by exact eigenvalue computation.

All functions live under `quantum_debugger.algorithms.<module>`.

## CHSH & Tsirelson's bound

A local theory obeys `S ≤ 2`; quantum mechanics reaches `2√2` (Tsirelson); a no-signaling PR box
reaches the algebraic maximum `4`.

- `bell_inequalities.chsh_value(state, ...)`, `chsh_violation(state)`, `tsirelson_bound()`,
  `classical_chsh_bound()`, `algebraic_bound()`, `correlator(...)`, `bell_state(kind)`.
- `nonlocality.chsh_maximum(rho)` (Horodecki closed form), `chsh_maximum_optimized(...)`,
  `correlation_matrix(rho)`, `werner_nonlocality(F)`.

```python
from quantum_debugger.algorithms.bell_inequalities import tsirelson_bound, chsh_value, bell_state, classical_chsh_bound
round(tsirelson_bound(), 4)          # -> 2.8284   (2√2)
round(chsh_value(bell_state()), 4)   # -> 2.8284   (a Bell state saturates it)
classical_chsh_bound()               # -> 2        (brute-forced LHV maximum)
```

## PR boxes & no-signaling

- `pr_box.pr_box_correlations()`, `chsh_from_box(box)`, `correlation_value(box, x, y)`,
  `is_no_signaling(box)`, `pr_box_is_superquantum()`, `local_deterministic_box(a_func, b_func)`.

```python
from quantum_debugger.algorithms.pr_box import pr_box_is_superquantum, chsh_from_box, pr_box_correlations
pr_box_is_superquantum()                    # -> True
chsh_from_box(pr_box_correlations())        # -> 4.0   (above Tsirelson, still no-signaling)
```

## Multiparty nonlocality, steering & device independence

The Mermin-Klyshko violation grows exponentially, `2^{(n-1)/2}`, with the number of parties.

- `mermin_multiparty.mermin_operator(n)`, `mermin_value(state, n)`, `mermin_optimal_value(n)`,
  `mermin_violation_ratio(n)`, `ghz_state(n)`.
- `steering.steering_value(rho)`, `is_steerable(rho)`, `werner_steering_threshold()`.
- `device_independent.certified_randomness(chsh)`, `guessing_probability(chsh)`,
  `di_key_rate(chsh)`, `is_randomness_certified(chsh)`.

```python
from quantum_debugger.algorithms.mermin_multiparty import mermin_violation_ratio
mermin_violation_ratio(3)   # -> 2.0   (= 2^{(3-1)/2}: exponential multiparty violation)
```

## Contextuality & uncertainty

- `contextuality.mermin_peres_square()`, `classical_assignment_maximum()`,
  `quantum_context_measurement(state, context, index)`.
- `uncertainty.robertson_bound(A, B, state)`, `entropic_uncertainty(A, B, state)`;
  `bell_test.chsh_game(...)`, `mermin_ghz_test()`.

## What this is verified against

- CHSH: the brute-forced classical bound `2`, the quantum Tsirelson bound `2√2`, and the algebraic
  `4`.
- PR box: no-signaling holds while CHSH `= 4` exceeds Tsirelson.
- Mermin: the `2^{(n-1)/2}` violation ratio from the exact operator spectrum.
- Contextuality: the Mermin-Peres magic square's algebraic contradiction.
