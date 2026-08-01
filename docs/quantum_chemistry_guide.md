# Quantum chemistry & electronic structure

Everything needed to map a molecule onto qubits and find its energy: fermion-to-qubit encodings
(Jordan-Wigner, parity, Bravyi-Kitaev), molecular Hamiltonians, Hartree-Fock and full
configuration interaction, chemistry ansätze (UCCSD, Givens rotations), qubit tapering by Z2
symmetries, excited states, imaginary-time and Krylov ground-state solvers, reduced density
matrices, and a truncated Fock space. Every routine is checked against exact diagonalization or
the canonical anticommutation relations.

All functions live under `quantum_debugger.algorithms.<module>`.

## Fermion-to-qubit mappings

The mappings differ in the Pauli weight (locality) of the resulting operators — Bravyi-Kitaev is
logarithmic where Jordan-Wigner is linear.

- `jordan_wigner.jw_annihilation(mode, n_modes)`, `jw_creation(...)`, `jw_number(...)`,
  `anticommutation_error(n_modes)` (checks `{a_i, a_j†} = δ_ij`).
- `fermion_mappings.jordan_wigner_annihilation(j, n)`, `parity_annihilation(...)`,
  `bravyi_kitaev_annihilation(...)`, `pauli_weight(operator)`, `satisfies_car(annihilators)`.

```python
from quantum_debugger.algorithms.jordan_wigner import anticommutation_error
from quantum_debugger.algorithms.fermion_mappings import (
    pauli_weight, jordan_wigner_annihilation, bravyi_kitaev_annihilation)
anticommutation_error(3)                          # -> 0.0   (CAR satisfied exactly)
pauli_weight(jordan_wigner_annihilation(3, 4))    # -> 4
pauli_weight(bravyi_kitaev_annihilation(3, 4))    # -> 3     (BK is more local)
```

## Molecular Hamiltonians, Hartree-Fock & FCI

- `molecular_hamiltonian.molecular_hamiltonian(one_body, two_body, mapping)`,
  `hartree_fock_energy(one_body, two_body, n_electrons)`,
  `fci_energy(hamiltonian, n_electrons, ...)`, `hubbard_dimer_hamiltonian(t, U)`,
  `number_operator(n, mapping)`.

```python
from quantum_debugger.algorithms.molecular_hamiltonian import hubbard_dimer_hamiltonian, fci_energy
H = hubbard_dimer_hamiltonian(t=1.0, U=4.0)
round(fci_energy(H, n_electrons=2), 4)    # -> -0.8284   (matches the exact dimer ground state)
```

## Ansätze, tapering & excited states

- `chemistry_ansatze.hartree_fock_state(...)`, `uccsd_operator(singles, doubles, n)`,
  `givens_rotation(theta, p, q, n)`, `conserves_particle_number(op, n)`.
- `qubit_tapering.z2_symmetry_generators(H)`, `taper_energy(H, label, sign)`,
  `spectrum_is_union_of_sectors(H, label)` — tapering that provably loses nothing.
- `excited_states.excited_spectrum_by_deflation(H, k, beta)`, `ssvqe_cost(...)`,
  `folded_spectrum_operator(H, omega)`, `subspace_energies(H, basis)`.

## Ground-state solvers & reduced density matrices

- `vqe_solver.variational_ground_state(terms, ...)`, `tfim_hamiltonian(n)`,
  `heisenberg_hamiltonian(n)`.
- `imaginary_time.imaginary_time_evolution(hamiltonian, ...)`,
  `krylov.krylov_ground_energy(hamiltonian, dim)`, `krylov_spectrum(...)`.
- `rdm.one_particle_rdm(state)`, `two_particle_rdm(state)`, `natural_orbital_occupations(state)`,
  `energy_from_rdm(rdm1, rdm2, one_body, two_body)`.
- `fock_space.creation_operator(cutoff)`, `annihilation_operator(...)`,
  `coherent_state_fock(alpha, cutoff)`, `displacement_operator(...)`, `squeeze_operator(...)`.

## What this is verified against

- Mappings: the exact canonical anticommutation relations and analytic Pauli weights.
- Molecular energies: exact diagonalization (FCI) and the exactly-solvable Hubbard dimer.
- Tapering: the tapered spectrum equals the exact symmetry-sector spectrum.
- Imaginary-time / Krylov: convergence to the exact ground energy.
