from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from typing import List, Optional, Dict, Any
import asyncio
from loguru import logger

from app.core.config import settings
from app.core.database import engine, Base
from app.core.dinov3_service import DINOv3Service
from app.routers import (
    media_management,
    feature_extraction,
    similarity,
    quality_analysis,
    batch_processing,
    character_analysis,
    production_services,
    video_analysis,
    utilities,
    analytics,
    configuration
)

# Global DINOv3 service instance
dinov3_service: Optional[DINOv3Service] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown tasks."""
    global dinov3_service
    
    logger.info("Starting DINOv3 Utilities Service...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize DINOv3 service
    dinov3_service = DINOv3Service()
    await dinov3_service.initialize()
    
    logger.info("DINOv3 service initialized successfully")
    
    yield
    
    # Cleanup
    if dinov3_service:
        await dinov3_service.cleanup()
    logger.info("DINOv3 Utilities Service shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="DINOv3 Utilities Service",
    description="Comprehensive DINOv3-based image analysis and processing service",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DINOv3 service
async def get_dinov3_service() -> DINOv3Service:
    if dinov3_service is None:
        raise HTTPException(status_code=503, detail="DINOv3 service not initialized")
    return dinov3_service

# Include all routers
app.include_router(
    media_management.router,
    prefix="/api/v1",
    tags=["Media Management"],
    dependencies=[Depends(get_dinov3_service)]
)

app.include_router(
    feature_extraction.router,
    prefix="/api/v1",
    tags=["Feature Extraction"],
    dependencies=[Depends(get_dinov3_service)]
)

app.include_router(
    similarity.router,
    prefix="/api/v1",
    tags=["Similarity & Matching"],
    dependencies=[Depends(get_dinov3_service)]
)

app.include_router(
    quality_analysis.router,
    prefix="/api/v1",
    tags=["Quality Analysis"],
    dependencies=[Depends(get_dinov3_service)]
)

app.include_router(
    batch_processing.router,
    prefix="/api/v1",
    tags=["Batch Processing"],
    dependencies=[Depends(get_dinov3_service)]
)

app.include_router(
    character_analysis.router,
    prefix="/api/v1",
    tags=["Character Analysis"],
    dependencies=[Depends(get_dinov3_service)]
)

app.include_router(
    production_services.router,
    prefix="/api/v1",
    tags=["Production Services"],
    dependencies=[Depends(get_dinov3_service)]
)

app.include_router(
    video_analysis.router,
    prefix="/api/v1",
    tags=["Video Analysis"],
    dependencies=[Depends(get_dinov3_service)]
)

app.include_router(
    utilities.router,
    prefix="/api/v1",
    tags=["Utilities"],
    dependencies=[Depends(get_dinov3_service)]
)

app.include_router(
    analytics.router,
    prefix="/api/v1",
    tags=["Advanced Analytics"],
    dependencies=[Depends(get_dinov3_service)]
)

app.include_router(
    configuration.router,
    prefix="/api/v1",
    tags=["Configuration"],
    dependencies=[Depends(get_dinov3_service)]
)

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "DINOv3 Utilities",
        "version": "1.0.0",
        "status": "running",
        "endpoints": "/docs",
        "health": "/api/v1/health"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for better error responses."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        workers=settings.API_WORKERS
    )
