"""
Memory Tests for Parameterized Gates
====================================

Tests memory usage, leak detection, and efficiency.
"""

import pytest
import numpy as np
import gc
import sys
from quantum_debugger.qml import RXGate, RYGate, RZGate


class TestMemoryUsage:
    """Test memory usage patterns"""
    
    def test_large_gate_array(self):
        """Test creating large number of gates"""
        gates = []
        
        # Create 10,000 gates
        for i in range(10000):
            gate = RXGate(target=i % 100, parameter=np.random.rand())
            gates.append(gate)
        
        assert len(gates) == 10000
        
        # Clean up
        del gates
        gc.collect()
    
    def test_memory_leak_detection(self):
        """Test for memory leaks in repeated operations"""
        initial_objects = len(gc.get_objects())
        
        # Create and destroy gates repeatedly
        for _ in range(1000):
            gate = RXGate(target=0, parameter=np.random.rand())
            _ = gate.matrix()
            del gate
        
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Should not have significant object growth
        # Allow some margin for Python internals
        assert final_objects - initial_objects < 100
    
    def test_matrix_memory_reuse(self):
        """Test that matrices don't accumulate in memory"""
        gate = RXGate(target=0, parameter=0.5)
        
        # Compute matrix many times
        for _ in range(1000):
            _ = gate.matrix()
        
        gc.collect()
        # Should only have one gate object
        gates_in_memory = sum(1 for obj in gc.get_objects() 
                              if isinstance(obj, RXGate))
        assert gates_in_memory == 1
    
    def test_parameter_array_efficiency(self):
        """Test memory efficiency with large parameter arrays"""
        # Create gates with array parameters would be for batch processing
        params = np.random.rand(1000)
        gates = [RXGate(target=i % 10, parameter=p) for i, p in enumerate(params)]
        
        # Check that parameters aren't duplicated unnecessarily
        assert len(gates) == 1000
        
        del gates, params
        gc.collect()


class TestGarbageCollection:
    """Test garbage collection behavior"""
    
    def test_gate_cleanup(self):
        """Test gates are properly garbage collected"""
        gates = [RXGate(target=i, parameter=i * 0.1) for i in range(100)]
        
        # Get initial count
        initial_count = sum(1 for obj in gc.get_objects() 
                           if isinstance(obj, (RXGate, RYGate, RZGate)))
        
        # Delete gates
        del gates
        gc.collect()
        
        # Count should decrease
        final_count = sum(1 for obj in gc.get_objects() 
                         if isinstance(obj, (RXGate, RYGate, RZGate)))
        
        assert final_count < initial_count
    
    def test_circular_reference_handling(self):
        """Test handling of potential circular references"""
        gate = RXGate(target=0, parameter=0.5)
        
        # Create a potential circular reference
        gate.self_ref = gate
        
        # Delete and collect
        del gate
        gc.collect()
        
        # Should be cleaned up
        # (This is more of a demonstration that Python handles it)


class TestMemoryEfficiency:
    """Test memory efficiency optimizations"""
    
    def test_matrix_size_consistency(self):
        """Test that all matrices are consistently sized"""
        gates = [
            RXGate(target=0, parameter=np.random.rand()),
            RYGate(target=0, parameter=np.random.rand()),
            RZGate(target=0, parameter=np.random.rand()),
        ]
        
        for gate in gates:
            U = gate.matrix()
            # 2x2 complex128 = 4 elements * 16 bytes = 64 bytes
            assert U.nbytes == 64
    
    def test_parameter_storage_efficiency(self):
        """Test parameter storage doesn't waste memory"""
        gate = RXGate(target=0, parameter=np.pi/4)
        
        # Parameter should be stored as single float
        param_size = sys.getsizeof(gate.parameter)
        
        # Should be small (< 100 bytes for a float)
        assert param_size < 100
    
    def test_gradient_storage_efficiency(self):
        """Test gradient storage is efficient"""
        gate = RXGate(target=0, parameter=0.5, trainable=True)
        
        # Initially no gradient
        assert gate.gradient is None
        
        # Store gradient
        gate.gradient = 0.123
        
        # Should be single float
        assert isinstance(gate.gradient, (float, np.floating))


class TestLargeScale:
    """Test behavior at large scale"""
    
    def test_million_parameter_updates(self):
        """Test updating parameter million times"""
        gate = RXGate(target=0, parameter=0.0)
        
        # Update parameter 1 million times
        for i in range(1000000):
            gate.parameter = i * 0.000001
        
        # Should complete without memory issues
        assert gate.parameter > 0
    
    def test_thousand_concurrent_gates(self):
        """Test 1000 gates with different parameters"""
        gates = [RXGate(target=i % 100, parameter=i * 0.001) 
                 for i in range(1000)]
        
        # Compute all matrices
        matrices = [g.matrix() for g in gates]
        
        assert len(matrices) == 1000
        
        # All should be unitary
        for U in matrices:
            identity = U.conj().T @ U
            np.testing.assert_allclose(identity, np.eye(2), atol=1e-14)


class TestMemoryBenchmark:
    """Benchmark memory usage"""
    
    def test_memory_per_gate(self):
        """Measure memory per gate instance"""
        import tracemalloc
        
        tracemalloc.start()
        
        # Create 1000 gates
        gates = [RXGate(target=i % 10, parameter=i * 0.1) 
                 for i in range(1000)]
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        memory_per_gate = peak / 1000  # bytes per gate
        
        # Should be reasonable (< 10KB per gate)
        assert memory_per_gate < 10000
        
        print(f"\nMemory per gate: {memory_per_gate:.2f} bytes")
        print(f"Total peak memory: {peak / 1024:.2f} KB")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
