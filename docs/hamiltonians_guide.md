# Molecular Hamiltonians Guide

## Overview

The molecular Hamiltonians module provides quantum chemistry Hamiltonians for small molecules, enabling Variational Quantum Eigensolver (VQE) calculations of molecular ground state energies.

## Supported Molecules

### Hydrogen (H₂)

The simplest diatomic molecule, commonly used for benchmarking.

**Specifications:**
- Number of qubits: 2
- Number of electrons: 2  
- Basis set: STO-3G
- Default bond length: 0.735 Å (equilibrium)

**Usage:**
```python
from quantum_debugger.qml.hamiltonians.molecular import h2_hamiltonian

# At equilibrium geometry
H, E_nuc = h2_hamiltonian(bond_length=0.735)

# At different bond length
H_stretched, E_nuc_stretched = h2_hamiltonian(bond_length=1.0)
```

**Matrix Dimensions:** 4 × 4 (2² for 2 qubits)

**Expected Ground State Energy:** -1.137 Hartree (at 0.735 Å)

---

### Lithium Hydride (LiH)

An alkali metal hydride with ionic bonding character.

**Specifications:**
- Number of qubits: 4
- Number of electrons: 4
- Basis set: STO-3G
- Default bond length: 1.546 Å

**Usage:**
```python
from quantum_debugger.qml.hamiltonians.molecular import lih_hamiltonian

H, E_nuc = lih_hamiltonian(bond_length=1.546)
```

**Matrix Dimensions:** 16 × 16 (2⁴ for 4 qubits)

**Expected Ground State Energy:** -7.882 Hartree

---

### Water (H₂O)

A bent triatomic molecule with important chemical properties.

**Specifications:**
- Number of qubits: 6
- Number of electrons: 10
- Basis set: Minimal basis
- Default H-O-H angle: 104.5°

**Usage:**
```python
from quantum_debugger.qml.hamiltonians.molecular import h2o_hamiltonian

# At equilibrium geometry
H, E_nuc = h2o_hamiltonian(angle=104.5)

# At different angle
H_bent, E_nuc_bent = h2o_hamiltonian(angle=110.0)
```

**Matrix Dimensions:** 64 × 64 (2⁶ for 6 qubits)

**Expected Ground State Energy:** -75.0 Hartree

---

### Beryllium Hydride (BeH₂)

A linear triatomic molecule.

**Specifications:**
- Number of qubits: 5
- Number of electrons: 6
- Basis set: STO-3G
- Default Be-H bond length: 1.33 Å

**Usage:**
```python
from quantum_debugger.qml.hamiltonians.molecular import beh2_hamiltonian

H, E_nuc = beh2_hamiltonian(bond_length=1.33)
```

**Matrix Dimensions:** 32 × 32 (2⁵ for 5 qubits)

**Expected Ground State Energy:** -15.59 Hartree

---

## Factory Function

Simplified access to all molecules:

```python
from quantum_debugger.qml.hamiltonians.molecular import get_molecule_hamiltonian

# Get any molecule by name
H_h2, E_nuc_h2 = get_molecule_hamiltonian('H2', bond_length=0.74)
H_lih, E_nuc_lih = get_molecule_hamiltonian('LiH')
H_h2o, E_nuc_h2o = get_molecule_hamiltonian('H2O', angle=105.0)
H_beh2, E_nuc_beh2 = get_molecule_hamiltonian('BeH2')
```

**Case Insensitive:** 'h2', 'H2', 'LiH', 'lih' all work

---

## Ground State Calculation

Calculate exact ground state energy for comparison with VQE results:

```python
from quantum_debugger.qml.hamiltonians.molecular import get_ground_state_energy

# Get exact ground state (eigenvalue + nuclear repulsion)
E_exact = get_ground_state_energy('H2')
E_exact_lih = get_ground_state_energy('LiH', bond_length=1.5)

print(f"H2 exact energy: {E_exact:.6f} Hartree")
```

---

## Molecule Information Database

Access molecular properties:

```python
from quantum_debugger.qml.hamiltonians.molecular import get_molecule_info

info = get_molecule_info('H2O')

print(f"Name: {info['name']}")
print(f"Formula: {info['formula']}")
print(f"Qubits needed: {info['n_qubits']}")
print(f"Number of electrons: {info['n_electrons']}")
print(f"Basis set: {info['basis']}")
```

**Output:**
```
Name: Water
Formula: H2O
Qubits needed: 6
Number of electrons: 10
Basis set: Minimal
```

---

## Integration with VQE

Complete workflow for molecular ground state calculation:

