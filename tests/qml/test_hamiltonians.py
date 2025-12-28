"""
Tests for advanced molecular Hamiltonians
"""

import pytest
import numpy as np
from quantum_debugger.qml.hamiltonians.molecular import (
    h2_hamiltonian,
    lih_hamiltonian,
    h2o_hamiltonian,
    beh2_hamiltonian,
    get_molecule_hamiltonian,
    get_ground_state_energy,
    get_molecule_info,
)


class TestH2Hamiltonian:
    """Test H2 Hamiltonian (already exists, just verify)"""
    
    def test_h2_default(self):
        """Test H2 at equilibrium"""
        H, E_nuc = h2_hamiltonian()
        
        assert H.shape == (4, 4)
        assert isinstance(E_nuc, float)
        assert E_nuc > 0  # Nuclear repulsion is positive
    
    def test_h2_hermitian(self):
        """H2 Hamiltonian should be Hermitian"""
        H, _ = h2_hamiltonian()
        
        np.testing.assert_array_almost_equal(H, H.T)
    
    def test_h2_different_bond_length(self):
        """Test with different bond length"""
        H1, E1 = h2_hamiltonian(0.5)
        H2, E2 = h2_hamiltonian(1.0)
        
        # Different bond lengths should give different energies
        assert not np.allclose(H1, H2)
        assert E1 != E2


class TestLiHHamiltonian:
    """Test Lithium Hydride Hamiltonian"""
    
    def test_lih_shape(self):
        """Test LiH matrix dimensions"""
        H, E_nuc = lih_hamiltonian()
        
        assert H.shape == (16, 16)  # 4 qubits = 16x16
        assert isinstance(E_nuc, float)
    
    def test_lih_hermitian(self):
        """LiH Hamiltonian should be Hermitian"""
        H, _ = lih_hamiltonian()
        
        np.testing.assert_array_almost_equal(H, H.T)
    
    def test_lih_real(self):
        """LiH Hamiltonian should be real"""
        H, _ = lih_hamiltonian()
        
        assert np.all(np.abs(np.imag(H)) < 1e-10)
    
    def test_lih_ground_state(self):
        """Test LiH has valid ground state"""
        H, E_nuc = lih_hamiltonian()
        
        eigenvalues = np.linalg.eigvalsh(H)
        E_ground = eigenvalues[0] + E_nuc
        
        # Ground state should be negative (bound state)
        assert E_ground < 0
    
    def test_lih_bond_length_variation(self):
        """Test with different bond lengths"""
        H1, _ = lih_hamiltonian(1.3)
        H2, _ = lih_hamiltonian(1.8)
        
        assert not np.allclose(H1, H2)


class TestH2OHamiltonian:
    """Test Water Hamiltonian"""
    
    def test_h2o_shape(self):
        """Test H2O matrix dimensions"""
        H, E_nuc = h2o_hamiltonian()
        
        assert H.shape == (64, 64)  # 6 qubits = 64x64
        assert isinstance(E_nuc, float)
    
    def test_h2o_hermitian(self):
        """H2O Hamiltonian should be Hermitian"""
        H, _ = h2o_hamiltonian()
        
        np.testing.assert_array_almost_equal(H, H.T)
    
    def test_h2o_real(self):
        """H2O Hamiltonian should be real"""
        H, _ = h2o_hamiltonian()
        
        assert np.all(np.abs(np.imag(H)) < 1e-10)
    
    def test_h2o_ground_state(self):
        """Test H2O has valid ground state"""
        H, E_nuc = h2o_hamiltonian()
        
        eigenvalues = np.linalg.eigvalsh(H)
        E_ground = eigenvalues[0] + E_nuc
        
        # Ground state should be very negative
        assert E_ground < -60
    
    def test_h2o_angle_variation(self):
        """Test with different angles"""
        H1, _ = h2o_hamiltonian(100)
        H2, _ = h2o_hamiltonian(110)
        
        assert not np.allclose(H1, H2)


class TestBeH2Hamiltonian:
    """Test Beryllium Hydride Hamiltonian"""
    
    def test_beh2_shape(self):
        """Test BeH2 matrix dimensions"""
        H, E_nuc = beh2_hamiltonian()
        
        assert H.shape == (32, 32)  # 5 qubits = 32x32
        assert isinstance(E_nuc, float)
    
    def test_beh2_hermitian(self):
        """BeH2 Hamiltonian should be Hermitian"""
        H, _ = beh2_hamiltonian()
        
        np.testing.assert_array_almost_equal(H, H.T)
    
    def test_beh2_real(self):
        """BeH2 Hamiltonian should be real"""
        H, _ = beh2_hamiltonian()
        
        assert np.all(np.abs(np.imag(H)) < 1e-10)
    
    def test_beh2_ground_state(self):
        """Test BeH2 has valid ground state"""
        H, E_nuc = beh2_hamiltonian()
        
        eigenvalues = np.linalg.eigvalsh(H)
        E_ground = eigenvalues[0] + E_nuc
        
        # Ground state should be negative
        assert E_ground < 0
    
    def test_beh2_bond_length_variation(self):
        """Test with different bond lengths"""
        H1, _ = beh2_hamiltonian(1.2)
        H2, _ = beh2_hamiltonian(1.5)
        
        assert not np.allclose(H1, H2)


