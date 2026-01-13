"""
Tests for quantum kernels and QSVM
"""

import pytest
import numpy as np
from quantum_debugger.qml.kernels import (
    QuantumKernel,
    FidelityKernel,
    ProjectedKernel,
    QuantumSVM,
    train_qsvm,
    kernel_target_alignment,
    optimize_feature_map,
    evaluate_kernel_quality
)


class TestFidelityKernel:
    """Test fidelity-based quantum kernel"""
    
    def test_initialization(self):
        kernel = FidelityKernel(n_qubits=4, feature_map='zz', reps=2)
        
        assert kernel.n_qubits == 4
        assert kernel.feature_map == 'zz'
        assert kernel.reps == 2
    
    def test_encode_data(self):
        kernel = FidelityKernel(n_qubits=3, feature_map='angle')
        x = np.array([1.0, 2.0, 3.0])
        
        encoded = kernel.encode_data(x)
        
        assert len(encoded) == 3
        assert np.allclose(encoded, x)
    
    def test_kernel_element(self):
        kernel = FidelityKernel(n_qubits=2, feature_map='angle')
        x1 = np.array([0.5, 1.0])
        x2 = np.array([0.5, 1.0])
        
        k_val = kernel.compute_kernel_element(x1, x2)
        
        # Same points should have kernel ~1
        assert 0.9 < k_val <= 1.0
    
    def test_kernel_element_different_points(self):
        kernel = FidelityKernel(n_qubits=2)
        x1 = np.array([0.0, 0.0])
        x2 = np.array([1.0, 1.0])
        
        k_val = kernel.compute_kernel_element(x1, x2)
        
        # Different points should have kernel < 1
        assert 0 <= k_val < 1.0
    
    def test_kernel_matrix_symmetric(self):
        kernel = FidelityKernel(n_qubits=2)
        X = np.random.rand(5, 2)
        
        K = kernel.compute_kernel_matrix(X, X)
        
        # Should be symmetric
        assert np.allclose(K, K.T)
        assert K.shape == (5, 5)
    
    def test_kernel_matrix_diagonal_ones(self):
        kernel = FidelityKernel(n_qubits=2)
        X = np.random.rand(5, 2)
        
        K = kernel.compute_kernel_matrix(X, X)
        
        # Diagonal should be close to 1 (self-similarity)
        diag = np.diag(K)
        assert np.all(diag >= 0.9)
    
    def test_kernel_cache(self):
        kernel = FidelityKernel(n_qubits=2)
        x1 = np.array([0.5, 1.0])
        x2 = np.array([1.0, 0.5])
        
        # Compute kernel matrix which should populate cache
        X = np.array([x1, x2])
        K = kernel.compute_kernel_matrix(X, X)
        
        # Cache should now be populated
        assert len(kernel._kernel_cache) > 0
        
        # Clear cache
        kernel.clear_cache()
        assert len(kernel._kernel_cache) == 0


class TestProjectedKernel:
    """Test projected quantum kernel"""
    
    def test_initialization(self):
        kernel = ProjectedKernel(n_qubits=3, measurement_basis='z')
        
        assert kernel.n_qubits == 3
        assert kernel.measurement_basis == 'z'
    
    def test_kernel_element(self):
        kernel = ProjectedKernel(n_qubits=2)
        x1 = np.array([0.5, 1.0])
        x2 = np.array([0.6, 1.1])
        
        k_val = kernel.compute_kernel_element(x1, x2)
        
        # Should be a valid kernel value
        assert -1 <= k_val <= 1


