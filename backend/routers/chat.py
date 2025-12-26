from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from pydantic import BaseModel

from database import Database, ChatSession, ChatMessage
from rag_service import RAGService, RAGResponse

router = APIRouter(prefix="/chat", tags=["chat"])

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    selected_text: Optional[str] = None
    context: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    sources: List[Dict[str, Any]]
    tokens_used: Optional[Dict[str, int]]

class SessionRequest(BaseModel):
    metadata: Optional[Dict[str, Any]] = None

class SessionResponse(BaseModel):
    session_id: str
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]]

class MessageHistoryResponse(BaseModel):
    messages: List[ChatMessage]

# Global instances (in a real app, use dependency injection)
try:
    db = Database()
    print("Database instance created successfully")
except Exception as e:
    print(f"Error creating database instance: {str(e)}")
    db = None

try:
    rag_service = RAGService()
    print("RAG service instance created successfully")
except Exception as e:
    print(f"Error creating RAG service instance: {str(e)}")
    rag_service = None

@router.post("/", response_model=ChatResponse)
async def chat(chat_request: ChatRequest):
    """Handle a chat message and return a response."""
    try:
        # Connect to database if not already connected
        if not db.pool:
            await db.connect()
        
        # Create or validate session ID
        session_id = chat_request.session_id or str(uuid.uuid4())

        # Ensure session exists before adding message
        existing_session = await db.get_session(session_id)
        if not existing_session:
            # Create the session if it doesn't exist
            await db.create_session(session_id, metadata={"created_from_chat": True})

        # Add user message to session
        user_message = await db.add_message(
            session_id=session_id,
            role="user",
            content=chat_request.message,
            metadata={
                "selected_text": chat_request.selected_text,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Prepare context for RAG
        context = chat_request.context or ""
        if chat_request.selected_text:
            context += f"\n\nUser selected text: {chat_request.selected_text}"
        
        # Get response from RAG service
        rag_response: RAGResponse = await rag_service.query_with_sources(
            query=chat_request.message,
            session_id=session_id,
            max_context_chunks=5
        )
        
        # Add assistant response to session
        assistant_message = await db.add_message(
            session_id=session_id,
            role="assistant",
            content=rag_response.answer,
            metadata={
                "sources": rag_response.sources,
                "tokens_used": rag_response.tokens_used,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        return ChatResponse(
            response=rag_response.answer,
            session_id=session_id,
            sources=rag_response.sources,
            tokens_used=rag_response.tokens_used
        )
    except Exception as e:
        print(f"Chat error: {str(e)}")  # Log the error
        import traceback
        print(f"Traceback: {traceback.format_exc()}")  # Full traceback
        # Initialize database if not already connected
        try:
            if not db.pool:
                await db.connect()
        except Exception as db_error:
            print(f"Database connection error: {str(db_error)}")

        # Test RAG service
        try:
            # Test if RAG service can process a simple query
            test_response = await rag_service.query_with_sources(query="test", max_context_chunks=1)
            print("RAG service working fine")
        except Exception as rag_error:
            print(f"RAG service error: {str(rag_error)}")

        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@router.post("/session", response_model=SessionResponse)
async def create_session(session_request: SessionRequest = None):
    """Create a new chat session."""
    try:
        # Connect to database if not already connected
        if not db.pool:
            await db.connect()
        
        session_id = str(uuid.uuid4())
        metadata = session_request.metadata if session_request else {}
        
        session = await db.create_session(session_id, metadata)
        
        return SessionResponse(
            session_id=session.id,
            created_at=session.created_at,
            updated_at=session.updated_at,
            metadata=session.metadata
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")

@router.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get a specific chat session."""
    try:
        # Connect to database if not already connected
        if not db.pool:
            await db.connect()
        
        session = await db.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return SessionResponse(
            session_id=session.id,
            created_at=session.created_at,
            updated_at=session.updated_at,
            metadata=session.metadata
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving session: {str(e)}")

@router.get("/session/{session_id}/messages", response_model=MessageHistoryResponse)
async def get_session_messages(session_id: str):
    """Get all messages for a specific session."""
    try:
        # Connect to database if not already connected
        if not db.pool:
            await db.connect()
        
        # Verify session exists
        session = await db.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = await db.get_messages(session_id)
        
        return MessageHistoryResponse(messages=messages)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving messages: {str(e)}")

@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session and all its messages."""
    try:
        # Connect to database if not already connected
        if not db.pool:
            await db.connect()
        
        success = await db.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")

@router.get("/sessions", response_model=List[SessionResponse])
async def get_recent_sessions(limit: int = 20):
    """Get recent chat sessions."""
    try:
        # Connect to database if not already connected
        if not db.pool:
            await db.connect()
        
        sessions = await db.get_recent_sessions(limit=limit)
        
        return [
            SessionResponse(
                session_id=session.id,
                created_at=session.created_at,
                updated_at=session.updated_at,
                metadata=session.metadata
            )
            for session in sessions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving sessions: {str(e)}")

# Health check for the chat router
@router.get("/health")
async def chat_health():
    """Health check for the chat service."""
    return {"status": "healthy", "service": "chat"}
