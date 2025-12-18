"""
Basic QML Example: Parameterized Quantum Gates

This example demonstrates the fundamental usage of RX, RY, and RZ gates.
"""

import sys
import os
# Add parent directory to path for development
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quantum_debugger.qml import RXGate, RYGate, RZGate
import numpy as np


def basic_gate_usage():
    """Demonstrate creating and using parameterized gates"""
    print("=" * 60)
    print("Basic Parameterized Gates Example")
    print("=" * 60)
    
    # Create RX gate
    print("\n1. Creating RX gate (X-axis rotation)")
    rx = RXGate(target=0, parameter=np.pi/4)
    print(f"   Gate: {rx}")
    print(f"   Matrix shape: {rx.matrix().shape}")
    print(f"   Matrix:\n{rx.matrix()}")
    
    # Create RY gate
    print("\n2. Creating RY gate (Y-axis rotation)")
    ry = RYGate(target=1, parameter=np.pi/3)
    print(f"   Gate: {ry}")
    
    # Create RZ gate
    print("\n3. Creating RZ gate (Z-axis/Phase rotation)")
    rz = RZGate(target=2, parameter=np.pi/6)
    print(f"   Gate: {rz}")


def verify_unitarity():
    """Verify that gates are unitary (U†U = I)"""
    print("\n" + "=" * 60)
    print("Verifying Unitarity")
    print("=" * 60)
    
    angles = [np.pi/6, np.pi/4, np.pi/3, np.pi/2, np.pi]
    
    for angle in angles:
        rx = RXGate(target=0, parameter=angle)
        U = rx.matrix()
        
        # Compute U†U
        identity = U.conj().T @ U
        
        # Check if equal to I
        is_unitary = np.allclose(identity, np.eye(2))
        
        print(f"   RX({angle:.4f}): Unitary = {is_unitary}")


def special_angles():
    """Test gates at special angles"""
    print("\n" + "=" * 60)
    print("Special Angles")
    print("=" * 60)
    
    # RX(0) should be identity
    rx_zero = RXGate(target=0, parameter=0)
    is_identity = np.allclose(rx_zero.matrix(), np.eye(2))
    print(f"\n   RX(0) = I: {is_identity}")
    
    # RX(π) should be -iX (Pauli X with phase)
    rx_pi = RXGate(target=0, parameter=np.pi)
    X = np.array([[0, 1], [1, 0]])
    is_pauli_x = np.allclose(rx_pi.matrix(), -1j * X)
    print(f"   RX(π) = -iX: {is_pauli_x}")
    
    # RY(π/2) creates superposition
    ry_half_pi = RYGate(target=0, parameter=np.pi/2)
    state_0 = np.array([1, 0])  # |0⟩
    superposition = ry_half_pi.matrix() @ state_0
    expected = np.array([1/np.sqrt(2), 1/np.sqrt(2)])
    is_superposition = np.allclose(superposition, expected)
    print(f"   RY(π/2)|0⟩ = |+⟩: {is_superposition}")


def parameter_updates():
    """Demonstrate parameter updates"""
    print("\n" + "=" * 60)
    print("Parameter Updates")
    print("=" * 60)
    
    rx = RXGate(target=0, parameter=0.5, trainable=True)
    print(f"\n   Initial parameter: θ = {rx.parameter:.4f}")
    print(f"   Trainable: {rx.trainable}")
    
    # Simulate gradient descent step
    print("\n   Simulating gradient descent...")
    rx.gradient = 0.123  # Computed gradient
    learning_rate = 0.1
    
    print(f"   Gradient: {rx.gradient:.4f}")
    print(f"   Learning rate: {learning_rate}")
    
    # Update parameter
    rx.parameter -= learning_rate * rx.gradient
    print(f"   Updated parameter: θ = {rx.parameter:.4f}")


def create_variational_circuit():
    """Build a simple variational circuit"""
    print("\n" + "=" * 60)
    print("Variational Circuit Example")
    print("=" * 60)
    
    # Parameters for 2-qubit, 2-layer circuit
    params = np.array([0.5, 0.8, 0.3, 0.7])
    
    print(f"\n   Parameters: {params}")
    print(f"   Circuit: 2 qubits, 2 layers")
    
    # Layer 1: RY rotations
    print("\n   Layer 1 (RY rotations):")
    ry0 = RYGate(target=0, parameter=params[0], trainable=True)
    ry1 = RYGate(target=1, parameter=params[1], trainable=True)
    print(f"      RY(q0, θ={params[0]:.4f})")
    print(f"      RY(q1, θ={params[1]:.4f})")
    print("      CNOT(q0, q1)")
    
    # Layer 2: RX rotations
    print("\n   Layer 2 (RX rotations):")
    rx0 = RXGate(target=0, parameter=params[2], trainable=True)
    rx1 = RXGate(target=1, parameter=params[3], trainable=True)
    print(f"      RX(q0, θ={params[2]:.4f})")
    print(f"      RX(q1, θ={params[3]:.4f})")
    
    gates = [ry0, ry1, rx0, rx1]
    print(f"\n   Total parameterized gates: {len(gates)}")
    print(f"   All trainable: {all(g.trainable for g in gates)}")


def main():
    """Run all examples"""
    basic_gate_usage()
    verify_unitarity()
    special_angles()
    parameter_updates()
    create_variational_circuit()
    
    print("\n" + "=" * 60)
    print("Example Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  - Try VQE for molecular ground states")
    print("  - Implement QAOA for optimization")
    print("  - Build quantum neural networks")


if __name__ == "__main__":
    main()
