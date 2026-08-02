# The ZX-calculus

The ZX-calculus is a diagrammatic language for qubit quantum computing: circuits become graphs of
**Z-spiders** (green) and **X-spiders** (red), and a small set of **rewrite rules** simplifies them
while provably preserving the linear map they denote. It underlies modern circuit optimization,
measurement-based computing, and error-correction reasoning. This guide covers the spiders and their
matrix semantics, the core rewrite rules, the standard gate set as diagrams, and phase gadgets —
every claim checked against the exact matrix (ZX rules hold up to a scalar, which the checks
account for).

All functions live under `quantum_debugger.algorithms.<module>`.

## Spiders

A Z-spider is `|0…0⟩⟨0…0| + e^{iα}|1…1⟩⟨1…1|`; an X-spider is the same in the `|+⟩/|−⟩` basis
(Hadamards on every leg).

- `zx_spiders.z_spider_tensor(m, n, phase)`, `z_spider_matrix(...)`,
  `x_spider_tensor(...)`, `x_spider_matrix(...)`, `spider_to_matrix(...)`.
- `zx_spiders.hadamard_matrix()`, `is_hadamard_self_inverse()`, `green_phase(phase)`,
  `red_phase(phase)`.

```python
import numpy as np
from quantum_debugger.algorithms.zx_spiders import z_spider_matrix, x_spider_matrix
np.allclose(z_spider_matrix(1, 1, np.pi), np.diag([1, -1]))   # -> True  (Z(1,1,π) = Pauli Z)
np.allclose(x_spider_matrix(1, 1, np.pi), [[0, 1], [1, 0]])   # -> True  (X(1,1,π) = Pauli X)
```

## Rewrite rules

Each rule is a matrix identity: the two sides of the rewrite denote the same map.

- `zx_rewrite.spider_fusion_z(a, b)`, `spider_fusion_x(...)`, `spider_fusion_multi(...)`,
  `identity_rule()`, `color_change_rule(m, n, phase)`, `copy_rule()`, `pi_copy_rule(...)`,
  `hopf_rule()`.

```python
from quantum_debugger.algorithms.zx_rewrite import spider_fusion_z, color_change_rule, copy_rule
spider_fusion_z(0.7, 1.1)        # -> True   connected green spiders fuse, phases add
color_change_rule(2, 1, 0.6)     # -> True   X = H^⊗n Z H^⊗m
copy_rule()                      # -> True   the Z-spider copies |0>,|1>
```

## Gates as ZX diagrams

Every Clifford+T gate is a spider; the two-qubit entanglers are spiders joined by wires. Diagrams
equal the unitary up to a scalar, restored here.

- `zx_gates.hadamard_gate()`, `z_phase_gate(α)`, `x_phase_gate(α)`, `z_gate()`, `x_gate()`,
  `s_gate()`, `t_gate()`, `cnot_zx()`, `cz_zx()`, `gate_equals(U, target)`, `cnot_zx_is_cnot()`,
  `cz_zx_is_cz()`.

```python
from quantum_debugger.algorithms.zx_gates import cnot_zx_is_cnot, cz_zx_is_cz
cnot_zx_is_cnot(), cz_zx_is_cz()    # -> (True, True)   CNOT and CZ built from spiders
```

## Phase gadgets

A phase gadget applies `exp(−i(α/2) Z⊗Z⊗…⊗Z)` — a parity-dependent phase — built from a CNOT ladder
around a single `Rz`.

- `phase_gadgets.zz_gadget(α)`, `zz_phase_exact(α)`, `phase_gadget(n, α)`, `phase_gadget_exact(n, α)`,
  `gadget_matches_exact(n, α)`.

```python
from quantum_debugger.algorithms.phase_gadgets import gadget_matches_exact
gadget_matches_exact(3, 0.6)     # -> True   the CNOT-ladder gadget == exp(−i(α/2) Z⊗Z⊗Z)
```

## What this is verified against

- Spiders: `Z(1,1,π)` and `X(1,1,π)` equal the Pauli gates; the Hadamard box is self-inverse.
- Rewrite rules: each is an exact matrix identity — spider fusion, identity, colour change, copy,
  pi-commutation (up to the ZX scalar), and Hopf.
- Gates: the ZX CNOT and CZ diagrams equal the textbook unitaries (little-endian); the Clifford+T
  spiders equal their gates.
- Phase gadgets: the CNOT-ladder construction matches `exp(−i(α/2) Z^{⊗n})` for n up to 4.
