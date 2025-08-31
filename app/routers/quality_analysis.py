from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any
import time
import numpy as np
from PIL import Image
import io
from loguru import logger

from app.core.database import get_db, MediaAsset, QualityAnalysis
from app.core.storage import storage_service
from app.core.dinov3_service import DINOv3Service

router = APIRouter()

class QualityRequest(BaseModel):
    asset_id: str

@router.post("/analyze-quality")
async def analyze_quality(
    request: QualityRequest,
    db: AsyncSession = Depends(get_db),
    dinov3_service: DINOv3Service = Depends()
) -> Dict[str, Any]:
    """Comprehensive image quality analysis using DINOv3 features."""
    start_time = time.time()
    
    try:
        # Get asset from database
        result = await db.execute(select(MediaAsset).where(MediaAsset.id == request.asset_id))
        asset = result.scalar_one_or_none()
        
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        if not asset.features_extracted:
            raise HTTPException(status_code=400, detail="Features not extracted. Extract features first.")
        
        # Get features and analyze quality
        features = np.array(asset.features)
        quality_metrics = dinov3_service.analyze_quality(features)
        
        # Store results in database
        quality_analysis = QualityAnalysis(
            asset_id=request.asset_id,
            quality_score=quality_metrics["quality_score"],
            diversity_score=quality_metrics["diversity_score"],
            feature_mean=quality_metrics["feature_mean"],
            feature_std=quality_metrics["feature_std"],
            feature_max=quality_metrics["feature_max"],
            feature_min=quality_metrics["feature_min"],
            processing_time=time.time() - start_time
        )
        
        db.add(quality_analysis)
        await db.commit()
        
        processing_time = time.time() - start_time
        
        return {
            "asset_id": request.asset_id,
            "quality_score": quality_metrics["quality_score"],
            "diversity_score": quality_metrics["diversity_score"],
            "feature_statistics": {
                "mean": quality_metrics["feature_mean"],
                "std": quality_metrics["feature_std"],
                "max": quality_metrics["feature_max"],
                "min": quality_metrics["feature_min"]
            },
            "processing_time": processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quality analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-image-metrics")
async def analyze_image_metrics(
    request: QualityRequest,
    db: AsyncSession = Depends(get_db),
    dinov3_service: DINOv3Service = Depends()
) -> Dict[str, Any]:
    """Detailed image quality metrics including sharpness, lighting, composition."""
    start_time = time.time()
    
    try:
        # Get asset from database
        result = await db.execute(select(MediaAsset).where(MediaAsset.id == request.asset_id))
        asset = result.scalar_one_or_none()
        
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        # Download image from storage
        await storage_service.initialize()
        image_data = await storage_service.download_file(asset.r2_object_key)
        image = Image.open(io.BytesIO(image_data))
        
        # Analyze image metrics
        image_metrics = dinov3_service.analyze_image_metrics(image)
        
        # If features are available, also get DINOv3-based quality
        dinov3_quality = None
        if asset.features_extracted:
            features = np.array(asset.features)
            dinov3_quality = dinov3_service.analyze_quality(features)
        
        # Update quality analysis in database if exists
        if dinov3_quality:
            # Check if quality analysis exists
            quality_result = await db.execute(
                select(QualityAnalysis).where(QualityAnalysis.asset_id == request.asset_id)
            )
            existing_analysis = quality_result.scalar_one_or_none()
            
            if existing_analysis:
                # Update with image metrics
                existing_analysis.sharpness_score = image_metrics["sharpness_score"]
                existing_analysis.lighting_quality = image_metrics["lighting_quality"]
                existing_analysis.composition_score = image_metrics["composition_score"]
            else:
                # Create new analysis
                quality_analysis = QualityAnalysis(
                    asset_id=request.asset_id,
                    quality_score=dinov3_quality["quality_score"],
                    diversity_score=dinov3_quality["diversity_score"],
                    sharpness_score=image_metrics["sharpness_score"],
                    lighting_quality=image_metrics["lighting_quality"],
                    composition_score=image_metrics["composition_score"],
                    feature_mean=dinov3_quality["feature_mean"],
                    feature_std=dinov3_quality["feature_std"],
                    feature_max=dinov3_quality["feature_max"],
                    feature_min=dinov3_quality["feature_min"],
                    processing_time=time.time() - start_time
                )
                db.add(quality_analysis)
            
            await db.commit()
        
        processing_time = time.time() - start_time
        
        return {
            "asset_id": request.asset_id,
            "sharpness_score": image_metrics["sharpness_score"],
            "lighting_quality": image_metrics["lighting_quality"],
            "composition_score": image_metrics["composition_score"],
            "overall_quality": image_metrics["overall_quality"],
            "dinov3_quality": dinov3_quality["quality_score"] if dinov3_quality else None,
            "processing_time": processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image metrics analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
