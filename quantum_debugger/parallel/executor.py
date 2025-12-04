"""
Parallel execution for quantum circuits

Enables multi-core parallel execution of shots for faster simulation.
"""

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import Dict, List, Optional, Callable
import os
import multiprocessing as mp


class ParallelExecutor:
    """
    Execute quantum circuits in parallel across multiple cores.
    
    Supports two modes:
    - Thread-based: Fast, shared memory, good for I/O bound
    - Process-based: True parallelism, good for CPU bound
    
    Example:
        >>> executor = ParallelExecutor(n_workers=4, use_processes=True)
        >>> result = executor.run_parallel(circuit, shots=1000)
    """
    
    def __init__(self, n_workers: Optional[int] = None, use_processes: bool = True):
        """
        Initialize parallel executor
        
        Args:
            n_workers: Number of workers (default: CPU count)
            use_processes: Use ProcessPool (True) or ThreadPool (False)
        """
        self.n_workers = n_workers or os.cpu_count() or 4
        self.use_processes = use_processes
        
    def run_parallel(self, circuit, shots: int, progress: bool = False) -> Dict:
        """
        Run circuit with parallel shot execution
        
        Args:
            circuit: QuantumCircuit to execute
            shots: Total number of shots
            progress: Show progress bar (requires tqdm)
            
        Returns:
            Combined results dictionary
        """
        # Split shots across workers
        shots_per_worker = shots // self.n_workers
        remaining_shots = shots % self.n_workers
        
        # Create shot distribution
        shot_distribution = [shots_per_worker] * self.n_workers
        if remaining_shots > 0:
            shot_distribution[0] += remaining_shots
        
        # Execute in parallel
        if self.use_processes:
            return self._run_with_processes(circuit, shot_distribution, progress)
        else:
            return self._run_with_threads(circuit, shot_distribution, progress)
    
    def _run_with_processes(self, circuit, shot_distribution: List[int], progress: bool) -> Dict:
        """Execute with ProcessPoolExecutor"""
        results = []
        
        with ProcessPoolExecutor(max_workers=self.n_workers) as executor:
            # Submit all jobs
            futures = []
            for shots_i in shot_distribution:
                if shots_i > 0:
                    future = executor.submit(self._run_circuit_worker, circuit, shots_i)
                    futures.append(future)
            
            # Collect results
            if progress:
                results = self._collect_with_progress(futures)
            else:
                results = [future.result() for future in futures]
        
        return self._merge_results(results)
    
    def _run_with_threads(self, circuit, shot_distribution: List[int], progress: bool) -> Dict:
        """Execute with ThreadPoolExecutor"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.n_workers) as executor:
            # Submit all jobs
            futures = []
            for shots_i in shot_distribution:
                if shots_i > 0:
                    future = executor.submit(circuit.run, shots_i)
                    futures.append(future)
            
            # Collect results
            if progress:
                results = self._collect_with_progress(futures)
            else:
                results = [future.result() for future in futures]
        
        return self._merge_results(results)
    
    @staticmethod
    def _run_circuit_worker(circuit, shots: int) -> Dict:
        """Worker function for process pool execution"""
        return circuit.run(shots=shots)
    
    def _collect_with_progress(self, futures) -> List[Dict]:
        """Collect results with progress bar"""
        try:
            from tqdm import tqdm
            results = []
            for future in tqdm(as_completed(futures), total=len(futures), desc="Parallel shots"):
                results.append(future.result())
            return results
        except ImportError:
            # tqdm not available, collect without progress
            return [future.result() for future in futures]
    
    def _merge_results(self, results: List[Dict]) -> Dict:
        """Merge results from multiple workers"""
        if not results:
            return {'counts': {}, 'shots': 0}
        
        # Merge counts
        merged_counts = {}
        total_shots = 0
        
        for result in results:
            counts = result.get('counts', {})
            total_shots += result.get('shots', 0)
            
            for outcome, count in counts.items():
                merged_counts[outcome] = merged_counts.get(outcome, 0) + count
        
        return {
            'counts': merged_counts,
            'shots': total_shots,
            'parallel_workers': self.n_workers
        }


def run_parallel(circuit, shots: int = 1000, n_workers: Optional[int] = None, 
                 use_processes: bool = True, progress: bool = False) -> Dict:
    """
    Convenience function for parallel execution
    
    Args:
        circuit: QuantumCircuit to execute
        shots: Total number of shots
        n_workers: Number of parallel workers (default: CPU count)
        use_processes: Use processes (True) or threads (False)
        progress: Show progress bar
        
    Returns:
        Results dictionary with counts
        
    Example:
        >>> from quantum_debugger.parallel import run_parallel
        >>> result = run_parallel(circuit, shots=10000, n_workers=4)
    """
    executor = ParallelExecutor(n_workers, use_processes)
    return executor.run_parallel(circuit, shots, progress)
