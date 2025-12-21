"""
Shared pytest configuration and fixtures for all tests
"""

import pytest
import numpy as np


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
