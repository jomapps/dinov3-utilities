from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any
import time
from loguru import logger

from app.core.config import settings

router = APIRouter()

class QualityThresholdRequest(BaseModel):
    threshold: float

class SimilarityThresholdRequest(BaseModel):
    threshold: float

# Global configuration storage (in production, use database or Redis)
_config_store = {
    "quality_threshold": settings.DEFAULT_QUALITY_THRESHOLD,
    "similarity_threshold": settings.DEFAULT_SIMILARITY_THRESHOLD
}

@router.put("/config/quality-threshold")
async def update_quality_threshold(
    request: QualityThresholdRequest
) -> Dict[str, Any]:
    """Update quality threshold for analysis."""
    start_time = time.time()
    
    try:
        # Validate threshold range
        if not 0.0 <= request.threshold <= 1.0:
            raise HTTPException(
                status_code=400,
                detail="Quality threshold must be between 0.0 and 1.0"
            )
        
        # Update configuration
        _config_store["quality_threshold"] = request.threshold
        
        processing_time = time.time() - start_time
        
        return {
            "quality_threshold": request.threshold,
            "previous_threshold": settings.DEFAULT_QUALITY_THRESHOLD,
            "updated": True,
            "processing_time": processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quality threshold update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/config/similarity-threshold")
async def update_similarity_threshold(
    request: SimilarityThresholdRequest
) -> Dict[str, Any]:
    """Update similarity threshold for character matching."""
    start_time = time.time()
    
    try:
        # Validate threshold range
        if not 0.0 <= request.threshold <= 100.0:
            raise HTTPException(
                status_code=400,
                detail="Similarity threshold must be between 0.0 and 100.0"
            )
        
        # Update configuration
        _config_store["similarity_threshold"] = request.threshold
        
        processing_time = time.time() - start_time
        
        return {
            "similarity_threshold": request.threshold,
            "previous_threshold": settings.DEFAULT_SIMILARITY_THRESHOLD,
            "updated": True,
            "processing_time": processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Similarity threshold update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_configuration() -> Dict[str, Any]:
    """Get current configuration settings."""
    return {
        "quality_threshold": _config_store["quality_threshold"],
        "similarity_threshold": _config_store["similarity_threshold"],
        "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
        "max_batch_size": settings.MAX_BATCH_SIZE,
        "request_timeout_seconds": settings.REQUEST_TIMEOUT_SECONDS,
        "dinov3_batch_size": settings.DINOV3_BATCH_SIZE,
        "dinov3_device": settings.DINOV3_DEVICE,
        "site_url": settings.SITE_URL,
        "cors_origins": settings.CORS_ORIGINS
    }
