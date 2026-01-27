"""
Composite noise model for combining multiple noise sources
"""


from typing import List, Optional
from quantum_debugger.noise.noise_models import NoiseModel


class CompositeNoise(NoiseModel):
    """
    Composite noise model that applies multiple noise sources sequentially

    Allows realistic simulation by combining different noise types:
    - Thermal relaxation (T1/T2)
    - Depolarizing errors
    - Readout errors
    - etc.

    Example:
        >>> thermal = ThermalRelaxation(t1=100e-6, t2=80e-6, gate_time=50e-9)
        >>> depol = DepolarizingNoise(0.001)
        >>> composite = CompositeNoise([thermal, depol])
    """

    def __init__(self, noise_models: List[NoiseModel]):
        """
        Initialize composite noise model

        Args:
            noise_models: List of NoiseModel instances to apply sequentially
        """
        if not noise_models:
            raise ValueError("CompositeNoise requires at least one noise model")

        self.noise_models = noise_models

    def apply(self, state, qubits: Optional[list] = None):
        """
        Apply all noise models sequentially

        Args:
            state: QuantumState to apply noise to
            qubits: Optional list of qubits (None = all qubits)
        """
        for noise_model in self.noise_models:
            noise_model.apply(state, qubits)

    def __repr__(self):
        models_str = ", ".join(repr(m) for m in self.noise_models)
        return f"CompositeNoise([{models_str}])"

    def __str__(self):
        return f"CompositeNoise with {len(self.noise_models)} noise sources"
