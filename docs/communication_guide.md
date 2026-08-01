# Quantum communication & networks

Sending information through quantum channels and across quantum networks: channel capacities
(classical, quantum, private) and coherent information, channel metrics (fidelity, diamond-norm
proxies, Pauli transfer matrices), advanced QKD (BB84, E91, six-state, decoy states), and
quantum-repeater networks. Capacities are checked against their closed forms, and network
fidelities against exact entanglement-swapping algebra.

All functions live under `quantum_debugger.algorithms.<module>`.

## Channel capacities & metrics

- `channel_capacity.coherent_information(kraus_ops, rho)`, `amplitude_damping_capacity(gamma)`.
- `quantum_channels_advanced.dephasing_quantum_capacity(p)` (`= 1 - h(p)`),
  `erasure_quantum_capacity(p)` (`= max(0, 1-2p)`), `entanglement_assisted_capacity(kraus)`,
  `holevo_information(probs, states)`, plus channel builders (`depolarizing_kraus`,
  `amplitude_damping_kraus`, `dephasing_kraus`).
- `channel_metrics.average_gate_fidelity(kraus, U)`, `entanglement_fidelity(...)`,
  `choi_matrix(...)`, `pauli_transfer_matrix(...)`, `unitarity(...)`.

```python
from quantum_debugger.algorithms.quantum_channels_advanced import dephasing_quantum_capacity, erasure_quantum_capacity
round(dephasing_quantum_capacity(0.1), 3)   # -> 0.531   (1 - h(0.1))
erasure_quantum_capacity(0.3)               # -> 0.4     (1 - 2p)
```

## Quantum key distribution

- `qkd_advanced.bb84_key_rate(qber)` (`1 - 2h(QBER)`), `bb84_threshold()` (`≈ 0.110`),
  `six_state_key_rate(qber)`, `six_state_threshold()` (`≈ 0.126`), `e91_key_rate(chsh)`,
  `qber_from_chsh(chsh)`, `decoy_state_gain(mu, transmittance)`, `secret_fraction(...)`,
  `sifting_ratio(...)`; `bb84.bb84(n_bits, eavesdropper)`.

```python
from quantum_debugger.algorithms.qkd_advanced import bb84_threshold, bb84_key_rate, six_state_threshold
round(bb84_threshold(), 3)        # -> 0.11    (BB84 QBER cutoff)
round(bb84_key_rate(0.05), 4)     # -> 0.4272
round(six_state_threshold(), 4)   # -> 0.1262  (six-state tolerates more error)
```

## Quantum networks & repeaters

Entanglement swapping multiplies Werner parameters (`w_out = w1 · w2`), so end-to-end fidelity
decays geometrically with the number of links — the reason repeaters need purification.

- `quantum_networks.swap_werner(w1, w2)`, `repeater_werner(w, n_segments)`,
  `path_fidelity(link_fidelities)`, `entanglement_swapping_fidelity(f1, f2)`,
  `entanglement_routing(graph, source, target)`, `repeater_rate(...)`, `purified_fidelity(f)`,
  `hops_before_threshold(...)`, `ghz_distribution_fidelity(...)`.
- `cloning.universal_clone(alpha, beta)` (optimal `5/6` fidelity), `protocols.teleport(psi)`,
  `superdense_coding(bits)`, `entanglement_swap(...)`.

```python
from quantum_debugger.algorithms.quantum_networks import swap_werner, repeater_werner
swap_werner(0.9, 0.9)          # -> 0.81    (w1 · w2)
round(repeater_werner(0.9, 3), 3)   # -> 0.729   (0.9^3 over three links)
```

## What this is verified against

- Capacities: the closed forms `1 - h(p)` (dephasing) and `1 - 2p` (erasure).
- QKD: the `1 - 2h(QBER)` BB84 rate and its `≈11%` threshold; the six-state `≈12.6%` threshold.
- Networks: the exact `w_out = w1·w2` swapping law and geometric `w^n` decay.
- Cloning: the optimal universal `5/6` clone fidelity.
