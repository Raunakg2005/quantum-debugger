"""
Tests for Quantum Neural Networks
"""

import pytest
import numpy as np
from quantum_debugger.qml.qnn import (
    QNNLayer,
    EncodingLayer,
    VariationalLayer,
    QuantumNeuralNetwork,
    get_loss_function
)


class TestEncodingLayer:
    """Test encoding layers"""
    
    def test_zz_encoding(self):
        """Test ZZ feature map encoding"""
        layer = EncodingLayer(n_qubits=3, feature_map='zz', reps=1)
        
        assert layer.n_qubits == 3
        assert layer.num_parameters == 0  # Encoding has no trainable params
        
        data = np.array([0.5, 0.8, 0.3])
        circuit = layer.build_circuit(data=data)
        
        assert circuit.num_qubits == 3
   
    def test_angle_encoding(self):
        """Test angle encoding"""
        layer = EncodingLayer(n_qubits=2, feature_map='angle', rotation='Y')
        
        data = np.array([1.0, 2.0])
        circuit = layer.build_circuit(data=data)
        
        assert len(circuit.gates) == 2  # 2 RY gates
    
    def test_dimension_mismatch(self):
        """Test error when data dimension doesn't match"""
        layer = EncodingLayer(n_qubits=3, feature_map='zz')
        
        with pytest.raises(ValueError, match="doesn't match"):
            layer.build_circuit(data=np.array([0.1, 0.2]))  # Only 2 features
    
    def test_requires_data(self):
        """Test that encoding layer requires data"""
        layer = EncodingLayer(n_qubits=2, feature_map='zz')
        
        with pytest.raises(ValueError, match="requires data"):
            layer.build_circuit()  # No data provided


class TestVariationalLayer:
    """Test variational layers"""
    
    def test_real_amplitudes(self):
        """Test real amplitudes ansatz"""
        layer = VariationalLayer(n_qubits=3, ansatz='real_amplitudes', reps=2)
        
        assert layer.n_qubits == 3
        assert layer.num_parameters > 0
        
        # Build circuit with parameters
        params = np.random.uniform(0, 2*np.pi, layer.num_parameters)
        circuit = layer.build_circuit(params=params)
        
        assert circuit.num_qubits == 3
    
    def test_strongly_entangling(self):
        """Test strongly entangling ansatz"""
        layer = VariationalLayer(n_qubits=4, ansatz='strongly_entangling', reps=2)
        
        assert layer.num_parameters == 24  # 4 qubits × 3 rotations × 2 reps
        
        params = np.random.uniform(0, 2*np.pi, 24)
        circuit = layer.build_circuit(params=params)
        
        assert circuit is not None
    
    def test_parameter_initialization(self):
        """Test parameter initialization"""
        layer = VariationalLayer(n_qubits=2, ansatz='real_amplitudes', reps=1)
        
        # Random initialization
        params = layer.initialize_parameters('random', seed=42)
        assert len(params) == layer.num_parameters
        assert np.all((params >= 0) & (params <= 2*np.pi))
        
        # Zeros initialization
        params_zero = layer.initialize_parameters('zeros')
        assert np.all(params_zero == 0)


class TestLossFunctions:
    """Test loss functions"""
    
    def test_mse(self):
        """Test mean squared error"""
        loss_fn = get_loss_function('mse')
        
        pred = np.array([1.0, 2.0, 3.0])
        true = np.array([1.1, 1.9, 3.2])
        
        loss = loss_fn(pred, true)
        
        expected = np.mean((pred - true)**2)
        assert np.isclose(loss, expected)
    
    def test_binary_crossentropy(self):
        """Test binary cross-entropy"""
        loss_fn = get_loss_function('binary_crossentropy')
        
        pred = np.array([0.9, 0.1, 0.8])
        true = np.array([1.0, 0.0, 1.0])
        
        loss = loss_fn(pred, true)
        
        assert loss > 0
        assert np.isfinite(loss)
    
    def test_invalid_loss(self):
        """Test error for unknown loss function"""
        with pytest.raises(ValueError, match="Unknown loss"):
            get_loss_function('invalid_loss')