```python
from quantum_debugger.qml.algorithms import VQE
from quantum_debugger.qml.ansatz import excitation_preserving
from quantum_debugger.qml.hamiltonians.molecular import (
    get_molecule_hamiltonian,
    get_ground_state_energy
)
import numpy as np

# 1. Get Hamiltonian
H, E_nuc = get_molecule_hamiltonian('LiH', bond_length=1.546)

# 2. Get exact ground state for comparison
E_exact = get_ground_state_energy('LiH')

# 3. Create ansatz (4 qubits for LiH)
ansatz = excitation_preserving(num_qubits=4, reps=2)

# 4. Initialize parameters
initial_params = np.random.uniform(0, 2*np.pi, ansatz.num_parameters)

# 5. Run VQE
vqe = VQE(
    hamiltonian=H,
    ansatz=ansatz,
    optimizer='adam',
    learning_rate=0.01,
    max_iterations=100
)

result = vqe.run(initial_params)

# 6. Compare results
E_vqe = result['energy'] + E_nuc
error = abs(E_vqe - E_exact)

print(f"VQE energy: {E_vqe:.6f} Hartree")
print(f"Exact energy: {E_exact:.6f} Hartree")
print(f"Error: {error:.6f} Hartree")
```

---

## Hamiltonian Structure

### Qubit Encoding

Hamiltonians are expressed as sums of Pauli operators:

```
H = Σᵢ cᵢ Pᵢ
```

Where:
- `cᵢ` are real-valued coefficients
- `Pᵢ` are tensor products of Pauli matrices (I, X, Y, Z)

**Example for H₂:**
```
H = c₀·I⊗I + c₁·I⊗Z + c₂·Z⊗I + c₃·Z⊗Z + c₄·X⊗X
```

### Matrix Properties

All Hamiltonians satisfy:

1. **Hermitian:** H = H†
2. **Real:** All matrix elements are real
3. **Sparse:** Most elements are zero

---

## Bond Dissociation Curves

Calculate energy as a function of geometry:

```python
import numpy as np
import matplotlib.pyplot as plt

bond_lengths = np.linspace(0.5, 2.0, 20)
energies = []

for r in bond_lengths:
    E = get_ground_state_energy('H2', bond_length=r)
    energies.append(E)

plt.plot(bond_lengths, energies)
plt.xlabel('Bond Length (Å)')
plt.ylabel('Energy (Hartree)')
plt.title('H₂ Potential Energy Curve')
plt.show()
```

---

## Basis Sets

### STO-3G (Slater-Type Orbital with 3 Gaussians)

Used for H₂, LiH, BeH₂:
- Minimal basis: one basis function per atomic orbital
- Computationally efficient
- Suitable for proof-of-concept calculations

### Minimal Basis

Used for H₂O:
- Simplified representation
- Reduced number of qubits
- Educational purposes

---

## Numerical Accuracy

### Precision Considerations

Hamiltonian coefficients are stored as floating-point numbers:
- Precision: ~10⁻¹⁵ (double precision)
- Eigenvalue accuracy: ~10⁻¹⁰ Hartree

### Verification

Check Hamiltonian properties:

```python
import numpy as np

H, _ = get_molecule_hamiltonian('H2')

# Verify Hermitian
is_hermitian = np.allclose(H, H.conj().T)
print(f"Hermitian: {is_hermitian}")

# Verify real
is_real = np.allclose(H.imag, 0)
print(f"Real: {is_real}")

# Check eigenvalues
eigenvalues = np.linalg.eigvalsh(H)
print(f"Lowest eigenvalue: {eigenvalues[0]:.6f}")
```

---

## API Reference

### Hamiltonian Functions

```python
h2_hamiltonian(bond_length: float = 0.735) -> Tuple[np.ndarray, float]
lih_hamiltonian(bond_length: float = 1.546) -> Tuple[np.ndarray, float]
h2o_hamiltonian(angle: float = 104.5) -> Tuple[np.ndarray, float]
beh2_hamiltonian(bond_length: float = 1.33) -> Tuple[np.ndarray, float]
```

**Returns:** (Hamiltonian matrix, nuclear repulsion energy)

### Utility Functions

```python
get_molecule_hamiltonian(molecule: str, **kwargs) -> Tuple[np.ndarray, float]
get_ground_state_energy(molecule: str, **kwargs) -> float
get_molecule_info(molecule: str) -> Dict[str, Any]
```

---

## Testing

Run Hamiltonian tests:

```bash
pytest tests/qml/test_hamiltonians.py -v
```

Expected: 55 tests passing

---

## Performance Characteristics

### Matrix Size

| Molecule | Qubits | Matrix Size | Memory |
|----------|--------|-------------|--------|
| H₂       | 2      | 4 × 4       | 128 bytes |
| LiH      | 4      | 16 × 16     | 2 KB |
| BeH₂     | 5      | 32 × 32     | 8 KB |
| H₂O      | 6      | 64 × 64     | 32 KB |

### Computational Cost

- Eigenvalue calculation: O(n³) where n = 2^(qubits)
- Matrix-vector multiplication: O(n²)

---

## Limitations

1. **Small molecules only:** Current implementation limited to 2-6 qubits
2. **Minimal basis sets:** Not chemically accurate
3. **Fixed geometries:** Limited geometry optimization support
4. **No excited states:** Only ground state calculations

---

## References

1. Seeley, Richard & Love, "The Bravyi-Kitaev transformation" (2012)
2. Cao et al., "Quantum chemistry in the age of quantum computing" (2019)
3. McArdle et al., "Quantum computational chemistry" (2020)
