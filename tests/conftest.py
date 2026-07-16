"""
Shared pytest configuration and fixtures for all tests
"""

import pytest
import numpy as np

# Make pip-installed CUDA DLLs discoverable and initialize CuPy BEFORE any test
# file imports torch. conftest runs before collection, so this happens first.
# Rationale: (1) a failed early cupy import is cached by CuPy for the whole
# process; (2) importing torch first can shadow CuPy's nvrtc so its JIT targets
# the wrong GPU arch (NO_BINARY_FOR_GPU). Warming up CuPy here locks in the
# correct nvrtc path so the GPU tests pass regardless of later torch imports.
try:
    from quantum_debugger.backends._cuda_dll import ensure_cuda_dlls

    ensure_cuda_dlls()
    import cupy as _cp

    _ = int((_cp.arange(8) ** 2).sum())
    _cp.cuda.Stream.null.synchronize()
except Exception:
    pass


@pytest.fixture
def random_seed():
    """Set random seed for reproducible tests"""
    np.random.seed(42)
    return 42


@pytest.fixture
def small_circuit_size():
    """Standard small circuit size for quick tests"""
    return 2


@pytest.fixture
def medium_circuit_size():
    """Medium circuit size for moderate tests"""
    return 5


@pytest.fixture
def large_circuit_size():
    """Large circuit size for stress tests"""
    return 10


# Tolerance settings
TIGHT_TOLERANCE = 1e-10
NORMAL_TOLERANCE = 1e-6
LOOSE_TOLERANCE = 1e-3


@pytest.fixture
def tight_tol():
    """Tight numerical tolerance"""
    return TIGHT_TOLERANCE


@pytest.fixture
def normal_tol():
    """Normal numerical tolerance"""
    return NORMAL_TOLERANCE


@pytest.fixture
def loose_tol():
    """Loose tolerance for stochastic algorithms"""
    return LOOSE_TOLERANCE
