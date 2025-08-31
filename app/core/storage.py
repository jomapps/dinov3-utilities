import boto3
from botocore.exceptions import ClientError
import aiofiles
from typing import Optional, Dict, Any, BinaryIO
import uuid
from pathlib import Path
import mimetypes
from loguru import logger
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.core.config import settings

class StorageService:
    """Cloudflare R2 storage service for media assets."""
    
    def __init__(self):
        self.s3_client = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    async def initialize(self):
        """Initialize Cloudflare R2 client."""
        try:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=settings.CLOUDFLARE_R2_ENDPOINT,
                aws_access_key_id=settings.CLOUDFLARE_R2_ACCESS_KEY_ID,
                aws_secret_access_key=settings.CLOUDFLARE_R2_SECRET_ACCESS_KEY,
                region_name='auto'
            )
            
            # Test connection
            await self._run_sync(self.s3_client.head_bucket, Bucket=settings.CLOUDFLARE_R2_BUCKET_NAME)
            logger.info(f"Storage service connected to R2 bucket: {settings.CLOUDFLARE_R2_BUCKET_NAME}")
            
        except Exception as e:
            logger.error(f"R2 storage service initialization failed: {e}")
            raise
    
    async def _run_sync(self, func, *args, **kwargs):
        """Run synchronous function in thread pool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, func, *args, **kwargs)
    
    async def upload_file(self, file_data: bytes, filename: str, content_type: str) -> Dict[str, Any]:
        """Upload file to S3/R2 storage."""
        try:
            # Generate unique object key
            file_extension = Path(filename).suffix
            object_key = f"{uuid.uuid4()}{file_extension}"
            
            # Upload to S3/R2
            await self._run_sync(
                self.s3_client.put_object,
                Bucket=settings.S3_BUCKET_NAME,
                Key=object_key,
                Body=file_data,
                ContentType=content_type,
                Metadata={
                    'original_filename': filename,
                    'upload_source': 'dinov3-utilities'
                }
            )
            
            # Generate public URL
            public_url = f"{settings.S3_ENDPOINT_URL}/{settings.S3_BUCKET_NAME}/{object_key}"
            
            return {
                "object_key": object_key,
                "public_url": public_url,
                "filename": filename,
                "content_type": content_type,
                "file_size": len(file_data)
            }
            
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            raise
    
    async def download_file(self, object_key: str) -> bytes:
        """Download file from S3/R2 storage."""
        try:
            response = await self._run_sync(
                self.s3_client.get_object,
                Bucket=settings.S3_BUCKET_NAME,
                Key=object_key
            )
            return response['Body'].read()
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise FileNotFoundError(f"Object not found: {object_key}")
            raise
        except Exception as e:
            logger.error(f"File download failed: {e}")
            raise
    
    async def delete_file(self, object_key: str) -> bool:
        """Delete file from S3/R2 storage."""
        try:
            await self._run_sync(
                self.s3_client.delete_object,
                Bucket=settings.S3_BUCKET_NAME,
                Key=object_key
            )
            return True
            
        except Exception as e:
            logger.error(f"File deletion failed: {e}")
            return False
    
    async def get_file_info(self, object_key: str) -> Dict[str, Any]:
        """Get file metadata from S3/R2 storage."""
        try:
            response = await self._run_sync(
                self.s3_client.head_object,
                Bucket=settings.S3_BUCKET_NAME,
                Key=object_key
            )
            
            return {
                "object_key": object_key,
                "content_type": response.get('ContentType'),
                "file_size": response.get('ContentLength'),
                "last_modified": response.get('LastModified'),
                "metadata": response.get('Metadata', {})
            }
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise FileNotFoundError(f"Object not found: {object_key}")
            raise
        except Exception as e:
            logger.error(f"Get file info failed: {e}")
            raise
    
    async def generate_presigned_url(self, object_key: str, expiration: int = 3600) -> str:
        """Generate presigned URL for temporary access."""
        try:
            url = await self._run_sync(
                self.s3_client.generate_presigned_url,
                'get_object',
                Params={'Bucket': settings.S3_BUCKET_NAME, 'Key': object_key},
                ExpiresIn=expiration
            )
            return url
            
        except Exception as e:
            logger.error(f"Presigned URL generation failed: {e}")
            raise
    
    def cleanup(self):
        """Cleanup resources."""
        if self.executor:
            self.executor.shutdown(wait=True)

# Global storage service instance
storage_service = StorageService()
