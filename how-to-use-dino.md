# How to Use DINOv3 Utilities Service

## 📖 What This App Does

The **DINOv3 Utilities Service** is a production-ready FastAPI application that provides AI-powered visual intelligence through 30+ specialized endpoints. Built on Meta's DINOv3 vision transformer model, it offers:

### 🎯 Core Capabilities
- **🖼️ Image Feature Extraction** - Generate 384-dimensional embeddings using DINOv3
- **🔍 Visual Similarity Analysis** - Compare images with cosine similarity and advanced metrics
- **👤 Character Consistency Validation** - Ensure character consistency across scenes (perfect for animation/gaming)
- **📊 Quality Assessment** - Automated image quality analysis and scoring
- **🎬 Video Intelligence** - Shot detection, camera movement analysis, and cinematic recommendations
- **🔄 Batch Processing** - Efficient processing of multiple assets simultaneously
- **🎨 Semantic Search** - Content-based image retrieval using natural language
- **📈 Advanced Analytics** - Clustering, anomaly detection, and pattern recognition

### 🏭 Production Features
- **⚡ GPU Acceleration** - CUDA-optimized inference with 16GB VRAM support
- **📦 Cloud Storage** - Integrated Cloudflare R2 for scalable media storage
- **💾 Smart Caching** - Redis-powered caching for optimal performance
- **📊 Monitoring** - Health checks, metrics, and performance tracking
- **🔧 Configurable** - Flexible thresholds and processing parameters

### 🎯 Perfect For
- **Animation Studios** - Character consistency across scenes
- **Game Development** - Asset quality control and style matching
- **Content Creation** - Video analysis and cinematic intelligence
- **E-commerce** - Visual search and product similarity
- **Media & Entertainment** - Content analysis and recommendations

---

## 📚 Integration Guide

A comprehensive guide for external applications integrating with the DINOv3 Utilities Service for AI-powered image analysis, feature extraction, and video intelligence.

## 🚀 Quick Start

### Service Information
- **Base URL**: `http://localhost:3012` (development) or `https://your-domain.com` (production)
- **API Version**: v1
- **Interactive Documentation**: `/docs` (Swagger UI) or `/redoc` (ReDoc)
- **Health Check**: `/api/v1/health`

### Authentication
Currently no authentication required. For production deployments, implement API keys or JWT tokens.

## 📋 Core Workflows

### 1. Upload and Analyze Images

#### Step 1: Upload Media Asset
```http
POST /api/v1/upload-media
Content-Type: multipart/form-data

file: [binary image data]
```

**Response:**
```json
{
  "asset_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "character_image.jpg",
  "content_type": "image/jpeg",
  "file_size": 1024000,
  "public_url": "https://media.example.com/550e8400-e29b-41d4-a716-446655440000.jpg",
  "width": 1920,
  "height": 1080,
  "format": "JPEG",
  "upload_timestamp": "2025-09-01T11:33:25Z",
  "processing_status": "uploaded",
  "processing_time": 0.85
}
```

#### Step 2: Extract DINOv3 Features
```http
POST /api/v1/extract-features
Content-Type: application/json

{
  "asset_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:**
```json
{
  "asset_id": "550e8400-e29b-41d4-a716-446655440000",
  "features": [0.123, -0.456, 0.789, ...],
  "features_extracted": true,
  "features_timestamp": "2025-09-01T11:33:26Z",
  "processing_time": 1.25,
  "cached": false
}
```

### 2. Character Consistency Validation

Perfect for animation studios, game development, and content creation to ensure character consistency across scenes.

```http
POST /api/v1/validate-consistency
Content-Type: application/json

{
  "asset_id_1": "character_reference_id",
  "asset_id_2": "character_test_id"
}
```

**Response:**
```json
{
  "asset_id_1": "character_reference_id",
  "asset_id_2": "character_test_id",
  "same_character": true,
  "similarity_score": 87.5,
  "confidence_level": "high",
  "explanation": "High similarity suggests same character/person",
  "cosine_similarity": 0.875,
  "euclidean_distance": 0.234,
  "processing_time": 0.45
}
```

### 3. Quality Analysis

Automated quality assessment for content pipelines.

```http
POST /api/v1/analyze-quality
Content-Type: application/json

