"""
GPU Backend for Quantum Circuit Simulation

Provides GPU-accelerated quantum state vector operations using CuPy.
Falls back gracefully to CPU (NumPy) if GPU is not available.
"""

import numpy as np
from typing import Optional, Union
import warnings


class GPUBackend:
    """
    GPU-accelerated backend for quantum simulations.
    
    Automatically detects GPU availability and falls back to CPU if needed.
    Uses CuPy for GPU operations when available.
    """
    
    def __init__(self, device: Optional[str] = None):
        """
        Initialize GPU backend.
        
        Args:
            device: GPU device ('cuda:0', 'cuda:1', etc.) or None for auto-detect
        """
        self.device = device
        self.use_gpu = False
        self.xp = np  # Default to NumPy
        
        # Try to import and initialize CuPy with CUDA
        try:
            import cupy as cp
            self.cp = cp
            
            # Test CUDA is actually working (catches missing DLL errors)
            try:
                test_arr = cp.array([1.0])
                _ = cp.asnumpy(test_arr)
                self.use_gpu = True
                self.xp = cp
            except Exception as cuda_err:
                # CUDA runtime error - fall back to CPU
                warnings.warn(
                    f"CuPy installed but CUDA unavailable ({cuda_err}). Using CPU.",
                    UserWarning
                )
                self.use_gpu = False
                self.xp = np
                self.device_name = "CPU (CUDA error)"
                self.device_memory = None
                return
            
            if device:
                # Set specific device
                device_id = int(device.split(':')[1]) if ':' in device else 0
                cp.cuda.Device(device_id).use()
            
            # Get device info (compatible with different CuPy versions)
            try:
                dev = cp.cuda.Device()
                self.device_name = f"GPU (CUDA Device {dev.id})"
                mem_info = dev.mem_info
                self.device_memory = mem_info[1] / (1024**3)  # Total memory in GB
            except:
                self.device_name = "GPU (CuPy)"
                self.device_memory = None
            
        except ImportError:
            warnings.warn(
                "CuPy not available. Using CPU (NumPy) backend. "
                "Install CuPy for GPU acceleration: pip install cupy-cuda11x",
                UserWarning
            )
            self.device_name = "CPU"
            self.device_memory = None
    
    def allocate_state(self, n_qubits: int) -> Union[np.ndarray, 'cp.ndarray']:
        """
        Allocate quantum state vector.
        
        Args:
            n_qubits: Number of qubits
            
        Returns:
            State vector on GPU or CPU
        """
        dim = 2 ** n_qubits
        state = self.xp.zeros(dim, dtype=complex)
        state[0] = 1.0  # Initialize to |0...0⟩
        return state
    
    def to_gpu(self, array: np.ndarray):
        """Move array to GPU"""
        if self.use_gpu:
            return self.cp.asarray(array)
        return array
    
    def to_cpu(self, array: Union[np.ndarray, 'cp.ndarray']) -> np.ndarray:
        """Move array to CPU"""
        if self.use_gpu and isinstance(array, self.cp.ndarray):
            return self.cp.asnumpy(array)
        return np.asarray(array)
    
    def kron(self, a, b):
        """Kronecker product"""
        return self.xp.kron(a, b)
    
    def dot(self, a, b):
        """Matrix multiplication"""
        return self.xp.dot(a, b)
    
    def matmul(self, a, b):
        """Matrix multiplication (alternative)"""
        return self.xp.matmul(a, b)
    
    def apply_gate(self, state, gate_matrix, qubits):
        """
        Apply quantum gate to state vector.
        
        Args:
            state: Current state vector
            gate_matrix: Gate matrix
            qubits: Target qubit indices
            
        Returns:
            New state vector
        """
        # Ensure gate matrix is on correct device
        gate = self.to_gpu(gate_matrix) if not isinstance(gate_matrix, type(state)) else gate_matrix
        
        # For single-qubit gates, use efficient indexing
        if len(qubits) == 1:
            return self._apply_single_qubit_gate(state, gate, qubits[0])
        elif len(qubits) == 2:
            return self._apply_two_qubit_gate(state, gate, qubits)
        else:
            # General multi-qubit gate
            return self._apply_general_gate(state, gate, qubits)
    
    def _apply_single_qubit_gate(self, state, gate, qubit):
        """Optimized single-qubit gate application"""
        n_qubits = int(self.xp.log2(len(state)))
        
        # Create full gate matrix
        if qubit == 0:
            full_gate = gate
            for i in range(1, n_qubits):
                full_gate = self.kron(full_gate, self.xp.eye(2))
        else:
            full_gate = self.xp.eye(2)
            for i in range(1, qubit):
                full_gate = self.kron(full_gate, self.xp.eye(2))
            full_gate = self.kron(full_gate, gate)
            for i in range(qubit + 1, n_qubits):
                full_gate = self.kron(full_gate, self.xp.eye(2))
        
        return self.dot(full_gate, state)
    
    def _apply_two_qubit_gate(self, state, gate, qubits):
        """Two-qubit gate application"""
        n_qubits = int(self.xp.log2(len(state)))
        
        # Build full unitary
        full_gate = self.xp.eye(1, dtype=complex)
        
        for i in range(n_qubits):
            if i in qubits:
                if i == qubits[0]:
                    # First qubit of the gate
                    if len(full_gate.shape) == 1 or full_gate.shape[0] == 1:
                        full_gate = gate
                    else:
                        full_gate = self.kron(full_gate, gate[0:2, 0:2])
                # Skip second qubit
            else:
                # Identity for uninvolved qubits
                if len(full_gate.shape) == 1 or full_gate.shape[0] == 1:
                    full_gate = self.xp.eye(2, dtype=complex)
                else:
                    full_gate = self.kron(full_gate, self.xp.eye(2, dtype=complex))
        
        return self.dot(full_gate, state)
    
    def _apply_general_gate(self, state, gate, qubits):
        """General multi-qubit gate application"""
        n_qubits = int(self.xp.log2(len(state)))
        dim = 2 ** n_qubits
        
        # Create full unitary operator
        full_unitary = self.xp.eye(dim, dtype=complex)
        
        # This is a simplified approach - for production, would use tensor contraction
        return self.dot(gate, state)
    
    def get_info(self) -> dict:
        """Get backend information"""
        return {
            'backend': 'GPU' if self.use_gpu else 'CPU',
            'library': 'CuPy' if self.use_gpu else 'NumPy',
            'device': self.device_name,
            'memory_gb': self.device_memory,
            'available': self.use_gpu
        }
    
    def synchronize(self):
        """Synchronize GPU operations"""
        if self.use_gpu:
            self.cp.cuda.Stream.null.synchronize()
    
    def __repr__(self):
        if self.use_gpu:
            return f"GPUBackend(device={self.device_name}, memory={self.device_memory:.1f}GB)"
        else:
            return "GPUBackend(CPU fallback)"


