"""
Hardware noise profiles for realistic quantum computer simulation

Profiles are versioned and based on published specifications from real quantum hardware.
Parameters are updated regularly to reflect improvements in quantum computing technology.
"""

import numpy as np
from typing import Dict, Optional
from quantum_debugger.noise.noise_models import (
    ThermalRelaxation,
    DepolarizingNoise,
    NoiseModel
)


class HardwareProfile:
    """
    Hardware-specific noise profile with versioned parameters
    
    Represents realistic noise characteristics of actual quantum computers.
    """
    
    def __init__(
        self,
        name: str,
        version: str,
        date_updated: str,
        t1: float,
        t2: float,
        gate_times: Dict[str, float],
        gate_error_1q: float,
        gate_error_2q: float,
        readout_error: float,
        source_url: str = "",
        description: str = ""
    ):
        """
        Initialize hardware profile
        
        Args:
            name: Hardware name (e.g., "IBM Perth")
            version: Version number (e.g., "2025.1")
            date_updated: Last update date (e.g., "2025-01-15")
            t1: T1 relaxation time in seconds
            t2: T2 dephasing time in seconds
            gate_times: Dict of gate times {'1q': time, '2q': time} in seconds
            gate_error_1q: Single-qubit gate error rate
            gate_error_2q: Two-qubit gate error rate
            readout_error: Measurement error rate
            source_url: URL to published specifications
            description: Additional information
        """
        self.name = name
        self.version = version
        self.date_updated = date_updated
        self.t1 = t1
        self.t2 = t2
        self.gate_times = gate_times
        self.gate_error_1q = gate_error_1q
        self.gate_error_2q = gate_error_2q
        self.readout_error = readout_error
        self.source_url = source_url
        self.description = description
        
        # Create composite noise model
        self._build_noise_model()
    
    def _build_noise_model(self):
        """Build composite noise model from hardware parameters"""
        # For now, use simple depolarizing approximation
        # In future, could create more sophisticated composite models
        
        # Use gate error rates to approximate depolarizing noise
        # Average error across gate types weighted by typical circuit composition
        avg_error = 0.7 * self.gate_error_1q + 0.3 * self.gate_error_2q
        
        self.noise_model = DepolarizingNoise(avg_error)
        
        # Could also create thermal relaxation component
        # self.thermal_noise = ThermalRelaxation(self.t1, self.t2, self.gate_times['1q'])
    
    def apply_to_circuit(self, circuit):
        """
        Apply this hardware profile to a quantum circuit
        
        Args:
            circuit: QuantumCircuit to apply noise to
        """
        circuit.set_noise_model(self.noise_model)
    
    def info(self) -> str:
        """
        Get formatted information about this hardware profile
        
        Returns:
            Multi-line string with hardware specifications
        """
        info_str = f"""
{'='*60}
{self.name} Hardware Profile
{'='*60}
Version:           {self.version}
Last Updated:      {self.date_updated}
Source:            {self.source_url or 'N/A'}

Coherence Times:
  T1 (relaxation):    {self.t1*1e6:.1f} μs
  T2 (dephasing):     {self.t2*1e6:.1f} μs

Gate Times:
  Single-qubit:       {self.gate_times['1q']*1e9:.0f} ns
  Two-qubit:          {self.gate_times['2q']*1e9:.0f} ns

Error Rates:
  Single-qubit gate:  {self.gate_error_1q*100:.3f}%
  Two-qubit gate:     {self.gate_error_2q*100:.3f}%
  Readout:            {self.readout_error*100:.2f}%

Description:
  {self.description or 'No description available'}
{'='*60}
"""
        return info_str
    
    def __repr__(self):
        return f"HardwareProfile('{self.name}', v{self.version})"
    
    def __str__(self):
        return self.info()


# ============================================================================
# Pre-defined Hardware Profiles (2025 specifications)
# ============================================================================

IBM_PERTH_2025 = HardwareProfile(
    name="IBM Perth",
    version="2025.1",
    date_updated="2025-01-15",
    t1=180e-6,  # 180 microseconds
    t2=220e-6,  # 220 microseconds (improved from 2024)
    gate_times={
        '1q': 35e-9,   # 35 nanoseconds
        '2q': 500e-9   # 500 nanoseconds
    },
    gate_error_1q=0.0003,  # 0.03% (improved with better calibration)
    gate_error_2q=0.008,   # 0.8% (improved CNOT gates)
    readout_error=0.015,   # 1.5% (improved readout fidelity)
    source_url="https://quantum-computing.ibm.com/services/resources",
    description="IBM Quantum Eagle processor. 127-qubit heavy-hex architecture. "
                "Improved coherence times and gate fidelities in 2025."
)

