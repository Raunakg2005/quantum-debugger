# Dataset Integration Guide

## Overview

The dataset integration module provides tools for loading, preprocessing, and encoding classical data for quantum machine learning applications. It bridges classical machine learning workflows with quantum circuit construction.

## Core Components

### QuantumDataset

A container class for managing datasets in quantum machine learning contexts.

**Attributes:**
- `X`: Feature matrix (N samples × D features)
- `y`: Labels (N samples) - optional for unsupervised learning
- `feature_names`: List of feature names
- `metadata`: Dictionary with dataset information
- `n_samples`: Number of samples
- `n_features`: Number of features
- `shape`: Tuple of (n_samples, n_features)

---

## Data Loading

### From CSV

```python
from quantum_debugger.qml.data import load_csv

# With header and label column
dataset = load_csv(
    'data.csv',
    label_column='class',
    has_header=True
)

# Without header, using column index
dataset = load_csv(
    'data.csv',
    label_column=2,  # Third column is label
    has_header=False
)
```

**Parameters:**
- `filepath` (str or Path): Path to CSV file
- `label_column` (str or int): Column name or index for labels
- `has_header` (bool): Whether CSV has header row
- `feature_columns` (list, optional): Specific columns to use as features

---

### From JSON

```python
from quantum_debugger.qml.data import load_json

dataset = load_json('data.json')
```

**Expected JSON Format:**
```json
{
    "data": [[x1, x2, ...], [x1, x2, ...], ...],
    "labels": [y1, y2, ...],
    "feature_names": ["feature_1", "feature_2", ...]
}
```

---

### From NumPy Arrays

```python
from quantum_debugger.qml.data import load_numpy
import numpy as np

X = np.random.rand(100, 4)
y = np.random.randint(0, 2, 100)

dataset = load_numpy(X, y)
```

---

## Preprocessing

### Normalization

Transform features to a specific range or distribution.

**Min-Max Normalization:**
```python
# Scale features to [0, 1]
normalized_dataset = dataset.normalize(method='minmax')
```

**Z-Score Standardization:**
```python
# Transform to mean=0, std=1
standardized_dataset = dataset.normalize(method='standard')
```

**Max Absolute Value:**
```python
# Scale by maximum absolute value
scaled_dataset = dataset.normalize(method='maxabs')
```

---

### Train/Test Splitting

```python
# 80-20 split with shuffling
train_dataset, test_dataset = dataset.train_test_split(
    test_size=0.2,
    shuffle=True,
    random_state=42  # For reproducibility
)

# Without shuffling (maintains order)
train, test = dataset.train_test_split(
    test_size=0.3,
    shuffle=False
)
```

**Parameters:**
- `test_size` (float): Fraction of data for testing (0.0 to 1.0)
- `shuffle` (bool): Whether to shuffle before splitting
- `random_state` (int, optional): Random seed for reproducibility

---

## Quantum Feature Maps

Feature maps encode classical data into quantum states.

### ZZ Feature Map

Most commonly used feature map in quantum machine learning.

```python
from quantum_debugger.qml.data import zz_feature_map

# Create feature map for 4-dimensional data
feature_map = zz_feature_map(n_qubits=4, reps=2)

# Encode single data point
data_point = dataset.X[0]
circuit = feature_map(data_point)
```

**Properties:**
- Uses Hadamard gates for superposition
- RZ rotations encode feature values
- ZZ entanglement between adjacent qubits
- Depth scales with `reps` parameter

**Formula:**
```
U(x) = H^⊗n · RZ(x) · ZZ(x) · ... (repeated reps times)
```

---

### Pauli Feature Map

Configurable feature map with different Pauli operators.

```python
from quantum_debugger.qml.data import pauli_feature_map

# Using Z operators
fm_z = pauli_feature_map(n_qubits=3, paulis='Z', reps=2)

# Using ZZ operators  
fm_zz = pauli_feature_map(n_qubits=3, paulis='ZZ', reps=2)

circuit = fm_zz(data_point)
```

---

### Angle Encoding

