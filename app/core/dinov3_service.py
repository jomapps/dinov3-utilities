import torch
import torch.nn.functional as F
from transformers import AutoImageProcessor, AutoModel
from huggingface_hub import login
from PIL import Image
import numpy as np
from typing import List, Optional, Tuple, Dict, Any
import asyncio
import redis.asyncio as redis
from loguru import logger
import time
import io
import cv2
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import os

from app.core.config import settings

class DINOv3Service:
    """Core DINOv3 service for feature extraction and analysis."""
    
    def __init__(self):
        self.model = None
        self.processor = None
        self.device = None
        self.redis = None
        self.feature_cache = {}
        
    async def initialize(self):
        """Initialize DINOv3 model and supporting services."""
        logger.info("Initializing DINOv3 service...")
        
        # Authenticate with Hugging Face if token is available
        hf_token = os.getenv("HF_TOKEN")
        if hf_token:
            try:
                login(token=hf_token)
                logger.info("Successfully authenticated with Hugging Face")
            except Exception as e:
                logger.warning(f"Failed to authenticate with Hugging Face: {e}")
        else:
            logger.warning("No HF_TOKEN found in environment variables")
        
        # Set device
        if settings.DINOV3_DEVICE == "cuda" and torch.cuda.is_available():
            self.device = torch.device("cuda")
            logger.info(f"Using GPU: {torch.cuda.get_device_name()}")
            logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        else:
            self.device = torch.device("cpu")
            logger.info("Using CPU")
        
        # Load DINOv3 model
        model_name = settings.DINOV3_MODEL_NAME
        logger.info(f"Loading model: {model_name}")
        
        try:
            self.processor = AutoImageProcessor.from_pretrained(
                model_name,
                token=hf_token if hf_token else None,
                trust_remote_code=True
            )
            self.model = AutoModel.from_pretrained(
                model_name,
                token=hf_token if hf_token else None,
                trust_remote_code=True
            )
            self.model.to(self.device)
            self.model.eval()
            logger.info("DINOv3 model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load DINOv3 model: {e}")
            raise
        
        # Initialize Redis for caching
        try:
            self.redis = redis.from_url(settings.REDIS_URL)
            await self.redis.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self.redis = None
        
        logger.info("DINOv3 service initialization complete")
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.redis:
            await self.redis.close()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    def preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """Preprocess image for DINOv3."""
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Process with DINOv3 processor
        inputs = self.processor(images=image, return_tensors="pt")
        return inputs.pixel_values.to(self.device)
    
    async def extract_features(self, image: Image.Image) -> np.ndarray:
        """Extract DINOv3 features from image."""
        start_time = time.time()
        
        try:
            # Preprocess image
            pixel_values = self.preprocess_image(image)
            
            # Extract features
            with torch.no_grad():
                outputs = self.model(pixel_values)
                # Use CLS token features (384-dimensional for ViT-B/16)
                features = outputs.last_hidden_state[:, 0, :].cpu().numpy()
            
            processing_time = time.time() - start_time
            logger.debug(f"Feature extraction completed in {processing_time:.3f}s")
            
            return features.flatten()
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            raise
    
    async def extract_features_batch(self, images: List[Image.Image]) -> List[np.ndarray]:
        """Extract features from multiple images in batch."""
        if len(images) > settings.DINOV3_BATCH_SIZE:
            # Process in chunks
            results = []
            for i in range(0, len(images), settings.DINOV3_BATCH_SIZE):
                batch = images[i:i + settings.DINOV3_BATCH_SIZE]
                batch_results = await self._process_batch(batch)
                results.extend(batch_results)
            return results
        else:
            return await self._process_batch(images)
    
    async def _process_batch(self, images: List[Image.Image]) -> List[np.ndarray]:
        """Process a batch of images."""
        start_time = time.time()
        
        try:
            # Preprocess all images
            pixel_values_list = [self.preprocess_image(img) for img in images]
            pixel_values = torch.cat(pixel_values_list, dim=0)
            
            # Extract features
            with torch.no_grad():
                outputs = self.model(pixel_values)
                features = outputs.last_hidden_state[:, 0, :].cpu().numpy()
            
            processing_time = time.time() - start_time
            logger.debug(f"Batch feature extraction ({len(images)} images) completed in {processing_time:.3f}s")
            
            return [feat for feat in features]
            
        except Exception as e:
            logger.error(f"Batch feature extraction failed: {e}")
            raise
    
    def calculate_similarity(self, features1: np.ndarray, features2: np.ndarray) -> Dict[str, float]:
        """Calculate similarity between two feature vectors."""
        # Reshape for sklearn
        feat1 = features1.reshape(1, -1)
        feat2 = features2.reshape(1, -1)
        
        # Cosine similarity
        cos_sim = cosine_similarity(feat1, feat2)[0][0]
        
        # Euclidean distance
        euclidean_dist = np.linalg.norm(features1 - features2)
        
        # Convert cosine similarity to percentage
        similarity_percentage = (cos_sim + 1) * 50  # Convert from [-1,1] to [0,100]
        
        return {
            "similarity_percentage": float(similarity_percentage),
            "cosine_similarity": float(cos_sim),
            "euclidean_distance": float(euclidean_dist)
        }
    
    def calculate_similarity_matrix(self, features_list: List[np.ndarray]) -> np.ndarray:
        """Calculate similarity matrix for multiple feature vectors."""
        features_array = np.array(features_list)
        similarity_matrix = cosine_similarity(features_array)
        
        # Convert to percentage
        similarity_matrix = (similarity_matrix + 1) * 50
        
        return similarity_matrix
    
    def analyze_quality(self, features: np.ndarray) -> Dict[str, float]:
        """Analyze image quality based on DINOv3 features."""
        # Feature statistics
        feature_mean = float(np.mean(features))
        feature_std = float(np.std(features))
        feature_max = float(np.max(features))
        feature_min = float(np.min(features))
        
        # Quality score based on feature diversity and magnitude
        diversity_score = feature_std / (abs(feature_mean) + 1e-8)
        magnitude_score = np.linalg.norm(features) / len(features)
        
        # Combined quality score
        quality_score = (diversity_score * 0.6 + magnitude_score * 0.4)
        quality_score = min(max(quality_score, 0.0), 1.0)  # Clamp to [0,1]
        
        return {
            "quality_score": quality_score,
            "diversity_score": diversity_score,
            "feature_mean": feature_mean,
            "feature_std": feature_std,
            "feature_max": feature_max,
            "feature_min": feature_min
        }
    
    def analyze_image_metrics(self, image: Image.Image) -> Dict[str, float]:
        """Analyze technical image metrics."""
        # Convert to OpenCV format
        img_array = np.array(image)
        if len(img_array.shape) == 3:
            img_gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            img_gray = img_array
        
        # Sharpness (Laplacian variance)
        laplacian = cv2.Laplacian(img_gray, cv2.CV_64F)
        sharpness = float(laplacian.var())
        
        # Lighting quality (histogram analysis)
        hist = cv2.calcHist([img_gray], [0], None, [256], [0, 256])
        hist_norm = hist / hist.sum()
        
        # Avoid extreme dark/bright regions
        dark_pixels = hist_norm[:50].sum()
        bright_pixels = hist_norm[200:].sum()
        lighting_quality = 1.0 - (dark_pixels + bright_pixels)
        
        # Composition score (rule of thirds approximation)
        h, w = img_gray.shape
        third_h, third_w = h // 3, w // 3
        
        # Check interest points near rule of thirds intersections
        corners = [
            img_gray[third_h:2*third_h, third_w:2*third_w],
        ]
        composition_score = float(np.std(corners[0]) / 255.0)
        
        # Overall quality rating
        overall_quality = (sharpness/10000 * 0.4 + lighting_quality * 0.4 + composition_score * 0.2)
        overall_quality = min(max(overall_quality, 0.0), 1.0)
        
        return {
            "sharpness_score": min(sharpness / 1000, 1.0),  # Normalize
            "lighting_quality": lighting_quality,
            "composition_score": composition_score,
            "overall_quality": overall_quality
        }
    
    def detect_anomalies(self, reference_features: List[np.ndarray], test_features: List[np.ndarray]) -> List[Dict[str, Any]]:
        """Detect anomalous features compared to reference set."""
        # Calculate mean and std of reference features
        ref_array = np.array(reference_features)
        ref_mean = np.mean(ref_array, axis=0)
        ref_std = np.std(ref_array, axis=0)
        
        anomaly_results = []
        
        for i, test_feat in enumerate(test_features):
            # Calculate z-score
            z_scores = np.abs((test_feat - ref_mean) / (ref_std + 1e-8))
            anomaly_score = float(np.mean(z_scores))
            
            # Similarity to reference centroid
            centroid_similarity = cosine_similarity([test_feat], [ref_mean])[0][0]
            
            is_anomaly = anomaly_score > 2.0 or centroid_similarity < 0.5
            
            anomaly_results.append({
                "index": i,
                "anomaly_score": anomaly_score,
                "centroid_similarity": float(centroid_similarity),
                "is_anomaly": is_anomaly,
                "confidence": min(anomaly_score / 3.0, 1.0)
            })
        
        return anomaly_results
    
    def cluster_features(self, features_list: List[np.ndarray], n_clusters: int = None) -> Dict[str, Any]:
        """Cluster features using K-means."""
        features_array = np.array(features_list)
        
        if n_clusters is None:
            # Estimate optimal clusters using elbow method (simplified)
            n_clusters = min(max(len(features_list) // 10, 2), 10)
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(features_array)
        
        # Calculate cluster statistics
        cluster_stats = []
        for i in range(n_clusters):
            cluster_mask = cluster_labels == i
            cluster_features = features_array[cluster_mask]
            
            if len(cluster_features) > 0:
                centroid = np.mean(cluster_features, axis=0)
                inertia = np.mean([np.linalg.norm(feat - centroid) for feat in cluster_features])
                
                cluster_stats.append({
                    "cluster_id": i,
                    "size": int(np.sum(cluster_mask)),
                    "centroid": centroid.tolist(),
                    "inertia": float(inertia)
                })
        
        return {
            "cluster_labels": cluster_labels.tolist(),
            "n_clusters": n_clusters,
            "cluster_stats": cluster_stats,
            "total_inertia": float(kmeans.inertia_)
        }
    
    async def cache_features(self, asset_id: str, features: np.ndarray):
        """Cache features in Redis if available."""
        if self.redis:
            try:
                features_bytes = features.tobytes()
                await self.redis.setex(f"features:{asset_id}", 3600, features_bytes)  # 1 hour TTL
            except Exception as e:
                logger.warning(f"Failed to cache features: {e}")
    
    async def get_cached_features(self, asset_id: str) -> Optional[np.ndarray]:
        """Get cached features from Redis."""
        if self.redis:
            try:
                features_bytes = await self.redis.get(f"features:{asset_id}")
                if features_bytes:
                    return np.frombuffer(features_bytes, dtype=np.float32)
            except Exception as e:
                logger.warning(f"Failed to get cached features: {e}")
        return None
