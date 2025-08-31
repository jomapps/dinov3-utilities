from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List
import time
import numpy as np
from loguru import logger

from app.core.database import MediaAsset, SimilarityResult
from app.core.dinov3_service import DINOv3Service

router = APIRouter()

class SimilarityRequest(BaseModel):
    asset_id_1: str
    asset_id_2: str

class BestMatchRequest(BaseModel):
    reference_asset_id: str
    candidate_asset_ids: List[str]

class ConsistencyRequest(BaseModel):
    asset_id_1: str
    asset_id_2: str

@router.post("/calculate-similarity")
async def calculate_similarity(
    request: SimilarityRequest,
    dinov3_service: DINOv3Service = Depends()
) -> Dict[str, Any]:
    """Calculate cosine similarity between two media assets using DINOv3 features."""
    start_time = time.time()
    
    try:
        # Get both assets
        result1 = await db.execute(select(MediaAsset).where(MediaAsset.id == request.asset_id_1))
        asset1 = result1.scalar_one_or_none()
        
        result2 = await db.execute(select(MediaAsset).where(MediaAsset.id == request.asset_id_2))
        asset2 = result2.scalar_one_or_none()
        
        if not asset1 or not asset2:
            raise HTTPException(status_code=404, detail="One or both assets not found")
        
        # Check if features are available
        if not asset1.features_extracted or not asset2.features_extracted:
            raise HTTPException(
                status_code=400, 
                detail="Features not extracted for one or both assets. Extract features first."
            )
        
        # Get features
        features1 = np.array(asset1.features)
        features2 = np.array(asset2.features)
        
        # Calculate similarity
        similarity_metrics = dinov3_service.calculate_similarity(features1, features2)
        
        # Store result in database
        similarity_result = SimilarityResult(
            asset_id_1=request.asset_id_1,
            asset_id_2=request.asset_id_2,
            similarity_score=similarity_metrics["similarity_percentage"],
            cosine_similarity=similarity_metrics["cosine_similarity"],
            euclidean_distance=similarity_metrics["euclidean_distance"],
            processing_time=time.time() - start_time
        )
        
        db.add(similarity_result)
        
        
        processing_time = time.time() - start_time
        
        return {
            "asset_id_1": request.asset_id_1,
            "asset_id_2": request.asset_id_2,
            "similarity_percentage": similarity_metrics["similarity_percentage"],
            "cosine_similarity": similarity_metrics["cosine_similarity"],
            "euclidean_distance": similarity_metrics["euclidean_distance"],
            "processing_time": processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Similarity calculation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/find-best-match")
async def find_best_match(
    request: BestMatchRequest,
    dinov3_service: DINOv3Service = Depends()
) -> Dict[str, Any]:
    """Find the best matching asset from a set of candidates against a reference asset."""
    start_time = time.time()
    
    try:
        # Get reference asset
        result = await db.execute(select(MediaAsset).where(MediaAsset.id == request.reference_asset_id))
        reference_asset = result.scalar_one_or_none()
        
        if not reference_asset or not reference_asset.features_extracted:
            raise HTTPException(status_code=404, detail="Reference asset not found or features not extracted")
        
        reference_features = np.array(reference_asset.features)
        
        # Get candidate assets
        candidate_results = []
        for candidate_id in request.candidate_asset_ids:
            candidate = await MediaAsset.get(candidate_id)
            
            if candidate and candidate.features_extracted:
                candidate_features = np.array(candidate.features)
                similarity_metrics = dinov3_service.calculate_similarity(reference_features, candidate_features)
                
                candidate_results.append({
                    "asset_id": candidate_id,
                    "filename": candidate.filename,
                    "similarity_percentage": similarity_metrics["similarity_percentage"],
                    "cosine_similarity": similarity_metrics["cosine_similarity"],
                    "euclidean_distance": similarity_metrics["euclidean_distance"]
                })
        
        # Sort by similarity score (descending)
        candidate_results.sort(key=lambda x: x["similarity_percentage"], reverse=True)
        
        processing_time = time.time() - start_time
        
        return {
            "reference_asset_id": request.reference_asset_id,
            "candidates_processed": len(candidate_results),
            "best_match": candidate_results[0] if candidate_results else None,
            "ranked_results": candidate_results,
            "processing_time": processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Best match search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate-consistency")
async def validate_consistency(
    request: ConsistencyRequest,
    dinov3_service: DINOv3Service = Depends()
) -> Dict[str, Any]:
    """Check if two assets show the same character/person with detailed analysis."""
    start_time = time.time()
    
    try:
        # Get both assets
        result1 = await db.execute(select(MediaAsset).where(MediaAsset.id == request.asset_id_1))
        asset1 = result1.scalar_one_or_none()
        
        result2 = await db.execute(select(MediaAsset).where(MediaAsset.id == request.asset_id_2))
        asset2 = result2.scalar_one_or_none()
        
        if not asset1 or not asset2:
            raise HTTPException(status_code=404, detail="One or both assets not found")
        
        if not asset1.features_extracted or not asset2.features_extracted:
            raise HTTPException(
                status_code=400, 
                detail="Features not extracted for one or both assets"
            )
        
        # Get features and calculate similarity
        features1 = np.array(asset1.features)
        features2 = np.array(asset2.features)
        similarity_metrics = dinov3_service.calculate_similarity(features1, features2)
        
        # Determine if same character based on threshold
        similarity_score = similarity_metrics["similarity_percentage"]
        same_character = similarity_score >= 75.0  # Configurable threshold
        
        # Generate confidence explanation
        if similarity_score >= 90:
            confidence_level = "very_high"
            explanation = "Very high similarity indicates likely same character/person"
        elif similarity_score >= 75:
            confidence_level = "high"
            explanation = "High similarity suggests same character/person"
        elif similarity_score >= 60:
            confidence_level = "medium"
            explanation = "Medium similarity - possibly same character with different conditions"
        elif similarity_score >= 40:
            confidence_level = "low"
            explanation = "Low similarity - likely different characters"
        else:
            confidence_level = "very_low"
            explanation = "Very low similarity - definitely different characters"
        
        processing_time = time.time() - start_time
        
        return {
            "asset_id_1": request.asset_id_1,
            "asset_id_2": request.asset_id_2,
            "same_character": same_character,
            "similarity_score": similarity_score,
            "confidence_level": confidence_level,
            "explanation": explanation,
            "cosine_similarity": similarity_metrics["cosine_similarity"],
            "euclidean_distance": similarity_metrics["euclidean_distance"],
            "processing_time": processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Consistency validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