{
  "asset_id": "image_to_analyze_id"
}
```

**Response:**
```json
{
  "asset_id": "image_to_analyze_id",
  "quality_score": 85.7,
  "quality_grade": "high",
  "technical_metrics": {
    "sharpness": 0.92,
    "contrast": 0.78,
    "brightness": 0.65,
    "noise_level": 0.15
  },
  "recommendations": [
    "Image quality is excellent for production use",
    "Good contrast and sharpness levels"
  ],
  "processing_time": 0.67
}
```

## 🎬 Video Analysis & Cinematic Intelligence

### Shot Detection and Analysis

Analyze videos for automatic shot detection, camera movement analysis, and cinematic patterns.

```http
POST /api/v1/analyze-video-shots
Content-Type: application/json

{
  "video_asset_id": "video_file_id",
  "shot_detection_threshold": 0.3,
  "extract_keyframes": true
}
```

**Response:**
```json
{
  "video_asset_id": "video_file_id",
  "total_shots": 15,
  "video_duration": 120.5,
  "shot_analyses": [
    {
      "shot_id": 1,
      "start_time": 0.0,
      "end_time": 8.5,
      "duration": 8.5,
      "movement_type": "static",
      "camera_angle": "medium_shot",
      "emotional_tone": "neutral",
      "keyframe_features": [0.234, -0.567, ...],
      "technical_quality": 0.89
    }
  ],
  "processing_time": 45.2
}
```

### Store Shot Data for Cinematic Database

Build a searchable database of cinematic shots for AI-powered recommendations.

```http
POST /api/v1/store-shot-data
Content-Type: application/json

{
  "video_asset_id": "video_file_id",
  "shots": [...],
  "scene_context": "Action sequence with car chase",
  "manual_tags": ["action", "chase", "urban", "fast_paced"]
}
```

### Get Cinematography Recommendations

AI-powered shot suggestions based on scene requirements.

```http
POST /api/v1/suggest-shots
Content-Type: application/json

{
  "scene_description": "Dramatic confrontation between two characters",
  "emotional_tone": "tense",
  "genre_context": "thriller",
  "desired_tags": ["close_up", "dramatic"],
  "limit": 5
}
```

**Response:**
```json
{
  "scene_description": "Dramatic confrontation between two characters",
  "suggested_shots": [
    {
      "shot_id": "shot_123",
      "video_asset_id": "reference_video",
      "movement_type": "close_up",
      "emotional_tone": "tense",
      "similarity_score": 0.92,
      "tags": ["close_up", "dramatic", "tension"],
      "technical_notes": "Tight framing emphasizes character emotion"
    }
  ],
  "total_suggestions": 5,
  "processing_time": 1.2
}
```

## 🔍 Advanced Analytics

### Similarity Analysis

Compare multiple assets to find the most similar content.

```http
POST /api/v1/find-best-match
Content-Type: application/json

{
  "reference_asset_id": "reference_image_id",
  "candidate_asset_ids": ["candidate1", "candidate2", "candidate3"]
}
```

**Response:**
```json
{
  "reference_asset_id": "reference_image_id",
  "candidates_processed": 3,
  "best_match": {
    "asset_id": "candidate2",
    "filename": "similar_image.jpg",
    "similarity_percentage": 89.3,
    "cosine_similarity": 0.893,
    "euclidean_distance": 0.156
  },
  "ranked_results": [...],
  "processing_time": 0.78
}
```

### Semantic Search

Content-based image retrieval using natural language descriptions.

```http
POST /api/v1/semantic-search
Content-Type: application/json

{
  "query_text": "red sports car in urban setting",
  "asset_ids": ["id1", "id2", "id3"],
  "limit": 10
}
```

### Batch Processing

Efficient processing of multiple assets simultaneously.

```http
POST /api/v1/batch-similarity
Content-Type: application/json

{
  "asset_ids": ["id1", "id2", "id3", "id4"],
  "comparison_type": "all_pairs"
}
```

**Response:**
```json
{
  "similarity_matrix": [
    [1.0, 0.75, 0.45, 0.23],
    [0.75, 1.0, 0.67, 0.34],
    [0.45, 0.67, 1.0, 0.56],
    [0.23, 0.34, 0.56, 1.0]
  ],
  "asset_ids": ["id1", "id2", "id3", "id4"],
  "processing_time": 2.1
}
```

## 🛠️ System Utilities

### Health Check

Monitor service status and GPU availability.

```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-01T11:33:25Z",
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

