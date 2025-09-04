from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import time
import numpy as np
from PIL import Image
import io
import cv2
import moviepy.editor as mp
from loguru import logger

from app.core.database import MediaAsset, VideoShot
from app.core.storage import storage_service
from app.core.dinov3_service import DINOv3Service

router = APIRouter()

class VideoAnalysisRequest(BaseModel):
    video_asset_id: str
    shot_detection_threshold: float = 0.3
    extract_keyframes: bool = True

class StoreShotDataRequest(BaseModel):
    video_asset_id: str
    shots: List[Dict[str, Any]]
    scene_context: Optional[str] = None
    manual_tags: Optional[List[str]] = None

class SuggestShotsRequest(BaseModel):
    scene_description: str
    emotional_tone: Optional[str] = None
    genre_context: Optional[str] = None
    desired_tags: Optional[List[str]] = None
    limit: int = 10

class ShotLibraryRequest(BaseModel):
    movement_type: Optional[str] = None
    emotional_tone: Optional[str] = None
    genre: Optional[str] = None
    tags: Optional[List[str]] = None
    page: int = 1
    page_size: int = 20

@router.post("/analyze-video-shots")
async def analyze_video_shots(
    request: VideoAnalysisRequest,
    dinov3_service: DINOv3Service = Depends()
) -> Dict[str, Any]:
    """Analyze video for shot detection, camera movement, and cinematic patterns."""
    start_time = time.time()
    
    try:
        # Get video asset
        video_asset = await MediaAsset.get(request.video_asset_id)
        
        if not video_asset:
            raise HTTPException(status_code=404, detail="Video asset not found")
        
        # Validate that the asset is a video file
        if not video_asset.content_type or not video_asset.content_type.startswith('video/'):
            raise HTTPException(
                status_code=400, 
                detail=f"Asset is not a video file. Found content type: {video_asset.content_type}. Please upload a video file for shot analysis."
            )
        
        # Download video from storage
        await storage_service.initialize()
        video_data = await storage_service.download_file(video_asset.r2_object_key)
        
        if not video_data:
            raise HTTPException(status_code=404, detail="Video file not found in storage")
        
        # Save temporarily for processing
        temp_video_path = f"/tmp/{video_asset.id}.mp4"
        with open(temp_video_path, "wb") as f:
            f.write(video_data)
        
        # Load video with moviepy and validate it's a proper video
        try:
            video = mp.VideoFileClip(temp_video_path)
        except Exception as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid video file format. Please ensure the uploaded file is a valid video. Error: {str(e)}"
            )
        fps = video.fps
        duration = video.duration
        
        # Validate video properties
        if not fps or fps <= 0:
            raise HTTPException(status_code=400, detail="Invalid video: FPS is not valid")
        if not duration or duration <= 0:
            raise HTTPException(status_code=400, detail="Invalid video: Duration is not valid")
        
        # Detect shots using frame difference
        shots = []
        prev_frame = None
        shot_boundaries = [0]  # Start with first frame
        
        # Sample frames for shot detection
        sample_interval = max(1, int(fps / 2))  # Sample every 0.5 seconds
        
        for t in np.arange(0, duration, 1/fps * sample_interval):
            frame = video.get_frame(t)
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            
            if prev_frame is not None:
                # Calculate frame difference
                diff = cv2.absdiff(frame_gray, prev_frame)
                diff_score = np.mean(diff) / 255.0
                
                if diff_score > request.shot_detection_threshold:
                    shot_boundaries.append(t)
            
            prev_frame = frame_gray
        
        shot_boundaries.append(duration)  # End with last frame
        
        # Analyze each shot
        shot_analyses = []
        
        for i in range(len(shot_boundaries) - 1):
            start_time_shot = shot_boundaries[i]
            end_time_shot = shot_boundaries[i + 1]
            shot_duration = end_time_shot - start_time_shot
            
            # Skip very short shots
            if shot_duration < 0.5:
                continue
            
            # Extract keyframe from middle of shot
            keyframe_time = start_time_shot + shot_duration / 2
            keyframe = video.get_frame(keyframe_time)
            keyframe_image = Image.fromarray(keyframe)
            
            # Extract DINOv3 features if requested
            features = None
            if request.extract_keyframes:
                try:
                    features = await dinov3_service.extract_features(keyframe_image)
                except Exception as e:
                    logger.warning(f"Feature extraction failed for shot {i}: {e}")
            
            # Analyze camera movement (simplified)
            movement_analysis = analyze_camera_movement(video, start_time_shot, end_time_shot)
            
            # Analyze shot composition
            composition_analysis = analyze_shot_composition(keyframe_image)
            
            # Generate auto tags
            auto_tags = generate_shot_tags(movement_analysis, composition_analysis, shot_duration)
            
            shot_analysis = {
                "shot_index": i,
                "start_timestamp": start_time_shot,
                "end_timestamp": end_time_shot,
                "duration": shot_duration,
                "camera_movement": movement_analysis["movement_type"],
                "movement_intensity": movement_analysis["intensity"],
                "shot_size": composition_analysis["shot_size"],
                "shot_angle": composition_analysis["shot_angle"],
                "framing": composition_analysis["framing"],
                "features": features.tolist() if features is not None else None,
                "auto_tags": auto_tags,
                "keyframe_time": keyframe_time
            }
            
            shot_analyses.append(shot_analysis)
        
        video.close()
        
        # Clean up temp file
        import os
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
        
        processing_time = time.time() - start_time
        
        return {
            "video_asset_id": request.video_asset_id,
            "video_filename": video_asset.filename,
            "video_duration": duration,
            "fps": fps,
            "shots_detected": len(shot_analyses),
            "shot_analyses": shot_analyses,
            "processing_time": processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video shot analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/store-shot-data")
async def store_shot_data(
    request: StoreShotDataRequest
) -> Dict[str, Any]:
    """Store analyzed shot data with contextual information and tags."""
    start_time = time.time()
    
    try:
        stored_shots = []
        
        for shot_data in request.shots:
            # Combine auto tags with manual tags
            all_tags = shot_data.get("auto_tags", [])
            if request.manual_tags:
                all_tags.extend(request.manual_tags)
            
            # Create video shot record
            video_shot = VideoShot(
                video_asset_id=request.video_asset_id,
                start_timestamp=shot_data["start_timestamp"],
                end_timestamp=shot_data["end_timestamp"],
                duration=shot_data["duration"],
                camera_movement=shot_data.get("camera_movement"),
                movement_intensity=shot_data.get("movement_intensity"),
                shot_size=shot_data.get("shot_size"),
                shot_angle=shot_data.get("shot_angle"),
                framing=shot_data.get("framing"),
                features=shot_data.get("features"),
                scene_description=request.scene_context,
                tags=all_tags,
                usage_situations=generate_usage_situations(shot_data, request.scene_context)
            )

            await video_shot.insert()
            stored_shots.append({
                "shot_id": video_shot.id,
                "start_timestamp": video_shot.start_timestamp,
                "duration": video_shot.duration,
                "tags": video_shot.tags
            })
        
        
        
        processing_time = time.time() - start_time
        
        return {
            "video_asset_id": request.video_asset_id,
            "shots_stored": len(stored_shots),
            "stored_shot_ids": [s["shot_id"] for s in stored_shots],
            "scene_context": request.scene_context,
            "processing_time": processing_time
        }
        
    except Exception as e:
        logger.error(f"Shot data storage failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/suggest-shots")
async def suggest_shots(
    request: SuggestShotsRequest,
    dinov3_service: DINOv3Service = Depends()
) -> Dict[str, Any]:
    """Get cinematography recommendations based on scene requirements."""
    start_time = time.time()
    
    try:
        # Build query filters using Beanie ODM
        query_filters = {}

        # Filter by emotional tone if specified
        if request.emotional_tone:
            query_filters["emotional_tone"] = request.emotional_tone

        # Execute query with filters
        if query_filters:
            shots = await VideoShot.find(query_filters).limit(request.limit * 2).to_list()
        else:
            shots = await VideoShot.find().limit(request.limit * 2).to_list()

        # Additional filtering for tags (since Beanie doesn't support array contains in find)
        if request.desired_tags:
            filtered_shots = []
            for shot in shots:
                if shot.tags and any(tag in shot.tags for tag in request.desired_tags):
                    filtered_shots.append(shot)
            shots = filtered_shots
        
        if not shots:
            return {
                "scene_description": request.scene_description,
                "recommendations": [],
                "total_found": 0,
                "message": "No matching shots found in database"
            }
        
        # Rank shots by relevance (simplified scoring)
        shot_recommendations = []
        
        for shot in shots:
            relevance_score = calculate_shot_relevance(
                shot, request.scene_description, request.emotional_tone, request.desired_tags
            )
            
            shot_recommendations.append({
                "shot_id": shot.id,
                "video_asset_id": shot.video_asset_id,
                "start_timestamp": shot.start_timestamp,
                "duration": shot.duration,
                "camera_movement": shot.camera_movement,
                "shot_size": shot.shot_size,
                "shot_angle": shot.shot_angle,
                "emotional_tone": shot.emotional_tone,
                "tags": shot.tags,
                "usage_situations": shot.usage_situations,
                "scene_description": shot.scene_description,
                "relevance_score": relevance_score
            })
        
        # Sort by relevance and limit
        shot_recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)
        shot_recommendations = shot_recommendations[:request.limit]
        
        processing_time = time.time() - start_time
        
        return {
            "scene_description": request.scene_description,
            "emotional_tone": request.emotional_tone,
            "desired_tags": request.desired_tags,
            "recommendations": shot_recommendations,
            "total_found": len(shots),
            "processing_time": processing_time
        }
        
    except Exception as e:
        logger.error(f"Shot suggestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/shot-library")
