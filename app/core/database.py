from motor.motor_asyncio import AsyncIOMotorClient
from beanie import Document, init_beanie
from pydantic import Field
from datetime import datetime
from typing import List, Optional, AsyncGenerator
import uuid

from app.core.config import settings

# MongoDB client
client: Optional[AsyncIOMotorClient] = None

async def init_database():
    """Initialize MongoDB connection and Beanie ODM."""
    global client
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = client.get_default_database()
    
    # Initialize Beanie with document models
    await init_beanie(
        database=database,
        document_models=[
            MediaAsset,
            QualityAnalysis,
            SimilarityResult,
            VideoShot,
            CharacterConsistency
        ]
    )

async def close_database():
    """Close MongoDB connection."""
    if client:
        client.close()

class MediaAsset(Document):
    """Media asset model for R2-based asset management."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    filename: str
    content_type: str
    file_size: int
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)
    r2_object_key: str
    public_url: str
    
    # DINOv3 features (384-dimensional)
    features: Optional[List[float]] = None
    features_extracted: bool = False
    features_timestamp: Optional[datetime] = None
    
    # Processing status
    processing_status: str = "uploaded"  # uploaded, processing, completed, error
    error_message: Optional[str] = None
    
    # Metadata
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None
    
    class Settings:
        name = "media_assets"
    
class QualityAnalysis(Document):
    """Quality analysis results for media assets."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    asset_id: str = Field(index=True)
    
    # Quality metrics
    quality_score: float
    diversity_score: float
    sharpness_score: Optional[float] = None
    lighting_quality: Optional[float] = None
    composition_score: Optional[float] = None
    
    # Feature statistics
    feature_mean: float
    feature_std: float
    feature_max: float
    feature_min: float
    
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_time: float
    
    class Settings:
        name = "quality_analyses"

class SimilarityResult(Document):
    """Similarity calculation results between assets."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    asset_id_1: str = Field(index=True)
    asset_id_2: str = Field(index=True)
    
    similarity_score: float
    cosine_similarity: float
    euclidean_distance: float
    
    calculation_timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_time: float
    
    class Settings:
        name = "similarity_results"

class VideoShot(Document):
    """Video shot analysis and cinematic intelligence."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    video_asset_id: str = Field(index=True)
    
    # Temporal data
    start_timestamp: float
    end_timestamp: float
    duration: float
    
    # Camera movement analysis
    camera_movement: Optional[str] = None  # dolly, pan, tilt, static, etc.
    movement_intensity: Optional[float] = None
    
    # Shot composition
    shot_size: Optional[str] = None  # close-up, medium, wide, etc.
    shot_angle: Optional[str] = None  # high, low, eye-level, etc.
    framing: Optional[str] = None
    
    # DINOv3 embeddings for the shot
    features: Optional[List[float]] = None
    
    # Context and tags
    scene_description: Optional[str] = None
    emotional_tone: Optional[str] = None
    narrative_function: Optional[str] = None
    tags: Optional[List[str]] = None
    
    # Usage situations
    usage_situations: Optional[List[str]] = None
    
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "video_shots"

class CharacterConsistency(Document):
    """Character consistency analysis results."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    reference_asset_id: str = Field(index=True)
    test_asset_id: str = Field(index=True)
    
    same_character: bool
    confidence_score: float
    similarity_score: float
    explanation: Optional[str] = None
    
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_time: float
    
    class Settings:
        name = "character_consistency"

# Database dependency (no longer needed with Beanie)
# MongoDB connection is handled globally through Beanie
