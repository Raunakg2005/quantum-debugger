"""
Data Re-uploading Quantum Classifier

Implements the data re-uploading scheme (Perez-Salinas et al., 2020): instead of
encoding the input once, the data is *re-encoded* before every variational
layer. Interleaving encoding and trainable layers dramatically increases
expressivity -- a single qubit with enough re-uploading layers is a universal
function approximator, and a few qubits can learn nonlinearly-separable data
(e.g. concentric circles) that a single-encoding circuit cannot.

The readout is the Pauli-Z expectation on qubit 0, and training uses exact
parameter-shift gradients on a squared-error objective.
"""

import numpy as np


class DataReuploadingClassifier:
    """
    A binary classifier based on data re-uploading.

    Examples:
        >>> from sklearn.datasets import make_circles
        >>> X, y = make_circles(n_samples=100, noise=0.05, factor=0.3)
        >>> clf = DataReuploadingClassifier(n_qubits=2, n_layers=4)
        >>> clf.fit(X, y, epochs=60)
        >>> preds = clf.predict(X)
    """

    def __init__(
        self,
        n_qubits: int = 2,
        n_layers: int = 4,
        learning_rate: float = 0.1,
        data_scale: float = 1.0,
    ):
        self.n_qubits = n_qubits
        self.n_layers = n_layers
        self.learning_rate = learning_rate
        self.data_scale = data_scale

        # One trainable RY angle per qubit per layer.
        self.params = np.random.uniform(0, 2 * np.pi, n_layers * n_qubits)
        self.history = {"loss": [], "accuracy": []}

    def _output(self, x: np.ndarray, params: np.ndarray) -> float:
        """<Z_0> of the data-re-uploading circuit for a single sample."""
        from ...core.circuit import QuantumCircuit

        x = np.asarray(x, dtype=float).ravel()
        circuit = QuantumCircuit(self.n_qubits)

        p = 0
        for _ in range(self.n_layers):
            # Re-upload the data.
            for q in range(self.n_qubits):
                circuit.ry(self.data_scale * float(x[q % x.shape[0]]), q)
            # Trainable layer + entanglement.
            for q in range(self.n_qubits):
                circuit.ry(float(params[p]), q)
                p += 1
            for q in range(self.n_qubits - 1):
                circuit.cnot(q, q + 1)

        sv = circuit.get_statevector().state_vector
        probs = np.abs(sv) ** 2
        indices = np.arange(sv.shape[0])
        return float(np.dot(probs, 1.0 - 2.0 * (indices & 1)))  # <Z_0> in [-1, 1]

    def decision_function(self, X: np.ndarray) -> np.ndarray:
        """Raw <Z_0> outputs in [-1, 1]."""
        return np.array([self._output(x, self.params) for x in np.asarray(X)])

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Probability of class 1, mapped from <Z_0> as (<Z_0> + 1) / 2."""
        return (self.decision_function(X) + 1.0) / 2.0

    def predict(self, X: np.ndarray) -> np.ndarray:
        return (self.predict_proba(X) > 0.5).astype(int)

    def _loss_and_grad(self, X: np.ndarray, y: np.ndarray):
        """Squared error between <Z_0> and the +/-1 label, with parameter-shift grad."""
        targets = 2.0 * np.asarray(y, dtype=float) - 1.0  # {0,1} -> {-1,+1}
        outputs = np.array([self._output(x, self.params) for x in X])
        loss = float(np.mean((outputs - targets) ** 2))

        shift = np.pi / 2
        grad = np.zeros_like(self.params)
        for k in range(self.params.shape[0]):
            p_plus = self.params.copy()
            p_plus[k] += shift
            p_minus = self.params.copy()
            p_minus[k] -= shift
            out_plus = np.array([self._output(x, p_plus) for x in X])
            out_minus = np.array([self._output(x, p_minus) for x in X])
            d_out = 0.5 * (out_plus - out_minus)  # exact d<Z_0>/d theta_k per sample
            grad[k] = float(np.mean(2.0 * (outputs - targets) * d_out))
        return loss, grad

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 60,
        verbose: bool = False,
    ):
        from ..optimizers.basics import Adam

        X = np.asarray(X, dtype=float)
        y = np.asarray(y)
        optimizer = Adam(learning_rate=self.learning_rate)

        for epoch in range(epochs):
            loss, grad = self._loss_and_grad(X, y)
            self.params = optimizer.step(self.params, grad)

            accuracy = float(np.mean(self.predict(X) == y))
            self.history["loss"].append(loss)
            self.history["accuracy"].append(accuracy)
            if verbose and (epoch + 1) % 10 == 0:
                print(
                    f"Epoch {epoch + 1}/{epochs} - loss {loss:.4f} - acc {accuracy:.3f}"
                )

        return self

    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        return float(np.mean(self.predict(X) == np.asarray(y)))
