# Quantum Debugger v0.6.0

Production release of the comprehensive quantum machine learning library with AutoML, advanced algorithms, and GPU acceleration.

## Installation

```bash
pip install quantum-debugger
```

## New Features

### AutoML for Quantum Machine Learning

One-line interface for automatic quantum neural network training:

```python
from quantum_debugger.qml.automl import auto_qnn
model = auto_qnn(X_train, y_train)
predictions = model.predict(X_test)
```

Automatically optimizes ansatz selection, hyperparameters, and architecture.

### Advanced Quantum Algorithms

**Quantum Generative Adversarial Networks (QGANs)**
- Generate quantum states through adversarial training
- Applications in data augmentation and state preparation

**Quantum Reinforcement Learning**
- Q-learning with quantum circuit approximation
- SimpleEnvironment for testing and development

### GPU Acceleration

**Multi-GPU Support**
- Distribute training across multiple GPUs
- 1.8-3x speedup with 2-4 GPUs

**Mixed Precision Training**
- FP16/FP32 automatic mixed precision
- 2-3x faster training
- 40% memory reduction

**Memory Optimization**
- Gradient checkpointing
- 50% memory reduction for large models

### Jupyter Notebooks

Five comprehensive example notebooks:
1. AutoML Quick Start
2. Transfer Learning Guide
3. Hardware Deployment
4. Advanced Optimization
5. QML vs Classical Benchmarking

All notebooks are Google Colab compatible.

### CI/CD Automation

- GitHub Actions workflows for automated testing
- Multi-version testing (Python 3.9-3.12)
- Automatic PyPI publishing
- Code quality checks (black, flake8, mypy)

## Complete Feature Set

**Quantum Machine Learning**
- Transfer learning with pretrained models
- Error mitigation (PEC, CDR)
- Circuit optimization
- Framework bridges (Qiskit, PennyLane, Cirq)
- Hardware backends (IBM Quantum FREE, AWS Braket)
- Hybrid models (TensorFlow, PyTorch)
- Quantum kernels (QSVM)
- VQE and QAOA algorithms

**Development Tools**
- Step-through debugging
- State inspection
- Circuit profiling
- Visualization tools
- Noise simulation

## Statistics

- **Tests:** 413 passing (100%)
- **Code Coverage:** 95%+
- **Production Code:** 9,420+ lines
- **Documentation:** 9,000+ lines
- **Python Support:** 3.9, 3.10, 3.11, 3.12

## Documentation

- [Complete Features](https://github.com/Raunakg2005/quantum-debugger/blob/main/V06_FEATURES.md)
- [Jupyter Notebooks](https://github.com/Raunakg2005/quantum-debugger/tree/main/notebooks)
- [API Documentation](https://github.com/Raunakg2005/quantum-debugger#readme)

## Quick Start Examples

### AutoML

```python
from quantum_debugger.qml.automl import auto_qnn
import numpy as np

X_train = np.random.randn(100, 4)
y_train = np.random.randint(0, 2, 100)

model = auto_qnn(X_train, y_train)
predictions = model.predict(X_test)
```

### Multi-GPU Training

```python
from quantum_debugger.gpu import MultiGPUManager

manager = MultiGPUManager(gpu_ids=[0, 1, 2, 3])
distributed_qnn = manager.distribute_qnn(qnn)
distributed_qnn.fit(X_train, y_train)
```

### Mixed Precision

```python
from quantum_debugger.gpu import MixedPrecisionTrainer

trainer = MixedPrecisionTrainer(qnn, precision='fp16')
trainer.fit(X_train, y_train, epochs=100)
```

### Real Quantum Hardware

```python
from quantum_debugger.backends import IBMQuantumBackend

backend = IBMQuantumBackend()
backend.connect({'token': 'YOUR_FREE_IBM_TOKEN'})
results = backend.execute(circuit, n_shots=1024)
```

Get free IBM Quantum token at: https://quantum.ibm.com

## Compatibility

- Python 3.9, 3.10, 3.11, 3.12
- Windows, Linux, macOS
- IBM Quantum (FREE tier available)
- AWS Braket
- Qiskit, PennyLane, Cirq

## Citation

```bibtex
@software{quantum_debugger_2026,
  title = {Quantum Debugger: Production-Grade Quantum Machine Learning Library},
  author = {Gupta, Raunak Kumar},
  year = {2026},
  version = {0.6.0},
  url = {https://github.com/Raunakg2005/quantum-debugger}
}
```

## Author

**Raunak Kumar Gupta**  
GitHub: [@Raunakg2005](https://github.com/Raunakg2005)  
LinkedIn: [Raunak Kumar Gupta](https://www.linkedin.com/in/raunak-kumar-gupta-7b3503270/)

**Supervised by:** Dr. Vaibhav Prakash Vasani  
LinkedIn: [Dr. Vaibhav Vasani](https://www.linkedin.com/in/dr-vaibhav-vasani-phd-460a4162/)  
**Institution:** K.J. Somaiya School of Engineering

## Links

- **PyPI:** https://pypi.org/project/quantum-debugger/
- **GitHub:** https://github.com/Raunakg2005/quantum-debugger
- **Issues:** https://github.com/Raunakg2005/quantum-debugger/issues
- **Documentation:** https://github.com/Raunakg2005/quantum-debugger#readme
