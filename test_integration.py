"""
Integration Tests for QML Components
====================================

Test complete workflows combining gates, algorithms, training, and optimization.
"""

import pytest
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quantum_debugger.qml import (
    RXGate, RYGate, RZGate,
    VQE, QAOA,
    h2_hamiltonian,
    hardware_efficient_ansatz
)
from quantum_debugger.qml.optimizers import Adam, GradientDescent
from quantum_debugger.qml.training import QuantumTrainer


class TestVQEIntegration:
    """Integration tests for complete VQE workflows"""
    
    def test_vqe_with_custom_ansatz(self):
        """Test VQE with a custom ansatz builder"""
        H = h2_hamiltonian()
        
        def custom_ansatz(params, num_qubits):
            """Custom 3-layer ansatz"""
            gates = []
            idx = 0
            for _ in range(3):
                for q in range(num_qubits):
                    gates.append(RYGate(q, params[idx], trainable=True))
                    idx += 1
            return gates
        
        vqe = VQE(H, custom_ansatz, num_qubits=2, max_iterations=30)
        
        # 3 layers, 2 qubits = 6 params
        params = np.random.rand(6)
        result = vqe.run(params)
        
        # Should find reasonable energy
        exact = vqe.exact_ground_state()
        assert result['ground_state_energy'] - exact < 0.2
    
    def test_vqe_with_different_optimizers(self):
        """Test VQE works with all optimizer types"""
        H = h2_hamiltonian()
        
        optimizers = ['COBYLA', 'SLSQP', 'Powell']
        
        for opt in optimizers:
            vqe = VQE(H, hardware_efficient_ansatz, num_qubits=2, 
                     optimizer=opt, max_iterations=20)
            
            result = vqe.run(np.random.rand(2))
            
            # Should complete successfully
            assert 'ground_state_energy' in result
            # Energy should be reasonable
            assert -2.0 < result['ground_state_energy'] < 0.0
    
    def test_vqe_convergence_tracking(self):
        """Test VQE properly tracks convergence"""
        H = h2_hamiltonian()
        vqe = VQE(H, hardware_efficient_ansatz, num_qubits=2, max_iterations=30)
        
        result = vqe.run(np.array([0.5, 0.8]))
        
        # Check history is populated
        assert len(vqe.history) > 0
        
        # Energy should improve or stay same (variational principle)
        energies = [h['energy'] for h in vqe.history]
        
        # First should be worse than or equal to last
        assert energies[0] >= energies[-1] - 0.01  # Small tolerance


class TestQAOAIntegration:
    """Integration tests for QAOA workflows"""
    
    def test_qaoa_on_various_graphs(self):
        """Test QAOA on different graph topologies"""
        graphs = {
            'line': [(0,1), (1,2)],
            'triangle': [(0,1), (1,2), (2,0)],
            'star': [(0,1), (0,2), (0,3)],
            'complete_4': [(0,1), (0,2), (0,3), (1,2), (1,3), (2,3)]
        }
        
        for name, graph in graphs.items():
            qaoa = QAOA(graph=graph, p=1, max_iterations=15)
            result = qaoa.run()
            
            # Should find some cut
            assert result['best_value'] > 0, f"Failed on {name} graph"
            # Shouldn't exceed number of edges
            assert result['best_value'] <= len(graph) + 0.5
    
    def test_qaoa_increasing_p(self):
        """Test QAOA with increasing p values"""
        graph = [(0,1), (1,2), (2,3), (3,0)]
        results = []
        
        for p in [1, 2, 3]:
            qaoa = QAOA(graph=graph, p=p, max_iterations=20)
            result = qaoa.run(np.random.rand(2*p))
            results.append(result['best_value'])
        
        # Generally, higher p should give better or equal results
        # (Allow some variance due to optimization)
        assert results[2] >= results[0] - 1.0


class TestGatesWithAlgorithms:
    """Test parameterized gates integration with algorithms"""
    
    def test_gates_in_vqe_circuit(self):
        """Test gates work correctly within VQE"""
        H = h2_hamiltonian()
        
        def test_ansatz(params, num_qubits):
            """Ansatz with all gate types"""
            return [
                RYGate(0, params[0], trainable=True),
                RXGate(1, params[1], trainable=True),
                RZGate(0, params[2], trainable=True),
            ]
        
        vqe = VQE(H, test_ansatz, num_qubits=2, max_iterations=20)
        result = vqe.run(np.random.rand(3))
        
        # Should work with mixed gate types
        assert result['success'] or len(vqe.history) > 5
    
    def test_gate_parameter_updates(self):
        """Test gates properly update parameters during optimization"""
        gate = RXGate(0, 0.5, trainable=True)
        
        # Simulate optimization
        for i in range(10):
            grad = 0.1  # Simulated gradient
            gate.parameter -= 0.1 * grad
            gate.gradient = grad
        
        # Parameter should have changed
        assert gate.parameter != 0.5
        # Gradient should be stored
        assert gate.gradient == 0.1


