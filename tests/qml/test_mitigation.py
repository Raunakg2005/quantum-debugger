"""
Tests for error mitigation module
"""

import pytest
import numpy as np

from quantum_debugger.qml.mitigation import (
    PEC, CDR,
    DepolarizingNoise, AmplitudeDampingNoise, PhaseDampingNoise, CompositeNoise,
    characterize_readout_error, estimate_gate_fidelity, measure_gate_errors
)
from quantum_debugger.qml.mitigation.noise_models import create_realistic_noise_model


class TestNoiseModels:
    """Test quantum noise models"""
    
    def test_depolarizing_noise_initialization(self):
        """Test depolarizing noise can be initialized"""
        noise = DepolarizingNoise(error_rate=0.01)
        assert noise.error_rate == 0.01
    
    def test_depolarizing_noise_invalid_rate(self):
        """Test error on invalid error rate"""
        with pytest.raises(ValueError, match="between 0 and 1"):
            DepolarizingNoise(error_rate=1.5)
    
    def test_depolarizing_noise_apply(self):
        """Test applying depolarizing noise"""
        noise = DepolarizingNoise(error_rate=0.1)
        state = np.array([1, 0, 0, 0], dtype=complex)  # |00⟩
        
        noisy_state = noise.apply_noise(state, 'rx')
        
        # State should still be normalized
        assert np.isclose(np.linalg.norm(noisy_state), 1.0)
    
    def test_amplitude_damping_initialization(self):
        """Test amplitude damping initialization"""
        noise = AmplitudeDampingNoise(gamma=0.05)
        assert noise.gamma == 0.05
    
    def test_phase_damping_initialization(self):
        """Test phase damping initialization"""
        noise = PhaseDampingNoise(lambda_param=0.03)
        assert noise.lambda_param == 0.03
    
    def test_composite_noise(self):
        """Test composite noise combines multiple sources"""
        noise1 = DepolarizingNoise(0.01)
        noise2 = AmplitudeDampingNoise(0.05)
        noise3 = PhaseDampingNoise(0.03)
        
        composite = CompositeNoise([noise1, noise2, noise3])
        
        assert len(composite.models) == 3
    
    def test_composite_noise_empty_list(self):
        """Test error on empty noise model list"""
        with pytest.raises(ValueError, match="at least one"):
            CompositeNoise([])
    
    def test_composite_noise_apply(self):
        """Test applying composite noise"""
        noise = CompositeNoise([
            DepolarizingNoise(0.01),
            AmplitudeDampingNoise(0.02)
        ])
        
        state = np.array([1, 0], dtype=complex)
        noisy_state = noise.apply_noise(state, 'rx')
        
        assert len(noisy_state) == len(state)
    
    def test_create_realistic_noise_model(self):
        """Test creating realistic noise model from hardware params"""
        noise = create_realistic_noise_model(
            gate_error_rate=0.005,
            t1_time=100.0,
            t2_time=70.0,
            gate_time=0.05
        )
        
        assert isinstance(noise, CompositeNoise)
        assert len(noise.models) == 3


class TestPEC:
    """Test Probabilistic Error Cancellation"""
    
    def test_pec_initialization(self):
        """Test PEC can be initialized"""
        pec = PEC(gate_error_rates={'rx': 0.01, 'cnot': 0.02})
        
        assert 'rx' in pec.gate_errors
        assert pec.gate_errors['rx'] == 0.01
    
    def test_set_gate_error(self):
        """Test setting gate error rate"""
        pec = PEC()
        pec.set_gate_error('rx', 0.015)
        
        assert pec.gate_errors['rx'] == 0.015
    
    def test_decompose_noisy_gate(self):
        """Test quasi-probability decomposition"""
        pec = PEC()
        decomposition = pec.decompose_noisy_gate('rx', error_rate=0.01)
        
        # Should have 4 terms (ideal + 3 Pauli errors)
        assert len(decomposition) == 4
        
        # First term should be ideal gate
        assert decomposition[0][0] == 'rx'
        
        # Coefficients should sum to 1
        total_weight = sum(coef for _, coef in decomposition)
        assert np.isclose(total_weight, 1.0)
    
    def test_estimate_sampling_overhead(self):
        """Test sampling overhead estimation"""
        pec = PEC()
        overhead = pec.estimate_sampling_overhead(
            circuit_depth=10,
            avg_error_rate=0.01
        )
        
        assert overhead > 0
        assert overhead < 10000  # Should be capped
    
    def test_apply_pec(self):
        """Test applying PEC"""
        pec = PEC(gate_error_rates={'test': 0.01})
        
        # Mock circuit function
        def mock_circuit(params):
            return 0.5 + np.random.randn() * 0.1
        
        result, uncertainty = pec.apply_pec(
            mock_circuit,
            np.array([0.1, 0.2]),
            n_samples=10
        )
        
        assert isinstance(result, (float, np.floating))
        assert uncertainty >= 0


