from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List
import time
import numpy as np
from loguru import logger

from app.core.database import MediaAsset
from app.core.dinov3_service import DINOv3Service

router = APIRouter()

class ShotConsistencyRequest(BaseModel):
    shot_asset_ids: List[str]
    character_reference_asset_id: str

class ReferenceEnforcementRequest(BaseModel):
    master_reference_asset_id: str
    generated_asset_ids: List[str]
    compliance_threshold: float = 80.0

@router.post("/validate-shot-consistency")
async def validate_shot_consistency(
    request: ShotConsistencyRequest,
    dinov3_service: DINOv3Service = Depends()
) -> Dict[str, Any]:
    """Validate character consistency across cinematic shots."""
    start_time = time.time()
    
    try:
        # Get character reference asset
        result = await db.execute(select(MediaAsset).where(MediaAsset.id == request.character_reference_asset_id))
        reference_asset = result.scalar_one_or_none()
        
        if not reference_asset or not reference_asset.features_extracted:
            raise HTTPException(status_code=404, detail="Character reference asset not found or features not extracted")
        
        reference_features = np.array(reference_asset.features)
        shot_validations = []
        
        # Validate each shot
        for i, shot_asset_id in enumerate(request.shot_asset_ids):
            try:
                shot_asset = await MediaAsset.get(shot_asset_id)
                
                if not shot_asset or not shot_asset.features_extracted:
                    shot_validations.append({
                        "shot_index": i,
                        "shot_asset_id": shot_asset_id,
                        "error": "Shot asset not found or features not extracted",
                        "consistent": False,
                        "similarity_score": 0.0
                    })
                    continue
                
                shot_features = np.array(shot_asset.features)
                similarity_metrics = dinov3_service.calculate_similarity(reference_features, shot_features)
                
                similarity_score = similarity_metrics["similarity_percentage"]
                consistent = similarity_score >= 70.0  # Production threshold
                
                # Determine validation status
                if similarity_score >= 85:
                    validation_status = "excellent"
                    recommendation = "Character consistency is excellent"
                elif similarity_score >= 75:
                    validation_status = "good"
                    recommendation = "Character consistency is good"
                elif similarity_score >= 65:
                    validation_status = "acceptable"
                    recommendation = "Character consistency is acceptable but could be improved"
                elif similarity_score >= 50:
                    validation_status = "poor"
                    recommendation = "Character consistency is poor - consider reshooting"
                else:
                    validation_status = "unacceptable"
                    recommendation = "Character consistency is unacceptable - reshoot required"
                
                shot_validations.append({
                    "shot_index": i,
                    "shot_asset_id": shot_asset_id,
                    "filename": shot_asset.filename,
                    "consistent": consistent,
                    "similarity_score": similarity_score,
                    "validation_status": validation_status,
                    "recommendation": recommendation,
                    "cosine_similarity": similarity_metrics["cosine_similarity"],
                    "euclidean_distance": similarity_metrics["euclidean_distance"]
                })
                
            except Exception as e:
                shot_validations.append({
                    "shot_index": i,
                    "shot_asset_id": shot_asset_id,
                    "error": str(e),
                    "consistent": False,
                    "similarity_score": 0.0
                })
        
        # Calculate sequence statistics
        valid_shots = [s for s in shot_validations if "error" not in s]
        consistent_shots = [s for s in valid_shots if s["consistent"]]
        avg_similarity = np.mean([s["similarity_score"] for s in valid_shots]) if valid_shots else 0
        
        # Overall sequence validation
        consistency_rate = len(consistent_shots) / len(valid_shots) if valid_shots else 0
        
        if consistency_rate >= 0.9:
            sequence_status = "excellent"
            sequence_recommendation = "Sequence has excellent character consistency"
        elif consistency_rate >= 0.8:
            sequence_status = "good"
            sequence_recommendation = "Sequence has good character consistency"
        elif consistency_rate >= 0.7:
            sequence_status = "acceptable"
            sequence_recommendation = "Sequence has acceptable consistency but some shots need attention"
        else:
            sequence_status = "needs_work"
            sequence_recommendation = "Sequence needs significant work on character consistency"
        
        processing_time = time.time() - start_time
        
        return {
            "character_reference_asset_id": request.character_reference_asset_id,
            "reference_filename": reference_asset.filename,
            "total_shots": len(request.shot_asset_ids),
            "processed_shots": len(valid_shots),
            "consistent_shots": len(consistent_shots),
            "consistency_rate": consistency_rate,
            "average_similarity": float(avg_similarity),
            "sequence_status": sequence_status,
            "sequence_recommendation": sequence_recommendation,
            "shot_validations": shot_validations,
            "processing_time": processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Shot consistency validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reference-enforcement")
async def reference_enforcement(
    request: ReferenceEnforcementRequest,
    dinov3_service: DINOv3Service = Depends()
) -> Dict[str, Any]:
    """Enforce character reference consistency in generated content."""
    start_time = time.time()
    
    try:
        # Get master reference asset
        result = await db.execute(select(MediaAsset).where(MediaAsset.id == request.master_reference_asset_id))
        master_asset = result.scalar_one_or_none()
        
        if not master_asset or not master_asset.features_extracted:
            raise HTTPException(status_code=404, detail="Master reference asset not found or features not extracted")
        
        master_features = np.array(master_asset.features)
        compliance_results = []
        
        # Check compliance for each generated asset
        for generated_asset_id in request.generated_asset_ids:
            try:
                generated_asset = await MediaAsset.get(generated_asset_id)
                
                if not generated_asset or not generated_asset.features_extracted:
                    compliance_results.append({
                        "generated_asset_id": generated_asset_id,
                        "error": "Generated asset not found or features not extracted",
                        "compliant": False,
                        "compliance_score": 0.0
                    })
                    continue
                
                generated_features = np.array(generated_asset.features)
                similarity_metrics = dinov3_service.calculate_similarity(master_features, generated_features)
                
                similarity_score = similarity_metrics["similarity_percentage"]
                compliant = similarity_score >= request.compliance_threshold
                
                # Generate recommendations
                if similarity_score >= 90:
                    recommendation = "Excellent compliance - approved for use"
                    action = "approve"
                elif similarity_score >= request.compliance_threshold:
                    recommendation = "Good compliance - approved with minor notes"
                    action = "approve"
                elif similarity_score >= request.compliance_threshold - 10:
                    recommendation = "Borderline compliance - consider regeneration with adjustments"
                    action = "review"
                else:
                    recommendation = "Poor compliance - regeneration required"
                    action = "regenerate"
                
                compliance_results.append({
                    "generated_asset_id": generated_asset_id,
                    "filename": generated_asset.filename,
                    "compliant": compliant,
                    "compliance_score": similarity_score,
                    "recommendation": recommendation,
                    "action": action,
                    "cosine_similarity": similarity_metrics["cosine_similarity"],
                    "euclidean_distance": similarity_metrics["euclidean_distance"]
                })
                
            except Exception as e:
                compliance_results.append({
                    "generated_asset_id": generated_asset_id,
                    "error": str(e),
                    "compliant": False,
                    "compliance_score": 0.0
                })
        
        # Calculate enforcement statistics
        valid_results = [r for r in compliance_results if "error" not in r]
        compliant_count = sum(1 for r in valid_results if r["compliant"])
        avg_compliance = np.mean([r["compliance_score"] for r in valid_results]) if valid_results else 0
        
        # Categorize by action needed
        approve_count = sum(1 for r in valid_results if r.get("action") == "approve")
        review_count = sum(1 for r in valid_results if r.get("action") == "review")
        regenerate_count = sum(1 for r in valid_results if r.get("action") == "regenerate")
        
        processing_time = time.time() - start_time
        
        return {
            "master_reference_asset_id": request.master_reference_asset_id,
            "master_filename": master_asset.filename,
            "compliance_threshold": request.compliance_threshold,
            "total_generated": len(request.generated_asset_ids),
            "processed_successfully": len(valid_results),
            "compliant_count": compliant_count,
            "compliance_rate": compliant_count / len(valid_results) if valid_results else 0,
            "average_compliance_score": float(avg_compliance),
            "action_summary": {
                "approve": approve_count,
                "review": review_count,
                "regenerate": regenerate_count
            },
            "compliance_results": compliance_results,
            "processing_time": processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reference enforcement failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
