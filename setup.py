from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="quantum-debugger",
    version="0.1.1",
    author="warlord9004",  # Update with your real name if desired
    author_email="your.email@example.com",  # Add your email
    description="Interactive debugger and profiler for quantum circuits",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/quantum-debugger",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Software Development :: Debuggers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "matplotlib>=3.5.0",
        "scipy>=1.7.0",
    ],
    extras_require={
        "qiskit": ["qiskit>=0.39.0"],
        "cirq": ["cirq>=1.0.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "sphinx>=4.5.0",
        ],
    },
    keywords="quantum computing debugging profiling quantum-circuit visualization",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/quantum-debugger/issues",
        "Source": "https://github.com/yourusername/quantum-debugger",
        "Documentation": "https://quantum-debugger.readthedocs.io",
    },
)
