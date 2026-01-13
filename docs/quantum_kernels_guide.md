# Quantum Kernels and QSVM Guide

## Overview

Quantum kernels provide a powerful way to classify data by computing similarities using quantum circuits. This module implements quantum Support Vector Machines (QSVM) with various kernel types.

## Quick Start

### Basic QSVM

```python
from quantum_debugger.qml.kernels import QuantumSVM
import numpy as np
from sklearn.datasets import make_classification

# Generate dataset
X, y = make_classification(n_samples=100, n_features=4, n_classes=2)

# Split data
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

# Create and train QSVM
qsvm = QuantumSVM(
    n_qubits=4,
    feature_map='zz',
    kernel_type='fidelity',
    C=1.0
)

qsvm.fit(X_train, y_train)

# Evaluate
train_acc = qsvm.score(X_train, y_train)
test_acc = qsvm.score(X_test, y_test)
print(f"Train Accuracy: {train_acc:.3f}")
print(f"Test Accuracy: {test_acc:.3f}")

# Predict
predictions = qsvm.predict(X_test)
```

### Using train_qsvm()

```python
from quantum_debugger.qml.kernels import train_qsvm

# All-in-one training
result = train_qsvm(
    X_train, y_train,
    X_test, y_test,
    n_qubits=4,
    feature_map='zz',
    C=1.0
)

print(f"Train accuracy: {result['train_accuracy']:.3f}")
print(f"Test accuracy: {result['test_accuracy']:.3f}")

# Access trained model
model = result['model']
predictions = result['predictions']
```

## Quantum Kernels

### FidelityKernel

Computes kernel based on quantum state fidelity:

**K(x₁, x₂) = |⟨φ(x₁)|φ(x₂)⟩|²**

```python
from quantum_debugger.qml.kernels import FidelityKernel

kernel = FidelityKernel(
    n_qubits=4,
    feature_map='zz',
    reps=2
)

# Compute kernel matrix
K = kernel.compute_kernel_matrix(X_train, X_train)
print(f"Kernel matrix shape: {K.shape}")
print(f"Diagonal (self-similarity): {np.diag(K)}")
```

**Properties:**
- Always symmetric: K(x₁, x₂) = K(x₂, x₁)
- Self-similarity ≈ 1: K(x, x) ≈ 1
- Positive semi-definite
- Values in [0, 1]

### ProjectedKernel

Computes kernel using Pauli measurements:

**K(x₁, x₂) = ⟨φ(x₁)|M|φ(x₂)⟩**

```python
from quantum_debugger.qml.kernels import ProjectedKernel

kernel = ProjectedKernel(
    n_qubits=4,
    feature_map='pauli',
    reps=2,
    measurement_basis='z'
)

K = kernel.compute_kernel_matrix(X, X)
```

**Properties:**
- Can have negative values: K ∈ [-1, 1]
- More flexible than fidelity
- Measurement basis matters

## Feature Maps

### ZZ Feature Map
Entangling feature map with ZZ interactions:

```python
kernel = FidelityKernel(
    n_qubits=4,
    feature_map='zz',  # ZZ entangling
    reps=2
)
```

**Circuit structure:**
- RY(x_i) rotations
- ZZ(x_i × x_j) entanglers
- Repeats for `reps` layers

**Best for:** Capturing feature correlations

### Pauli Feature Map
Simple Pauli rotations:

```python
kernel = FidelityKernel(
    n_qubits=4,
    feature_map='pauli',
    reps=1
)
```

**Circuit structure:**
- RX, RY, RZ rotations
- Product of Pauli operators

**Best for:** Quick prototyping

### Angle Encoding
Direct angle encoding:

```python
kernel = FidelityKernel(
    n_qubits=4,
    feature_map='angle',
    reps=1
)
```

**Circuit structure:**
- RY(x_i) on each qubit
- No entanglement

**Best for:** Simple, linearly separable data

## Kernel Alignment

Optimize feature maps to maximize classification performance:

```python
from quantum_debugger.qml.kernels import (
    kernel_target_alignment,
    optimize_feature_map
)

# Compute alignment
K = kernel.compute_kernel_matrix(X_train, X_train)
alignment = kernel_target_alignment(K, y_train)
print(f"Kernel-target alignment: {alignment:.3f}")

# Optimize feature map
result = optimize_feature_map(
    X_train, y_train,
    base_kernel=kernel,
    n_iterations=100
)

print(f"Best alignment: {result['best_alignment']:.3f}")
```

### What is Kernel Alignment?

Measures how well kernel matrix aligns with target labels:
- **1.0**: Perfect alignment (ideal kernel)
- **0.0**: No alignment
- **Higher is better** for classification

### Optimization

```python
# Optimize feature map parameters
result = optimize_feature_map(
    X_train, y_train,
    base_kernel=kernel,
    n_iterations=100,
    method='COBYLA'  # or 'SLSQP', 'Powell'
)

# Track optimization progress
import matplotlib.pyplot as plt
plt.plot(result['alignments_history'])
plt.xlabel('Iteration')
plt.ylabel('Alignment')
plt.title('Kernel Alignment Optimization')
plt.show()
```

## Kernel Quality Metrics

Evaluate multiple quality metrics:

```python
from quantum_debugger.qml.kernels import evaluate_kernel_quality

metrics = evaluate_kernel_quality(K, y_train)

print(f"Alignment: {metrics['alignment']:.3f}")
print(f"Centered alignment: {metrics['centered_alignment']:.3f}")
print(f"Condition number: {metrics['condition_number']:.2f}")
print(f"Rank: {metrics['rank']}")
print(f"Trace: {metrics['trace']:.2f}")
```

