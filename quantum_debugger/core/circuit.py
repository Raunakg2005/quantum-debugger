"""
Quantum circuit representation and execution
"""

import numpy as np
import warnings
from typing import List, Optional, Union, Any
from quantum_debugger.core.quantum_state import QuantumState
from quantum_debugger.core.gates import GateLibrary, Gate


class QuantumCircuit:
    """Quantum circuit with gate operations"""
    
    def __init__(self, num_qubits: int, num_classical: int = 0, 
                 noise_model: Optional[Any] = None,
                 noise_simulation_method: str = 'density_matrix',
                 backend: str = 'auto'):
        """
        Initialize a quantum circuit
        
        Args:
            num_qubits: Number of quantum bits
            num_classical: Number of classical bits for measurements
            noise_model: Optional noise model (NoiseModel or HardwareProfile)
            noise_simulation_method: 'density_matrix', 'stochastic', or 'approximate'
            backend: Computational backend ('auto', 'numpy', 'numba', 'sparse')
        """
        self.num_qubits = num_qubits
        self.num_classical = num_classical if num_classical > 0 else num_qubits
        self.gates: List[Gate] = []
        self.measurements: List[tuple] = []
        self.backend = backend
        self._initial_state = QuantumState(num_qubits, backend=backend)
        
        # Noise configuration
        self.noise_model = noise_model
        self.noise_simulation_method = noise_simulation_method
        self.apply_noise = noise_model is not None
        
        # Memory warning for large circuits with density matrices
        if self.apply_noise and num_qubits > 10 and noise_simulation_method == 'density_matrix':
            memory_mb = (2**num_qubits)**2 * 16 / (1024**2)  # complex128 = 16 bytes
            warnings.warn(
                f"Density matrix for {num_qubits} qubits requires ~{memory_mb:.1f}MB memory. "
                f"Consider noise_simulation_method='stochastic' for circuits with >10 qubits.",
                ResourceWarning,
                stacklevel=2
            )
    
    def set_noise_model(self, noise_model: Optional[Any], 
                        noise_simulation_method: str = 'density_matrix'):
        """
        Set or update noise model for the circuit
        
        Args:
            noise_model: NoiseModel instance, HardwareProfile, or None to disable
            noise_simulation_method: 'density_matrix', 'stochastic', or 'approximate'
        """
        self.noise_model = noise_model
        self.noise_simulation_method = noise_simulation_method
        self.apply_noise = noise_model is not None
        
        # Update memory warning if needed
        if self.apply_noise and self.num_qubits > 10 and noise_simulation_method == 'density_matrix':
            memory_mb = (2**self.num_qubits)**2 * 16 / (1024**2)
            warnings.warn(
                f"Density matrix for {self.num_qubits} qubits requires ~{memory_mb:.1f}MB memory. "
                f"Consider noise_simulation_method='stochastic' for circuits with >10 qubits.",
                ResourceWarning,
                stacklevel=2
            )
    
    def _add_gate(self, name: str, matrix: np.ndarray, qubits: Union[int, List[int]], params: dict = None):
        """Add a gate to the circuit"""
        if isinstance(qubits, int):
            qubits = [qubits]
        
        gate = Gate(name, matrix, qubits, params)
        self.gates.append(gate)
        return self
    
    # Single-qubit gates
    def h(self, qubit: int):
        """Apply Hadamard gate"""
        return self._add_gate('H', GateLibrary.H, qubit)
    
    def x(self, qubit: int):
        """Apply Pauli-X (NOT) gate"""
        return self._add_gate('X', GateLibrary.X, qubit)
    
    def y(self, qubit: int):
        """Apply Pauli-Y gate"""
        return self._add_gate('Y', GateLibrary.Y, qubit)
    
    def z(self, qubit: int):
        """Apply Pauli-Z gate"""
        return self._add_gate('Z', GateLibrary.Z, qubit)
    
    def s(self, qubit: int):
        """Apply S (phase) gate"""
        return self._add_gate('S', GateLibrary.S, qubit)
    
    def t(self, qubit: int):
        """Apply T gate"""
        return self._add_gate('T', GateLibrary.T, qubit)
    
    def rx(self, theta: float, qubit: int):
        """Apply RX rotation gate"""
        return self._add_gate('RX', GateLibrary.RX(theta), qubit, {'theta': theta})
    
    def ry(self, theta: float, qubit: int):
        """Apply RY rotation gate"""
        return self._add_gate('RY', GateLibrary.RY(theta), qubit, {'theta': theta})
    
    def rz(self, theta: float, qubit: int):
        """Apply RZ rotation gate"""
        return self._add_gate('RZ', GateLibrary.RZ(theta), qubit, {'theta': theta})
    
    def phase(self, theta: float, qubit: int):
        """Apply phase shift gate"""
        return self._add_gate('PHASE', GateLibrary.PHASE(theta), qubit, {'theta': theta})
    
    # Two-qubit gates
    def cnot(self, control: int, target: int):
        """Apply CNOT (controlled-NOT) gate"""
        return self._add_gate('CNOT', GateLibrary.CNOT, [control, target])
    
    def cx(self, control: int, target: int):
        """Alias for CNOT"""
        return self.cnot(control, target)
    
    def cz(self, control: int, target: int):
        """Apply CZ (controlled-Z) gate"""
        return self._add_gate('CZ', GateLibrary.CZ, [control, target])
    
    def cp(self, theta: float, control: int, target: int):
        """Apply controlled-phase gate"""
        return self._add_gate('CP', GateLibrary.CP(theta), [control, target], {'theta': theta})
    
    def swap(self, qubit1: int, qubit2: int):
        """Apply SWAP gate"""
        return self._add_gate('SWAP', GateLibrary.SWAP, [qubit1, qubit2])
    
    # Three-qubit gates
    def toffoli(self, control1: int, control2: int, target: int):
        """Apply Toffoli (CCNOT) gate"""
        return self._add_gate('TOFFOLI', GateLibrary.TOFFOLI, [control1, control2, target])
    
    def ccx(self, control1: int, control2: int, target: int):
        """Alias for Toffoli"""
        return self.toffoli(control1, control2, target)
    
    # Measurements
    def measure(self, qubit: int, classical_bit: int = None):
        """
        Measure a qubit
        
        Args:
            qubit: Qubit index to measure
            classical_bit: Classical bit to store result (defaults to same as qubit)
        """
        if classical_bit is None:
            classical_bit = qubit
        self.measurements.append((qubit, classical_bit))
        return self
    
    def measure_all(self):
        """Measure all qubits"""
        for i in range(self.num_qubits):
            self.measure(i, i)
        return self
    
    # Circuit information
    def depth(self) -> int:
        """Calculate circuit depth (number of gate layers)"""
        if not self.gates:
            return 0
        
        # Track when each qubit is last used
        qubit_times = [0] * self.num_qubits
        
        for gate in self.gates:
            # Get max time of qubits involved
            max_time = max(qubit_times[q] for q in gate.qubits)
            
            # Update all involved qubits
            for q in gate.qubits:
                qubit_times[q] = max_time + 1
        
        return max(qubit_times)
    
    def size(self) -> int:
        """Total number of gates"""
        return len(self.gates)
    
    def count_gates(self, gate_name: str = None) -> int:
        """
        Count gates of specific type
        
        Args:
            gate_name: Name of gate to count (None for all gates)
        """
        if gate_name is None:
            return len(self.gates)
        return sum(1 for g in self.gates if g.name == gate_name)
    
    # Execution
    def run(self, shots: int = 1, initial_state: Optional[QuantumState] = None) -> dict:
        """
        Execute the circuit
        
        Args:
            shots: Number of times to run the circuit
            initial_state: Optional initial state (defaults to |0...0⟩)
            
        Returns:
            Dictionary with measurement results and statistics
        """
        # Route to noisy execution if noise model is enabled
        if self.apply_noise:
            return self._run_with_noise(shots, initial_state)
        
        # Standard noiseless execution
        results = []
        
        for _ in range(shots):
            state = initial_state.copy() if initial_state else QuantumState(self.num_qubits, backend=self.backend)
            
            # Apply all gates
            for gate in self.gates:
                state.apply_gate(gate.matrix, gate.qubits)
            
            # Perform measurements
            classical_bits = [0] * self.num_classical
            for qubit, classical_bit in self.measurements:
                classical_bits[classical_bit] = state.measure(qubit)
            
            results.append(classical_bits)
        
        # Analyze results
        counts = {}
        for result in results:
            key = ''.join(map(str, result))
            counts[key] = counts.get(key, 0) + 1
        
        return {
            'counts': counts,
            'results': results,
            'shots': shots
        }
    
    def _run_with_noise(self, shots: int, initial_state: Optional[QuantumState]) -> dict:
        """
        Execute circuit with noise simulation
        
        Args:
            shots: Number of times to run the circuit
            initial_state: Optional initial state
            
        Returns:
            Dictionary with measurement results, statistics, and fidelity
        """
        from quantum_debugger.noise import QuantumState as NoisyQuantumState
        
        results = []
        fidelities = []
        
        for _ in range(shots):
            # Initialize with density matrix
            if initial_state:
                # Convert existing state to density matrix if needed
                if hasattr(initial_state, 'density_matrix') and initial_state.density_matrix is not None:
                    state = initial_state.copy()
                else:
                    state = NoisyQuantumState(self.num_qubits, 
                                            state_vector=initial_state.state_vector, 
                                            use_density_matrix=True)
            else:
                state = NoisyQuantumState(self.num_qubits, use_density_matrix=True)
            
            # Store reference state for fidelity calculation
            reference_state = NoisyQuantumState(self.num_qubits, use_density_matrix=True)
            for gate in self.gates:
                reference_state.apply_gate(gate.matrix, gate.qubits)
            
            # Apply gates with noise
            for gate in self.gates:
                # Apply the gate
                state.apply_gate(gate.matrix, gate.qubits)
                
                # Apply noise after the gate
                if self.noise_model:
                    self.noise_model.apply(state, qubits=gate.qubits)
            
            # Calculate fidelity
            if hasattr(state, 'density_matrix') and state.density_matrix is not None:
                # Fidelity = Tr(ρ_ideal * ρ_noisy)
                fidelity = np.trace(reference_state.density_matrix @ state.density_matrix).real
                fidelities.append(fidelity)
            
            # Perform measurements
            classical_bits = [0] * self.num_classical
            for qubit, classical_bit in self.measurements:
                classical_bits[classical_bit] = state.measure(qubit)
            
            results.append(classical_bits)
        
        # Analyze results
        counts = {}
        for result in results:
            key = ''.join(map(str, result))
            counts[key] = counts.get(key, 0) + 1
        
        return {
            'counts': counts,
            'results': results,
            'shots': shots,
            'fidelity': np.mean(fidelities) if fidelities else 1.0,
            'fidelity_std': np.std(fidelities) if fidelities else 0.0
        }
    
    def get_statevector(self, initial_state: Optional[QuantumState] = None) -> QuantumState:
        """
        Get final state vector without measurements
        
        Args:
            initial_state: Optional initial state
            
        Returns:
            Final quantum state
        """
        state = initial_state.copy() if initial_state else QuantumState(self.num_qubits)
        
        for gate in self.gates:
            state.apply_gate(gate.matrix, gate.qubits)
        
        return state
    
    # Visualization helpers
    def draw(self, output: str = 'text') -> str:
        """
        Draw the circuit
        
        Args:
            output: Output format ('text' for ASCII art)
            
        Returns:
            String representation of circuit
        """
        if output == 'text':
            return self._draw_text()
        return str(self)
    
    def _draw_text(self) -> str:
        """Draw circuit as ASCII art"""
        lines = []
        
        # Header
        lines.append(f"Circuit with {self.num_qubits} qubits, {len(self.gates)} gates")
        lines.append("")
        
        # Qubit lines
        for q in range(self.num_qubits):
            line = f"q{q}: |0>─"
            
            for i, gate in enumerate(self.gates):
                if q in gate.qubits:
                    # This qubit is involved in this gate
                    if len(gate.qubits) == 1:
                        # Single-qubit gate
                        gate_str = f"[{gate.name}]"
                    elif gate.qubits[0] == q:
                        # First qubit (control or first target)
                        gate_str = "●" if gate.name in ['CNOT', 'CZ'] else "┬"
                    else:
                        # Target qubit
                        gate_str = "⊕" if gate.name == 'CNOT' else "┴"
                    
                    line += gate_str + "─"
                else:
                    # Not involved, just continue line
                    line += "─" * (len(gate.name) + 3)
            
            lines.append(line)
        
        return "\n".join(lines)
    
    def __repr__(self):
        gate_str = ", ".join(str(g) for g in self.gates)
        return f"QuantumCircuit({self.num_qubits} qubits, gates=[{gate_str}])"
    
    def __str__(self):
        return self.draw()
