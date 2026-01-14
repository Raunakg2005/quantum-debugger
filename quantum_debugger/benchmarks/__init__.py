"""
Benchmarking Suite

Performance benchmarking and comparison tools for quantum machine learning.

Features:
- QML vs Classical ML comparison
- Circuit optimization benchmarks
- Scalability analysis
- Performance reporting
"""

from .qml_benchmarks import (
    benchmark_qnn,
    benchmark_qsvm,
    compare_with_classical,
    benchmark_suite
)

from .optimization_benchmarks import (
    benchmark_optimization,
    benchmark_transpilation,
    measure_speedup,
    optimization_comparison_suite
)

from .scalability_benchmarks import (
    scalability_analysis,
    parallel_benchmark,
    memory_profiling
)

from .report_generator import (
    generate_benchmark_report,
    plot_results,
    save_results_json
)

__all__ = [
    # QML benchmarks
    'benchmark_qnn',
    'benchmark_qsvm',
    'compare_with_classical',
    'benchmark_suite',
    
    # Optimization
    'benchmark_optimization',
    'benchmark_transpilation',
    'measure_speedup',
    'optimization_comparison_suite',
    
    # Scalability
    'scalability_analysis',
    'parallel_benchmark',
    'memory_profiling',
    
    # Reporting
    'generate_benchmark_report',
    'plot_results',
    'save_results_json'
]
