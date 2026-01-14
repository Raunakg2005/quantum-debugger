"""
Parallel execution module

Provides parallel shot execution for faster quantum simulations.
"""

from .executor import ParallelExecutor, run_parallel

__all__ = [
    "ParallelExecutor",
    "run_parallel",
]