class TestCDR:
    """Test Clifford Data Regression"""
    
    def test_cdr_initialization(self):
        """Test CDR can be initialized"""
        cdr = CDR(n_clifford_circuits=50)
        
        assert cdr.n_training == 50
        assert not cdr.is_trained()
    
    def test_generate_training_data(self):
        """Test generating Clifford training circuits"""
        cdr = CDR(n_clifford_circuits=10)
        training_data = cdr.generate_training_data(n_qubits=2, circuit_depth=3)
        
        assert len(training_data) == 10
        assert all(len(item) == 2 for item in training_data)
    
    def test_cdr_training(self):
        """Test CDR training"""
        cdr = CDR(n_clifford_circuits=5, regression_method='linear')
        
        # Generate training data
        training_data = cdr.generate_training_data(n_qubits=2, circuit_depth=2)
        
        # Mock noisy executor
        def noisy_executor(circuit):
            # Return noisy version of ideal result
            return np.random.rand(4)
        
        cdr.train(training_data, noisy_executor)
        
        assert cdr.is_trained()
    
    def test_apply_cdr_not_trained(self):
        """Test error when applying CDR before training"""
        cdr = CDR()
        
        with pytest.raises(RuntimeError, match="must be trained"):
            cdr.apply_cdr(np.array([0.1, 0.2, 0.3, 0.4]))
    
    def test_apply_cdr_after_training(self):
        """Test applying CDR after training"""
        cdr = CDR(n_clifford_circuits=5)
        
        training_data = cdr.generate_training_data(2, 2)
        cdr.train(training_data, lambda x: np.random.rand(4))
        
        mitigated = cdr.apply_cdr(np.array([0.25, 0.25, 0.25, 0.25]))
        
        assert len(mitigated) == 4
    
    def test_different_regression_methods(self):
        """Test CDR with different regression methods"""
        for method in ['linear', 'ridge', 'lasso']:
            cdr = CDR(n_clifford_circuits=5, regression_method=method)
            
            training_data = cdr.generate_training_data(2, 2)
            cdr.train(training_data, lambda x: np.random.rand(4))
            
            assert cdr.is_trained()
    
    def test_get_model_info(self):
        """Test getting model info"""
        cdr = CDR(n_clifford_circuits=20)
        
        info_untrained = cdr.get_model_info()
        assert not info_untrained['trained']
        
        training_data = cdr.generate_training_data(2, 2)
        cdr.train(training_data, lambda x: np.random.rand(4))
        
        info_trained = cdr.get_model_info()
        assert info_trained['trained']
        assert info_trained['n_training_circuits'] == 20


class TestErrorCharacterization:
    """Test error characterization tools"""
    
    def test_characterize_readout_error(self):
        """Test readout error characterization"""
        # Mock executor
        def mock_executor(circuit, n_shots):
            return {0: n_shots // 2, 1: n_shots // 2}
        
        confusion = characterize_readout_error(
            n_qubits=1,
            executor=mock_executor,
            n_shots=1000
        )
        
        assert confusion.shape == (2, 2)
        # Each column should sum to 1 (probabilities)
        assert np.allclose(confusion.sum(axis=0), 1.0)
    
    def test_estimate_gate_fidelity(self):
        """Test gate fidelity estimation"""
        def mock_executor(circuit):
            return {'success': 0.99}
        
        fidelity = estimate_gate_fidelity('rx', mock_executor, n_trials=10)
        
        assert 0 <= fidelity <= 1
    
    def test_measure_gate_errors(self):
        """Test measuring multiple gate errors"""
        def mock_executor(circuit):
            return {'success': 0.95}
        
        errors = measure_gate_errors(['rx', 'ry', 'cnot'], mock_executor, n_trials=5)
        
        assert len(errors) == 3
        assert all(0 <= e <= 1 for e in errors.values())


class TestIntegration:
    """Integration tests for error mitigation"""
    
    def test_pec_with_noise_model(self):
        """Test PEC with realistic noise"""
        noise = DepolarizingNoise(0.01)
        pec = PEC(gate_error_rates={'rx': 0.01})
        
        assert pec.gate_errors['rx'] == noise.error_rate
    
    def test_composite_workflow(self):
        """Test complete PEC + CDR workflow"""
        # Setup PEC
        pec = PEC(gate_error_rates={'rx': 0.005})
        
        # Setup CDR
        cdr = CDR(n_clifford_circuits=10)
        training_data = cdr.generate_training_data(2, 2)
        cdr.train(training_data, lambda x: np.random.rand(4))
        
        # Both should be ready to use
        assert 'rx' in pec.gate_errors
        assert cdr.is_trained()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
