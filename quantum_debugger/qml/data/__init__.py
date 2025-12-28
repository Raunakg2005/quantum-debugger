"""
Data module for quantum machine learning
"""

from .dataset import QuantumDataset, load_csv, load_json, load_numpy
from .feature_maps import (
    zz_feature_map,
    pauli_feature_map,
    angle_encoding,
    amplitude_encoding,
    get_feature_map,
)

__all__ = [
    # Dataset
    'QuantumDataset',
    'load_csv',
    'load_json',
    'load_numpy',
    # Feature maps
    'zz_feature_map',
    'pauli_feature_map',
    'angle_encoding',
    'amplitude_encoding',
    'get_feature_map',
]
