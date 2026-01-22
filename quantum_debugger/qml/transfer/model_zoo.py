"""
Model Zoo - Registry of pre-trained quantum neural networks.

Provides easy access to pre-trained models for transfer learning.
"""

import os
from pathlib import Path
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

# Get the models directory
MODELS_DIR = Path(__file__).parent.parent.parent.parent / "models"
MODELS_DIR.mkdir(exist_ok=True)

# Model Registry
MODEL_REGISTRY = {
    "mnist_qnn": {
        "path": str(MODELS_DIR / "mnist_qnn.pkl"),
        "dataset": "MNIST (binary: 0 vs 1)",
        "task": "binary_classification",
        "n_qubits": 4,
        "n_layers": 2,
        "input_dim": 64,  # 8x8 downsampled
        "output_dim": 2,
        "target_accuracy": 0.98,
        "description": "Binary classifier for MNIST digits 0 and 1",
    },
    "fashion_mnist_qnn": {
        "path": str(MODELS_DIR / "fashion_mnist_qnn.pkl"),
        "dataset": "Fashion-MNIST (T-shirt vs Trouser)",
        "task": "binary_classification",
        "n_qubits": 4,
        "n_layers": 2,
        "input_dim": 64,
        "output_dim": 2,
        "target_accuracy": 0.95,
        "description": "Binary classifier for T-shirt vs Trouser",
    },
    "iris_qnn": {
        "path": str(MODELS_DIR / "iris_qnn.pkl"),
        "dataset": "Iris (3-class)",
        "task": "multiclass_classification",
        "n_qubits": 4,
        "n_layers": 2,
        "input_dim": 4,  # 4 features
        "output_dim": 3,  # 3 classes
        "target_accuracy": 0.97,
        "description": "Multi-class classifier for Iris dataset",
    },
    "wine_qnn": {
        "path": str(MODELS_DIR / "wine_qnn.pkl"),
        "dataset": "Wine Quality (good vs bad)",
        "task": "binary_classification",
        "n_qubits": 4,
        "n_layers": 2,
        "input_dim": 13,  # 13 features
        "output_dim": 2,
        "target_accuracy": 0.88,
        "description": "Wine quality binary classifier",
    },
    "digits_qnn": {
        "path": str(MODELS_DIR / "digits_qnn.pkl"),
        "dataset": "Sklearn Digits (0 vs 1)",
        "task": "binary_classification",
        "n_qubits": 4,
        "n_layers": 2,
        "input_dim": 64,  # 8x8 images
        "output_dim": 2,
        "target_accuracy": 0.99,
        "description": "Binary classifier for handwritten digits 0 and 1",
    },
}


def list_models() -> List[str]:
    """
    List all available pre-trained models.

    Returns:
        List of model names

    Example:
        >>> from quantum_debugger.qml.transfer import list_models
        >>> models = list_models()
        >>> print(models)
        ['mnist_qnn', 'fashion_mnist_qnn', 'iris_qnn', 'wine_qnn', 'digits_qnn']
    """
    return list(MODEL_REGISTRY.keys())


def get_model_info(model_name: str) -> Dict:
    """
    Get detailed information about a model.

    Args:
        model_name: Name of the model

    Returns:
        Dictionary with model information

    Raises:
        ValueError: If model name not found

    Example:
        >>> info = get_model_info('mnist_qnn')
        >>> print(info['dataset'])
        MNIST (binary: 0 vs 1)
    """
    if model_name not in MODEL_REGISTRY:
        available = ", ".join(list_models())
        raise ValueError(
            f"Model '{model_name}' not found. " f"Available models: {available}"
        )

    return MODEL_REGISTRY[model_name].copy()


def load_pretrained(model_name: str, format: str = "pickle"):
    """
    Load a pre-trained model by name.

    Args:
        model_name: Name of the model to load
        format: Serialization format (default: 'pickle')

    Returns:
        PretrainedQNN instance

    Raises:
        ValueError: If model name not found
        FileNotFoundError: If model file doesn't exist

    Example:
        >>> from quantum_debugger.qml.transfer import load_pretrained
        >>> model = load_pretrained('mnist_qnn')
        >>> predictions = model.predict(X_test)
    """
    if model_name not in MODEL_REGISTRY:
        available = ", ".join(list_models())
        raise ValueError(
            f"Model '{model_name}' not found. " f"Available models: {available}"
        )

    model_info = MODEL_REGISTRY[model_name]
    model_path = model_info["path"]

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model file not found: {model_path}\n"
            f"You may need to train the models first using:\n"
            f"python scripts/train_pretrained_models.py"
        )

    from .serialization import load_model

    model = load_model(model_path, format=format)

    logger.info(f"Loaded pre-trained model '{model_name}' from {model_path}")
    return model


def model_exists(model_name: str) -> bool:
    """
    Check if a pre-trained model file exists.

    Args:
        model_name: Name of the model

    Returns:
        True if model file exists, False otherwise
    """
    if model_name not in MODEL_REGISTRY:
        return False

    model_path = MODEL_REGISTRY[model_name]["path"]
    return os.path.exists(model_path)


def get_available_models() -> List[str]:
    """
    Get list of models that have been trained (files exist).

    Returns:
        List of available model names
    """
    return [name for name in list_models() if model_exists(name)]


def print_model_zoo():
    """Print formatted table of all models in the zoo."""
    print("\n" + "=" * 80)
    print(" " * 25 + "QUANTUM MODEL ZOO")
    print("=" * 80)
    print(f"{'Model Name':<20} {'Dataset':<30} {'Qubits':<8} {'Trained'}")
    print("-" * 80)

    for name in list_models():
        info = MODEL_REGISTRY[name]
        dataset = info["dataset"]
        qubits = info["n_qubits"]
        exists = "✓" if model_exists(name) else "✗"

        print(f"{name:<20} {dataset:<30} {qubits:<8} {exists}")

    print("=" * 80)
    available = len(get_available_models())
    total = len(list_models())
    print(f"\nAvailable: {available}/{total} models trained")
    print("\nTo train models: python scripts/train_pretrained_models.py")
    print()
