from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Simple Chat API",
    description="Basic chat API for frontend integration",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Add exposed headers for frontend
    expose_headers=["Access-Control-Allow-Origin", "Access-Control-Allow-Credentials"]
)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "chat-api"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Generate a session ID if not provided
        session_id = request.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Simple response logic - in a real app, this would connect to LLM
        user_message = request.message.lower()

        if "hello" in user_message or "hi" in user_message:
            response = "Hello! I'm your AI assistant for Physical AI and Humanoid Robotics. How can I help you today?"
        elif "physical ai" in user_message:
            response = "Physical AI is an interdisciplinary field that combines artificial intelligence with physical systems. It focuses on creating AI systems that can understand, interact with, and manipulate the physical world."
        elif "robotics" in user_message:
            response = "Humanoid robotics involves creating robots with human-like characteristics and behaviors. This includes locomotion, manipulation, and social interaction capabilities."
        else:
            response = f"I received your message: '{request.message}'. I'm a simple AI assistant. For more complex queries about Physical AI and Robotics, please be more specific."

        return ChatResponse(
            response=response,
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)