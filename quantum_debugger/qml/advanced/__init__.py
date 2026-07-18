"""
Advanced QML

Data re-uploading classifiers and ansatz-analysis diagnostics (expressibility,
entangling capability, barren-plateau gradient variance).
"""

from .data_reuploading import DataReuploadingClassifier
from .ansatz_analysis import (
    expressibility,
    entangling_capability,
    gradient_variance,
    n_params,
)

__all__ = [
    "DataReuploadingClassifier",
    "expressibility",
    "entangling_capability",
    "gradient_variance",
    "n_params",
]
