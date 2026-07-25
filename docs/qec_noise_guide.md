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

## Dynamical decoupling: the Hahn spin echo

The DFS exploited a *spatial* symmetry; the spin echo exploits a *temporal* one —
noise that stays correlated across one shot:

```python
from quantum_debugger.algorithms import spin_echo

r = spin_echo(sigma=1.5, static=True)   # quasi-static random detuning
r["no_echo"]    # 0.325 == exp(-sigma^2/2) -- free evolution dephases
r["echo"]       # 1.0   -- X pulse at mid-time refocuses the phase EXACTLY

r = spin_echo(sigma=1.5, static=False)  # noise re-randomizes mid-shot
r["echo"]       # 0.325 -- no advantage: nothing to refocus
```

Per shot, `U(phi/2) X U(phi/2) = X` for *every* realization `phi` — the phase
accumulated after the flip cancels the phase before it, so the ensemble average
is perfectly coherent. The failure case is just as instructive: when the two
half-evolutions carry independent phases, the echoed coherence equals the free
one exactly. **Noise correlation is the resource** — which is why real devices
characterize their noise spectrum before choosing a decoupling sequence.

## The quantum Zeno effect

The third protection mechanism is the strangest: **measurement itself**. A watched
qubit cannot Rabi-flip:

```python
import numpy as np
from quantum_debugger.algorithms import quantum_zeno, zeno_postselected

quantum_zeno(np.pi, 1)["survival"]      # 0.0   -- a free pi-pulse fully inverts
quantum_zeno(np.pi, 50)["survival"]     # 0.953 -- 50 unread measurements freeze it
quantum_zeno(np.pi, 2000)["survival"]   # 0.9988 -- N -> infinity: never leaves |0>

r = zeno_postselected(np.pi / 2, 100)   # demand outcome 0 at every check
r["survival_probability"]               # 0.9938 == cos^200(pi/400)
r["state_fidelity"]                     # 1.0 -- the survivor is still exactly |0>
```

Each unread measurement is the exact channel `rho -> P0 rho P0 + P1 rho P1`; the
final `|0>` population is exactly `1/2 + cos^N(wT/N)/2`. Post-selecting outcome 0
each time survives with probability `cos^{2N}(wT/2N) -> 1`. Together with the DFS
(symmetry) and the spin echo (correlation), this completes the trio of ways to
protect a qubit *without* the overhead of full error correction.

## Distance 3 in action: the Steane code vs depolarizing noise

The 3-qubit codes above correct only one error *type*. Running the full Steane
[[7,1,3]] code against independent depolarizing noise on all 7 qubits (exact
64-syndrome CPTP recovery on the density matrix) shows what distance 3 buys:

```python
from quantum_debugger.algorithms import steane_code_noisy

r = steane_code_noisy(p=0.002)
1 - r["corrected"]      # 4.2e-5  -- logical error
1 - r["uncorrected"]    # 1.0e-3  -- bare qubit: 24x worse
r["weight1_bound"]      # (1-p)^7 + 7p(1-p)^6, always exceeded

# Quadratic suppression: doubling p quadruples the logical error.
(1 - steane_code_noisy(0.004)["corrected"]) / (1 - steane_code_noisy(0.002)["corrected"])
# 3.98  ~= 4
```

`1 - F ~ O(p^2)` versus `O(p)` bare — the hallmark of a distance-3 code, since any
single-qubit error is corrected and only (some) weight-2 errors cause logical
failure. The **pseudo-threshold** sits near `p ~ 0.05`: below it encoding helps,
at `p = 0.25` it hurts. This is the number a fault-tolerant architecture must
engineer its physical error rate below.