class TestFactoryFunctions:
    """Test factory and utility functions"""
    
    def test_get_molecule_hamiltonian_h2(self):
        """Test factory for H2"""
        H, E_nuc = get_molecule_hamiltonian('H2')
        
        assert H.shape == (4, 4)
    
    def test_get_molecule_hamiltonian_lih(self):
        """Test factory for LiH"""
        H, E_nuc = get_molecule_hamiltonian('LiH', bond_length=1.5)
        
        assert H.shape == (16, 16)
    
    def test_get_molecule_hamiltonian_h2o(self):
        """Test factory for H2O"""
        H, E_nuc = get_molecule_hamiltonian('H2O')
        
        assert H.shape == (64, 64)
    
    def test_get_molecule_hamiltonian_beh2(self):
        """Test factory for BeH2"""
        H, E_nuc = get_molecule_hamiltonian('BeH2')
        
        assert H.shape == (32, 32)
    
    def test_get_molecule_hamiltonian_case_insensitive(self):
        """Test case insensitivity"""
        H1, _ = get_molecule_hamiltonian('h2')
        H2, _ = get_molecule_hamiltonian('H2')
        
        np.testing.assert_array_equal(H1, H2)
    
    def test_get_molecule_hamiltonian_invalid(self):
        """Test error for invalid molecule"""
        with pytest.raises(ValueError, match="Unknown molecule"):
            get_molecule_hamiltonian('CH4')
    
    def test_get_ground_state_energy_h2(self):
        """Test ground state energy calculation for H2"""
        E_ground = get_ground_state_energy('H2')
        
        assert isinstance(E_ground, float)
        assert E_ground < 0  # Bound state
    
    def test_get_ground_state_energy_comparison(self):
        """Test that different molecules have different energies"""
        E_h2 = get_ground_state_energy('H2')
        E_lih = get_ground_state_energy('LiH')
        E_h2o = get_ground_state_energy('H2O')
        
        # All different
        assert E_h2 != E_lih
        assert E_lih != E_h2o
        
        # H2O should have lowest (most negative) energy
        assert E_h2o < E_lih < E_h2
    
    def test_get_molecule_info_h2(self):
        """Test molecule info for H2"""
        info = get_molecule_info('H2')
        
        assert info['name'] == 'Hydrogen'
        assert info['n_qubits'] == 2
        assert info['n_electrons'] == 2
    
    def test_get_molecule_info_lih(self):
        """Test molecule info for LiH"""
        info = get_molecule_info('LiH')
        
        assert info['name'] == 'Lithium Hydride'
        assert info['n_qubits'] == 4
        assert info['formula'] == 'LiH'
    
    def test_get_molecule_info_h2o(self):
        """Test molecule info for H2O"""
        info = get_molecule_info('H2O')
        
        assert info['name'] == 'Water'
        assert info['n_qubits'] == 6
        assert 'default_angle' in info
    
    def test_get_molecule_info_beh2(self):
        """Test molecule info for BeH2"""
        info = get_molecule_info('BeH2')
        
        assert info['formula'] == 'BeH2'
        assert info['n_qubits'] == 5
    
    def test_get_molecule_info_invalid(self):
        """Test error for invalid molecule"""
        with pytest.raises(ValueError, match="Unknown molecule"):
            get_molecule_info('Invalid')


class TestQubitRequirements:
    """Test qubit requirements for molecules"""
    
    def test_qubit_scaling(self):
        """Test that molecules need different numbers of qubits"""
        molecules = {
            'H2': 2,
            'LiH': 4,
            'BeH2': 5,
            'H2O': 6,
        }
        
        for mol, expected_qubits in molecules.items():
            H, _ = get_molecule_hamiltonian(mol)
            actual_qubits = int(np.log2(H.shape[0]))
            assert actual_qubits == expected_qubits


class TestNumericalProperties:
    """Test numerical properties of Hamiltonians"""
    
    def test_all_hamiltonians_hermitian(self):
        """All Hamiltonians should be Hermitian"""
        for mol in ['H2', 'LiH', 'H2O', 'BeH2']:
            H, _ = get_molecule_hamiltonian(mol)
            np.testing.assert_array_almost_equal(
                H, H.conj().T,
                err_msg=f"{mol} Hamiltonian is not Hermitian"
            )
    
    def test_all_hamiltonians_real(self):
        """All Hamiltonians should be real"""
        for mol in ['H2', 'LiH', 'H2O', 'BeH2']:
            H, _ = get_molecule_hamiltonian(mol)
            assert np.all(np.abs(np.imag(H)) < 1e-10), f"{mol} has imaginary components"
    
    def test_eigenvalue_ordering(self):
        """Eigenvalues should be sorted (lowest first)"""
        for mol in ['H2', 'LiH', 'H2O', 'BeH2']:
            H, _ = get_molecule_hamiltonian(mol)
            eigenvalues = np.linalg.eigvalsh(H)
            
            # Should be sorted ascending
            assert np.all(eigenvalues[:-1] <= eigenvalues[1:])
