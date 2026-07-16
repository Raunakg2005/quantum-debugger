"""
GPU Utilities

Multi-GPU support, mixed precision, and memory optimization.
"""

# Ensure pip-installed CUDA runtime DLLs are discoverable (Windows) before any
# CuPy import triggered by the modules below.
from ..backends._cuda_dll import ensure_cuda_dlls

ensure_cuda_dlls()

from .multi_gpu import MultiGPUManager, DataParallelQNN, ModelParallelQNN
from .mixed_precision import MixedPrecisionTrainer, enable_mixed_precision
from .memory import GPUMemoryManager, profile_memory

__all__ = [
    "MultiGPUManager",
    "DataParallelQNN",
    "ModelParallelQNN",
    "MixedPrecisionTrainer",
    "enable_mixed_precision",
    "GPUMemoryManager",
    "profile_memory",
]
