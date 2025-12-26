import asyncio
from typing import List, Dict, Any
from pydantic import BaseModel
from embedding_service import QwenEmbeddingService
from vector_db import VectorDB
from llm_service import LLMService

class RAGRequest(BaseModel):
    query: str
    session_id: str = None
    max_context_chunks: int = 5
    temperature: float = 0.7

class RAGResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    context_used: str
    tokens_used: Dict[str, int] = None

class RAGService:
    def __init__(self):
        self.embedding_service = QwenEmbeddingService()
        self.vector_db = VectorDB()
        self.llm_service = LLMService()
        self.max_context_length = 3000  # Max characters for context

    async def retrieve_context(self, query: str, max_chunks: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant context from the vector database based on the query."""
        try:
            # Generate embedding for the query
            print(f"Generating embedding for query: {query[:50]}...")
            query_embedding = await self.embedding_service.get_embedding(query)
            print(f"Generated embedding with {len(query_embedding)} dimensions")

            # Search for similar documents in the vector database
            print(f"Searching for similar documents with limit {max_chunks}")
            search_results = self.vector_db.search_similar(
                query_embedding=query_embedding,
                limit=max_chunks
            )
            print(f"Found {len(search_results)} results")

            return search_results
        except Exception as e:
            print(f"Error in retrieve_context: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return []

    async def generate_answer(self, query: str, context: str = "", session_id: str = None) -> RAGResponse:
        """Generate an answer based on the query and context."""
        # Use the LLM service to generate a response
        llm_response = await self.llm_service.generate_response(
            prompt=query,
            context=context,
            max_tokens=1000,
            temperature=0.7
        )
        
        # Return the RAG response with sources
        return RAGResponse(
            answer=llm_response.content,
            sources=[],
            context_used=context,
            tokens_used=llm_response.tokens_used
        )

    async def query(self, query: str, session_id: str = None, max_context_chunks: int = 5) -> RAGResponse:
        """Main RAG query method that retrieves context and generates an answer."""
        # Retrieve relevant context from the vector database
        context_results = await self.retrieve_context(query, max_context_chunks)
        
        # Combine the context from all results
        combined_context = ""
        sources = []
        
        for result in context_results:
            content = result.get("content", "")
            metadata = result.get("metadata", {})
            
            # Add to combined context
            if len(combined_context + content) <= self.max_context_length:
                combined_context += f"\n\n{content}"
                sources.append({
                    "id": result.get("id"),
                    "score": result.get("score"),
                    "metadata": metadata
                })
            else:
                # If adding this chunk would exceed the limit, stop adding
                break
        
        # Generate answer using the context
        response = await self.generate_answer(query, combined_context, session_id)
        
        # Update sources with the ones we actually used
        response.sources = sources
        response.context_used = combined_context
        
        return response

    async def query_with_sources(self, query: str, session_id: str = None, max_context_chunks: int = 5) -> RAGResponse:
        """Query method that includes source attribution."""
        # Retrieve relevant context from the vector database
        context_results = await self.retrieve_context(query, max_context_chunks)
        
        # Combine the context from all results
        combined_context = ""
        sources = []
        
        for result in context_results:
            content = result.get("content", "")
            metadata = result.get("metadata", {})
            
            # Add to combined context
            if len(combined_context + content) <= self.max_context_length:
                combined_context += f"\n\n{content}"
                sources.append({
                    "id": result.get("id"),
                    "score": result.get("score"),
                    "metadata": metadata,
                    "content_preview": content[:200] + "..." if len(content) > 200 else content
                })
            else:
                # If adding this chunk would exceed the limit, stop adding
                break
        
        # Create a detailed prompt with source information
        detailed_prompt = f"Based on the following documentation, please answer the question. If you use information from the documentation, please cite the source.\n\nDocumentation:\n{combined_context}\n\nQuestion: {query}\n\nAnswer:"
        
        # Generate response with source attribution
        llm_response = await self.llm_service.generate_response(
            prompt=detailed_prompt,
            max_tokens=1000,
            temperature=0.7
        )
        
        return RAGResponse(
            answer=llm_response.content,
            sources=sources,
            context_used=combined_context,
            tokens_used=llm_response.tokens_used
        )

    async def add_document(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """Add a document to the vector database."""
        # Generate embedding for the content
        embedding = await self.embedding_service.get_embedding(content)
        
        # Upsert to vector database
        doc_id = self.vector_db.upsert_document(
            content=content,
            embedding=embedding,
            metadata=metadata or {}
        )
        
        return doc_id

    async def batch_add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Add multiple documents to the vector database."""
        # Prepare chunks for batch upsert
        chunks = []
        for doc in documents:
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            embedding = await self.embedding_service.get_embedding(content)
            chunks.append((content, embedding, metadata))
        
        # Batch upsert to vector database
        doc_ids = self.vector_db.upsert_documents(chunks)
        
        return doc_ids

# Example usage function
async def test_rag_service():
    """Test the RAG service."""
    rag_service = RAGService()
    
    # Add a test document
    test_doc = {
        "content": "The RAG (Retrieval-Augmented Generation) model is a type of neural network architecture that combines the retrieval of relevant documents with the generation of responses. This approach allows language models to access external knowledge sources during the generation process, improving the accuracy and factualness of their outputs.",
        "metadata": {
            "source": "test_documentation",
            "type": "technical_explanation",
            "topic": "RAG_models"
        }
    }
    
    doc_id = await rag_service.add_document(test_doc["content"], test_doc["metadata"])
    print(f"Added document with ID: {doc_id}")
    
    # Query the RAG service
    response = await rag_service.query_with_sources(
        query="What is a RAG model?",
        max_context_chunks=3
    )
    
    print(f"RAG Answer: {response.answer}")
    print(f"Sources: {len(response.sources)}")
    if response.sources:
        print(f"First source preview: {response.sources[0]['content_preview'][:100]}...")
    
    return response

if __name__ == "__main__":
    async def main():
        try:
            response = await test_rag_service()
            print("RAG service test completed successfully")
        except Exception as e:
            print(f"Error during RAG service test: {str(e)}")

    asyncio.run(main())