class TestQuantumSVM:
    """Test Quantum SVM"""
    
    def test_initialization(self):
        qsvm = QuantumSVM(n_qubits=4, feature_map='zz', C=1.0)
        
        assert qsvm.n_qubits == 4
        assert qsvm.feature_map == 'zz'
        assert qsvm.C == 1.0
    
    def test_fit_simple_dataset(self):
        # Simple linearly separable dataset
        X_train = np.array([
            [0, 0],
            [0, 1],
            [1, 0],
            [1, 1]
        ])
        y_train = np.array([0, 1, 1, 0])  # XOR-like
        
        qsvm = QuantumSVM(n_qubits=2, feature_map='angle')
        qsvm.fit(X_train, y_train)
        
        assert qsvm.X_train is not None
        assert qsvm.K_train is not None
        assert qsvm.K_train.shape == (4, 4)
    
    def test_predict(self):
        X_train = np.array([[0, 0], [1, 1], [0, 1], [1, 0]])
        y_train = np.array([0, 0, 1, 1])
        
        qsvm = QuantumSVM(n_qubits=2)
        qsvm.fit(X_train, y_train)
        
        X_test = np.array([[0, 0], [1, 1]])
        predictions = qsvm.predict(X_test)
        
        assert len(predictions) == 2
        assert all(p in [0, 1] for p in predictions)
    
    def test_score(self):
        X = np.array([[0, 0], [1, 1], [0, 1], [1, 0]])
        y = np.array([0, 0, 1, 1])
        
        qsvm = QuantumSVM(n_qubits=2)
        qsvm.fit(X, y)
        
        accuracy = qsvm.score(X, y)
        
        # Should achieve some accuracy
        assert 0 <= accuracy <= 1.0
    
    def test_get_support_vectors(self):
        X = np.array([[0, 0], [1, 1], [0, 1], [1, 0]])
        y = np.array([0, 0, 1, 1])
        
        qsvm = QuantumSVM(n_qubits=2)
        qsvm.fit(X, y)
        
        support_vectors = qsvm.get_support_vectors()
        
        assert len(support_vectors) > 0
        assert len(support_vectors) <= len(X)


class TestKernelAlignment:
    """Test kernel alignment methods"""
    
    def test_kernel_target_alignment(self):
        # Perfect alignment case
        K = np.array([[1, 0], [0, 1]])
        y = np.array([0, 1])
        
        alignment = kernel_target_alignment(K, y)
        
        assert 0 <= alignment <= 1.0
    
    def test_alignment_symmetric_labels(self):
        K = np.array([
            [1, 0.5, 0],
            [0.5, 1, 0],
            [0, 0, 1]
        ])
        y = np.array([0, 0, 1])
        
        alignment = kernel_target_alignment(K, y)
        
        # Should be positive for this case
        assert alignment > 0
    
    def test_evaluate_kernel_quality(self):
        K = np.array([
            [1, 0.5, 0.1],
            [0.5, 1, 0.2],
            [0.1, 0.2, 1]
        ])
        y = np.array([0, 0, 1])
        
        metrics = evaluate_kernel_quality(K, y)
        
        assert 'alignment' in metrics
        assert 'centered_alignment' in metrics
        assert 'condition_number' in metrics
        assert 'rank' in metrics
        assert 'trace' in metrics


class TestTrainQSVM:
    """Test QSVM training convenience function"""
    
    def test_train_qsvm_basic(self):
        X_train = np.random.rand(10, 2)
        y_train = np.random.randint(0, 2, 10)
        
        result = train_qsvm(
            X_train, y_train,
            n_qubits=2,
            feature_map='angle'
        )
        
        assert 'model' in result
        assert 'train_accuracy' in result
        assert isinstance(result['model'], QuantumSVM)
    
    def test_train_qsvm_with_test(self):
        X_train = np.random.rand(10, 2)
        y_train = np.random.randint(0, 2, 10)
        X_test = np.random.rand(5, 2)
        y_test = np.random.randint(0, 2, 5)
        
        result = train_qsvm(
            X_train, y_train,
            X_test, y_test,
            n_qubits=2
        )
        
        assert 'test_accuracy' in result
        assert 'predictions' in result
        assert len(result['predictions']) == 5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
