"""
QML Benchmarking Tools

Benchmark quantum machine learning algorithms and compare with classical counterparts.
"""

import time
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def benchmark_qnn(
    n_qubits: int,
    n_layers: int,
    dataset_size: int,
    epochs: int = 10
) -> Dict:
    """
    Benchmark Quantum Neural Network performance.
    
    Args:
        n_qubits: Number of qubits
        n_layers: Number of layers
        dataset_size: Size of training dataset
        epochs: Number of training epochs
        
    Returns:
        Benchmark results dictionary
        
    Examples:
        >>> results = benchmark_qnn(n_qubits=4, n_layers=3, dataset_size=100)
        >>> print(f"Training time: {results['train_time']:.2f}s")
        >>> print(f"Accuracy: {results['accuracy']:.3f}")
    """
    from quantum_debugger.qml.qnn import QuantumNeuralNetwork
    
    # Create QNN
    qnn = QuantumNeuralNetwork(n_qubits=n_qubits)
    qnn.compile(optimizer='adam', loss='mse')
    
    # Generate synthetic data
    X = np.random.randn(dataset_size, n_qubits)
    y = np.random.randint(0, 2, dataset_size)
    
    # Benchmark training
    start_time = time.time()
    history = qnn.fit(X, y, epochs=epochs, verbose=0)
    train_time = time.time() - start_time
    
    # Benchmark inference
    start_time = time.time()
    predictions = qnn.predict(X)
    inference_time = time.time() - start_time
    
    # Calculate accuracy
    pred_labels = (predictions > 0.5).astype(int).flatten()
    accuracy = np.mean(pred_labels == y)
    
    results = {
        'n_qubits': n_qubits,
        'n_layers': n_layers,
        'dataset_size': dataset_size,
        'epochs': epochs,
        'train_time': train_time,
        'inference_time': inference_time,
        'time_per_epoch': train_time / epochs,
        'time_per_sample': inference_time / dataset_size,
        'accuracy': accuracy,
        'final_loss': history['loss'][-1] if history['loss'] else None
    }
    
    logger.info(f"QNN Benchmark: {train_time:.2f}s training, {accuracy:.3f} accuracy")
    
    return results


def benchmark_qsvm(
    n_qubits: int,
    dataset_size: int,
    kernel_type: str = 'fidelity'
) -> Dict:
    """
    Benchmark Quantum Support Vector Machine.
    
    Args:
        n_qubits: Number of qubits
        dataset_size: Size of dataset
        kernel_type: Type of quantum kernel
        
    Returns:
        Benchmark results
    """
    from quantum_debugger.qml.kernels import QSVM
    
    # Generate data
    X = np.random.randn(dataset_size, n_qubits)
    y = np.random.choice([-1, 1], dataset_size)
    
    # Create QSVM
    qsvm = QSVM(n_qubits=n_qubits, kernel_type=kernel_type)
    
    # Benchmark training
    start_time = time.time()
    qsvm.fit(X, y)
    train_time = time.time() - start_time
    
    # Benchmark inference
    start_time = time.time()
    predictions = qsvm.predict(X)
    inference_time = time.time() - start_time
    
    accuracy = np.mean(predictions == y)
    
    return {
        'n_qubits': n_qubits,
        'dataset_size': dataset_size,
        'kernel_type': kernel_type,
        'train_time': train_time,
        'inference_time': inference_time,
        'accuracy': accuracy
    }


def compare_with_classical(
    n_qubits: int,
    dataset_size: int,
    task: str = 'classification'
) -> Dict:
    """
    Compare QML with classical machine learning.
    
    Args:
        n_qubits: Number of qubits (= number of features)
        dataset_size: Dataset size
        task: 'classification' or 'regression'
        
    Returns:
        Comparison results
        
    Examples:
        >>> results = compare_with_classical(n_qubits=4, dataset_size=100)
        >>> print(f"QNN: {results['qnn']['accuracy']:.3f}")
        >>> print(f"Classical: {results['classical']['accuracy']:.3f}")
        >>> print(f"Speedup: {results['speedup']:.2f}x")
    """
    from quantum_debugger.qml.qnn import QuantumNeuralNetwork
    from sklearn.neural_network import MLPClassifier
    from sklearn.svm import SVC
    
    # Generate data
    X = np.random.randn(dataset_size, n_qubits)
    y = np.random.randint(0, 2, dataset_size)
    
    # Benchmark QNN
    qnn = QuantumNeuralNetwork(n_qubits=n_qubits)
    qnn.compile(optimizer='adam', loss='mse')
    
    start = time.time()
    qnn.fit(X, y, epochs=10, verbose=0)
    qnn_train_time = time.time() - start
    
    qnn_pred = (qnn.predict(X) > 0.5).astype(int).flatten()
    qnn_accuracy = np.mean(qnn_pred == y)
    
    # Benchmark Classical NN
    mlp = MLPClassifier(hidden_layer_sizes=(10, 10), max_iter=100, random_state=42)
    
    start = time.time()
    mlp.fit(X, y)
    mlp_train_time = time.time() - start
    
    mlp_pred = mlp.predict(X)
    mlp_accuracy = mlp.score(X, y)
    
    # Calculate comparison metrics
    speedup = mlp_train_time / qnn_train_time if qnn_train_time > 0 else float('inf')
    accuracy_diff = qnn_accuracy - mlp_accuracy
    
    return {
        'qnn': {
            'train_time': qnn_train_time,
            'accuracy': qnn_accuracy
        },
        'classical': {
            'train_time': mlp_train_time,
            'accuracy': mlp_accuracy
        },
        'speedup': speedup,
        'accuracy_difference': accuracy_diff,
        'quantum_advantage': accuracy_diff > 0.05  # 5% better
    }


def benchmark_suite(
    quick: bool = False
) -> Dict:
    """
    Run complete benchmark suite.
    
    Args:
        quick: If True, use smaller parameters for faster results
        
    Returns:
        Complete benchmark results
    """
    if quick:
        configs = [
            (2, 2, 50),
            (4, 3, 50)
        ]
    else:
        configs = [
            (2, 2, 100),
            (4, 3, 100),
            (6, 4, 100)
        ]
    
    results = []
    
    for n_qubits, n_layers, dataset_size in configs:
        logger.info(f"Benchmarking QNN: {n_qubits} qubits, {n_layers} layers")
        
        qnn_result = benchmark_qnn(n_qubits, n_layers, dataset_size, epochs=10)
        comparison = compare_with_classical(n_qubits, dataset_size)
        
        results.append({
            'config': {'n_qubits': n_qubits, 'n_layers': n_layers},
            'qnn': qnn_result,
            'comparison': comparison
        })
    
    return {'benchmarks': results}
