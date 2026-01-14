# Hardware Backends Guide

Connect quantum-debugger to real quantum computers.

---

## Supported Backends

| Backend | Cost | Setup | Qubits |
|---------|------|-------|--------|
| **IBM Quantum** | FREE* | 5 min | 5-127 |
| **AWS Braket** | PAID | 10 min | 11-30 |

*FREE tier: 10 minutes/month execution time

---

## Quick Start

### IBM Quantum (FREE)

**Step 1: Get Free API Token**
```
1. Visit https://quantum.ibm.com
2. Sign up (free account)
3. Go to Account Settings
4. Copy your API token
```

**Step 2: Install & Connect**
```bash
# Install IBM backend support
pip install quantum-debugger[ibm]
```

```python
from quantum_debugger.backends import IBMQuantumBackend

# Connect with your free token
backend = IBMQuantumBackend()
backend.connect({'token': 'YOUR_IBM_TOKEN_HERE'})

# Execute on real quantum computer (FREE!)
gates = [('h', 0), ('cnot', (0, 1))]
counts = backend.execute(gates, n_shots=1000)
print(counts)  # {'00': 523, '11': 477}
```

**Cost:** $0.00 ✅

---

### AWS Braket (PAID)

**⚠️ WARNING: This costs real money!**

**Step 1: AWS Setup**
```
1. Create AWS account
2. Enable Braket service
3. Configure AWS credentials
4. Set up S3 bucket (for results)
```

**Step 2: Install & Connect**
```bash
# Install AWS backend support
pip install quantum-debugger[aws]
```

```python
from quantum_debugger.backends import AWSBraketBackend

# Connect (requires AWS credentials)
backend = AWSBraketBackend()
backend.connect({
    'aws_access_key': 'YOUR_AWS_KEY',
    'aws_secret_key': 'YOUR_SECRET',
    'region': 'us-east-1',
    's3_bucket': 'my-braket-results'
})

# ⚠️ THIS COSTS ~$0.65 for 1000 shots
gates = [('h', 0), ('x', 1)]
counts = backend.execute(gates, n_shots=1000)
```

**Cost:** ~$0.30-$1.00 per execution ⚠️

---

## Complete Example

### Using with Circuit Optimization

```python
from quantum_debugger.backends import IBMQuantumBackend
from quantum_debugger.optimization import optimize_circuit
from quantum_debugger.integrations import to_qiskit

# 1. Create circuit
gates = [
    ('h', 0),
    ('h', 0),  # Will be optimized away
    ('cnot', (0, 1)),
    ('x', 2)
]

# 2. Optimize before sending to hardware
optimized = optimize_circuit(gates)
print(f"Reduced from {len(gates)} to {len(optimized)} gates")

# 3. Connect to IBM
backend = IBMQuantumBackend()
backend.connect({'token': 'YOUR_TOKEN'})

# 4. Execute on real quantum computer
counts = backend.execute(optimized, n_shots=1024)
print(f"Results: {counts}")
```

---

## Using with Error Mitigation

```python
from quantum_debugger.backends import IBMQuantumBackend
from quantum_debugger.qml.mitigation import PEC, CDR

# Setup error mitigation
pec = PEC(gate_error_rates={'rx': 0.005, 'cnot': 0.02})
cdr = CDR(n_clifford_circuits=50)

# Connect to hardware
backend = IBMQuantumBackend()
backend.connect({'token': 'YOUR_TOKEN'})

# Train CDR (uses real hardware, costs free tier minutes)
training_data = cdr.generate_training_data(n_qubits=4, depth=3)
cdr.train(training_data, backend.execute)

# Execute with mitigation
raw_result = backend.execute(gates, n_shots=100)
mitigated = cdr.apply_cdr(raw_result)
```

---

## Backend Information

### List Available Devices

```python
backend = IBMQuantumBackend()
backend.connect({'token': 'YOUR_TOKEN'})

# See available quantum computers
devices = backend.get_available_devices()
print(devices)
# ['ibm_brisbane', 'ibm_kyoto', 'ibm_osaka', ...]

# Get device details
info = backend.get_device_info('ibm_brisbane')
print(f"Qubits: {info['n_qubits']}")  # 127
print(f"Status: {info['operational']}")  # True/False
```

### Check Free Tier Usage

```python
# See your free tier limits
info = backend.get_free_tier_info()
print(info)
# {
#     'monthly_limit_minutes': 10,
#     'cost_per_minute': 0.0,
#     'available_qubits': '5-127'
# }
```

