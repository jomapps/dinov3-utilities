# DINOv3 Utilities API Test Script
# Test all major endpoints to verify functionality

Write-Host "Testing DINOv3 Utilities API..." -ForegroundColor Green

$API_BASE = "http://localhost:3012/api/v1"
$testImage = "test_image.jpg"

# Test health endpoint
Write-Host "`nTesting health endpoint..." -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "$API_BASE/health" -Method GET
    Write-Host "✓ Health check passed" -ForegroundColor Green
    Write-Host "  GPU Available: $($health.gpu.available)" -ForegroundColor Yellow
    Write-Host "  Model Loaded: $($health.model.loaded)" -ForegroundColor Yellow
} catch {
    Write-Host "✗ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test model info
Write-Host "`nTesting model info endpoint..." -ForegroundColor Cyan
try {
    $modelInfo = Invoke-RestMethod -Uri "$baseUrl/model-info" -Method GET
    Write-Host "✓ Model info retrieved" -ForegroundColor Green
    Write-Host "  Model: $($modelInfo.model_config.model_name)" -ForegroundColor Yellow
    Write-Host "  Device: $($modelInfo.model_config.device)" -ForegroundColor Yellow
} catch {
    Write-Host "✗ Model info failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Create a test image if it doesn't exist
if (-not (Test-Path $testImage)) {
    Write-Host "`nCreating test image..." -ForegroundColor Cyan
    # Create a simple test image using Python
    python -c "
from PIL import Image
import numpy as np

# Create a simple test image
img = Image.new('RGB', (224, 224), color=(73, 109, 137))
img.save('$testImage')
print('Test image created: $testImage')
"
}

# Test media upload
Write-Host "`nTesting media upload..." -ForegroundColor Cyan
try {
    $uploadForm = @{
        file = Get-Item $testImage
    }
    $upload = Invoke-RestMethod -Uri "$baseUrl/upload-media" -Method POST -Form $uploadForm
    $assetId = $upload.asset_id
    Write-Host "✓ Media upload successful" -ForegroundColor Green
    Write-Host "  Asset ID: $assetId" -ForegroundColor Yellow
    
    # Test feature extraction
    Write-Host "`nTesting feature extraction..." -ForegroundColor Cyan
    $featureBody = @{ asset_id = $assetId } | ConvertTo-Json
    $features = Invoke-RestMethod -Uri "$baseUrl/extract-features" -Method POST -Body $featureBody -ContentType "application/json"
    Write-Host "✓ Feature extraction successful" -ForegroundColor Green
    Write-Host "  Features extracted: $($features.features_extracted)" -ForegroundColor Yellow
    
    # Test quality analysis
    Write-Host "`nTesting quality analysis..." -ForegroundColor Cyan
    $qualityBody = @{ asset_id = $assetId } | ConvertTo-Json
    $quality = Invoke-RestMethod -Uri "$baseUrl/analyze-quality" -Method POST -Body $qualityBody -ContentType "application/json"
    Write-Host "✓ Quality analysis successful" -ForegroundColor Green
    Write-Host "  Quality score: $([math]::Round($quality.quality_score, 3))" -ForegroundColor Yellow
    
} catch {
    Write-Host "✗ API test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nAPI testing completed!" -ForegroundColor Green
