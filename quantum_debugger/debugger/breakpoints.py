"""
Breakpoint management for quantum circuit debugging
"""

from typing import Callable, List, Optional
from quantum_debugger.core.quantum_state import QuantumState


class Breakpoint:
    """Represents a breakpoint in circuit execution"""
    
    def __init__(self, gate_index: Optional[int] = None, 
                 condition: Optional[Callable[[QuantumState], bool]] = None,
                 description: str = ""):
        """
        Initialize a breakpoint
        
        Args:
            gate_index: Index of gate to break at (None for conditional)
            condition: Function that returns True when breakpoint should trigger
            description: Human-readable description
        """
        self.gate_index = gate_index
        self.condition = condition
        self.description = description
        self.enabled = True
        self.hit_count = 0
    
    def should_break(self, current_gate: int, state: QuantumState) -> bool:
        """
        Check if breakpoint should trigger
        
        Args:
            current_gate: Current gate index
            state: Current quantum state
            
        Returns:
            True if breakpoint should trigger
        """
        if not self.enabled:
            return False
        
        # Gate-based breakpoint
        if self.gate_index is not None and current_gate == self.gate_index:
            self.hit_count += 1
            return True
        
        # Conditional breakpoint
        if self.condition is not None:
            try:
                if self.condition(state):
                    self.hit_count += 1
                    return True
            except Exception:
                pass
        
        return False
    
    def __repr__(self):
        if self.gate_index is not None:
            return f"Breakpoint(gate={self.gate_index}, hits={self.hit_count})"
        return f"Breakpoint(conditional, hits={self.hit_count})"


class BreakpointManager:
    """Manages breakpoints for debugging"""
    
    def __init__(self):
        self.breakpoints: List[Breakpoint] = []
    
    def add(self, gate_index: Optional[int] = None,
            condition: Optional[Callable[[QuantumState], bool]] = None,
            description: str = "") -> Breakpoint:
        """
        Add a breakpoint
        
        Args:
            gate_index: Gate index to break at
            condition: Condition function
            description: Breakpoint description
            
        Returns:
            Created breakpoint
        """
        bp = Breakpoint(gate_index, condition, description)
        self.breakpoints.append(bp)
        return bp
    
    def remove(self, breakpoint: Breakpoint):
        """Remove a breakpoint"""
        if breakpoint in self.breakpoints:
            self.breakpoints.remove(breakpoint)
    
    def clear(self):
        """Remove all breakpoints"""
        self.breakpoints.clear()
    
    def check(self, gate_index: int, state: QuantumState) -> Optional[Breakpoint]:
        """
        Check if any breakpoint should trigger
        
        Args:
            gate_index: Current gate index
            state: Current quantum state
            
        Returns:
            Triggered breakpoint or None
        """
        for bp in self.breakpoints:
            if bp.should_break(gate_index, state):
                return bp
        return None
    
    def enable_all(self):
        """Enable all breakpoints"""
        for bp in self.breakpoints:
            bp.enabled = True
    
    def disable_all(self):
        """Disable all breakpoints"""
        for bp in self.breakpoints:
            bp.enabled = False
    
    def list_breakpoints(self) -> List[Breakpoint]:
        """Get list of all breakpoints"""
        return self.breakpoints.copy()
    
    def __len__(self):
        return len(self.breakpoints)
    
    def __repr__(self):
        return f"BreakpointManager({len(self.breakpoints)} breakpoints)"
