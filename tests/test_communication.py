"""
Tests for the 2.6.0 communication suite: quantum-channel capacities, QKD key rates and
thresholds, and quantum networks (swapping, repeaters, routing). Verified against closed
forms.
"""

import numpy as np
import pytest

from quantum_debugger.algorithms.quantum_channels_advanced import (
    binary_entropy, depolarizing_kraus, dephasing_kraus, amplitude_damping_kraus,
    coherent_information, entanglement_assisted_capacity, erasure_quantum_capacity,
    dephasing_quantum_capacity, holevo_information, channel_fidelity)
from quantum_debugger.algorithms.qkd_advanced import (
    bb84_key_rate, bb84_threshold, six_state_key_rate, six_state_threshold,
    qber_from_chsh, e91_key_rate, sifting_ratio, decoy_state_gain)
from quantum_debugger.algorithms.quantum_networks import (
    werner_fidelity, swap_werner, entanglement_swapping_fidelity, repeater_werner,
    repeater_rate, purified_fidelity, path_fidelity, hops_before_threshold, entanglement_routing)

_MIX = np.eye(2, dtype=complex) / 2


class TestChannels:
    def test_dephasing_capacity(self):
        for p in (0.1, 0.25, 0.5):
            assert abs(coherent_information(dephasing_kraus(p), _MIX) - dephasing_quantum_capacity(p)) < 1e-6

    def test_erasure_capacity(self):
        assert erasure_quantum_capacity(0.2) == 0.6 and erasure_quantum_capacity(0.6) == 0.0

    def test_ea_capacity(self):
        k = depolarizing_kraus(0.2)
        assert entanglement_assisted_capacity(k) >= coherent_information(k, _MIX)

    def test_amplitude_damping(self):
        assert coherent_information(amplitude_damping_kraus(0.1), _MIX) > 0
        assert coherent_information(amplitude_damping_kraus(0.6), _MIX) < 0

    def test_holevo_and_fidelity(self):
        z0 = np.array([[1, 0], [0, 0]], dtype=complex); z1 = np.array([[0, 0], [0, 1]], dtype=complex)
        assert abs(holevo_information([0.5, 0.5], [z0, z1]) - 1) < 1e-9
        assert holevo_information([0.5, 0.5], [z0, z0]) < 1e-9
        assert abs(channel_fidelity([np.eye(2, dtype=complex)]) - 1) < 1e-9


class TestQKD:
    def test_bb84_threshold(self):
        assert abs(bb84_threshold() - 0.11) < 5e-3
        assert bb84_key_rate(bb84_threshold()) < 1e-6
        assert bb84_key_rate(0.01) > 0.8

    def test_six_state_higher(self):
        assert six_state_threshold() > bb84_threshold()
        assert abs(six_state_threshold() - 0.126) < 5e-3

    def test_e91(self):
        assert abs(qber_from_chsh(2 * np.sqrt(2))) < 1e-9
        assert abs(e91_key_rate(2 * np.sqrt(2)) - 1) < 1e-6
        assert e91_key_rate(2.0) < 1e-6            # classical bound -> no key

    def test_sifting_decoy(self):
        assert sifting_ratio("bb84") == 0.5 and abs(sifting_ratio("six_state") - 1 / 3) < 1e-9
        assert decoy_state_gain(0.5, 0.1) > 0


class TestNetworks:
    def test_werner_swap(self):
        assert werner_fidelity(1.0) == 1.0 and werner_fidelity(0.0) == 0.25
        assert abs(swap_werner(0.9, 0.8) - 0.72) < 1e-9
        assert abs(entanglement_swapping_fidelity(0.9, 1.0) - 0.9) < 1e-9

    def test_repeater(self):
        assert abs(repeater_werner(0.95, 5) - 0.95**5) < 1e-9
        assert repeater_rate(0.8, 5, 0.9) < 0.8

    def test_purification(self):
        assert purified_fidelity(0.7) > 0.7

    def test_path_and_hops(self):
        assert path_fidelity([0.95] * 6) < path_fidelity([0.95] * 3)
        assert hops_before_threshold(0.95) > hops_before_threshold(0.8)

    def test_routing(self):
        graph = {(0, 1): 0.9, (1, 3): 0.9, (0, 2): 0.99, (2, 3): 0.99}
        fid, path = entanglement_routing(graph, 0, 3)
        assert path == [0, 2, 3] and fid > 0.9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
