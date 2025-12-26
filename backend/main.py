from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="RAG Chatbot API",
    description="API for RAG-based chatbot integration with Docusaurus book",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=r"https?://.*",
    # Add exposed headers for frontend
    expose_headers=["Access-Control-Allow-Origin", "Access-Control-Allow-Credentials"]
)

# Setup error handling and logging middleware
from middleware.error_handler import setup_middleware
setup_middleware(app)

@app.get("/")
async def root():
    return {"message": "RAG Chatbot API is running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "RAG Chatbot API"}

# Include routers
try:
    from routers import chat, ingest, health
    app.include_router(chat.router, prefix="/api")
    app.include_router(ingest.router, prefix="/api")
    app.include_router(health.router, prefix="/api")
except ImportError as e:
    print(f"Error importing routers: {e}")
    # Import routers individually to see which one fails
    try:
        from routers import chat
        app.include_router(chat.router, prefix="/api")
    except ImportError as chat_error:
        print(f"Error importing chat router: {chat_error}")

    try:
        from routers import ingest
        app.include_router(ingest.router, prefix="/api")
    except ImportError as ingest_error:
        print(f"Error importing ingest router: {ingest_error}")

    try:
        from routers import health
        app.include_router(health.router, prefix="/api")
    except ImportError as health_error:
        print(f"Error importing health router: {health_error}")

if __name__ == "__main__":
    import uvicorn
    import asyncio
    from scheduler import start_document_scheduler

    async def run_server_with_scheduler():
        # Start the scheduler in the background
        scheduler_task = asyncio.create_task(start_document_scheduler())

        # Run the FastAPI server
        config = uvicorn.Config(app, host="0.0.0.0", port=8004, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()

        # Cancel the scheduler task when server stops
        scheduler_task.cancel()

    # Run both the server and scheduler
    asyncio.run(run_server_with_scheduler())