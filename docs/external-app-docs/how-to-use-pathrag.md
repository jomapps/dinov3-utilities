# How to Use PathRAG API

This document provides comprehensive instructions on how to use the PathRAG API from external applications. PathRAG is a graph-based retrieval augmented generation system that provides REST API endpoints for document insertion and knowledge querying.

## Base URL

The default API server runs on:
```
http://movie.ft.tc:5000
```

You can configure the host and port using environment variables:
- `FLASK_HOST` (default: 0.0.0.0)
- `FLASK_PORT` (default: 5000)

## Available API Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Description:** Check the health status of the API server and ArangoDB connection.

**Parameters:** None

**Example Request:**
```bash
curl -X GET http://localhost:5000/health
```

**Example Response:**
```json
{
  "status": "healthy",
  "message": "PathRAG API is running",
  "arangodb_status": "connected",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

### 2. System Status

**Endpoint:** `GET /status`

**Description:** Get detailed system status information.

**Parameters:** None

**Example Request:**
```bash
curl -X GET http://localhost:5000/status
```

**Example Response:**
```json
{
  "pathrag_initialized": true,
  "arangodb_status": "connected",
  "working_directory": "/path/to/pathrag",
  "log_directory": "/home/user/pathrag/logs"
}
```

### 3. Insert Documents

**Endpoint:** `POST /insert`

**Description:** Insert documents into the PathRAG knowledge base for indexing.

**Required Parameters:**
- `documents` (string or array of strings): The document(s) to insert

**Example Request (Single Document):**
```bash
curl -X POST http://localhost:5000/insert \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "PathRAG is a graph-based retrieval augmented generation system that uses ArangoDB for knowledge storage."
  }'
```

**Example Request (Multiple Documents):**
```bash
curl -X POST http://localhost:5000/insert \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      "PathRAG provides efficient document indexing capabilities.",
      "It supports natural language querying with graph-based retrieval.",
      "ArangoDB is used as the backend storage for knowledge graphs."
    ]
  }'
```

**Example Response:**
```json
{
  "message": "Documents inserted successfully",
  "document_count": 3,
  "timestamp": "2024-01-15T10:35:00.123456"
}
```

### 4. Query Knowledge Base

**Endpoint:** `POST /query`

**Description:** Query the PathRAG knowledge base using natural language.

**Required Parameters:**
- `query` (string): The natural language query

**Optional Parameters (in `params` object):**
- `mode` (string): Query mode, currently supports "hybrid" (default: "hybrid")
- `only_need_context` (boolean): Return only context without generating response (default: false)
- `only_need_prompt` (boolean): Return only the system prompt (default: false)
- `response_type` (string): Type of response format (default: "Multiple Paragraphs")
- `stream` (boolean): Enable streaming response (default: false)
- `top_k` (integer): Number of top results to retrieve (default: 40)
- `max_token_for_text_unit` (integer): Maximum tokens for text units (default: 4000)
- `max_token_for_global_context` (integer): Maximum tokens for global context (default: 3000)
- `max_token_for_local_context` (integer): Maximum tokens for local context (default: 5000)

**Example Request (Basic Query):**
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is PathRAG and how does it work?"
  }'
```

**Example Request (With Parameters):**
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain the architecture of PathRAG",
    "params": {
      "mode": "hybrid",
      "response_type": "Detailed Explanation",
      "top_k": 20,
      "max_token_for_global_context": 2000
    }
  }'
```

**Example Response:**
```json
{
  "query": "What is PathRAG and how does it work?",
  "result": "PathRAG is a graph-based retrieval augmented generation system that combines the power of knowledge graphs with large language models. It works by first indexing documents into a graph structure stored in ArangoDB, then using hybrid retrieval methods to find relevant information for answering queries. The system extracts entities and relationships from documents, creates embeddings for semantic search, and uses both local and global context to generate comprehensive responses.",
  "params": {
    "mode": "hybrid",
    "top_k": 40
  },
  "timestamp": "2024-01-15T10:40:00.123456"
}
```

### 5. Insert Custom Knowledge Graph

**Endpoint:** `POST /insert_custom_kg`

**Description:** Insert custom knowledge graph data with predefined entities and relationships.

**Required Parameters:**
- `custom_kg` (object): Custom knowledge graph data containing:
  - `chunks` (array): Text chunks
  - `entities` (array): Entity definitions
  - `relationships` (array): Relationship definitions

**Example Request:**
```bash
curl -X POST http://localhost:5000/insert_custom_kg \
  -H "Content-Type: application/json" \
  -d '{
    "custom_kg": {
      "chunks": [
        "PathRAG is an advanced AI system.",
        "It uses graph databases for storage."
      ],
      "entities": [
        {"name": "PathRAG", "type": "System", "description": "AI retrieval system"},
        {"name": "ArangoDB", "type": "Database", "description": "Graph database"}
      ],
      "relationships": [
        {"source": "PathRAG", "target": "ArangoDB", "relation": "uses"}
      ]
    }
  }'
```

**Example Response:**
```json
{
  "message": "Custom knowledge graph inserted successfully",
  "entities_count": 2,
  "relationships_count": 1,
  "chunks_count": 2,
  "timestamp": "2024-01-15T10:45:00.123456"
}
```

### 6. Delete Entity

**Endpoint:** `DELETE /delete_entity`

**Description:** Delete an entity and its associated relationships from the knowledge graph.

**Required Parameters:**
- `entity_name` (string): Name of the entity to delete

**Example Request:**
```bash
curl -X DELETE http://localhost:5000/delete_entity \
  -H "Content-Type: application/json" \
  -d '{
    "entity_name": "PathRAG"
  }'
