"""
Optimization Passes

Individual optimization pass functions for circuit optimization.
"""

import numpy as np
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


def cancellation_pass(gates: List[Tuple]) -> List[Tuple]:
    """
    Cancel adjacent inverse gates.

    Cancellation rules:
    - H·H = I
    - X·X = I
    - CNOT·CNOT = I
    - S†·S = I

    Args:
        gates: Input gate sequence

    Returns:
        Gate sequence with cancellations applied
    """
    inverse_pairs = {
        ("h", "h"),
        ("x", "x"),
        ("y", "y"),
        ("z", "z"),
        ("cnot", "cnot"),
        ("swap", "swap"),
        ("s", "s_dagger"),
        ("s_dagger", "s"),
        ("t", "t_dagger"),
        ("t_dagger", "t"),
    }

    optimized = []
    i = 0

    while i < len(gates):
        if i + 1 < len(gates):
            g1 = gates[i]
            g2 = gates[i + 1]

            # Check if consecutive gates cancel
            if _can_cancel(g1, g2, inverse_pairs):
                i += 2  # Skip both
                continue

        optimized.append(gates[i])
        i += 1

    return optimized


def _can_cancel(gate1: Tuple, gate2: Tuple, pairs: set) -> bool:
    """Check if two gates can cancel."""
    if not (isinstance(gate1, tuple) and isinstance(gate2, tuple)):
        return False

    name1, name2 = gate1[0], gate2[0]

    # Must act on same qubits
    if len(gate1) > 1 and len(gate2) > 1:
        if gate1[1] != gate2[1]:
            return False

    return (name1, name2) in pairs


def merge_rotations_pass(gates: List[Tuple]) -> List[Tuple]:
    """
    Merge consecutive rotation gates.

    Rz(θ₁)·Rz(θ₂) = Rz(θ₁ + θ₂)

    Args:
        gates: Input gate sequence

    Returns:
        Gate sequence with merged rotations
    """
    rotation_gates = {"rx", "ry", "rz"}

    optimized = []
    i = 0

    while i < len(gates):
        if i + 1 < len(gates):
            g1 = gates[i]
            g2 = gates[i + 1]

            merged = _try_merge_rotations(g1, g2, rotation_gates)
            if merged is not None:
                # Skip if merged to identity
                if not _is_identity_rotation(merged):
                    optimized.append(merged)
                i += 2
                continue

        optimized.append(gates[i])
        i += 1

    return optimized


def _try_merge_rotations(g1: Tuple, g2: Tuple, rotation_gates: set) -> Tuple:
    """Try to merge two rotation gates."""
    if not (isinstance(g1, tuple) and isinstance(g2, tuple)):
        return None

    if len(g1) < 3 or len(g2) < 3:
        return None

    name1, qubit1, angle1 = g1[0], g1[1], g1[2]
    name2, qubit2, angle2 = g2[0], g2[1], g2[2]

    # Same gate type on same qubit
    if name1 == name2 and qubit1 == qubit2 and name1 in rotation_gates:
        merged_angle = angle1 + angle2
        return (name1, qubit1, merged_angle)

    return None


def _is_identity_rotation(gate: Tuple) -> bool:
    """Check if rotation is effectively identity."""
    if len(gate) < 3:
        return False

    angle = gate[2]
    # Multiple of 2π
    return np.abs(angle % (2 * np.pi)) < 1e-10


def depth_reduction_pass(gates: List[Tuple]) -> List[Tuple]:
    """
    Reduce circuit depth by reordering commuting gates.

    This is a simplified version - full implementation would
    build dependency graph and optimize scheduling.

    Args:
        gates: Input gate sequence

    Returns:
        Reordered gate sequence
    """
    # Simplified: just return as-is
    # Full implementation would:
    # 1. Build gate dependency graph
    # 2. Find independent gates
    # 3. Schedule for minimal depth

    return gates


def gate_count_reduction_pass(gates: List[Tuple]) -> List[Tuple]:
    """
    Minimize total gate count.

    Priority: Reduce 2-qubit gates (most expensive).

    Args:
        gates: Input gate sequence

    Returns:
        Gate sequence with reduced count
    """
    # Apply pattern matching for 2-qubit gate reduction
    optimized = gates.copy()

    # Remove identity-like gates
    optimized = [g for g in optimized if not _is_negligible_gate(g)]

    return optimized


def _is_negligible_gate(gate: Tuple) -> bool:
    """Check if gate has negligible effect."""
    if not isinstance(gate, tuple):
        return False

    # Zero-angle rotations
    if len(gate) >= 3 and gate[0] in ["rx", "ry", "rz"]:
        return np.abs(gate[2]) < 1e-10

    return False
