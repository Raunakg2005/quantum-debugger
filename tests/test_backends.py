"""
Tests for hardware backends (without actual execution)

These tests verify the backend interfaces work correctly
WITHOUT requiring API keys or incurring costs.
"""

import pytest
import numpy as np

from quantum_debugger.backends import get_available_backends
from quantum_debugger.backends.base_backend import QuantumBackend


class TestBackendAvailability:
    """Test backend detection and availability"""
    
    def test_get_available_backends(self):
        """Test getting list of available backends"""
        backends = get_available_backends()
        
        # Should return a list
        assert isinstance(backends, list)
    
    def test_backend_imports(self):
        """Test that backend classes can be imported"""
        # These should not raise ImportError
        from quantum_debugger.backends import IBMQuantumBackend, AWSBraketBackend
        
        assert IBMQuantumBackend is not None
        assert AWSBraketBackend is not None


class TestIBMBackend:
    """Test IBM Quantum backend interface (no execution)"""
    
    def test_ibm_backend_initialization(self):
        """Test IBM backend can be instantiated"""
        try:
            from quantum_debugger.backends import IBMQuantumBackend
            backend = IBMQuantumBackend()
            
            assert backend.name == "ibm_quantum"
            assert not backend.is_connected
            
        except ImportError:
            pytest.skip("qiskit-ibm-runtime not installed")
    
    def test_ibm_free_tier_info(self):
        """Test getting free tier information"""
        try:
            from quantum_debugger.backends import IBMQuantumBackend
            backend = IBMQuantumBackend()
            
            info = backend.get_free_tier_info()
            
            assert 'monthly_limit_minutes' in info
            assert info['monthly_limit_minutes'] == 10
            assert info['cost_per_minute'] == 0.0
            
        except ImportError:
            pytest.skip("qiskit-ibm-runtime not installed")
    
    def test_ibm_connect_requires_token(self):
        """Test that connect requires token"""
        try:
            from quantum_debugger.backends import IBMQuantumBackend
            backend = IBMQuantumBackend()
            
            with pytest.raises(ValueError, match="token required"):
                backend.connect({})  # No token
                
        except ImportError:
            pytest.skip("qiskit-ibm-runtime not installed")


class TestAWSBackend:
    """Test AWS Braket backend interface (no execution)"""
    
    def test_aws_backend_initialization(self):
        """Test AWS backend can be instantiated"""
        try:
            from quantum_debugger.backends import AWSBraketBackend
            backend = AWSBraketBackend()
            
            assert backend.name == "aws_braket"
            assert not backend.is_connected
            
        except ImportError:
            pytest.skip("amazon-braket-sdk not installed")
    
    def test_aws_cost_estimation(self):
        """Test cost estimation works"""
        try:
            from quantum_debugger.backends import AWSBraketBackend
            backend = AWSBraketBackend()
            
            # QPU cost
            qpu_cost = backend.estimate_cost(n_shots=1000, device_type='qpu')
            
            assert 'total_cost_usd' in qpu_cost
            assert qpu_cost['total_cost_usd'] > 0
            assert qpu_cost['per_task_fee'] == 0.30
            
            # Simulator cost (cheaper)
            sim_cost = backend.estimate_cost(n_shots=1000, device_type='simulator')
            
            assert sim_cost['total_cost_usd'] < qpu_cost['total_cost_usd']
            
        except ImportError:
            pytest.skip("amazon-braket-sdk not installed")
    
    def test_aws_connect_requires_credentials(self):
        """Test that connect requires full credentials"""
        try:
            from quantum_debugger.backends import AWSBraketBackend
            backend = AWSBraketBackend()
            
            with pytest.raises(ValueError, match="Missing required credentials"):
                backend.connect({'region': 'us-east-1'})  # Missing keys
                
        except ImportError:
            pytest.skip("amazon-braket-sdk not installed")


class TestBaseBackend:
    """Test base backend interface"""
    
    def test_base_backend_is_abstract(self):
        """Test that base backend cannot be instantiated directly"""
        with pytest.raises(TypeError):
            backend = QuantumBackend("test")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
