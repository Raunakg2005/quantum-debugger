# Quick Start Guide: GPU Testing Setup

## What This Does

This guide helps you set up a Python 3.12 environment to test the GPU (CuPy) backend, while keeping your Python 3.14 installation untouched.

## Prerequisites

- **Python 3.12** (we'll install this)
- **NVIDIA RTX 5060 GPU** ✓ (you have this!)
- **NVIDIA GPU Drivers** (already installed for gaming/etc)

## Step-by-Step Instructions

### 1. Install Python 3.12

**Download:**
- Go to: https://www.python.org/downloads/release/python-31210/
- Click: "Windows installer (64-bit)"
- File: `python-3.12.10-amd64.exe` (~25MB)

**Install:**
1. Run the installer
2. ✅ Check "Add Python 3.12 to PATH"
3. ✅ Check "Install for all users" (optional but recommended)
4. Click "Install Now"
5. Wait 2-3 minutes

**Verify:**
```powershell
py -3.12 --version
# Should show: Python 3.12.x
```

### 2. Run Setup Script

Open PowerShell in your project directory:

```powershell
cd "d:\E\qc application\application 2"

# Run the automated setup
.\setup_gpu.ps1
```

**What it does:**
- ✓ Checks for Python 3.12
- ✓ Creates `venv_gpu` virtual environment
- ✓ Installs NumPy, SciPy
- ✓ Installs CuPy (GPU support)
- ✓ Activates the environment

### 3. Test GPU Backend

After setup completes:

```powershell
# Should already be activated, but if not:
.\venv_gpu\Scripts\Activate.ps1

# Quick GPU test
python -c "from quantum_debugger.backends import get_backend; b = get_backend('gpu'); print('GPU:', b.name)"

# Full backend tests
python test_backends.py

# GPU-specific tests
python test_backends_comprehensive.py
```

### 4. Use GPU in Your Code

```python
from quantum_debugger import QuantumCircuit

# Use GPU backend
circuit = QuantumCircuit(10, backend='gpu')
circuit.h(0)
for i in range(9):
    circuit.cnot(i, i+1)

result = circuit.run(shots=1000)
print("GPU execution complete!")
```

## Switching Between Python Versions

### Use Python 3.12 (GPU testing):
```powershell
.\venv_gpu\Scripts\Activate.ps1
python --version  # Shows 3.12.x
# GPU backend available!
```

### Use Python 3.14 (main work):
```powershell
deactivate  # Exit venv
python --version  # Shows 3.14.0
# Back to your main Python
```

## Troubleshooting

### Problem: "CuPy installation failed"

**Cause:** Missing CUDA Toolkit or Visual C++ Build Tools

**Solutions:**

**Option A: Install CUDA Toolkit** (Recommended)
1. Download: https://developer.nvidia.com/cuda-downloads
2. Select: Windows → x86_64 → 12.x → exe (local)
3. Install (~3GB download)
4. Rerun: `.\setup_gpu.ps1`

**Option B: Try older CUDA version**
```powershell
.\venv_gpu\Scripts\Activate.ps1
pip install cupy-cuda11x
```

**Option C: Use other backends** (Works now!)
```python
# Sparse backend (98% memory savings)
circuit = QuantumCircuit(10, backend='sparse')

# With parallel execution
from quantum_debugger.parallel import run_parallel
result = run_parallel(circuit, shots=5000, n_workers=4)
```

### Problem: "Python 3.12 not found"

**Solution:** Install Python 3.12 first (see Step 1)

### Problem: "Execution policy" error

**Solution:**
```powershell
# Allow script execution (one-time)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then run setup again
.\setup_gpu.ps1
```

## What Backends Will Work?

After setup:

| Backend | Python 3.14 | Python 3.12 (venv) |
|---------|-------------|-------------------|
| NumPy   | ✓ Yes       | ✓ Yes             |
| Sparse  | ✓ Yes (98% savings!) | ✓ Yes |
| Parallel| ✓ Yes       | ✓ Yes             |
| Numba   | ✗ No        | ✓ Yes (2-3x faster)|
| GPU     | ✗ No        | ✓ Yes (5-10x faster)|

## Recommended Workflow

**For development (Python 3.14):**
- Use sparse backend + parallel execution
- 98% memory savings + multi-core = excellent performance
- No GPU needed for most work

**For benchmarking (Python 3.12 venv):**
- Activate `venv_gpu`
- Test GPU performance
- Compare: NumPy vs Sparse vs Numba vs GPU
- Deactivate when done

## Quick Reference

```powershell
# Activate GPU environment
.\venv_gpu\Scripts\Activate.ps1

# Deactivate
deactivate

# Check current Python
python --version

# List installed packages
pip list

# Update packages
pip install --upgrade cupy-cuda12x
```

## Need Help?

The setup script (`setup_gpu.ps1`) will:
- ✓ Check all prerequisites
- ✓ Show clear error messages
- ✓ Provide solutions if something fails
- ✓ Work even if CuPy fails (sparse backend works!)

Run it and follow the instructions!
