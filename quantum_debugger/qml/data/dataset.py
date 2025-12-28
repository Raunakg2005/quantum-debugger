"""
Dataset Loading and Management

Utilities for loading, preprocessing, and managing datasets for QML.
"""

import numpy as np
import csv
import json
from typing import Optional, Tuple, Dict, Any, Union
from pathlib import Path


class QuantumDataset:
    """
    Dataset container for quantum machine learning.
    
    Handles loading, preprocessing, and splitting of classical data
    for quantum machine learning tasks.
    
    Attributes:
        X: Feature data (N samples × D features)
        y: Labels (N samples)
        feature_names: Names of features
        metadata: Additional dataset information
    """
    
    def __init__(self, X: np.ndarray, y: Optional[np.ndarray] = None,
                 feature_names: Optional[list] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize dataset.
        
        Args:
            X: Feature matrix (N × D)
            y: Labels (N,) - optional for unsupervised learning
            feature_names: List of feature names
            metadata: Dictionary with dataset info
        """
        self.X = np.asarray(X)
        self.y = np.asarray(y) if y is not None else None
        self.feature_names = feature_names or [f"feature_{i}" for i in range(self.X.shape[1])]
        self.metadata = metadata or {}
        
        # Validate dimensions
        if self.y is not None and len(self.X) != len(self.y):
            raise ValueError(f"X and y must have same length: {len(self.X)} != {len(self.y)}")
    
    @property
    def n_samples(self) -> int:
        """Number of samples"""
        return len(self.X)
    
    @property
    def n_features(self) -> int:
        """Number of features"""
        return self.X.shape[1] if len(self.X.shape) > 1 else 1
    
    @property
    def shape(self) -> Tuple[int, int]:
        """Dataset shape (n_samples, n_features)"""
        return (self.n_samples, self.n_features)
    
    def train_test_split(self, test_size: float = 0.2, 
                         shuffle: bool = True,
                         random_state: Optional[int] = None) -> Tuple['QuantumDataset', 'QuantumDataset']:
        """
        Split dataset into training and testing sets.
        
        Args:
            test_size: Fraction of data for testing (0.0 to 1.0)
            shuffle: Whether to shuffle before splitting
            random_state: Random seed for reproducibility
            
        Returns:
            (train_dataset, test_dataset) tuple
        """
        if not 0 < test_size < 1:
            raise ValueError(f"test_size must be between 0 and 1, got {test_size}")
        
        n_samples = self.n_samples
        n_test = int(n_samples * test_size)
        n_train = n_samples - n_test
        
        # Create indices
        indices = np.arange(n_samples)
        if shuffle:
            if random_state is not None:
                np.random.seed(random_state)
            np.random.shuffle(indices)
        
        # Split indices
        train_indices = indices[:n_train]
        test_indices = indices[n_train:]
        
        # Create datasets
        train_dataset = QuantumDataset(
            X=self.X[train_indices],
            y=self.y[train_indices] if self.y is not None else None,
            feature_names=self.feature_names,
            metadata={**self.metadata, 'split': 'train'}
        )
        
        test_dataset = QuantumDataset(
            X=self.X[test_indices],
            y=self.y[test_indices] if self.y is not None else None,
            feature_names=self.feature_names,
            metadata={**self.metadata, 'split': 'test'}
        )
        
        return train_dataset, test_dataset
    
    def normalize(self, method: str = 'minmax') -> 'QuantumDataset':
        """
        Normalize features.
        
        Args:
            method: Normalization method:
                - 'minmax': Scale to [0, 1]
                - 'standard': Z-score normalization (mean=0, std=1)
                - 'maxabs': Scale by max absolute value
                
        Returns:
            New dataset with normalized features
        """
        X_norm = self.X.copy()
        
        if method == 'minmax':
            # Scale to [0, 1]
            X_min = X_norm.min(axis=0)
            X_max = X_norm.max(axis=0)
            X_range = X_max - X_min
            # Avoid division by zero
            X_range[X_range == 0] = 1.0
            X_norm = (X_norm - X_min) / X_range
            
        elif method == 'standard':
            # Z-score: (x - mean) / std
            X_mean = X_norm.mean(axis=0)
            X_std = X_norm.std(axis=0)
            # Avoid division by zero
            X_std[X_std == 0] = 1.0
            X_norm = (X_norm - X_mean) / X_std
            
        elif method == 'maxabs':
            # Scale by maximum absolute value
            X_max_abs = np.abs(X_norm).max(axis=0)
            X_max_abs[X_max_abs == 0] = 1.0
            X_norm = X_norm / X_max_abs
            
        else:
            raise ValueError(f"Unknown normalization method: {method}")
        
        return QuantumDataset(
            X=X_norm,
            y=self.y,
            feature_names=self.feature_names,
            metadata={**self.metadata, 'normalized': method}
        )
    
    def __len__(self) -> int:
        """Number of samples"""
        return self.n_samples
    
    def __repr__(self) -> str:
        """String representation"""
        return (f"QuantumDataset(n_samples={self.n_samples}, "
                f"n_features={self.n_features}, "
                f"has_labels={self.y is not None})")


def load_csv(filepath: Union[str, Path],
             feature_columns: Optional[list] = None,
             label_column: Optional[str] = None,
             has_header: bool = True) -> QuantumDataset:
    """
    Load dataset from CSV file.
    
    Args:
        filepath: Path to CSV file
        feature_columns: List of column indices/names for features (None = all except label)
        label_column: Column index/name for labels
        has_header: Whether CSV has header row
        
    Returns:
        QuantumDataset object
        
    Example:
        >>> dataset = load_csv('data.csv', label_column='class')
        >>> print(dataset.shape)
        (100, 4)
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # Read CSV
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        if has_header:
            header = next(reader)
        else:
            header = None
        data = list(reader)
    
    # Convert to numpy - handle empty or single-row edge cases
    if len(data) == 0:
        raise ValueError("CSV file is empty")
    
    # Convert each row to floats
    data_floats = []
    for row in data:
        try:
            data_floats.append([float(x) for x in row])
        except ValueError as e:
            raise ValueError(f"Could not convert data to float: {e}")
    
    data = np.array(data_floats)
    
    # Extract features and labels
    if label_column is not None:
        if isinstance(label_column, str):
            if header is None:
                raise ValueError("Cannot use column name without header")
            label_idx = header.index(label_column)
        else:
            label_idx = label_column
        
        y = data[:, label_idx]
        X = np.delete(data, label_idx, axis=1)
        
        if header:
            feature_names = [h for i, h in enumerate(header) if i != label_idx]
        else:
            feature_names = None
    else:
        X = data
        y = None
        feature_names = header
    
    return QuantumDataset(
        X=X,
        y=y,
        feature_names=feature_names,
        metadata={'source': str(filepath), 'format': 'csv'}
    )


def load_json(filepath: Union[str, Path]) -> QuantumDataset:
    """
    Load dataset from JSON file.
    
    Expected format:
    {
        "data": [[x1, x2, ...], [x1, x2, ...], ...],
        "labels": [y1, y2, ...],  # optional
        "feature_names": ["f1", "f2", ...]  # optional
    }
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        QuantumDataset object
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with open(filepath, 'r') as f:
        data_dict = json.load(f)
    
    X = np.array(data_dict['data'])
    y = np.array(data_dict.get('labels')) if 'labels' in data_dict else None
    feature_names = data_dict.get('feature_names')
    
    return QuantumDataset(
        X=X,
        y=y,
        feature_names=feature_names,
        metadata={'source': str(filepath), 'format': 'json'}
    )


def load_numpy(X: np.ndarray, y: Optional[np.ndarray] = None) -> QuantumDataset:
    """
    Create dataset from NumPy arrays.
    
    Args:
        X: Feature array
        y: Label array (optional)
        
    Returns:
        QuantumDataset object
    """
    return QuantumDataset(X=X, y=y, metadata={'format': 'numpy'})
