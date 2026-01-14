# Transfer Learning Guide

Comprehensive guide to transfer learning with quantum neural networks in quantum-debugger.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Pre-trained Models](#pre-trained-models)
3. [Loading Models](#loading-models)
4. [Fine-tuning](#fine-tuning)
5. [Saving Models](#saving-models)
6. [Advanced Usage](#advanced-usage)
7. [Best Practices](#best-practices)
8. [API Reference](#api-reference)

---

## Quick Start

### Using a Pre-trained Model

```python
from quantum_debugger.qml.transfer import load_pretrained

# Load pre-trained model
model = load_pretrained('mnist_qnn')

# Make predictions
predictions = model.predict(X_test)
accuracy = model.score(X_test, y_test)
print(f"Accuracy: {accuracy:.2%}")
```

### Fine-tuning on New Data

```python
from quantum_debugger.qml.transfer import load_pretrained, fine_tune_model

# Load pre-trained model
model = load_pretrained('mnist_qnn')

# Fine-tune on your data
history = fine_tune_model(
    model,
    X_new_train,
    y_new_train,
    epochs=20,
    freeze_layers=[0]  # Freeze early layers
)

# Evaluate
accuracy = model.score(X_new_test, y_new_test)
```

### Creating Your Own Pre-trained Model

```python
from quantum_debugger.qml.qnn import QuantumNeuralNetwork
from quantum_debugger.qml.transfer import PretrainedQNN

# Train a QNN
qnn = QuantumNeuralNetwork(n_qubits=4)
# ... add layers and train ...

# Convert to pre-trained format
pretrained = PretrainedQNN.from_qnn(
    qnn,
    model_name='my_model',
    dataset='My Dataset',
    metadata={'accuracy': 0.95}
)

# Save for later use
pretrained.save('my_model.pkl')
```

---

## Pre-trained Models

### Model Zoo

The quantum-debugger includes 5 pre-trained quantum models:

| Model | Dataset | Task | Qubits | Target Acc |
|-------|---------|------|--------|-----------|
| `mnist_qnn` | MNIST (0 vs 1) | Binary | 4 | 98% |
| `fashion_mnist_qnn` | Fashion-MNIST | Binary | 4 | 95% |
| `iris_qnn` | Iris (3-class) | Multi-class | 4 | 97% |
| `wine_qnn` | Wine Quality | Binary | 4 | 88% |
| `digits_qnn` | Sklearn Digits | Binary | 4 | 99% |

### Listing Available Models

```python
from quantum_debugger.qml.transfer import list_models, get_model_info, print_model_zoo

# List all models
models = list_models()
print(models)
# ['mnist_qnn', 'fashion_mnist_qnn', 'iris_qnn', 'wine_qnn', 'digits_qnn']

# Get model details
info = get_model_info('mnist_qnn')
print(info)
# {'dataset': 'MNIST (binary: 0 vs 1)',
#  'task': 'binary_classification',
#  'n_qubits': 4,
#  'n_layers': 2,
#  'target_accuracy': 0.98}

# Pretty print all models
print_model_zoo()
```

### Model Information

Each model includes:
- **Architecture**: Number of qubits and layers
- **Training Data**: Dataset used for pre-training
- **Performance**: Expected accuracy metrics
- **Task Type**: Binary or multi-class classification

---

## Loading Models

### From Model Zoo

```python
from quantum_debugger.qml.transfer import load_pretrained

# Load by name
model = load_pretrained('mnist_qnn')
```

### From File

```python
from quantum_debugger.qml.transfer import PretrainedQNN

# Load from pickle
model = PretrainedQNN.load('my_model.pkl')

# Load from JSON
model = PretrainedQNN.load('my_model.json', format='json')

# Load from HDF5
model = PretrainedQNN.load('my_model.h5', format='hdf5')
```

### Inspecting Loaded Models

```python
# Get model information
info = model.get_info()
print(f"Model: {info['model_name']}")
print(f"Dataset: {info['dataset']}")
print(f"Accuracy: {info['accuracy']}")
print(f"Parameters: {info['n_parameters']}")

# Or use repr
print(model)
# PretrainedQNN(name='mnist_qnn', dataset='MNIST', qubits=4, accuracy=0.98)
```

---

## Fine-tuning

### Basic Fine-tuning

```python
from quantum_debugger.qml.transfer import fine_tune_model

history = fine_tune_model(
    pretrained_model=model,
    X_train=X_new_train,
    y_train=y_new_train,
    epochs=10,
    batch_size=32
)
```

### With Validation Data

```python
history = fine_tune_model(
    model,
    X_train, y_train,
    X_val=X_val,      # Validation features
    y_val=y_val,      # Validation labels
    epochs=20
)

print(f"Val accuracy: {history['val_accuracy']:.2%}")
```

### Freezing Layers

Freeze early layers to preserve learned features:

```python
history = fine_tune_model(
    model,
    X_train, y_train,
    freeze_layers=[0, 1],  # Freeze first 2 layers
    epochs=15
)
```

### Using Model Method

```python
# Direct method on model
history = model.fine_tune(
    X_train,
    y_train,
    epochs=10,
    learning_rate=0.01,
    batch_size=32,
    verbose=True
)
```

### Few-Shot Learning

Transfer learning shines with limited data:

```python
from quantum_debugger.qml.transfer.fine_tuning import create_few_shot_dataset

# Create few-shot dataset (5 samples per class)
X_few, y_few = create_few_shot_dataset(
    X_full,
    y_full,
    n_samples_per_class=5
)

# Fine-tune on limited data
history = fine_tune_model(model, X_few, y_few, epochs=30)
```

---

## Saving Models

### Pickle Format (Default)

Fast and compact Python serialization:

```python
from quantum_debugger.qml.transfer import save_model

# Using function
save_model(model, 'my_model.pkl', format='pickle')

# Using model method
model.save('my_model.pkl')  # pickle is default
```

### JSON Format

Human-readable, good for inspection:

```python
# Save as JSON
save_model(model, 'my_model.json', format='json')

# or
model.save('my_model.json', format='json')
```

### HDF5 Format

For large models with many parameters:

```python
# Requires h5py: pip install h5py
save_model(model, 'my_model.h5', format='hdf5')
```

### Format Comparison

| Format | Speed | Size | Human-Readable | Dependencies |
|--------|-------|------|----------------|--------------|
| Pickle | ⚡ Fast | Small | ❌ No | None |
| JSON | Medium | Larger | ✅ Yes | None |
| HDF5 | Fast | Smallest | ❌ No | h5py |

**Recommendation**: Use pickle for most cases, JSON for inspection, HDF5 for very large models.

---

## Advanced Usage

### Measuring Transfer Benefit

Compare transfer learning vs training from scratch:

```python
from quantum_debugger.qml.transfer.fine_tuning import compute_transfer_benefit

results = compute_transfer_benefit(
    pretrained_model=model,
    X_train=X_train,
    y_train=y_train,
    X_test=X_test,
    y_test=y_test,
    fine_tune_epochs=10,
    train_from_scratch_epochs=50
)

print(f"Fine-tune accuracy: {results['fine_tune_accuracy']:.2%}")
print(f"Scratch accuracy: {results['scratch_accuracy']:.2%}")
print(f"Improvement: {results['improvement']:.2%}")
print(f"Time saved: {results['time_ratio']:.1f}x faster")
```

### Weight Transfer Between Models

```python
from quantum_debugger.qml.transfer import transfer_weights

# Transfer weights from source to target
transfer_weights(
    source_model=pretrained_source,
    target_model=my_target,
    layer_mapping={0: 0, 1: 2}  # Map specific layers
)
```

### Custom Model Creation

```python
from quantum_debugger.qml.qnn import QuantumNeuralNetwork
from quantum_debugger.qml.qnn.encoding import EncodingLayer
from quantum_debugger.qml.qnn.variational import VariationalLayer
from quantum_debugger.qml.transfer import PretrainedQNN

# Build custom QNN
qnn = QuantumNeuralNetwork(n_qubits=4)
qnn.add(EncodingLayer(n_qubits=4, n_features=8))
qnn.add(VariationalLayer(n_qubits=4, depth=2))
qnn.compile(optimizer='adam', loss='mse')

# Train
qnn.fit(X_train, y_train, epochs=50)

# Convert to pre-trained
pretrained = PretrainedQNN.from_qnn(
    qnn,
    model_name='custom_qnn',
    dataset='Custom Dataset',
    metadata={
        'accuracy': qnn.score(X_test, y_test),
        'training_epochs': 50,
        'notes': 'Custom architecture'
    }
)

# Save
pretrained.save('custom_qnn.pkl')
```

### Model Ensembles

Combine multiple pre-trained models:

```python
from quantum_debugger.qml.transfer import load_pretrained

# Load multiple models
models = [
    load_pretrained('mnist_qnn'),
    load_pretrained('digits_qnn'),
    # ... your custom models
]

# Ensemble predictions (majority vote)
predictions = []
for model in models:
    predictions.append(model.predict(X_test))

# Majority vote
import numpy as np
ensemble_pred = np.apply_along_axis(
    lambda x: np.bincount(x.astype(int)).argmax(),
    axis=0,
    arr=np.array(predictions)
)
```

---

## Best Practices

### When to Use Transfer Learning

✅ **Good Use Cases:**
- Limited training data available
- Similar task to pre-trained model
- Need faster convergence
- Want better generalization

❌ **Not Recommended:**
- Completely different task
- Abundant training data
- Different input dimensions
- Need full control over architecture

### Fine-tuning Strategy

**Start Conservative:**
1. First try: Freeze all layers except last, train 5-10 epochs
2. If needed: Unfreeze last 2 layers, train 10-20 epochs
3. If still needed: Unfreeze all, train with very small learning rate

```python
# Stage 1: Last layer only
history1 = fine_tune_model(
    model, X_train, y_train,
    freeze_layers=[0, 1, 2],
    epochs=10
)

# Stage 2: Last 2 layers
history2 = fine_tune_model(
    model, X_train, y_train,
    freeze_layers=[0, 1],
    epochs=20
)

# Stage 3: All layers, small LR
model.fine_tune(
    X_train, y_train,
    epochs=30,
    learning_rate=0.001  # Small LR
)
```

### Data Preparation

**Input Preprocessing:**
- Normalize features to [0, 1] or [-1, 1]
- Match pre-training data distribution if possible
- Use PCA/feature selection to match input dimensions

```python
from sklearn.preprocessing import MinMaxScaler, PCA

# Normalize
scaler = MinMaxScaler()
X_normalized = scaler.fit_transform(X)

# Reduce dimensions if needed
pca = PCA(n_components=64)
X_reduced = pca.fit_transform(X_normalized)

# Fine-tune
model.fine_tune(X_reduced, y, epochs=20)
```

### Saving Strategy

**Version Control:**
```python
import datetime

# Add version to filename
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"model_v{timestamp}.pkl"
model.save(filename)

# Save metadata separately
import json
with open(f"model_v{timestamp}_meta.json", 'w') as f:
    json.dump(model.get_info(), f, indent=2)
```

### Debugging

**Common Issues:**

1. **Poor Performance After Fine-tuning**
   - Try smaller learning rate
   - Freeze more layers
   - Add more training data
   - Check data distribution match

2. **Training Too Slow**
   - Reduce batch size
   - Freeze more layers
   - Use fewer epochs
   - Try different optimizer

3. **Memory Issues**
   - Use HDF5 format for large models
   - Reduce batch size
   - Clear unused models: `del model`

---

## API Reference

### PretrainedQNN

#### Constructor

```python
PretrainedQNN(
    model_name: str,
    config: Dict[str, Any],
    weights: np.ndarray,
    metadata: Optional[Dict[str, Any]] = None
)
```

#### Methods

**predict(X: np.ndarray) -> np.ndarray**
- Make predictions on input data
- Returns: Class predictions

**predict_proba(X: np.ndarray) -> np.ndarray**
- Get class probabilities
- Returns: Probability distributions

**score(X: np.ndarray, y: np.ndarray) -> float**
- Compute accuracy
- Returns: Accuracy score (0 to 1)

**fine_tune(...) -> Dict**
- Fine-tune model on new data
- Returns: Training history

**save(path: str, format: str = 'pickle')**
- Save model to disk

**get_info() -> Dict**
- Get model information

#### Class Methods

**load(path: str, format: str = 'pickle') -> PretrainedQNN**
- Load model from file

**from_qnn(qnn, model_name: str, dataset: str, ...) -> PretrainedQNN**
- Convert trained QNN to PretrainedQNN

### Model Zoo Functions

**list_models() -> List[str]**
- Get all available model names

**load_pretrained(model_name: str, format: str = 'pickle') -> PretrainedQNN**
- Load pre-trained model by name

**get_model_info(model_name: str) -> Dict**
- Get model metadata

**print_model_zoo()**
- Display formatted model table

### Fine-tuning Functions

**fine_tune_model(pretrained_model, X_train, y_train, ...) -> Dict**
- Fine-tune a pre-trained model

**transfer_weights(source_model, target_model, layer_mapping)**
- Transfer weights between models

**compute_transfer_benefit(...) -> Dict**
- Measure transfer learning effectiveness

**create_few_shot_dataset(X, y, n_samples_per_class: int) -> Tuple**
- Create limited training set

### Serialization Functions

**save_model(model, path: str, format: str = 'pickle')**
- Save model to disk

**load_model(path: str, format: str = 'pickle') -> PretrainedQNN**
- Load model from disk

**get_model_size(path: str) -> int**
- Get file size in bytes

**get_model_size_mb(path: str) -> float**
- Get file size in MB

---

## Examples

### Complete Fine-tuning Workflow

```python
from quantum_debugger.qml.transfer import load_pretrained, fine_tune_model
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

# 1. Load pre-trained model
model = load_pretrained('mnist_qnn')
print(f"Loaded: {model}")

# 2. Prepare your data
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X_custom)
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y_custom, test_size=0.2, random_state=42
)

# 3. Evaluate pre-trained performance
baseline_acc = model.score(X_test, y_test)
print(f"Baseline accuracy: {baseline_acc:.2%}")

# 4. Fine-tune
history = fine_tune_model(
    model,
    X_train, y_train,
    X_val=X_test, y_val=y_test,
    freeze_layers=[0],
    epochs=20,
    batch_size=32
)

# 5. Evaluate fine-tuned performance
final_acc = model.score(X_test, y_test)
improvement = final_acc - baseline_acc
print(f"Fine-tuned accuracy: {final_acc:.2%}")
print(f"Improvement: {improvement:+.2%}")

# 6. Save fine-tuned model
model.save('finetuned_model.pkl')
```

---

## Troubleshooting

### Model Not Found

```python
# Check available models
from quantum_debugger.qml.transfer import get_available_models
available = get_available_models()
print(f"Trained models: {available}")

# If empty, models need to be trained first
# (Note: Pre-trained models will be available in future releases)
```

### Import Errors

```python
# HDF5 requires h5py
pip install h5py

# If still errors, use pickle or JSON instead
model.save('model.pkl')  # Always works
```

### Performance Issues

```python
# Monitor training
history = model.fine_tune(
    X_train, y_train,
    epochs=20,
    verbose=True  # Print progress
)

# Check convergence
import matplotlib.pyplot as plt
plt.plot(history['loss'])
plt.title('Training Loss')
plt.show()
```

---

## Next Steps

- **Week 4**: Advanced error mitigation techniques
- **Week 5**: Circuit optimization
- **Week 6**: Hardware integration

For more examples, see:
- `examples/transfer_learning_demo.py`
- `tutorials/fine_tuning_tutorial.ipynb`
- `tests/qml/test_transfer.py`

---

**Full API Documentation**: [quantum-debugger.readthedocs.io](https://quantum-debugger.readthedocs.io)

**GitHub**: [github.com/Raunakg2005/quantum-debugger](https://github.com/Raunakg2005/quantum-debugger)
