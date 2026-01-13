"""
PyTorch integration for quantum layers - simplified version
"""

import numpy as np
from typing import Optional, List

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch.autograd import Function
    HAS_PYTORCH = True
except ImportError:
    HAS_PYTORCH = False
    # Dummy classes when PyTorch not available
    class nn:
        class Module:
            pass
        class Parameter:
            pass

from .layers import QuantumMiddleLayer


if HAS_PYTORCH:
    class QuantumFunction(Function):
        """Custom autograd function for quantum circuits"""
        
        @staticmethod
        def forward(ctx, inputs, quantum_params, quantum_layer):
            ctx.save_for_backward(inputs, quantum_params)
            ctx.quantum_layer = quantum_layer
            
            inputs_np = inputs.detach().cpu().numpy()
            params_np = quantum_params.detach().cpu().numpy()
            
            quantum_layer.quantum_params = params_np
            outputs_np = quantum_layer.forward(inputs_np)
            
            outputs = torch.from_numpy(outputs_np).float()
            if inputs.is_cuda:
                outputs = outputs.cuda()
            
            return outputs
        
        @staticmethod
        def backward(ctx, grad_output):
            inputs, quantum_params = ctx.saved_tensors
            quantum_layer = ctx.quantum_layer
            
            inputs_np = inputs.detach().cpu().numpy()
            params_np = quantum_params.detach().cpu().numpy()
            grad_output_np = grad_output.detach().cpu().numpy()
            
            # Simplified gradient (could use parameter shift rule)
            param_grads = np.zeros_like(params_np)
            param_grads_tensor = torch.from_numpy(param_grads).float()
            if inputs.is_cuda:
                param_grads_tensor = param_grads_tensor.cuda()
            
            return None, param_grads_tensor, None


    class QuantumTorchLayer(nn.Module):
        """PyTorch-compatible quantum layer"""
        
        def __init__(
            self,
            n_qubits: int,
            encoding_type: str = 'angle',
            ansatz_type: str = 'real_amplitudes',
            ansatz_reps: int = 2,
            output_dim: Optional[int] = None
        ):
            super().__init__()
            
            self.n_qubits = n_qubits
            self.encoding_type = encoding_type
            self.ansatz_type = ansatz_type
            self.ansatz_reps = ansatz_reps
            self.output_dim = output_dim or n_qubits
            
            self.quantum_layer = QuantumMiddleLayer(
                n_qubits=n_qubits,
                encoding_type=encoding_type,
                ansatz_type=ansatz_type,
                ansatz_reps=ansatz_reps
            )
            
            n_params = len(self.quantum_layer.quantum_params)
            self.quantum_weights = nn.Parameter(
                torch.from_numpy(self.quantum_layer.quantum_params).float()
            )
        
        def forward(self, x):
            outputs = QuantumFunction.apply(x, self.quantum_weights, self.quantum_layer)
            
            if outputs.shape[-1] != self.output_dim:
                outputs = outputs[:, :self.output_dim]
            
            return outputs


    class HybridQNN(nn.Module):
        """Complete hybrid quantum-classical neural network"""
        
        def __init__(
            self,
            input_dim: int,
            output_dim: int,
            n_qubits: int = 4,
            classical_hidden_pre: List[int] = None,
            classical_hidden_post: List[int] = None,
            quantum_ansatz: str = 'real_amplitudes',
            quantum_reps: int = 2,
            activation: str = 'relu',
            output_activation: str = 'softmax',
            dropout_rate: float = 0.0
        ):
            super().__init__()
            
            self.output_activation = output_activation
            classical_hidden_pre = classical_hidden_pre or []
            classical_hidden_post = classical_hidden_post or []
            
            # Classical preprocessing
            pre_layers = []
            prev_dim = input_dim
            
            for hidden_dim in classical_hidden_pre:
                pre_layers.append(nn.Linear(prev_dim, hidden_dim))
                pre_layers.append(nn.ReLU())
                if dropout_rate > 0:
                    pre_layers.append(nn.Dropout(dropout_rate))
                prev_dim = hidden_dim
            
            if prev_dim != n_qubits:
                pre_layers.append(nn.Linear(prev_dim, n_qubits))
            
            self.classical_pre = nn.Sequential(*pre_layers) if pre_layers else nn.Identity()
            
            # Quantum layer
            self.quantum_layer = QuantumTorchLayer(
                n_qubits=n_qubits,
                ansatz_type=quantum_ansatz,
                ansatz_reps=quantum_reps
            )
            
            # Classical postprocessing
            post_layers = []
            prev_dim = n_qubits
            
            for hidden_dim in classical_hidden_post:
                post_layers.append(nn.Linear(prev_dim, hidden_dim))
                post_layers.append(nn.ReLU())
                if dropout_rate > 0:
                    post_layers.append(nn.Dropout(dropout_rate))
                prev_dim = hidden_dim
            
            post_layers.append(nn.Linear(prev_dim, output_dim))
            self.classical_post = nn.Sequential(*post_layers)
        
        def forward(self, x):
            x = self.classical_pre(x)
            x = self.quantum_layer(x)
            x = self.classical_post(x)
            
            if self.output_activation == 'softmax':
                x = F.softmax(x, dim=1)
            elif self.output_activation == 'sigmoid':
                x = torch.sigmoid(x)
            
            return x
else:
    # Dummy classes when PyTorch not available
    class QuantumTorchLayer:
        def __init__(self, *args, **kwargs):
            raise ImportError("PyTorch is required. Install with: pip install torch")
    
    class HybridQNN:
        def __init__(self, *args, **kwargs):
            raise ImportError("PyTorch is required. Install with: pip install torch")


def create_hybrid_pytorch_model(
    input_dim: int,
    output_dim: int,
    n_qubits: int = 4,
    **kwargs
):
    """Create a hybrid quantum-classical PyTorch model"""
    if not HAS_PYTORCH:
        raise ImportError("PyTorch is required")
    
    return HybridQNN(
        input_dim=input_dim,
        output_dim=output_dim,
        n_qubits=n_qubits,
        **kwargs
    )
