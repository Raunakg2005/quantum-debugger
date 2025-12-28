# Quantum Neural Networks (QNN) Guide

## Overview

The Quantum Neural Networks (QNN) module provides a layer-based architecture for building and training quantum machine learning models. QNNs combine quantum circuits with classical machine learning paradigms to enable learning on quantum data.

## Key Features

- **Layer-Based Architecture**: Build networks by stacking encoding and variational layers
- **Multiple Feature Maps**: ZZ, Pauli, angle encoding for data transformation
- **Flexible Ansätze**: Support for all quantum circuit templates
- **Batch Training**: Train on multiple samples with mini-batch support
- **Validation Support**: Track performance on validation data
- **Multiple Loss Functions**: MSE, MAE, cross-entropy, hinge loss

---

## Quick Start

### Basic QNN Example

```python
from quantum_debugger.qml.qnn import (
    QuantumNeuralNetwork,
    EncodingLayer,
    VariationalLayer
)
import numpy as np

# Create network
qnn = QuantumNeuralNetwork(n_qubits=4)

# Add encoding layer for classical data
qnn.add(EncodingLayer(4, feature_map='zz', reps=1))

# Add trainable layers
qnn.add(VariationalLayer(4, ansatz='real_amplitudes', reps=2))
qnn.add(VariationalLayer(4, ansatz='strongly_entangling', reps=1))

# Compile with optimizer and loss
qnn.compile(optimizer='adam', loss='mse', learning_rate=0.01)

# View architecture
qnn.summary()

# Train on data
history = qnn.fit(X_train, y_train, epochs=50, batch_size=16)

# Make predictions
predictions = qnn.predict(X_test)
```

---

## Architecture

### Layer Types

#### 1. Encoding Layer

Transforms classical data into quantum states.

```python
from quantum_debugger.qml.qnn import EncodingLayer

# ZZ Feature Map
layer = EncodingLayer(n_qubits=4, feature_map='zz', reps=2)

# Angle Encoding (RY rotations)
layer = EncodingLayer(n_qubits=4, feature_map='angle', rotation='Y')

# Pauli Feature Map
layer = EncodingLayer(n_qubits=4, feature_map='pauli', paulis=['Z', 'ZZ'])
```

**Parameters:**
- `n_qubits`: Number of qubits
- `feature_map`: Type of encoding ('zz', 'pauli', 'angle')
- `reps`: Number of repetitions
- `rotation`: Rotation axis for angle encoding ('X', 'Y', 'Z')

#### 2. Variational Layer

Trainable quantum layer with parameterized gates.

```python
from quantum_debugger.qml.qnn import VariationalLayer

# Real Amplitudes ansatz
layer = VariationalLayer(n_qubits=4, ansatz='real_amplitudes', reps=3)

# Strongly Entangling
layer = VariationalLayer(n_qubits=4, ansatz='strongly_entangling', reps=2)

# Two Local
layer = VariationalLayer(
    n_qubits=4,
    ansatz='two_local',
    rotation_blocks=['ry', 'rz'],
    entanglement='linear'
)
```

**Parameters:**
- `n_qubits`: Number of qubits
- `ansatz`: Ansatz template name
- `reps`: Number of ansatz repetitions
- Additional ansatz-specific parameters

---

## Network Configuration

### Building a Network

```python
qnn = QuantumNeuralNetwork(n_qubits=6)

# Encoding stage
qnn.add(EncodingLayer(6, feature_map='zz'))

# Processing stages
qnn.add(VariationalLayer(6, ansatz='excitation_preserving', reps=2))
qnn.add(VariationalLayer(6, ansatz='real_amplitudes', reps=1))

# Check parameter count
print(f"Total parameters: {qnn.num_parameters}")
```

### Compilation

```python
qnn.compile(
    optimizer='adam',      # Optimizer name
    loss='mse',           # Loss function
    learning_rate=0.01    # Learning rate
)
```

**Supported Optimizers:**
- `'adam'`: Adam optimizer
- `'sgd'`: Stochastic gradient descent
- Other standard optimizers

**Supported Loss Functions:**
- `'mse'`: Mean squared error
- `'mae'`: Mean absolute error
- `'binary_crossentropy'`: Binary classification
- `'categorical_crossentropy'`: Multi-class classification
- `'hinge'`: SVM-style loss

---

## Training

### Basic Training

```python
history = qnn.fit(
    X_train,              # Training data (N × D)
    y_train,              # Training labels (N,)
    epochs=100,           # Number of epochs
    batch_size=32,        # Mini-batch size
    verbose=1             # Print progress
)

# Access training history
losses = history['loss']
```

### With Validation Data

```python
history = qnn.fit(
    X_train, y_train,
    epochs=100,
    batch_size=32,
    validation_data=(X_val, y_val),
    verbose=1
)

# Plot learning curves
import matplotlib.pyplot as plt

plt.plot(history['loss'], label='Training Loss')
plt.plot(history['val_loss'], label='Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()
```

---

## Prediction

```python
# After training
predictions = qnn.predict(X_test)

# Evaluate
from sklearn.metrics import mean_squared_error, r2_score

mse = mean_squared_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print(f"Test MSE: {mse:.4f}")
print(f"Test R²: {r2:.4f}")
```

---

