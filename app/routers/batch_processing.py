from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List
import time
import numpy as np
from loguru import logger

from app.core.database import MediaAsset
from app.core.dinov3_service import DINOv3Service
from app.core.config import settings

router = APIRouter()

class BatchSimilarityRequest(BaseModel):
    asset_ids: List[str]

class BatchQualityRequest(BaseModel):
    asset_ids: List[str]

@router.post("/batch-similarity")
async def batch_similarity(
    request: BatchSimilarityRequest,
    dinov3_service: DINOv3Service = Depends()
) -> Dict[str, Any]:
    """Calculate similarity matrix for multiple assets."""
    start_time = time.time()
    
    try:
        # Validate batch size
        if len(request.asset_ids) > settings.MAX_BATCH_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Batch size too large. Maximum: {settings.MAX_BATCH_SIZE}"
            )
        
        # Get all assets with features
        assets_with_features = []
        asset_info = {}
        
        for asset_id in request.asset_ids:
            asset = await MediaAsset.get(asset_id)
            
            if asset and asset.features_extracted:
                features = np.array(asset.features)
                assets_with_features.append(features)
                asset_info[asset_id] = {
                    "filename": asset.filename,
                    "index": len(assets_with_features) - 1
                }
        
        if len(assets_with_features) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 assets with extracted features required"
            )
        
        # Calculate similarity matrix
        similarity_matrix = dinov3_service.calculate_similarity_matrix(assets_with_features)
        
        # Format results
        matrix_results = []
        for i, asset_id_1 in enumerate(request.asset_ids):
            if asset_id_1 in asset_info:
                row_results = []
                for j, asset_id_2 in enumerate(request.asset_ids):
                    if asset_id_2 in asset_info:
                        idx_1 = asset_info[asset_id_1]["index"]
                        idx_2 = asset_info[asset_id_2]["index"]
                        similarity = float(similarity_matrix[idx_1][idx_2])
                        row_results.append({
                            "asset_id": asset_id_2,
                            "similarity_percentage": similarity
                        })
                
                matrix_results.append({
                    "asset_id": asset_id_1,
                    "similarities": row_results
                })
        
        processing_time = time.time() - start_time
        
        return {
            "assets_processed": len(assets_with_features),
            "similarity_matrix": matrix_results,
            "matrix_shape": [len(assets_with_features), len(assets_with_features)],
            "processing_time": processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch similarity calculation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-quality-check")
async def batch_quality_check(
    request: BatchQualityRequest,
    dinov3_service: DINOv3Service = Depends()
) -> Dict[str, Any]:
    """Analyze quality for multiple assets in batch."""
    start_time = time.time()
    
    try:
        # Validate batch size
        if len(request.asset_ids) > settings.MAX_BATCH_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Batch size too large. Maximum: {settings.MAX_BATCH_SIZE}"
            )
        
        quality_results = []
        processed_count = 0
        
        for asset_id in request.asset_ids:
            try:
                # Get asset
                asset = await MediaAsset.get(asset_id)
                
                if not asset:
                    quality_results.append({
                        "asset_id": asset_id,
                        "error": "Asset not found",
                        "quality_score": None
                    })
                    continue
                
                if not asset.features_extracted:
                    quality_results.append({
                        "asset_id": asset_id,
                        "error": "Features not extracted",
                        "quality_score": None
                    })
                    continue
                
                # Analyze quality
                features = np.array(asset.features)
                quality_metrics = dinov3_service.analyze_quality(features)
                
                quality_results.append({
                    "asset_id": asset_id,
                    "filename": asset.filename,
                    "quality_score": quality_metrics["quality_score"],
                    "diversity_score": quality_metrics["diversity_score"],
                    "feature_statistics": {
                        "mean": quality_metrics["feature_mean"],
                        "std": quality_metrics["feature_std"],
                        "max": quality_metrics["feature_max"],
                        "min": quality_metrics["feature_min"]
                    },
                    "error": None
                })
                
                processed_count += 1
                
            except Exception as e:
                quality_results.append({
                    "asset_id": asset_id,
                    "error": str(e),
                    "quality_score": None
                })
        
        # Calculate batch statistics
        valid_scores = [r["quality_score"] for r in quality_results if r["quality_score"] is not None]
        batch_stats = {}
        
        if valid_scores:
            batch_stats = {
                "mean_quality": float(np.mean(valid_scores)),
                "std_quality": float(np.std(valid_scores)),
                "min_quality": float(np.min(valid_scores)),
                "max_quality": float(np.max(valid_scores)),
                "median_quality": float(np.median(valid_scores))
            }
        
        processing_time = time.time() - start_time
        
        return {
            "total_assets": len(request.asset_ids),
            "processed_successfully": processed_count,
            "failed_assets": len(request.asset_ids) - processed_count,
            "quality_results": quality_results,
            "batch_statistics": batch_stats,
            "processing_time": processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch quality check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
