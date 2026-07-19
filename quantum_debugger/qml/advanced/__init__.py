"""
Advanced QML

Data re-uploading classifiers and ansatz-analysis diagnostics (expressibility,
entangling capability, barren-plateau gradient variance).
"""

from .data_reuploading import DataReuploadingClassifier
from .autoencoder import QuantumAutoencoder
from .qcnn import QCNN
from .vqc import VariationalQuantumClassifier
from .ansatz_analysis import (
    expressibility,
    entangling_capability,
    gradient_variance,
    n_params,
)

__all__ = [
    "DataReuploadingClassifier",
    "QuantumAutoencoder",
    "QCNN",
    "VariationalQuantumClassifier",
    "expressibility",
    "entangling_capability",
    "gradient_variance",
    "n_params",
]
