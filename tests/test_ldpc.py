"""LDPC codes & message-passing decoding (v3.3.0) -- verification tests.

Exact syndrome decoding is checked on the Hamming [7,4,3] code; belief-propagation, min-sum, and
bit-flipping are checked on a regular column-weight-3 circulant LDPC (distance 4), where they
correct every single-bit error and agree with the exact ML decoder.
"""
import numpy as np
import pytest

from quantum_debugger.algorithms.ldpc_codes import (
    repetition_check, hamming_code_check, syndrome, is_codeword, all_codewords,
    code_dimension, code_rate, code_parameters, minimum_distance, tanner_graph,
    column_weights, row_weights, is_regular, tanner_girth, random_regular_ldpc,
)
from quantum_debugger.algorithms.syndrome_decoding import (
    syndrome_table, coset_leader, ml_decode, corrects_all_errors_up_to,
    error_correcting_capability,
)
from quantum_debugger.algorithms.belief_propagation import (
    bsc_llr, sum_product_decode, min_sum_decode, bp_corrects, bp_matches_ml_on_weight1,
)
from quantum_debugger.algorithms.bit_flipping_decoder import (
    unsatisfied_checks, gallager_bit_flip, bit_flip_corrects_all_weight1, min_column_weight,
)

HAMMING = hamming_code_check(3)


def _circulant_ldpc():
    """A regular (3,3) circulant LDPC on 7 bits: distance 4, column weight 3."""
    base = np.array([1, 1, 0, 1, 0, 0, 0])
    return np.array([np.roll(base, i) for i in range(7)])


def test_hamming_parameters():
    assert code_parameters(HAMMING) == {"n": 7, "k": 4, "d": 3}
    assert len(all_codewords(HAMMING)) == 16
    assert code_rate(HAMMING) == pytest.approx(4 / 7)


def test_codeword_and_syndrome():
    cw = all_codewords(HAMMING)[5]
    assert is_codeword(HAMMING, cw)
    assert np.all(syndrome(HAMMING, cw) == 0)
    e = np.zeros(7, dtype=int)
    e[2] = 1
    assert not is_codeword(HAMMING, (cw + e) % 2)


def test_single_error_syndromes_distinct():
    syns = {tuple(syndrome(HAMMING, np.eye(7, dtype=int)[j])) for j in range(7)}
    assert len(syns) == 7  # each single error has its own syndrome


def test_exact_ml_decodes_hamming():
    assert corrects_all_errors_up_to(HAMMING, 1)
    assert error_correcting_capability(HAMMING) == 1
    table = syndrome_table(HAMMING)
    e = np.zeros(7, dtype=int)
    e[3] = 1
    assert np.array_equal(coset_leader(HAMMING, e, table), e)
    assert np.all(ml_decode(HAMMING, e, table) == 0)


def test_repetition_code():
    R = repetition_check(5)
    assert code_parameters(R) == {"n": 5, "k": 1, "d": 5}


def test_regular_and_girth():
    C = _circulant_ldpc()
    assert is_regular(C)
    assert np.all(column_weights(C) == 3)
    assert np.all(row_weights(C) == 3)
    assert tanner_girth(HAMMING) == 4          # short cycles
    assert min_column_weight(C) == 3


def test_random_regular_ldpc_shape():
    L = random_regular_ldpc(12, 3, 6, seed=1)
    assert L.shape == (6, 12)
    assert set(np.unique(L)).issubset({0, 1})


def test_bsc_llr_sign():
    llr = bsc_llr(np.array([0, 1]), 0.1)
    assert llr[0] > 0 and llr[1] < 0        # a received 0 favours 0, a received 1 favours 1


def test_belief_propagation_corrects_ldpc():
    C = _circulant_ldpc()
    assert bp_matches_ml_on_weight1(C)      # BP corrects every single-bit error
    for j in range(7):
        e = np.zeros(7, dtype=int)
        e[j] = 1
        assert bp_corrects(C, e, decoder=min_sum_decode)  # min-sum too


def test_bp_recovers_zero_codeword_and_converges():
    C = _circulant_ldpc()
    e = np.zeros(7, dtype=int)
    e[4] = 1
    decoded, converged = sum_product_decode(C, e, p=0.05)
    assert converged
    assert np.all(decoded == 0)


def test_bit_flipping_corrects_ldpc():
    C = _circulant_ldpc()
    assert bit_flip_corrects_all_weight1(C)
    e = np.zeros(7, dtype=int)
    e[2] = 1
    assert np.array_equal(unsatisfied_checks(C, e), np.nonzero(syndrome(C, e))[0])
    decoded, converged = gallager_bit_flip(C, e)
    assert converged and np.all(decoded == 0)
