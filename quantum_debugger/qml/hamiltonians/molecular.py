"""
Molecular Hamiltonians for Quantum Chemistry

Provides pre-computed Hamiltonians for common molecules used in VQE.
"""

import numpy as np
from typing import Dict, Tuple


def h2_hamiltonian(bond_length: float = 0.735) -> Tuple[np.ndarray, float]:
    """
    Hydrogen molecule (H2) Hamiltonian.

    Args:
        bond_length: H-H bond length in Angstroms (default: 0.735 Å)

    Returns:
        (hamiltonian_matrix, nuclear_repulsion_energy)

    Example:
        >>> H, E_nuc = h2_hamiltonian(0.735)
        >>> print(H.shape)
        (4, 4)
    """
    # Qubit Hamiltonian for H2 in minimal basis (STO-3G)
    # 2 qubits needed for 2 spin orbitals

    # Coefficients depend on bond length
    # These are approximate values for demonstration
    if abs(bond_length - 0.735) < 0.01:
        # Equilibrium geometry
        coeffs = {
            "II": -0.81054,
            "IZ": 0.17218,
            "ZI": 0.17218,
            "ZZ": -0.22575,
            "XX": 0.04523,
        }
        E_nuc = 0.71317
    else:
        # Scale coefficients approximately
        scale = 0.735 / bond_length
        coeffs = {
            "II": -0.81054 * scale,
            "IZ": 0.17218 * scale,
            "ZI": 0.17218 * scale,
            "ZZ": -0.22575 * scale,
            "XX": 0.04523 * scale,
        }
        E_nuc = 0.71317 * scale

    # Build Hamiltonian matrix (4x4 for 2 qubits)
    H = np.zeros((4, 4))

    # Identity contribution
    H += coeffs["II"] * np.eye(4)

    # Pauli Z terms
    Z = np.array([[1, 0], [0, -1]])
    identity = np.eye(2)

    IZ = np.kron(identity, Z)
    ZI = np.kron(Z, identity)
    ZZ = np.kron(Z, Z)

    H += coeffs["IZ"] * IZ
    H += coeffs["ZI"] * ZI
    H += coeffs["ZZ"] * ZZ

    # XX term
    X = np.array([[0, 1], [1, 0]])
    XX = np.kron(X, X)
    H += coeffs["XX"] * XX

    return H, E_nuc


def lih_hamiltonian(bond_length: float = 1.546) -> Tuple[np.ndarray, float]:
    """
    Lithium Hydride (LiH) Hamiltonian.

    More complex than H2, requires 4 qubits (8 spin orbitals mapped to 4 qubits).

    Args:
        bond_length: Li-H bond length in Angstroms (default: 1.546 Å equilibrium)

    Returns:
        (hamiltonian_matrix, nuclear_repulsion_energy)

    Example:
        >>> H, E_nuc = lih_hamiltonian()
        >>> print(H.shape)
        (16, 16)
    """
    # LiH requires 4 qubits (16x16 matrix)
    n_qubits = 4
    dim = 2**n_qubits

    # Pauli matrices
    identity = np.eye(2)
    X = np.array([[0, 1], [1, 0]])
    Y = np.array([[0, -1j], [1j, 0]])
    Z = np.array([[1, 0], [0, -1]])

    # Coefficients for LiH at equilibrium geometry
    # These are simplified values for demonstration
    if abs(bond_length - 1.546) < 0.01:
        coeffs = {
            "IIII": -7.8823,
            "IIIZ": 0.1809,
            "IIZI": 0.1809,
            "IZII": -0.4750,
            "ZIII": -0.4750,
            "IIZZ": 0.1750,
            "IZIZ": 0.1201,
            "ZIIZ": 0.1201,
            "ZZII": 0.1629,
            "IXXI": 0.0454,
            "IYYI": 0.0454,
        }
        E_nuc = 0.9953
    else:
        # Approximate scaling
        scale = 1.546 / bond_length
        coeffs = {
            k: v * scale
            for k, v in {
                "IIII": -7.8823,
                "IIIZ": 0.1809,
                "IIZI": 0.1809,
                "IZII": -0.4750,
                "ZIII": -0.4750,
                "IIZZ": 0.1750,
                "IZIZ": 0.1201,
                "ZIIZ": 0.1201,
                "ZZII": 0.1629,
                "IXXI": 0.0454,
                "IYYI": 0.0454,
            }.items()
        }
        E_nuc = 0.9953 * scale

    # Build Hamiltonian
    H = np.zeros((dim, dim), dtype=complex)

    # Helper to build tensor products
    pauli_map = {"I": identity, "X": X, "Y": Y, "Z": Z}

    for pauli_string, coeff in coeffs.items():
        term = pauli_map[pauli_string[0]]
        for p in pauli_string[1:]:
            term = np.kron(term, pauli_map[p])
        H += coeff * term

    return H.real, E_nuc


