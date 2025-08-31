from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import time
from PIL import Image
import io
from loguru import logger

from app.core.database import MediaAsset
from app.core.storage import storage_service
from app.core.dinov3_service import DINOv3Service
from app.core.config import settings

router = APIRouter()

@router.post("/upload-media")
async def upload_media(
    file: UploadFile = File(...),
    dinov3_service: DINOv3Service = Depends()
) -> Dict[str, Any]:
    """Upload media asset to R2 and register in system."""
    start_time = time.time()
    
    try:
        # Validate file size
        file_data = await file.read()
        if len(file_data) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB}MB"
            )
        
        # Validate content type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="Only image files are supported"
            )
        
        # Upload to storage
        await storage_service.initialize()
        upload_result = await storage_service.upload_file(
            file_data, file.filename, file.content_type
        )
        
        # Extract image metadata
        try:
            image = Image.open(io.BytesIO(file_data))
            width, height = image.size
            format_name = image.format
        except Exception as e:
            logger.warning(f"Could not extract image metadata: {e}")
            width = height = format_name = None
        
        # Create database record
        asset = MediaAsset(
            filename=file.filename,
            content_type=file.content_type,
            file_size=len(file_data),
            r2_object_key=upload_result["object_key"],
            public_url=upload_result["public_url"],
            width=width,
            height=height,
            format=format_name,
            processing_status="uploaded"
        )
        
        await asset.insert()
        
        processing_time = time.time() - start_time
        
        return {
            "asset_id": asset.id,
            "filename": asset.filename,
            "content_type": asset.content_type,
            "file_size": asset.file_size,
            "public_url": asset.public_url,
            "width": asset.width,
            "height": asset.height,
            "format": asset.format,
            "upload_timestamp": asset.upload_timestamp.isoformat(),
            "processing_status": asset.processing_status,
            "processing_time": processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/media/{asset_id}")
async def get_media(
    asset_id: str
) -> Dict[str, Any]:
    """Retrieve media asset information and access URL."""
    try:
        asset = await MediaAsset.get(asset_id)

        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        return {
            "asset_id": asset.id,
            "filename": asset.filename,
            "content_type": asset.content_type,
            "file_size": asset.file_size,
            "public_url": asset.public_url,
            "width": asset.width,
            "height": asset.height,
            "format": asset.format,
            "upload_timestamp": asset.upload_timestamp.isoformat(),
            "processing_status": asset.processing_status,
            "features_extracted": asset.features_extracted,
            "features_timestamp": asset.features_timestamp.isoformat() if asset.features_timestamp else None,
            "error_message": asset.error_message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get media failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/media/{asset_id}")
async def delete_media(
    asset_id: str
) -> Dict[str, Any]:
    """Remove media asset from R2 and database."""
    try:
        asset = await MediaAsset.get(asset_id)

        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")

        # Delete from storage
        await storage_service.initialize()
        storage_deleted = await storage_service.delete_file(asset.r2_object_key)

        # Delete from database
        await asset.delete()
        await db.commit()
        
        return {
            "asset_id": asset_id,
            "deleted": True,
            "storage_deleted": storage_deleted,
            "message": "Asset deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete media failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
