"""
Variational Quantum Classifier (multi-class)

A general K-class classifier: the input is angle-encoded, a variational ansatz is
applied, and the Pauli-Z expectations of K readout qubits are turned into class
probabilities with a softmax. Trained by minimizing the cross-entropy with exact
parameter-shift gradients.
"""

import numpy as np


class VariationalQuantumClassifier:
    """
    Multi-class variational quantum classifier.

    Examples:
        >>> from sklearn.datasets import make_blobs
        >>> X, y = make_blobs(n_samples=90, centers=3, n_features=3)
        >>> clf = VariationalQuantumClassifier(n_qubits=3, n_classes=3, n_layers=3)
        >>> clf.fit(X, y, epochs=40)
        >>> clf.predict(X)
    """

    def __init__(
        self,
        n_qubits: int,
        n_classes: int,
        n_layers: int = 3,
        learning_rate: float = 0.1,
    ):
        if n_classes > n_qubits:
            raise ValueError("n_classes must be <= n_qubits (one readout qubit each)")
        self.n_qubits = n_qubits
        self.n_classes = n_classes
        self.n_layers = n_layers
        self.learning_rate = learning_rate

        self.params = np.random.uniform(0, 2 * np.pi, n_layers * n_qubits)
        self.history = {"loss": [], "accuracy": []}

    def _logits(self, x, params):
        from ...core.circuit import QuantumCircuit

        x = np.asarray(x, dtype=float).ravel()
        circuit = QuantumCircuit(self.n_qubits)
        for q in range(self.n_qubits):
            circuit.ry(float(x[q % x.shape[0]]), q)
        p = 0
        for _ in range(self.n_layers):
            for q in range(self.n_qubits):
                circuit.ry(float(params[p]), q)
                p += 1
            for q in range(self.n_qubits - 1):
                circuit.cnot(q, q + 1)
        sv = circuit.get_statevector().state_vector
        probs = np.abs(sv) ** 2
        idx = np.arange(sv.shape[0])
        return np.array(
            [np.dot(probs, 1.0 - 2.0 * ((idx >> c) & 1)) for c in range(self.n_classes)]
        )

    @staticmethod
    def _softmax(v):
        e = np.exp(v - np.max(v))
        return e / np.sum(e)

    def predict_proba(self, X):
        return np.array(
            [self._softmax(self._logits(x, self.params)) for x in np.asarray(X)]
        )

    def predict(self, X):
        return np.argmax(self.predict_proba(X), axis=1)

    def _loss_and_grad(self, X, y):
        y = np.asarray(y, dtype=int)
        # Forward pass: logits and softmax for every sample.
        logits = np.array([self._logits(x, self.params) for x in X])
        soft = np.array([self._softmax(z) for z in logits])
        loss = float(-np.mean([np.log(soft[i, y[i]] + 1e-9) for i in range(len(X))]))

        # d(cross-entropy)/d(logit_c) = softmax_c - onehot_c.
        dlogits = soft.copy()
        for i in range(len(X)):
            dlogits[i, y[i]] -= 1.0

        shift = np.pi / 2
        grad = np.zeros_like(self.params)
        for k in range(self.params.shape[0]):
            p_plus = self.params.copy()
            p_plus[k] += shift
            p_minus = self.params.copy()
            p_minus[k] -= shift
            # d(logit_c)/d(theta_k) per sample via parameter-shift.
            dz = np.array(
                [0.5 * (self._logits(x, p_plus) - self._logits(x, p_minus)) for x in X]
            )
            grad[k] = float(np.mean(np.sum(dlogits * dz, axis=1)))
        return loss, grad

    def fit(self, X, y, epochs: int = 40, verbose: bool = False):
        from ..optimizers.basics import Adam

        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=int)
        optimizer = Adam(learning_rate=self.learning_rate)

        for epoch in range(epochs):
            loss, grad = self._loss_and_grad(X, y)
            self.params = optimizer.step(self.params, grad)
            acc = float(np.mean(self.predict(X) == y))
            self.history["loss"].append(loss)
            self.history["accuracy"].append(acc)
            if verbose and (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch + 1}/{epochs} - loss {loss:.4f} - acc {acc:.3f}")
        return self

    def score(self, X, y):
        return float(np.mean(self.predict(X) == np.asarray(y, dtype=int)))
