# Hybrid Quantum-Classical Models Guide

## Overview

The hybrid models module enables seamless integration between quantum circuits and classical neural networks, supporting both **TensorFlow/Keras** and **PyTorch** frameworks.

## Quick Start

### TensorFlow/Keras Example

```python
from quantum_debugger.qml.hybrid import create_hybrid_model
import numpy as np

# Create hybrid model
model = create_hybrid_model(
    input_dim=8,
    output_dim=2,
    n_qubits=4,
    classical_layers_pre=[16, 8],    # Classical preprocessing
    classical_layers_post=[4],        # Classical postprocessing
    quantum_ansatz='real_amplitudes',
    activation='relu',
    output_activation='softmax'
)

# Compile
model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# Train
X_train = np.random.rand(100, 8)
y_train = np.random.randint(0, 2, 100)

model.fit(X_train, y_train, epochs=10, batch_size=16)

# Predict
predictions = model.predict(X_test)
```

### PyTorch Example

```python
from quantum_debugger.qml.hybrid import HybridQNN
import torch
import torch.nn as nn

# Create hybrid model
model = HybridQNN(
    input_dim=8,
    output_dim=2,
    n_qubits=4,
    classical_hidden_pre=[16, 8],
    classical_hidden_post=[4],
    quantum_ansatz='real_amplitudes',
    output_activation='softmax'
)

# Setup training
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = nn.CrossEntropyLoss()

# Training loop
for epoch in range(10):
    optimizer.zero_grad()
    outputs = model(inputs)
    loss = criterion(outputs, labels)
    loss.backward()
    optimizer.step()
```

## Architecture

### Layer Types

#### 1. Classical Preprocessor
Prepares classical data for quantum encoding:
- Dense layers with configurable activations (ReLU, Tanh, Sigmoid)
- Batch normalization (optional)
- Dropout regularization
- Xavier weight initialization

```python
from quantum_debugger.qml.hybrid import ClassicalPreprocessor

preprocessor = ClassicalPreprocessor(
    input_dim=8,
    output_dim=4,
    hidden_layers=[16, 8],
    activation='relu',
    dropout_rate=0.2
)

output = preprocessor.forward(input_data)
```

#### 2. Quantum Middle Layer
Processes data using quantum circuits:
- Multiple encoding types: angle, amplitude, ZZ
- Variational ansatz: real_amplitudes, strongly_entangling
- Trainable quantum parameters

```python
from quantum_debugger.qml.hybrid import QuantumMiddleLayer

quantum_layer = QuantumMiddleLayer(
    n_qubits=4,
    encoding_type='angle',
    ansatz_type='real_amplitudes',
    ansatz_reps=2
)

quantum_output = quantum_layer.forward(classical_features)
```

#### 3. Classical Postprocessor
Produces final outputs:
- Dense layers
- Softmax for classification
- Sigmoid for binary classification
- Linear for regression

```python
from quantum_debugger.qml.hybrid import ClassicalPostprocessor

postprocessor = ClassicalPostprocessor(
    input_dim=4,
    output_dim=2,
    output_activation='softmax'
)

predictions = postprocessor.forward(quantum_outputs)
```

## Advanced Usage

### Custom Keras Layer

```python
from quantum_debugger.qml.hybrid import QuantumKerasLayer
import tensorflow as tf

# Build custom model
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(8,)),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(4, activation='tanh'),
    
    # Quantum layer
    QuantumKerasLayer(
        n_qubits=4,
        ansatz_type='real_amplitudes',
        ansatz_reps=3
    ),
    
    tf.keras.layers.Dense(8, activation='relu'),
    tf.keras.layers.Dense(2, activation='softmax')
])
```

### Custom PyTorch Module

```python
from quantum_debugger.qml.hybrid import QuantumTorchLayer
import torch.nn as nn

class CustomHybridModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(8, 16)
        self.relu = nn.ReLU()
        self.quantum = QuantumTorchLayer(n_qubits=4)
        self.fc2 = nn.Linear(4, 2)
    
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.quantum(x)
        x = self.fc2(x)
        return x

model = CustomHybridModel()
```

## Feature Map Options

### Encoding Types

