# Implementation Plan: RAG-Based Chatbot Integration

## Technical Context

### Architecture Overview
- **Frontend**: Docusaurus-based documentation site with integrated React chat component
- **Backend**: FastAPI server handling RAG logic, embeddings, and chat history
- **Vector Database**: Qdrant Cloud for document embeddings and retrieval
- **Database**: Neon Serverless Postgres for chat history storage
- **LLM API**: OpenRouter with Claude 3.5 Sonnet
- **Embeddings**: Qwen embeddings for document processing

### Technology Stack
- **Backend Framework**: FastAPI (Python)
- **Frontend Framework**: React (integrated with Docusaurus)
- **Vector Database**: Qdrant Cloud
- **Relational Database**: Neon Postgres
- **LLM Provider**: OpenRouter
- **Embedding Model**: Qwen
- **Deployment**: Cloud platform (TBD)

### Dependencies
- FastAPI and related dependencies (Pydantic, uvicorn, etc.)
- Qdrant client library
- AsyncPG or similar for Postgres connectivity
- OpenRouter API client
- Sentence transformers or similar for embeddings
- Docusaurus plugin system for frontend integration

### Unknowns
- Specific OpenRouter API rate limits and pricing
- Qwen embedding model access method and performance characteristics
- Qdrant Cloud API rate limits and performance
- Neon Postgres connection pooling best practices
- Docusaurus plugin development requirements

## Constitution Check

### Alignment with Project Principles
- ✅ **User-Centric**: Directly improves user experience by providing immediate Q&A capability
- ✅ **Quality Focus**: Uses high-quality LLM (Claude 3.5 Sonnet) for accurate responses
- ✅ **Performance**: Implements caching and efficient retrieval to maintain responsiveness
- ✅ **Security**: Anonymous sessions protect user privacy while maintaining functionality
- ✅ **Scalability**: Cloud-based infrastructure supports growth

### Potential Violations & Mitigation
- **API Costs**: Monitor usage and implement rate limiting to prevent excessive charges
- **Response Latency**: Implement proper caching and connection pooling to maintain 5-second response time

## Gates

### ✅ Planning Gates Passed
- [X] Architecture aligns with project goals
- [X] Technology choices support success criteria
- [X] Implementation approach is technically feasible
- [X] Performance requirements are achievable
- [X] Security and privacy requirements addressed

## Phase 0: Research & Preparation

### Research Findings

#### RQ-01: OpenRouter API Integration
- **Decision**: Use OpenRouter's API with Claude 3.5 Sonnet model
- **Rationale**: Provides access to high-quality LLM with good documentation and support
- **Alternatives considered**: Direct Anthropic API, other LLM providers
- **Implementation**: Use OpenRouter Python SDK with proper error handling and retry logic

#### RQ-02: Qwen Embedding Model Access
- **Decision**: Use Alibaba Cloud's Qwen embedding API or local model
- **Rationale**: Matches requirements from specification and provides good performance
- **Alternatives considered**: OpenAI embeddings, Sentence Transformers models
- **Implementation**: Implement both cloud and local options with fallback mechanism

#### RQ-03: Qdrant Vector Database Integration
- **Decision**: Use Qdrant Cloud with async client for performance
- **Rationale**: Good performance characteristics and cloud-hosted option fits requirements
- **Alternatives considered**: Pinecone, Weaviate, ChromaDB
- **Implementation**: Use Qdrant Python client with async operations

#### RQ-04: Neon Postgres Connection Management
- **Decision**: Use async connection pooling with proper session management
- **Rationale**: Neon's serverless features align with usage patterns and cost requirements
- **Alternatives considered**: Supabase, traditional Postgres, SQLite
- **Implementation**: Use asyncpg with connection pooling and proper transaction management

#### RQ-05: Docusaurus Integration Approach
- **Decision**: Create custom React component with Docusaurus plugin
- **Rationale**: Maintains design consistency while adding functionality
- **Alternatives considered**: Iframe embedding, external widget
- **Implementation**: React component with proper lifecycle management

## Phase 1: System Design

### Data Model

#### ChatSession Entity
- `session_id`: UUID (Primary Key) - Unique identifier for the conversation
- `created_at`: DateTime (Default: now) - Timestamp when session started
- `updated_at`: DateTime (Default: now) - Timestamp of last activity
- `expires_at`: DateTime - Session expiration time (for cleanup)

#### ChatMessage Entity
- `message_id`: UUID (Primary Key) - Unique identifier for the message
- `session_id`: UUID (Foreign Key) - Reference to the chat session
- `role`: String (Values: 'user', 'assistant') - Message sender role
- `content`: Text - The text content of the message
- `timestamp`: DateTime (Default: now) - When the message was created
- `metadata`: JSON (Optional) - Additional message metadata

#### DocumentChunk Entity
- `chunk_id`: UUID (Primary Key) - Unique identifier for the document chunk
- `document_id`: String - Reference to the source document
- `content`: Text - The text content of the chunk
- `embedding`: Vector - Vector representation of the content
- `metadata`: JSON - Additional information about the chunk (path, title, etc.)
- `created_at`: DateTime (Default: now) - When the chunk was created

### API Contracts

#### Backend API Endpoints

**POST /api/chat**
- **Purpose**: Process chat messages and return responses
- **Request Body**:
  ```json
  {
    "session_id": "string",
    "message": "string",
    "selected_text": "string (optional)"
  }
  ```
- **Response**:
  ```json
  {
    "response": "string",
    "session_id": "string"
  }
  ```
