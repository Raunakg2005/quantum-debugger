# Quick Start Guide

## Installation

Install QuantumDebugger using pip:

```bash
pip install quantum-debugger
```

## Your First Circuit

```python
from quantum_debugger import QuantumCircuit

# Create a 2-qubit circuit
qc = QuantumCircuit(2)

# Add gates
qc.h(0)        # Hadamard on qubit 0
qc.cnot(0, 1)  # CNOT with control=0, target=1

# Get the final state
state = qc.get_statevector()
print(state)  # Bell state: 0.707|00⟩ + 0.707|11⟩
```

## Debugging

```python
from quantum_debugger import QuantumDebugger

# Create debugger
debugger = QuantumDebugger(qc)

# Step through gates
debugger.step()  # Execute first gate
print(debugger.get_current_state())

debugger.step()  # Execute second gate
print(debugger.get_current_state())
```

## Qiskit Integration

```python
from qiskit import QuantumCircuit as QiskitCircuit
from quantum_debugger.integrations.qiskit_adapter import QiskitAdapter

# Import from Qiskit
qc_qiskit = QiskitCircuit(2)
qc_qiskit.h(0)
qc_qiskit.cx(0, 1)

qc_qd = QiskitAdapter.from_qiskit(qc_qiskit)

# Debug with QuantumDebugger
debugger = QuantumDebugger(qc_qd)
```

## Next Steps

- Explore the [API Reference](api.md)
- Check out [Examples](examples.md)
- Read about [Qiskit Integration](qiskit.md)
