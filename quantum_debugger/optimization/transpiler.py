"""
Circuit Transpiler

Transpile quantum circuits to hardware topology and native gate sets.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class Transpiler:
    """
    Transpile circuits to specific hardware backends.
    
    Handles:
    - Qubit layout mapping
    - SWAP insertion for connectivity
    - Native gate decomposition
    - Hardware topology constraints
    
    Examples:
        >>> topology = {'edges': [(0,1), (1,2), (2,3)]}
        >>> transpiler = Transpiler(topology)
        >>> hw_circuit = transpiler.transpile(abstract_circuit)
    """
    
    def __init__(self, backend_topology: Dict):
        """
        Initialize transpiler.
        
        Args:
            backend_topology: Hardware coupling map
                {'edges': [(q1, q2), ...], 'n_qubits': n}
        """
        self.topology = backend_topology
        self.edges = set(backend_topology.get('edges', []))
        self.n_physical_qubits = backend_topology.get('n_qubits', 5)
        self.native_gates = self._get_native_gates()
        
        logger.info(f"Initialized Transpiler with {len(self.edges)} connections")
    
    def _get_native_gates(self) -> set:
        """Get native gate set (default: U3 + CNOT)."""
        return {'u3', 'cnot', 'id'}
    
    def transpile(
        self,
        circuit_gates: List[Tuple],
        initial_layout: Optional[List[int]] = None
    ) -> List[Tuple]:
        """
        Transpile circuit to hardware.
        
        Args:
            circuit_gates: Abstract circuit
            initial_layout: Optional qubit mapping
            
        Returns:
            Transpiled circuit
        """
        logger.debug(f"Transpiling circuit with {len(circuit_gates)} gates")
        
        # 1. Apply initial layout
        mapped = self._apply_layout(circuit_gates, initial_layout)
        
        # 2. Route for connectivity
        routed = self._route_circuit(mapped)
        
        # 3. Decompose to native gates
        native = self._decompose_to_native(routed)
        
        # 4. Final optimization
        optimized = self._post_transpile_optimization(native)
        
        overhead = len(optimized) - len(circuit_gates)
        logger.info(f"Transpilation added {overhead} gates "
                   f"({len(circuit_gates)} → {len(optimized)})")
        
        return optimized
    
    def _apply_layout(
        self,
        gates: List[Tuple],
        layout: Optional[List[int]]
    ) -> List[Tuple]:
        """Map logical to physical qubits."""
        if layout is None:
            # Identity layout
            return gates
        
        mapped = []
        for gate in gates:
            if isinstance(gate, tuple) and len(gate) >= 2:
                gate_name = gate[0]
                qubits = gate[1] if isinstance(gate[1], (list, tuple)) else [gate[1]]
                params = gate[2:] if len(gate) > 2 else []
                
                # Map qubits
                physical_qubits = [layout[q] for q in qubits]
                
                if len(physical_qubits) == 1:
                    mapped.append((gate_name, physical_qubits[0], *params))
                else:
                    mapped.append((gate_name, tuple(physical_qubits), *params))
            else:
                mapped.append(gate)
        
        return mapped
    
    def _route_circuit(self, gates: List[Tuple]) -> List[Tuple]:
        """Insert SWAP gates for connectivity."""
        routed = []
        current_mapping = list(range(self.n_physical_qubits))
        
        for gate in gates:
            if isinstance(gate, tuple) and len(gate) >= 2:
                gate_name = gate[0]
                qubits = gate[1]
                
                # Check if 2-qubit gate
                if isinstance(qubits, (list, tuple)) and len(qubits) == 2:
                    q1, q2 = qubits
                    
                    # Check connectivity
                    if (q1, q2) not in self.edges and (q2, q1) not in self.edges:
                        # Need SWAP
                        swap_path = self._find_swap_path(q1, q2, current_mapping)
                        routed.extend(swap_path)
                        
                        # Update mapping
                        for swap in swap_path:
                            if swap[0] == 'swap':
                                sq1, sq2 = swap[1]
                                current_mapping[sq1], current_mapping[sq2] = \
                                    current_mapping[sq2], current_mapping[sq1]
                
                routed.append(gate)
            else:
                routed.append(gate)
        
        return routed
    
    def _find_swap_path(
        self,
        q1: int,
        q2: int,
        mapping: List[int]
    ) -> List[Tuple]:
        """Find SWAP gates needed to connect q1 and q2."""
        # Simplified: insert one SWAP to make adjacent
        # Real implementation would use shortest path
        
        # Find intermediate qubit
        for edge in self.edges:
            if q1 in edge:
                intermediate = edge[1] if edge[0] == q1 else edge[0]
                return [('swap', (q1, intermediate))]
        
        return []  # Already connected or not possible
    
    def _decompose_to_native(self, gates: List[Tuple]) -> List[Tuple]:
        """Decompose all gates to native gate set."""
        native_circuit = []
        
        for gate in gates:
            if isinstance(gate, tuple):
                gate_name = gate[0]
                
                if gate_name in self.native_gates:
                    native_circuit.append(gate)
                else:
                    # Decompose non-native gate
                    decomposed = self._decompose_gate(gate)
                    native_circuit.extend(decomposed)
            else:
                native_circuit.append(gate)
        
        return native_circuit
    
    def _decompose_gate(self, gate: Tuple) -> List[Tuple]:
        """Decompose a single gate to native gates."""
        gate_name = gate[0]
        qubit = gate[1] if len(gate) > 1 else 0
        params = gate[2:] if len(gate) > 2 else []
        
        # Common decompositions
        decompositions = {
            'h': [('u3', qubit, np.pi/2, 0, np.pi)],
            'x': [('u3', qubit, np.pi, 0, np.pi)],
            'y': [('u3', qubit, np.pi, np.pi/2, np.pi/2)],
            'z': [('u3', qubit, 0, 0, np.pi)],
            's': [('u3', qubit, 0, 0, np.pi/2)],
            't': [('u3', qubit, 0, 0, np.pi/4)],
        }
        
        # Rotation gates
        if gate_name in ['rx', 'ry', 'rz'] and params:
            theta = params[0]
            if gate_name == 'rx':
                return [('u3', qubit, theta, -np.pi/2, np.pi/2)]
            elif gate_name == 'ry':
                return [('u3', qubit, theta, 0, 0)]
            elif gate_name == 'rz':
                return [('u3', qubit, 0, 0, theta)]
        
        return decompositions.get(gate_name, [gate])
    
    def _post_transpile_optimization(self, gates: List[Tuple]) -> List[Tuple]:
        """Final optimization after transpilation."""
        from .gate_reduction import GateOptimizer
        
        optimizer = GateOptimizer()
        return optimizer.optimize(gates)
    
    def get_transpiler_info(self) -> Dict:
        """Get transpiler configuration info."""
        return {
            'n_physical_qubits': self.n_physical_qubits,
            'n_connections': len(self.edges),
            'native_gates': list(self.native_gates),
            'topology': self.topology
        }


def transpile_circuit(
    circuit_gates: List[Tuple],
    backend_topology: Dict
) -> List[Tuple]:
    """
    Convenience function to transpile a circuit.
    
    Args:
        circuit_gates: Input circuit
        backend_topology: Hardware topology
        
    Returns:
        Transpiled circuit
        
    Examples:
        >>> topology = {'edges': [(0,1), (1,2)], 'n_qubits': 3}
        >>> transpiled = transpile_circuit(gates, topology)
    """
    transpiler = Transpiler(backend_topology)
    return transpiler.transpile(circuit_gates)
