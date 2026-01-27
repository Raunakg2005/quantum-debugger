"""
Circuit Compiler

Multi-level circuit optimization and compilation for quantum circuits.
"""


from typing import Dict, List, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class CircuitCompiler:
    """
    Compile quantum circuits with configurable optimization levels.

    Optimization levels:
    - Level 0: No optimization (passthrough)
    - Level 1: Basic gate reduction
    - Level 2: Gate reduction + merging + depth optimization
    - Level 3: Aggressive optimization + layout optimization

    Examples:
        >>> compiler = CircuitCompiler(optimization_level=2)
        >>> compiled = compiler.compile(circuit)
    """

    def __init__(self, optimization_level: int = 2):
        """
        Initialize circuit compiler.

        Args:
            optimization_level: 0-3, higher = more aggressive
        """
        if not 0 <= optimization_level <= 3:
            raise ValueError("Optimization level must be 0-3")

        self.opt_level = optimization_level
        self.passes = self._configure_passes()

        logger.info(f"Initialized CircuitCompiler (level {optimization_level})")

    def _configure_passes(self) -> List[Callable]:
        """Configure optimization passes based on level."""
        from .optimization_passes import (
            cancellation_pass,
            merge_rotations_pass,
            depth_reduction_pass,
            gate_count_reduction_pass,
        )

        if self.opt_level == 0:
            return []
        elif self.opt_level == 1:
            return [cancellation_pass]
        elif self.opt_level == 2:
            return [cancellation_pass, merge_rotations_pass, depth_reduction_pass]
        else:  # Level 3
            return [
                cancellation_pass,
                merge_rotations_pass,
                depth_reduction_pass,
                gate_count_reduction_pass,
                cancellation_pass,  # Final cleanup
            ]

    def compile(
        self, circuit_gates: List, backend_constraints: Optional[Dict] = None
    ) -> List:
        """
        Compile circuit with optimizations.

        Args:
            circuit_gates: Input circuit as list of gates
            backend_constraints: Optional hardware constraints

        Returns:
            Compiled circuit
        """
        compiled = circuit_gates.copy()

        logger.debug(f"Compiling circuit with {len(compiled)} gates")

        # Apply optimization passes
        for pass_func in self.passes:
            prev_count = len(compiled)
            compiled = pass_func(compiled)

            if len(compiled) < prev_count:
                logger.debug(
                    f"{pass_func.__name__}: {prev_count} → {len(compiled)} gates"
                )

        # Apply backend constraints if provided
        if backend_constraints:
            compiled = self._apply_constraints(compiled, backend_constraints)

        improvement = len(circuit_gates) - len(compiled)
        if improvement > 0:
            pct = 100 * improvement / len(circuit_gates)
            logger.info(
                f"Compilation reduced circuit by {improvement} gates ({pct:.1f}%)"
            )

        return compiled

    def _apply_constraints(self, circuit: List, constraints: Dict) -> List:
        """Apply hardware backend constraints."""
        # Placeholder for backend-specific optimizations
        max_gates = constraints.get("max_gates")
        if max_gates and len(circuit) > max_gates:
            logger.warning(f"Circuit has {len(circuit)} gates, exceeds max {max_gates}")

        return circuit

    def get_optimization_info(self) -> Dict:
        """Get information about configured optimization."""
        return {
            "optimization_level": self.opt_level,
            "num_passes": len(self.passes),
            "passes": [p.__name__ for p in self.passes],
        }


def compile_circuit(circuit_gates: List, optimization_level: int = 2) -> List:
    """
    Convenience function to compile a circuit.

    Args:
        circuit_gates: Input circuit
        optimization_level: 0-3

    Returns:
        Compiled circuit

    Examples:
        >>> gates = [('h', 0), ('h', 0), ('x', 1), ('x', 1)]
        >>> compiled = compile_circuit(gates, optimization_level=2)
        >>> print(compiled)  # [] - all gates cancelled
    """
    compiler = CircuitCompiler(optimization_level=optimization_level)
    return compiler.compile(circuit_gates)
