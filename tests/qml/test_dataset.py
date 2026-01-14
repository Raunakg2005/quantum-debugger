"""
Tests for dataset loading and preprocessing
"""

import pytest
import numpy as np
import tempfile
import csv
import json
from pathlib import Path

from quantum_debugger.qml.data import (
    QuantumDataset,
    load_csv,
    load_json,
    load_numpy,
    zz_feature_map,
    pauli_feature_map,
    angle_encoding,
    get_feature_map,
)


class TestQuantumDataset:
    """Test QuantumDataset class"""

    def test_initialization(self):
        """Test basic initialization"""
        X = np.random.rand(10, 4)
        y = np.random.randint(0, 2, 10)

        dataset = QuantumDataset(X, y)

        assert dataset.n_samples == 10
        assert dataset.n_features == 4
        assert dataset.shape == (10, 4)

    def test_without_labels(self):
        """Test dataset without labels (unsupervised)"""
        X = np.random.rand(20, 3)
        dataset = QuantumDataset(X)

        assert dataset.n_samples == 20
        assert dataset.y is None

    def test_dimension_mismatch(self):
        """Test error when X and y have different lengths"""
        X = np.random.rand(10, 4)
        y = np.random.rand(5)  # Wrong size

        with pytest.raises(ValueError, match="same length"):
            QuantumDataset(X, y)

    def test_train_test_split(self):
        """Test train/test splitting"""
        X = np.random.rand(100, 4)
        y = np.random.randint(0, 2, 100)
        dataset = QuantumDataset(X, y)

        train, test = dataset.train_test_split(test_size=0.2, random_state=42)

        assert train.n_samples == 80
        assert test.n_samples == 20
        assert train.n_features == 4
        assert test.n_features == 4

    def test_split_without_shuffle(self):
        """Test splitting without shuffling"""
        X = np.arange(100).reshape(100, 1)
        y = np.arange(100)
        dataset = QuantumDataset(X, y)

        train, test = dataset.train_test_split(test_size=0.2, shuffle=False)

        # Without shuffle, last 20 should be test
        assert test.y[0] == 80
        assert test.y[-1] == 99

    def test_normalize_minmax(self):
        """Test min-max normalization"""
        X = np.array([[0, 10], [5, 20], [10, 30]])
        dataset = QuantumDataset(X)

        normalized = dataset.normalize(method="minmax")

        # Should be scaled to [0, 1]
        assert normalized.X.min() == 0.0
        assert normalized.X.max() == 1.0

    def test_normalize_standard(self):
        """Test z-score normalization"""
        X = np.random.randn(100, 3) * 10 + 5
        dataset = QuantumDataset(X)

        normalized = dataset.normalize(method="standard")

        # Should have mean ≈ 0, std ≈ 1
        assert np.abs(normalized.X.mean(axis=0)).max() < 0.1
        np.testing.assert_array_almost_equal(normalized.X.std(axis=0), 1.0, decimal=1)

    def test_normalize_maxabs(self):
        """Test max absolute value normalization"""
        X = np.array([[-10, 20], [5, -15], [8, 10]])
        dataset = QuantumDataset(X)

        normalized = dataset.normalize(method="maxabs")

        # Max absolute value should be 1
        assert np.abs(normalized.X).max() == 1.0

    def test_feature_names(self):
        """Test feature names handling"""
        X = np.random.rand(10, 3)
        names = ["feat_a", "feat_b", "feat_c"]
        dataset = QuantumDataset(X, feature_names=names)

        assert dataset.feature_names == names

    def test_metadata(self):
        """Test metadata storage"""
        X = np.random.rand(5, 2)
        meta = {"source": "test", "version": 1}
        dataset = QuantumDataset(X, metadata=meta)

        assert dataset.metadata == meta


class TestDataLoading:
    """Test data loading functions"""

    def test_load_csv_with_header(self):
        """Test loading CSV with header"""
        # Create temporary CSV
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".csv", newline=""
        ) as f:
            writer = csv.writer(f)
            writer.writerow(["feature1", "feature2", "label"])
            writer.writerow(["1.0", "2.0", "0"])
            writer.writerow(["3.0", "4.0", "1"])
            writer.writerow(["5.0", "6.0", "0"])
            csv_path = f.name

        try:
            dataset = load_csv(csv_path, label_column="label", has_header=True)

            assert dataset.n_samples == 3
            assert dataset.n_features == 2
            assert len(dataset.y) == 3
            assert dataset.feature_names == ["feature1", "feature2"]
        finally:
            Path(csv_path).unlink()

    def test_load_csv_without_header(self):
        """Test loading CSV without header"""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".csv", newline=""
        ) as f:
            writer = csv.writer(f)
            writer.writerow(["1.0", "2.0", "0"])
            writer.writerow(["3.0", "4.0", "1"])
            csv_path = f.name

        try:
            dataset = load_csv(csv_path, label_column=2, has_header=False)

            assert dataset.n_samples == 2
            assert dataset.n_features == 2
        finally:
            Path(csv_path).unlink()

    def test_load_json(self):
        """Test loading JSON data"""
        data_dict = {
            "data": [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]],
            "labels": [0, 1, 0],
            "feature_names": ["x", "y"],
        }

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            json.dump(data_dict, f)
            json_path = f.name

        try:
            dataset = load_json(json_path)

            assert dataset.n_samples == 3
            assert dataset.n_features == 2
            assert dataset.feature_names == ["x", "y"]
        finally:
            Path(json_path).unlink()

    def test_load_numpy(self):
        """Test loading from NumPy arrays"""
        X = np.random.rand(20, 5)
        y = np.random.randint(0, 3, 20)

        dataset = load_numpy(X, y)

        assert dataset.n_samples == 20
        assert dataset.n_features == 5


