"""
Quantum Kernels Module

Provides quantum kernel methods for quantum machine learning,
including quantum SVM and kernel alignment.
"""

from .quantum_kernel import (
    QuantumKernel,
    FidelityKernel,
    ProjectedKernel,
    compute_gram_matrix,
    kernel_centering,
)

from .qsvm import QuantumSVM, train_qsvm

from .alignment import (
    kernel_target_alignment,
    centered_kernel_alignment,
    optimize_feature_map,
    evaluate_kernel_quality,
)

__all__ = [
    "QuantumKernel",
    "FidelityKernel",
    "ProjectedKernel",
    "compute_gram_matrix",
    "kernel_centering",
    "QuantumSVM",
    "train_qsvm",
    "kernel_target_alignment",
    "centered_kernel_alignment",
    "optimize_feature_map",
    "evaluate_kernel_quality",
]
