from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import time
import numpy as np
from loguru import logger

from app.core.database import MediaAsset
from app.core.dinov3_service import DINOv3Service

router = APIRouter()

class SemanticSearchRequest(BaseModel):
    query_asset_id: str
    dataset_asset_ids: List[str]
    top_k: int = 10

class AnomalyDetectionRequest(BaseModel):
    reference_asset_ids: List[str]
    test_asset_ids: List[str]
    anomaly_threshold: float = 2.0

class FeatureClusteringRequest(BaseModel):
    asset_ids: List[str]
    n_clusters: Optional[int] = None
    cluster_method: str = "kmeans"

@router.post("/semantic-search")
async def semantic_search(
    request: SemanticSearchRequest,
    dinov3_service: DINOv3Service = Depends()
) -> Dict[str, Any]:
    """Search for semantically similar assets in a dataset."""
    start_time = time.time()
    
    try:
        # Get query asset
        result = await db.execute(select(MediaAsset).where(MediaAsset.id == request.query_asset_id))
        query_asset = result.scalar_one_or_none()
        
        if not query_asset or not query_asset.features_extracted:
            raise HTTPException(status_code=404, detail="Query asset not found or features not extracted")
        
        query_features = np.array(query_asset.features)
        
        # Get dataset assets and calculate similarities
        search_results = []
        
        for asset_id in request.dataset_asset_ids:
            asset = await MediaAsset.get(asset_id)
            
            if asset and asset.features_extracted:
                asset_features = np.array(asset.features)
                similarity_metrics = dinov3_service.calculate_similarity(query_features, asset_features)
                
                search_results.append({
                    "asset_id": asset_id,
                    "filename": asset.filename,
                    "similarity_score": similarity_metrics["similarity_percentage"],
                    "cosine_similarity": similarity_metrics["cosine_similarity"],
                    "euclidean_distance": similarity_metrics["euclidean_distance"]
                })
        
        # Sort by similarity score and limit
        search_results.sort(key=lambda x: x["similarity_score"], reverse=True)
        top_results = search_results[:request.top_k]
        
        processing_time = time.time() - start_time
        
        return {
            "query_asset_id": request.query_asset_id,
            "query_filename": query_asset.filename,
            "dataset_size": len(request.dataset_asset_ids),
            "results_found": len(search_results),
            "top_k": request.top_k,
            "search_results": top_results,
            "processing_time": processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/anomaly-detection")
async def anomaly_detection(
    request: AnomalyDetectionRequest,
    dinov3_service: DINOv3Service = Depends()
) -> Dict[str, Any]:
    """Detect anomalous assets that don't fit expected patterns."""
    start_time = time.time()
    
    try:
        # Get reference features
        reference_features = []
        reference_info = {}
        
        for asset_id in request.reference_asset_ids:
            asset = await MediaAsset.get(asset_id)
            
            if asset and asset.features_extracted:
                features = np.array(asset.features)
                reference_features.append(features)
                reference_info[asset_id] = asset.filename
        
        if len(reference_features) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 reference assets with features required"
            )
        
        # Get test features
        test_features = []
        test_info = {}
        
        for asset_id in request.test_asset_ids:
            asset = await MediaAsset.get(asset_id)
            
            if asset and asset.features_extracted:
                features = np.array(asset.features)
                test_features.append(features)
                test_info[len(test_features) - 1] = {
                    "asset_id": asset_id,
                    "filename": asset.filename
                }
        
        if not test_features:
            raise HTTPException(
                status_code=400,
                detail="No test assets with features found"
            )
        
        # Detect anomalies
        anomaly_results = dinov3_service.detect_anomalies(reference_features, test_features)
        
        # Format results with asset information
        formatted_results = []
        for result in anomaly_results:
            asset_info = test_info[result["index"]]
            formatted_results.append({
                "asset_id": asset_info["asset_id"],
                "filename": asset_info["filename"],
                "anomaly_score": result["anomaly_score"],
                "centroid_similarity": result["centroid_similarity"],
                "is_anomaly": result["is_anomaly"],
                "confidence": result["confidence"]
            })
        
        # Calculate summary statistics
        anomaly_count = sum(1 for r in formatted_results if r["is_anomaly"])
        avg_anomaly_score = np.mean([r["anomaly_score"] for r in formatted_results])
        
        processing_time = time.time() - start_time
        
        return {
            "reference_assets": len(reference_features),
            "test_assets": len(test_features),
            "anomaly_threshold": request.anomaly_threshold,
            "anomalies_detected": anomaly_count,
            "anomaly_rate": anomaly_count / len(test_features),
            "average_anomaly_score": float(avg_anomaly_score),
            "anomaly_results": formatted_results,
            "processing_time": processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Anomaly detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feature-clustering")
async def feature_clustering(
    request: FeatureClusteringRequest,
    dinov3_service: DINOv3Service = Depends()
) -> Dict[str, Any]:
    """Cluster assets based on DINOv3 features."""
    start_time = time.time()
    
    try:
        # Get assets with features
        features_list = []
        asset_mapping = {}
        
        for asset_id in request.asset_ids:
            asset = await MediaAsset.get(asset_id)
            
            if asset and asset.features_extracted:
                features = np.array(asset.features)
                features_list.append(features)
                asset_mapping[len(features_list) - 1] = {
                    "asset_id": asset_id,
                    "filename": asset.filename
                }
        
        if len(features_list) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 assets with features required for clustering"
            )
        
        # Perform clustering
        clustering_result = dinov3_service.cluster_features(
            features_list, 
            n_clusters=request.n_clusters
        )
        
        # Format results with asset information
        clustered_assets = {}
        for i, cluster_label in enumerate(clustering_result["cluster_labels"]):
            if cluster_label not in clustered_assets:
                clustered_assets[cluster_label] = []
            
            asset_info = asset_mapping[i]
            clustered_assets[cluster_label].append({
                "asset_id": asset_info["asset_id"],
                "filename": asset_info["filename"]
            })
        
        # Format cluster statistics
        cluster_info = []
        for cluster_stat in clustering_result["cluster_stats"]:
            cluster_id = cluster_stat["cluster_id"]
            cluster_info.append({
                "cluster_id": cluster_id,
                "size": cluster_stat["size"],
                "inertia": cluster_stat["inertia"],
                "assets": clustered_assets.get(cluster_id, [])
            })
        
        processing_time = time.time() - start_time
        
        return {
            "total_assets": len(request.asset_ids),
            "assets_clustered": len(features_list),
            "n_clusters": clustering_result["n_clusters"],
            "total_inertia": clustering_result["total_inertia"],
            "cluster_method": request.cluster_method,
            "clusters": cluster_info,
            "processing_time": processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Feature clustering failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