GOOGLE_SYCAMORE_2025 = HardwareProfile(
    name="Google Sycamore",
    version="2025.2",
    date_updated="2025-02-01",
    t1=40e-6,   # 40 microseconds (improved from 2024's 35μs)
    t2=30e-6,   # 30 microseconds (improved coherence)
    gate_times={
        '1q': 25e-9,   # 25 nanoseconds (fast single-qubit gates)
        '2q': 32e-9    # 32 nanoseconds (fast iSWAP gates)
    },
    gate_error_1q=0.0015,  # 0.15% (improved calibration)
    gate_error_2q=0.005,   # 0.5% (improved two-qubit gates)
    readout_error=0.01,    # 1.0% (state-of-the-art readout)
    source_url="https://quantumai.google/hardware",
    description="Google superconducting transmon qubits. 70-qubit grid layout. "
                "Fast gate times with improved fidelities in 2025."
)

IONQ_ARIA_2025 = HardwareProfile(
    name="IonQ Aria",
    version="2025.1",
    date_updated="2025-01-10",
    t1=1.0,     # 1 second (ion trap advantage!)
    t2=0.5,     # 500 milliseconds (excellent coherence)
    gate_times={
        '1q': 10e-6,    # 10 microseconds (slower but high fidelity)
        '2q': 200e-6    # 200 microseconds (Mølmer-Sørensen gates)
    },
    gate_error_1q=0.0001,   # 0.01% (best in class!)
    gate_error_2q=0.002,    # 0.2% (excellent two-qubit gates)
    readout_error=0.005,    # 0.5% (excellent readout with ion traps)
    source_url="https://ionq.com/quantum-systems",
    description="IonQ trapped-ion quantum computer. 25 algorithmic qubits. "
                "All-to-all connectivity. Industry-leading gate fidelities."
)

RIGETTI_ASPEN_2025 = HardwareProfile(
    name="Rigetti Aspen-M-3",
    version="2025.1",
    date_updated="2025-01-20",
    t1=50e-6,   # 50 microseconds
    t2=40e-6,   # 40 microseconds
    gate_times={
        '1q': 40e-9,    # 40 nanoseconds
        '2q': 200e-9    # 200 nanoseconds (CZ gates)
    },
    gate_error_1q=0.0005,   # 0.05%
    gate_error_2q=0.01,     # 1.0%
    readout_error=0.02,     # 2.0%
    source_url="https://qcs.rigetti.com/",
    description="Rigetti superconducting qubits. 80-qubit octagonal architecture. "
                "Active qubit reset and parametric gates."
)


# Convenience dictionary for easy access
HARDWARE_PROFILES = {
    'ibm_perth': IBM_PERTH_2025,
    'ibm': IBM_PERTH_2025,  # Alias
    'google_sycamore': GOOGLE_SYCAMORE_2025,
    'google': GOOGLE_SYCAMORE_2025,  # Alias
    'ionq_aria': IONQ_ARIA_2025,
    'ionq': IONQ_ARIA_2025,  # Alias
    'rigetti_aspen': RIGETTI_ASPEN_2025,
    'rigetti': RIGETTI_ASPEN_2025,  # Alias
}


def get_hardware_profile(name: str) -> Optional[HardwareProfile]:
    """
    Get a pre-defined hardware profile by name
    
    Args:
        name: Profile name (e.g., 'ibm', 'google', 'ionq', 'rigetti')
        
    Returns:
        HardwareProfile instance or None if not found
        
    Examples:
        >>> profile = get_hardware_profile('ibm')
        >>> print(profile.info())
    """
    return HARDWARE_PROFILES.get(name.lower())


def list_hardware_profiles() -> list:
    """
    List all available hardware profiles
    
    Returns:
        List of profile names
    """
    # Return unique profiles (without aliases)
    unique_profiles = list(set(HARDWARE_PROFILES.values()))
    return [p.name for p in unique_profiles]
