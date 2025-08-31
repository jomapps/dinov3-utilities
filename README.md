# DINOv3 Utilities Service

A production-ready FastAPI service for DINOv3 image analysis, featuring 30+ endpoints for feature extraction, similarity analysis, quality assessment, and cinematic intelligence.

## 🚀 Quick Start

### Prerequisites
- **Python 3.12+**
- **MongoDB** (local installation)
- **Redis** (local installation)
- **NVIDIA GPU** with 8GB+ VRAM (RTX 4060 Ti 16GB tested)
- **CUDA 12.1+** for GPU acceleration
- **DINOv3 Model** (included in `/models` directory)

### Installation & Setup

1. **Clone Repository**
```bash
git clone <repository-url>
cd dinov3-utilities
```

2. **Create Virtual Environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment**
```bash
# Copy and edit .env file with your settings
cp .env.example .env
```

5. **Start Services**
```bash
# Start MongoDB and Redis locally
# Then start the application
python -m uvicorn app.main:app --host 0.0.0.0 --port 3012 --reload
```

6. **Verify Installation**
- API Documentation: http://localhost:3012/docs
- Health Check: http://localhost:3012/api/v1/health

## 🏗️ Architecture

### Core Components
- **FastAPI** - REST API with 30+ endpoints and automatic OpenAPI documentation
- **MongoDB + Beanie ODM** - Document database for metadata and feature storage
- **Redis** - High-performance caching for feature vectors and results
- **Cloudflare R2** - S3-compatible object storage for media assets
- **DINOv3 Model** - Local GPU-accelerated vision transformer for feature extraction
- **NVIDIA GPU** - CUDA acceleration for model inference

### Key Features
- **🎯 Production Ready** - Fully tested and deployed configuration
- **⚡ GPU Accelerated** - CUDA-optimized DINOv3 inference with 16GB VRAM support
- **📦 Asset Management** - Complete media upload, processing, and retrieval pipeline
- **🔍 Advanced Analytics** - Similarity analysis, quality assessment, character consistency
- **🎬 Video Intelligence** - Shot detection, cinematic analysis, and recommendations
- **📊 Batch Processing** - Efficient multi-asset operations with queue management
- **🚀 High Performance** - Redis caching, optimized database queries, async processing

## 📋 Service Endpoints

### Media Asset Management
- `POST /upload-media` - Upload to R2 storage
- `GET /media/{id}` - Retrieve asset metadata
- `DELETE /media/{id}` - Remove asset

### Core Feature Extraction  
- `POST /extract-features` - DINOv3 embeddings (384-dim)
- `POST /preprocess-image` - Standard preprocessing

### Similarity & Matching
- `POST /calculate-similarity` - Cosine similarity between assets
- `POST /find-best-match` - Best match from candidates
- `POST /validate-consistency` - Character consistency check

### Quality Analysis
- `POST /analyze-quality` - DINOv3-based quality metrics
- `POST /analyze-image-metrics` - Technical image assessment

### Batch Processing
- `POST /batch-similarity` - Similarity matrix for multiple assets
- `POST /batch-quality-check` - Quality analysis for batches

### Character Analysis
- `POST /character-matching` - Advanced consistency checking
- `POST /group-by-character` - Cluster by detected characters

### Production Services
- `POST /validate-shot-consistency` - Cinematic sequence validation
- `POST /reference-enforcement` - Generated content compliance

### Video Analysis & Intelligence
- `POST /analyze-video-shots` - Shot detection and camera analysis
- `POST /store-shot-data` - Build cinematic shot database
- `POST /suggest-shots` - AI cinematography recommendations
- `GET /shot-library` - Browse shot database

### Advanced Analytics
- `POST /semantic-search` - Content-based image retrieval
- `POST /anomaly-detection` - Outlier detection
- `POST /feature-clustering` - K-means clustering

### Utilities
- `GET /health` - Service health and GPU status
- `GET /model-info` - DINOv3 model information
- `GET /config` - Current configuration
- `PUT /config/quality-threshold` - Update quality threshold
- `PUT /config/similarity-threshold` - Update similarity threshold

## 🔧 Configuration

### Environment Variables (.env)
```env
# Database Configuration
MONGODB_URL=mongodb://localhost:27017/dinov3_db

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Cloudflare R2 Storage
CLOUDFLARE_R2_ENDPOINT=https://your-account-id.r2.cloudflarestorage.com
CLOUDFLARE_R2_ACCESS_KEY_ID=your_access_key_id
CLOUDFLARE_R2_SECRET_ACCESS_KEY=your_secret_access_key
CLOUDFLARE_R2_BUCKET_NAME=your_bucket_name
CLOUDFLARE_R2_PUBLIC_URL=https://your-domain.com

# DINOv3 Model Configuration
DINOV3_MODEL_NAME=models/dinov3-vitb16-pretrain-lvd1689m
DINOV3_DEVICE=cuda
DINOV3_BATCH_SIZE=32

# API Configuration
API_HOST=0.0.0.0
API_PORT=3012
CORS_ORIGINS=http://localhost:3012,http://127.0.0.1:3012

# Hugging Face Token (for model downloads)
HF_TOKEN=your_hugging_face_token

# Processing Limits
MAX_FILE_SIZE_MB=50
MAX_BATCH_SIZE=100
```