class TestQuantumNeuralNetwork:
    """Test QNN network"""
    
    def test_initialization(self):
        """Test QNN creation"""
        qnn = QuantumNeuralNetwork(n_qubits=3)
        
        assert qnn.n_qubits == 3
        assert len(qnn.layers) == 0
        assert qnn.num_parameters == 0
    
    def test_add_layers(self):
        """Test adding layers"""
        qnn = QuantumNeuralNetwork(n_qubits=3)
        
        qnn.add(EncodingLayer(3, feature_map='zz'))
        qnn.add(VariationalLayer(3, ansatz='real_amplitudes', reps=1))
        
        assert len(qnn.layers) == 2
        assert qnn.num_parameters > 0
    
    def test_layer_qubit_mismatch(self):
        """Test error when layer qubits don't match"""
        qnn = QuantumNeuralNetwork(n_qubits=3)
        
        with pytest.raises(ValueError, match="qubits"):
            qnn.add(EncodingLayer(4, feature_map='zz'))  # Wrong number
    
    def test_compile(self):
        """Test network compilation"""
        qnn = QuantumNeuralNetwork(n_qubits=2)
        qnn.add(EncodingLayer(2, feature_map='angle'))
        qnn.add(VariationalLayer(2, ansatz='real_amplitudes', reps=1))
        
        qnn.compile(optimizer='adam', loss='mse', learning_rate=0.01)
        
        assert qnn.compiled
        assert qnn.optimizer_name == 'adam'
        assert qnn.learning_rate == 0.01
        assert qnn.loss_fn is not None
    
    def test_forward_pass(self):
        """Test forward pass"""
        qnn = QuantumNeuralNetwork(n_qubits=2)
        qnn.add(EncodingLayer(2, feature_map='angle'))
        qnn.add(VariationalLayer(2, ansatz='real_amplitudes', reps=1))
        
        qnn.compile(optimizer='adam', loss='mse')
        
        # Test data
        X = np.random.rand(5, 2)  # 5 samples, 2 features
        
        params = qnn._initialize_all_parameters()
        predictions = qnn.forward(params, X)
        
        assert len(predictions) == 5
        assert np.all(np.isfinite(predictions))
    
    def test_training_toy_problem(self):
        """Test training on simple problem"""
        # Create simple dataset
        X_train = np.array([[0.1, 0.2], [0.3, 0.4], [0.5, 0.6], [0.7, 0.8]])
        y_train = np.array([0.3, 0.7, 1.1, 1.5])
        
        qnn = QuantumNeuralNetwork(n_qubits=2)
        qnn.add(EncodingLayer(2, feature_map='angle'))
        qnn.add(VariationalLayer(2, ansatz='real_amplitudes', reps=1))
        
        qnn.compile(optimizer='adam', loss='mse')
        
        history = qnn.fit(X_train, y_train, epochs=5, verbose=0)
        
        assert 'loss' in history
        assert len(history['loss']) == 5
    
    def test_prediction(self):
        """Test making predictions"""
        X_train = np.random.rand(10, 2)
        y_train = np.random.rand(10)
        
        qnn = QuantumNeuralNetwork(n_qubits=2)
        qnn.add(EncodingLayer(2, feature_map='angle'))
        qnn.add(VariationalLayer(2, ansatz='real_amplitudes', reps=1))
        
        qnn.compile(optimizer='adam', loss='mse')
        qnn.fit(X_train, y_train, epochs=3, verbose=0)
        
        X_test = np.random.rand(3, 2)
        predictions = qnn.predict(X_test)
        
        assert len(predictions) == 3
    
    def test_summary(self):
        """Test network summary"""
        qnn = QuantumNeuralNetwork(n_qubits=3)
        qnn.add(EncodingLayer(3, feature_map='zz'))
        qnn.add(VariationalLayer(3, ansatz='real_amplitudes', reps=2))
        qnn.add(VariationalLayer(3, ansatz='strongly_entangling', reps=1))
        
        # Should not raise error
        qnn.summary()


class TestIntegration:
    """Integration tests"""
    
    def test_complete_workflow(self):
        """Test complete QNN workflow"""
        # Synthetic dataset
        np.random.seed(42)
        X_train = np.random.rand(20, 3)
        y_train = np.random.rand(20)
        X_test = np.random.rand(5, 3)
        
        # Build network
        qnn = QuantumNeuralNetwork(n_qubits=3)
        qnn.add(EncodingLayer(3, feature_map='zz', reps=1))
        qnn.add(VariationalLayer(3, ansatz='real_amplitudes', reps=2))
        qnn.add(VariationalLayer(3, ansatz='strongly_entangling', reps=1))
        
        # Compile
        qnn.compile(optimizer='adam', loss='mse', learning_rate=0.01)
        
        # Train
        history = qnn.fit(X_train, y_train, epochs=5, batch_size=5, verbose=0)
        
        # Predict
        predictions = qnn.predict(X_test)
        
        assert len(predictions) == 5
        assert len(history['loss']) == 5
    
    def test_validation_split(self):
        """Test training with validation data"""
        X_train = np.random.rand(30, 2)
        y_train = np.random.rand(30)
        X_val = np.random.rand(10, 2)
        y_val = np.random.rand(10)
        
        qnn = QuantumNeuralNetwork(n_qubits=2)
        qnn.add(EncodingLayer(2, feature_map='angle'))
        qnn.add(VariationalLayer(2, ansatz='real_amplitudes', reps=1))
        
        qnn.compile(optimizer='adam', loss='mse')
        
        history = qnn.fit(
            X_train, y_train,
            epochs=5,
            validation_data=(X_val, y_val),
            verbose=0
        )
        
        assert 'loss' in history
        assert 'val_loss' in history
        assert len(history['val_loss']) == 5
