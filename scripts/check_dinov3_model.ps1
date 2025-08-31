# DINOv3 Model Download and Verification Script
# This script checks if the DINOv3 model is available and downloads it if needed

Write-Host "Checking DINOv3 model availability..." -ForegroundColor Green

# Activate virtual environment if not already activated
if (-not $env:VIRTUAL_ENV) {
    if (Test-Path ".\venv\Scripts\Activate.ps1") {
        Write-Host "Activating virtual environment..." -ForegroundColor Cyan
        & ".\venv\Scripts\Activate.ps1"
    }
}

# Check if DINOv3 model is available
Write-Host "Testing DINOv3 model download and initialization..." -ForegroundColor Cyan
python -c "
import torch
import sys
import os
from pathlib import Path
from transformers import AutoImageProcessor, AutoModel
from huggingface_hub import login
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print('=== DINOv3 Model Check ===')
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')

try:
    # Authenticate with Hugging Face
    hf_token = os.getenv('HF_TOKEN')
    if hf_token:
        print('\\nAuthenticating with Hugging Face...')
        login(token=hf_token)
        print('✓ Hugging Face authentication successful!')
    else:
        print('\\n⚠ No HF_TOKEN found in environment')
    
    # Try to load DINOv3 model
    print('\\nAttempting to load DINOv3 model from Hugging Face...')
    model_name = 'facebook/dinov3-vitb16-pretrain-lvd1689m'
    
    processor = AutoImageProcessor.from_pretrained(
        model_name,
        token=hf_token if hf_token else None,
        trust_remote_code=True
    )
    model = AutoModel.from_pretrained(
        model_name,
        token=hf_token if hf_token else None,
        trust_remote_code=True
    )
    print('✓ DINOv3 model loaded successfully!')
    
    # Test model inference
    print('\\nTesting model inference...')
    model.eval()
    
    # Create dummy input (3x224x224 image)
    from PIL import Image
    import numpy as np
    
    # Create a dummy RGB image
    dummy_image = Image.fromarray(np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8))
    
    # Process image
    inputs = processor(images=dummy_image, return_tensors='pt')
    
    with torch.no_grad():
        if torch.cuda.is_available():
            print('Moving model to GPU...')
            model = model.cuda()
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        outputs = model(**inputs)
        features = outputs.last_hidden_state[:, 0, :]  # CLS token
        print(f'✓ Model inference successful! Feature shape: {features.shape}')
        print(f'Expected feature dimension: 768 (DINOv3 ViT-B/16)')
    
    print('\\n=== DINOv3 Model Check Complete ===')
    print('✓ Model is ready for use!')
    
except Exception as e:
    print(f'✗ Error loading DINOv3 model: {e}')
    print('\\nTroubleshooting steps:')
    print('1. Check HF_TOKEN in .env file')
    print('2. Verify internet connection for model download')
    print('3. Ensure sufficient disk space for model cache (~1GB)')
    print('4. Check if you have access to the facebook/dinov3_vitb16_pretrain model')
    sys.exit(1)
"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ DINOv3 model check passed!" -ForegroundColor Green
} else {
    Write-Host "✗ DINOv3 model check failed!" -ForegroundColor Red
    Write-Host "Run this script again after fixing PyTorch installation" -ForegroundColor Yellow
}
