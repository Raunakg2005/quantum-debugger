# Topological codes & fault tolerance

Fault-tolerant quantum computing needs codes that scale (surface, toric, color, and general CSS
codes), a way to push the logical error rate down (concatenation and thresholds), and a
fault-tolerant gate set (transversal gates plus magic-state distillation, Clifford+T synthesis,
and gate teleportation). Every construction here is checked against an exact stabilizer /
code-space computation or a closed-form threshold.

All functions live under `quantum_debugger.algorithms.<module>`.

## The CSS framework and surface/color codes

- `css_code.css_from_classical(H)`, `hypergraph_product(H1, H2)`, plus GF(2) linear algebra
  (`gf2_rank`, `gf2_nullspace`, `gf2_rref`).
- `surface_code.planar_surface_code(d)` → a `CSSCode`, `surface_code_parameters(d)`,
  `corrects_all_errors_up_to(code, weight)` (exhaustive decoder check).
- `color_code.steane_color_code()`, `is_self_dual_css(code)`, `transversal_cnot_valid(code)`,
  `transversal_hadamard_valid(code)`.

```python
from quantum_debugger.algorithms.surface_code import surface_code_parameters
surface_code_parameters(3)   # -> {'n': 13, 'k': 1, 'd': 3}   (distance-3 planar code)
```

## Small codes: Steane [[7,1,3]] and the 5-qubit perfect code

- `steane_code.steane_code(alpha, beta, error)`, `steane_stabilizers()`,
  `steane_transversal(gate, ...)`, `steane_transversal_cnot(...)`, `steane_code_noisy(p, ...)`.
- `perfect_code.five_qubit_code(alpha, beta, error)`, `five_qubit_stabilizers()`.

## Concatenation & thresholds

Below the pseudothreshold, each level of concatenation squares the error, giving a
double-exponential suppression.

- `concatenation.one_level_logical_error(p, A)` (`A p^2`), `concatenated_logical_error(p, levels)`,
  `pseudothreshold(A)`, `levels_for_target(p, target)`, `qubit_overhead(levels)`,
  `double_exponential_check(...)`.

```python
from quantum_debugger.algorithms.concatenation import pseudothreshold, concatenated_logical_error
pseudothreshold(1.0)                          # -> 1.0
concatenated_logical_error(0.001, levels=3)   # -> 1e-24   (p -> A p^2, three times)
```

## Transversal gates & the Eastin-Knill barrier

Transversal gates are automatically fault-tolerant, but no code has a transversal *universal*
gate set (Eastin-Knill) — hence magic states.

- `transversal_gates.transversal_gate(gate, n)`, `preserves_code_space(gate)`,
  `logical_action(gate)`, `steane_transversal_hadamard_is_logical_h()`,
  `steane_transversal_s_is_logical_phase()`, `eastin_knill_obstruction()`.

## Magic-state distillation

- `magic_states.t_state()`, `h_magic_state()`, `stabilizer_fidelity(state)`,
  `distillation_15to1_error(p)`, `distillation_threshold()` (`1/sqrt(35) ≈ 0.169`),
  `distillation_rounds_to_target(p, target)`; `magic_state.inject_t_gate(...)`.

```python
from quantum_debugger.algorithms.magic_states import distillation_threshold, distillation_15to1_error
round(distillation_threshold(), 3)     # -> 0.169
distillation_15to1_error(0.01)         # -> 3.5e-05   (35 p^3 at leading order)
```

## Synthesis & gate teleportation

- `clifford_t_synthesis.synthesize_rz(angle, max_length)`, `t_count(word)`, `gate_distance(U, V)`.
- `two_qubit_synthesis.cnot_count(U)` (0–3, via Makhlin invariants), `makhlin_invariants(U)`,
  `locally_equivalent(U, V)`, `is_local(U)`.
- `gate_teleportation.gate_teleportation(U, psi)`, `t_injection(psi)`;
  `multicontrol.toffoli_gates(...)`, `mcx_gates(...)`, `fredkin_gates(...)`.

```python
import numpy as np
from quantum_debugger.algorithms.two_qubit_synthesis import cnot_count
CNOT = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]], dtype=complex)
SWAP = np.array([[1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1]], dtype=complex)
cnot_count(CNOT), cnot_count(SWAP)     # -> (1, 3)   (a SWAP costs three CNOTs)
```

## What this is verified against

- CSS/surface/color codes: exact stabilizer commutation, `[[n,k,d]]` parameters, and exhaustive
  small-weight decoding.
- Concatenation: the closed-form `p_th (p/p_th)^{2^levels}` double-exponential.
- Transversal gates: the exact logical action on the code words, and the Eastin-Knill obstruction.
- Magic states: the `1/sqrt(35)` distillation threshold and `35 p^3` output error.
- Synthesis: the Shende-Bullock-Markov CNOT count from Makhlin invariants.
