# DINOv3 Utilities - Project Structure

## 📁 Directory Overview

```
dinov3-utilities/
├── 📁 app/                          # Main application code
│   ├── 📁 core/                     # Core services and utilities
│   │   ├── config.py                # Configuration management
│   │   ├── database.py              # MongoDB with Beanie ODM
│   │   ├── dinov3_service.py        # DINOv3 model service
│   │   └── storage.py               # Cloudflare R2 storage service
│   ├── 📁 routers/                  # API endpoint routers
│   │   ├── analytics.py             # Advanced analytics endpoints
│   │   ├── batch_processing.py      # Batch operation endpoints
│   │   ├── character_analysis.py    # Character consistency endpoints
│   │   ├── feature_extraction.py    # Core feature extraction
│   │   ├── media_management.py      # Media upload/management
│   │   ├── production_services.py   # Production workflow endpoints
│   │   ├── quality_analysis.py      # Quality assessment endpoints
│   │   ├── similarity.py            # Similarity analysis endpoints
│   │   ├── utilities.py             # System utilities endpoints
│   │   └── video_analysis.py        # Video processing endpoints
│   └── main.py                      # FastAPI application entry point
├── 📁 docs/                         # Documentation
│   └── 📁 external-app-docs/        # External integration docs
│       └── how-to-use-pathrag.md    # PathRAG integration guide
├── 📁 models/                       # DINOv3 model files (gitignored)
│   └── dinov3-vitb16-pretrain-lvd1689m/  # Local model directory
├── 📁 scripts/                      # Utility scripts
│   ├── check_dinov3_model.ps1       # Model verification script
│   ├── install_pytorch.ps1          # PyTorch installation
│   ├── start_dev.ps1                # Development startup script
│   └── test_api.ps1                 # API testing script
├── 📁 test-data/                    # Test assets
│   ├── test_image.jpg               # Sample image for testing
│   └── test-video.mp4               # Sample video for testing
├── 📁 tests/                        # Test suite
│   ├── run_tests.py                 # Test runner
│   ├── simple_endpoint_test.py      # Basic endpoint tests
│   ├── test_all_endpoints.py        # Comprehensive test suite
│   ├── test_dinov3.py               # DINOv3 model tests
│   ├── test_dinov3_access.py        # Model access tests
│   ├── test_dinov3_model.py         # Model functionality tests
│   └── test_local_dinov3.py         # Local model tests
├── 📁 venv/                         # Python virtual environment (gitignored)
├── .env                             # Environment configuration
├── .gitignore                       # Git ignore rules
├── API_REFERENCE.md                 # Complete API documentation
├── DEPLOYMENT.md                    # Production deployment guide
├── PROJECT_STRUCTURE.md             # This file
├── README.md                        # Main project documentation
├── dinov3-service-list.md           # Service endpoint catalog
├── docker-compose.yml               # Docker services configuration
├── infra-requirements.md            # Infrastructure requirements
├── install_dependencies.py         # Dependency installation script
├── install_manual.py               # Manual installation script
├── minimal_dinov3_test.py           # Minimal model test
├── requirements.txt                 # Python dependencies
└── service-test-results.md          # Service status and test results
```

## 🏗️ Architecture Components

### Core Application (`app/`)

#### `app/main.py`
- **Purpose**: FastAPI application entry point
- **Features**: 
  - Application lifecycle management
  - Router registration
  - CORS configuration
  - Database initialization
  - DINOv3 service startup

#### `app/core/`
Core services that power the application:

**`config.py`**
- Environment variable management
- Settings validation with Pydantic
- Configuration for all services

**`database.py`**
- MongoDB connection with Beanie ODM
- Document models for media assets
- Database initialization and cleanup

**`dinov3_service.py`**
- DINOv3 model loading and management
- GPU memory optimization
- Feature extraction pipeline
- Redis caching integration

**`storage.py`**
- Cloudflare R2 integration
- File upload/download operations
- Presigned URL generation
- Asset management

