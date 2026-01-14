"""
Tests for hybrid classical-quantum models
"""

import pytest
import numpy as np
from quantum_debugger.qml.hybrid.layers import (
    ClassicalPreprocessor,
    QuantumMiddleLayer,
    ClassicalPostprocessor,
)

# TensorFlow tests
try:
    import tensorflow as tf
    from quantum_debugger.qml.hybrid.tensorflow_integration import (
        QuantumKerasLayer,
        create_hybrid_model,
        compile_hybrid_model,
    )

    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False

# PyTorch tests
try:
    import torch
    import torch.nn as nn
    from quantum_debugger.qml.hybrid.pytorch_integration import (
        QuantumTorchLayer,
        HybridQNN,
        create_hybrid_pytorch_model,
    )

    HAS_PYTORCH = True
except ImportError:
    HAS_PYTORCH = False


class TestClassicalPreprocessor:
    """Test classical preprocessing layers"""

    def test_initialization(self):
        layer = ClassicalPreprocessor(
            input_dim=8, output_dim=4, hidden_layers=[16, 8], activation="relu"
        )

        assert layer.input_dim == 8
        assert layer.output_dim == 4
        assert len(layer.weights) == 3  # 8->16, 16->8, 8->4

    def test_forward_pass(self):
        layer = ClassicalPreprocessor(input_dim=4, output_dim=2)
        inputs = np.random.rand(10, 4)  # Batch of 10

        outputs = layer.forward(inputs)

        assert outputs.shape == (10, 2)
        assert not np.any(np.isnan(outputs))

    def test_with_hidden_layers(self):
        layer = ClassicalPreprocessor(
            input_dim=8, output_dim=4, hidden_layers=[16, 8], activation="tanh"
        )

        inputs = np.random.rand(5, 8)
        outputs = layer.forward(inputs)

        assert outputs.shape == (5, 4)

    def test_different_activations(self):
        for activation in ["relu", "tanh", "sigmoid", "linear"]:
            layer = ClassicalPreprocessor(
                input_dim=4, output_dim=2, activation=activation
            )

            inputs = np.random.rand(3, 4)
            outputs = layer.forward(inputs)

            assert outputs.shape == (3, 2)


class TestQuantumMiddleLayer:
    """Test quantum middle layer"""

    def test_initialization(self):
        layer = QuantumMiddleLayer(
            n_qubits=4, ansatz_type="real_amplitudes", ansatz_reps=2
        )

        assert layer.n_qubits == 4
        assert layer.ansatz_type == "real_amplitudes"
        assert len(layer.quantum_params) > 0

    def test_forward_pass(self):
        layer = QuantumMiddleLayer(n_qubits=4)
        inputs = np.random.rand(5, 4)  # Must match n_qubits

        outputs = layer.forward(inputs)

        assert outputs.shape == (5, 4)

    def test_angle_encoding(self):
        layer = QuantumMiddleLayer(n_qubits=3, encoding_type="angle")
        data = np.array([1.0, 2.0, 3.0])

        encoded = layer.encode_data(data)

        assert encoded.shape == (3,)
        assert np.all(encoded >= 0) and np.all(encoded < 2 * np.pi)

    def test_different_ansatz_types(self):
        for ansatz in ["real_amplitudes", "strongly_entangling"]:
            layer = QuantumMiddleLayer(n_qubits=4, ansatz_type=ansatz, ansatz_reps=2)

            inputs = np.random.rand(3, 4)
            outputs = layer.forward(inputs)

            assert outputs.shape == (3, 4)


class TestClassicalPostprocessor:
    """Test classical postprocessing layers"""

    def test_initialization(self):
        layer = ClassicalPostprocessor(
            input_dim=4, output_dim=2, output_activation="softmax"
        )

        assert layer.input_dim == 4
        assert layer.output_dim == 2

    def test_forward_softmax(self):
        layer = ClassicalPostprocessor(
            input_dim=4, output_dim=3, output_activation="softmax"
        )

        inputs = np.random.rand(5, 4)
        outputs = layer.forward(inputs)

        assert outputs.shape == (5, 3)
        # Check softmax properties
        assert np.allclose(np.sum(outputs, axis=1), 1.0)
        assert np.all(outputs >= 0) and np.all(outputs <= 1)

    def test_forward_sigmoid(self):
        layer = ClassicalPostprocessor(
            input_dim=4, output_dim=1, output_activation="sigmoid"
        )

        inputs = np.random.rand(5, 4)
        outputs = layer.forward(inputs)

        assert outputs.shape == (5, 1)
        assert np.all(outputs >= 0) and np.all(outputs <= 1)