### System Requirements
- **GPU**: NVIDIA GPU with 8GB+ VRAM (RTX 4060 Ti 16GB tested and recommended)
- **RAM**: 16GB+ system RAM
- **Storage**: 10GB+ free space (for models and cache)
- **OS**: Windows 11, Ubuntu 20.04+, or macOS (with CUDA support)

## 📊 Usage Examples

### Upload and Analyze Image
```python
import requests

# Upload image
with open('image.jpg', 'rb') as f:
    upload = requests.post('http://localhost:3012/api/v1/upload-media', 
                          files={'file': f})
asset_id = upload.json()['asset_id']

# Extract features
features = requests.post('http://localhost:3012/api/v1/extract-features',
                        json={'asset_id': asset_id})

# Analyze quality  
quality = requests.post('http://localhost:3012/api/v1/analyze-quality',
                       json={'asset_id': asset_id})
```

### Character Consistency Check
```python
# Compare two character images
consistency = requests.post('http://localhost:3012/api/v1/validate-consistency',
                           json={
                               'asset_id_1': 'character_ref_id',
                               'asset_id_2': 'character_test_id'
                           })

same_character = consistency.json()['same_character']
similarity_score = consistency.json()['similarity_score']
```

### Video Shot Analysis
```python
# Analyze video for shots
shots = requests.post('http://localhost:3012/api/v1/analyze-video-shots',
                     json={'video_asset_id': 'video_id'})

# Store in shot database
requests.post('http://localhost:3012/api/v1/store-shot-data',
              json={
                  'video_asset_id': 'video_id',
                  'shots': shots.json()['shot_analyses'],
                  'scene_context': 'Action sequence with car chase'
              })
```

## 🚀 Production Deployment

### Pre-Deployment Checklist
- ✅ **Environment Configuration**: Update `.env` with production credentials
- ✅ **Database Setup**: Configure production MongoDB instance
- ✅ **Storage Setup**: Configure Cloudflare R2 bucket and CDN
- ✅ **GPU Drivers**: Install NVIDIA drivers and CUDA toolkit
- ✅ **Model Files**: Ensure DINOv3 model is available in `/models` directory
- ✅ **Security**: Set secure API keys and enable HTTPS
- ✅ **Monitoring**: Configure health checks and logging

### Deployment Steps
1. **Server Setup**
   ```bash
   # Install system dependencies
   sudo apt update && sudo apt install -y python3.12 python3.12-venv nvidia-driver-535

   # Clone repository
   git clone <your-repo> /opt/dinov3-utilities
   cd /opt/dinov3-utilities
   ```

2. **Application Setup**
   ```bash
   # Create virtual environment
   python3.12 -m venv venv
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Service Configuration**
   ```bash
   # Create systemd service
   sudo cp scripts/dinov3-service.service /etc/systemd/system/
   sudo systemctl enable dinov3-service
   sudo systemctl start dinov3-service
   ```

## 📊 Monitoring & Health Checks

### Health Endpoints
- `GET /api/v1/health` - System status, GPU memory, model status
- `GET /api/v1/model-info` - DINOv3 configuration and capabilities

### Key Metrics to Monitor
- **GPU Utilization** - VRAM usage and temperature
- **Processing Latency** - Feature extraction and similarity calculation times
- **Cache Performance** - Redis hit/miss ratios
- **Database Performance** - MongoDB query times and connection pool status
- **Storage Usage** - Cloudflare R2 bandwidth and storage consumption
- **API Response Times** - Endpoint performance and error rates

## 🐛 Troubleshooting

### Common Issues & Solutions

**🔧 GPU Not Detected**
```bash
# Check NVIDIA drivers and CUDA
nvidia-smi
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}, Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}')"
```

**🔧 Model Loading Issues**
```bash
# Check model files exist
ls -la models/dinov3-vitb16-pretrain-lvd1689m/
# Verify VRAM availability
nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits
```

**🔧 Database Connection Issues**
```bash
# Check MongoDB status
sudo systemctl status mongod
# Test connection
python -c "from pymongo import MongoClient; print(MongoClient('mongodb://localhost:27017').admin.command('ping'))"
```

**🔧 Redis Connection Issues**
```bash
# Check Redis status
redis-cli ping
# Should return "PONG"
```

**🔧 API Startup Failures**
- Check port 3012 availability: `netstat -tulpn | grep 3012`
- Verify all dependencies installed: `pip check`
- Check logs for specific error messages

## 📝 Development

### Project Structure
```
dinov3-utilities/
├── app/
│   ├── core/           # Core services (DINOv3, database, storage)
│   ├── routers/        # API endpoint routers
│   └── main.py         # FastAPI application
├── scripts/            # Development scripts
├── docker-compose.yml  # Local services
└── requirements.txt    # Python dependencies
```

### Adding New Endpoints
1. Create router in `app/routers/`
2. Add database models if needed
3. Include router in `main.py`
4. Update documentation

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

---

**Ready to process 30+ DINOv3 operations with GPU acceleration! 🚀**