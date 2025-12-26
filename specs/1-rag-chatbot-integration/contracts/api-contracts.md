# API Contracts: RAG-Based Chatbot Integration

## Overview
This document defines the API contracts for the RAG-based chatbot integration with the Physical AI and Humanoid Robotics book. The backend is built with FastAPI and provides endpoints for chat functionality, document ingestion, and health monitoring.

## Base URL
```
https://api.rag-chatbot.example.com
```

## Authentication
All endpoints use session-based authentication via the `session_id` parameter. No API keys are required as the system uses anonymous sessions.

## Common Error Responses
All endpoints may return these common error responses:

### 400 Bad Request
```json
{
  "detail": "string"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["string"],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "An unexpected error occurred"
}
```

## Endpoints

### Chat Operations

#### POST /api/chat
Initiates or continues a chat conversation with the AI assistant.

**Description**: Process a user message and return an AI response based on the book's documentation. If selected_text is provided, the response will be focused on that content.

**Request Body**:
```json
{
  "session_id": "string",
  "message": "string",
  "selected_text": "string (optional)"
}
```

**Request Body Fields**:
- `session_id`: Unique identifier for the chat session (UUID format). If not provided, a new session will be created.
- `message`: The user's message/question to the AI assistant (max 10000 characters).
- `selected_text`: Optional text that the user selected from the documentation (max 500 words).

**Success Response (200)**:
```json
{
  "response": "string",
  "session_id": "string",
  "sources": [
    {
      "document_id": "string",
      "title": "string",
      "path": "string"
    }
  ]
}
```

**Success Response Fields**:
- `response`: The AI-generated response to the user's message.
- `session_id`: The session identifier (new or existing).
- `sources`: Array of source documents used to generate the response.

**Example Request**:
```bash
curl -X POST https://api.rag-chatbot.example.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "message": "Explain how ROS 2 handles communication between nodes",
    "selected_text": "ROS 2 uses a publish-subscribe model for node communication"
  }'
```

**Example Response**:
```json
{
  "response": "ROS 2 handles communication between nodes using a publish-subscribe model where nodes can publish messages to topics and subscribe to topics to receive messages. This decouples publishers and subscribers in time and space.",
  "session_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "sources": [
    {
      "document_id": "module-1-ros/ros-nervous-system",
      "title": "ROS 2 as the Nervous System",
      "path": "/docs/modules/module-1-ros/ros-nervous-system"
    }
  ]
}
```

### Document Ingestion

#### POST /api/ingest
Processes documentation files and creates vector embeddings for RAG retrieval.

**Description**: Scans the /docs directory for markdown files, chunks them, generates embeddings, and stores them in the vector database.

**Request Body**:
```json
{
  "file_paths": ["string"],
  "force_reprocess": "boolean (default: false)"
}
```

**Request Body Fields**:
- `file_paths`: Array of file paths to process (if empty, processes all .md files in /docs).
- `force_reprocess`: Whether to reprocess files even if they already have embeddings.

**Success Response (200)**:
```json
{
  "processed_count": "integer",
  "status": "string",
  "details": {
    "processed_files": ["string"],
    "skipped_files": ["string"],
    "errors": [
      {
        "file_path": "string",
        "error": "string"
      }
    ]
  }
}
```

**Success Response Fields**:
- `processed_count`: Number of files successfully processed.
- `status`: Overall status of the ingestion process.
- `details`: Additional information about the processing results.

**Example Request**:
```bash
curl -X POST https://api.rag-chatbot.example.com/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "file_paths": ["/docs/modules/module-1-ros/index.md"],
    "force_reprocess": true
  }'
```

**Example Response**:
```json
{
  "processed_count": 1,
  "status": "completed",
  "details": {
    "processed_files": ["/docs/modules/module-1-ros/index.md"],
    "skipped_files": [],
    "errors": []
  }
}
```

### Health and Monitoring

#### GET /api/health
Checks the health status of the system and its dependencies.

**Description**: Returns the health status of the application and its connected services.

