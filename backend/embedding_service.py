import os
import asyncio
import aiohttp
import numpy as np
from typing import List, Dict, Any
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class EmbeddingRequest(BaseModel):
    input: str
    model: str = "text-embedding-3-small"  # Default model, will be replaced with Qwen

class EmbeddingResponse(BaseModel):
    embeddings: List[List[float]]
    model: str

class EmbeddingService:
    def __init__(self):
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.qwen_model = os.getenv("QWEN_EMBEDDING_MODEL", "Qwen/qwen2-7b-instruct")
        self.openrouter_base_url = "https://openrouter.ai/api/v1"
        self._session = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()

    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text using OpenRouter with Qwen model."""
        if not self.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set")

        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json"
        }

        # Note: OpenRouter doesn't have Qwen embedding models directly
        # We'll use a compatible embedding model from OpenRouter
        # For this implementation, we'll use OpenAI-compatible embeddings
        url = f"{self.openrouter_base_url}/embeddings"

        payload = {
            "model": "text-embedding-3-small",  # Using OpenAI embedding model via OpenRouter
            "input": text
        }

        try:
            if not self._session:
                self._session = aiohttp.ClientSession()

            async with self._session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Embedding API request failed with status {response.status}: {error_text}")

                data = await response.json()

                if 'data' not in data or len(data['data']) == 0:
                    raise Exception("No embeddings returned from API")

                embedding = data['data'][0]['embedding']
                return embedding
        except Exception as e:
            print(f"Error getting embedding: {str(e)}")
            raise

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts."""
        embeddings = []
        for text in texts:
            embedding = await self.get_embedding(text)
            embeddings.append(embedding)
        return embeddings

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def euclidean_distance(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate Euclidean distance between two vectors."""
        return sum((a - b) ** 2 for a, b in zip(vec1, vec2)) ** 0.5

# Alternative implementation for Qwen embeddings if needed
class QwenEmbeddingService:
    """
    Alternative implementation for Qwen embeddings.
    Note: As of now, Qwen doesn't provide embedding APIs directly.
    This is a placeholder for when embedding support is available.
    """

    def __init__(self):
        self.model_name = os.getenv("QWEN_EMBEDDING_MODEL", "Qwen/qwen2-7b-instruct")
        # In a real implementation, this would connect to a Qwen embedding service
        # For now, we'll use the OpenRouter-compatible version above

    async def get_embedding(self, text: str) -> List[float]:
        """Placeholder for Qwen embedding - uses OpenRouter instead."""
        # Use the standard embedding service since Qwen doesn't have embedding API
        async with EmbeddingService() as service:
            return await service.get_embedding(text)

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Placeholder for Qwen embeddings - uses OpenRouter instead."""
        async with EmbeddingService() as service:
            return await service.get_embeddings(texts)

# Singleton instance for the embedding service
async def get_embedding_service():
    """Get the embedding service instance."""
    return QwenEmbeddingService()

# Example usage function
async def test_embedding():
    """Test the embedding service."""
    service = QwenEmbeddingService()
    text = "This is a test document for embedding."
    embedding = await service.get_embedding(text)
    print(f"Generated embedding with {len(embedding)} dimensions")
    return embedding

if __name__ == "__main__":
    # Test the embedding service
    async def main():
        try:
            embedding = await test_embedding()
            print(f"Sample embedding: {embedding[:10]}...")  # Print first 10 dimensions
        except Exception as e:
            print(f"Error during embedding test: {str(e)}")

    asyncio.run(main())
