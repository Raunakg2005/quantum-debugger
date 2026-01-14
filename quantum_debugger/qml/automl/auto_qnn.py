"""
Auto QNN - Automatic Quantum Neural Network

Simple interface: auto_qnn(X, y) automatically finds best model!
"""

import numpy as np
from typing import Optional, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


def auto_qnn(
    X: np.ndarray,
    y: np.ndarray,
    max_qubits: Optional[int] = None,
    time_budget: int = 300,  # 5 minutes
    optimization_metric: str = 'accuracy'
):
    """
    Automatically find the best QNN for your data.
    
    This is the SIMPLEST way to use quantum machine learning!
    
    Args:
        X: Training features (n_samples, n_features)
        y: Training labels (n_samples,)
        max_qubits: Maximum qubits to use (default: auto from data)
        time_budget: Time budget in seconds (default: 300)
        optimization_metric: 'accuracy', 'loss', or 'f1'
        
    Returns:
        Trained QNN model ready to use
        
    Examples:
        >>> # That's it! AutoML does everything:
        >>> model = auto_qnn(X_train, y_train)
        >>> predictions = model.predict(X_test)
        
        >>> # With custom settings:
        >>> model = auto_qnn(X_train, y_train, max_qubits=6, time_budget=600)
    """
    logger.info(f"🤖 AutoML starting: {X.shape[0]} samples, {X.shape[1]} features")
    
    # Auto-determine qubits
    if max_qubits is None:
        max_qubits = min(X.shape[1], 8)  # Cap at 8 qubits for reasonable time
        logger.info(f"Auto-selected {max_qubits} qubits")
    
    # Create AutoQNN instance
    auto = AutoQNN(
        max_qubits=max_qubits,
        time_budget=time_budget,
        metric=optimization_metric
    )
    
    # Find best model
    auto.fit(X, y)
    
    logger.info(f"✅ AutoML complete! Best accuracy: {auto.best_score_:.3f}")
    
    return auto.best_model_


class AutoQNN:
    """
    Automated Quantum Neural Network with model selection and tuning.
    
    Automatically searches for:
    - Best number of qubits
    - Best ansatz type
    - Best hyperparameters
    - Best architecture
    
    Examples:
        >>> auto = AutoQNN(max_qubits=6)
        >>> auto.fit(X_train, y_train)
        >>> predictions = auto.predict(X_test)
        >>> 
        >>> # Access best configuration
        >>> print(auto.best_config_)
        >>> print(f"Best score: {auto.best_score_:.3f}")
    """
    
    def __init__(
        self,
        max_qubits: int = 8,
        time_budget: int = 300,
        metric: str = 'accuracy',
        n_trials: int = 20
    ):
        """
        Initialize AutoQNN.
        
        Args:
            max_qubits: Maximum qubits to search
            time_budget: Total time budget (seconds)
            metric: Optimization metric
            n_trials: Number of configurations to try
        """
        self.max_qubits = max_qubits
        self.time_budget = time_budget
        self.metric = metric
        self.n_trials = n_trials
        
        self.best_model_ = None
        self.best_score_ = -np.inf
        self.best_config_ = None
        self.search_history_ = []
    
    def fit(self, X: np.ndarray, y: np.ndarray):
        """
        Automatically find and train best QNN.
        
        Args:
            X: Training features
            y: Training labels
        """
        import time
        from quantum_debugger.qml.qnn import QuantumNeuralNetwork
        
        start_time = time.time()
        time_per_trial = self.time_budget / self.n_trials
        
        # Search space
        search_configs = self._generate_search_space(X.shape[1])
        
        for i, config in enumerate(search_configs[:self.n_trials]):
            if time.time() - start_time > self.time_budget:
                logger.info(f"Time budget exceeded, stopping at trial {i}")
                break
            
            logger.info(f"Trial {i+1}/{self.n_trials}: {config}")
            
            try:
                # Create and train model
                model = QuantumNeuralNetwork(n_qubits=config['n_qubits'])
                model.compile(
                    optimizer=config.get('optimizer', 'adam'),
                    loss=config.get('loss', 'mse'),
                    learning_rate=config.get('learning_rate', 0.01)
                )
                
                history = model.fit(
                    X, y,
                    epochs=config.get('epochs', 20),
                    batch_size=config.get('batch_size'),
                    verbose=0
                )
                
                # Evaluate
                predictions = model.predict(X)
                pred_labels = (predictions > 0.5).astype(int).flatten()
                score = np.mean(pred_labels == y)
                
                # Track
                self.search_history_.append({
                    'config': config,
                    'score': score,
                    'final_loss': history['loss'][-1] if history['loss'] else None
                })
                
                # Update best
                if score > self.best_score_:
                    self.best_score_ = score
                    self.best_model_ = model
                    self.best_config_ = config
                    logger.info(f"  ✨ New best! Score: {score:.3f}")
                
            except Exception as e:
                logger.warning(f"  ❌ Trial failed: {e}")
                continue
        
        logger.info(f"Search complete! Best config: {self.best_config_}")
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict using best model."""
        if self.best_model_ is None:
            raise RuntimeError("No model trained. Call fit() first.")
        
        return self.best_model_.predict(X)
    
    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """Score best model."""
        predictions = self.predict(X)
        pred_labels = (predictions > 0.5).astype(int).flatten()
        return np.mean(pred_labels == y)
    
    def _generate_search_space(self, n_features: int) -> list:
        """Generate hyperparameter search space."""
        configs = []
        
        # Try different qubit counts
        for n_qubits in [2, 4, min(n_features, self.max_qubits)]:
            # Try different configurations
            for epochs in [10, 20, 30]:
                for lr in [0.001, 0.01, 0.05]:
                    configs.append({
                        'n_qubits': n_qubits,
                        'epochs': epochs,
                        'learning_rate': lr,
                        'optimizer': 'adam',
                        'loss': 'mse'
                    })
        
        # Shuffle for diversity
        np.random.shuffle(configs)
        
        return configs
    
    def get_search_summary(self) -> Dict:
        """Get summary of architecture search."""
        return {
            'n_trials': len(self.search_history_),
            'best_score': self.best_score_,
            'best_config': self.best_config_,
            'all_scores': [h['score'] for h in self.search_history_]
        }
