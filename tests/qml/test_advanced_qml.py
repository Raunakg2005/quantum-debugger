"""Tests for advanced QML: data re-uploading + ansatz analysis."""

import numpy as np
import pytest

from quantum_debugger.qml.advanced import (
    DataReuploadingClassifier,
    expressibility,
    entangling_capability,
    gradient_variance,
    n_params,
)


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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
