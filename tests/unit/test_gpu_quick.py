"""Quick GPU Backend Test"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from quantum_debugger.backends import get_backend, list_available_backends


def test_gpu_backend_availability():
    """Test GPU backend availability and basic operations"""
    # Check available backends
    backends = list_available_backends()
    assert 'cupy' in backends, "CuPy backend should be listed"
    
    # Test GPU backend if available
    if backends.get('cupy', False):
        gpu = get_backend('gpu')
        assert gpu is not None, "GPU backend should be available"
        assert hasattr(gpu, 'name'), "GPU backend should have name"
        assert hasattr(gpu, 'device_id'), "GPU backend should have device_id"
        
        # Test memory info
        mem = gpu.memory_info()
        assert 'total_mb' in mem, "Memory info should include total_mb"
        assert 'free_mb' in mem, "Memory info should include free_mb"
        assert 'used_mb' in mem, "Memory info should include used_mb"
        
        # Quick operation test
        a = gpu.eye(4)
        b = gpu.matmul(a, a)
        assert b is not None, "Matrix operations should work"
    else:
        pytest.skip("CuPy not available - GPU backend not installed")
