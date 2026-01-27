"""
Fine-tuning utilities for transfer learning.

Provides functions to fine-tune pre-trained models on new data,
freeze layers, and transfer weights between models.
"""

import numpy as np
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


def fine_tune_model(
    pretrained_model,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: Optional[np.ndarray] = None,
    y_val: Optional[np.ndarray] = None,
    freeze_layers: Optional[List[int]] = None,
    learning_rate: float = 0.01,
    epochs: int = 10,
    batch_size: int = 32,
    early_stopping: bool = False,
    patience: int = 5,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Fine-tune a pre-trained model on new data.

    Args:
        pretrained_model: PretrainedQNN instance
        X_train: Training features (n_samples, n_features)
        y_train: Training labels (n_samples,)
        X_val: Optional validation features
        y_val: Optional validation labels
        freeze_layers: Layer indices to freeze (not update)
        learning_rate: Learning rate for optimization
        epochs: Number of training epochs
        batch_size: Batch size for training
        early_stopping: Enable early stopping
        patience: Epochs to wait before stopping
        verbose: Print progress

    Returns:
        Dictionary with training history:
        - 'train_loss': Training loss per epoch
        - 'train_acc': Training accuracy per epoch
        - 'val_loss': Validation loss per epoch (if validation data provided)
        - 'val_acc': Validation accuracy per epoch
        - 'best_epoch': Best epoch number

    Example:
        >>> from quantum_debugger.qml.transfer import load_pretrained, fine_tune_model
        >>> model = load_pretrained('mnist_qnn')
        >>> history = fine_tune_model(
        ...     model,
        ...     X_new_train,
        ...     y_new_train,
        ...     freeze_layers=[0],  # Freeze first layer
        ...     epochs=20
        ... )
    """
    logger.info(f"Fine-tuning '{pretrained_model.model_name}' for {epochs} epochs...")

    if freeze_layers:
        logger.info(f"Freezing layers: {freeze_layers}")
        # TODO: Implement layer freezing when we have layer-wise parameters

    # Train using the model's fine_tune method
    history = pretrained_model.fine_tune(
        X_train=X_train,
        y_train=y_train,
        epochs=epochs,
        learning_rate=learning_rate,
        batch_size=batch_size,
        freeze_layers=freeze_layers,
        verbose=verbose,
    )

    # Add validation metrics if provided
    if X_val is not None and y_val is not None:
        val_acc = pretrained_model.score(X_val, y_val)
        history["val_accuracy"] = val_acc
        logger.info(f"Validation accuracy: {val_acc:.4f}")

    return history


def transfer_weights(
    source_model, target_model, layer_mapping: Optional[Dict[int, int]] = None
):
    """
    Transfer weights from source model to target model.

    Args:
        source_model: Source PretrainedQNN model
        target_model: Target PretrainedQNN model
        layer_mapping: Optional mapping of source layers to target layers
                      e.g., {0: 0, 1: 1} maps source layer 0 to target layer 0
                      If None, copies all compatible layers

    Example:
        >>> source = load_pretrained('mnist_qnn')
        >>> target = PretrainedQNN(...)
        >>> transfer_weights(source, target, layer_mapping={0: 0, 1: 2})
    """
    if layer_mapping is None:
        # Copy all weights if shapes match
        if source_model.weights.shape == target_model.weights.shape:
            target_model.weights = source_model.weights.copy()
            logger.info("Transferred all weights from source to target")
        else:
            logger.warning(
                f"Weight shapes don't match: "
                f"source {source_model.weights.shape}, "
                f"target {target_model.weights.shape}"
            )
    else:
        # Transfer specific layers
        # TODO: Implement layer-wise weight transfer
        logger.info(f"Transferring layers: {layer_mapping}")
        raise NotImplementedError("Layer-wise transfer not yet implemented")


def compute_transfer_benefit(
    pretrained_model,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    fine_tune_epochs: int = 10,
    train_from_scratch_epochs: int = 50,
) -> Dict[str, float]:
    """
    Compute the benefit of transfer learning vs training from scratch.

    Args:
        pretrained_model: Pre-trained model to fine-tune
        X_train: Training data
        y_train: Training labels
        X_test: Test data
        y_test: Test labels
        fine_tune_epochs: Epochs for fine-tuning
        train_from_scratch_epochs: Epochs for training from scratch

    Returns:
        Dictionary with:
        - 'fine_tune_accuracy': Test accuracy after fine-tuning
        - 'scratch_accuracy': Test accuracy after training from scratch
        - 'improvement': Accuracy improvement (fine_tune - scratch)
        - 'time_saved': Training time ratio
    """
    import time
    from ..qnn import QuantumNeuralNetwork

    # Fine-tune pre-trained model
    logger.info("Fine-tuning pre-trained model...")
    start_time = time.time()
    fine_tune_model(
        pretrained_model, X_train, y_train, epochs=fine_tune_epochs, verbose=False
    )
    fine_tune_time = time.time() - start_time
    fine_tune_acc = pretrained_model.score(X_test, y_test)

    # Train from scratch
    logger.info("Training from scratch...")
    scratch_model = QuantumNeuralNetwork(
        n_qubits=pretrained_model.n_qubits, n_layers=pretrained_model.n_layers
    )
    start_time = time.time()
    scratch_model.fit(X_train, y_train, epochs=train_from_scratch_epochs, verbose=False)
    scratch_time = time.time() - start_time
    scratch_acc = scratch_model.score(X_test, y_test)

    results = {
        "fine_tune_accuracy": fine_tune_acc,
        "scratch_accuracy": scratch_acc,
        "improvement": fine_tune_acc - scratch_acc,
        "fine_tune_time": fine_tune_time,
        "scratch_time": scratch_time,
        "time_ratio": (
            scratch_time / fine_tune_time if fine_tune_time > 0 else float("inf")
        ),
    }

    logger.info("Transfer Learning Benefit:")
    logger.info(f"  Fine-tune accuracy: {fine_tune_acc:.4f}")
    logger.info(f"  Scratch accuracy: {scratch_acc:.4f}")
    logger.info(f"  Improvement: {results['improvement']:.4f}")
    logger.info(f"  Time speedup: {results['time_ratio']:.2f}x")

    return results


def create_few_shot_dataset(
    X: np.ndarray, y: np.ndarray, n_samples_per_class: int = 5
) -> tuple:
    """
    Create a few-shot learning dataset.

    Useful for testing transfer learning with limited data.

    Args:
        X: Full dataset features
        y: Full dataset labels
        n_samples_per_class: Number of samples per class

    Returns:
        (X_few_shot, y_few_shot) tuple
    """
    classes = np.unique(y)
    indices = []

    for cls in classes:
        cls_indices = np.where(y == cls)[0]
        selected = np.random.choice(
            cls_indices, size=min(n_samples_per_class, len(cls_indices)), replace=False
        )
        indices.extend(selected)

    indices = np.array(indices)
    np.random.shuffle(indices)

    return X[indices], y[indices]