---

## AWS Cost Estimator

```python
backend = AWSBraketBackend()

# Estimate cost before running
cost = backend.estimate_cost(n_shots=1000, device_type='qpu')
print(f"Estimated cost: ${cost['total_cost_usd']}")
# Estimated cost: $0.65

# Simulator is cheaper
sim_cost = backend.estimate_cost(n_shots=1000, device_type='simulator')
print(f"Simulator cost: ${sim_cost['total_cost_usd']}")
# Simulator cost: $0.04
```

---

## Integration with QNN

```python
from quantum_debugger.qml.qnn import QuantumNeuralNetwork
from quantum_debugger.backends import IBMQuantumBackend

# Create QNN
qnn = QuantumNeuralNetwork(n_qubits=4)
# ... add layers ...
qnn.compile(optimizer='adam', loss='mse')

# Connect to real hardware
backend = IBMQuantumBackend()
backend.connect({'token': 'YOUR_TOKEN'})

# Train on real quantum computer (uses free tier minutes)
# WARNING: Training is slow on real hardware!
history = qnn.fit(
    X_train[:10],  # Use small dataset to save time
    y_train[:10],
    epochs=5
)
```

---

## Best Practices

### 1. **Optimize First**
Always optimize circuits before sending to hardware:
```python
from quantum_debugger.optimization import compile_circuit

optimized = compile_circuit(gates, optimization_level=3)
backend.execute(optimized)  # Fewer gates = cheaper & faster
```

### 2. **Use Simulators for Development**
```python
# Test on free simulator first
from quantum_debugger.integrations import to_qiskit
from qiskit import Aer

qc = to_qiskit(gates)
simulator = Aer.get_backend('qasm_simulator')
result = simulator.run(qc, shots=1000).result()

# Then run on real hardware once confident
```

### 3. **Batch Jobs**
```python
# Don't run multiple small jobs
# BAD:
for circuit in circuits:
    backend.execute(circuit)  # Costs add up!

# GOOD: Combine if possible
combined = combine_circuits(circuits)
backend.execute(combined, n_shots=1024)
```

### 4. **Monitor Free Tier**
```python
# Check before running
info = backend.get_free_tier_info()
if minutes_used < info['monthly_limit_minutes']:
    backend.execute(gates)
else:
    print("Free tier exhausted, wait for next month")
```

---

## Troubleshooting

### "ImportError: qiskit-ibm-runtime not installed"

```bash
pip install quantum-debugger[ibm]
```

### "Connection failed: Invalid token"

1. Check your IBM Quantum token is correct
2. Token might have expired - get new one from https://quantum.ibm.com
3. Make sure you saved account: `QiskitRuntimeService.save_account(token='...')`

### "No available backends"

Your account might not have access. Check:
```python
backend.service.backends()  # List all backends you can access
```

### AWS Charges Unexpected

AWS Braket charges are **per task** + **per shot**:
- Task fee: $0.30
- Shot fee: $0.00035 × n_shots
- Always check `estimate_cost()` before running!

---

## Cost Comparison

| Shots | IBM (FREE) | AWS QPU | AWS Simulator |
|-------|------------|---------|---------------|
| 100   | $0.00      | $0.33   | $0.04        |
| 1000  | $0.00      | $0.65   | $0.04        |
| 10000 | $0.00*     | $3.80   | $0.08        |

*Subject to 10 min/month limit

---

## Working Without API Keys

You can use all quantum-debugger features without hardware backends:

```python
# This works without any API keys
from quantum_debugger.qml.qnn import QuantumNeuralNetwork
from quantum_debugger.optimization import optimize_circuit
from quantum_debugger.qml.transfer import PretrainedQNN

# All QML features work on classical simulator
qnn = QuantumNeuralNetwork(n_qubits=4)
# ... works fine ...
```

Hardware backends are **optional extras** for users who want to run on real quantum computers.

---

## Summary

**For most users:**
- Use built-in classical simulators (free, fast)
- Only use hardware for final validation

**For research:**
- IBM Quantum free tier is perfect
- 10 minutes/month is enough for testing

**For production:**
- AWS Braket if you need specific hardware
- Budget accordingly (~$5-20/month for light usage)

---

**Next:** [Complete Documentation](https://github.com/Raunakg2005/quantum-debugger#readme)
