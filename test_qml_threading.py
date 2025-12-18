"""
Threading Safety Tests for Parameterized Gates
==============================================

Tests concurrent gate creation, parameter updates, and matrix computation.
"""

import pytest
import numpy as np
import threading
import time
from quantum_debugger.qml import RXGate, RYGate, RZGate


class TestThreadingSafety:
    """Test thread safety of parameterized gates"""
    
    def test_concurrent_gate_creation(self):
        """Test creating gates from multiple threads simultaneously"""
        gates = []
        errors = []
        
        def create_gates():
            try:
                for i in range(100):
                    gate = RXGate(target=i % 10, parameter=np.random.rand())
                    gates.append(gate)
            except Exception as e:
                errors.append(e)
        
        # Create 10 threads
        threads = [threading.Thread(target=create_gates) for _ in range(10)]
        
        # Start all threads
        for t in threads:
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # Should have 1000 gates with no errors
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(gates) == 1000
    
    def test_concurrent_matrix_computation(self):
        """Test computing matrices from multiple threads"""
        gate = RXGate(target=0, parameter=np.pi/4)
        results = []
        errors = []
        
        def compute_matrix():
            try:
                for _ in range(50):
                    U = gate.matrix()
                    results.append(U)
            except Exception as e:
                errors.append(e)
        
        # 5 threads computing same gate
        threads = [threading.Thread(target=compute_matrix) for _ in range(5)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0
        assert len(results) == 250
        
        # All matrices should be identical
        U0 = results[0]
        for U in results[1:]:
            np.testing.assert_array_equal(U, U0)
    
    def test_concurrent_parameter_updates(self):
        """Test updating parameters from multiple threads"""
        gate = RXGate(target=0, parameter=0.0)
        
        def update_parameters(value):
            for _ in range(100):
                gate.parameter = value
                time.sleep(0.0001)  # Small delay
        
        # Multiple threads updating to different values
        threads = [
            threading.Thread(target=update_parameters, args=(i * 0.1,))
            for i in range(5)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Final parameter should be close to one of the values
        expected_values = [0.0, 0.1, 0.2, 0.3, 0.4]
        assert any(np.isclose(gate.parameter, v, atol=1e-10) for v in expected_values)
    
    def test_concurrent_gradient_storage(self):
        """Test storing gradients from multiple threads"""
        gates = [RXGate(target=i, parameter=0.5, trainable=True) for i in range(10)]
        
        def store_gradients():
            for gate in gates:
                gate.gradient = np.random.rand()
                time.sleep(0.0001)
        
        threads = [threading.Thread(target=store_gradients) for _ in range(3)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All gates should have gradients
        for gate in gates:
            assert gate.gradient is not None
            assert isinstance(gate.gradient, (float, np.floating))


class TestRaceConditions:
    """Test for race conditions in concurrent operations"""
    
    def test_read_write_race(self):
        """Test concurrent read and write operations"""
        gate = RXGate(target=0, parameter=np.pi/3)
        read_results = []
        
        def reader():
            for _ in range(100):
                param = gate.parameter
                U = gate.matrix()
                read_results.append((param, U))
        
        def writer():
            for i in range(100):
                gate.parameter = i * 0.01
        
        # One writer, multiple readers
        writer_thread = threading.Thread(target=writer)
        reader_threads = [threading.Thread(target=reader) for _ in range(3)]
        
        writer_thread.start()
        for t in reader_threads:
            t.start()
        
        writer_thread.join()
        for t in reader_threads:
            t.join()
        
        # Should complete without errors
        assert len(read_results) == 300
    
    def test_matrix_computation_consistency(self):
        """Test that concurrent matrix computation gives consistent results"""
        gate = RXGate(target=0, parameter=0.789)
        matrices = []
        lock = threading.Lock()
        
        def compute_and_store():
            for _ in range(50):
                U = gate.matrix()
                with lock:
                    matrices.append(U)
        
        threads = [threading.Thread(target=compute_and_store) for _ in range(4)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All matrices should be identical
        U0 = matrices[0]
        for U in matrices:
            np.testing.assert_array_equal(U, U0)


class TestConcurrentTypes:
    """Test different gate types concurrently"""
    
    def test_mixed_gate_types(self):
        """Test RX, RY, RZ gates concurrently"""
        results = {'rx': [], 'ry': [], 'rz': []}
        
        def create_rx():
            for i in range(100):
                gate = RXGate(target=0, parameter=i * 0.01)
                results['rx'].append(gate.matrix())
        
        def create_ry():
            for i in range(100):
                gate = RYGate(target=0, parameter=i * 0.01)
                results['ry'].append(gate.matrix())
        
        def create_rz():
            for i in range(100):
                gate = RZGate(target=0, parameter=i * 0.01)
                results['rz'].append(gate.matrix())
        
        threads = [
            threading.Thread(target=create_rx),
            threading.Thread(target=create_ry),
            threading.Thread(target=create_rz),
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(results['rx']) == 100
        assert len(results['ry']) == 100
        assert len(results['rz']) == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
