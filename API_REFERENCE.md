# DINOv3 Utilities API Reference

## 🌐 Base URL
- **Development**: `http://localhost:3012`
- **Production**: `https://your-domain.com`

## 📚 Interactive Documentation
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`

## 🔐 Authentication
Currently, the API does not require authentication. For production deployments, consider implementing:
- API Key authentication
- JWT tokens
- OAuth 2.0

## 📋 API Endpoints Overview

### 🎯 Core Endpoints

#### Media Asset Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/upload-media` | POST | Upload media file to Cloudflare R2 |
| `/api/v1/media/{asset_id}` | GET | Retrieve media asset information |
| `/api/v1/media/{asset_id}` | DELETE | Delete media asset |

#### Feature Extraction
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/extract-features` | POST | Extract DINOv3 feature embeddings |
| `/api/v1/preprocess-image` | POST | Preprocess image for analysis |

#### Similarity Analysis
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/calculate-similarity` | POST | Calculate similarity between two assets |
| `/api/v1/find-best-match` | POST | Find best matching asset from candidates |
| `/api/v1/validate-consistency` | POST | Validate character consistency |

#### Quality Analysis
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/analyze-quality` | POST | Comprehensive quality analysis |
| `/api/v1/analyze-image-metrics` | POST | Detailed image quality metrics |

#### Batch Processing
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/batch-similarity` | POST | Calculate similarity matrix for multiple assets |
| `/api/v1/batch-quality-check` | POST | Batch quality analysis |

#### Character Analysis
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/character-matching` | POST | Advanced character consistency checking |
| `/api/v1/group-by-character` | POST | Group assets by detected characters |

#### Video Analysis
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/analyze-video-shots` | POST | Analyze video for shot detection |
| `/api/v1/store-shot-data` | POST | Store shot analysis data |
| `/api/v1/suggest-shots` | POST | Get cinematography recommendations |
| `/api/v1/shot-library` | GET | Browse shot database |

#### Advanced Analytics
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/semantic-search` | POST | Content-based image retrieval |
| `/api/v1/anomaly-detection` | POST | Detect anomalous assets |
| `/api/v1/feature-clustering` | POST | Cluster assets by features |

#### System Utilities
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | System health and status |
| `/api/v1/model-info` | GET | DINOv3 model information |
| `/api/v1/config` | GET | Current system configuration |

## 📝 Request/Response Examples

### Upload Media
```http
POST /api/v1/upload-media
Content-Type: multipart/form-data

file: [binary image data]
```

**Response:**
```json
{
  "asset_id": "uuid-string",
  "filename": "image.jpg",
  "content_type": "image/jpeg",
  "file_size": 1024000,
  "upload_timestamp": "2025-08-31T12:00:00Z",
  "public_url": "https://media.example.com/uuid-string.jpg",
  "processing_status": "uploaded"
}
```

### Extract Features
```http
POST /api/v1/extract-features
Content-Type: application/json

{
  "asset_id": "uuid-string"
}
```

**Response:**
```json
{
  "asset_id": "uuid-string",
  "features": [0.123, -0.456, 0.789, ...],  // 384-dimensional array
  "processing_time": 0.85,
  "model_version": "dinov3-vitb16",
  "status": "completed"
}
```

### Calculate Similarity
```http
POST /api/v1/calculate-similarity
Content-Type: application/json

{
  "asset_id_1": "uuid-string-1",
  "asset_id_2": "uuid-string-2"
}
```

**Response:**
```json
{
  "asset_id_1": "uuid-string-1",
  "asset_id_2": "uuid-string-2",
  "similarity_score": 85.7,
  "processing_time": 0.12,
  "confidence": "high"
}
```

### Health Check
```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-31T12:00:00Z",
  "version": "1.0.0",
  "gpu": {
    "available": true,
    "device_name": "NVIDIA GeForce RTX 4060 Ti",
    "memory_total": 16384,
    "memory_used": 2048,
    "memory_free": 14336
  },
  "model": {
    "loaded": true,
    "name": "dinov3-vitb16-pretrain-lvd1689m",
    "device": "cuda"
  },
  "database": {
    "connected": true,
    "type": "mongodb"
  },
  "cache": {
    "connected": true,
    "type": "redis"
  }
}
```

## ⚠️ Error Responses

### Standard Error Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": "Additional error details",
    "timestamp": "2025-08-31T12:00:00Z"
  }
}
```

### Common Error Codes
| Code | Status | Description |
|------|--------|-------------|
| `ASSET_NOT_FOUND` | 404 | Asset ID not found in database |
| `INVALID_FILE_FORMAT` | 400 | Unsupported file format |
| `FILE_TOO_LARGE` | 413 | File exceeds maximum size limit |
| `GPU_MEMORY_ERROR` | 500 | Insufficient GPU memory |
| `MODEL_NOT_LOADED` | 503 | DINOv3 model not available |
| `PROCESSING_FAILED` | 500 | Feature extraction failed |
| `STORAGE_ERROR` | 500 | Cloudflare R2 storage error |

## 📊 Rate Limits
- **Default**: 100 requests per minute per IP
- **Batch operations**: 10 requests per minute per IP
- **Upload operations**: 50 requests per minute per IP

## 🔧 Configuration Parameters

### File Upload Limits
- **Maximum file size**: 50MB
- **Supported formats**: JPG, JPEG, PNG, WEBP, MP4, MOV, AVI
- **Maximum batch size**: 100 assets

### Processing Limits
- **Feature extraction**: 32 images per batch (configurable)
- **Similarity calculations**: 1000 comparisons per request
- **Video analysis**: 60 minutes maximum duration

## 🚀 Performance Optimization

### Caching
- Feature vectors are cached in Redis for 24 hours
- Similarity results are cached for 1 hour
- Preprocessed images are cached for 6 hours

### Batch Processing
- Use batch endpoints for multiple operations
- Optimal batch size: 16-32 assets depending on GPU memory
- Async processing for large batches

## 📈 Monitoring Endpoints

### Metrics
- `/api/v1/metrics` - Prometheus-compatible metrics
- `/api/v1/stats` - Processing statistics
- `/api/v1/performance` - Performance benchmarks

---

For complete API documentation with interactive examples, visit `/docs` when the service is running.