@pytest.mark.skipif(not HAS_TENSORFLOW, reason="TensorFlow not installed")
class TestQuantumKerasLayer:
    """Test TensorFlow/Keras integration"""

    def test_layer_creation(self):
        layer = QuantumKerasLayer(
            n_qubits=4, ansatz_type="real_amplitudes", ansatz_reps=2
        )

        assert layer.n_qubits == 4
        assert layer.ansatz_type == "real_amplitudes"

    def test_layer_build(self):
        layer = QuantumKerasLayer(n_qubits=4)
        layer.build((None, 4))

        assert hasattr(layer, "quantum_weights")
        assert layer.quantum_weights.shape[0] > 0

    def test_layer_call(self):
        layer = QuantumKerasLayer(n_qubits=4)
        layer.build((None, 4))

        inputs = tf.constant(np.random.rand(5, 4), dtype=tf.float32)
        outputs = layer(inputs)

        assert outputs.shape == (5, 4)

    def test_in_sequential_model(self):
        model = tf.keras.Sequential(
            [
                tf.keras.layers.Dense(4, activation="relu", input_shape=(8,)),
                QuantumKerasLayer(n_qubits=4, ansatz_type="real_amplitudes"),
                tf.keras.layers.Dense(2, activation="softmax"),
            ]
        )

        # Test forward pass
        inputs = np.random.rand(10, 8)
        outputs = model(inputs)

        assert outputs.shape == (10, 2)


@pytest.mark.skipif(not HAS_TENSORFLOW, reason="TensorFlow not installed")
class TestHybridModelBuilder:
    """Test hybrid model creation"""

    def test_create_hybrid_model(self):
        model = create_hybrid_model(
            input_dim=8,
            output_dim=2,
            n_qubits=4,
            classical_layers_pre=[16],
            classical_layers_post=[4],
        )

        assert isinstance(model, tf.keras.Model)
        assert len(model.layers) > 0

    def test_model_forward_pass(self):
        model = create_hybrid_model(input_dim=4, output_dim=2, n_qubits=4)

        inputs = np.random.rand(5, 4)
        outputs = model(inputs)

        assert outputs.shape == (5, 2)

    def test_compile_hybrid_model(self):
        model = create_hybrid_model(input_dim=4, output_dim=2, n_qubits=4)

        compiled_model = compile_hybrid_model(
            model,
            optimizer="adam",
            learning_rate=0.001,
            loss="sparse_categorical_crossentropy",
        )

        assert compiled_model.optimizer is not None


@pytest.mark.skipif(not HAS_PYTORCH, reason="PyTorch not installed")
class TestQuantumTorchLayer:
    """Test PyTorch integration"""

    def test_layer_creation(self):
        layer = QuantumTorchLayer(
            n_qubits=4, ansatz_type="real_amplitudes", ansatz_reps=2
        )

        assert layer.n_qubits == 4
        assert layer.ansatz_type == "real_amplitudes"

    def test_forward_pass(self):
        layer = QuantumTorchLayer(n_qubits=4)
        inputs = torch.randn(5, 4)

        outputs = layer(inputs)

        assert outputs.shape == (5, 4)

    def test_gradient_computation(self):
        layer = QuantumTorchLayer(n_qubits=4)
        inputs = torch.randn(5, 4, requires_grad=True)

        outputs = layer(inputs)
        loss = outputs.sum()
        loss.backward()

        # Check gradients exist
        assert layer.quantum_weights.grad is not None

    def test_in_sequential_model(self):
        model = nn.Sequential(
            nn.Linear(8, 4),
            nn.ReLU(),
            QuantumTorchLayer(n_qubits=4),
            nn.Linear(4, 2),
            nn.Softmax(dim=1),
        )

        inputs = torch.randn(10, 8)
        outputs = model(inputs)

        assert outputs.shape == (10, 2)


@pytest.mark.skipif(not HAS_PYTORCH, reason="PyTorch not installed")
class TestHybridQNN:
    """Test hybrid quantum-classical PyTorch model"""

    def test_model_creation(self):
        model = HybridQNN(
            input_dim=8,
            output_dim=2,
            n_qubits=4,
            classical_hidden_pre=[16],
            classical_hidden_post=[4],
        )

        assert isinstance(model, nn.Module)

    def test_forward_pass(self):
        model = HybridQNN(input_dim=4, output_dim=2, n_qubits=4)

        inputs = torch.randn(5, 4)
        outputs = model(inputs)

        assert outputs.shape == (5, 2)

    def test_training_step(self):
        model = HybridQNN(input_dim=4, output_dim=2, n_qubits=4)

        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        criterion = nn.CrossEntropyLoss()

        inputs = torch.randn(5, 4)
        labels = torch.randint(0, 2, (5,))

        # Forward pass
        outputs = model(inputs)
        loss = criterion(outputs, labels)

        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        assert loss.item() >= 0

    def test_create_hybrid_pytorch_model(self):
        model = create_hybrid_pytorch_model(
            input_dim=8,
            output_dim=2,
            n_qubits=4,
            classical_hidden_pre=[16],
            classical_hidden_post=[4],
        )

        assert isinstance(model, HybridQNN)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
