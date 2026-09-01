# Examples and Tutorials

This page provides practical examples demonstrating the capabilities of QuantumDebugger v1.0.0, from interactive circuit debugging and Matrix Product States (MPS) to quantum chemistry with VQE, noise simulation, and framework integrations.

---

## 1. Circuit Debugging & State Inspection

Step through quantum circuits gate-by-gate with breakpoints and inspect intermediate statevectors, probabilities, and Bloch coordinates:

```python
from quantum_debugger import QuantumCircuit, QuantumDebugger, Breakpoint

# Build an entangled 3-qubit GHZ state
qc = QuantumCircuit(3)
qc.h(0)
qc.cnot(0, 1)
qc.cnot(1, 2)

# Initialize debugger with a breakpoint after the 2nd gate
debugger = QuantumDebugger(qc)
debugger.add_breakpoint(Breakpoint(step=2, name="after_first_cnot"))

# Step through circuit execution
print("Initial state:", debugger.get_current_state())
debugger.step()
print("After Hadamard on qubit 0:", debugger.get_current_state())

# Continue execution to breakpoint
debugger.run_to_end()
final_state = debugger.get_current_state()
print("Final GHZ State Vector:", final_state)
print("Born Probabilities:", final_state.get_probabilities())
```

---

## 2. Matrix Product States (MPS): 100-Qubit Simulation

The Matrix Product State engine breaks the exponential state-vector memory wall ($\mathcal{O}(n \cdot \chi^2)$ memory instead of $2^n$), enabling simulation of 100+ qubits for low-entangled systems:

```python
import numpy as np
from quantum_debugger import MPS
from quantum_debugger.core.gates import GateLibrary

# Construct a 100-qubit GHZ state (2^100 amplitudes held at bond dimension chi=2)
n_qubits = 100
mps = MPS.zero_state(n_qubits, max_bond=4)

# Apply gates across the 100-qubit chain
mps.apply_single(GateLibrary.H, 0)
for q in range(n_qubits - 1):
    mps.apply_two(GateLibrary.CNOT, q)

# Entanglement and correlation diagnostics
print("Max bond dimension:", mps.max_bond_dimension())  # 2
print("Entanglement entropy at cut 50:", mps.entanglement_entropy(50))  # 1.0 bit

Z = np.diag([1, -1]).astype(complex)
print("<Z0 Z99> correlation:", mps.correlation(Z, 0, Z, n_qubits - 1))  # 1.0
print("<Z50> expectation:", mps.expectation(Z, 50))                    # 0.0

# Draw exact Born-rule measurement shots directly from the MPS
shots = mps.sample(shots=1000, seed=42)
print("1000 Measurement samples (GHZ):", shots)
```

---

## 3. TEBD Real-Time Dynamics & Ground State Cooling

Perform real-time time evolution of many-body quantum spin chains and find ground states using DMRG-style imaginary-time TEBD:

```python
from quantum_debugger.algorithms import (
    tebd_magnetization,
    imaginary_tebd_ground_state,
)

# 1. Real-Time Quench Dynamics on a 30-qubit Ising chain
quench_results = tebd_magnetization(
    n=30,
    time=1.0,
    steps=40,
    j_coupling=1.0,
    field=0.8,
    max_bond=16,
)
print("30-qubit average magnetization <Z>:", quench_results["mean_z"])
print("Magnetization profile across 30 sites:", quench_results["z_profile"][:5], "...")

# 2. Imaginary-Time Ground State Cooling on a 24-qubit chain
ground_state = imaginary_tebd_ground_state(
    n=24,
    j_coupling=1.0,
    field=1.0,
    dtau=0.05,
    steps=150,
    max_bond=16,
)
print("Variational Ground Energy:", ground_state["energy"])
print("Ground State Bond Dimension:", ground_state["bond"])
```

---

## 4. Variational Quantum Eigensolver (VQE) for Molecular Chemistry

Compute molecular ground-state energies (such as $H_2$ dissociation) using VQE with hardware-efficient and excitation-preserving ansätze:

```python
from quantum_debugger.qml.algorithms.vqe import VQE
from quantum_debugger.qml.hamiltonians.molecular import h2_hamiltonian
from quantum_debugger.qml.ansatz.hardware_efficient import hardware_efficient_ansatz
from quantum_debugger.qml.optimizers.advanced import AdamOptimizer
import numpy as np

# Load H2 molecular Hamiltonian at equilibrium bond distance (0.735 A)
H = h2_hamiltonian(distance=0.735)

# Setup VQE with 2 qubits and Adam optimizer
vqe = VQE(
    hamiltonian=H,
    ansatz=hardware_efficient_ansatz,
    num_qubits=2,
    optimizer=AdamOptimizer(learning_rate=0.1),
)

# Optimize ground state
initial_params = np.random.uniform(0, 2 * np.pi, size=8)
result = vqe.run(initial_params=initial_params, max_iterations=60)

print(f"Calculated Ground State Energy: {result['ground_state_energy']:.6f} Hartree")
print(f"Exact Full Configuration Interaction (FCI): -1.137284 Hartree")
```