1. **Angle Encoding**: `encoding_type='angle'`
   - Simple RY rotations: RY(x_i) on each qubit
   - Best for small feature spaces

2. **Amplitude Encoding**: `encoding_type='amplitude'`
   - Normalizes data to quantum state amplitudes
   - Exponentially compact but limited by qubit count

3. **ZZ Feature Map**: `encoding_type='zz'`
   - Entangling ZZ rotations
   - Captures feature correlations

### Ansatz Types

1. **Real Amplitudes**: `ansatz_type='real_amplitudes'`
   - RY rotations + CNOT entanglers
   - n_qubits × (reps + 1) parameters
   - Good general-purpose ansatz

2. **Strongly Entangling**: `ansatz_type='strongly_entangling'`
   - Full RX, RY, RZ rotations + CNOTs
   - 3 × n_qubits × reps parameters
   - Maximum expressivity

## Training Tips

### Learning Rates
- **Classical layers**: 0.001 - 0.01
- **Quantum parameters**: 0.01 - 0.1 (usually higher)
- Use learning rate scheduling for best results

### Batch Sizes
- Start with 16-32 for small datasets
- Quantum simulation overhead scales with batch size
- GPU acceleration helps significantly

### Regularization
```python
model = create_hybrid_model(
    ...,
    dropout_rate=0.2  # Add dropout
)

# Or in PyTorch
model = HybridQNN(
    ...,
    dropout_rate=0.3
)
```

## Performance Optimization

### Caching
Quantum circuit simulations are cached automatically:
```python
# First forward pass: computes quantum circuit
output1 = quantum_layer.forward(x)

# Repeated calls with same params: uses cache
output2 = quantum_layer.forward(x)  # Much faster!
```

### GPU Acceleration
Both TensorFlow and PyTorch automatically use GPU if available:
```python
# TensorFlow - automatic
with tf.device('/GPU:0'):
    model.fit(X_train, y_train)

# PyTorch - move to GPU
model = model.cuda()
inputs = inputs.cuda()
```

## Common Patterns

### Binary Classification
```python
model = create_hybrid_model(
    input_dim=features,
    output_dim=2,
    n_qubits=4,
    output_activation='softmax'
)
```

### Multi-class Classification
```python
model = create_hybrid_model(
    input_dim=features,
    output_dim=num_classes,
    n_qubits=6,
    output_activation='softmax'
)
```

### Regression
```python
model = create_hybrid_model(
    input_dim=features,
    output_dim=1,
    n_qubits=4,
    output_activation='linear'  # No activation
)
```

## Troubleshooting

### Import Errors
```python
# TensorFlow not installed
pip install tensorflow

# PyTorch not installed
pip install torch
```

### Model Not Training
- Check learning rate (try 0.01)
- Verify data normalization (scale to [0, 1] or [-1, 1])
- Increase ansatz repetitions
- Try different feature maps

### Slow Performance
- Reduce batch size
- Decrease number of qubits
- Use GPU acceleration
- Enable quantum circuit caching

## API Reference

### create_hybrid_model()
```python
create_hybrid_model(
    input_dim: int,              # Input features
    output_dim: int,             # Output classes
    n_qubits: int = 4,           # Quantum layer size
    classical_layers_pre: List[int] = None,   # e.g. [16, 8]
    classical_layers_post: List[int] = None,  # e.g. [4]
    quantum_ansatz: str = 'real_amplitudes',
    quantum_reps: int = 2,
    activation: str = 'relu',
    output_activation: str = 'softmax',
    name: str = 'hybrid_model'
) -> keras.Sequential
```

### HybridQNN()
```python
HybridQNN(
    input_dim: int,
    output_dim: int,
    n_qubits: int = 4,
    classical_hidden_pre: List[int] = None,
    classical_hidden_post: List[int] = None,
    quantum_ansatz: str = 'real_amplitudes',
    quantum_reps: int = 2,
    activation: str = 'relu',
    output_activation: str = 'softmax',
    dropout_rate: float = 0.0
) -> nn.Module
```

## Examples

See `examples/hybrid_models/` for complete working examples:
- `classification_keras.py` - TensorFlow classification
- `classification_pytorch.py` - PyTorch classification
- `regression.py` - Regression task
- `custom_architectures.py` - Advanced patterns
