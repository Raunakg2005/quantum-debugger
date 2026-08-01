"""
Tests for the 2.9.0 quantum-thermodynamics suite: work/heat/entropy production, the Jarzynski
and Crooks relations, the Landauer bound, the quantum Otto engine, and passive states /
ergotropy. Verified against closed forms and the exact statistics.
"""

import numpy as np
import pytest

from quantum_debugger.algorithms.quantum_thermodynamics import (
    gibbs_state, free_energy, internal_energy, quench_work, nonequilibrium_free_energy,
    heat_capacity, thermal_entropy, entropy_production)
from quantum_debugger.algorithms.fluctuation_theorems import (
    two_point_work_distribution, jarzynski_average, free_energy_difference, average_work,
    work_variance, dissipated_work, verify_jarzynski, landauer_bound, crooks_ratio)
from quantum_debugger.algorithms.quantum_otto_cycle import (
    otto_cycle, otto_efficiency, carnot_efficiency, is_engine, efficiency_below_carnot)
from quantum_debugger.algorithms.passive_states import (
    passive_state, ergotropy, is_passive, bound_energy, gibbs_is_passive)


def _herm(n, seed):
    rng = np.random.default_rng(seed)
    A = rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n))
    return (A + A.conj().T) / 2


class TestThermodynamics:
    def test_gibbs_valid(self):
        g = gibbs_state(_herm(4, 0), 1.3)
        assert abs(np.trace(g) - 1) < 1e-9 and np.min(np.linalg.eigvalsh(g)) > -1e-9

    def test_gibbs_minimizes_free_energy(self):
        H = _herm(4, 1); beta = 1.3
        assert abs(nonequilibrium_free_energy(gibbs_state(H, beta), H, beta) - free_energy(H, beta)) < 1e-6
        assert nonequilibrium_free_energy(np.eye(4) / 4, H, beta) >= free_energy(H, beta) - 1e-9

    def test_second_law(self):
        Hi, Hf = _herm(4, 0), _herm(4, 2)
        assert entropy_production(gibbs_state(Hi, 1.3), Hi, Hf, 1.3) >= -1e-9

    def test_heat_capacity_entropy(self):
        H = np.diag([0, 1, 2, 3]).astype(complex)
        assert heat_capacity(H, 1.0) > 0 and thermal_entropy(H, 1.0) >= 0


class TestFluctuation:
    def test_jarzynski(self):
        Hi, Hf = _herm(4, 0), _herm(4, 2)
        assert verify_jarzynski(Hi, Hf, 1.3)
        assert abs(jarzynski_average(Hi, Hf, 1.3) - np.exp(-1.3 * free_energy_difference(Hi, Hf, 1.3))) < 1e-9

    def test_second_law_bounds(self):
        Hi, Hf = _herm(4, 0), _herm(4, 2)
        assert average_work(Hi, Hf, 1.3) >= free_energy_difference(Hi, Hf, 1.3) - 1e-9
        assert dissipated_work(Hi, Hf, 1.3) >= -1e-9
        w, p = two_point_work_distribution(Hi, Hf, 1.3)
        assert abs(p.sum() - 1) < 1e-9 and work_variance(Hi, Hf, 1.3) >= 0

    def test_landauer_crooks(self):
        assert abs(landauer_bound(1, 1.0) - np.log(2)) < 1e-9
        dF = 0.7
        assert abs(crooks_ratio(dF, dF, 1.0) - 1) < 1e-9


class TestOtto:
    def test_efficiency_and_carnot(self):
        wc, wh, Tc, Th = 1.0, 2.0, 0.5, 2.0
        cyc = otto_cycle(wc, wh, Tc, Th)
        assert abs(cyc["efficiency"] - otto_efficiency(wc, wh)) < 1e-9
        assert is_engine(wc, wh, Tc, Th)
        assert efficiency_below_carnot(wc, wh, Tc, Th)
        assert otto_efficiency(wc, wh) <= carnot_efficiency(Tc, Th) + 1e-9

    def test_non_engine_second_law(self):
        assert efficiency_below_carnot(1.8, 2.0, 0.5, 2.0)


class TestPassive:
    def test_ergotropy(self):
        H = np.diag([0, 1, 2, 3]).astype(complex)
        rho = _herm(4, 1); rho = rho @ rho.conj().T; rho /= np.trace(rho)
        assert ergotropy(rho, H) >= -1e-9
        assert abs(ergotropy(rho, H) + bound_energy(rho, H) - internal_energy(rho, H)) < 1e-9

    def test_passive_and_gibbs(self):
        H = np.diag([0, 1, 2, 3]).astype(complex)
        rho = _herm(4, 3); rho = rho @ rho.conj().T; rho /= np.trace(rho)
        assert is_passive(passive_state(rho, H), H)
        assert gibbs_is_passive(H, 1.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
