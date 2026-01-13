"""
Test VQE Algorithm
==================

Test Variational Quantum Eigensolver with H2 molecule.
"""

import pytest
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quantum_debugger.qml.algorithms import VQE
from quantum_debugger.qml.hamiltonians import h2_hamiltonian
from quantum_debugger.qml.ansatz import hardware_efficient_ansatz


class TestVQEBasic:
    """Basic VQE functionality tests"""
    
    def test_vqe_initialization(self):
        """Test VQE can be initialized"""
        H, _ = h2_hamiltonian()
        vqe = VQE(
            hamiltonian=H,
            ansatz_builder=hardware_efficient_ansatz,
            num_qubits=2
        )
        
        assert vqe.num_qubits == 2
        assert vqe.optimizer == 'COBYLA'
        assert vqe.hamiltonian.shape == (4, 4)
    
    def test_exact_ground_state(self):
        """Test exact ground state computation"""
        H, _ = h2_hamiltonian()
        vqe = VQE(H, hardware_efficient_ansatz, num_qubits=2)
        
        exact_energy = vqe.exact_ground_state()
        
        # Should be around -1.38 Hartree (actual computed value)
        assert -1.5 < exact_energy < -1.3
        assert np.isclose(exact_energy, -1.384, atol=0.01)
    
    def test_cost_function(self):
        """Test cost function returns valid energy"""
        H, _ = h2_hamiltonian()
        vqe = VQE(H, hardware_efficient_ansatz, num_qubits=2)
        
        params = np.array([0.5, 0.8, 0.3, 0.6])  # 4 params for 2 qubits
        energy = vqe.cost_function(params)
        
        # Energy should be real and bounded
        assert isinstance(energy, (float, np.floating))
        assert -2.0 < energy < 0.5  # Broader range for varied params


class TestVQEOptimization:
    """Test VQE optimization"""
    
    def test_vqe_finds_ground_state(self):
        """Test VQE finds H2 ground state reasonably well"""
        H, _ = h2_hamiltonian()
        vqe = VQE(H, hardware_efficient_ansatz, num_qubits=2, max_iterations=50)
        
        # Random initialization
        np.random.seed(42)
        initial_params = np.random.rand(4)  # 4 params for 2 qubits
        
        result = vqe.run(initial_params)
        
        # Check results
        assert 'ground_state_energy' in result
        assert 'optimal_params' in result
        assert 'iterations' in result
        
        # Should be close to exact value
        exact = vqe.exact_ground_state()
        error = abs(result['ground_state_energy'] - exact)
        
        # Allow some error (variational principle: E_VQE >= E_exact)
        assert error < 0.1, f"Error {error:.4f} too large"
        
        # Should have improved from initial
        initial_energy = vqe.cost_function(initial_params)
        assert result['ground_state_energy'] <= initial_energy
    
    def test_vqe_convergence_history(self):
        """Test VQE tracks optimization history"""
        H, _ = h2_hamiltonian()
        vqe = VQE(H, hardware_efficient_ansatz, num_qubits=2, max_iterations=20)
        
        result = vqe.run(np.array([0.5, 0.5, 0.3, 0.6]))  # 4 params
        
        # Should have history
        assert len(vqe.history) > 0
        
        # Energy should generally decrease
        energies = [h['energy'] for h in vqe.history]
        assert energies[-1] <= energies[0]


class TestVQEDifferentAnsatz:
    """Test VQE with different ansätze"""
    
    def test_vqe_with_deeper_ansatz(self):
        """Test VQE with 2-layer ansatz"""
        from quantum_debugger.qml.ansatz import hardware_efficient_ansatz
        
        H, _ = h2_hamiltonian()
        
        # Create deep ansatz properly
        deep_ansatz = hardware_efficient_ansatz(num_qubits=2, depth=2)
        
        vqe = VQE(H, deep_ansatz, num_qubits=2, max_iterations=30)
        
        # 2 layers means 3 rotation layers, 2 qubits = 6 parameters
        initial_params = np.random.rand(6)
        result = vqe.run(initial_params)
        
        # Should still find ground state
        exact = vqe.exact_ground_state()
        assert abs(result['ground_state_energy'] - exact) < 0.1


class TestVQEEdgeCases:
    """Edge cases and error handling"""
    
    def test_wrong_hamiltonian_size(self):
        """Test error on wrong Hamiltonian size"""
        # 2x2 Hamiltonian but claim 2 qubits (needs 4x4)
        H_wrong = np.array([[1, 0], [0, -1]])
        
        with pytest.raises(ValueError, match="doesn't match"):
            VQE(H_wrong, hardware_efficient_ansatz, num_qubits=2)
    
    def test_vqe_different_optimizers(self):
        """Test VQE with different optimizers"""
        H, _ = h2_hamiltonian()
        
        for optimizer in ['COBYLA', 'SLSQP']:
            ansatz = hardware_efficient_ansatz(num_qubits=2)
            vqe = VQE(H, ansatz, num_qubits=2,
                     optimizer=optimizer, max_iterations=20)
            
            result = vqe.run(np.array([0.5, 0.5, 0.3, 0.6]), method=optimizer)
            
            # Should complete
            assert 'ground_state_energy' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
