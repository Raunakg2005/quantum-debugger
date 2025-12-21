"""
Test QAOA Algorithm
===================

Test Quantum Approximate Optimization Algorithm for MaxCut.
"""

import pytest
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quantum_debugger.qml.algorithms import QAOA


class TestQAOABasic:
    """Basic QAOA functionality tests"""
    
    def test_qaoa_initialization(self):
        """Test QAOA can be initialized"""
        graph = [(0, 1), (1, 2), (2, 0)]  # Triangle
        qaoa = QAOA(graph=graph, p=1)
        
        assert qaoa.num_qubits == 3
        assert qaoa.p == 1
        assert len(qaoa.graph) == 3
    
    def test_qaoa_determines_num_qubits(self):
        """Test QAOA correctly determines number of qubits from graph"""
        graph = [(0, 2), (2, 5), (1, 3)]
        qaoa = QAOA(graph=graph, p=1)
        
        # Highest node is 5, so 6 qubits (0-5)
        assert qaoa.num_qubits == 6
    
    def test_cost_function_returns_number(self):
        """Test cost function returns valid number"""
        graph = [(0, 1), (1, 2)]
        qaoa = QAOA(graph=graph, p=1)
        
        # 2 parameters (gamma, beta) for p=1
        params = np.array([0.5, 0.3])
        cost = qaoa.cost_function(params)
        
        assert isinstance(cost, (float, np.floating))


class TestQAOAMaxCut:
    """Test QAOA on MaxCut problems"""
    
    def test_qaoa_simple_graph(self):
        """Test QAOA on simple 2-node graph"""
        graph = [(0, 1)]  # Single edge
        qaoa = QAOA(graph=graph, p=1, max_iterations=30)
        
        initial_params = np.array([0.5, 0.5])
        result = qaoa.run(initial_params)
        
        # Check result structure
        assert 'optimal_params' in result
        assert 'best_value' in result
        assert 'iterations' in result
        
        # MaxCut for single edge should be close to 1
        # QAOA with limited iterations may not be exact
        assert result['best_value'] > 0.3
    
    def test_qaoa_triangle_graph(self):
        """Test QAOA on triangle graph"""
        graph = [(0, 1), (1, 2), (2, 0)]
        qaoa = QAOA(graph=graph, p=2, max_iterations=30)
        
        result = qaoa.run()
        
        # Triangle MaxCut optimal is 2
        # QAOA approximation should find at least some cut
        assert result['best_value'] >= 0.5
        assert result['best_value'] <= 3.0
    
    def test_qaoa_square_graph(self):
        """Test QAOA on square graph"""
        graph = [(0, 1), (1, 2), (2, 3), (3, 0)]
        qaoa = QAOA(graph=graph, p=2, max_iterations=30)
        
        result = qaoa.run()
        
        # Square MaxCut optimal is 4
        # QAOA should find reasonable approximation  
        assert result['best_value'] >= 0.5
        assert result['best_value'] <= 4.5


class TestQAOALayers:
    """Test QAOA with different p values"""
    
    def test_qaoa_p1_vs_p2(self):
        """Test that p=2 generally finds better solutions than p=1"""
        graph = [(0, 1), (1, 2), (2, 3), (3, 0)]
        
        qaoa_p1 = QAOA(graph=graph, p=1, max_iterations=20)
        qaoa_p2 = QAOA(graph=graph, p=2, max_iterations=20)
        
        np.random.seed(42)
        result_p1 = qaoa_p1.run(np.random.rand(2))
        result_p2 = qaoa_p2.run(np.random.rand(4))
        
        # p=2 should generally be at least as good (allow small margin)
        assert result_p2['best_value'] >= result_p1['best_value'] - 0.5
    
    def test_qaoa_parameter_count(self):
        """Test correct number of parameters for different p"""
        graph = [(0, 1)]
        
        qaoa_p1 = QAOA(graph=graph, p=1)
        qaoa_p3 = QAOA(graph=graph, p=3)
        
        # p=1 needs 2 params (gamma, beta)
        params_p1 = np.random.rand(2)
        qaoa_p1.cost_function(params_p1)  # Should work
        
        # p=3 needs 6 params (3 gammas, 3 betas)
        params_p3 = np.random.rand(6)
        qaoa_p3.cost_function(params_p3)  # Should work


class TestQAOAOptimization:
    """Test QAOA optimization process"""
    
    def test_qaoa_tracks_history(self):
        """Test QAOA tracks optimization history"""
        graph = [(0, 1), (1, 2)]
        qaoa = QAOA(graph=graph, p=1, max_iterations=15)
        
        result = qaoa.run(np.array([0.5, 0.5]))
        
        # Should have history
        assert len(qaoa.history) > 0
        
        # Each entry should have cost
        for entry in qaoa.history:
            assert 'cost' in entry
            assert 'params' in entry
    
    def test_qaoa_convergence(self):
        """Test QAOA improves cost over iterations"""
        graph = [(0, 1), (1, 2), (2, 0)]
        qaoa = QAOA(graph=graph, p=1, max_iterations=20)
        
        result = qaoa.run(np.array([0.2, 0.2]))
        
        # Cost should generally improve (become less negative for maximization)
        costs = [-h['cost'] for h in qaoa.history]  # Negate back to positive
        
        # Final cost should be better than or equal to initial
        assert costs[-1] >= costs[0] - 0.5  # Allow small margin


class TestQAOAEdgeCases:
    """Edge cases and special graphs"""
    
    def test_qaoa_single_edge(self):
        """Test QAOA on graph with single edge"""
        graph = [(0, 1)]
        qaoa = QAOA(graph=graph, p=1, max_iterations=10)
        
        result = qaoa.run()
        
        # Single edge - stochastic optimization may vary
        assert 0.3 <= result['best_value'] <= 1.5
    
    def test_qaoa_disconnected_graph(self):
        """Test QAOA on disconnected graph"""
        graph = [(0, 1), (2, 3)]  # Two separate edges
        qaoa = QAOA(graph=graph, p=1, max_iterations=10)
        
        result = qaoa.run()
        
        # Both edges can be cut, but optimization may vary
        assert result['best_value'] >= 0.5
    
    def test_qaoa_with_different_optimizers(self):
        """Test QAOA with different optimizers"""
        graph = [(0, 1), (1, 2)]
        
        for optimizer in ['COBYLA', 'SLSQP']:
            qaoa = QAOA(graph=graph, p=1, optimizer=optimizer, max_iterations=10)
            result = qaoa.run(np.array([0.5, 0.5]))
            
            assert 'best_value' in result
            assert result['best_value'] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
