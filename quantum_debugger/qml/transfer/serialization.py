"""
Model serialization for saving and loading quantum models.

Supports multiple formats: pickle, JSON, and HDF5.
"""

import pickle
import json
import numpy as np
from pathlib import Path
from typing import Any, Union
import logging

logger = logging.getLogger(__name__)


def save_model(model, path: str, format: str = "pickle"):
    """
    Save PretrainedQNN model to disk.

    Args:
        model: PretrainedQNN instance to save
        path: File path to save to
        format: Serialization format ('pickle', 'json', 'hdf5')

    Raises:
        ValueError: If format is not supported
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if format == "pickle":
        _save_pickle(model, path)
    elif format == "json":
        _save_json(model, path)
    elif format == "hdf5":
        _save_hdf5(model, path)
    else:
        raise ValueError(
            f"Unsupported format: {format}. " f"Use 'pickle', 'json', or 'hdf5'"
        )

    logger.info(f"Model saved to {path} (format: {format})")


def load_model(path: str, format: str = "pickle"):
    """
    Load PretrainedQNN model from disk.

    Args:
        path: File path to load from
        format: Serialization format

    Returns:
        Loaded PretrainedQNN instance

    Raises:
        ValueError: If format is not supported
        FileNotFoundError: If file doesn't exist
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Model file not found: {path}")

    if format == "pickle":
        model = _load_pickle(path)
    elif format == "json":
        model = _load_json(path)
    elif format == "hdf5":
        model = _load_hdf5(path)
    else:
        raise ValueError(f"Unsupported format: {format}")

    logger.info(f"Model loaded from {path}")
    return model


def _save_pickle(model, path: Path):
    """Save using pickle format (default, fastest)."""
    with open(path, "wb") as f:
        pickle.dump(model, f, protocol=pickle.HIGHEST_PROTOCOL)


def _load_pickle(path: Path):
    """Load from pickle format."""
    with open(path, "rb") as f:
        return pickle.load(f)


def _save_json(model, path: Path):
    """Save using JSON format (human-readable)."""
    from .pretrained import PretrainedQNN

    # Convert to JSON-serializable format
    data = {
        "model_name": model.model_name,
        "config": model.config,
        "weights": model.weights.tolist(),  # Convert numpy to list
        "metadata": model.metadata,
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _load_json(path: Path):
    """Load from JSON format."""
    from .pretrained import PretrainedQNN

    with open(path, "r") as f:
        data = json.load(f)

    # Convert weights back to numpy
    data["weights"] = np.array(data["weights"])

    return PretrainedQNN(
        model_name=data["model_name"],
        config=data["config"],
        weights=data["weights"],
        metadata=data.get("metadata", {}),
    )


def _save_hdf5(model, path: Path):
    """Save using HDF5 format (for large models)."""
    try:
        import h5py
    except ImportError:
        raise ImportError(
            "h5py required for HDF5 format. Install with: pip install h5py"
        )

    with h5py.File(path, "w") as f:
        # Save model attributes
        f.attrs["model_name"] = model.model_name
        f.attrs["config"] = json.dumps(model.config)
        f.attrs["metadata"] = json.dumps(model.metadata)

        # Save weights as dataset
        f.create_dataset("weights", data=model.weights)


def _load_hdf5(path: Path):
    """Load from HDF5 format."""
    try:
        import h5py
    except ImportError:
        raise ImportError(
            "h5py required for HDF5 format. Install with: pip install h5py"
        )

    from .pretrained import PretrainedQNN

    with h5py.File(path, "r") as f:
        model_name = f.attrs["model_name"]
        config = json.loads(f.attrs["config"])
        metadata = json.loads(f.attrs["metadata"])
        weights = np.array(f["weights"])

    return PretrainedQNN(
        model_name=model_name, config=config, weights=weights, metadata=metadata
    )


def get_model_size(path: str) -> int:
    """
    Get model file size in bytes.

    Args:
        path: Path to model file

    Returns:
        File size in bytes
    """
    return Path(path).stat().st_size


def get_model_size_mb(path: str) -> float:
    """
    Get model file size in megabytes.

    Args:
        path: Path to model file

    Returns:
        File size in MB
    """
    return get_model_size(path) / (1024 * 1024)