#### `app/routers/`
API endpoint implementations organized by functionality:

- **`media_management.py`**: Upload, retrieve, delete media assets
- **`feature_extraction.py`**: Core DINOv3 feature extraction
- **`similarity.py`**: Similarity calculations and matching
- **`quality_analysis.py`**: Image quality assessment
- **`character_analysis.py`**: Character consistency validation
- **`batch_processing.py`**: Bulk operations and batch processing
- **`video_analysis.py`**: Video shot detection and analysis
- **`production_services.py`**: Production workflow endpoints
- **`analytics.py`**: Advanced analytics and clustering
- **`utilities.py`**: System health and configuration

### Documentation (`docs/`)

- **`external-app-docs/`**: Integration guides for external services
- **`how-to-use-pathrag.md`**: PathRAG integration documentation

### Models (`models/`)

- **`dinov3-vitb16-pretrain-lvd1689m/`**: Local DINOv3 model files
- Contains model weights, configuration, and tokenizer files
- Excluded from git due to large file sizes

### Scripts (`scripts/`)

Development and deployment automation:
- **`start_dev.ps1`**: Complete development environment setup
- **`test_api.ps1`**: API endpoint testing
- **`check_dinov3_model.ps1`**: Model verification
- **`install_pytorch.ps1`**: PyTorch installation with CUDA

### Tests (`tests/`)

Comprehensive test suite:
- **`test_all_endpoints.py`**: Full API endpoint testing
- **`simple_endpoint_test.py`**: Basic connectivity tests
- **`test_dinov3*.py`**: Model-specific tests
- **`run_tests.py`**: Test execution orchestration

### Configuration Files

- **`.env`**: Environment variables and secrets
- **`requirements.txt`**: Python package dependencies
- **`docker-compose.yml`**: Local service orchestration
- **`.gitignore`**: Version control exclusions

## 🔧 Key Design Patterns

### Dependency Injection
- Services are injected into routers using FastAPI's dependency system
- Enables easy testing and service swapping

### Async/Await Pattern
- All I/O operations are asynchronous
- Improves performance and scalability

### Configuration Management
- Centralized configuration with environment variable validation
- Type-safe settings using Pydantic

### Error Handling
- Consistent error responses across all endpoints
- Comprehensive logging for debugging

### Caching Strategy
- Redis caching for expensive operations
- Feature vector caching to improve response times

## 📦 Dependencies

### Core Dependencies
- **FastAPI**: Web framework and API documentation
- **Uvicorn**: ASGI server for production deployment
- **Pydantic**: Data validation and settings management
- **Beanie**: Async MongoDB ODM

### ML/AI Dependencies
- **PyTorch**: Deep learning framework
- **Transformers**: Hugging Face model integration
- **Timm**: Vision model implementations
- **Pillow**: Image processing
- **OpenCV**: Computer vision operations

### Storage & Database
- **Motor**: Async MongoDB driver
- **Redis**: Caching and session management
- **Boto3**: S3-compatible storage (Cloudflare R2)

### Utilities
- **Loguru**: Advanced logging
- **Python-dotenv**: Environment variable management
- **Psutil**: System monitoring

## 🚀 Development Workflow

1. **Setup**: Run `scripts/start_dev.ps1` for complete environment setup
2. **Development**: Edit code with hot-reload enabled
3. **Testing**: Use `tests/` directory for comprehensive testing
4. **Documentation**: Update relevant `.md` files
5. **Deployment**: Follow `DEPLOYMENT.md` for production setup

## 📊 Monitoring & Observability

### Logging
- Structured logging with Loguru
- Request/response logging
- Error tracking and debugging

### Health Checks
- `/api/v1/health` endpoint for system status
- GPU memory monitoring
- Database connection status
- Model loading verification

### Performance Metrics
- Processing time tracking
- Cache hit/miss ratios
- GPU utilization monitoring
- API response time measurement

---

This structure supports scalable development, easy testing, and production deployment while maintaining clean separation of concerns.