def h2o_hamiltonian(angle: float = 104.5) -> Tuple[np.ndarray, float]:
    """
    Water molecule (H2O) Hamiltonian.

    H2O is more complex with 3 atoms. This uses a minimal basis set.
    Requires 6 qubits for proper representation.

    Args:
        angle: H-O-H bond angle in degrees (default: 104.5° equilibrium)

    Returns:
        (hamiltonian_matrix, nuclear_repulsion_energy)

    Example:
        >>> H, E_nuc = h2o_hamiltonian()
        >>> print(H.shape)
        (64, 64)
    """
    # H2O requires 6 qubits (64x64 matrix)
    n_qubits = 6
    dim = 2**n_qubits

    # Simplified Hamiltonian for demonstration
    # Real H2O would have many more terms

    identity = np.eye(2)
    Z = np.array([[1, 0], [0, -1]])
    X = np.array([[0, 1], [1, 0]])

    # Approximate coefficients for H2O at equilibrium
    if abs(angle - 104.5) < 1.0:
        coeffs = {
            "IIIIII": -75.0137,
            "IIIIIZ": 0.3923,
            "IIIIZI": 0.3923,
            "IIIZII": 0.0116,
            "IIZIII": -1.0636,
            "IZIIII": -1.0636,
            "ZIIIII": -0.4759,
        }
        E_nuc = 9.1876
    else:
        # Very rough scaling
        scale = np.cos(np.radians(angle - 104.5))
        coeffs = {
            k: v * scale
            for k, v in {
                "IIIIII": -75.0137,
                "IIIIIZ": 0.3923,
                "IIIIZI": 0.3923,
                "IIIZII": 0.0116,
                "IIZIII": -1.0636,
                "IZIIII": -1.0636,
                "ZIIIII": -0.4759,
            }.items()
        }
        E_nuc = 9.1876

    # Build Hamiltonian
    H = np.zeros((dim, dim))

    pauli_map = {"I": identity, "X": X, "Z": Z}

    for pauli_string, coeff in coeffs.items():
        term = pauli_map[pauli_string[0]]
        for p in pauli_string[1:]:
            term = np.kron(term, pauli_map[p])
        H += coeff * term

    return H, E_nuc


