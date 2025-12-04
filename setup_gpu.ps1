# GPU Testing Setup Script for Python 3.12
# Automates virtual environment creation and CuPy installation

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "GPU Backend Setup - Python 3.12 Virtual Environment" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if Python 3.12 is installed
Write-Host "[1/5] Checking for Python 3.12..." -ForegroundColor Yellow

$python312 = $null
try {
    $version = py -3.12 --version 2>&1 | Out-String
    if ($version -match "Python 3.12") {
        Write-Host "  Found: $version" -ForegroundColor Green
        $python312 = "py"
        $python312args = "-3.12"
    }
} catch {
    Write-Host "  Python 3.12 not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.12 from:" -ForegroundColor Yellow
    Write-Host "  https://www.python.org/downloads/release/python-31210/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "See GPU_SETUP_GUIDE.md for detailed instructions" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 2: Create virtual environment
Write-Host ""
Write-Host "[2/5] Creating Python 3.12 virtual environment..." -ForegroundColor Yellow

$venvPath = "venv_gpu"

if (Test-Path $venvPath) {
    Write-Host "  Virtual environment already exists" -ForegroundColor Yellow
    $response = Read-Host "  Delete and recreate? (y/n)"
    if ($response -eq "y") {
        Remove-Item -Recurse -Force $venvPath
    } else {
        Write-Host "  Using existing environment" -ForegroundColor Green
        exit 0
    }
}

Write-Host "  Creating venv..." -ForegroundColor White
& py -3.12 -m venv $venvPath

if (Test-Path "$venvPath\Scripts\Activate.ps1") {
    Write-Host "  Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "  Failed to create virtual environment!" -ForegroundColor Red
    exit 1
}

# Step 3: Activate and install
Write-Host ""
Write-Host "[3/5] Installing core packages..." -ForegroundColor Yellow

& "$venvPath\Scripts\python.exe" -m pip install --upgrade pip --quiet
& "$venvPath\Scripts\pip.exe" install numpy scipy --quiet

Write-Host "  Core packages installed" -ForegroundColor Green

# Step 4: Install CuPy
Write-Host ""
Write-Host "[4/5] Installing CuPy (this may take a few minutes)..." -ForegroundColor Yellow

$installed = $false

Write-Host "  Trying CUDA 12.x..." -ForegroundColor White
& "$venvPath\Scripts\pip.exe" install cupy-cuda12x --quiet 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  CuPy installed successfully!" -ForegroundColor Green
    $installed = $true
}

if (-not $installed) {
    Write-Host "  Trying CUDA 11.x..." -ForegroundColor White
    & "$venvPath\Scripts\pip.exe" install cupy-cuda11x --quiet 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  CuPy (CUDA 11.x) installed!" -ForegroundColor Green
        $installed = $true
    }
}

if (-not $installed) {
    Write-Host "  CuPy installation failed" -ForegroundColor Red
    Write-Host "  You can still use NumPy and Sparse backends!" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "SETUP COMPLETE!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To use GPU backend:" -ForegroundColor Yellow
Write-Host "  1. Activate: .\venv_gpu\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "  2. Test: python test_backends.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "See GPU_SETUP_GUIDE.md for more details" -ForegroundColor White
Write-Host ""
