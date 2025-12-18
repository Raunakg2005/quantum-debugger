"""
Molecular Hamiltonians
=====================

Hamiltonians for quantum chemistry simulations.
"""

import numpy as np


def h2_hamiltonian() -> np.ndarray:
    """
    Hamiltonian for H₂ molecule at equilibrium bond distance (0.735 Å).
    
    2-qubit Hamiltonian in Jordan-Wigner encoding.
    
    H = g₀·I⊗I + g₁·I⊗Z + g₂·Z⊗I + g₃·Z⊗Z + g₄·X⊗X
    
    Returns:
        4x4 Hamiltonian matrix (in Hartree units)
    
    Expected ground state energy: -1.857275 Hartree
    
    Examples:
        >>> H = h2_hamiltonian()
        >>> eigenvalues = np.linalg.eigvalsh(H)
        >>> print(f"Ground state: {eigenvalues[0]:.6f} Hartree")
    """
    # Pauli operators
    I = np.eye(2)
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    
    # Coefficients from quantum chemistry calculations
    # Bond distance: 0.735 Angstrom
    g0 = -1.0523732
    g1 =  0.39793742
    g2 = -0.39793742
    g3 = -0.01128010
    g4 =  0.18093120
    
    # Build Hamiltonian using Kronecker products
    H = (g0 * np.kron(I, I) +
         g1 * np.kron(I, Z) +
         g2 * np.kron(Z, I) +
         g3 * np.kron(Z, Z) +
         g4 * np.kron(X, X))
    
    return H


def h2_hamiltonian_dissociation(distance: float = 0.735) -> np.ndarray:
    """
    H₂ Hamiltonian at variable bond distances.
    
    Args:
        distance: Bond distance in Angstroms
        
    Returns:
        4x4 Hamiltonian matrix
    """
    # Coefficients vary with distance
    # For now, return equilibrium Hamiltonian
    # TODO: Implement distance-dependent coefficients
    return h2_hamiltonian()


def lih_hamiltonian() -> np.ndarray:
    """
    Hamiltonian for LiH molecule.
    
    4-qubit Hamiltonian (12 spin orbitals reduced to 4 qubits).
    
    Returns:
        16x16 Hamiltonian matrix
        
    Expected ground state energy: -7.882 Hartree
    """
    # Simplified 4-qubit LiH Hamiltonian
    # Full implementation requires more Pauli terms
    
    I = np.eye(2, dtype=complex)
    Z = np.array([[1, 0], [0, -1]], dtype=complex)
    
    # Placeholder - simplified version
    # Real LiH has ~100+ Pauli terms
    H = np.kron(np.kron(I, I), np.kron(Z, Z))
    
    return H


def pauli_decomposition(hamiltonian: np.ndarray) -> list:
    """
    Decompose Hamiltonian into Pauli operators.
    
    H = Σᵢ cᵢ Pᵢ
    
    where Pᵢ are Pauli strings (e.g., "IXYZ")
    
    Args:
        hamiltonian: Hamiltonian matrix
        
    Returns:
        List of (coefficient, pauli_string) tuples
    """
    # To be implemented for general Hamiltonians
    pass
