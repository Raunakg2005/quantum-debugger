"""
Hyperparameter Tuning

Automatic hyperparameter optimization for quantum models.
"""

import numpy as np
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class HyperparameterTuner:
    """
    Automatic hyperparameter tuning for QNN.
    
    Uses random search or grid search to find optimal parameters.
    
    Examples:
        >>> tuner = HyperparameterTuner()
        >>> best_params = tuner.tune(X_train, y_train, n_qubits=4)
        >>> print(f"Best learning rate: {best_params['learning_rate']}")
    """
    
    def __init__(
        self,
        param_space: Optional[Dict] = None,
        n_trials: int = 20,
        method: str = 'random'
    ):
        """
        Initialize hyperparameter tuner.
        
        Args:
            param_space: Parameter search space
            n_trials: Number of configurations to try
            method: 'random' or 'grid'
        """
        self.param_space = param_space or self._default_param_space()
        self.n_trials = n_trials
        self.method = method
        
        self.best_params_ = None
        self.best_score_ = -np.inf
        self.trials_ = []
    
    def _default_param_space(self) -> Dict:
        """Default hyperparameter search space."""
        return {
            'learning_rate': [0.001, 0.01, 0.05, 0.1],
            'epochs': [10, 20, 30, 50],
            'batch_size': [None, 16, 32],
            'optimizer': ['adam', 'sgd']
        }
    
    def tune(
        self,
        X: np.ndarray,
        y: np.ndarray,
        n_qubits: int
    ) -> Dict[str, Any]:
        """
        Find best hyperparameters.
        
        Args:
            X: Training features
            y: Training labels
            n_qubits: Number of qubits
            
        Returns:
            Best hyperparameters dictionary
        """
        from quantum_debugger.qml.qnn import QuantumNeuralNetwork
        
        logger.info(f"Starting hyperparameter tuning ({self.n_trials} trials)")
        
        # Generate configurations
        configs = self._generate_configs()
        
        for i, config in enumerate(configs[:self.n_trials]):
            logger.info(f"Trial {i+1}/{self.n_trials}: {config}")
            
            try:
                # Create model
                model = QuantumNeuralNetwork(n_qubits=n_qubits)
                model.compile(
                    optimizer=config['optimizer'],
                    loss='mse',
                    learning_rate=config['learning_rate']
                )
                
                # Train
                history = model.fit(
                    X, y,
                    epochs=config['epochs'],
                    batch_size=config['batch_size'],
                    verbose=0
                )
                
                # Evaluate
                predictions = model.predict(X)
                pred_labels = (predictions > 0.5).astype(int).flatten()
                score = np.mean(pred_labels == y)
                
                # Track trial
                self.trials_.append({
                    'params': config,
                    'score': score,
                    'loss': history['loss'][-1] if history['loss'] else None
                })
                
                # Update best
                if score > self.best_score_:
                    self.best_score_ = score
                    self.best_params_ = config
                    logger.info(f"  ✨ New best! Score: {score:.3f}")
                    
            except Exception as e:
                logger.warning(f"  ❌ Trial failed: {e}")
                continue
        
        logger.info(f"Tuning complete! Best parameters: {self.best_params_}")
        
        return self.best_params_
    
    def _generate_configs(self) -> List[Dict]:
        """Generate hyperparameter configurations."""
        if self.method == 'grid':
            return self._grid_search_configs()
        else:
            return self._random_search_configs()
    
    def _random_search_configs(self) -> List[Dict]:
        """Generate random search configurations."""
        configs = []
        
        for _ in range(self.n_trials * 2):  # Generate extras
            config = {}
            for param_name, param_values in self.param_space.items():
                config[param_name] = np.random.choice(param_values)
            configs.append(config)
        
        return configs
    
    def _grid_search_configs(self) -> List[Dict]:
        """Generate grid search configurations."""
        import itertools
        
        keys = list(self.param_space.keys())
        values = [self.param_space[k] for k in keys]
        
        configs = []
        for combo in itertools.product(*values):
            configs.append(dict(zip(keys, combo)))
        
        return configs
    
    def get_results(self) -> Dict:
        """Get tuning results."""
        return {
            'best_params': self.best_params_,
            'best_score': self.best_score_,
            'n_trials': len(self.trials_),
            'all_scores': [t['score'] for t in self.trials_]
        }


def tune_hyperparameters(
    X: np.ndarray,
    y: np.ndarray,
    n_qubits: int,
    n_trials: int = 15
) -> Dict:
    """
    Quick hyperparameter tuning.
    
    Args:
        X: Training data
        y: Labels  
        n_qubits: Number of qubits
        n_trials: Number of trials
        
    Returns:
        Best hyperparameters
        
    Examples:
        >>> params = tune_hyperparameters(X, y, n_qubits=4)
        >>> # Use params to create optimized model
    """
    tuner = HyperparameterTuner(n_trials=n_trials)
    return tuner.tune(X, y, n_qubits)
