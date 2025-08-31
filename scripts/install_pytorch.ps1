# PyTorch Installation Script for CUDA 12.1
# This script installs PyTorch with CUDA support separately to avoid pip conflicts

Write-Host "Installing PyTorch with CUDA 12.1 support..." -ForegroundColor Green

# Activate virtual environment if not already activated
if (-not $env:VIRTUAL_ENV) {
    if (Test-Path ".\venv\Scripts\Activate.ps1") {
        Write-Host "Activating virtual environment..." -ForegroundColor Cyan
        & ".\venv\Scripts\Activate.ps1"
    }
}

# Install PyTorch with CUDA support
Write-Host "Installing PyTorch, torchvision, and torchaudio with CUDA 12.1..." -ForegroundColor Cyan
pip install torch==2.1.1+cu121 torchvision==0.16.1+cu121 torchaudio==2.1.1+cu121 --extra-index-url https://download.pytorch.org/whl/cu121

# Verify installation
Write-Host "Verifying PyTorch installation..." -ForegroundColor Cyan
python -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    print(f'GPU device: {torch.cuda.get_device_name(0)}')
else:
    print('CUDA not available - will use CPU')
"

Write-Host "PyTorch installation complete!" -ForegroundColor Green
