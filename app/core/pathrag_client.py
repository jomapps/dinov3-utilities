import httpx
from typing import Dict, Any, List, Optional
from loguru import logger

from app.core.config import settings

class PathRAGClient:
    """Client for PathRAG API integration (ArangoDB access)."""
    
    def __init__(self):
        self.base_url = settings.PATHRAG_API_URL
        self.enabled = settings.PATHRAG_ENABLE
        
    async def health_check(self) -> Dict[str, Any]:
        """Check PathRAG service health."""
        if not self.enabled:
            return {"status": "disabled", "message": "PathRAG integration disabled"}
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
                return response.json()
        except Exception as e:
            logger.error(f"PathRAG health check failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def insert_documents(self, documents: List[str]) -> Dict[str, Any]:
        """Insert documents into PathRAG knowledge base."""
        if not self.enabled:
            return {"message": "PathRAG disabled", "document_count": 0}
            
        try:
            payload = {"documents": documents}
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/insert",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                return response.json()
        except Exception as e:
            logger.error(f"PathRAG document insertion failed: {e}")
            raise
    
    async def query_knowledge(self, query: str, **params) -> Dict[str, Any]:
        """Query PathRAG knowledge base."""
        if not self.enabled:
            return {"result": "PathRAG integration disabled", "query": query}
            
        try:
            # Set default parameters from config
            query_params = {
                "mode": "hybrid",
                "top_k": settings.PATHRAG_DEFAULT_TOP_K,
                "max_token_for_text_unit": settings.PATHRAG_MAX_TOKEN_FOR_TEXT_UNIT,
                "max_token_for_global_context": settings.PATHRAG_MAX_TOKEN_FOR_GLOBAL_CONTEXT,
                "max_token_for_local_context": settings.PATHRAG_MAX_TOKEN_FOR_LOCAL_CONTEXT,
                **params
            }
            
            payload = {
                "query": query,
                "params": query_params
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/query",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                return response.json()
        except Exception as e:
            logger.error(f"PathRAG query failed: {e}")
            raise
    
    async def insert_custom_kg(self, custom_kg: Dict[str, Any]) -> Dict[str, Any]:
        """Insert custom knowledge graph data."""
        if not self.enabled:
            return {"message": "PathRAG disabled"}
            
        try:
            payload = {"custom_kg": custom_kg}
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/insert_custom_kg",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                return response.json()
        except Exception as e:
            logger.error(f"PathRAG custom KG insertion failed: {e}")
            raise
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get PathRAG system statistics."""
        if not self.enabled:
            return {"message": "PathRAG disabled"}
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/stats")
                return response.json()
        except Exception as e:
            logger.error(f"PathRAG stats retrieval failed: {e}")
            raise

# Global PathRAG client instance
pathrag_client = PathRAGClient()
