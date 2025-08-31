from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, List
import time
import numpy as np
from loguru import logger

from app.core.database import get_db, MediaAsset, CharacterConsistency
from app.core.dinov3_service import DINOv3Service

router = APIRouter()

class CharacterMatchingRequest(BaseModel):
    reference_asset_id: str
    test_asset_ids: List[str]

class GroupByCharacterRequest(BaseModel):
    asset_ids: List[str]
    similarity_threshold: float = 75.0

@router.post("/character-matching")
async def character_matching(
    request: CharacterMatchingRequest,
    db: AsyncSession = Depends(get_db),
    dinov3_service: DINOv3Service = Depends()
) -> Dict[str, Any]:
    """Advanced character consistency checking with detailed feedback."""
    start_time = time.time()
    
    try:
        # Get reference asset
        result = await db.execute(select(MediaAsset).where(MediaAsset.id == request.reference_asset_id))
        reference_asset = result.scalar_one_or_none()
        
        if not reference_asset or not reference_asset.features_extracted:
            raise HTTPException(status_code=404, detail="Reference asset not found or features not extracted")
        
        reference_features = np.array(reference_asset.features)
        consistency_results = []
        
        # Process each test asset
        for test_asset_id in request.test_asset_ids:
            try:
                result = await db.execute(select(MediaAsset).where(MediaAsset.id == test_asset_id))
                test_asset = result.scalar_one_or_none()
                
                if not test_asset or not test_asset.features_extracted:
                    consistency_results.append({
                        "test_asset_id": test_asset_id,
                        "error": "Asset not found or features not extracted",
                        "same_character": False,
                        "confidence_score": 0.0
                    })
                    continue
                
                test_features = np.array(test_asset.features)
                similarity_metrics = dinov3_service.calculate_similarity(reference_features, test_features)
                
                similarity_score = similarity_metrics["similarity_percentage"]
                same_character = similarity_score >= 75.0
                
                # Generate detailed confidence assessment
                if similarity_score >= 95:
                    confidence_level = "extremely_high"
                    explanation = "Extremely high similarity - definitely same character"
                elif similarity_score >= 85:
                    confidence_level = "very_high"
                    explanation = "Very high similarity - very likely same character"
                elif similarity_score >= 75:
                    confidence_level = "high"
                    explanation = "High similarity - likely same character"
                elif similarity_score >= 65:
                    confidence_level = "medium"
                    explanation = "Medium similarity - possibly same character with variations"
                elif similarity_score >= 50:
                    confidence_level = "low"
                    explanation = "Low similarity - unlikely same character"
                else:
                    confidence_level = "very_low"
                    explanation = "Very low similarity - definitely different character"
                
                # Store in database
                character_consistency = CharacterConsistency(
                    reference_asset_id=request.reference_asset_id,
                    test_asset_id=test_asset_id,
                    same_character=same_character,
                    confidence_score=similarity_score / 100.0,
                    similarity_score=similarity_score,
                    explanation=explanation,
                    processing_time=time.time() - start_time
                )
                
                db.add(character_consistency)
                
                consistency_results.append({
                    "test_asset_id": test_asset_id,
                    "filename": test_asset.filename,
                    "same_character": same_character,
                    "similarity_score": similarity_score,
                    "confidence_level": confidence_level,
                    "confidence_score": similarity_score / 100.0,
                    "explanation": explanation,
                    "cosine_similarity": similarity_metrics["cosine_similarity"],
                    "euclidean_distance": similarity_metrics["euclidean_distance"]
                })
                
            except Exception as e:
                consistency_results.append({
                    "test_asset_id": test_asset_id,
                    "error": str(e),
                    "same_character": False,
                    "confidence_score": 0.0
                })
        
        await db.commit()
        
        # Calculate summary statistics
        valid_results = [r for r in consistency_results if "error" not in r]
        same_character_count = sum(1 for r in valid_results if r["same_character"])
        avg_similarity = np.mean([r["similarity_score"] for r in valid_results]) if valid_results else 0
        
        processing_time = time.time() - start_time
        
        return {
            "reference_asset_id": request.reference_asset_id,
            "reference_filename": reference_asset.filename,
            "total_tested": len(request.test_asset_ids),
            "processed_successfully": len(valid_results),
            "same_character_count": same_character_count,
            "average_similarity": float(avg_similarity),
            "consistency_results": consistency_results,
            "processing_time": processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Character matching failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/group-by-character")
async def group_by_character(
    request: GroupByCharacterRequest,
    db: AsyncSession = Depends(get_db),
    dinov3_service: DINOv3Service = Depends()
) -> Dict[str, Any]:
    """Group assets by detected characters/persons."""
    start_time = time.time()
    
    try:
        # Get all assets with features
        assets_with_features = []
        asset_mapping = {}
        
        for asset_id in request.asset_ids:
            result = await db.execute(select(MediaAsset).where(MediaAsset.id == asset_id))
            asset = result.scalar_one_or_none()
            
            if asset and asset.features_extracted:
                features = np.array(asset.features)
                assets_with_features.append(features)
                asset_mapping[len(assets_with_features) - 1] = {
                    "asset_id": asset_id,
                    "filename": asset.filename
                }
        
        if len(assets_with_features) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 assets with features required for grouping"
            )
        
        # Calculate similarity matrix
        similarity_matrix = dinov3_service.calculate_similarity_matrix(assets_with_features)
        
        # Group assets based on similarity threshold
        groups = []
        assigned = set()
        
        for i in range(len(assets_with_features)):
            if i in assigned:
                continue
            
            # Start new group with current asset
            current_group = [i]
            assigned.add(i)
            
            # Find similar assets
            for j in range(i + 1, len(assets_with_features)):
                if j in assigned:
                    continue
                
                if similarity_matrix[i][j] >= request.similarity_threshold:
                    current_group.append(j)
                    assigned.add(j)
            
            # Convert indices to asset info
            group_assets = []
            for idx in current_group:
                asset_info = asset_mapping[idx]
                group_assets.append({
                    "asset_id": asset_info["asset_id"],
                    "filename": asset_info["filename"]
                })
            
            groups.append({
                "group_id": len(groups),
                "character_count": len(current_group),
                "assets": group_assets,
                "representative_asset": group_assets[0]  # First asset as representative
            })
        
        processing_time = time.time() - start_time
        
        return {
            "total_assets": len(request.asset_ids),
            "assets_with_features": len(assets_with_features),
            "similarity_threshold": request.similarity_threshold,
            "groups_found": len(groups),
            "character_groups": groups,
            "processing_time": processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Character grouping failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