class TestFeatureMaps:
    """Test quantum feature maps"""

    def test_zz_feature_map_basic(self):
        """Test ZZ feature map creation"""
        feature_map = zz_feature_map(n_qubits=3, reps=1)
        data = np.array([0.5, 0.8, 0.3])

        circuit = feature_map(data)

        assert circuit.num_qubits == 3
        assert len(circuit.gates) > 0

    def test_zz_feature_map_dimension_check(self):
        """Test dimension mismatch error"""
        feature_map = zz_feature_map(n_qubits=3, reps=1)
        data = np.array([0.5, 0.8])  # Wrong size

        with pytest.raises(ValueError, match="doesn't match"):
            feature_map(data)

    def test_zz_feature_map_multiple_reps(self):
        """Test with multiple repetitions"""
        feature_map = zz_feature_map(n_qubits=2, reps=3)
        data = np.array([0.1, 0.2])

        circuit = feature_map(data)

        # More reps should mean more gates
        assert len(circuit.gates) > 6

    def test_pauli_feature_map_z(self):
        """Test Pauli feature map with Z"""
        feature_map = pauli_feature_map(n_qubits=2, paulis="Z", reps=1)
        data = np.array([0.5, 0.7])

        circuit = feature_map(data)

        assert circuit.num_qubits == 2

    def test_pauli_feature_map_zz(self):
        """Test Pauli feature map with ZZ"""
        feature_map = pauli_feature_map(n_qubits=3, paulis="ZZ", reps=2)
        data = np.array([0.1, 0.2, 0.3])

        circuit = feature_map(data)

        assert circuit.num_qubits == 3

    def test_angle_encoding_y(self):
        """Test angle encoding with Y rotations"""
        encoder = angle_encoding(n_qubits=4, rotation="Y")
        data = np.array([0.1, 0.2, 0.3, 0.4])

        circuit = encoder(data)

        assert circuit.num_qubits == 4
        # Should have 4 RY gates
        assert len(circuit.gates) == 4

    def test_angle_encoding_x(self):
        """Test angle encoding with X rotations"""
        encoder = angle_encoding(n_qubits=2, rotation="X")
        data = np.array([1.0, 2.0])

        circuit = encoder(data)

        # Check for RX gates
        assert all(g.name == "RX" for g in circuit.gates)

    def test_angle_encoding_z(self):
        """Test angle encoding with Z rotations"""
        encoder = angle_encoding(n_qubits=2, rotation="Z")
        data = np.array([0.5, 1.5])

        circuit = encoder(data)

        assert all(g.name == "RZ" for g in circuit.gates)

    def test_get_feature_map_zz(self):
        """Test factory function for ZZ map"""
        fm = get_feature_map("zz", n_qubits=3, reps=2)
        data = np.array([0.1, 0.2, 0.3])

        circuit = fm(data)

        assert circuit.num_qubits == 3

    def test_get_feature_map_angle(self):
        """Test factory function for angle encoding"""
        fm = get_feature_map("angle", n_qubits=2, rotation="Y")
        data = np.array([0.5, 1.0])

        circuit = fm(data)

        assert len(circuit.gates) == 2

    def test_get_feature_map_invalid(self):
        """Test error for unknown feature map"""
        with pytest.raises(ValueError, match="Unknown feature map"):
            get_feature_map("invalid", n_qubits=2)


class TestIntegration:
    """Integration tests combining dataset and feature maps"""

    def test_load_and_encode(self):
        """Test loading data and encoding to quantum"""
        # Create dataset
        X = np.random.rand(10, 3)
        y = np.random.randint(0, 2, 10)
        dataset = QuantumDataset(X, y)

        # Normalize
        dataset = dataset.normalize("minmax")

        # Split
        train, test = dataset.train_test_split(test_size=0.3, random_state=42)

        # Create feature map
        feature_map = zz_feature_map(n_qubits=3, reps=2)

        # Encode first sample
        circuit = feature_map(train.X[0])

        assert circuit.num_qubits == 3
        assert len(circuit.gates) > 0

    def test_workflow_csv_to_quantum(self):
        """Test complete workflow: CSV → Dataset → Normalize → Encode"""
        # Create temp CSV
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".csv", newline=""
        ) as f:
            writer = csv.writer(f)
            writer.writerow(["f1", "f2", "label"])
            for _ in range(20):
                writer.writerow(
                    [
                        str(np.random.rand()),
                        str(np.random.rand()),
                        str(np.random.randint(0, 2)),
                    ]
                )
            csv_path = f.name

        try:
            # Load
            dataset = load_csv(csv_path, label_column="label")

            # Preprocess
            dataset = dataset.normalize("standard")
            train, test = dataset.train_test_split(0.25)

            # Encode
            encoder = angle_encoding(n_qubits=2, rotation="Y")
            circuits = [encoder(sample) for sample in train.X[:5]]

            assert len(circuits) == 5
            assert all(c.num_qubits == 2 for c in circuits)
        finally:
            Path(csv_path).unlink()
