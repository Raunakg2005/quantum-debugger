"""
TensorFlow/Keras integration for quantum layers

Provides Keras-compatible quantum layers that can be used
in standard TensorFlow/Keras models alongside classical layers.
"""

import numpy as np
from typing import Optional, List

try:
    import tensorflow as tf
    from tensorflow import keras

    HAS_TENSORFLOW = True
except Exception:  # not just ImportError: a broken/incompatible install must not break our import
    HAS_TENSORFLOW = False

    # Create complete dummy classes when TensorFlow not available
    class tf:
        class keras:
            class initializers:
                @staticmethod
                class RandomUniform:
                    def __init__(self, *args, **kwargs):
                        pass

    class keras:
        class layers:
            class Layer:
                def __init__(self, **kwargs):
                    pass

                def build(self, input_shape):
                    pass

                def add_weight(self, **kwargs):
                    return None

                def get_config(self):
                    return {}

        class Model:
            pass

        class Sequential:
            pass

        class optimizers:
            class Adam:
                def __init__(self, *args, **kwargs):
                    pass

            class SGD:
                def __init__(self, *args, **kwargs):
                    pass

            class RMSprop:
                def __init__(self, *args, **kwargs):
                    pass


from .layers import QuantumMiddleLayer

if HAS_TENSORFLOW:

    class QuantumKerasLayer(keras.layers.Layer):
        """
        Keras-compatible quantum layer

        Can be used in Sequential or Functional API models.
        Supports backpropagation through parameter shift rule.

        Example:
            ```python
            model = keras.Sequential([
                keras.layers.Dense(4, activation='relu'),
                QuantumKerasLayer(n_qubits=4, ansatz_type='real_amplitudes'),
                keras.layers.Dense(2, activation='softmax')
            ])
            ```
        """

        def __init__(
            self,
            n_qubits: int,
            encoding_type: str = "angle",
            ansatz_type: str = "real_amplitudes",
            ansatz_reps: int = 2,
            output_dim: Optional[int] = None,
            **kwargs
        ):
            super().__init__(**kwargs)

            self.n_qubits = n_qubits
            self.encoding_type = encoding_type
            self.ansatz_type = ansatz_type
            self.ansatz_reps = ansatz_reps
            self.output_dim = output_dim or n_qubits

            # Create internal quantum layer
            self.quantum_layer = QuantumMiddleLayer(
                n_qubits=n_qubits,
                encoding_type=encoding_type,
                ansatz_type=ansatz_type,
                ansatz_reps=ansatz_reps,
            )

        def build(self, input_shape):
            """Build layer - called when input shape is known"""
            n_params = len(self.quantum_layer.quantum_params)

            self.quantum_weights = self.add_weight(
                name="quantum_weights",
                shape=(n_params,),
                initializer=tf.keras.initializers.RandomUniform(0, 2 * np.pi),
                trainable=True,
            )

            super().build(input_shape)

        def call(self, inputs, training=None):
            """
            Forward pass with a real custom gradient.

            Wraps the quantum layer in ``tf.custom_gradient`` so Keras can train
            through it: the backward pass returns exact parameter-shift gradients
            w.r.t. both the inputs and the quantum weights (the previous version
            dropped straight to numpy, so no gradient reached the weights).

            Runs eagerly (the quantum simulation is numpy); use
            ``model.compile(..., run_eagerly=True)`` when training inside Keras.
            """
            quantum_layer = self.quantum_layer

            @tf.custom_gradient
            def quantum_op(x, weights):
                x_np = x.numpy() if hasattr(x, "numpy") else np.asarray(x)
                w_np = weights.numpy() if hasattr(weights, "numpy") else np.asarray(weights)
                quantum_layer.quantum_params = w_np
                out_np = quantum_layer.forward(x_np)

                def grad(dy):
                    dy_np = dy.numpy() if hasattr(dy, "numpy") else np.asarray(dy)
                    quantum_layer.quantum_params = w_np
                    param_grads, input_grads = quantum_layer.parameter_shift_gradients(
                        x_np, dy_np
                    )
                    return (
                        tf.convert_to_tensor(input_grads, dtype=tf.float32),
                        tf.convert_to_tensor(param_grads, dtype=tf.float32),
                    )

                return tf.convert_to_tensor(out_np, dtype=tf.float32), grad

            outputs = quantum_op(inputs, self.quantum_weights)

            if outputs.shape[-1] != self.output_dim:
                outputs = outputs[:, : self.output_dim]

            return outputs

        def get_config(self):
            """Get layer configuration for serialization"""
            config = super().get_config()
            config.update(
                {
                    "n_qubits": self.n_qubits,
                    "encoding_type": self.encoding_type,
                    "ansatz_type": self.ansatz_type,
                    "ansatz_reps": self.ansatz_reps,
                    "output_dim": self.output_dim,
                }
            )
            return config

        def compute_output_shape(self, input_shape):
            """Compute output shape"""
            return (input_shape[0], self.output_dim)

else:
    # Dummy class when TensorFlow not available
    class QuantumKerasLayer:
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "TensorFlow is required for QuantumKerasLayer. "
                "Install with: pip install tensorflow"
            )


def create_hybrid_model(
    input_dim: int,
    output_dim: int,
    n_qubits: int = 4,
    classical_layers_pre: List[int] = None,
    classical_layers_post: List[int] = None,
    quantum_ansatz: str = "real_amplitudes",
    quantum_reps: int = 2,
    activation: str = "relu",
    output_activation: str = "softmax",
    name: str = "hybrid_model",
):
    """Create a hybrid classical-quantum Keras model"""
    if not HAS_TENSORFLOW:
        raise ImportError(
            "TensorFlow is required. Install with: pip install tensorflow"
        )

    classical_layers_pre = classical_layers_pre or []
    classical_layers_post = classical_layers_post or []

    layers = []
    layers.append(keras.layers.Input(shape=(input_dim,)))

    for units in classical_layers_pre:
        layers.append(keras.layers.Dense(units, activation=activation))

    if (not classical_layers_pre and input_dim != n_qubits) or (
        classical_layers_pre and classical_layers_pre[-1] != n_qubits
    ):
        layers.append(keras.layers.Dense(n_qubits, activation="linear"))

    layers.append(
        QuantumKerasLayer(
            n_qubits=n_qubits,
            ansatz_type=quantum_ansatz,
            ansatz_reps=quantum_reps,
            output_dim=n_qubits,
        )
    )

    for units in classical_layers_post:
        layers.append(keras.layers.Dense(units, activation=activation))

    layers.append(keras.layers.Dense(output_dim, activation=output_activation))

    model = keras.Sequential(layers, name=name)
    return model


def compile_hybrid_model(
    model,
    optimizer: str = "adam",
    learning_rate: float = 0.001,
    loss: str = "sparse_categorical_crossentropy",
    metrics: List[str] = None,
):
    """Compile hybrid model with optimizer and loss"""
    if not HAS_TENSORFLOW:
        raise ImportError("TensorFlow is required")

    metrics = metrics or ["accuracy"]

    if optimizer == "adam":
        opt = keras.optimizers.Adam(learning_rate=learning_rate)
    elif optimizer == "sgd":
        opt = keras.optimizers.SGD(learning_rate=learning_rate)
    elif optimizer == "rmsprop":
        opt = keras.optimizers.RMSprop(learning_rate=learning_rate)
    else:
        opt = optimizer

    model.compile(optimizer=opt, loss=loss, metrics=metrics)
    return model
