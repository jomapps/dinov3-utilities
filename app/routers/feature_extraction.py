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

# Global variable to hold the service instance
_dinov3_service_instance = None

def set_dinov3_service(service: DINOv3Service):
    """Set the global DINOv3 service instance"""
    global _dinov3_service_instance
    _dinov3_service_instance = service
    print(f"DEBUG: DINOv3 service set in feature_extraction router: {service is not None}")

async def get_dinov3_service() -> DINOv3Service:
    """Get the DINOv3 service instance with multiple fallback strategies"""
    global _dinov3_service_instance

    # Strategy 1: Use the set instance
    if _dinov3_service_instance is not None:
        return _dinov3_service_instance

    # Strategy 2: Try to get from main module directly
    try:
        import sys
        if 'app.main' in sys.modules:
            main_module = sys.modules['app.main']
            if hasattr(main_module, 'dinov3_service') and main_module.dinov3_service is not None:
                # Cache it for future use
                _dinov3_service_instance = main_module.dinov3_service
                return main_module.dinov3_service
    except Exception as e:
        pass

    # Strategy 3: Create a new instance if needed (last resort)
    try:
        from app.core.dinov3_service import DINOv3Service
        service = DINOv3Service()
        await service.initialize()
        _dinov3_service_instance = service
        return service
    except Exception as e:
        pass

    raise HTTPException(status_code=503, detail="DINOv3 service not initialized")

@router.post("/extract-features")
async def extract_features(
    asset_id: str
) -> Dict[str, Any]:
    """Extract DINOv3 feature embeddings from a media asset."""
    start_time = time.time()
    
    try:
        # Get the DINOv3 service instance
        dinov3_service = await get_dinov3_service()

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
    asset_id: str
) -> Dict[str, Any]:
    """Preprocess image using DINOv3 standard pipeline."""
    start_time = time.time()
    
    try:
        # Get the DINOv3 service instance
        dinov3_service = await get_dinov3_service()

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
