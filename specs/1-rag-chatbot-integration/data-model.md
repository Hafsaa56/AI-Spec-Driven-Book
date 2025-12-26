# Data Model: RAG-Based Chatbot Integration

## Entity Models

### ChatSession
**Description**: Represents a user's chat session with the AI assistant

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| session_id | UUID | Primary Key, Not Null | Unique identifier for the conversation |
| created_at | DateTime | Not Null, Default: now | Timestamp when session started |
| updated_at | DateTime | Not Null, Default: now | Timestamp of last activity |
| expires_at | DateTime | Not Null | Session expiration time (for cleanup) |

**Relationships**:
- One-to-Many with ChatMessage (via session_id foreign key)

**Validation Rules**:
- session_id must be a valid UUID
- created_at must be before updated_at
- expires_at must be in the future

### ChatMessage
**Description**: Represents a single message in a chat conversation

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| message_id | UUID | Primary Key, Not Null | Unique identifier for the message |
| session_id | UUID | Foreign Key, Not Null | Reference to the chat session |
| role | String | Not Null, Check: 'user'/'assistant' | Message sender role |
| content | Text | Not Null, Max: 10000 chars | The text content of the message |
| timestamp | DateTime | Not Null, Default: now | When the message was created |
| metadata | JSON | Optional | Additional message metadata |

**Relationships**:
- Many-to-One with ChatSession (via session_id foreign key)

**Validation Rules**:
- role must be either 'user' or 'assistant'
- content length must be between 1 and 10000 characters
- session_id must reference an existing ChatSession

### DocumentChunk
**Description**: Represents a chunk of documentation content with embeddings

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| chunk_id | UUID | Primary Key, Not Null | Unique identifier for the document chunk |
| document_id | String | Not Null | Reference to the source document |
| content | Text | Not Null, Max: 2000 chars | The text content of the chunk |
| embedding | Vector | Not Null | Vector representation of the content |
| metadata | JSON | Not Null | Additional information about the chunk |
| created_at | DateTime | Not Null, Default: now | When the chunk was created |

**Relationships**:
- No direct database relationships (referenced by document_id)

**Validation Rules**:
- content length must be between 10 and 2000 characters
- embedding must be a valid vector representation
- metadata must include 'source_path' and 'title' fields

## Database Schema

### Neon Postgres Schema

```sql
-- Chat sessions table
CREATE TABLE chat_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Chat messages table
CREATE TABLE chat_messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB
);

-- Indexes for performance
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_timestamp ON chat_messages(timestamp DESC);
CREATE INDEX idx_chat_sessions_expires_at ON chat_sessions(expires_at);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER update_chat_sessions_updated_at
    BEFORE UPDATE ON chat_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

## Vector Database Schema (Qdrant)

### Collection Configuration
- **Collection Name**: `documentation_chunks`
- **Vector Size**: Determined by Qwen embedding model (likely 768 or 1536 dimensions)
- **Distance Function**: Cosine distance
- **Sharding**: Based on expected data size

### Payload Structure
```json
{
  "chunk_id": "uuid",
  "document_id": "string",
  "source_path": "string",
  "title": "string",
  "content": "string",
  "created_at": "timestamp"
}
```

## State Transitions

### ChatSession States
- **Active**: Session is currently in use
- **Inactive**: Session has no recent activity
- **Expired**: Session has exceeded its lifetime and should be cleaned up

### State Transition Rules
- New sessions start in **Active** state
- Sessions transition to **Inactive** after 30 minutes of inactivity
- Sessions transition to **Expired** after 24 hours from creation
- Expired sessions are eligible for cleanup

## Data Lifecycle

### Chat Data
1. **Creation**: New session created when user starts chat
2. **Growth**: Messages added as conversation continues
3. **Inactivity**: Session marked inactive after timeout
4. **Expiration**: Session data marked for cleanup after expiry
5. **Deletion**: Expired sessions and messages purged

### Document Data
1. **Ingestion**: Documents processed and split into chunks
2. **Embedding**: Vector representations created
3. **Storage**: Chunks stored in vector database
4. **Update**: Chunks updated when source documents change
5. **Deletion**: Chunks removed when source documents are deleted

## Relationships and Constraints

### Referential Integrity
- ChatMessage.session_id must reference an existing ChatSession
- Deletion of ChatSession cascades to related ChatMessages

### Performance Considerations
- Chat messages are indexed by session_id for fast retrieval
- Timestamp indexing enables efficient history queries
- Vector database optimized for similarity search operations

### Data Consistency
- Transactional operations ensure session-message consistency
- Atomic updates maintain data integrity during concurrent access
- Validation rules enforced at both application and database levels