```

**Example Response:**
```json
{
  "message": "Entity deleted successfully",
  "entity_name": "PathRAG",
  "relationships_deleted": 3,
  "timestamp": "2024-01-15T10:50:00.123456"
}
```

### 7. Get Configuration

**Endpoint:** `GET /config`

**Description:** Retrieve sanitized configuration information (sensitive data excluded).

**Parameters:** None

**Example Request:**
```bash
curl -X GET http://localhost:5000/config
```

**Example Response:**
```json
{
  "pathrag_config": {
    "working_dir": "/path/to/pathrag",
    "enable_llm_cache": true,
    "default_top_k": 40
  },
  "api_config": {
    "host": "0.0.0.0",
    "port": 5000,
    "enable_cors": true
  },
  "timestamp": "2024-01-15T10:55:00.123456"
}
```

### 8. Get Statistics

**Endpoint:** `GET /stats`

**Description:** Get basic PathRAG system statistics.

**Parameters:** None

**Example Request:**
```bash
curl -X GET http://localhost:5000/stats
```

**Example Response:**
```json
{
  "total_documents": 150,
  "total_entities": 1250,
  "total_relationships": 3400,
  "cache_hit_rate": 0.85,
  "timestamp": "2024-01-15T11:00:00.123456"
}
```

## Error Responses

All endpoints return consistent error responses when something goes wrong:

**Example Error Response:**
```json
{
  "error": "No 'query' field provided",
  "endpoint": "/query",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `400`: Bad Request (missing or invalid parameters)
- `500`: Internal Server Error

## Query Parameters Reference

### QueryParam Options

When using the `/query` endpoint, you can customize the query behavior using these parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mode` | string | "hybrid" | Query mode (currently only "hybrid" supported) |
| `only_need_context` | boolean | false | Return only retrieved context without LLM response |
| `only_need_prompt` | boolean | false | Return only the system prompt |
| `response_type` | string | "Multiple Paragraphs" | Format of the generated response |
| `stream` | boolean | false | Enable streaming response |
| `top_k` | integer | 40 | Number of top results to retrieve |
| `max_token_for_text_unit` | integer | 4000 | Maximum tokens for individual text units |
| `max_token_for_global_context` | integer | 3000 | Maximum tokens for global context |
| `max_token_for_local_context` | integer | 5000 | Maximum tokens for local context |

## Configuration

The API server can be configured using environment variables. Key settings include:

### API Server Settings
- `FLASK_HOST`: Server host (default: 0.0.0.0)
- `FLASK_PORT`: Server port (default: 5000)
- `FLASK_DEBUG`: Debug mode (default: false)
- `FLASK_SECRET_KEY`: Secret key for sessions

### Rate Limiting
- `API_RATE_LIMIT`: Requests per period (default: 100)
- `API_RATE_LIMIT_PERIOD`: Period in seconds (default: 3600)

### CORS Settings
- `API_ENABLE_CORS`: Enable CORS (default: true)
- `API_CORS_ORIGINS`: Allowed origins (default: *)

### PathRAG Settings
- `PATHRAG_DEFAULT_TOP_K`: Default top-k value (default: 40)
- `PATHRAG_MAX_TOKEN_FOR_TEXT_UNIT`: Max tokens per text unit (default: 4000)
- `PATHRAG_MAX_TOKEN_FOR_GLOBAL_CONTEXT`: Max tokens for global context (default: 3000)
- `PATHRAG_MAX_TOKEN_FOR_LOCAL_CONTEXT`: Max tokens for local context (default: 5000)
- `PATHRAG_ENABLE_LLM_CACHE`: Enable LLM response caching (default: true)

## Best Practices

1. **Document Insertion**: Insert documents in batches for better performance
2. **Query Optimization**: Use appropriate `top_k` values based on your use case
3. **Context Management**: Adjust token limits based on your LLM model capabilities
4. **Error Handling**: Always check response status codes and handle errors gracefully
5. **Rate Limiting**: Respect the configured rate limits to avoid being throttled
6. **Caching**: Enable LLM caching for better performance on repeated queries

## Troubleshooting

### Common Issues

1. **Connection Refused**: Check if the API server is running and accessible
2. **ArangoDB Connection**: Verify ArangoDB is running and credentials are correct
3. **Memory Issues**: Adjust token limits if running into memory constraints
4. **Slow Responses**: Consider reducing `top_k` or enabling caching

### Checking Logs

Logs are typically stored in:
- Development: `./logs/pathrag.log`
- Production: `/home/pathrag/pathrag/logs/pathrag.log`

Use the `/status` endpoint to check system health and get log directory information.

## Example Integration

Here's a simple Python example of integrating with the PathRAG API:

```python
import requests
import json

class PathRAGClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    def health_check(self):
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def insert_documents(self, documents):
        payload = {"documents": documents}
        response = requests.post(
            f"{self.base_url}/insert",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        return response.json()
    
    def query(self, query_text, **params):
        payload = {
            "query": query_text,
            "params": params
        }
        response = requests.post(
            f"{self.base_url}/query",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        return response.json()

# Usage example
client = PathRAGClient()

# Check health
health = client.health_check()
print(f"API Status: {health['status']}")

# Insert documents
docs = [
    "PathRAG is a powerful knowledge retrieval system.",
    "It uses graph databases for efficient storage."
]
result = client.insert_documents(docs)
print(f"Inserted {result['document_count']} documents")

# Query the knowledge base
response = client.query(
    "What is PathRAG?",
    mode="hybrid",
    top_k=20
)
print(f"Answer: {response['result']}")
```

This documentation provides everything you need to integrate PathRAG into your external applications. For more detailed deployment and configuration information, refer to the deployment guides in the `docs` folder.