---

## 5. Open Quantum Systems & Realistic Hardware Noise

Simulate open quantum dynamics with density matrices, Lindblad master equations, and calibrated hardware noise profiles:

```python
from quantum_debugger.density_matrix import DensityMatrix
from quantum_debugger.noise import (
    DepolarizingNoise,
    AmplitudeDamping,
    ThermalRelaxation,
    IBM_PERTH_2025,
)

# Create a density matrix for a Bell state |Phi+>
dm = DensityMatrix.from_statevector([1/np.sqrt(2), 0, 0, 1/np.sqrt(2)])
print("Initial Purity:", dm.purity())  # 1.0 (pure state)

# Apply realistic depolarizing noise (Pauli error convention)
noise = DepolarizingNoise(probability=0.05)
noisy_dm = noise.apply(dm, target_qubit=0)

print("Purity after noise:", noisy_dm.purity())
print("Von Neumann Entanglement Entropy:", noisy_dm.entropy())
print("Fidelity to pure state:", noisy_dm.fidelity(dm))
```

---

## 6. Zero-Noise Extrapolation (ZNE) Error Mitigation

Mitigate circuit noise using unitary folding and polynomial or exponential extrapolation:

```python
from quantum_debugger import QuantumCircuit
from quantum_debugger.mitigation import (
    zero_noise_extrapolation,
    global_fold,
    local_fold,
)
from quantum_debugger.noise import DepolarizingNoise

# Define target circuit
qc = QuantumCircuit(2)
qc.h(0)
qc.cnot(0, 1)

# Fold circuit to scale noise (scale factor = 3, 5)
folded_x3 = global_fold(qc, scale_factor=3.0)
folded_x5 = global_fold(qc, scale_factor=5.0)

# Mitigate expectation values across scale factors
scale_factors = [1.0, 3.0, 5.0]
noisy_expectations = [0.85, 0.62, 0.45]  # Values obtained at each noise level

mitigated_value = zero_noise_extrapolation(
    scale_factors=scale_factors,
    expectation_values=noisy_expectations,
    method="polynomial",
    degree=2,
)
print("Mitigated Zero-Noise Expectation:", mitigated_value)
```

---

## 7. Clifford / Stabilizer Simulation for 100+ Qubits

Simulate large stabilizer states, random Clifford benchmarking circuits, and syndrome extraction without exponential memory:

```python
from quantum_debugger.algorithms.stabilizer import StabilizerSimulator

# Create stabilizer simulator on 50 qubits
sim = StabilizerSimulator(num_qubits=50)

# Build a 50-qubit GHZ state
sim.h(0)
for q in range(49):
    sim.cnot(q, q + 1)

# Measure all qubits (correlated stabilizer outcomes)
measurements = [sim.measure(q) for q in range(50)]
print("50-qubit stabilizer measurement outcome:", measurements)
```

---

## 8. Multi-Framework Integration (Qiskit, Cirq, PennyLane)

Convert circuits bidirectionally between QuantumDebugger and external frameworks:

```python
# 1. Qiskit Integration
from qiskit import QuantumCircuit as QiskitCircuit
from quantum_debugger.integrations.qiskit_adapter import QiskitAdapter
from quantum_debugger import QuantumDebugger

qiskit_qc = QiskitCircuit(2)
qiskit_qc.h(0)
qiskit_qc.cx(0, 1)

qd_qc = QiskitAdapter.from_qiskit(qiskit_qc)
debugger = QuantumDebugger(qd_qc)
debugger.step()
print("Debugged state from Qiskit circuit:", debugger.get_current_state())

# 2. Cirq Integration
import cirq
from quantum_debugger.integrations.cirq_bridge import to_cirq, from_cirq

q0, q1 = cirq.LineQubit.range(2)
cirq_circuit = cirq.Circuit(cirq.H(q0), cirq.CNOT(q0, q1))
qd_from_cirq = from_cirq(cirq_circuit)
print("Converted from Cirq:", qd_from_cirq.get_statevector())
```

---

## More Resources & Community

- Explore the [Quantum Algorithms Guide](quantum_algorithms_guide.md)
- Learn about [Matrix Product States](mps_guide.md)
- Check out example notebooks on [GitHub](https://github.com/Raunakg2005/quantum-debugger/tree/main/examples)
