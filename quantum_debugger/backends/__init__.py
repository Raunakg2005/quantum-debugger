"""
Backend management and auto-selection

Provides get_backend() for automatic backend selection.
"""

from .base import Backend
from .numpy_backend import NumPyBackend

# Import optional backends
try:
    from .numba_backend import NumbaBackend, HAS_NUMBA
except ImportError:
    HAS_NUMBA = False

try:
    from .sparse_backend import SparseBackend
    HAS_SPARSE = True
except ImportError:
    HAS_SPARSE = False

try:
    from .cupy_backend import CuPyBackend, HAS_CUPY
except ImportError:
    HAS_CUPY = False

# Global backend cache
_backend_cache = {}


def get_backend(name='auto'):
    """
    Get computational backend by name.
    
    Args:
        name: Backend name ('auto', 'numpy', 'numba', 'sparse', 'cupy')
              'auto' selects best available backend
    
    Returns:
        Backend instance
        
    Example:
        >>> backend = get_backend('numba')
        >>> backend = get_backend()  # Auto-select
    """
    if name in _backend_cache:
        return _backend_cache[name]
    
    if name == 'auto':
        # Auto-select best available
        if HAS_NUMBA:
            backend = NumbaBackend()
        else:
            backend = NumPyBackend()
    
    elif name == 'numpy':
        backend = NumPyBackend()
    
    elif name == 'numba':
        if not HAS_NUMBA:
            raise ImportError(
                "Numba not available. Install with: pip install numba\n"
                "Falling back to NumPy..."
            )
        backend = NumbaBackend()
    
    elif name == 'sparse':
        if not HAS_SPARSE:
            raise ImportError(
                "SciPy not available. Install with: pip install scipy"
            )
        backend = SparseBackend()
    
    elif name == 'cupy' or name == 'gpu':
        if not HAS_CUPY:
            raise ImportError(
                "CuPy not available. For GPU acceleration, install with:\n"
                "  pip install cupy-cuda12x  # CUDA 12.x\n"
                "  pip install cupy-cuda11x  # CUDA 11.x\n"
                "Check https://docs.cupy.dev/en/stable/install.html"
            )
        backend = CuPyBackend()
    
    else:
        raise ValueError(
            f"Unknown backend '{name}'. "
            f"Available: 'auto', 'numpy', 'numba', 'sparse'"
        )
    
    _backend_cache[name] = backend
    return backend


def list_available_backends():
    """
    List all available backends on this system.
    
    Returns:
        dict: Backend name -> availability status
    """
    backends = {
        'numpy': True,  # Always available
        'numba': HAS_NUMBA,
        'sparse': HAS_SPARSE,
        'cupy': HAS_CUPY,
    }
    
    return backends


__all__ = [
    'Backend',
    'NumPyBackend',
    'get_backend',
    'list_available_backends',
]

if HAS_NUMBA:
    __all__.append('NumbaBackend')

if HAS_SPARSE:
    __all__.append('SparseBackend')

if HAS_CUPY:
    __all__.append('CuPyBackend')

# Add GPU backend
try:
    from .gpu_backend import (
        GPUBackend,
        get_optimal_backend,
        benchmark_backends
    )
    __all__.extend(['GPUBackend', 'get_optimal_backend', 'benchmark_backends'])
except ImportError:
    pass

# Add hardware backends (quantum computers)
try:
    from .ibm_backend import IBMQuantumBackend, IBM_AVAILABLE
    from .aws_backend import AWSBraketBackend, AWS_AVAILABLE
    from .base_backend import QuantumBackend
    
    __all__.extend(['IBMQuantumBackend', 'AWSBraketBackend', 'QuantumBackend'])
    
    def get_available_backends():
        """Get list of available quantum backends."""
        backends = []
        if IBM_AVAILABLE:
            backends.append('ibm')
        if AWS_AVAILABLE:
            backends.append('aws')
        return backends
    
    __all__.append('get_available_backends')
    
except ImportError:
    # Hardware backends not installed
    def get_available_backends():
        return []
    __all__.append('get_available_backends')
