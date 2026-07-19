# Advanced Quantum Machine Learning

`quantum_debugger.qml.advanced` collects advanced QML models and diagnostics.
All are real circuit-based implementations trained with exact parameter-shift
gradients.

```python
from quantum_debugger.qml.advanced import (
    DataReuploadingClassifier, QuantumAutoencoder, QCNN,
    expressibility, entangling_capability, gradient_variance,
)
```

## Data Re-uploading Classifier

Re-encodes the input data before every variational layer (Perez-Salinas et al.),
which sharply increases expressivity -- it can learn nonlinearly-separable data
that single-encoding circuits cannot.

```python
from sklearn.datasets import make_circles
import numpy as np

X, y = make_circles(n_samples=100, noise=0.05, factor=0.3)
clf = DataReuploadingClassifier(n_qubits=2, n_layers=5, learning_rate=0.15)
clf.fit(X * np.pi, y, epochs=60)
clf.score(X * np.pi, y)          # ~0.9 on concentric circles
```

## Quantum Autoencoder

Compresses `n` qubits into `n - n_trash` qubits by training the trash qubits to
end up in `|0>` (Romero et al.). `inputs` is an array of state vectors.

```python
ae = QuantumAutoencoder(n_qubits=3, n_trash=1, n_layers=4)
ae.fit(inputs, epochs=60)
ae.trash_fidelity(inputs)        # -> ~1.0 for compressible data
compressed = ae.encode(inputs[0])
```

## Quantum Convolutional Neural Network

Alternating convolution and pooling layers halve the active qubits toward a
single readout qubit (Cong et al.).

```python
clf = QCNN(n_qubits=4, learning_rate=0.1)   # n_qubits must be a power of 2
clf.fit(X, y, epochs=50)
clf.score(X, y)
```

## Variational Quantum Classifier (multi-class)

A general K-class classifier: angle-encode the input, apply a variational ansatz,
softmax the Pauli-Z expectations of K readout qubits, and train with the
cross-entropy loss.

```python
from quantum_debugger.qml.advanced import VariationalQuantumClassifier

clf = VariationalQuantumClassifier(n_qubits=3, n_classes=3, n_layers=3)
clf.fit(X, y, epochs=40)         # y in {0, 1, 2}
clf.predict_proba(X)             # (n_samples, 3), rows sum to 1
```

## Ansatz Analysis

Quantitative diagnostics for variational circuits:

```python
expressibility(n_qubits=3, n_layers=4)        # KL to Haar; smaller = more expressible
entangling_capability(n_qubits=3, n_layers=3) # Meyer-Wallach Q in [0, 1]
gradient_variance(n_qubits=6, n_layers=6)      # barren-plateau probe (shrinks with n)
```

- **Expressibility** decreases (toward 0) as circuits get deeper.
- **Entangling capability** increases with entangling depth.
- **Gradient variance** decays exponentially with the qubit count in a barren
  plateau -- use it to check whether an ansatz is trainable at scale.
