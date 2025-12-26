# Tasks: RAG-Based Chatbot Integration

## Feature: 1-rag-chatbot-integration
**Description**: RAG-based chatbot integrated into the Docusaurus book with selection-based QA functionality

## Phase 1: Setup and Backend Foundation

### T001 [P] Create backend directory structure and initialize FastAPI
- **Description**: Create the backend directory and set up the initial FastAPI application structure
- **File**: `/backend/main.py`
- **Implementation**:
  - Create `/backend/` directory
  - Initialize FastAPI app with basic configuration
  - Set up basic routes structure
  - Create requirements.txt with FastAPI dependencies
- **Status**: TODO

### T002 [P] Set up project dependencies and environment
- **Description**: Configure all required dependencies for the backend application
- **File**: `/backend/requirements.txt`
- **Implementation**:
  - Add FastAPI, uvicorn, asyncpg, qdrant-client, python-dotenv
  - Add openrouter or appropriate LLM client library
  - Add markdown processing libraries
  - Include embedding model dependencies
- **Status**: TODO

## Phase 2: Document Ingestion Pipeline

### T003 [P] Write document ingestion script to parse MD files
- **Description**: Create script to parse MD files from the docs folder and prepare for embedding
- **File**: `/backend/ingest_docs.py`
- **Implementation**:
  - Scan `/docs/` directory for all .md files
  - Parse markdown content while preserving structure
  - Extract text content and metadata
  - Implement chunking logic (max 500 words per chunk)
  - Add filtering for excluded directories/files
- **Status**: TODO

### T004 [P] Implement Qwen embedding integration
- **Description**: Integrate Qwen embedding model to generate vector representations
- **File**: `/backend/embedding_service.py`
- **Implementation**:
  - Create embedding service class
  - Implement Qwen embedding generation
  - Add error handling for API calls
  - Implement fallback mechanisms if needed
  - Add caching for repeated embeddings
- **Status**: TODO

### T005 [P] Set up Qdrant client and vector storage
- **Description**: Configure Qdrant client to store document vectors for the Physical AI modules
- **File**: `/backend/vector_db.py`
- **Implementation**:
  - Create Qdrant client configuration
  - Set up collection for documentation chunks
  - Implement upsert functionality for new documents
  - Add similarity search capabilities
  - Create schema for document metadata
- **Status**: TODO

## Phase 3: Core RAG Logic

### T006 [P] Integrate OpenRouter API for LLM responses
- **Description**: Connect to OpenRouter API and implement LLM response generation
- **File**: `/backend/llm_service.py`
- **Implementation**:
  - Create OpenRouter API client
  - Implement prompt formatting for context
  - Add proper error handling and retries
  - Implement response streaming if available
  - Add rate limiting and usage tracking
- **Status**: TODO

### T007 [P] Implement RAG retrieval chain logic
- **Description**: Create the retrieval-augmented generation chain that connects all components
- **File**: `/backend/rag_service.py`
- **Implementation**:
  - Implement vector similarity search
  - Combine retrieved context with user query
  - Format prompts for OpenRouter
  - Process and return LLM responses
  - Add source attribution for responses
- **Status**: TODO

## Phase 4: Database Integration

### T008 [P] Set up Neon Postgres for chat history
- **Description**: Configure Neon Postgres database connection and session management
- **File**: `/backend/database.py`
- **Implementation**:
  - Create database connection pool
  - Define ChatSession and ChatMessage models
  - Implement session creation and management
  - Add chat history storage and retrieval
  - Create cleanup jobs for expired sessions
- **Status**: TODO

### T009 [P] Create chat session management endpoints
- **Description**: Implement API endpoints for managing chat sessions and history
- **File**: `/backend/routers/chat.py`
- **Implementation**:
  - Create /api/chat endpoint for conversations
  - Implement session creation with UUID
  - Add message storage and retrieval
  - Include error handling and validation
  - Add session expiration management
