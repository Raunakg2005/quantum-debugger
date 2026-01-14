from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="quantum-debugger",
    version="0.6.0",
    author="Raunak Kumar Gupta",
    author_email="raunak.gupta@somaiya.edu",
    description="Comprehensive quantum machine learning library with AutoML, GPU acceleration, advanced algorithms (QGANs, Quantum RL), transfer learning, and multi-framework support (Qiskit, PennyLane, Cirq, TensorFlow, PyTorch)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Raunakg2005/quantum-debugger",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Debuggers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "matplotlib>=3.5.0",
    ],
    extras_require={
        # Framework integrations
        "qiskit": ["qiskit>=1.0.0"],
        "pennylane": ["pennylane>=0.30.0"],
        "cirq": ["cirq>=1.0.0"],
        "tensorflow": ["tensorflow>=2.10.0"],
        "pytorch": ["torch>=1.13.0"],
        
        # Hardware backends (require user API keys)
        "ibm": ["qiskit-ibm-runtime>=0.15.0"],  # FREE tier available
        "aws": ["amazon-braket-sdk>=1.50.0", "boto3>=1.28.0"],  # PAID service
        
        # All frameworks
        "all": [
            "qiskit>=1.0.0",
            "pennylane>=0.30.0",
            "cirq>=1.0.0",
            "tensorflow>=2.10.0",
            "torch>=1.13.0",
            "scikit-learn>=1.0.0",
            "qiskit-ibm-runtime>=0.15.0",
            "amazon-braket-sdk>=1.50.0"
        ],
        
        # Development
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.990",
        ],
    },
    keywords="quantum computing debugging profiling quantum-circuit visualization qml vqe qaoa machine-learning",
    project_urls={
        "Bug Reports": "https://github.com/Raunakg2005/quantum-debugger/issues",
        "Source": "https://github.com/Raunakg2005/quantum-debugger",
        "Documentation": "https://github.com/Raunakg2005/quantum-debugger#readme",
    },
)
