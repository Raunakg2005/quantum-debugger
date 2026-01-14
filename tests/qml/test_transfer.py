"""
Tests for transfer learning module
"""

import pytest
import numpy as np
import tempfile
import os
from pathlib import Path

from quantum_debugger.qml.transfer import (
    PretrainedQNN,
    save_model,
    load_model,
    list_models,
    get_model_info,
    MODEL_REGISTRY
)


class TestPretrainedQNN:
    """Test PretrainedQNN class"""
    
    def test_initialization(self):
        """Test PretrainedQNN can be initialized"""
        config = {'n_qubits': 4, 'n_layers': 2, 'ansatz_type': 'real_amplitudes'}
        weights = np.random.rand(8)
        metadata = {'dataset': 'test', 'accuracy': 0.95}
        
        model = PretrainedQNN(
            model_name='test_model',
            config=config,
            weights=weights,
            metadata=metadata
        )
        
        assert model.model_name == 'test_model'
        assert model.n_qubits == 4
        assert model.n_layers == 2
        assert len(model.weights) == 8
    
    def test_predict(self):
        """Test prediction works"""
        config = {'n_qubits': 2, 'n_layers': 1}
        weights = np.random.rand(4)
        
        model = PretrainedQNN('test', config, weights)
        
        X = np.random.rand(5, 4)
        predictions = model.predict(X)
        
        assert len(predictions) == 5
        assert all(p in [0, 1] for p in predictions)
    
    def test_score(self):
        """Test scoring works"""
        config = {'n_qubits': 2, 'n_layers': 1}
        weights = np.random.rand(4)
        
        model = PretrainedQNN('test', config, weights)
        
        X = np.random.rand(10, 4)
        y = np.random.randint(0, 2, 10)
        
        score = model.score(X, y)
        
        assert 0 <= score <= 1.0
    
    def test_get_info(self):
        """Test get_info returns correct information"""
        config = {'n_qubits': 4, 'n_layers': 2}
        weights = np.random.rand(8)
        metadata = {'dataset': 'MNIST', 'accuracy': 0.98}
        
        model = PretrainedQNN('mnist_test', config, weights, metadata)
        info = model.get_info()
        
        assert info['model_name'] == 'mnist_test'
        assert info['n_qubits'] == 4
        assert info['dataset'] == 'MNIST'
        assert info['accuracy'] == 0.98


class TestSerialization:
    """Test model save/load functionality"""
    
    def test_save_load_pickle(self):
        """Test pickle format save/load"""
        config = {'n_qubits': 4, 'n_layers': 2}
        weights = np.random.rand(8)
        metadata = {'dataset': 'test', 'accuracy': 0.95}
        
        model = PretrainedQNN('test_model', config, weights, metadata)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as f:
            temp_path = f.name
        
        try:
            # Save
            save_model(model, temp_path, format='pickle')
            assert os.path.exists(temp_path)
            
            # Load
            loaded = load_model(temp_path, format='pickle')
            
            assert loaded.model_name == model.model_name
            assert np.allclose(loaded.weights, model.weights)
            assert loaded.metadata == model.metadata
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_save_load_json(self):
        """Test JSON format save/load"""
        config = {'n_qubits': 2, 'n_layers': 1}
        weights = np.array([0.5, 0.8, 0.3, 0.6])
        
        model = PretrainedQNN('test', config, weights)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            save_model(model, temp_path, format='json')
            loaded = load_model(temp_path, format='json')
            
            assert loaded.model_name == model.model_name
            assert np.allclose(loaded.weights, model.weights)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_method_save_load(self):
        """Test save/load using model methods"""
        config = {'n_qubits': 2, 'n_layers': 1}
        weights = np.random.rand(4)
        
        model = PretrainedQNN('test', config, weights)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as f:
            temp_path = f.name
        
        try:
            model.save(temp_path)
            loaded = PretrainedQNN.load(temp_path)
            
            assert loaded.model_name == model.model_name
            assert np.allclose(loaded.weights, model.weights)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestModelZoo:
    """Test model zoo functionality"""
    
    def test_list_models(self):
        """Test listing models"""
        models = list_models()
        
        assert isinstance(models, list)
        assert len(models) == 5
        assert 'mnist_qnn' in models
        assert 'iris_qnn' in models
    
    def test_get_model_info(self):
        """Test getting model info"""
        info = get_model_info('mnist_qnn')
        
        assert 'dataset' in info
        assert 'n_qubits' in info
        assert 'task' in info
        assert info['n_qubits'] == 4
    
    def test_get_model_info_invalid(self):
        """Test error on invalid model name"""
        with pytest.raises(ValueError, match="not found"):
            get_model_info('nonexistent_model')
    
    def test_model_registry_structure(self):
        """Test model registry has correct structure"""
        for name, info in MODEL_REGISTRY.items():
            assert 'dataset' in info
            assert 'n_qubits' in info
            assert 'n_layers' in info
            assert 'task' in info
            assert 'path' in info


class TestFineTuning:
    """Test fine-tuning functionality"""
    
    def test_fine_tune_basic(self):
        """Test basic fine-tuning"""
        from quantum_debugger.qml.transfer import fine_tune_model
        
        config = {'n_qubits': 2, 'n_layers': 1}
        weights = np.random.rand(4)
        model = PretrainedQNN('test', config, weights)
        
        X_train = np.random.rand(20, 4)
        y_train = np.random.randint(0, 2, 20)
        
        history = fine_tune_model(
            model,
            X_train,
            y_train,
            epochs=5,
            verbose=False
        )
        
        assert 'loss' in history or 'accuracy' in history
    
    def test_create_few_shot_dataset(self):
        """Test few-shot dataset creation"""
        from quantum_debugger.qml.transfer.fine_tuning import create_few_shot_dataset
        
        X = np.random.rand(100, 4)
        y = np.array([0]*50 + [1]*50)  # Binary classes
        
        X_few, y_few = create_few_shot_dataset(X, y, n_samples_per_class=5)
        
        assert len(X_few) == 10  # 5 per class
        assert len(np.unique(y_few)) == 2  # Both classes present


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