Direct encoding of features as rotation angles.

```python
from quantum_debugger.qml.data import angle_encoding

# Y rotations (most common)
encoder_y = angle_encoding(n_qubits=4, rotation='Y')

# X rotations
encoder_x = angle_encoding(n_qubits=4, rotation='X')

# Z rotations
encoder_z = angle_encoding(n_qubits=4, rotation='Z')

circuit = encoder_y(data_point)
```

**Characteristics:**
- Simplest encoding method
- One feature per qubit
- Number of qubits = number of features
- Fast to implement

---

### Amplitude Encoding

Encodes data into quantum state amplitudes.

```python
from quantum_debugger.qml.data import amplitude_encoding

# Requires log2(n_features) qubits
circuit = amplitude_encoding(data_point)
```

**Note:** This is an advanced encoding requiring state preparation circuits.

---

## Factory Function

Simplified feature map creation:

```python
from quantum_debugger.qml.data import get_feature_map

# Get ZZ feature map
fm = get_feature_map('zz', n_qubits=4, reps=2)

# Get angle encoding
fm = get_feature_map('angle', n_qubits=3, rotation='Y')

# Get Pauli feature map
fm = get_feature_map('pauli', n_qubits=4, paulis='ZZ')
```

---

## Complete Workflow Example

```python
from quantum_debugger.qml.data import (
    load_csv,
    zz_feature_map
)
import numpy as np

# 1. Load data
dataset = load_csv('iris.csv', label_column='species')

# 2. Preprocess
dataset = dataset.normalize('minmax')
train, test = dataset.train_test_split(0.2, random_state=42)

# 3. Create feature map
feature_map = zz_feature_map(
    n_qubits=train.n_features,
    reps=2
)

# 4. Encode training data
train_circuits = []
for sample in train.X:
    circuit = feature_map(sample)
    train_circuits.append(circuit)

# 5. Encode test data
test_circuits = []
for sample in test.X:
    circuit = feature_map(sample)
    test_circuits.append(circuit)

print(f"Training samples: {len(train_circuits)}")
print(f"Test samples: {len(test_circuits)}")
```

---

## Best Practices

### Data Normalization

Always normalize data before quantum encoding:

```python
# Recommended workflow
dataset = load_csv('data.csv', label_column='label')
dataset = dataset.normalize('minmax')  # Scale to [0, 1]
# Now encode to quantum
```

**Reason:** Rotation angles work best in range [0, 2π]

---

### Feature Dimension Matching

Ensure feature dimensionality matches qubit count:

```python
assert dataset.n_features == feature_map.n_qubits
```

---

### Reproducibility

Always set random seeds for reproducible results:

```python
train, test = dataset.train_test_split(
    test_size=0.2,
    random_state=42
)
```

---

## API Reference

### QuantumDataset Methods

```python
dataset.normalize(method='minmax')  # Returns new normalized dataset
dataset.train_test_split(test_size=0.2)  # Returns (train, test) tuple
len(dataset)  # Number of samples
dataset.shape  # (n_samples, n_features)
repr(dataset)  # String representation
```

### Feature Map Attributes

```python
feature_map = zz_feature_map(n_qubits=4, reps=2)

feature_map.n_qubits  # Number of qubits required
feature_map.reps  # Number of repetitions
feature_map.name  # Feature map type name
```

---

## Testing

Run dataset integration tests:

```bash
pytest tests/qml/test_dataset.py -v
```

Expected: 27 tests passing

---

## Performance Considerations

**Memory Usage:**
- Feature maps create quantum circuits in memory
- For large datasets, encode data in batches

**Computational Cost:**
- ZZ feature map: O(n_qubits × reps) gates
- Angle encoding: O(n_qubits) gates
- Amplitude encoding: O(2^n_qubits) complexity

---

## References

1. Havlíček et al., "Supervised learning with quantum-enhanced feature spaces" (2019)
2. Schuld & Killoran, "Quantum machine learning in feature Hilbert spaces" (2019)
3. LaRose & Coyle, "Robust data encodings for quantum classifiers" (2020)
