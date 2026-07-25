# Quantum Error Correction under Continuous Noise

The [error-correction routines](quantum_algorithms_guide) inject a single
*discrete* Pauli error and undo it on the state-vector engine. Real hardware is
noisier than that: every physical qubit independently suffers an error *channel*
with some probability `p` each cycle. This guide covers the exact
density-matrix treatment of a code cycle under that continuous noise — no
Monte-Carlo sampling.

## The 3-qubit bit-flip code against a bit-flip channel

```python
from quantum_debugger.algorithms import bit_flip_code_noisy

r = bit_flip_code_noisy(p=0.1)          # logical |0_L>
print(r["corrected"])    # 0.972  -- logical fidelity after syndrome recovery
print(r["uncorrected"])  # 0.9    -- a lone qubit under the same channel (1 - p)
print(r["analytic"])     # 0.972  -- (1-p)^3 + 3p(1-p)^2
```

Internally this encodes `alpha|0_L> + beta|1_L>` as a density matrix, applies an
independent `bit_flip(p)` channel to each of the three physical qubits, and then
applies the **exact CPTP recovery map**

```
R(rho) = sum_s  C_s P_s rho P_s C_s†
```

where `P_s` projects onto syndrome subspace `s` (the joint eigenspace of the
stabilizers `Z0Z1`, `Z1Z2`) and `C_s` is the matching single-qubit `X`
correction. Because the projectors partition the Hilbert space and each
correction is unitary, `R` is completely positive and trace-preserving — a
faithful model of the full measure-and-correct cycle.

The recovered fidelity of a computational-basis codeword is exactly

```
F_corrected(p) = (1 - p)^3 + 3 p (1 - p)^2
```

— the probability that 0 or 1 of the 3 qubits flips. It beats the un-encoded
`1 - p` for every `p < 1/2` (the code **threshold**) and is *worse* above it,
because majority voting then amplifies the error:

```python
bit_flip_code_noisy(0.6)["corrected"] < bit_flip_code_noisy(0.6)["uncorrected"]  # True
```

A `|+_L>` codeword is even better off: a logical-`X` failure maps
`(|000> + |111>)/√2` to itself, so it stays perfectly protected (`F = 1`) at any
`p`.

## Phase-flip code

The phase-flip code is the bit-flip code conjugated by Hadamards, so it protects
against a `phase_flip(p)` channel with the identical logical fidelity:

```python
from quantum_debugger.algorithms import phase_flip_code_noisy
phase_flip_code_noisy(0.1)["corrected"]   # 0.972
```

## Distance scaling and the threshold

For a distance-`d` (odd) repetition code with majority-vote decoding, the exact
logical error rate is

```
P_L(p, d) = sum_{k > d/2} C(d, k) p^k (1 - p)^(d - k)
```

```python
from quantum_debugger.algorithms import repetition_code_logical_error

repetition_code_logical_error(0.1, 3)   # 0.028
repetition_code_logical_error(0.1, 5)   # 0.00856
repetition_code_logical_error(0.1, 7)   # 0.00270
```

Below threshold, adding qubits suppresses the logical error — the defining
feature of a good code. At exactly `p = 1/2` every distance gives `P_L = 1/2`:
the code neither helps nor hurts. This complements the Monte-Carlo
`repetition_code_error_rate` with a closed-form curve.

## The physical syndrome-extraction circuit

`bit_flip_code_noisy` applies an abstract CPTP recovery. `syndrome_extraction_cycle`
instead runs the **measured-ancilla circuit** — the way a real device corrects errors:

```python
from quantum_debugger.algorithms import syndrome_extraction_cycle

r = syndrome_extraction_cycle(p=0.1)
r["corrected"]   # 0.972 == (1-p)^3 + 3p(1-p)^2
```

The cycle, on 3 data + 2 ancilla qubits (density matrix):

1. encode the logical qubit, ancillas in `|0>`;
2. hit each data qubit with an independent bit-flip channel of strength `p`;
3. **extract the syndrome** with CNOTs — ancilla 0 records `parity(d0, d1)`
   (stabilizer `Z0Z1`), ancilla 1 records `parity(d1, d2)` (`Z1Z2`);
4. **measure the ancillas** and apply the `X` correction their outcome selects,
   summed over outcomes as a CPTP measurement channel;
5. **discard the ancillas** (partial trace) and read out the logical fidelity.

This reproduces the ideal-recovery fidelity `(1-p)^3 + 3p(1-p)^2` exactly — a direct
check that the physical circuit implements the code, not just the abstract map.

## Protecting qubits without QEC: decoherence-free subspaces

Full error correction is not the only defense. When the noise has a *symmetry* —
e.g. a fluctuating global field that adds the **same** random Z phase to every
qubit — encoding in a symmetric subspace gives perfect protection with no
syndrome measurements at all:

```python
from quantum_debugger.algorithms import dfs_protection

r = dfs_protection(sigma=0.8)     # collective Gaussian dephasing, strength sigma
r["dfs_fidelity"]                 # 1.0     -- a|01> + b|10> is untouched, ANY sigma
r["bare_coherence"]               # 0.726   == exp(-sigma^2/2)  (a lone |+> qubit)
r["antidfs_coherence"]            # 0.278   == exp(-2 sigma^2)  (a|00> + b|11>: worse!)
```

Under `U(phi) = exp(-i phi/2 sum Z_q)` a basis state's phase depends only on its
excitation number, so the equal-excitation subspace `{|01>, |10>}` picks up a
single global phase — invariant for every realization of the noise. The channel is
computed as a genuine ensemble average of unitaries (Gauss-Hermite quadrature),
and all three behaviors match their closed forms exactly. Trapped-ion experiments
use exactly this encoding against collective magnetic-field noise.
