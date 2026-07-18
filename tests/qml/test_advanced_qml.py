"""Tests for advanced QML: data re-uploading + ansatz analysis."""

import numpy as np
import pytest

from quantum_debugger.qml.advanced import (
    DataReuploadingClassifier,
    QuantumAutoencoder,
    QCNN,
    expressibility,
    entangling_capability,
    gradient_variance,
    n_params,
)
from quantum_debugger.core.circuit import QuantumCircuit
from quantum_debugger.core.quantum_state import QuantumState


class TestDataReuploadingClassifier:
    def test_initialization(self):
        clf = DataReuploadingClassifier(n_qubits=2, n_layers=4)
        assert clf.params.shape[0] == 4 * 2

    def test_predict_shapes(self):
        clf = DataReuploadingClassifier(n_qubits=2, n_layers=3)
        X = np.random.rand(5, 2)
        assert clf.predict(X).shape == (5,)
        proba = clf.predict_proba(X)
        assert proba.shape == (5,)
        assert np.all((proba >= 0) & (proba <= 1))

    def test_decision_function_range(self):
        clf = DataReuploadingClassifier(n_qubits=2, n_layers=3)
        out = clf.decision_function(np.random.rand(8, 2))
        assert np.all((out >= -1.000001) & (out <= 1.000001))

    def test_fit_records_history(self):
        clf = DataReuploadingClassifier(n_qubits=2, n_layers=2)
        X = np.random.rand(10, 2)
        y = (X[:, 0] > 0.5).astype(int)
        clf.fit(X, y, epochs=5)
        assert len(clf.history["loss"]) == 5
        assert len(clf.history["accuracy"]) == 5

    def test_learns_nonlinear_circles(self):
        """Data re-uploading should separate concentric circles (>~0.8)."""
        pytest.importorskip("sklearn")
        from sklearn.datasets import make_circles

        np.random.seed(0)
        X, y = make_circles(n_samples=100, noise=0.05, factor=0.3, random_state=0)
        X = X * np.pi
        clf = DataReuploadingClassifier(n_qubits=2, n_layers=5, learning_rate=0.15)
        clf.fit(X, y, epochs=60)
        assert clf.score(X, y) > 0.8


class TestAnsatzAnalysis:
    def test_n_params(self):
        assert n_params(4, 3) == 12

    def test_expressibility_improves_with_depth(self):
        # More layers -> closer to Haar -> smaller KL.
        kl_shallow = expressibility(3, 1, n_samples=250)
        kl_deep = expressibility(3, 4, n_samples=250)
        assert kl_shallow >= 0 and kl_deep >= 0
        assert kl_deep < kl_shallow

    def test_entangling_capability_in_range(self):
        q1 = entangling_capability(3, 1, n_samples=150)
        q3 = entangling_capability(3, 3, n_samples=150)
        assert 0.0 <= q1 <= 1.0
        assert 0.0 <= q3 <= 1.0
        # Deeper circuits (more CNOT layers) entangle more.
        assert q3 >= q1

    def test_barren_plateau_gradient_decay(self):
        # Gradient variance should shrink as the qubit count grows.
        var_small = gradient_variance(2, 6, n_samples=100)
        var_large = gradient_variance(6, 6, n_samples=100)
        assert var_small > 0
        assert var_large < var_small


class TestQuantumAutoencoder:
    def test_initialization(self):
        ae = QuantumAutoencoder(n_qubits=3, n_trash=1, n_layers=3)
        assert ae.trash_qubits == [2]
        assert ae.params.shape[0] == 3 * 3

    def test_rejects_too_many_trash(self):
        with pytest.raises(ValueError):
            QuantumAutoencoder(n_qubits=2, n_trash=2)

    def test_compresses_compressible_data(self):
        """Trash qubit should be reset to |0> for compressible inputs."""
        np.random.seed(1)
        n = 3
        sp = np.random.uniform(0, 2 * np.pi, 2 * n)

        def scramble(sv):
            qc = QuantumCircuit(n)
            p = 0
            for _ in range(2):
                for q in range(n):
                    qc.ry(float(sp[p]), q)
                    p += 1
                for q in range(n - 1):
                    qc.cnot(q, q + 1)
            return qc.get_statevector(
                initial_state=QuantumState(n, state_vector=sv)
            ).state_vector

        inputs = []
        for _ in range(10):
            qc = QuantumCircuit(n)
            qc.ry(np.random.uniform(0, 2 * np.pi), 0)
            qc.ry(np.random.uniform(0, 2 * np.pi), 1)
            inputs.append(scramble(qc.get_statevector().state_vector))
        inputs = np.array(inputs)

        ae = QuantumAutoencoder(n_qubits=3, n_trash=1, n_layers=4, learning_rate=0.1)
        before = ae.trash_fidelity(inputs)
        ae.fit(inputs, epochs=60)
        after = ae.trash_fidelity(inputs)
        assert after > before
        assert after > 0.9


class TestQCNN:
    def test_structure_is_power_of_two(self):
        with pytest.raises(ValueError):
            QCNN(n_qubits=3)

    def test_reduces_to_single_readout(self):
        clf = QCNN(n_qubits=4)
        assert isinstance(clf.readout, int)
        assert clf.params.shape[0] == 2 * len(clf.blocks)

    def test_predict_shapes(self):
        clf = QCNN(n_qubits=4)
        X = np.random.rand(5, 4)
        assert clf.predict(X).shape == (5,)
        assert np.all((clf.predict_proba(X) >= 0) & (clf.predict_proba(X) <= 1))

    def test_learns_separable_blobs(self):
        pytest.importorskip("sklearn")
        from sklearn.datasets import make_blobs

        np.random.seed(0)
        X, y = make_blobs(
            n_samples=50, centers=2, n_features=4, cluster_std=1.2, random_state=0
        )
        X = (X - X.min(0)) / (X.max(0) - X.min(0)) * np.pi
        clf = QCNN(n_qubits=4, learning_rate=0.1)
        clf.fit(X, y, epochs=40)
        assert clf.score(X, y) > 0.75


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