### Configuration Management

Update processing thresholds and parameters.

```http
PUT /api/v1/config/similarity-threshold
Content-Type: application/json

{
  "threshold": 0.75
}
```

## 📊 Integration Examples

### Python Integration

```python
import requests
import json

class DINOv3Client:
    def __init__(self, base_url="http://localhost:3012"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
    
    def upload_image(self, image_path):
        """Upload an image and return asset ID."""
        with open(image_path, 'rb') as f:
            response = requests.post(
                f"{self.api_base}/upload-media",
                files={'file': f}
            )
        return response.json()['asset_id']
    
    def extract_features(self, asset_id):
        """Extract DINOv3 features from uploaded asset."""
        response = requests.post(
            f"{self.api_base}/extract-features",
            json={'asset_id': asset_id}
        )
        return response.json()
    
    def check_character_consistency(self, ref_id, test_id):
        """Validate if two images show the same character."""
        response = requests.post(
            f"{self.api_base}/validate-consistency",
            json={
                'asset_id_1': ref_id,
                'asset_id_2': test_id
            }
        )
        return response.json()
    
    def analyze_quality(self, asset_id):
        """Get quality analysis for an asset."""
        response = requests.post(
            f"{self.api_base}/analyze-quality",
            json={'asset_id': asset_id}
        )
        return response.json()

# Usage Example
client = DINOv3Client()

# Upload and analyze character reference
ref_id = client.upload_image("character_reference.jpg")
client.extract_features(ref_id)

# Upload test image
test_id = client.upload_image("character_test.jpg")
client.extract_features(test_id)

# Check consistency
consistency = client.check_character_consistency(ref_id, test_id)
print(f"Same character: {consistency['same_character']}")
print(f"Similarity: {consistency['similarity_score']:.1f}%")

# Quality analysis
quality = client.analyze_quality(test_id)
print(f"Quality score: {quality['quality_score']:.1f}")
```

### JavaScript/Node.js Integration

```javascript
class DINOv3Client {
    constructor(baseUrl = 'http://localhost:3012') {
        this.baseUrl = baseUrl;
        this.apiBase = `${baseUrl}/api/v1`;
    }

    async uploadImage(imageBuffer, filename) {
        const formData = new FormData();
        formData.append('file', new Blob([imageBuffer]), filename);
        
        const response = await fetch(`${this.apiBase}/upload-media`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        return result.asset_id;
    }

    async extractFeatures(assetId) {
        const response = await fetch(`${this.apiBase}/extract-features`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ asset_id: assetId })
        });
        
        return await response.json();
    }

    async validateConsistency(assetId1, assetId2) {
        const response = await fetch(`${this.apiBase}/validate-consistency`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                asset_id_1: assetId1,
                asset_id_2: assetId2
            })
        });
        
        return await response.json();
    }
}

// Usage
const client = new DINOv3Client();

// Process character images
const refId = await client.uploadImage(referenceImageBuffer, 'ref.jpg');
await client.extractFeatures(refId);

const testId = await client.uploadImage(testImageBuffer, 'test.jpg');
await client.extractFeatures(testId);

const consistency = await client.validateConsistency(refId, testId);
console.log(`Character match: ${consistency.same_character}`);
```

## ⚠️ Error Handling

### Standard Error Response Format

```json
{
  "error": {
    "code": "ASSET_NOT_FOUND",
    "message": "Asset ID not found in database",
    "details": "The specified asset ID does not exist or has been deleted",
    "timestamp": "2025-09-01T11:33:25Z"
  }
}
```

### Common Error Codes

| Code | Status | Description | Solution |
|------|--------|-------------|----------|
| `ASSET_NOT_FOUND` | 404 | Asset ID not found | Verify asset ID exists |
| `INVALID_FILE_FORMAT` | 400 | Unsupported file format | Use JPG, PNG, WEBP, or MP4 |
| `FILE_TOO_LARGE` | 413 | File exceeds 50MB limit | Compress or resize file |
| `GPU_MEMORY_ERROR` | 500 | Insufficient GPU memory | Reduce batch size or wait |
| `MODEL_NOT_LOADED` | 503 | DINOv3 model unavailable | Check service health |
| `PROCESSING_FAILED` | 500 | Feature extraction failed | Retry or check image quality |