def get_optimal_backend(n_qubits: int, prefer_gpu: bool = True) -> GPUBackend:
    """
    Get optimal backend based on problem size.
    
    Args:
        n_qubits: Number of qubits
        prefer_gpu: Whether to prefer GPU if available
        
    Returns:
        Optimal backend instance
    """
    backend = GPUBackend()
    
    # For small circuits, CPU might be faster due to overhead
    if n_qubits < 10 and backend.use_gpu and not prefer_gpu:
        # Force CPU for small circuits
        backend.use_gpu = False
        backend.xp = np
        backend.device_name = "CPU (optimal for <10 qubits)"
    
    return backend


def benchmark_backends(n_qubits_list: list = None) -> dict:
    """
    Benchmark CPU vs GPU performance.
    
    Args:
        n_qubits_list: List of qubit counts to test
        
    Returns:
        Benchmark results
    """
    if n_qubits_list is None:
        n_qubits_list = [5, 10, 12, 15]
    
    results = {}
    
    for n_qubits in n_qubits_list:
        # Skip if too large
        if n_qubits > 20:
            continue
        
        import time
        
        # CPU benchmark
        cpu_backend = GPUBackend()
        cpu_backend.use_gpu = False
        cpu_backend.xp = np
        
        state_cpu = cpu_backend.allocate_state(n_qubits)
        gate = np.array([[0, 1], [1, 0]], dtype=complex)  # X gate
        
        start = time.time()
        for _ in range(10):
            state_cpu = cpu_backend._apply_single_qubit_gate(state_cpu, gate, 0)
        cpu_time = time.time() - start
        
        # GPU benchmark (if available)
        gpu_time = None
        if GPUBackend().use_gpu:
            gpu_backend = GPUBackend()
            state_gpu = gpu_backend.allocate_state(n_qubits)
            gate_gpu = gpu_backend.to_gpu(gate)
            
            start = time.time()
            for _ in range(10):
                state_gpu = gpu_backend._apply_single_qubit_gate(state_gpu, gate_gpu, 0)
            gpu_backend.synchronize()
            gpu_time = time.time() - start
        
        results[n_qubits] = {
            'cpu_time': cpu_time,
            'gpu_time': gpu_time,
            'speedup': cpu_time / gpu_time if gpu_time else None
        }
    
    return results