## Complete Example: Regression

```python
import numpy as np
from quantum_debugger.qml.qnn import (
    QuantumNeuralNetwork,
    EncodingLayer,
    VariationalLayer
)

# Generate synthetic data
np.random.seed(42)
X = np.random.rand(200, 4)
y = np.sum(X**2, axis=1) + 0.1 * np.random.randn(200)

# Split data
X_train, X_test = X[:150], X[150:]
y_train, y_test = y[:150], y[150:]

# Build QNN
qnn = QuantumNeuralNetwork(n_qubits=4)
qnn.add(EncodingLayer(4, feature_map='zz', reps=1))
qnn.add(VariationalLayer(4, ansatz='real_amplitudes', reps=3))
qnn.add(VariationalLayer(4, ansatz='strongly_entangling', reps=1))

# Compile
qnn.compile(optimizer='adam', loss='mse', learning_rate=0.02)

# Train
history = qnn.fit(
    X_train, y_train,
    epochs=50,
    batch_size=16,
    validation_data=(X_test, y_test)
)

# Predict
predictions = qnn.predict(X_test)

print(f"Final training loss: {history['loss'][-1]:.4f}")
print(f"Final validation loss: {history['val_loss'][-1]:.4f}")
```

---

## Advanced Usage

### Custom Loss Function

```python
from quantum_debugger.qml.qnn.losses import get_loss_function

# Use built-in
loss_fn = get_loss_function('binary_crossentropy')

# Or define custom
def custom_loss(predictions, targets):
    return np.mean((predictions - targets)**2) + 0.1 * np.abs(predictions - targets)

# Use in training (requires manual training loop)
```

### Parameter Initialization

```python
# Initialize layer parameters
variational = VariationalLayer(4, ansatz='real_amplitudes', reps=2)

# Random initialization
params = variational.initialize_parameters('random', seed=42)

# Zero initialization
params = variational.initialize_parameters('zeros')

# Small random initialization
params = variational.initialize_parameters('small')
```

---

## API Reference

### QuantumNeuralNetwork

```python
class QuantumNeuralNetwork(n_qubits: int)
```

**Methods:**

- `add(layer)`: Add a layer to the network
- `compile(optimizer, loss, learning_rate, **kwargs)`: Compile the network
- `fit(X, y, epochs, batch_size, validation_data, verbose)`: Train the network
- `predict(X)`: Make predictions
- `summary()`: Print architecture summary

**Properties:**

- `num_parameters`: Total trainable parameters
- `layers`: List of network layers
- `history`: Training history

### EncodingLayer

```python
class EncodingLayer(n_qubits, feature_map='zz', reps=1, **kwargs)
```

**Feature Maps:**
- `'zz'`: ZZ feature map with entanglement
- `'pauli'`: Pauli feature map
- `'angle'`: Angle encoding (RX, RY, or RZ)

### VariationalLayer

```python
class VariationalLayer(n_qubits, ansatz='real_amplitudes', reps=1, **kwargs)
```

**Ansätze:**
- `'real_amplitudes'`: RY rotations with CNOT entanglement
- `'two_local'`: Customizable rotation and entanglement
- `'excitation_preserving'`: Preserves particle number
- `'strongly_entangling'`: Three rotation gates per qubit

---

## Best Practices

### Network Design

1. **Start Simple**: Begin with 1-2 variational layers
2. **Match Dimensions**: Ensure `n_qubits ≥ n_features`
3. **Layer Depth**: More layers ≠ better (risk of barren plateaus)
4. **Feature Map**: ZZ works well for most cases

### Training

1. **Learning Rate**: Start with 0.01, adjust based on convergence
2. **Batch Size**: Larger batches = more stable gradients
3. **Epochs**: Monitor validation loss for early stopping
4. **Normalization**: Normalize input features to [0, 2π]

### Performance

1. **Small Datasets**: QNN works well with 50-500 samples
2. **Few Qubits**: 4-8 qubits optimal for current simulators
3. **Gradient Issues**: Try different ansätze if training stalls

---

## Troubleshooting

### Training Not Converging

```python
# Try different learning rate
qnn.compile(optimizer='adam', loss='mse', learning_rate=0.001)

# Try different ansatz
qnn.add(VariationalLayer(4, ansatz='excitation_preserving', reps=2))

# Check data normalization
X_normalized = (X - X.min()) / (X.max() - X.min()) * 2 * np.pi
```

### Out of Memory

```python
# Reduce batch size
history = qnn.fit(X, y, batch_size=8)

# Reduce number of qubits
qnn = QuantumNeuralNetwork(n_qubits=4)  # Instead of 6
```

---

## References

1. Schuld, M., et al. "Quantum Machine Learning in Feature Hilbert Spaces." Physical Review Letters (2019)
2. Benedetti, M., et al. "Parameterized quantum circuits as machine learning models." Quantum Science and Technology (2019)
3. Farhi, E., & Neven, H. "Classification with Quantum Neural Networks on Near Term Processors." arXiv:1802.06002 (2018)

---

## See Also

- [Ansatz Guide](ansatz_guide.md) - Available quantum circuit templates
- [Dataset Guide](dataset_guide.md) - Data loading and preprocessing
- [Optimizers Guide](optimizers_guide.md) - Training optimization methods
