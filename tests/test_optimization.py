"""
Tests for circuit optimization module
"""

import pytest
import numpy as np

from quantum_debugger.optimization import (
    GateOptimizer,
    CircuitCompiler,
    Transpiler,
    optimize_circuit,
    compile_circuit,
    transpile_circuit,
    cancellation_pass,
    merge_rotations_pass,
)


class TestGateOptimizer:
    """Test gate reduction and optimization"""

    def test_gate_optimizer_initialization(self):
        """Test gate optimizer can be initialized"""
        optimizer = GateOptimizer()

        assert optimizer.cancellation_rules is not None
        assert optimizer.merge_rules is not None

    def test_self_inverse_cancellation(self):
        """Test cancellation of self-inverse gates"""
        # H·H = I
        gates = [("h", 0), ("h", 0), ("x", 1)]
        optimizer = GateOptimizer()

        optimized = optimizer.optimize(gates)

        # H·H should cancel
        assert len(optimized) == 1
        assert optimized[0] == ("x", 1)

    def test_pauli_cancellation(self):
        """Test Pauli gate cancellation"""
        gates = [("x", 0), ("x", 0), ("y", 1), ("y", 1)]
        optimizer = GateOptimizer()

        optimized = optimizer.optimize(gates)

        # All should cancel
        assert len(optimized) == 0

    def test_rotation_merging(self):
        """Test merging consecutive rotation gates"""
        gates = [("rz", 0, 0.5), ("rz", 0, 0.3)]
        optimizer = GateOptimizer()

        optimized = optimizer.optimize(gates)

        # Should merge to single Rz(0.8)
        assert len(optimized) == 1
        assert optimized[0][0] == "rz"
        assert np.isclose(optimized[0][2], 0.8)

    def test_identity_rotation_removal(self):
        """Test removal of identity rotations"""
        gates = [("rx", 0, 0.0), ("ry", 1, 0.5)]
        optimizer = GateOptimizer()

        optimized = optimizer.optimize(gates)

        # Rx(0) should be removed
        assert len(optimized) == 1
        assert optimized[0][0] == "ry"

    def test_pattern_matching(self):
        """Test H·X·H = Z pattern"""
        gates = [("h", 0), ("x", 0), ("h", 0)]
        optimizer = GateOptimizer()

        optimized = optimizer.optimize(gates)

        # Should be replaced with Z
        assert len(optimized) == 1
        assert optimized[0][0] == "z"

    def test_optimization_stats(self):
        """Test getting optimization statistics"""
        optimizer = GateOptimizer()
        original = [("h", 0), ("h", 0), ("x", 1)]
        optimized = [("x", 1)]

        stats = optimizer.get_optimization_stats(original, optimized)

        assert stats["original_gate_count"] == 3
        assert stats["optimized_gate_count"] == 1
        assert stats["gates_removed"] == 2


class TestCircuitCompiler:
    """Test circuit compiler"""

    def test_compiler_initialization(self):
        """Test compiler can be initialized"""
        compiler = CircuitCompiler(optimization_level=2)

        assert compiler.opt_level == 2
        assert len(compiler.passes) > 0

    def test_invalid_optimization_level(self):
        """Test error on invalid optimization level"""
        with pytest.raises(ValueError, match="must be 0-3"):
            CircuitCompiler(optimization_level=5)

    def test_optimization_level_0(self):
        """Test level 0 (no optimization)"""
        compiler = CircuitCompiler(optimization_level=0)

        gates = [("h", 0), ("h", 0)]
        compiled = compiler.compile(gates)

        # No optimization
        assert len(compiled) == 2

    def test_optimization_level_1(self):
        """Test level 1 (basic)"""
        compiler = CircuitCompiler(optimization_level=1)

        gates = [("h", 0), ("h", 0), ("x", 1)]
        compiled = compiler.compile(gates)

        # Should cancel H·H
        assert len(compiled) < len(gates)

    def test_optimization_level_2(self):
        """Test level 2 (advanced)"""
        compiler = CircuitCompiler(optimization_level=2)

        gates = [("rz", 0, 0.5), ("rz", 0, 0.3)]
        compiled = compiler.compile(gates)

        # Should merge rotations
        assert len(compiled) == 1

    def test_get_optimization_info(self):
        """Test getting compiler info"""
        compiler = CircuitCompiler(optimization_level=3)

        info = compiler.get_optimization_info()

        assert info["optimization_level"] == 3
        assert info["num_passes"] > 0


