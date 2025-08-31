# DINOv3 Utilities Service

A comprehensive FastAPI-based service for DINOv3 image analysis, featuring 30+ endpoints for feature extraction, similarity analysis, quality assessment, and cinematic intelligence.

## 🚀 Quick Start

### Prerequisites
- **Windows 11** 
- **Python 3.9+** 
- **MongoDB** (local installation)
- **Redis** (local installation)
- **NVIDIA GPU** (RTX 4060 16GB recommended)
- **CUDA 12.1+** for GPU acceleration

### Development Setup

1. **Clone and Setup Environment**
```powershell
cd d:\Projects\dinov3-utilities
```

2. **Start Development Environment**
```powershell
.\scripts\start_dev.ps1
```

This script will automatically:
- **Create Python virtual environment** (`venv/`)
- **Activate virtual environment**
- **Install all dependencies** in isolated environment
- **Check existing services** (MongoDB, Redis, PathRAG)
- **Initialize MongoDB database** with Beanie ODM
- **Launch FastAPI service** on port 3012

3. **Test the API**
```powershell
.\scripts\test_api.ps1
```

## 🏗️ Architecture

### Core Services
- **FastAPI** - Main API service with 30+ DINOv3 endpoints
- **MongoDB** - Document-based metadata and feature storage with Beanie ODM
- **Redis** - Feature caching and session management (existing local installation)
- **Cloudflare R2** - Production object storage
- **PathRAG** - ArangoDB integration for knowledge graph features (optional)
- **DINOv3** - GPU-accelerated feature extraction

### Key Features
- **Cloudflare R2 Asset Management** - Universal asset ID system
- **Virtual Environment** - Isolated Python dependency management
- **GPU Acceleration** - CUDA-optimized DINOv3 inference
- **MongoDB Integration** - Document-based storage with Beanie ODM
- **Batch Processing** - Efficient multi-asset operations
- **Video Analysis** - Shot detection and cinematic intelligence
- **Character Consistency** - Production-grade validation
- **Quality Assessment** - Comprehensive image metrics
- **PathRAG Integration** - Optional ArangoDB knowledge graph features

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

### Environment Variables
```env
# Database - MongoDB
MONGODB_URL=mongodb://localhost:27017/dinov3_db

# Redis (existing local installation)
REDIS_URL=redis://localhost:6379/0

# Cloudflare R2 Storage
CLOUDFLARE_R2_ENDPOINT=https://026089839555deec85ae1cfc77648038.r2.cloudflarestorage.com
CLOUDFLARE_R2_ACCESS_KEY_ID=your_access_key
CLOUDFLARE_R2_SECRET_ACCESS_KEY=your_secret_key
CLOUDFLARE_R2_BUCKET_NAME=rumble-fanz
CLOUDFLARE_R2_PUBLIC_URL=https://media.rumbletv.com

# DINOv3 Model
DINOV3_MODEL_NAME=dinov3_vitb16_pretrain
DINOV3_DEVICE=cuda
DINOV3_BATCH_SIZE=32

# API Configuration
API_HOST=0.0.0.0
API_PORT=3012
CORS_ORIGINS=http://localhost:3012,http://127.0.0.1:3012

# PathRAG Integration (Optional)
PATHRAG_API_URL=http://localhost:5000
PATHRAG_ENABLE=true
PATHRAG_DEFAULT_TOP_K=5
PATHRAG_MAX_TOKEN_FOR_TEXT_UNIT=512
PATHRAG_MAX_TOKEN_FOR_GLOBAL_CONTEXT=2048
PATHRAG_MAX_TOKEN_FOR_LOCAL_CONTEXT=4096

# Processing Limits
MAX_FILE_SIZE_MB=50
MAX_BATCH_SIZE=100
```

### GPU Requirements
- **Minimum**: 8GB VRAM
- **Recommended**: 16GB VRAM (RTX 4060/4070)
- **Optimal**: 24GB+ VRAM for large batches

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

## 🚀 Deployment

### Production Checklist
1. **Update Environment**
   - Verify Cloudflare R2 credentials
   - Use production MongoDB/Redis instances
   - Set secure API keys

2. **Virtual Environment Setup**
   - Create isolated Python environment: `python -m venv venv`
   - Activate environment: `.\venv\Scripts\Activate.ps1`
   - Install dependencies: `pip install -r requirements.txt`

3. **GPU Setup**
   - Install CUDA drivers
   - Verify PyTorch GPU support
   - Test DINOv3 model loading

4. **Scaling**
   - Configure multiple workers
   - Set up load balancing
   - Enable Redis clustering

## 🔍 Monitoring

### Health Endpoints
- `/api/v1/health` - System status, GPU memory, model status
- `/api/v1/model-info` - DINOv3 configuration and capabilities

### Key Metrics
- **GPU Utilization** - Monitor VRAM usage
- **Processing Time** - Track inference latency  
- **Cache Hit Rate** - Redis feature caching efficiency
- **Storage Usage** - R2/MinIO asset storage

## 🐛 Troubleshooting

### Common Issues

**GPU Not Detected**
```bash
# Check CUDA installation
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"
```

**Model Loading Fails**
- Verify internet connection for model download
- Check available disk space (models ~1GB)
- Ensure sufficient VRAM

**Database Connection Issues**
```bash
# Check Docker services
docker-compose ps
docker-compose logs postgres
```

**Storage Upload Failures**
- Verify MinIO is running on port 9000
- Check bucket permissions
- Validate file size limits

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