**Success Response (200)**:
```json
{
  "status": "string",
  "timestamp": "string (ISO 8601)",
  "dependencies": {
    "qdrant": {
      "status": "string",
      "response_time_ms": "integer"
    },
    "postgres": {
      "status": "string",
      "response_time_ms": "integer"
    },
    "openrouter": {
      "status": "string",
      "response_time_ms": "integer"
    }
  }
}
```

**Success Response Fields**:
- `status`: Overall system status ('healthy', 'degraded', 'unhealthy').
- `timestamp`: ISO 8601 timestamp of the health check.
- `dependencies`: Status of each external dependency.

**Example Request**:
```bash
curl -X GET https://api.rag-chatbot.example.com/api/health
```

**Example Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-22T10:30:00Z",
  "dependencies": {
    "qdrant": {
      "status": "connected",
      "response_time_ms": 25
    },
    "postgres": {
      "status": "connected",
      "response_time_ms": 15
    },
    "openrouter": {
      "status": "available",
      "response_time_ms": 120
    }
  }
}
```

#### GET /api/health/ready
Checks if the system is ready to handle requests.

**Description**: Returns whether the system is ready to process requests (all dependencies connected and operational).

**Success Response (200)**:
```json
{
  "status": "ready",
  "ready_services": ["qdrant", "postgres", "openrouter"]
}
```

**Service Unavailable Response (503)**:
```json
{
  "status": "not_ready",
  "missing_services": ["string"]
}
```

### Session Management

#### GET /api/session/{session_id}
Retrieves the chat history for a specific session.

**Description**: Returns the conversation history for the specified session.

**Path Parameters**:
- `session_id`: The session identifier to retrieve history for.

**Success Response (200)**:
```json
{
  "session_id": "string",
  "messages": [
    {
      "message_id": "string",
      "role": "string",
      "content": "string",
      "timestamp": "string (ISO 8601)"
    }
  ]
}
```

**Success Response Fields**:
- `session_id`: The session identifier.
- `messages`: Array of messages in chronological order.

**Example Request**:
```bash
curl -X GET https://api.rag-chatbot.example.com/api/session/a1b2c3d4-e5f6-7890-1234-567890abcdef
```

**Example Response**:
```json
{
  "session_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "messages": [
    {
      "message_id": "m1n2o3p4-q5r6-7890-1234-567890abcdef",
      "role": "user",
      "content": "What is ROS 2?",
      "timestamp": "2025-12-22T10:00:00Z"
    },
    {
      "message_id": "m2n3o4p5-q6r7-8901-2345-678901abcdef",
      "role": "assistant",
      "content": "ROS 2 (Robot Operating System 2) is a flexible framework for writing robot software...",
      "timestamp": "2025-12-22T10:00:02Z"
    }
  ]
}
```

## Data Models

### ChatMessage
Represents a single message in a chat conversation.

```json
{
  "message_id": "string (UUID)",
  "session_id": "string (UUID)",
  "role": "string (user|assistant)",
  "content": "string",
  "timestamp": "string (ISO 8601)"
}
```

### DocumentSource
Represents a source document used to generate a response.

```json
{
  "document_id": "string",
  "title": "string",
  "path": "string"
}
```

## Error Codes

### HTTP Status Codes
- `200`: Success
- `400`: Bad Request - Invalid input parameters
- `404`: Not Found - Session or resource not found
- `422`: Validation Error - Input validation failed
- `429`: Too Many Requests - Rate limit exceeded
- `500`: Internal Server Error - Unexpected server error
- `502`: Bad Gateway - External service error
- `503`: Service Unavailable - Dependency unavailable

### Application Error Codes
- `CHAT_001`: Session not found
- `CHAT_002`: Message content too long
- `CHAT_003`: Selected text exceeds limit
- `INGEST_001`: File processing error
- `INGEST_002`: Embedding generation failed
- `DB_001`: Database connection error
- `API_001`: External API error
- `RATE_LIMIT`: Rate limit exceeded

## Rate Limits
- Chat endpoint: 10 requests per minute per session
- Ingest endpoint: 1 request per 10 seconds per API key
- Health endpoints: Unlimited

## Security Considerations
- All sensitive data is handled server-side
- No PII is stored or transmitted
- Session IDs are UUIDs to prevent guessing
- Input validation prevents injection attacks
- Rate limiting prevents abuse