**Metrics:**
- `alignment`: Kernel-target alignment
- `centered_alignment`: Robust CKA score
- `condition_number`: Matrix stability (lower is better)
- `rank`: Effective dimensionality
- `trace`: Sum of eigenvalues
- `mean`, `std`, `min`, `max`: Kernel statistics

## Advanced Usage

### Multi-class Classification

```python
from sklearn.datasets import make_classification

# 3-class problem
X, y = make_classification(
    n_samples=150,
    n_features=4,
    n_classes=3,
    n_informative=4,
    n_redundant=0
)

# QSVM handles multi-class automatically
qsvm = QuantumSVM(n_qubits=4)
qsvm.fit(X_train, y_train)

# Predict probabilities
probabilities = qsvm.predict_proba(X_test)
```

### Hyperparameter Tuning

```python
from sklearn.model_selection import GridSearchCV

# Wrap QSVM for sklearn compatibility
class QSVMEstimator:
    def __init__(self, n_qubits=4, C=1.0):
        self.n_qubits = n_qubits
        self.C = C
        self.model = None
    
    def fit(self, X, y):
        self.model = QuantumSVM(n_qubits=self.n_qubits, C=self.C)
        self.model.fit(X, y)
        return self
    
    def predict(self, X):
        return self.model.predict(X)
    
    def score(self, X, y):
        return self.model.score(X, y)

# Grid search
param_grid = {
    'n_qubits': [2, 4, 6],
    'C': [0.1, 1.0, 10.0]
}

grid = GridSearchCV(QSVMEstimator(), param_grid, cv=3)
grid.fit(X_train, y_train)

print(f"Best params: {grid.best_params_}")
print(f"Best score: {grid.best_score_:.3f}")
```

### Custom Kernel

```python
from quantum_debugger.qml.kernels import QuantumKernel

class CustomKernel(QuantumKernel):
    def compute_kernel_element(self, x1, x2):
        # Custom kernel logic
        params1 = self.encode_data(x1)
        params2 = self.encode_data(x2)
        
        # Your custom similarity measure
        similarity = np.exp(-np.linalg.norm(params1 - params2))
        return similarity

# Use custom kernel
qsvm = QuantumSVM(n_qubits=4)
qsvm.quantum_kernel = CustomKernel(n_qubits=4)
qsvm.fit(X_train, y_train)
```

## Performance Tips

### Kernel Caching

Kernels are automatically cached:
```python
# First computation
k1 = kernel.compute_kernel_element(x1, x2)  # Computes

# Same inputs - uses cache
k2 = kernel.compute_kernel_element(x1, x2)  # Instant!

# Clear cache when done
kernel.clear_cache()
```

### Dataset Size

Kernel matrix scales as O(n²):
- 100 samples: 10,000 kernel elements
- 1,000 samples: 1,000,000 elements

**Recommendations:**
- **< 500 samples**: Full kernel matrix
- **500-2000 samples**: Use sampling
- **> 2000 samples**: Consider Nyström approximation

### Qubit Count

More qubits = more expressivity but slower:
- **2 qubits**: Very fast, limited capacity
- **4 qubits**: Good balance
- **6-8 qubits**: High capacity, slower
- **> 8 qubits**: Consider approximations

## Common Patterns

### Classification Pipeline

```python
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# Create pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('qsvm', QuantumSVM(n_qubits=4))
])

# Train
pipeline.fit(X_train, y_train)

# Predict
predictions = pipeline.predict(X_test)
```

### Cross-Validation

```python
from sklearn.model_selection import cross_val_score

qsvm = QuantumSVM(n_qubits=4, C=1.0)

scores = cross_val_score(
    qsvm, X, y,
    cv=5,  # 5-fold CV
    scoring='accuracy'
)

print(f"CV Accuracy: {scores.mean():.3f} (+/- {scores.std():.3f})")
```

### Feature Selection

```python
from sklearn.feature_selection import SelectKBest, f_classif

# Select best features
selector = SelectKBest(f_classif, k=4)
X_selected = selector.fit_transform(X, y)

# Train on selected features
qsvm = QuantumSVM(n_qubits=4)
qsvm.fit(X_selected, y)
```

## Troubleshooting

### Poor Accuracy
1. Check data normalization (scale to [0, 1])
2. Try different feature maps
3. Increase repetitions (`reps`)
4. Tune C parameter
5. Evaluate kernel alignment

### Slow Training
1. Reduce dataset size
2. Decrease number of qubits
3. Use simpler feature map
4. Clear kernel cache periodically

### Memory Issues
1. Use smaller batches
2. Clear kernel cache: `kernel.clear_cache()`
3. Reduce training set size
4. Consider kernel approximations

## API Reference

### QuantumSVM
```python
QuantumSVM(
    n_qubits: int = 4,
    feature_map: str = 'zz',
    kernel_type: str = 'fidelity',
    reps: int = 2,
    C: float = 1.0
)
```

**Methods:**
- `fit(X, y)`: Train on data
- `predict(X)`: Predict labels
- `score(X, y)`: Compute accuracy
- `get_support_vectors()`: Get support vectors
- `predict_proba(X)`: Class probabilities

### FidelityKernel
```python
FidelityKernel(
    feature_map: str = 'zz',
    n_qubits: int = 4,
    reps: int = 2
)
```

**Methods:**
- `compute_kernel_matrix(X1, X2)`: Compute kernel matrix
- `compute_kernel_element(x1, x2)`: Single kernel value
- `clear_cache()`: Clear cache

## Examples

See `examples/quantum_kernels/` for complete examples:
- `basic_qsvm.py` - Simple classification
- `kernel_comparison.py` - Compare kernel types
- `alignment_optimization.py` - Feature map optimization
- `multi_class.py` - Multi-class classification
