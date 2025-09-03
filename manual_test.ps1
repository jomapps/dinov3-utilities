# Simple manual test of production service
$BaseUrl = "https://dino.ft.tc"
$ApiBase = "$BaseUrl/api/v1"

Write-Host "Testing DINOv3 Production Service" -ForegroundColor Green
Write-Host "Base URL: $BaseUrl" -ForegroundColor Yellow

# Test health endpoint
try {
    Write-Host "`nTesting Health Endpoint..." -ForegroundColor Yellow
    $healthResponse = Invoke-WebRequest -Uri "$ApiBase/health" -Method GET -UseBasicParsing -TimeoutSec 30
    Write-Host "✓ Health endpoint responded with status: $($healthResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Health data:" -ForegroundColor Cyan
    Write-Host $healthResponse.Content
} catch {
    Write-Host "✗ Health endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test model info
try {
    Write-Host "`nTesting Model Info..." -ForegroundColor Yellow
    $modelResponse = Invoke-WebRequest -Uri "$ApiBase/model-info" -Method GET -UseBasicParsing -TimeoutSec 30
    Write-Host "✓ Model info responded with status: $($modelResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Model info:" -ForegroundColor Cyan
    Write-Host $modelResponse.Content
} catch {
    Write-Host "✗ Model info failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test config
try {
    Write-Host "`nTesting Configuration..." -ForegroundColor Yellow
    $configResponse = Invoke-WebRequest -Uri "$ApiBase/config" -Method GET -UseBasicParsing -TimeoutSec 30
    Write-Host "✓ Config responded with status: $($configResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Config data:" -ForegroundColor Cyan
    Write-Host $configResponse.Content
} catch {
    Write-Host "✗ Config failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test shot library
try {
    Write-Host "`nTesting Shot Library..." -ForegroundColor Yellow
    $shotResponse = Invoke-WebRequest -Uri "$ApiBase/shot-library" -Method GET -UseBasicParsing -TimeoutSec 30
    Write-Host "✓ Shot library responded with status: $($shotResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Shot library data:" -ForegroundColor Cyan
    Write-Host $shotResponse.Content
} catch {
    Write-Host "✗ Shot library failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nTest completed." -ForegroundColor Green
