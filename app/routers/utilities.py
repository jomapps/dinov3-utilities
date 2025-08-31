from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import torch
import psutil
import time
from loguru import logger

# Database imports removed - using MongoDB with Beanie
from app.core.dinov3_service import DINOv3Service
from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Service health check and model status."""
    start_time = time.time()
    
    try:
        # System information
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # GPU information
        gpu_info = {}
        if torch.cuda.is_available():
            gpu_info = {
                "available": True,
                "device_count": torch.cuda.device_count(),
                "current_device": torch.cuda.current_device(),
                "device_name": torch.cuda.get_device_name(),
                "memory_allocated": torch.cuda.memory_allocated() / 1024**3,  # GB
                "memory_reserved": torch.cuda.memory_reserved() / 1024**3,   # GB
                "memory_total": torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB
            }
        else:
            gpu_info = {"available": False}
        
        # Import the global dinov3_service from main
        from app.main import dinov3_service

        # Model status
        model_status = {
            "loaded": dinov3_service is not None and dinov3_service.model is not None,
            "device": str(dinov3_service.device) if dinov3_service and dinov3_service.device else None,
            "model_name": settings.DINOV3_MODEL_NAME
        }

        # Redis status
        redis_status = {"connected": False}
        if dinov3_service and dinov3_service.redis:
            try:
                await dinov3_service.redis.ping()
                redis_status = {"connected": True}
            except:
                redis_status = {"connected": False, "error": "Ping failed"}
        
        processing_time = time.time() - start_time
        
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / 1024**3
            },
            "gpu": gpu_info,
            "model": model_status,
            "redis": redis_status,
            "processing_time": processing_time
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }

@router.get("/model-info")
async def get_model_info() -> Dict[str, Any]:
    """Get information about loaded DINOv3 model."""
    try:
        # Import the global dinov3_service from main
        from app.main import dinov3_service

        if not dinov3_service or not dinov3_service.model:
            raise HTTPException(status_code=503, detail="Model not loaded")
        
        # Model configuration
        model_config = {
            "model_name": settings.DINOV3_MODEL_NAME,
            "architecture": "Vision Transformer",
            "patch_size": 16,
            "embedding_dim": 384,
            "device": str(dinov3_service.device),
            "batch_size": settings.DINOV3_BATCH_SIZE
        }
        
        # Model capabilities
        capabilities = {
            "feature_extraction": True,
            "similarity_calculation": True,
            "quality_analysis": True,
            "batch_processing": True,
            "video_analysis": True,
            "character_consistency": True
        }
        
        # Processing limits
        limits = {
            "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
            "max_batch_size": settings.MAX_BATCH_SIZE,
            "request_timeout_seconds": settings.REQUEST_TIMEOUT_SECONDS
        }
        
        return {
            "model_config": model_config,
            "capabilities": capabilities,
            "limits": limits,
            "status": "ready"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Model info retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