- **Errors**: 400 (bad request), 500 (internal server error)

**POST /api/ingest**
- **Purpose**: Process documentation files and create embeddings
- **Request Body**:
  ```json
  {
    "file_paths": ["string"],
    "force_reprocess": "boolean (default: false)"
  }
  ```
- **Response**:
  ```json
  {
    "processed_count": "number",
    "status": "string"
  }
  ```
- **Errors**: 400 (bad request), 500 (internal server error)

**GET /api/health**
- **Purpose**: Check system health and dependencies
- **Response**:
  ```json
  {
    "status": "healthy",
    "dependencies": {
      "qdrant": "connected",
      "postgres": "connected",
      "openrouter": "available"
    }
  }
  ```

### Frontend Integration

#### Docusaurus Plugin Components
- **FloatingChatWidget**: React component that appears on all pages
- **TextSelectionHandler**: Custom hook to detect text selection and show "Consult AI" button
- **ChatModal**: Modal interface for full chat experience

#### Text Selection Hook Requirements
- Detect text selection across all browsers
- Show "Consult AI" button near selection
- Limit selection to 500 words
- Pass selected text to chat interface

## Phase 2: Implementation Strategy

### Backend Implementation (FastAPI)

#### 1. Backend Setup
- **Directory Structure**: `/backend/rag_chatbot/`
- **Core Files**:
  - `main.py`: FastAPI application entry point
  - `config.py`: Configuration and settings management
  - `dependencies.py`: Shared dependencies and database connections
  - `models/`: Pydantic models for request/response validation
  - `schemas/`: Database schema definitions
  - `services/`: Business logic implementations
  - `routers/`: API route definitions

#### 2. Ingestion Pipeline
- **File Processing**: Scan /docs directory for .md files
- **Text Chunking**: Split documents into manageable chunks (500-1000 words)
- **Embedding Generation**: Generate Qwen embeddings for each chunk
- **Vector Storage**: Upsert embeddings to Qdrant Cloud with metadata
- **Scheduling**: Implement daily scheduled updates

#### 3. RAG Logic Implementation
- **Retrieval Component**: Query Qdrant for relevant document chunks
- **Context Assembly**: Combine retrieved chunks with user query
- **LLM Integration**: Format prompt and send to OpenRouter
- **Response Processing**: Format and return response to frontend

#### 4. Database Integration
- **Connection Pooling**: Implement async connection pooling with Neon Postgres
- **Session Management**: Handle anonymous session creation and persistence
- **Chat History**: Store and retrieve conversation history
- **Cleanup Jobs**: Implement session expiration and cleanup

### Frontend Implementation (Docusaurus/React)

#### 1. Floating Chat Component
- **Positioning**: Fixed position in bottom-right corner
- **State Management**: React hooks for chat state
- **UI Components**: Message history, input area, typing indicators
- **API Integration**: Connect to backend API endpoints

#### 2. Text Selection Feature
- **Event Listeners**: Monitor for text selection events
- **Word Counting**: Implement 500-word limit
- **Button Placement**: Dynamic positioning near selection
- **Context Passing**: Send selected text with user query

#### 3. Docusaurus Integration
- **Plugin Development**: Create reusable Docusaurus plugin
- **Theme Compatibility**: Ensure design consistency
- **Page Integration**: Include component on all documentation pages

## Risk Analysis

### High-Risk Items
1. **API Costs**: LLM and embedding API usage could become expensive
   - *Mitigation*: Implement usage tracking and rate limiting

2. **Performance**: Vector search and LLM calls may exceed 5-second requirement
   - *Mitigation*: Implement caching and optimize chunk sizes

3. **Data Freshness**: Scheduled updates may not reflect real-time content changes
   - *Mitigation*: Provide manual refresh option and monitor update frequency

### Medium-Risk Items
1. **Dependency Availability**: Third-party services (OpenRouter, Qdrant) could have outages
   - *Mitigation*: Implement graceful degradation and fallback mechanisms

2. **Document Processing**: Large documentation sets may take long to process
   - *Mitigation*: Implement incremental processing and progress tracking

## Success Criteria Verification

### Performance Targets
- [ ] 5-second response time for 95% of queries
- [ ] 99% availability during business hours
- [ ] Support for 100 concurrent users

### Quality Targets
- [ ] 85% of user questions receive contextually appropriate responses
- [ ] Selection-based QA feature used by 60% of active users
- [ ] User engagement time increases by 25%
- [ ] User satisfaction score increases by 30%

## Deployment Strategy

### Environment Setup
1. **Development**: Local Docker setup with mock services
2. **Staging**: Cloud deployment with limited access
3. **Production**: Full cloud deployment with monitoring

### Rollout Plan
1. **Phase 1**: Backend API development and testing
2. **Phase 2**: Frontend integration and testing
3. **Phase 3**: Documentation processing and initial embedding
4. **Phase 4**: Gradual rollout to production

## Operational Considerations

### Monitoring
- API response times and error rates
- Database connection pool metrics
- Vector database query performance
- LLM API usage and costs

### Maintenance
- Scheduled documentation reprocessing
- Session cleanup jobs
- Embedding model updates
- Performance optimization

## Constitution Check Post-Design

### ✅ Alignment Confirmed
- **User Experience**: Directly improves user experience as intended
- **Quality Standards**: Uses appropriate technology stack for requirements
- **Performance**: Architecture supports 5-second response time goal
- **Security**: Anonymous sessions protect user privacy
- **Maintainability**: Clean architecture with clear separation of concerns