"""
Quantum Machine Learning (QML) Module
======================================

Adds variational quantum algorithms and machine learning capabilities
to the quantum-debugger library.

Features:
- Parameterized quantum gates (RX, RY, RZ)
- Variational Quantum Eigensolver (VQE)
- Quantum Approximate Optimization Algorithm (QAOA)
- Quantum Neural Networks (QNN)
- Training and optimization framework
- Gradient calculation (parameter shift rule)

Example:
    >>> from quantum_debugger.qml import RXGate, VQE
    >>> 
    >>> # Create parameterized gate
    >>> rx = RXGate(target=0, parameter=np.pi/4)
    >>> 
    >>> # Run VQE
    >>> vqe = VQE(hamiltonian=H, ansatz=my_ansatz)
    >>> result = vqe.run(initial_params)
"""

__version__ = "0.5.0"

from .gates.parameterized import RXGate, RYGate, RZGate, ParameterizedGate

__all__ = [
    'RXGate',
    'RYGate', 
    'RZGate',
    'ParameterizedGate'
]
