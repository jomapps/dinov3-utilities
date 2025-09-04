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
    file: UploadFile = File(...)
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
        
        # Validate content type with improved detection
        def is_valid_image_content_type(content_type, filename):
            """Check if content type indicates an image file."""
            # Direct image content type check
            if content_type and content_type.startswith('image/'):
                return True

            # Check file extension if content type is missing or generic
            if filename:
                import mimetypes
                guessed_type, _ = mimetypes.guess_type(filename)
                if guessed_type and guessed_type.startswith('image/'):
                    return True

            # Allow common generic types that might contain images
            generic_types = ['application/octet-stream', 'binary/octet-stream']
            if content_type in generic_types and filename:
                # Check if filename has image extension
                image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.svg']
                filename_lower = filename.lower()
                if any(filename_lower.endswith(ext) for ext in image_extensions):
                    return True

            return False

        if not is_valid_image_content_type(file.content_type, file.filename):
            raise HTTPException(
                status_code=400,
                detail="Only image files are supported. Please ensure the file has an image content-type or proper file extension."
            )
        
        # Upload to storage
        await storage_service.initialize()

        # Ensure content_type is not None for storage service
        content_type_for_storage = file.content_type
        if not content_type_for_storage:
            # Guess content type from filename
            import mimetypes
            guessed_type, _ = mimetypes.guess_type(file.filename or '')
            content_type_for_storage = guessed_type or 'application/octet-stream'

        upload_result = await storage_service.upload_file(
            file_data, file.filename, content_type_for_storage
        )
        
        # Extract image metadata and validate it's actually an image
        try:
            image = Image.open(io.BytesIO(file_data))
            width, height = image.size
            format_name = image.format

            # Validate image dimensions
            if not width or not height or width <= 0 or height <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid image file: image has invalid dimensions"
                )

        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # If we can't read as image, it's not a valid image file
            logger.error(f"Failed to process image file: {e}")
            raise HTTPException(
                status_code=400,
                detail="Invalid image file: file is not a valid image or is corrupted"
            )
        
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
