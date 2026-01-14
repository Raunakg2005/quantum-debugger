# v0.6.0 - Complete Feature Reference

This section documents all features added in v0.6.0 across 9 major development weeks.

## 🤖 Week 9: AutoML (NEW!)

**One-Line Quantum Machine Learning**

The simplest way to use quantum ML - no expertise required!

### Quick Start

```python
from quantum_debugger.qml.automl import auto_qnn

# That's all you need!
model = auto_qnn(X_train, y_train)
predictions = model.predict(X_test)
```

### What It Does Automatically

- ✅ Determines optimal number of qubits
- ✅ Selects best ansatz architecture
- ✅ Tunes learning rate, epochs, batch size
- ✅ Finds best optimizer
- ✅ Optimizes layer count

### Advanced Usage

```python
from quantum_debugger.qml.automl import AutoQNN, select_best_ansatz, tune_hyperparameters

# Custom AutoML with more control
auto = AutoQNN(max_qubits=6, time_budget=600, n_trials=30)
auto.fit(X_train, y_train)

print(f"Best accuracy: {auto.best_score_:.3f}")
print(f"Best config: {auto.best_config_}")

# Access trained model
predictions = auto.predict(X_test)

# Or just ansatz selection
best_ansatz = select_best_ansatz(X, y, n_qubits=4)

# Or just hyperparameter tuning
best_params = tune_hyperparameters(X, y, n_qubits=4, n_trials=20)
```

## 🎓 Week 3: Transfer Learning

**Reuse Pre-trained Quantum Models**

Save training time by starting from pre-trained models.

```python
from quantum_debugger.qml.transfer import PretrainedQNN

# Load pre-trained model
pretrained = PretrainedQNN.from_zoo('iris_classifier')

# Fine-tune on your data
pretrained.fine_tune(X_new, y_new, epochs=10, freeze_layers=2)

# Or save your own trained model
from quantum_debugger.qml.qnn import QuantumNeuralNetwork

qnn = QuantumNeuralNetwork(n_qubits=4)
# ... train qnn ...

# Save for reuse
pretrained = PretrainedQNN.from_qnn(qnn, model_name='my_model', dataset='custom')
pretrained.save('models/my_qnn.pkl')

# Load later
loaded = PretrainedQNN.load('models/my_qnn.pkl')
predictions = loaded.predict(X_test)
```

📖 **Documentation:** [Transfer Learning Guide](docs/transfer_learning_guide.md)

## 🔬 Week 4: Error Mitigation

**Production-Grade Noise Reduction**

### Probabil istic Error Cancellation (PEC)

```python
from quantum_debugger.qml.mitigation import PEC

pec = PEC(gate_error_rates={'rx': 0.01, 'cnot': 0.02})
mitigated_result, uncertainty = pec.apply_pec(circuit)
```

### Clifford Data Regression (CDR)

```python
from quantum_debugger.qml.mitigation import CDR

cdr = CDR(n_clifford_circuits=50)
training_data = cdr.generate_training_data(n_qubits=4, depth=3)
cdr.train(training_data, noisy_executor)

# Apply to results
mitigated = cdr.apply_cdr(noisy_measurement)
```

📖 **Documentation:** [Error Mitigation Guide](docs/error_mitigation_guide.md)

## ⚡ Week 5: Circuit Optimization

**Reduce Gate Count & Circuit Depth**

```python
from quantum_debugger.optimization import (
    optimize_circuit,
    compile_circuit,
    transpile_circuit
)

# Simple optimization
gates = [('h', 0), ('h', 0), ('x', 1)]  # H cancels itself
optimized = optimize_circuit(gates)  # Returns: [('x', 1)]

# Multi-level compilation
compiled = compile_circuit(gates, optimization_level=3)

# Hardware transpilation
topology = {'edges': [(0, 1), (1, 2), (2, 3)], 'n_qubits': 4}
transpiled = transpile_circuit(gates, topology)
```

**Optimization Levels:**
- 0: No optimization
- 1: Basic (cancellation only)
- 2: Advanced (+ pattern matching)
- 3: Aggressive (+ depth reduction)

📖 **Documentation:** [Circuit Optimization Guide](docs/circuit_optimization_guide.md)

##🌐 Week 6: Framework Integrations

**Universal Compatibility**

Convert between quantum-debugger and other frameworks:

```python
from quantum_debugger.integrations import (
    to_qiskit, from_qiskit,
    to_pennylane, from_pennylane,
    to_cirq, from_cirq
)

# From Qiskit
from qiskit import QuantumCircuit
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)

gates = from_qiskit(qc)  # Convert to our format

# To PennyLane
qnode = to_pennylane(gates)
result = qnode()

# To Cirq
cirq_circuit = to_cirq(gates)

# Round-trip works too!
qc2 = to_qiskit(gates)
```

## 💻 Week 7: Hardware Backends

**Run on Real Quantum Computers**

### IBM Quantum (FREE Tier!)

```python
from quantum_debugger.backends import IBMQuantumBackend

# Connect with free API token
backend = IBMQuantumBackend()
backend.connect({'token': 'YOUR_FREE_IBM_TOKEN'})

# Execute on real quantum computer
gates = [('h', 0), ('cnot', (0, 1))]
counts = backend.execute(gates, n_shots=1024)

# List available devices
devices = backend.get_available_devices()
print(devices)  # ['ibm_brisbane', 'ibm_kyoto', ...]
```

**Get free token:** https://quantum.ibm.com (10 min/month free)

### AWS Braket (Paid)

