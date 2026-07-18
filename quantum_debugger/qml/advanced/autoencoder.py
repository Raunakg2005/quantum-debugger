"""
Quantum Autoencoder

Compresses n-qubit quantum data into (n - n_trash) qubits (Romero et al. 2017).
A variational encoder V(theta) is trained so that the ``trash`` qubits are
disentangled and left in |0>; the remaining qubits then hold the compressed
state, and applying V-dagger reconstructs the input. Training minimizes the
probability that the trash qubits are measured as |1>, using exact
parameter-shift gradients.
"""

import numpy as np


class QuantumAutoencoder:
    """
    Variational quantum autoencoder.

    Examples:
        >>> ae = QuantumAutoencoder(n_qubits=3, n_trash=1, n_layers=3)
        >>> ae.fit(input_states, epochs=60)      # input_states: (m, 2**n) array
        >>> ae.trash_fidelity(input_states)       # -> close to 1 after training
    """

    def __init__(
        self,
        n_qubits: int,
        n_trash: int,
        n_layers: int = 3,
        learning_rate: float = 0.1,
    ):
        if n_trash >= n_qubits:
            raise ValueError("n_trash must be < n_qubits")
        self.n_qubits = n_qubits
        self.n_trash = n_trash
        self.n_layers = n_layers
        self.learning_rate = learning_rate

        # Trash qubits are the last n_trash qubits.
        self.trash_qubits = list(range(n_qubits - n_trash, n_qubits))
        self.params = np.random.uniform(0, 2 * np.pi, n_layers * n_qubits)
        self.history = {"cost": []}

    def _encoder_circuit(self, params):
        from ...core.circuit import QuantumCircuit

        circuit = QuantumCircuit(self.n_qubits)
        p = 0
        for _ in range(self.n_layers):
            for q in range(self.n_qubits):
                circuit.ry(float(params[p]), q)
                p += 1
            for q in range(self.n_qubits - 1):
                circuit.cnot(q, q + 1)
        return circuit

    def _encoded_state(self, input_sv, params):
        from ...core.quantum_state import QuantumState

        init = QuantumState(self.n_qubits, state_vector=np.asarray(input_sv))
        return (
            self._encoder_circuit(params)
            .get_statevector(initial_state=init)
            .state_vector
        )

    def _trash_prob(self, state_vector) -> float:
        """Average probability that the trash qubits are |1> (0 = perfect)."""
        probs = np.abs(state_vector) ** 2
        indices = np.arange(state_vector.shape[0])
        total = 0.0
        for q in self.trash_qubits:
            total += float(np.sum(probs[((indices >> q) & 1) == 1]))
        return total / len(self.trash_qubits)

    def cost(self, inputs, params=None) -> float:
        params = self.params if params is None else params
        return float(
            np.mean([self._trash_prob(self._encoded_state(x, params)) for x in inputs])
        )

    def trash_fidelity(self, inputs) -> float:
        """1 - average trash-|1> probability (1.0 = trash perfectly reset to |0>)."""
        return 1.0 - self.cost(inputs)

    def fit(self, inputs, epochs: int = 60, verbose: bool = False):
        from ..optimizers.basics import Adam

        inputs = np.asarray(inputs)
        optimizer = Adam(learning_rate=self.learning_rate)
        shift = np.pi / 2

        for epoch in range(epochs):
            base = self.cost(inputs)
            grad = np.zeros_like(self.params)
            for k in range(self.params.shape[0]):
                p_plus = self.params.copy()
                p_plus[k] += shift
                p_minus = self.params.copy()
                p_minus[k] -= shift
                grad[k] = 0.5 * (self.cost(inputs, p_plus) - self.cost(inputs, p_minus))
            self.params = optimizer.step(self.params, grad)

            self.history["cost"].append(base)
            if verbose and (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch + 1}/{epochs} - cost {base:.4f}")

        return self

    def encode(self, input_sv):
        """Return the encoded state vector V(theta)|input>."""
        return self._encoded_state(input_sv, self.params)
