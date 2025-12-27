import os
import asyncio
import asyncpg
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
from dotenv import load_dotenv
import json

load_dotenv()

class ChatSession(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None

class ChatMessage(BaseModel):
    id: str
    session_id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class Database:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        self.pool = None

    async def connect(self):
        """Create a connection pool to the database."""
        try:
            self.pool = await asyncpg.create_pool(
                dsn=self.database_url,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            
            # Initialize tables
            await self._initialize_tables()
            print("Database connection established and tables initialized")
        except Exception as e:
            print(f"Error connecting to database: {str(e)}")
            raise

    async def _initialize_tables(self):
        """Create the necessary tables if they don't exist."""
        async with self.pool.acquire() as conn:
            # Create chat_sessions table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB DEFAULT '{}'
                )
            """)
            
            # Create chat_messages table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB DEFAULT '{}',
                    FOREIGN KEY (session_id) REFERENCES chat_sessions (id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for better performance
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id 
                ON chat_messages (session_id)
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp 
                ON chat_messages (timestamp)
            """)

    async def create_session(self, session_id: str, metadata: Optional[Dict[str, Any]] = None) -> ChatSession:
        """Create a new chat session."""
        async with self.pool.acquire() as conn:
            try:
                # Insert the new session
                import json
                json_metadata = json.dumps(metadata or {})
                await conn.execute(
                    """
                    INSERT INTO chat_sessions (id, metadata)
                    VALUES ($1, $2)
                    """,
                    session_id,
                    json_metadata
                )
                
                # Return the created session
                row = await conn.fetchrow(
                    """
                    SELECT id, created_at, updated_at, metadata
                    FROM chat_sessions
                    WHERE id = $1
                    """,
                    session_id
                )
                
                # Handle metadata that might be stored as JSON string
                metadata = row['metadata']
                if isinstance(metadata, str):
                    try:
                        import json
                        metadata = json.loads(metadata)
                    except json.JSONDecodeError:
                        metadata = {}

                return ChatSession(
                    id=row['id'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    metadata=metadata
                )
            except Exception as e:
                print(f"Error creating session: {str(e)}")
                raise

    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get a chat session by ID."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, created_at, updated_at, metadata
                FROM chat_sessions
                WHERE id = $1
                """,
                session_id
            )
            
            if row:
                # Handle metadata that might be stored as JSON string
                metadata = row['metadata']
                if isinstance(metadata, str):
                    try:
                        import json
                        metadata = json.loads(metadata)
                    except json.JSONDecodeError:
                        metadata = {}

                return ChatSession(
                    id=row['id'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    metadata=metadata
                )
            return None

    async def update_session(self, session_id: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update a chat session's metadata."""
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow(
                """
                UPDATE chat_sessions
                SET metadata = $2, updated_at = CURRENT_TIMESTAMP
                WHERE id = $1
                RETURNING id
                """,
                session_id,
                json.dumps(metadata or {})
            )
            
            return result is not None

    async def delete_session(self, session_id: str) -> bool:
        """Delete a chat session and all its messages."""
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow(
                """
                DELETE FROM chat_sessions
                WHERE id = $1
                RETURNING id
                """,
                session_id
            )
            
            return result is not None

    async def add_message(self, session_id: str, role: str, content: str, 
                         message_id: str = None, metadata: Optional[Dict[str, Any]] = None) -> ChatMessage:
        """Add a message to a chat session."""
        import uuid
        
        message_id = message_id or str(uuid.uuid4())
        
        async with self.pool.acquire() as conn:
            # Insert the new message
            await conn.execute(
                """
                INSERT INTO chat_messages (id, session_id, role, content, metadata)
                VALUES ($1, $2, $3, $4, $5)
                """,
                message_id,
                session_id,
                role,
                content,
                json.dumps(metadata or {})
            )
            
            # Update the session's updated_at timestamp
            await conn.execute(
                """
                UPDATE chat_sessions
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = $1
                """,
                session_id
            )
            
            # Return the created message
            row = await conn.fetchrow(
                """
                SELECT id, session_id, role, content, timestamp, metadata
                FROM chat_messages
                WHERE id = $1
                """,
                message_id
            )
            
            return ChatMessage(
                id=row['id'],
                session_id=row['session_id'],
                role=row['role'],
                content=row['content'],
                timestamp=row['timestamp'],
                metadata=self._parse_metadata(row['metadata'])
            )

    async def get_messages(self, session_id: str, limit: int = 50, offset: int = 0) -> List[ChatMessage]:
        """Get messages for a specific session, ordered by timestamp."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, session_id, role, content, timestamp, metadata
                FROM chat_messages
                WHERE session_id = $1
                ORDER BY timestamp ASC
                LIMIT $2 OFFSET $3
                """,
                session_id, limit, offset
            )
            
            result = []
            for row in rows:
                # Handle metadata that might be stored as JSON string
                metadata = row['metadata']
                if isinstance(metadata, str):
                    try:
                        import json
                        metadata = json.loads(metadata)
                    except json.JSONDecodeError:
                        metadata = {}

                result.append(
                    ChatMessage(
                        id=row['id'],
                        session_id=row['session_id'],
                        role=row['role'],
                        content=row['content'],
                        timestamp=row['timestamp'],
                        metadata=metadata
                    )
                )
            return result

    async def get_recent_sessions(self, limit: int = 20) -> List[ChatSession]:
        """Get the most recently updated chat sessions."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, created_at, updated_at, metadata
                FROM chat_sessions
                ORDER BY updated_at DESC
                LIMIT $1
                """,
                limit
            )
            
            result = []
            for row in rows:
                # Handle metadata that might be stored as JSON string
                metadata = row['metadata']
                if isinstance(metadata, str):
                    try:
                        import json
                        metadata = json.loads(metadata)
                    except json.JSONDecodeError:
                        metadata = {}

                result.append(
                    ChatSession(
                        id=row['id'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at'],
                        metadata=metadata
                    )
                )
            return result

    async def delete_old_sessions(self, days: int = 30) -> int:
        """Delete sessions that haven't been updated in the specified number of days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                """
                DELETE FROM chat_sessions
                WHERE updated_at < $1
                RETURNING COUNT(*)
                """,
                cutoff_date
            )
            
            return result or 0

    async def get_session_stats(self) -> Dict[str, int]:
        """Get statistics about chat sessions."""
        async with self.pool.acquire() as conn:
            # Total sessions
            total_sessions = await conn.fetchval("SELECT COUNT(*) FROM chat_sessions")
            
            # Total messages
            total_messages = await conn.fetchval("SELECT COUNT(*) FROM chat_messages")
            
            # Sessions in last 24 hours
            recent_sessions = await conn.fetchval(
                "SELECT COUNT(*) FROM chat_sessions WHERE updated_at > NOW() - INTERVAL '1 day'"
            )
            
            return {
                "total_sessions": total_sessions,
                "total_messages": total_messages,
                "recent_sessions": recent_sessions
            }

    def _parse_metadata(self, metadata_value):
        """Parse metadata that might be stored as JSON string or dict."""
        import json
        if isinstance(metadata_value, str):
            try:
                return json.loads(metadata_value)
            except json.JSONDecodeError:
                return {}
        return metadata_value if metadata_value is not None else {}
    async def close(self):
        """Close the database connection pool."""
        if self.pool:
            await self.pool.close()

# Example usage function
async def test_database():
    """Test the database functionality."""
    # Note: This requires a valid DATABASE_URL to be set
    if not os.getenv("DATABASE_URL"):
        print("DATABASE_URL not set, skipping database test")
        return
    
    db = Database()
    try:
        await db.connect()
        
        import uuid
        session_id = str(uuid.uuid4())
        
        # Create a session
        session = await db.create_session(session_id, {"user_type": "test", "source": "api"})
        print(f"Created session: {session.id}")
        
        # Add some messages
        await db.add_message(session_id, "user", "Hello, how does RAG work?")
        await db.add_message(session_id, "assistant", "RAG stands for Retrieval-Augmented Generation...")
        
        # Get messages
        messages = await db.get_messages(session_id)
        print(f"Retrieved {len(messages)} messages")
        
        # Get session
        retrieved_session = await db.get_session(session_id)
        print(f"Retrieved session: {retrieved_session.id}")
        
        # Get stats
        stats = await db.get_session_stats()
        print(f"Database stats: {stats}")
        
    except Exception as e:
        print(f"Error during database test: {str(e)}")
    finally:
        await db.close()

if __name__ == "__main__":
    async def main():
        await test_database()

    asyncio.run(main())
