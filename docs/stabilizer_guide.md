# Clifford / Stabilizer Simulator

`quantum_debugger.stabilizer.StabilizerSimulator` is a second simulation engine
for **Clifford circuits** (H, S, X, Y, Z, CNOT, CZ + measurement). Instead of a
`2**n` state vector it tracks the stabilizer group as a binary tableau
(Aaronson-Gottesman CHP), updating in `O(n)` per gate and `O(n^2)` per
measurement. Circuits of *hundreds* of qubits run instantly -- far beyond the
dense state-vector simulator.

```python
from quantum_debugger.stabilizer import StabilizerSimulator

# 200-qubit GHZ state -- impossible for a state vector (2**200 amplitudes).
sim = StabilizerSimulator(200, seed=0)
sim.h(0)
for q in range(199):
    sim.cnot(0, q + 1)

outs = sim.measure_all()
assert len(set(outs)) == 1     # every qubit measures the same bit (GHZ correlation)
```

## Inspecting the stabilizer group

`stabilizers()` returns the `n` generators as `(sign, pauli_string)` pairs, with
`pauli_string[q]` in `I/X/Y/Z` acting on qubit `q`.

```python
sim = StabilizerSimulator(2)
sim.h(0)
sim.cnot(0, 1)
sim.stabilizers()      # [(1, 'XX'), (1, 'ZZ')]  -- the Bell state's stabilizers
```

## Measurement

`measure(q)` collapses the tableau and returns 0/1. Indeterminate outcomes are
random (seeded); once a qubit is fixed, re-measuring returns the same value, and
correlated qubits agree.

```python
sim = StabilizerSimulator(3)
sim.h(0); sim.cnot(0, 1); sim.cnot(1, 2)   # 3-qubit GHZ
b = sim.measure(0)
assert sim.measure(0) == b                 # deterministic on repeat
assert sim.measure(2) == b                 # perfectly correlated
```

## When to use it

Use the stabilizer simulator for stabilizer codes, GHZ/graph/cluster states,
randomized benchmarking sequences, and any large Clifford circuit. For circuits
with non-Clifford gates (T, arbitrary rotations, controlled-phase at generic
angles) use the state-vector simulator (`QuantumCircuit`) instead.

Correctness is verified against the state-vector simulator: for random Clifford
circuits, every reported stabilizer `S` satisfies `<psi|S|psi> = +1` to machine
precision.
