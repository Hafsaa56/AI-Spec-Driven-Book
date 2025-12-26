import os
import uuid
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class DocumentChunk(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any]

class VectorDB:
    def __init__(self):
        # Initialize Qdrant client
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        
        if qdrant_url:
            self.client = QdrantClient(
                url=qdrant_url,
                api_key=qdrant_api_key,
                timeout=10
            )
        else:
            # For development, you can use in-memory storage
            self.client = QdrantClient(":memory:")
        
        self.collection_name = "documentation_chunks"
        self.vector_size = 1536  # Default size for text-embedding-3-small
        self.distance = Distance.COSINE
        
        # Initialize the collection
        self._init_collection()

    def _init_collection(self):
        """Initialize the Qdrant collection if it doesn't exist."""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                # Create collection with specified vector parameters
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=self.distance
                    )
                )
                print(f"Created collection: {self.collection_name}")
            else:
                print(f"Collection {self.collection_name} already exists")
        except Exception as e:
            print(f"Error initializing collection: {str(e)}")
            # In case of error with remote Qdrant, try in-memory
            self.client = QdrantClient(":memory:")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=self.distance
                )
            )
            print("Initialized in-memory Qdrant collection")

    def upsert_document(self, content: str, embedding: List[float], metadata: Dict[str, Any] = None) -> str:
        """Upsert a document chunk with its embedding to the vector database."""
        if metadata is None:
            metadata = {}
        
        # Generate a unique ID for the document
        doc_id = str(uuid.uuid4())
        
        # Prepare the point for Qdrant
        points = [
            models.PointStruct(
                id=doc_id,
                vector=embedding,
                payload={
                    "content": content,
                    "metadata": metadata
                }
            )
        ]
        
        # Upsert the point to the collection
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        return doc_id

    def upsert_documents(self, chunks: List[tuple]) -> List[str]:
        """Upsert multiple document chunks at once.
        
        Args:
            chunks: List of tuples (content, embedding, metadata)
        Returns:
            List of document IDs
        """
        doc_ids = []
        points = []
        
        for content, embedding, metadata in chunks:
            doc_id = str(uuid.uuid4())
            doc_ids.append(doc_id)
            
            points.append(
                models.PointStruct(
                    id=doc_id,
                    vector=embedding,
                    payload={
                        "content": content,
                        "metadata": metadata or {}
                    }
                )
            )
        
        # Upsert all points in a single operation
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        return doc_ids

    def search_similar(self, query_embedding: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents based on the query embedding."""
        try:
            # Check what type of client we're dealing with
            print(f"Qdrant client type: {type(self.client)}")

            # List all available methods to see what's available
            available_methods = [method for method in dir(self.client) if not method.startswith('_')]
            print(f"Some available methods: {available_methods[:10]}")  # Show first 10 methods

            # For Qdrant client, the correct method should be search
            # But let's handle the case where it might not exist
            if not hasattr(self.client, 'search'):
                print("Qdrant client doesn't have 'search' method, trying alternative approaches")
                return []

            try:
                # Try the search method with correct parameters
                results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_embedding,
                    limit=limit
                )
            except TypeError as e:
                print(f"Search method signature issue: {str(e)}")
                try:
                    # Try with different parameter name
                    results = self.client.search(
                        collection_name=self.collection_name,
                        query_vector=query_embedding,
                        limit=limit,
                        with_payload=True
                    )
                except:
                    print("All search attempts failed")
                    return []
            except Exception as e:
                print(f"Qdrant search failed: {str(e)}")
                return []
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.id,
                    "content": result.payload.get("content", ""),
                    "metadata": result.payload.get("metadata", {}),
                    "score": result.score
                })
            
            return formatted_results
        except Exception as e:
            print(f"Error searching for similar documents: {str(e)}")
            return []

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by its ID."""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=[doc_id]
                )
            )
            return True
        except Exception as e:
            print(f"Error deleting document {doc_id}: {str(e)}")
            return False

    def get_document_count(self) -> int:
        """Get the total number of documents in the collection."""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return collection_info.points_count
        except Exception as e:
            print(f"Error getting document count: {str(e)}")
            return 0

    def clear_collection(self) -> bool:
        """Clear all documents from the collection."""
        try:
            # Delete and recreate the collection to clear all points
            self.client.delete_collection(self.collection_name)
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=self.distance
                )
            )
            return True
        except Exception as e:
            print(f"Error clearing collection: {str(e)}")
            return False

    def update_document(self, doc_id: str, content: str = None, embedding: List[float] = None, metadata: Dict[str, Any] = None):
        """Update an existing document."""
        # First, get the current document
        current_docs = self.client.retrieve(
            collection_name=self.collection_name,
            ids=[doc_id]
        )
        
        if not current_docs:
            raise ValueError(f"Document with ID {doc_id} not found")
        
        current_doc = current_docs[0]
        updated_payload = current_doc.payload
        
        # Update fields if provided
        if content is not None:
            updated_payload["content"] = content
        if metadata is not None:
            updated_payload["metadata"] = metadata
        
        # Prepare the updated point
        updated_point = models.PointStruct(
            id=doc_id,
            vector=embedding if embedding is not None else current_doc.vector,
            payload=updated_payload
        )
        
        # Upsert the updated point
        self.client.upsert(
            collection_name=self.collection_name,
            points=[updated_point]
        )

# Example usage
async def test_vector_db():
    """Test the vector database functionality."""
    from embedding_service import QwenEmbeddingService
    
    # Initialize vector DB
    vector_db = VectorDB()
    
    # Test embedding service
    embedding_service = QwenEmbeddingService()
    test_content = "This is a test document for the RAG chatbot system."
    test_embedding = await embedding_service.get_embedding(test_content)
    
    # Add a test document
    metadata = {
        "source": "test",
        "type": "test_document",
        "created_at": "2025-01-01"
    }
    
    doc_id = vector_db.upsert_document(
        content=test_content,
        embedding=test_embedding,
        metadata=metadata
    )
    
    print(f"Upserted document with ID: {doc_id}")
    print(f"Total documents in DB: {vector_db.get_document_count()}")
    
    # Search for similar content
    search_results = vector_db.search_similar(test_embedding, limit=1)
    print(f"Search results: {len(search_results)}")
    
    if search_results:
        result = search_results[0]
        print(f"Found content: {result['content'][:50]}...")
        print(f"Score: {result['score']}")
    
    return vector_db

if __name__ == "__main__":
    import asyncio
    
    async def main():
        try:
            db = await test_vector_db()
            print("Vector DB test completed successfully")
        except Exception as e:
            print(f"Error during vector DB test: {str(e)}")

    asyncio.run(main())
