"""
Quantum Training Module
=======================

Training loops and utilities for quantum machine learning.
"""

import numpy as np
from typing import Callable, Dict, List, Optional
from ..optimizers import get_optimizer
from ..utils.gradients import compute_gradients
import logging

logger = logging.getLogger(__name__)


class QuantumTrainer:
    """
    Training framework for parameterized quantum circuits.
    
    Handles the training loop, gradient computation, optimization,
    and tracking of training metrics.
    
    Examples:
        >>> from quantum_debugger.qml.training import QuantumTrainer
        >>> 
        >>> def circuit(params): ...
        >>> def cost(circuit): ...
        >>> 
        >>> trainer = QuantumTrainer(
        ...     circuit_builder=circuit,
        ...     cost_function=cost,
        ...     optimizer='adam',
        ...     learning_rate=0.01
        ... )
        >>> result = trainer.train(initial_params, epochs=100)
    """
    
    def __init__(
        self,
        circuit_builder: Callable,
        cost_function: Callable,
        optimizer: str = 'adam',
        learning_rate: float = 0.01,
        gradient_method: str = 'parameter_shift'
    ):
        """
        Initialize trainer.
        
        Args:
            circuit_builder: Function(params) -> circuit
            cost_function: Function(circuit) -> cost
            optimizer: Optimizer name ('adam', 'sgd', 'spsa')
            learning_rate: Learning rate
            gradient_method: 'parameter_shift' or 'finite_difference'
        """
        self.circuit_builder = circuit_builder
        self.cost_function = cost_function
        self.optimizer = get_optimizer(optimizer, learning_rate=learning_rate)
        self.gradient_method = gradient_method
        self.history = []
        
        logger.info(f"Trainer initialized: optimizer={optimizer}, lr={learning_rate}")
    
    def train(
        self,
        initial_params: np.ndarray,
        epochs: int = 100,
        callback: Optional[Callable] = None,
        verbose: bool = True
    ) -> Dict:
        """
        Train the quantum circuit.
        
        Args:
            initial_params: Starting parameter values
            epochs: Number of training epochs
            callback: Optional callback function(epoch, loss, params)
            verbose: Print progress
            
        Returns:
            Training results dictionary
        """
        params = initial_params.copy()
        self.history = []
        
        logger.info(f"Starting training: {epochs} epochs")
        
        for epoch in range(epochs):
            # Forward pass
            circuit = self.circuit_builder(params)
            loss = self.cost_function(circuit)
            
            # Compute gradients
            gradients = compute_gradients(
                self.circuit_builder,
                self.cost_function,
                params,
                method=self.gradient_method
            )
            
            # Optimization step
            params = self.optimizer.step(params, gradients)
            
            # Track history
            self.history.append({
                'epoch': epoch,
                'loss': loss,
                'params': params.copy(),
                'gradients': gradients.copy(),
                'grad_norm': np.linalg.norm(gradients)
            })
            
            # Logging
            if verbose and (epoch % 10 == 0 or epoch == epochs - 1):
                logger.info(f"Epoch {epoch}: loss={loss:.6f}, |∇|={np.linalg.norm(gradients):.6f}")
            
            # Callback
            if callback is not None:
                callback(epoch, loss, params)
        
        final_loss = self.history[-1]['loss']
        logger.info(f"Training complete: final loss={final_loss:.6f}")
        
        return {
            'final_params': params,
            'final_loss': final_loss,
            'epochs': epochs,
            'history': self.history
        }
    
    def get_loss_history(self) -> List[float]:
        """Get list of loss values from training history"""
        return [h['loss'] for h in self.history]
    
    def get_gradient_norms(self) -> List[float]:
        """Get list of gradient norms from training"""
        return [h['grad_norm'] for h in self.history]
