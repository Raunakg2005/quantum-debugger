"""
Main debugger class for step-through quantum circuit execution
"""

from typing import Optional, List, Dict
from quantum_debugger.core.circuit import QuantumCircuit
from quantum_debugger.core.quantum_state import QuantumState
from quantum_debugger.debugger.breakpoints import BreakpointManager, Breakpoint
from quantum_debugger.debugger.inspector import StateInspector


class ExecutionState:
    """Represents the state at a point in circuit execution"""

    def __init__(
        self, gate_index: int, quantum_state: QuantumState, gate_name: str = ""
    ):
        self.gate_index = gate_index
        self.quantum_state = quantum_state.copy()
        self.gate_name = gate_name

    def __repr__(self):
        return f"ExecutionState(gate={self.gate_index}, {self.gate_name})"


class QuantumDebugger:
    """Interactive debugger for quantum circuits"""

    def __init__(
        self, circuit: QuantumCircuit, initial_state: Optional[QuantumState] = None
    ):
        """
        Initialize the debugger

        Args:
            circuit: Quantum circuit to debug
            initial_state: Optional initial state (defaults to |0...0>)
        """
        self.circuit = circuit
        self.initial_state = initial_state or QuantumState(circuit.num_qubits)
        self.current_state = self.initial_state.copy()
        self.current_gate_index = 0
        self.execution_history: List[ExecutionState] = []
        self.breakpoints = BreakpointManager()
        self.inspector = StateInspector()

        # Store initial state in history
        self.execution_history.append(ExecutionState(0, self.current_state, "INITIAL"))

    def reset(self):
        """Reset debugger to initial state"""
        self.current_state = self.initial_state.copy()
        self.current_gate_index = 0
        self.execution_history = [ExecutionState(0, self.current_state, "INITIAL")]

    def step(self, steps: int = 1) -> bool:
        """
        Execute one or more gates

        Args:
            steps: Number of gates to execute

        Returns:
            True if stepped successfully, False if at end
        """
        for _ in range(steps):
            if self.current_gate_index >= len(self.circuit.gates):
                return False

            # Get current gate
            gate = self.circuit.gates[self.current_gate_index]

            # Apply gate
            self.current_state.apply_gate(gate.matrix, gate.qubits)

            # Update index
            self.current_gate_index += 1

            # Save state to history
            self.execution_history.append(
                ExecutionState(self.current_gate_index, self.current_state, str(gate))
            )

            # Check for breakpoints
            bp = self.breakpoints.check(self.current_gate_index, self.current_state)
            if bp:
                print(f"⚠️  Breakpoint hit: {bp}")
                return True

        return True

    def step_back(self, steps: int = 1) -> bool:
        """
        Step backwards in execution history

        Args:
            steps: Number of steps to go back

        Returns:
            True if stepped back successfully
        """
        target_index = max(0, self.current_gate_index - steps)

        if target_index < len(self.execution_history):
            exec_state = self.execution_history[target_index]
            self.current_state = exec_state.quantum_state.copy()
            self.current_gate_index = exec_state.gate_index
            return True

        return False

    def run_to_end(self):
        """Execute all remaining gates"""
        while self.step():
            pass

    def run_until_breakpoint(self):
        """Execute until a breakpoint is hit or circuit ends"""
        while self.current_gate_index < len(self.circuit.gates):
            bp = self.breakpoints.check(self.current_gate_index, self.current_state)
            if bp:
                print(
                    f"⚠️  Breakpoint hit at gate {self.current_gate_index}: {bp.description}"
                )
                break

            if not self.step():
                break

    def set_breakpoint(
        self, gate: Optional[int] = None, condition=None, description: str = ""
    ) -> Breakpoint:
        """
        Set a breakpoint

        Args:
            gate: Gate index to break at
            condition: Conditional function
            description: Breakpoint description

        Returns:
            Created breakpoint
        """
        return self.breakpoints.add(gate, condition, description)

    def clear_breakpoints(self):
        """Remove all breakpoints"""
        self.breakpoints.clear()

    def add_breakpoint_at_gate(self, gate_index: int):
        """Add breakpoint at specific gate index"""
        return self.set_breakpoint(
            gate=gate_index, description=f"Breakpoint at gate {gate_index}"
        )

    def continue_execution(self):
        """Continue execution until end (alias for run_to_end)"""
        return self.run_to_end()

    def get_current_state(self):
        """Get current quantum state (alias for get_state)"""
        return self.get_state()

    def inspect_state(self) -> Dict:
        """
        Get detailed information about current state

        Returns:
            Dictionary with state information
        """
        return self.inspector.get_state_summary(self.current_state)

    def get_state(self) -> QuantumState:
        """Get current quantum state"""
        return self.current_state.copy()

    def visualize(self):
        """Print visualization of current state"""
        print(f"\n{'=' * 60}")
        print(f"Gate {self.current_gate_index}/{len(self.circuit.gates)}")
        if self.current_gate_index < len(self.circuit.gates):
            print(f"Next gate: {self.circuit.gates[self.current_gate_index]}")
        else:
            print("Circuit execution complete")
        print(f"{'=' * 60}")

        self.inspector.print_state_info(self.current_state)

    def get_execution_trace(self) -> List[Dict]:
        """
        Get full execution trace

        Returns:
            List of execution states with information
        """
        trace = []
        for exec_state in self.execution_history:
            trace.append(
                {
                    "gate_index": exec_state.gate_index,
                    "gate_name": exec_state.gate_name,
                    "state_summary": self.inspector.get_state_summary(
                        exec_state.quantum_state
                    ),
                }
            )
        return trace

    def compare_with_expected(self, expected_state: QuantumState) -> Dict:
        """
        Compare current state with expected state

        Args:
            expected_state: Expected quantum state

        Returns:
            Comparison metrics
        """
        return self.inspector.compare_states(self.current_state, expected_state)

    def print_status(self):
        """Print current debugging status"""
        print(f"\n{'=' * 60}")
        print("DEBUGGER STATUS")
        print(f"{'=' * 60}")
        print(
            f"Circuit: {self.circuit.num_qubits} qubits, {len(self.circuit.gates)} gates"
        )
        print(
            f"Current position: Gate {self.current_gate_index}/{len(self.circuit.gates)}"
        )

        if self.current_gate_index < len(self.circuit.gates):
            print(f"Next gate: {self.circuit.gates[self.current_gate_index]}")
        else:
            print("Status: Circuit execution complete")

        print(f"\nBreakpoints: {len(self.breakpoints)}")
        for bp in self.breakpoints.list_breakpoints():
            status = "✓" if bp.enabled else "✗"
            print(f"  {status} {bp}")

        print(f"\nExecution history: {len(self.execution_history)} states saved")
        print(f"{'=' * 60}\n")

    def __repr__(self):
        return (
            f"QuantumDebugger(gate {self.current_gate_index}/{len(self.circuit.gates)})"
        )