- **Status**: TODO

## Phase 5: Frontend Integration

### T010 [P] Create Docusaurus theme component for floating chat UI
- **Description**: Build a React component that floats on all Docusaurus pages
- **File**: `/frontend/src/theme/ChatWidget/index.js`
- **Implementation**:
  - Create React component for chat widget
  - Implement floating position (bottom-right)
  - Add expand/collapse functionality
  - Create message display area
  - Implement input field and send button
- **Status**: TODO

### T011 [P] Implement cyberpunk/robotics CSS styling
- **Description**: Create CSS with electric blue/dark mode theme for the chat widget
- **File**: `/frontend/src/theme/ChatWidget/styles.css`
- **Implementation**:
  - Design dark theme with electric blue accents
  - Create cyberpunk-inspired UI elements
  - Implement responsive design
  - Add animations and transitions
  - Ensure accessibility compliance
- **Status**: TODO

### T012 [P] Add text selection capture feature
- **Description**: Implement feature to capture window.getSelection() and send as context
- **File**: `/frontend/src/theme/ChatWidget/TextSelection.js`
- **Implementation**:
  - Create text selection detection
  - Implement "Consult AI" button that appears on selection
  - Limit selection to 500 words
  - Position button near selection
  - Send selected text as context to backend
- **Status**: TODO

## Phase 6: Integration and Configuration

### T013 [P] Update docusaurus.config.js with backend API URL
- **Description**: Configure Docusaurus to connect to the backend API
- **File**: `/frontend/docusaurus.config.js`
- **Implementation**:
  - Add backend API URL configuration
  - Configure any necessary environment variables
  - Update plugin configuration for chat widget
  - Add any required metadata
- **Status**: TODO

### T014 [P] Create ingestion endpoint for document processing
- **Description**: Add API endpoint to trigger document ingestion and embedding
- **File**: `/backend/routers/ingest.py`
- **Implementation**:
  - Create /api/ingest endpoint
  - Connect to document ingestion service
  - Add progress tracking
  - Implement force reprocessing option
  - Add status reporting
- **Status**: TODO

## Phase 7: Testing and Polish

### T015 [P] Implement health check endpoints
- **Description**: Add health monitoring endpoints for system status
- **File**: `/backend/routers/health.py`
- **Implementation**:
  - Create /api/health endpoint
  - Check connectivity to all services
  - Report response times
  - Add readiness endpoint
- **Status**: TODO

### T016 [P] Add comprehensive error handling
- **Description**: Implement proper error handling throughout the application
- **File**: `/backend/middleware/error_handler.py`
- **Implementation**:
  - Create global error handler
  - Add custom exception classes
  - Implement user-friendly error messages
  - Add logging for debugging
- **Status**: TODO

### T017 [P] Implement scheduled document updates
- **Description**: Create scheduled task to update embeddings when docs change
- **File**: `/backend/scheduler.py`
- **Implementation**:
  - Set up scheduled task for daily updates
  - Monitor docs directory for changes
  - Process only changed files
  - Add notification system for processing status
- **Status**: TODO

## Dependencies

- **Backend**: FastAPI server must be running before frontend integration
- **Database**: Neon Postgres connection required for chat history
- **Vector DB**: Qdrant Cloud must be configured before ingestion
- **API Keys**: OpenRouter and Qdrant keys must be configured

## Parallel Execution Opportunities

- Tasks T001-T002 can run in parallel with T008
- Tasks T010-T012 can run after T001 is complete
- Tasks T003-T007 can run in parallel once dependencies are met
- Tasks T015-T017 can run after core functionality is implemented

## Implementation Strategy

1. **MVP First**: Implement basic chat functionality with static responses
2. **RAG Integration**: Add document retrieval and LLM integration
3. **UI Enhancement**: Add text selection and styling
4. **Polish**: Add error handling, monitoring, and scheduled updates