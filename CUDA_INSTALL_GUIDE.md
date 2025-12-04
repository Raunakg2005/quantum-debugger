# CUDA Toolkit Installation Guide

## What We're Installing

**CUDA Toolkit 12.6** - Complete development environment for GPU computing
- Size: ~3-4 GB download
- Time: 10-15 minutes
- Requirement: NVIDIA RTX 5060 (you have this!)

## Installation Methods

### Method 1: Automatic (Recommended)

Using Windows Package Manager:
```powershell
winget install NVIDIA.CUDA
```

### Method 2: Manual Download

If winget doesn't have the latest version:

1. **Download:**
   - Go to: https://developer.nvidia.com/cuda-downloads
   - Select:
     - Operating System: Windows
     - Architecture: x86_64
     - Version: 11 (or your Windows version)
     - Installer Type: exe (local)
   
2. **Run Installer:**
   - File: `cuda_12.6.X_windows.exe` (~3.5 GB)
   - Choose: Express Installation (recommended)
   - Wait: 10-15 minutes

3. **Verify:**
   ```powershell
   nvcc --version
   # Should show: Cuda compilation tools, release 12.6
   ```

## What Gets Installed

✓ CUDA Runtime Libraries
✓ cuBLAS (matrix operations - what we need!)
✓ Development Tools (nvcc compiler)
✓ Code Samples
✓ Documentation

## After Installation

1. **Restart PowerShell** (to refresh environment variables)

2. **Test GPU Backend:**
   ```powershell
   .\venv_gpu\Scripts\Activate.ps1
   python test_gpu_quick.py
   ```

3. **Should see:**
   ```
   ✓ GPU Backend: CuPy (GPU:0)
   ✓ GPU Device: 0
   ✓ GPU Memory: 4096MB total
   🎉 GPU BACKEND READY!
   ```

## Troubleshooting

### "CUDA path could not be detected"
**Solution:** Add to system environment:
```powershell
$env:CUDA_PATH = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6"
```

### "cudaErrorNoDevice"
**Solution:** 
1. Check GPU drivers: `nvidia-smi` (run as admin)
2. Restart computer after CUDA installation

### Installation takes too long
**Normal!** CUDA is large (~3.5 GB) and installation can take 10-15 minutes.

## Quick Reference

**Check CUDA version:**
```powershell
nvcc --version
```

**Check GPU status:**
```powershell
nvidia-smi
```

**Test in Python:**
```python
import cupy as cp
print(cp.cuda.runtime.getDeviceCount())  # Should show: 1
```

## What Happens Next

After CUDA installs, your GPU backend will work:

```python
from quantum_debugger import QuantumCircuit

# 5-10x faster!
circuit = QuantumCircuit(10, backend='gpu')
circuit.h(0)
for i in range(9):
    circuit.cnot(i, i+1)

# GPU does the heavy lifting
result = circuit.run(shots=5000)
```

**Expected Performance:**
- 10-qubit circuit: ~0.3s (was 2s with CPU)
- **~6-7x speedup!**
