from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import time
from PIL import Image
import io
from datetime import datetime
from loguru import logger

from app.core.database import MediaAsset
from app.core.storage import storage_service
from app.core.dinov3_service import DINOv3Service

router = APIRouter()

@router.post("/extract-features")
async def extract_features(
    asset_id: str,
    dinov3_service: DINOv3Service = Depends()
) -> Dict[str, Any]:
    """Extract DINOv3 feature embeddings from a media asset."""
    start_time = time.time()
    
    try:
        # Get asset from database
        asset = await MediaAsset.get(asset_id)

        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        # Check if features already extracted
        if asset.features_extracted and asset.features is not None:
            return {
                "asset_id": asset_id,
                "features": asset.features,
                "features_extracted": True,
                "features_timestamp": asset.features_timestamp.isoformat(),
                "processing_time": 0.0,
                "cached": True
            }
        
        # Update status to processing
        asset.processing_status = "processing"
        await asset.save()
        
        # Download image from storage
        await storage_service.initialize()
        image_data = await storage_service.download_file(asset.r2_object_key)
        
        # Load image
        image = Image.open(io.BytesIO(image_data))
        
        # Extract features
        features = await dinov3_service.extract_features(image)
        
        # Cache features
        await dinov3_service.cache_features(asset_id, features)
        
        # Update database with features
        asset.features = features.tolist()
        asset.features_extracted = True
        asset.features_timestamp = datetime.utcnow()
        asset.processing_status = "completed"
        await asset.save()
        
        processing_time = time.time() - start_time
        
        return {
            "asset_id": asset_id,
            "features": features.tolist(),
            "features_extracted": True,
            "features_timestamp": datetime.utcnow().isoformat(),
            "processing_time": processing_time,
            "cached": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Update status to error
        try:
            asset = await MediaAsset.get(asset_id)
            if asset:
                asset.processing_status = "error"
                asset.error_message = str(e)
                await asset.save()
        except:
            pass  # Don't fail if we can't update error status
        
        logger.error(f"Feature extraction failed for {asset_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/preprocess-image")
async def preprocess_image(
    asset_id: str,
    dinov3_service: DINOv3Service = Depends()
) -> Dict[str, Any]:
    """Preprocess image using DINOv3 standard pipeline."""
    start_time = time.time()
    
    try:
        # Get asset from database
        asset = await MediaAsset.get(asset_id)

        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        # Download image from storage
        await storage_service.initialize()
        image_data = await storage_service.download_file(asset.r2_object_key)
        
        # Load and preprocess image
        image = Image.open(io.BytesIO(image_data))
        preprocessed_tensor = dinov3_service.preprocess_image(image)
        
        processing_time = time.time() - start_time
        
        return {
            "asset_id": asset_id,
            "preprocessed": True,
            "tensor_shape": list(preprocessed_tensor.shape),
            "device": str(preprocessed_tensor.device),
            "dtype": str(preprocessed_tensor.dtype),
            "processing_time": processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image preprocessing failed for {asset_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