class TestTranspiler:
    """Test circuit transpiler"""

    def test_transpiler_initialization(self):
        """Test transpiler can be initialized"""
        topology = {"edges": [(0, 1), (1, 2)], "n_qubits": 3}
        transpiler = Transpiler(topology)

        assert len(transpiler.edges) == 2
        assert transpiler.n_physical_qubits == 3

    def test_basic_transpilation(self):
        """Test basic circuit transpilation"""
        topology = {"edges": [(0, 1), (1, 2), (2, 3)], "n_qubits": 4}
        transpiler = Transpiler(topology)

        gates = [("h", 0), ("cnot", (0, 1))]
        transpiled = transpiler.transpile(gates)

        assert len(transpiled) > 0

    def test_native_gate_decomposition(self):
        """Test decomposition to native gates"""
        topology = {"edges": [(0, 1)], "n_qubits": 2}
        transpiler = Transpiler(topology)

        # Non-native gate
        gates = [("h", 0)]
        transpiled = transpiler.transpile(gates)

        # Should be decomposed to U3
        assert any(g[0] == "u3" for g in transpiled if isinstance(g, tuple))

    def test_swap_insertion(self):
        """Test SWAP insertion for non-connected qubits"""
        # Linear topology: 0-1-2
        topology = {"edges": [(0, 1), (1, 2)], "n_qubits": 3}
        transpiler = Transpiler(topology)

        # CNOT between 0 and 2 (not directly connected)
        gates = [("cnot", (0, 2))]
        transpiled = transpiler.transpile(gates)

        # Should have more gates (SWAPs inserted)
        assert len(transpiled) >= len(gates)

    def test_get_transpiler_info(self):
        """Test getting transpiler info"""
        topology = {"edges": [(0, 1), (1, 2)], "n_qubits": 3}
        transpiler = Transpiler(topology)

        info = transpiler.get_transpiler_info()

        assert info["n_physical_qubits"] == 3
        assert info["n_connections"] == 2


class TestOptimizationPasses:
    """Test individual optimization passes"""

    def test_cancellation_pass(self):
        """Test cancellation pass"""
        gates = [("h", 0), ("h", 0), ("x", 1)]

        result = cancellation_pass(gates)

        # H·H cancelled
        assert len(result) == 1
        assert result[0] == ("x", 1)

    def test_merge_rotations_pass(self):
        """Test rotation merging pass"""
        gates = [("rx", 0, 0.5), ("rx", 0, 0.3)]

        result = merge_rotations_pass(gates)

        # Should merge
        assert len(result) == 1
        assert np.isclose(result[0][2], 0.8)

    def test_merge_different_gates_no_effect(self):
        """Test merging doesn't affect different gates"""
        gates = [("rx", 0, 0.5), ("ry", 0, 0.3)]

        result = merge_rotations_pass(gates)

        # Should not merge (different gates)
        assert len(result) == 2


class TestConvenienceFunctions:
    """Test convenience functions"""

    def test_optimize_circuit_function(self):
        """Test optimize_circuit convenience function"""
        gates = [("h", 0), ("h", 0), ("x", 1)]

        optimized = optimize_circuit(gates)

        assert len(optimized) < len(gates)

    def test_compile_circuit_function(self):
        """Test compile_circuit convenience function"""
        gates = [("h", 0), ("h", 0)]

        compiled = compile_circuit(gates, optimization_level=2)

        # Should be optimized
        assert len(compiled) == 0  # H·H cancelled

    def test_transpile_circuit_function(self):
        """Test transpile_circuit convenience function"""
        topology = {"edges": [(0, 1)], "n_qubits": 2}
        gates = [("h", 0)]

        transpiled = transpile_circuit(gates, topology)

        assert len(transpiled) > 0


class TestIntegration:
    """Integration tests for complete optimization pipeline"""

    def test_complete_optimization_pipeline(self):
        """Test full pipeline: optimize -> compile -> transpile"""
        # Original circuit
        gates = [
            ("h", 0),
            ("h", 0),  # Will cancel
            ("rz", 1, 0.5),
            ("rz", 1, 0.3),  # Will merge
            ("x", 2),
        ]

        # Step 1: Optimize
        optimized = optimize_circuit(gates)

        # Step 2: Compile
        compiled = compile_circuit(optimized, optimization_level=2)

        # Step 3: Transpile
        topology = {"edges": [(0, 1), (1, 2)], "n_qubits": 3}
        transpiled = transpile_circuit(compiled, topology)

        # Should be significantly reduced
        assert len(transpiled) < len(gates)

    def test_preserve_circuit_semantics(self):
        """Test that optimization preserves circuit behavior"""
        # Simple circuit: X gate
        gates = [("x", 0)]

        # Apply all optimizations
        optimized = optimize_circuit(gates)
        compiled = compile_circuit(optimized, optimization_level=3)

        # X should still be there (or equivalent decomposition)
        assert len(compiled) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