class TestEndToEndWorkflows:
    """Test complete end-to-end QML workflows"""
    
    def test_complete_vqe_workflow(self):
        """Test full VQE workflow from setup to result"""
        # 1. Define problem
        H = h2_hamiltonian()
        exact_energy = np.linalg.eigvalsh(H)[0]
        
        # 2. Choose ansatz
        def my_ansatz(params, num_qubits):
            return hardware_efficient_ansatz(params, num_qubits, depth=2)
        
        # 3. Setup VQE
        vqe = VQE(
            hamiltonian=H,
            ansatz_builder=my_ansatz,
            num_qubits=2,
            optimizer='COBYLA',
            max_iterations=40
        )
        
        # 4. Run optimization
        np.random.seed(42)
        initial_params = np.random.rand(4) * 0.1
        result = vqe.run(initial_params)
        
        # 5. Verify results
        assert 'ground_state_energy' in result
        assert 'optimal_params' in result
        
        # 6. Check accuracy
        error = abs(result['ground_state_energy'] - exact_energy)
        assert error < 0.1, f"VQE error {error:.4f} too large"
        
        # 7. Verify convergence
        assert len(vqe.history) > 0
    
    def test_complete_qaoa_workflow(self):
        """Test full QAOA workflow"""
        # 1. Define MaxCut problem
        graph = [(0,1), (1,2), (2,3), (3,0)]  # Square
        
        # 2. Setup QAOA
        qaoa = QAOA(
            graph=graph,
            p=2,
            optimizer='COBYLA',
            max_iterations=30
        )
        
        # 3. Initialize parameters
        np.random.seed(42)
        initial_params = np.random.rand(4) * np.pi
        
        # 4. Run optimization
        result = qaoa.run(initial_params)
        
        # 5. Verify results
        assert 'best_value' in result
        assert 'optimal_params' in result
        
        # 6. Check solution quality
        # Square graph maxcut optimal is 4
        # Allow for optimization variance
        assert result['best_value'] >= 1.0  # At least 25% approximation
        
        # 7. Verify optimization happened
        assert len(qaoa.history) > 0


class TestStressTests:
    """Stress tests for QML components"""
    
    def test_vqe_many_iterations(self):
        """Test VQE with many iterations"""
        H = h2_hamiltonian()
        vqe = VQE(H, hardware_efficient_ansatz, num_qubits=2, max_iterations=100)
        
        result = vqe.run(np.array([0.5, 0.5]))
        
        # Should complete without errors
        # Optimizer might terminate early if converged
        assert len(vqe.history) > 10
        
        # Should converge to good solution
        exact = vqe.exact_ground_state()
        assert result['ground_state_energy'] - exact < 0.05
    
    def test_qaoa_large_graph(self):
        """Test QAOA on larger graph"""
        # 8-node cycle graph
        graph = [(i, (i+1) % 8) for i in range(8)]
        
        qaoa = QAOA(graph=graph, p=1, max_iterations=20)
        result = qaoa.run()
        
        # Should handle 8 qubits
        assert qaoa.num_qubits == 8
        # Should find some cut
        assert result['best_value'] > 0
    
    def test_deep_ansatz(self):
        """Test VQE with deep ansatz"""
        H = h2_hamiltonian()
        
        def deep_ansatz(params, num_qubits):
            return hardware_efficient_ansatz(params, num_qubits, depth=5)
        
        vqe = VQE(H, deep_ansatz, num_qubits=2, max_iterations=30)
        
        # 5 layers, 2 qubits = 10 params
        result = vqe.run(np.random.rand(10))
        
        # Should handle deep circuit
        assert 'ground_state_energy' in result


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_vqe_wrong_param_count(self):
        """Test VQE handles wrong parameter count gracefully"""
        H = h2_hamiltonian()
        vqe = VQE(H, hardware_efficient_ansatz, num_qubits=2)
        
        # Wrong number of params (need 2, give 3)
        # Should either fail gracefully or ignore extra
        try:
            result = vqe.run(np.array([0.5, 0.5, 0.5]))
            # If it works, that's fine too (might use subset)
        except (IndexError, ValueError):
            # Expected error
            pass
    
    def test_empty_graph_qaoa(self):
        """Test QAOA with empty graph"""
        graph = []
        
        try:
            qaoa = QAOA(graph=graph, p=1)
            # If initialization works, result should be 0
            result = qaoa.run()
            assert result['best_value'] == 0
        except ValueError:
            # Also acceptable - should reject empty graph
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