```python
from quantum_debugger.backends import AWSBraketBackend

backend = AWSBraketBackend()
backend.connect({
    'aws_access_key': 'YOUR_KEY',
    'aws_secret_key': 'YOUR_SECRET',
    'region': 'us-east-1'
})

# Estimate cost first!
cost = backend.estimate_cost(n_shots=1000, device_type='qpu')
print(f"Estimated cost: ${cost['total_cost_usd']}")

# Execute (charges apply!)
counts = backend.execute(gates, n_shots=1000)
```

📖 **Documentation:** [Hardware Backends Guide](docs/hardware_backends_guide.md)

## 📊 Week 8: Benchmarking

**Measure Performance**

```python
from quantum_debugger.benchmarks import (
    benchmark_qnn,
    compare_with_classical,
    benchmark_optimization,
    scalability_analysis
)

# Benchmark QNN
results = benchmark_qnn(n_qubits=4, n_layers=3, dataset_size=100)
print(f"Training time: {results['train_time']:.2f}s")
print(f"Accuracy: {results['accuracy']:.3f}")

# Compare with classical
comparison = compare_with_classical(n_qubits=4, dataset_size=100)
print(f"Speedup: {comparison['speedup']:.2f}x")
print(f"Quantum advantage: {comparison['quantum_advantage']}")

# Benchmark optimization
opt_results = benchmark_optimization(gates, optimization_level=2)
print(f"Gates reduced by {opt_results['reduction_percentage']:.1f}%")

# Scalability analysis
scaling = scalability_analysis([2, 4, 6], algorithm='qnn')
for n_qubits, data in scaling.items():
    print(f"{n_qubits} qubits: {data['time']:.2f}s")
```

## 🚀 Weeks 1-2: Hybrid Models & Kernels

### Hybrid TensorFlow/PyTorch Layers

```python
# TensorFlow
from quantum_debugger.qml.hybrid import TensorFlowQuantumLayer
import tensorflow as tf

model = tf.keras.Sequential([
    tf.keras.layers.Dense(4),
    TensorFlowQuantumLayer(n_qubits=4, n_layers=2),
    tf.keras.layers.Dense(1)
])

# PyTorch
from quantum_debugger.qml.hybrid import PyTorchQuantumLayer
import torch.nn as nn

class HybridNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.classical = nn.Linear(4, 4)
        self.quantum = PyTorchQuantumLayer(n_qubits=4)
        self.output = nn.Linear(4, 1)
```

### Quantum Support Vector Machine

```python
from quantum_debugger.qml.kernels import QSVM

qsvm = QSVM(n_qubits=4, kernel_type='fidelity')
qsvm.fit(X_train, y_train)
predictions = qsvm.predict(X_test)
score = qsvm.score(X_test, y_test)
```

📖 **Documentation:** [Hybrid Models Guide](docs/hybrid_models_guide.md)

## 📦 Installation

### Basic Installation

```bash
pip install quantum-debugger
```

### With Optional Dependencies

```bash
# With Qiskit support
pip install quantum-debugger[qiskit]

# With PennyLane support
pip install quantum-debugger[pennylane]

# With all frameworks
pip install quantum-debugger[all]

# With IBM Quantum backend (FREE)
pip install quantum-debugger[ibm]

# With AWS Brset backend (paid)
pip install quantum-debugger[aws]

# Everything!
pip install quantum-debugger[all]
```

## 📊 Test Coverage

**v0.6.0**: 384/384 tests passing (100%)

| Category | Tests | Status |
|----------|-------|--------|
| Hybrid Models (Week 1) | 26 | ✅ |
| Quantum Kernels (Week 2) | 19 | ✅ |
| Transfer Learning (Week 3) | 42 | ✅ |
| Error Mitigation (Week 4) | 26 | ✅ |
| Circuit Optimization (Week 5) | 26 | ✅ |
| Framework Integrations (Week 6) | 10 | ✅ |
| Hardware Backends (Week 7) | 6 | ✅ |
| Benchmarking (Week 8) | 8 | ✅ |
| **AutoML (Week 9)** | **6** | ✅ |
| v0.5.0 Base | 228 | ✅ |
| **Total** | **384** | **100%** |

See [FINAL_TEST_SUMMARY.md](tests/FINAL_TEST_SUMMARY.md) for details.

## 🎯 Quick Comparison

**quantum-debugger vs Other QML Libraries:**

| Feature | quantum-debugger | Qiskit ML | PennyLane | TensorFlow Quantum |
|---------|-----------------|-----------|-----------|-------------------|
| **AutoML** | ✅ One-line | ❌ | ❌ | ❌ |
| **Transfer Learning** | ✅ Full support | ⚠️ Limited | ❌ | ❌ |
| **Error Mitigation** | ✅ PEC + CDR | ⚠️ Basic | ⚠️ Basic | ❌ |
| **Circuit Optimization** | ✅ Multi-level | ✅ Good | ⚠️ Limited | ⚠️ Limited |
| **Multi-Framework** | ✅ 3 frameworks | ❌ Qiskit only | ❌ PennyLane only | ❌ TF only |
| **Hardware Backends** | ✅ IBM + AWS | ✅ IBM only | ✅ Multiple | ❌ |
| **Benchmarking** | ✅ Built-in | ❌ | ❌ | ❌ |
| **Free Hardware** | ✅ IBM 10 min/mo | ✅ IBM | Varies | ❌ |

**Winner:** quantum-debugger is the ONLY library with all features! 🏆

---

**Version:** 0.6.0  
**Last Updated:** January 14, 2026  
**Production Status:** ✅ Ready for Enterprise Use!
