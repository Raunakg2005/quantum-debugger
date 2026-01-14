"""
Tests for benchmarking suite
"""

import pytest
import numpy as np

from quantum_debugger.benchmarks import (
    benchmark_qnn,
    benchmark_optimization,
    scalability_analysis,
    generate_benchmark_report
)


class TestQMLBenchmarks:
    """Test QML benchmarking tools"""
    
    def test_benchmark_qnn(self):
        """Test QNN benchmarking"""
        results = benchmark_qnn(
            n_qubits=2,
            n_layers=2,
            dataset_size=20,
            epochs=2
        )
        
        assert 'train_time' in results
        assert 'inference_time' in results
        assert 'accuracy' in results
        assert results['n_qubits'] == 2
        assert results['train_time'] > 0
    
    def test_compare_with_classical(self):
        """Test QML vs classical comparison"""
        from quantum_debugger.benchmarks import compare_with_classical
        
        results = compare_with_classical(
            n_qubits=2,
            dataset_size=20
        )
        
        assert 'qnn' in results
        assert 'classical' in results
        assert 'speedup' in results
        assert results['qnn']['train_time'] > 0
        assert results['classical']['train_time'] > 0


class TestOptimizationBenchmarks:
    """Test optimization benchmarking"""
    
    def test_benchmark_optimization(self):
        """Test circuit optimization benchmarking"""
        gates = [('h', 0), ('h', 0), ('x', 1)]
        
        results = benchmark_optimization(gates, optimization_level=2)
        
        assert 'original_gates' in results
        assert 'optimized_gates' in results
        assert 'reduction_percentage' in results
        assert results['original_gates'] == 3
        assert results['optimized_gates'] <= results['original_gates']
    
    def test_benchmark_transpilation(self):
        """Test transpilation benchmarking"""
        from quantum_debugger.benchmarks import benchmark_transpilation
        
        gates = [('h', 0), ('cnot', (0, 1))]
        topology = {'edges': [(0, 1), (1, 2)], 'n_qubits': 3}
        
        results = benchmark_transpilation(gates, topology)
        
        assert 'original_gates' in results
        assert 'transpiled_gates' in results
        assert 'transpile_time' in results


class TestScalabilityBenchmarks:
    """Test scalability analysis"""
    
    def test_scalability_analysis(self):
        """Test scalability analysis"""
        results = scalability_analysis(
            n_qubits_range=[2, 4],
            algorithm='qnn',
            epochs=2
        )
        
        assert 2 in results
        assert 4 in results
        assert results[2]['time'] > 0
        assert results[4]['time'] > 0
    
    def test_memory_profiling(self):
        """Test memory profiling"""
        from quantum_debugger.benchmarks import memory_profiling
        
        results = memory_profiling([2, 4])
        
        assert 2 in results
        assert 4 in results
        assert results[2]['state_vector_mb'] > 0
        assert results[4]['state_vector_mb'] > results[2]['state_vector_mb']


class TestReportGeneration:
    """Test report generation"""
    
    def test_generate_benchmark_report(self):
        """Test benchmark report generation"""
        # Create mock results
        results = {
            'benchmarks': [
                {
                    'qnn': {
                        'n_qubits': 2,
                        'train_time': 1.5,
                        'accuracy': 0.85
                    },
                    'comparison': {
                        'classical': {'train_time': 0.5, 'accuracy': 0.80},
                        'speedup': 0.33
                    }
                }
            ]
        }
        
        report_path = generate_benchmark_report(results, 'test_report.md')
        
        # Verify report was created
        from pathlib import Path
        assert Path(report_path).exists()
        
        # Clean up
        Path(report_path).unlink()


class TestBenchmarkSuite:
    """Test complete benchmark suite"""
    
    def test_quick_benchmark_suite(self):
        """Test running quick benchmark suite"""
        from quantum_debugger.benchmarks import benchmark_suite
        
        results = benchmark_suite(quick=True)
        
        assert 'benchmarks' in results
        assert len(results['benchmarks']) >= 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
