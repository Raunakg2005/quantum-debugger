"""
Hybrid Classical-Quantum Models

This module provides integration between classical neural networks
and quantum circuits, enabling hybrid quantum-classical machine learning.

Supports:
- TensorFlow/Keras integration (optional)
- PyTorch integration (optional)
- Classical preprocessing layers
- Quantum middle layers
- Classical postprocessing layers
"""

# Always available - base classes
from .layers import (
    HybridLayer,
    ClassicalPreprocessor,
    QuantumMiddleLayer,
    ClassicalPostprocessor,
)

__all__ = [
    "HybridLayer",
    "ClassicalPreprocessor",
    "QuantumMiddleLayer",
    "ClassicalPostprocessor",
]

# Optional TensorFlow integration
try:
    from .tensorflow_integration import QuantumKerasLayer, create_hybrid_model

    __all__.extend(["QuantumKerasLayer", "create_hybrid_model"])
except ImportError:
    pass

# Optional PyTorch integration
try:
    from .pytorch_integration import (
        QuantumTorchLayer,
        HybridQNN,
        create_hybrid_pytorch_model,
    )

    __all__.extend(["QuantumTorchLayer", "HybridQNN", "create_hybrid_pytorch_model"])
except ImportError:
    pass
