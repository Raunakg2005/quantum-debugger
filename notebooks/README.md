# Quantum Debugger - Jupyter Notebooks

Comprehensive interactive examples demonstrating quantum-debugger features.

## Available Notebooks

### 1. Quickstart: AutoML (01_quickstart_automl.ipynb)
**Time:** 5-10 minutes  
**Level:** Beginner

Learn quantum ML in 60 seconds with one-line AutoML.

**Topics:**
- Installation
- Data preparation
- auto_qnn() usage
- Predictions and evaluation
- Results visualization

**Use when:** You're new to quantum ML and want the easiest start.

---

### 2. Transfer Learning Guide (02_transfer_learning_guide.ipynb)
**Time:** 15-20 minutes  
**Level:** Intermediate

Fine-tune pretrained quantum models on your data.

**Topics:**
- Loading pretrained models
- Model zoo exploration
- Layer freezing
- Fine-tuning workflows
- Saving custom models

**Use when:** You want to save training time with pretrained models.

---

### 3. Hardware Deployment (03_hardware_deployment.ipynb)
**Time:** 20-30 minutes  
**Level:** Advanced

Run quantum circuits on real quantum computers.

**Topics:**
- IBM Quantum setup (FREE)
- Circuit optimization for hardware
- Error mitigation
- Real QPU execution
- Results analysis

**Use when:** You're ready to move beyond simulation.

---

### 4. Advanced Optimization (04_advanced_optimization.ipynb)
**Time:** 15-20 minutes  
**Level:** Intermediate

Master circuit optimization techniques.

**Topics:**
- Gate reduction
- Multi-level compilation
- Hardware transpilation
- Custom optimization passes
- Performance benchmarks

**Use when:** You need to optimize circuit performance.

---

### 5. Benchmarking: QML vs Classical (05_benchmarking_qml_vs_classical.ipynb)
**Time:** 20-25 minutes  
**Level:** Intermediate

Compare quantum and classical machine learning.

**Topics:**
- Dataset preparation
- QML and classical training
- Performance comparison
- Scalability analysis
- Decision guidelines

**Use when:** You want to understand when quantum provides advantages.

---

## Quick Start

### Run Locally

```bash
# Install Jupyter
pip install jupyter

# Install quantum-debugger
pip install quantum-debugger

# Start Jupyter
jupyter notebook

# Open any .ipynb file
```

### Run on Google Colab

1. Upload notebook to Google Drive
2. Open with Google Colab
3. Run cells sequentially

**Note:** Install quantum-debugger in first cell:
```python
!pip install quantum-debugger
```

---

## Requirements

### Basic Requirements

```bash
pip install quantum-debugger jupyter matplotlib seaborn scikit-learn
```

### Optional (for specific notebooks)

```bash
# Hardware deployment (Notebook 3)
pip install quantum-debugger[ibm]  # FREE tier

# Framework comparisons
pip install quantum-debugger[all]
```

---

## Notebook Features

All notebooks include:
- Clear explanations
- Runnable code cells
- Visualization examples
- Exercise suggestions
- Further reading links

---

## Data

Sample datasets are in `data/` directory:
- Iris dataset (classification)
- Synthetic quantum data
- Benchmark datasets

---

## Troubleshooting

**Import errors:**
```bash
pip install -e ../  # Install from parent directory
```

**Kernel issues:**
```bash
python -m ipykernel install --user --name quantum-env
```

**GPU warnings:**
```python
# GPU is optional, notebooks work fine on CPU
```

---

## Next Steps

After completing notebooks:
1. Try with your own data
2. Explore [documentation](../README.md)
3. Check [V0.6.0 features](../V06_FEATURES.md)
4. Join discussions on [GitHub](https://github.com/Raunakg2005/quantum-debugger)

---

**Version:** v0.6.0  
**Last Updated:** January 14, 2026  
**Difficulty:** Beginner to Advanced
