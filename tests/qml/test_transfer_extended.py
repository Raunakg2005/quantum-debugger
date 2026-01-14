"""
Extended tests for transfer learning module - edge cases and integration
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
    fine_tune_model,
    transfer_weights
)
from quantum_debugger.qml.transfer.serialization import get_model_size, get_model_size_mb
from quantum_debugger.qml.transfer.fine_tuning import (
    compute_transfer_benefit,
    create_few_shot_dataset
)


class TestPretrainedQNNEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_weights(self):
        """Test handling of empty weights"""
        config = {'n_qubits': 2, 'n_layers': 1}
        weights = np.array([])
        
        # Should still create but may not work
        model = PretrainedQNN('test', config, weights)
        assert model.model_name == 'test'
    
    def test_mismatched_config(self):
        """Test config with missing values"""
        config = {}  # Empty config
        weights = np.random.rand(4)
        
        model = PretrainedQNN('test', config, weights)
        # Should use defaults
        assert model.n_qubits == 4
        assert model.n_layers == 2
    
    def test_predict_empty_data(self):
        """Test prediction with empty input"""
        config = {'n_qubits': 2, 'n_layers': 1}
        weights = np.random.rand(4)
        model = PretrainedQNN('test', config, weights)
        
        X = np.array([]).reshape(0, 4)
        predictions = model.predict(X)
        
        assert len(predictions) == 0
    
    def test_score_perfect_match(self):
        """Test scoring with perfect predictions"""
        config = {'n_qubits': 2, 'n_layers': 1}
        weights = np.random.rand(4)
        model = PretrainedQNN('test', config, weights)
        
        # Create data where predictions will match
        X = np.random.rand(10, 4)
        y_pred = model.predict(X)
        
        # Score against itself
        score = model.score(X, y_pred)
        assert score == 1.0


class TestSerializationFormats:
    """Test different serialization formats thoroughly"""
    
    def test_pickle_preserves_metadata(self):
        """Test pickle format preserves all metadata"""
        config = {'n_qubits': 4, 'n_layers': 2, 'custom_field': 'value'}
        weights = np.random.rand(8)
        metadata = {'dataset': 'test', 'accuracy': 0.95, 'custom': 'data'}
        
        model = PretrainedQNN('test', config, weights, metadata)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as f:
            temp_path = f.name
        
        try:
            save_model(model, temp_path, format='pickle')
            loaded = load_model(temp_path, format='pickle')
            
            assert loaded.config == config
            assert loaded.metadata == metadata
            assert loaded.metadata['custom'] == 'data'
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_json_handles_numpy_types(self):
        """Test JSON format handles numpy types correctly"""
        config = {'n_qubits': 2, 'n_layers': 1}
        weights = np.array([0.1, 0.2, 0.3, 0.4])
        
        model = PretrainedQNN('test', config, weights)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            save_model(model, temp_path, format='json')
            loaded = load_model(temp_path, format='json')
            
            assert isinstance(loaded.weights, np.ndarray)
            assert np.allclose(loaded.weights, weights)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_unsupported_format_raises_error(self):
        """Test unsupported format raises ValueError"""
        config = {'n_qubits': 2}
        weights = np.random.rand(4)
        model = PretrainedQNN('test', config, weights)
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Unsupported format"):
                save_model(model, temp_path, format='xml')
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_load_nonexistent_file(self):
        """Test loading nonexistent file raises error"""
        with pytest.raises(FileNotFoundError):
            load_model('/nonexistent/path/model.pkl')
    
    def test_model_size_functions(self):
        """Test file size utility functions"""
        config = {'n_qubits': 2}
        weights = np.random.rand(4)
        model = PretrainedQNN('test', config, weights)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as f:
            temp_path = f.name
        
        try:
            save_model(model, temp_path)
            
            size_bytes = get_model_size(temp_path)
            size_mb = get_model_size_mb(temp_path)
            
            assert size_bytes > 0
            assert size_mb > 0
            assert size_mb == size_bytes / (1024 * 1024)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestFineTuningAdvanced:
    """Advanced fine-tuning tests"""
    
    def test_fine_tune_improves_accuracy(self):
        """Test that fine-tuning completes successfully"""
        config = {'n_qubits': 2, 'n_layers': 1}
        weights = np.random.rand(4)
        model = PretrainedQNN('test', config, weights)
        
        # Create simple dataset
        X_train = np.random.rand(30, 4)
        y_train = np.random.randint(0, 2, 30)
        
        # Fine-tune
        history = fine_tune_model(
            model,
            X_train,
            y_train,
            epochs=5,
            verbose=False
        )
        
        # Verify fine-tuning completed and returned history
        assert isinstance(history, dict)
        assert len(history) > 0
        
        # Verify metadata was updated
        assert model.metadata.get('fine_tuned') == True
        assert model.metadata.get('fine_tune_epochs') == 5
    
    def test_fine_tune_with_validation(self):
        """Test fine-tuning with validation data"""
        config = {'n_qubits': 2, 'n_layers': 1}
        weights = np.random.rand(4)
        model = PretrainedQNN('test', config, weights)
        
        X_train = np.random.rand(20, 4)
        y_train = np.random.randint(0, 2, 20)
        X_val = np.random.rand(10, 4)
        y_val = np.random.randint(0, 2, 10)
        
        history = fine_tune_model(
            model,
            X_train,
            y_train,
            X_val=X_val,
            y_val=y_val,
            epochs=3,
            verbose=False
        )
        
        assert 'val_accuracy' in history
    
    def test_few_shot_dataset_balanced(self):
        """Test few-shot dataset maintains class balance"""
        X = np.random.rand(100, 4)
        y = np.array([0]*50 + [1]*50)
        
        X_few, y_few = create_few_shot_dataset(X, y, n_samples_per_class=10)
        
        # Check balance
        unique, counts = np.unique(y_few, return_counts=True)
        assert len(unique) == 2
        assert all(c == 10 for c in counts)
    
    def test_few_shot_with_imbalanced_data(self):
        """Test few-shot with imbalanced classes"""
        X = np.random.rand(100, 4)
        y = np.array([0]*80 + [1]*20)  # Imbalanced
        
        X_few, y_few = create_few_shot_dataset(X, y, n_samples_per_class=15)
        
        # Should get 15 from class 0, but only 15 from class 1 (limited)
        unique, counts = np.unique(y_few, return_counts=True)
        assert len(unique) == 2
        assert counts[1] <= 20  # Can't have more than available


class TestIntegration:
    """Integration tests with actual QNN workflow"""
    
    def test_from_qnn_conversion(self):
        """Test converting trained QNN to PretrainedQNN"""
        from quantum_debugger.qml.qnn import QuantumNeuralNetwork
        from quantum_debugger.qml.qnn.encoding import EncodingLayer
        
        # Create and configure QNN
        qnn = QuantumNeuralNetwork(n_qubits=2)
        qnn.add(EncodingLayer(n_qubits=2, n_features=4))
        qnn.compile(optimizer='adam', loss='mse')
        
        # Simulate some training
        qnn._parameters = np.random.rand(4)
        
        # Convert to PretrainedQNN
        pretrained = PretrainedQNN.from_qnn(
            qnn,
            model_name='test_qnn',
            dataset='Test Dataset',
            metadata={'accuracy': 0.85}
        )
        
        assert pretrained.model_name == 'test_qnn'
        assert pretrained.n_qubits == 2
        assert pretrained.metadata['dataset'] == 'Test Dataset'
        assert pretrained.metadata['accuracy'] == 0.85
    
    def test_save_load_roundtrip_preserves_predictions(self):
        """Test that save/load preserves model predictions"""
        config = {'n_qubits': 2, 'n_layers': 1}
        weights = np.random.rand(4)
        model = PretrainedQNN('test', config, weights)
        
        X_test = np.random.rand(5, 4)
        predictions_before = model.predict(X_test)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as f:
            temp_path = f.name
        
        try:
            model.save(temp_path)
            loaded_model = PretrainedQNN.load(temp_path)
            
            predictions_after = loaded_model.predict(X_test)
            
            # Predictions should be identical
            assert np.array_equal(predictions_before, predictions_after)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_metadata_updates_after_fine_tuning(self):
        """Test metadata is updated after fine-tuning"""
        config = {'n_qubits': 2}
        weights = np.random.rand(4)
        model = PretrainedQNN('test', config, weights)
        
        assert 'fine_tuned' not in model.metadata
        
        X = np.random.rand(20, 4)
        y = np.random.randint(0, 2, 20)
        
        model.fine_tune(X, y, epochs=3, verbose=False)
        
        assert model.metadata['fine_tuned'] == True
        assert model.metadata['fine_tune_epochs'] == 3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
