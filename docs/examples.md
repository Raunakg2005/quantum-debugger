# Examples

## Bell State

Create and debug a Bell state:

```python
from quantum_debugger import QuantumCircuit, QuantumDebugger

qc = QuantumCircuit(2)
qc.h(0)
qc.cnot(0, 1)

debugger = QuantumDebugger(qc)
debugger.run_to_end()
print(debugger.get_current_state())
```

## Grover's Algorithm

```python
from quantum_debugger import QuantumCircuit

# 2-qubit Grover's search
qc = QuantumCircuit(2)

# Superposition
qc.h(0)
qc.h(1)

# Oracle (marks |11⟩)
qc.cz(0, 1)

# Diffusion
qc.h(0)
qc.h(1)
qc.z(0)
qc.z(1)
qc.cz(0, 1)
qc.h(0)
qc.h(1)

state = qc.get_statevector()
probs = state.get_probabilities()
print(f"Most likely: {max(enumerate(probs), key=lambda x: x[1])}")
```

## Qiskit Integration

```python
from qiskit import QuantumCircuit as QiskitCircuit
from quantum_debugger.integrations.qiskit_adapter import QiskitAdapter
from quantum_debugger import QuantumDebugger

# Create in Qiskit
qc = QiskitCircuit(3)
qc.h(0)
qc.cx(0, 1)
qc.cx(1, 2)  # GHZ state

# Convert and debug
qc_qd = QiskitAdapter.from_qiskit(qc)
debugger = QuantumDebugger(qc_qd)

# Step through
for i in range(3):
    debugger.step()
    print(f"After gate {i+1}: {debugger.get_current_state()}")
```

## More Examples

See the [examples/](https://github.com/yourusername/quantum-debugger/tree/main/examples) directory for more!
