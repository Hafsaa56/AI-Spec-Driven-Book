from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Dict, Any
import asyncio
from pydantic import BaseModel

from ingest_docs import process_docs, DocumentChunk
from rag_service import RAGService

router = APIRouter(prefix="/ingest", tags=["ingest"])

class IngestRequest(BaseModel):
    file_paths: List[str] = None
    force_reprocess: bool = False

class IngestResponse(BaseModel):
    status: str
    processed_files: int
    processed_chunks: int
    details: List[Dict[str, Any]]

class ProgressResponse(BaseModel):
    status: str
    progress: float
    details: str

# Global RAG service instance
rag_service = RAGService()

@router.post("/", response_model=IngestResponse)
async def ingest_documents(ingest_request: IngestRequest = None):
    """Ingest documents from the docs directory into the vector database."""
    try:
        # Use default docs path if no specific paths provided
        docs_path = "docs"
        if ingest_request and ingest_request.file_paths:
            # For now, just process the default docs directory
            # In a real implementation, we would process specific file paths
            pass
        
        # Process documents
        document_chunks = process_docs(docs_path)
        
        # Add documents to RAG service (which will embed and store them)
        documents = []
        for chunk in document_chunks:
            documents.append({
                "content": chunk.content,
                "metadata": chunk.metadata
            })
        
        doc_ids = await rag_service.batch_add_documents(documents)
        
        return IngestResponse(
            status="completed",
            processed_files=len(set(chunk.metadata.get('source_file') for chunk in document_chunks)),
            processed_chunks=len(document_chunks),
            details=[
                {
                    "file": chunk.metadata.get('source_file', 'unknown'),
                    "chunks": 1,
                    "size": len(chunk.content)
                }
                for chunk in document_chunks[:5]  # Return first 5 as examples
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting documents: {str(e)}")

@router.post("/upload", response_model=IngestResponse)
async def upload_and_ingest(file: UploadFile = File(...)):
    """Upload and ingest a single document."""
    try:
        # Read the uploaded file
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Add to RAG service
        doc_id = await rag_service.add_document(
            content=content_str,
            metadata={
                "source_file": file.filename,
                "upload_time": "now",
                "file_size": len(content)
            }
        )
        
        return IngestResponse(
            status="completed",
            processed_files=1,
            processed_chunks=1,
            details=[
                {
                    "file": file.filename,
                    "chunks": 1,
                    "size": len(content_str)
                }
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing uploaded file: {str(e)}")

@router.get("/progress/{task_id}", response_model=ProgressResponse)
async def get_ingestion_progress(task_id: str):
    """Get the progress of a long-running ingestion task."""
    # In a real implementation, this would track actual background tasks
    # For now, return a mock response
    return ProgressResponse(
        status="completed",
        progress=100.0,
        details="Ingestion completed successfully"
    )

@router.get("/health")
async def ingest_health():
    """Health check for the ingestion service."""
    return {"status": "healthy", "service": "ingest"}