async def get_shot_library(
    movement_type: Optional[str] = None,
    emotional_tone: Optional[str] = None,
    genre: Optional[str] = None,
    tags: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
) -> Dict[str, Any]:
    """Browse and search the shot database with filters."""
    start_time = time.time()
    
    try:
        # Build query filters using Beanie ODM
        query_filters = {}

        if movement_type:
            query_filters["camera_movement"] = movement_type

        if emotional_tone:
            query_filters["emotional_tone"] = emotional_tone

        # Get all matching shots first for count and tag filtering
        if query_filters:
            all_shots = await VideoShot.find(query_filters).to_list()
        else:
            all_shots = await VideoShot.find().to_list()

        # Filter by tags if specified
        if tags:
            tag_list = [t.strip() for t in tags.split(",")]
            filtered_shots = []
            for shot in all_shots:
                if shot.tags and any(tag in shot.tags for tag in tag_list):
                    filtered_shots.append(shot)
            all_shots = filtered_shots

        total_shots = len(all_shots)

        # Apply pagination
        offset = (page - 1) * page_size
        shots = all_shots[offset:offset + page_size]
        
        # Format results
        shot_library = []
        for shot in shots:
            shot_library.append({
                "shot_id": shot.id,
                "video_asset_id": shot.video_asset_id,
                "start_timestamp": shot.start_timestamp,
                "duration": shot.duration,
                "camera_movement": shot.camera_movement,
                "movement_intensity": shot.movement_intensity,
                "shot_size": shot.shot_size,
                "shot_angle": shot.shot_angle,
                "framing": shot.framing,
                "emotional_tone": shot.emotional_tone,
                "tags": shot.tags,
                "usage_situations": shot.usage_situations,
                "scene_description": shot.scene_description,
                "analysis_timestamp": shot.analysis_timestamp.isoformat()
            })
        
        processing_time = time.time() - start_time
        
        return {
            "shots": shot_library,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_shots": total_shots,
                "total_pages": (total_shots + page_size - 1) // page_size
            },
            "filters_applied": {
                "movement_type": movement_type,
                "emotional_tone": emotional_tone,
                "genre": genre,
                "tags": tags.split(",") if tags else None
            },
            "processing_time": processing_time
        }
        
    except Exception as e:
        logger.error(f"Shot library query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
def analyze_camera_movement(video, start_time, end_time):
    """Analyze camera movement in video segment."""
    # Simplified camera movement detection
    sample_times = np.linspace(start_time, end_time, 5)
    movements = []
    
    prev_frame = None
    for t in sample_times:
        frame = video.get_frame(t)
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        
        if prev_frame is not None:
            # Calculate optical flow (simplified)
            diff = cv2.absdiff(frame_gray, prev_frame)
            movement_score = np.mean(diff) / 255.0
            movements.append(movement_score)
        
        prev_frame = frame_gray
    
    avg_movement = np.mean(movements) if movements else 0
    
    # Classify movement type
    if avg_movement < 0.05:
        movement_type = "static"
    elif avg_movement < 0.15:
        movement_type = "slow_pan"
    elif avg_movement < 0.3:
        movement_type = "pan"
    else:
        movement_type = "fast_movement"
    
    return {
        "movement_type": movement_type,
        "intensity": avg_movement
    }

def analyze_shot_composition(image):
    """Analyze shot composition from keyframe."""
    width, height = image.size
    
    # Simplified composition analysis
    aspect_ratio = width / height
    
    # Determine shot size based on aspect ratio and image characteristics
    if aspect_ratio > 2.0:
        shot_size = "wide"
    elif aspect_ratio > 1.5:
        shot_size = "medium"
    else:
        shot_size = "close_up"
    
    return {
        "shot_size": shot_size,
        "shot_angle": "eye_level",  # Simplified
        "framing": "standard",
        "aspect_ratio": aspect_ratio
    }

def generate_shot_tags(movement_analysis, composition_analysis, duration):
    """Generate automatic tags for shot."""
    tags = []
    
    # Movement tags
    tags.append(movement_analysis["movement_type"])
    
    # Composition tags
    tags.append(composition_analysis["shot_size"])
    
    # Duration tags
    if duration < 2:
        tags.append("quick_cut")
    elif duration < 5:
        tags.append("short_shot")
    elif duration < 10:
        tags.append("medium_shot")
    else:
        tags.append("long_shot")
    
    return tags

def generate_usage_situations(shot_data, scene_context):
    """Generate usage situations for shot."""
    situations = []
    
    movement = shot_data.get("camera_movement", "")
    shot_size = shot_data.get("shot_size", "")
    
    # Generate based on movement and composition
    if movement == "static" and shot_size == "close_up":
        situations.extend(["dialogue", "emotional_moment", "character_focus"])
    elif movement == "pan" and shot_size == "wide":
        situations.extend(["establishing_shot", "location_reveal", "transition"])
    elif movement == "fast_movement":
        situations.extend(["action_sequence", "chase", "dynamic_moment"])
    
    if scene_context:
        if "dialogue" in scene_context.lower():
            situations.append("conversation")
        if "action" in scene_context.lower():
            situations.append("action_scene")
    
    return list(set(situations))  # Remove duplicates

def calculate_shot_relevance(shot, scene_description, emotional_tone, desired_tags):
    """Calculate relevance score for shot recommendation."""
    score = 0.0
    
    # Tag matching
    if desired_tags and shot.tags:
        matching_tags = set(desired_tags) & set(shot.tags)
        score += len(matching_tags) * 10
    
    # Emotional tone matching
    if emotional_tone and shot.emotional_tone == emotional_tone:
        score += 20
    
    # Scene description matching (simplified)
    if scene_description and shot.scene_description:
        common_words = set(scene_description.lower().split()) & set(shot.scene_description.lower().split())
        score += len(common_words) * 5
    
    return score
