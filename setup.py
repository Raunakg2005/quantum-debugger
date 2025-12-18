from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="quantum-debugger",
    version="0.4.0",
    author="warlord9004",
    author_email="your.email@example.com",
    description="Interactive quantum circuit debugger and Quantum Machine Learning library with VQE, QAOA, and parameterized gates",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Raunakg2005/quantum-debugger",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Physics",
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
        "qiskit": ["qiskit>=2.0.0"],
        "cirq": ["cirq>=1.0.0"],
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