def beh2_hamiltonian(bond_length: float = 1.33) -> Tuple[np.ndarray, float]:
    """
    Beryllium Hydride (BeH2) Hamiltonian.

    Linear molecule: H-Be-H
    Requires 5 qubits for minimal basis representation.

    Args:
        bond_length: Be-H bond length in Angstroms (default: 1.33 Å)

    Returns:
        (hamiltonian_matrix, nuclear_repulsion_energy)

    Example:
        >>> H, E_nuc = beh2_hamiltonian()
        >>> print(H.shape)
        (32, 32)
    """
    # BeH2 requires 5 qubits (32x32 matrix)
    n_qubits = 5
    dim = 2**n_qubits

    identity = np.eye(2)
    Z = np.array([[1, 0], [0, -1]])
    X = np.array([[0, 1], [1, 0]])
    Y = np.array([[0, -1j], [1j, 0]])

    # Approximate coefficients for BeH2
    if abs(bond_length - 1.33) < 0.01:
        coeffs = {
            "IIIII": -15.5937,
            "IIIIZ": 0.2182,
            "IIIZI": 0.2182,
            "IIZII": -0.3864,
            "IZIII": -0.3864,
            "ZIIII": -0.1125,
            "IIZZZ": 0.1743,
        }
        E_nuc = 3.0314
    else:
        scale = 1.33 / bond_length
        coeffs = {
            k: v * scale
            for k, v in {
                "IIIII": -15.5937,
                "IIIIZ": 0.2182,
                "IIIZI": 0.2182,
                "IIZII": -0.3864,
                "IZIII": -0.3864,
                "ZIIII": -0.1125,
                "IIZZZ": 0.1743,
            }.items()
        }
        E_nuc = 3.0314 * scale

    # Build Hamiltonian
    H = np.zeros((dim, dim), dtype=complex)

    pauli_map = {"I": identity, "X": X, "Y": Y, "Z": Z}

    for pauli_string, coeff in coeffs.items():
        term = pauli_map[pauli_string[0]]
        for p in pauli_string[1:]:
            term = np.kron(term, pauli_map[p])
        H += coeff * term

    return H.real, E_nuc


def get_molecule_hamiltonian(molecule: str, **kwargs) -> Tuple[np.ndarray, float]:
    """
    Factory function to get molecular Hamiltonian by name.

    Args:
        molecule: Molecule name ('H2', 'LiH', 'H2O', 'BeH2')
        **kwargs: Molecule-specific parameters (bond_length, angle, etc.)

    Returns:
        (hamiltonian_matrix, nuclear_repulsion_energy)

    Example:
        >>> H, E_nuc = get_molecule_hamiltonian('H2', bond_length=0.74)
        >>> H_lih, E_nuc_lih = get_molecule_hamiltonian('LiH')
    """
    molecules = {
        "H2": h2_hamiltonian,
        "LIH": lih_hamiltonian,
        "H2O": h2o_hamiltonian,
        "BEH2": beh2_hamiltonian,
    }

    molecule = molecule.upper()
    if molecule not in molecules:
        raise ValueError(
            f"Unknown molecule: {molecule}. Choose from {list(molecules.keys())}"
        )

    return molecules[molecule](**kwargs)


def get_ground_state_energy(molecule: str, **kwargs) -> float:
    """
    Get the exact ground state energy for a molecule (for comparison).

    Args:
        molecule: Molecule name
        **kwargs: Molecule parameters

    Returns:
        Ground state energy (eigenvalue of Hamiltonian + nuclear repulsion)
    """
    H, E_nuc = get_molecule_hamiltonian(molecule, **kwargs)
    eigenvalues = np.linalg.eigvalsh(H)
    E_ground = eigenvalues[0] + E_nuc
    return E_ground


def get_molecule_info(molecule: str) -> Dict[str, any]:
    """
    Get information about a molecule.

    Args:
        molecule: Molecule name

    Returns:
        Dictionary with molecule information
    """
    info = {
        "H2": {
            "name": "Hydrogen",
            "formula": "H2",
            "n_qubits": 2,
            "n_electrons": 2,
            "basis": "STO-3G",
            "default_bond_length": 0.735,
            "unit": "Angstrom",
        },
        "LIH": {
            "name": "Lithium Hydride",
            "formula": "LiH",
            "n_qubits": 4,
            "n_electrons": 4,
            "basis": "STO-3G",
            "default_bond_length": 1.546,
            "unit": "Angstrom",
        },
        "H2O": {
            "name": "Water",
            "formula": "H2O",
            "n_qubits": 6,
            "n_electrons": 10,
            "basis": "Minimal",
            "default_angle": 104.5,
            "unit": "degrees",
        },
        "BEH2": {
            "name": "Beryllium Hydride",
            "formula": "BeH2",
            "n_qubits": 5,
            "n_electrons": 6,
            "basis": "STO-3G",
            "default_bond_length": 1.33,
            "unit": "Angstrom",
        },
    }

    molecule = molecule.upper()
    if molecule not in info:
        raise ValueError(f"Unknown molecule: {molecule}")

    return info[molecule]
