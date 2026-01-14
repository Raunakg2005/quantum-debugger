# Circuit Optimization Guide

Comprehensive guide to quantum circuit optimization for efficient quantum machine learning execution.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Gate Reduction](#gate-reduction)
3. [Circuit Compilation](#circuit-compilation)
4. [Transpilation](#transpilation)
5. [Best Practices](#best-practices)
6. [API Reference](#api-reference)

---

## Quick Start

### Basic Optimization

```python
from quantum_debugger.optimization import optimize_circuit

# Simple gate reduction
gates = [('h', 0), ('h', 0), ('x', 1)]  # H·H cancels
optimized = optimize_circuit(gates)
print(optimized)  # [('x', 1)]
```

### Multi-Level Compilation

```python
from quantum_debugger.optimization import CircuitCompiler

compiler = CircuitCompiler(optimization_level=2)
compiled = compiler.compile(circuit_gates)

print(f"Original: {len(circuit_gates)} gates")
print(f"Optimized: {len(compiled)} gates")
```

### Hardware Transpilation

```python
from quantum_debugger.optimization import Transpiler

# Define hardware topology
topology = {
    'edges': [(0,1), (1,2), (2,3)],  # Linear connectivity
    'n_qubits': 4
}

transpiler = Transpiler(topology)
hw_circuit = transpiler.transpile(circuit_gates)
```

---

## Gate Reduction

### Overview

Gate reduction minimizes circuit size by:
- Canceling inverse gates
- Merging rotation gates
- Pattern matching
- Removing identity operations

### Cancellation Rules

**Self-Inverse Gates:**
```python
# H·H = I (Hadamard is self-inverse)
gates = [('h', 0), ('h', 0)]
optimized = optimize_circuit(gates)  # []

# X·X = I (Pauli-X is self-inverse)
gates = [('x', 0), ('x', 0)]
optimized = optimize_circuit(gates)  # []

# CNOT·CNOT = I
gates = [('cnot', (0,1)), ('cnot', (0,1))]
optimized = optimize_circuit(gates)  # []
```

**Inverse Pairs:**
```python
# S·S† = I
gates = [('s', 0), ('s_dagger', 0)]
optimized = optimize_circuit(gates)  # []
```

### Rotation Merging

Consecutive rotations combine:
```python
# Rz(θ₁)·Rz(θ₂) = Rz(θ₁ + θ₂)
gates = [('rz', 0, 0.5), ('rz', 0, 0.3)]
optimized = optimize_circuit(gates)
# Result: [('rz', 0, 0.8)]

# Works for Rx, Ry, Rz
gates = [
    ('rx', 0, 0.2),
    ('rx', 0, 0.3),
    ('rx', 0, 0.5)
]
# Merges to: [('rx', 0, 1.0)]
```

### Pattern Matching

**Clifford Identities:**
```python
# H·X·H = Z
gates = [('h', 0), ('x', 0), ('h', 0)]
optimized = optimize_circuit(gates)  # [('z', 0)]

# H·Z·H = X
gates = [('h', 0), ('z', 0), ('h', 0)]
optimized = optimize_circuit(gates)  # [('x', 0)]
```

### Using GateOptimizer

```python
from quantum_debugger.optimization import GateOptimizer

optimizer = GateOptimizer()

# Optimize circuit
original = [('h', 0), ('h', 0), ('rz', 1, 0.5), ('rz', 1, 0.3)]
optimized = optimizer.optimize(original)

# Get statistics
stats = optimizer.get_optimization_stats(original, optimized)
print(f"Reduced by {stats['reduction_percentage']:.1f}%")
print(f"Removed {stats['gates_removed']} gates")
```

---

## Circuit Compilation

### Optimization Levels

**Level 0: No Optimization**
```python
compiler = CircuitCompiler(optimization_level=0)
compiled = compiler.compile(gates)  # Passthrough
```

**Level 1: Basic**
- Gate cancellation only
```python
compiler = CircuitCompiler(optimization_level=1)
# Applies: cancellation_pass
```

**Level 2: Advanced** (Recommended)
- Cancellation + merging + depth reduction
```python
compiler = CircuitCompiler(optimization_level=2)
# Applies: cancellation, merge_rotations, depth_reduction
```

**Level 3: Aggressive**
- Full optimization pipeline
```python
compiler = CircuitCompiler(optimization_level=3)
# Applies: all passes + final cleanup
```

### Choosing Optimization Level

| Level | Use Case | Speedup | Overhead |
|-------|----------|---------|----------|
| 0 | Debugging | 1x | None |
| 1 | Quick optimization | ~1.2x | Low |
| 2 | **Production** | ~1.5x | Medium |
| 3 | Critical applications | ~2x | High |

**Recommendation:** Level 2 for most cases

### Backend Constraints

```python
compiler = CircuitCompiler(optimization_level=2)

# Apply hardware constraints
constraints = {
    'max_gates': 100,
    'max_depth': 20,
    'native_gates': ['u3', 'cnot']
}

compiled = compiler.compile(circuit_gates, backend_constraints=constraints)
```

---

## Transpilation

### What is Transpilation?

Converts abstract circuits to hardware-executable circuits:
1. **Layout:** Map logical → physical qubits
2. **Routing:** Insert SWAPs for connectivity
3. **Decomposition:** Convert to native gates
4. **Optimization:** Final cleanup

### Basic Usage

```python
from quantum_debugger.optimization import Transpiler

# Define hardware topology
topology = {
    'edges': [(0,1), (1,2), (2,3), (3,4)],
    'n_qubits': 5
}

transpiler = Transpiler(topology)
transpiled = transpiler.transpile(circuit_gates)
```

### Hardware Topologies

**Linear Chain:**
```python
# 0 — 1 — 2 — 3
topology = {'edges': [(0,1), (1,2), (2,3)], 'n_qubits': 4}
```

**Star:**
```python
#   1
#   |
# 2-0-4
#   |
#   3
topology = {'edges': [(0,1), (0,2), (0,3), (0,4)], 'n_qubits': 5}
```

**Grid (2D):**
```python
# 0-1
# | |
# 2-3
topology = {
    'edges': [(0,1), (0,2), (1,3), (2,3)],
    'n_qubits': 4
}
```

### SWAP Insertion

When qubits aren't connected, SWAPs are inserted:

```python
# Linear topology: 0-1-2
topology = {'edges': [(0,1), (1,2)], 'n_qubits': 3}
transpiler = Transpiler(topology)

# CNOT between 0 and 2 (not connected)
gates = [('cnot', (0, 2))]
transpiled = transpiler.transpile(gates)
# Result includes SWAP gates to make 0 and 2 adjacent
```

### Native Gate Decomposition

All gates decomposed to U3 + CNOT:

```python
# Hadamard → U3
# H = U3(π/2, 0, π)
gates = [('h', 0)]
transpiled = transpiler.transpile(gates)
# Result: [('u3', 0, π/2, 0, π)]

# Pauli-X → U3
# X = U3(π, 0, π)
gates = [('x', 0)]
# Result: [('u3', 0, π, 0, π)]

# Rotations → U3
# Rx(θ) = U3(θ, -π/2, π/2)
# Ry(θ) = U3(θ, 0, 0)
# Rz(θ) = U3(0, 0, θ)
```

### Initial Layout

Specify qubit mapping:

```python
# Map logical qubits to physical qubits
initial_layout = [2, 0, 1]  # logical 0→physical 2, etc.

transpiled = transpiler.transpile(
    circuit_gates,
    initial_layout=initial_layout
)
```

---

## Best Practices

### When to Optimize

✅ **Always optimize for:**
- Production circuits
- Deep circuits (>10 gates)
- Circuits with many rotations
- Hardware execution

❌ **Skip optimization for:**
- Debugging (makes tracing harder)
- Single-gate circuits
- Prototype exploration

### Optimization Workflow

**Recommended pipeline:**
```python
from quantum_debugger.optimization import (
    optimize_circuit,
    compile_circuit,
    transpile_circuit
)

# Step 1: Gate reduction
optimized = optimize_circuit(original_gates)

# Step 2: Compilation
compiled = compile_circuit(optimized, optimization_level=2)

# Step 3: Transpilation
topology = {'edges': [(0,1), (1,2)], 'n_qubits': 3}
final = transpile_circuit(compiled, topology)

print(f"Reduction: {len(original_gates)} → {len(final)} gates")
```

### Measuring Improvement

```python
from quantum_debugger.optimization import GateOptimizer

optimizer = GateOptimizer()

# Before optimization
print(f"Original gates: {len(original)}")
print(f"Original depth: {calculate_depth(original)}")

# After optimization
optimized = optimizer.optimize(original)
print(f"Optimized gates: {len(optimized)}")
print(f"Optimized depth: {calculate_depth(optimized)}")

# Statistics
stats = optimizer.get_optimization_stats(original, optimized)
print(f"Improvement: {stats['reduction_percentage']:.1f}%")
```

### Hardware-Specific Tips

**IBM Quantum:**
```python
# IBM uses U3 + CNOT
topology = {
    'edges': [(0,1), (1,2), (1,3), (3,4)],  # IBM Melbourne
    'n_qubits': 5
}
transpiler = Transpiler(topology)
```

**Linear Qubit Systems:**
```python
# Minimize SWAPs by ordering operations
# Place interacting qubits adjacently when possible
```

---

## Complete Example

### Production Optimization Pipeline

```python
from quantum_debugger.optimization import (
    GateOptimizer,
    CircuitCompiler,
    Transpiler
)

# Original circuit (example)
circuit_gates = [
    ('h', 0),
    ('h', 0),  # Will cancel
    ('rz', 1, 0.5),
    ('rz', 1, 0.3),  # Will merge
    ('cnot', (0, 1)),
    ('x', 2),
    ('x', 2),  # Will cancel
]

print(f"Original: {len(circuit_gates)} gates")

# Step 1: Gate reduction
optimizer = GateOptimizer()
reduced = optimizer.optimize(circuit_gates)
print(f"After reduction: {len(reduced)} gates")

# Step 2: Compilation
compiler = CircuitCompiler(optimization_level=2)
compiled = compiler.compile(reduced)
print(f"After compilation: {len(compiled)} gates")

# Step 3: Transpilation
topology = {'edges': [(0,1), (1,2)], 'n_qubits': 3}
transpiler = Transpiler(topology)
final = transpiler.transpile(compiled)
print(f"After transpilation: {len(final)} gates")

# Results
improvement = (len(circuit_gates) - len(final)) / len(circuit_gates) * 100
print(f"\nTotal improvement: {improvement:.1f}% reduction")
```

---

## API Reference

### GateOptimizer

```python
class GateOptimizer:
    def __init__()
    def optimize(gates: List) -> List
    def get_optimization_stats(original, optimized) -> Dict
```

### CircuitCompiler

```python
class CircuitCompiler:
    def __init__(optimization_level: int = 2)
    def compile(gates: List, backend_constraints: Dict = None) -> List
    def get_optimization_info() -> Dict
```

### Transpiler

```python
class Transpiler:
    def __init__(backend_topology: Dict)
    def transpile(gates: List, initial_layout: List = None) -> List
    def get_transpiler_info() -> Dict
```

### Optimization Passes

```python
def cancellation_pass(gates: List) -> List
def merge_rotations_pass(gates: List) -> List
def depth_reduction_pass(gates: List) -> List
def gate_count_reduction_pass(gates: List) -> List
```

### Convenience Functions

```python
def optimize_circuit(gates: List) -> List
def compile_circuit(gates: List, optimization_level: int = 2) -> List
def transpile_circuit(gates: List, topology: Dict) -> List
```

---

## Troubleshooting

### Circuit Not Reducing

```python
# Check if gates are in correct format
gates = [
    ('h', 0),      # ✅ Correct
    ('h', 0),
]

# Not a tuple won't optimize
gates = ['h', 'h']  # ❌ Wrong format
```

### Transpilation Errors

```python
# Ensure topology is valid
topology = {
    'edges': [(0,1), (1,2)],  # Must be list of tuples
    'n_qubits': 3              # Must match edge qubits
}
```

### Overly Aggressive Optimization

```python
# If optimization breaks semantics, reduce level
compiler = CircuitCompiler(optimization_level=1)  # Less aggressive
```

---

## Performance Tips

1. **Cache optimized circuits** - Don't re-optimize identical circuits
2. **Profile first** - Measure gate counts before/after
3. **Match topology** - Design circuits for target hardware
4. **Use appropriate level** - Level 2 optimal for most cases
5. **Batch operations** - Optimize multiple circuits together

---

## Next Steps

- Integrate with error mitigation
- Apply to QNN circuits
- Deploy to hardware backends

---

**Full Documentation**: [quantum-debugger.readthedocs.io](https://quantum-debugger.readthedocs.io)

**GitHub**: [github.com/Raunakg2005/quantum-debugger](https://github.com/Raunakg2005/quantum-debugger)
