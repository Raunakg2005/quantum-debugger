# LDPC codes & message-passing decoding

Low-density parity-check (LDPC) codes — sparse linear codes decoded by iterative message passing —
are the backbone of modern classical error correction and, increasingly, fault-tolerant quantum
memories. This guide covers building parity-check matrices and their Tanner graphs, exact
maximum-likelihood syndrome decoding (the reference), and the two workhorse iterative decoders:
belief propagation (sum-product / min-sum) and Gallager bit-flipping. Every property is checked
against an exact reference — the enumerated codewords, the ML decoder, and the ``[7,4,3]`` Hamming
code.

All functions live under `quantum_debugger.algorithms.<module>`.

## Codes, parity checks & Tanner graphs

A code is the null space of its parity-check matrix `H` over GF(2); LDPC means `H` is sparse.

- `ldpc_codes.repetition_check(n)`, `hamming_code_check(r)`, `random_regular_ldpc(n, wc, wr)`.
- `ldpc_codes.syndrome(H, w)`, `is_codeword(...)`, `all_codewords(H)`, `code_dimension(H)`,
  `code_rate(H)`, `code_parameters(H)`, `minimum_distance(H)`.
- `ldpc_codes.tanner_graph(H)`, `column_weights(H)`, `row_weights(H)`, `is_regular(H)`,
  `tanner_girth(H)`.

```python
from quantum_debugger.algorithms.ldpc_codes import hamming_code_check, code_parameters, tanner_girth
H = hamming_code_check(3)
code_parameters(H)     # -> {'n': 7, 'k': 4, 'd': 3}
tanner_girth(H)        # -> 4   (short 4-cycles — these hurt belief propagation)
```

## Exact syndrome decoding (the ML reference)

Maximum-likelihood decoding picks the minimum-weight error consistent with the syndrome — the coset
leader. Building the full table is exact for small codes.

- `syndrome_decoding.syndrome_table(H)`, `coset_leader(H, error)`, `ml_decode(H, received)`,
  `syndrome_decoding.corrects_all_errors_up_to(H, weight)`, `error_correcting_capability(H)`.

```python
import numpy as np
from quantum_debugger.algorithms.ldpc_codes import hamming_code_check
from quantum_debugger.algorithms.syndrome_decoding import corrects_all_errors_up_to, error_correcting_capability
H = hamming_code_check(3)
error_correcting_capability(H)          # -> 1   (t = ⌊(d−1)/2⌋)
corrects_all_errors_up_to(H, 1)         # -> True (exact decoding fixes every single-bit error)
```

## Belief propagation

Belief propagation passes log-likelihood messages along the Tanner graph until the hard decision is
a codeword. It is near-optimal on well-structured (large-girth, higher column-weight) LDPC codes.

- `belief_propagation.bsc_llr(received, p)`, `sum_product_decode(H, received, p)`,
  `min_sum_decode(...)`, `bp_corrects(H, error)`, `bp_matches_ml_on_weight1(H)`.

```python
import numpy as np
from quantum_debugger.algorithms.belief_propagation import bp_matches_ml_on_weight1
# a regular column-weight-3 circulant LDPC (distance 4)
base = np.array([1, 1, 0, 1, 0, 0, 0])
C = np.array([np.roll(base, i) for i in range(7)])
bp_matches_ml_on_weight1(C)     # -> True   (BP corrects every single-bit error, matching ML)
```

## Gallager bit-flipping

The simplest hard-decision decoder: repeatedly flip the bit sitting on the most unsatisfied checks.
It reliably corrects a single error when the column weight is `>= 3`.

- `bit_flipping_decoder.unsatisfied_checks(H, w)`, `unsatisfied_count_per_bit(...)`,
  `gallager_bit_flip(H, received)`, `bit_flip_corrects_all_weight1(H)`, `min_column_weight(H)`.

```python
import numpy as np
from quantum_debugger.algorithms.bit_flipping_decoder import bit_flip_corrects_all_weight1, min_column_weight
base = np.array([1, 1, 0, 1, 0, 0, 0])
C = np.array([np.roll(base, i) for i in range(7)])
min_column_weight(C), bit_flip_corrects_all_weight1(C)     # -> (3, True)
```

## What this is verified against

- Codes: the Hamming ``[7,4,3]`` parameters, its 16 enumerated codewords, and 7 distinct single-error
  syndromes.
- Exact decoding: every weight-``t`` error corrected (``t = ⌊(d−1)/2⌋``).
- Belief propagation & bit-flipping: correcting *every* single-bit error on a regular
  column-weight-3 LDPC, and agreeing with the exact ML decoder there. (On the Hamming code, whose
  Tanner graph has weight-1 columns and girth-4 cycles, message passing is honestly reported as
  suboptimal — the exact decoder is used instead.)
