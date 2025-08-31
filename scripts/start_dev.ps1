# DINOv3 Utilities Development Startup Script
# Run this script to start the development environment (no Docker needed)

Write-Host "Starting DINOv3 Utilities Development Environment..." -ForegroundColor Green

# Create Python virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "Please edit .env file with your API keys before continuing." -ForegroundColor Yellow
    Read-Host "Press Enter when ready to continue"
}

# Check existing services
Write-Host "Checking existing services..." -ForegroundColor Cyan

# Load environment variables from .env file
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

# Check MongoDB
try {
    $mongoUrl = [Environment]::GetEnvironmentVariable("MONGODB_URL") -replace "mongodb://", "" -replace "/.*", ""
    if (-not $mongoUrl) { $mongoUrl = "localhost:27017" }
    
    $mongoTest = Test-NetConnection -ComputerName ($mongoUrl -split ":")[0] -Port ([int]($mongoUrl -split ":")[1]) -WarningAction SilentlyContinue
    if ($mongoTest.TcpTestSucceeded) {
        Write-Host "✓ MongoDB is accessible ($mongoUrl)" -ForegroundColor Green
    } else {
        Write-Host "✗ MongoDB not accessible ($mongoUrl) - please start MongoDB service" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ MongoDB connection test failed - please start MongoDB service" -ForegroundColor Red
}

# Check Redis
try {
    $redisUrl = [Environment]::GetEnvironmentVariable("REDIS_URL") -replace "redis://", "" -replace "/.*", ""
    if (-not $redisUrl) { $redisUrl = "localhost:6379" }
    
    $redisTest = Test-NetConnection -ComputerName ($redisUrl -split ":")[0] -Port ([int]($redisUrl -split ":")[1]) -WarningAction SilentlyContinue
    if ($redisTest.TcpTestSucceeded) {
        Write-Host "✓ Redis is accessible ($redisUrl)" -ForegroundColor Green
    } else {
        Write-Host "✗ Redis not accessible ($redisUrl) - please start Redis service" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Redis connection test failed - please start Redis service" -ForegroundColor Red
}

# Check PathRAG
try {
    $pathragUrl = [Environment]::GetEnvironmentVariable("PATHRAG_API_URL")
    if (-not $pathragUrl) { $pathragUrl = "http://localhost:5000" }
    
    $pathragResponse = Invoke-WebRequest -Uri "$pathragUrl/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
    if ($pathragResponse.StatusCode -eq 200) {
        Write-Host "✓ PathRAG is running ($pathragUrl)" -ForegroundColor Green
    } else {
        Write-Host "⚠ PathRAG not accessible ($pathragUrl) - ArangoDB features will be disabled" -ForegroundColor Yellow
    }
} catch {
    $pathragUrl = [Environment]::GetEnvironmentVariable("PATHRAG_API_URL")
    if (-not $pathragUrl) { $pathragUrl = "http://localhost:5000" }
    Write-Host "⚠ PathRAG not accessible ($pathragUrl) - ArangoDB features will be disabled" -ForegroundColor Yellow
}

# Install Python dependencies in virtual environment
Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

# Install PyTorch separately with CUDA support
Write-Host "Installing PyTorch with CUDA support..." -ForegroundColor Cyan
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu121

# Initialize MongoDB database
Write-Host "Initializing MongoDB database..." -ForegroundColor Cyan
python -c "
import asyncio
from app.core.database import init_database

async def setup_db():
    try:
        await init_database()
        print('MongoDB database initialized successfully')
    except Exception as e:
        print(f'Database initialization failed: {e}')

asyncio.run(setup_db())
"

# Start the FastAPI application
Write-Host "Starting DINOv3 Utilities API..." -ForegroundColor Green
Write-Host "API will be available at: http://localhost:3012" -ForegroundColor Yellow
Write-Host "API Documentation: http://localhost:3012/docs" -ForegroundColor Yellow
Write-Host "Using Cloudflare R2 for storage" -ForegroundColor Yellow

python -m uvicorn app.main:app --host 0.0.0.0 --port 3012 --reload
