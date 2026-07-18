"""
Quantum Convolutional Neural Network (QCNN)

A QCNN (Cong et al. 2019) alternates *convolution* layers (parameterized
two-qubit gates on neighbouring qubits) with *pooling* layers that correlate
pairs of qubits and then drop half of them, funnelling information toward a
single readout qubit. This gives a shallow, translationally-structured circuit
with O(log n) depth of distinct parameters. Training uses parameter-shift
gradients on a squared-error objective; the prediction is read from the Pauli-Z
expectation of the final surviving qubit.
"""

import numpy as np


class QCNN:
    """
    Quantum Convolutional Neural Network binary classifier.

    Examples:
        >>> clf = QCNN(n_qubits=4)
        >>> clf.fit(X, y, epochs=50)   # X: (m, n_features), y in {0, 1}
        >>> clf.predict(X)
    """

    def __init__(self, n_qubits: int = 4, learning_rate: float = 0.1):
        if n_qubits < 2 or (n_qubits & (n_qubits - 1)) != 0:
            raise ValueError("n_qubits must be a power of two >= 2")
        self.n_qubits = n_qubits
        self.learning_rate = learning_rate

        self.blocks, self.readout = self._build_structure()
        self.params = np.random.uniform(0, 2 * np.pi, 2 * len(self.blocks))
        self.history = {"loss": [], "accuracy": []}

    def _build_structure(self):
        """List of (a, b) two-qubit blocks (conv + pool) and the readout qubit."""
        blocks = []
        active = list(range(self.n_qubits))
        while len(active) > 1:
            # Convolution on adjacent (non-overlapping) pairs.
            for i in range(0, len(active) - 1, 2):
                blocks.append((active[i], active[i + 1]))
            # Pooling: correlate each pair, keep the even one, drop the odd.
            new_active = []
            for i in range(0, len(active), 2):
                if i + 1 < len(active):
                    blocks.append((active[i + 1], active[i]))
                new_active.append(active[i])
            active = new_active
        return blocks, active[0]

    def _output(self, x, params) -> float:
        from ...core.circuit import QuantumCircuit

        x = np.asarray(x, dtype=float).ravel()
        circuit = QuantumCircuit(self.n_qubits)

        # Angle-encode the input.
        for q in range(self.n_qubits):
            circuit.ry(float(x[q % x.shape[0]]), q)

        # Convolution / pooling blocks.
        p = 0
        for a, b in self.blocks:
            circuit.ry(float(params[p]), a)
            circuit.ry(float(params[p + 1]), b)
            circuit.cnot(a, b)
            p += 2

        sv = circuit.get_statevector().state_vector
        probs = np.abs(sv) ** 2
        indices = np.arange(sv.shape[0])
        z = 1.0 - 2.0 * ((indices >> self.readout) & 1)
        return float(np.dot(probs, z))  # <Z_readout> in [-1, 1]

    def decision_function(self, X) -> np.ndarray:
        return np.array([self._output(x, self.params) for x in np.asarray(X)])

    def predict_proba(self, X) -> np.ndarray:
        return (self.decision_function(X) + 1.0) / 2.0

    def predict(self, X) -> np.ndarray:
        return (self.predict_proba(X) > 0.5).astype(int)

    def _loss_and_grad(self, X, y):
        targets = 2.0 * np.asarray(y, dtype=float) - 1.0
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
            d_out = 0.5 * (out_plus - out_minus)
            grad[k] = float(np.mean(2.0 * (outputs - targets) * d_out))
        return loss, grad

    def fit(self, X, y, epochs: int = 50, verbose: bool = False):
        from ..optimizers.basics import Adam

        X = np.asarray(X, dtype=float)
        y = np.asarray(y)
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

    def score(self, X, y) -> float:
        return float(np.mean(self.predict(X) == np.asarray(y)))