### Error Handling Best Practices

```python
def safe_api_call(func, *args, **kwargs):
    """Wrapper for safe API calls with retry logic."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 503:  # Service unavailable
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            elif e.response.status_code == 413:  # File too large
                raise ValueError("File too large - compress before upload")
            else:
                raise
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(1)
    
    raise Exception(f"Failed after {max_retries} attempts")
```

## 🚀 Performance Optimization

### Caching Strategy
- **Feature vectors**: Cached for 24 hours in Redis
- **Similarity results**: Cached for 1 hour
- **Preprocessed images**: Cached for 6 hours

### Batch Processing Guidelines
- **Optimal batch size**: 16-32 assets for GPU memory efficiency
- **Use batch endpoints**: For multiple operations to reduce overhead
- **Async processing**: Large batches process asynchronously

### Rate Limits
- **Default**: 100 requests/minute per IP
- **Batch operations**: 10 requests/minute per IP
- **Upload operations**: 50 requests/minute per IP

## 📈 Monitoring & Analytics

### Performance Metrics

```http
GET /api/v1/metrics
```

Returns Prometheus-compatible metrics for monitoring processing times, GPU utilization, and error rates.

### Processing Statistics

```http
GET /api/v1/stats
```

Get detailed statistics about processing volumes, average response times, and system performance.

## 🎯 Use Cases

### Animation & Game Development
- **Character consistency**: Ensure characters look consistent across scenes
- **Asset quality control**: Automated quality assessment for art pipelines
- **Style matching**: Find assets matching specific visual styles

### Content Creation & Media
- **Video shot analysis**: Automatic shot detection and categorization
- **Cinematic recommendations**: AI-powered suggestions for shot composition
- **Content similarity**: Find similar content for recommendations

### E-commerce & Product Catalogs
- **Visual search**: Find products by image similarity
- **Quality assessment**: Automated product image quality control
- **Duplicate detection**: Identify duplicate or near-duplicate products

### Security & Surveillance
- **Person identification**: Character/person consistency across footage
- **Anomaly detection**: Identify unusual patterns in visual content
- **Content verification**: Validate authenticity of visual content

## 🔧 Configuration & Deployment

### Environment Variables

```env
# Core Service Configuration
MONGODB_URL=mongodb://localhost:27017/dinov3_db
REDIS_URL=redis://localhost:6379/0
API_HOST=0.0.0.0
API_PORT=3012

# DINOv3 Model Configuration
DINOV3_MODEL_NAME=models/dinov3-vitb16-pretrain-lvd1689m
DINOV3_DEVICE=cuda
DINOV3_BATCH_SIZE=32

# Storage Configuration (Cloudflare R2)
CLOUDFLARE_R2_ENDPOINT=https://account-id.r2.cloudflarestorage.com
CLOUDFLARE_R2_ACCESS_KEY_ID=your_access_key
CLOUDFLARE_R2_SECRET_ACCESS_KEY=your_secret_key
CLOUDFLARE_R2_BUCKET_NAME=your_bucket

# Processing Limits
MAX_FILE_SIZE_MB=50
MAX_BATCH_SIZE=100
```

### System Requirements
- **GPU**: NVIDIA GPU with 8GB+ VRAM (RTX 4060 Ti 16GB recommended)
- **RAM**: 16GB+ system RAM
- **Storage**: 10GB+ free space
- **OS**: Windows 11, Ubuntu 20.04+, or macOS with CUDA support

### Docker Deployment

```yaml
version: '3.8'
services:
  dinov3-service:
    image: dinov3-utilities:latest
    ports:
      - "3012:3012"
    environment:
      - MONGODB_URL=mongodb://mongo:27017/dinov3_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - mongo
      - redis
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

---

## 📞 Support & Resources

- **API Documentation**: `/docs` (interactive Swagger UI)
- **Health Monitoring**: `/api/v1/health`
- **Performance Metrics**: `/api/v1/metrics`
- **GitHub Repository**: [Your repository URL]
- **Issues & Support**: [Your support channel]

**Ready to power your applications with AI-driven visual intelligence! 🚀**
