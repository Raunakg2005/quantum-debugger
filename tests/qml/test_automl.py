"""
Tests for AutoML functionality
"""

import pytest
import numpy as np

from quantum_debugger.qml.automl import (
    auto_qnn,
    AutoQNN,
    select_best_ansatz,
    tune_hyperparameters,
    quantum_nas
)


class TestAutoQNN:
    """Test automatic QNN"""
    
    def test_auto_qnn_simple(self):
        """Test simple auto_qnn interface"""
        # Generate simple data
        X = np.random.randn(30, 2)
        y = np.random.randint(0, 2, 30)
        
        # Auto QNN should work with one line!
        model = auto_qnn(X, y, max_qubits=2, time_budget=10)
        
        assert model is not None
        predictions = model.predict(X[:5])
        assert predictions.shape[0] == 5
    
    def test_autoqnn_class(self):
        """Test AutoQNN class"""
        X = np.random.randn(20, 2)
        y = np.random.randint(0, 2, 20)
        
        auto = AutoQNN(max_qubits=2, time_budget=10, n_trials=3)
        auto.fit(X, y)
        
        assert auto.best_model_ is not None
        assert auto.best_score_ >= 0
        assert auto.best_config_ is not None
        
        # Can predict
        predictions = auto.predict(X)
        assert len(predictions) == len(X)
        
        # Can score
        score = auto.score(X, y)
        assert 0 <= score <= 1
    
    def test_get_search_summary(self):
        """Test getting search summary"""
        X = np.random.randn(20, 2)
        y = np.random.randint(0, 2, 20)
        
        auto = AutoQNN(max_qubits=2, n_trials=2)
        auto.fit(X, y)
        
        summary = auto.get_search_summary()
        
        assert 'best_score' in summary
        assert 'best_config' in summary
        assert 'n_trials' in summary


class TestAnsatzSelector:
    """Test ansatz selection"""
    
    def test_select_best_ansatz(self):
        """Test ansatz selection"""
        X = np.random.randn(20, 2)
        y = np.random.randint(0, 2, 20)
        
        ansatz = select_best_ansatz(X, y, n_qubits=2, quick=True)
        
        assert ansatz is not None
        assert isinstance(ansatz, str)


class TestHyperparameterTuner:
    """Test hyperparameter tuning"""
    
    def test_tune_hyperparameters(self):
        """Test hyperparameter tuning"""
        X = np.random.randn(20, 2)
        y = np.random.randint(0, 2, 20)
        
        params = tune_hyperparameters(X, y, n_qubits=2, n_trials=3)
        
        assert 'learning_rate' in params
        assert 'epochs' in params
        assert params['learning_rate'] > 0


class TestQuantumNAS:
    """Test neural architecture search"""
    
    def test_quantum_nas(self):
        """Test architecture search"""
        X = np.random.randn(20, 2)
        y = np.random.randint(0, 2, 20)
        
        arch = quantum_nas(X, y, max_qubits=2, quick=True)
        
        assert 'n_qubits' in arch
        assert 'n_layers' in arch
        assert arch['n_qubits'] >= 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
