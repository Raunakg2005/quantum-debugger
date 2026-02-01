"""
Gate Reduction and Optimization

Reduce quantum circuit gate count through cancellation, merging,
and pattern matching.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class GateOptimizer:
    """
    Optimize quantum circuits by reducing gate count.

    Applies various optimization techniques:
    - Gate cancellation (H·H = I, X·X = I)
    - Rotation merging (Rz(θ₁)·Rz(θ₂) = Rz(θ₁+θ₂))
    - Pattern matching and replacement
    - Redundant gate removal

    Examples:
        >>> optimizer = GateOptimizer()
        >>> optimized_circuit = optimizer.optimize(circuit)
        >>> print(f"Reduced from {circuit.num_gates} to {optimized_circuit.num_gates} gates")
    """

    def __init__(self):
        """Initialize gate optimizer with optimization rules."""
        self.cancellation_rules = self._init_cancellation_rules()
        self.merge_rules = self._init_merge_rules()
        self.pattern_rules = self._init_pattern_rules()

        logger.debug("Initialized GateOptimizer")

    def _init_cancellation_rules(self) -> Dict:
        """Initialize gate cancellation rules."""
        return {
            # Self-inverse gates
            ("h", "h"): [],  # H·H = I
            ("x", "x"): [],  # X·X = I
            ("y", "y"): [],  # Y·Y = I
            ("z", "z"): [],  # Z·Z = I
            ("cnot", "cnot"): [],  # CNOT·CNOT = I
            # Pauli cancellations
            ("s", "s_dagger"): [],
            ("s_dagger", "s"): [],
            ("t", "t_dagger"): [],
            ("t_dagger", "t"): [],
        }

    def _init_merge_rules(self) -> Dict:
        """Initialize gate merging rules."""
        return {
            # Rotation merging
            "rotation_gates": ["rx", "ry", "rz"],
            "phase_gates": ["s", "t", "rz"],
        }

    def _init_pattern_rules(self) -> Dict:
        """Initialize pattern matching rules."""
        return {
            # H·X·H = Z
            ("h", "x", "h"): [("z",)],
            # H·Y·H = -Y
            ("h", "y", "h"): [("y",)],
            # H·Z·H = X
            ("h", "z", "h"): [("x",)],
        }

    def optimize(self, circuit_gates: List[Tuple]) -> List[Tuple]:
        """
        Optimize circuit by applying reduction techniques.

        Args:
            circuit_gates: List of (gate_name, qubit_indices, params) tuples

        Returns:
            Optimized gate sequence
        """
        gates = circuit_gates.copy()

        # Multiple passes for thorough optimization
        prev_count = len(gates)
        for iteration in range(3):  # Max 3 iterations
            gates = self._cancel_adjacent_gates(gates)
            gates = self._merge_rotation_gates(gates)
            gates = self._apply_pattern_matching(gates)
            gates = self._remove_identity_gates(gates)

            if len(gates) == prev_count:
                break  # Converged
            prev_count = len(gates)

        reduction = len(circuit_gates) - len(gates)
        if reduction > 0:
            logger.info(
                f"Reduced circuit from {len(circuit_gates)} to {len(gates)} gates "
                f"({reduction} gates removed)"
            )

        return gates

    def _cancel_adjacent_gates(self, gates: List[Tuple]) -> List[Tuple]:
        """Cancel adjacent inverse gates."""
        optimized = []
        i = 0

        while i < len(gates):
            if i + 1 < len(gates):
                gate1 = gates[i]
                gate2 = gates[i + 1]

                # Check if they cancel
                if self._gates_cancel(gate1, gate2):
                    i += 2  # Skip both gates
                    continue

            optimized.append(gates[i])
            i += 1

        return optimized

    def _gates_cancel(self, gate1: Tuple, gate2: Tuple) -> bool:
        """Check if two gates cancel each other."""
        # Extract gate names
        name1 = gate1[0] if isinstance(gate1, tuple) else gate1
        name2 = gate2[0] if isinstance(gate2, tuple) else gate2

        # Must act on same qubits
        if len(gate1) > 1 and len(gate2) > 1:
            if gate1[1] != gate2[1]:  # Different qubits
                return False

        # Check cancellation rules
        pair = (name1, name2)
        return pair in self.cancellation_rules

    def _merge_rotation_gates(self, gates: List[Tuple]) -> List[Tuple]:
        """Merge consecutive rotation gates on same qubit."""
        optimized = []
        i = 0

        while i < len(gates):
            if i + 1 < len(gates):
                gate1 = gates[i]
                gate2 = gates[i + 1]

                merged = self._try_merge(gate1, gate2)
                if merged is not None:
                    # Check if merged gate is identity
                    if not self._is_identity_rotation(merged):
                        optimized.append(merged)
                    i += 2
                    continue

            optimized.append(gates[i])
            i += 1

        return optimized

    def _try_merge(self, gate1: Tuple, gate2: Tuple) -> Optional[Tuple]:
        """Try to merge two rotation gates."""
        if not (isinstance(gate1, tuple) and isinstance(gate2, tuple)):
            return None

        name1, qubit1, *params1 = gate1
        name2, qubit2, *params2 = gate2

        # Must be same gate type on same qubit
        if name1 != name2 or qubit1 != qubit2:
            return None

        # Must be rotation gate
        if name1 not in self.merge_rules["rotation_gates"]:
            return None

        # Merge parameters
        if params1 and params2:
            merged_angle = params1[0] + params2[0]
            return (name1, qubit1, merged_angle)

        return None

    def _is_identity_rotation(self, gate: Tuple) -> bool:
        """Check if rotation gate is effectively identity."""
        if len(gate) < 3:
            return False

        angle = gate[2]
        # Check if angle is multiple of 2π
        return np.abs(angle % (2 * np.pi)) < 1e-10

    def _apply_pattern_matching(self, gates: List[Tuple]) -> List[Tuple]:
        """Apply pattern matching rules."""
        optimized = []
        i = 0

        while i < len(gates):
            matched = False

            # Check 3-gate patterns
            if i + 2 < len(gates):
                pattern = tuple(
                    g[0] if isinstance(g, tuple) else g for g in gates[i : i + 3]
                )

                if pattern in self.pattern_rules:
                    replacement = self.pattern_rules[pattern]
                    optimized.extend(replacement)
                    i += 3
                    matched = True

            if not matched:
                optimized.append(gates[i])
                i += 1

        return optimized

    def _remove_identity_gates(self, gates: List[Tuple]) -> List[Tuple]:
        """Remove gates that are effectively identity."""
        return [g for g in gates if not self._is_identity_gate(g)]

    def _is_identity_gate(self, gate: Tuple) -> bool:
        """Check if gate is identity."""
        if isinstance(gate, tuple) and len(gate) >= 3:
            # Rotation with zero angle
            if gate[0] in ["rx", "ry", "rz"]:
                return np.abs(gate[2]) < 1e-10
        return False

    def get_optimization_stats(
        self, original_gates: List, optimized_gates: List
    ) -> Dict:
        """
        Get optimization statistics.

        Returns:
            Dictionary with gate count reduction, etc.
        """
        return {
            "original_gate_count": len(original_gates),
            "optimized_gate_count": len(optimized_gates),
            "gates_removed": len(original_gates) - len(optimized_gates),
            "reduction_percentage": 100
            * (len(original_gates) - len(optimized_gates))
            / max(len(original_gates), 1),
        }


def optimize_circuit(circuit_gates: List[Tuple]) -> List[Tuple]:
    """
    Convenience function to optimize a circuit.

    Args:
        circuit_gates: List of gate tuples

    Returns:
        Optimized gate list

    Examples:
        >>> gates = [('h', 0), ('h', 0), ('x', 1)]
        >>> optimized = optimize_circuit(gates)
        >>> print(optimized)  # [('x', 1)]  # H·H cancelled
    """
    optimizer = GateOptimizer()
    return optimizer.optimize(circuit_gates)
