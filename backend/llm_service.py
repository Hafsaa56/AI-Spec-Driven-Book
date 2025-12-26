import os
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class LLMRequest(BaseModel):
    prompt: str
    model: str = "anthropic/claude-3.5-sonnet"
    max_tokens: int = 1000
    temperature: float = 0.7
    stream: bool = False

class LLMResponse(BaseModel):
    content: str
    model: str
    tokens_used: Optional[Dict[str, int]] = None

class LLMService:
    def __init__(self):
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_base_url = "https://openrouter.ai/api/v1"
        self.default_model = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
        self._session = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()

    async def generate_response(self, prompt: str, context: str = "", model: str = None, 
                              max_tokens: int = 1000, temperature: float = 0.7) -> LLMResponse:
        """Generate a response using OpenRouter API with Claude 3.5 Sonnet."""
        if not self.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set")

        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json"
        }

        # Prepare the full prompt with context
        full_prompt = prompt
        if context:
            full_prompt = f"Context: {context}\n\nQuestion: {prompt}\n\nPlease provide a helpful answer based on the provided context."

        payload = {
            "model": model or self.default_model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant that answers questions based on provided documentation. Be concise, accurate, and cite sources when possible."
                },
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        try:
            if not self._session:
                self._session = aiohttp.ClientSession()

            async with self._session.post(f"{self.openrouter_base_url}/chat/completions", 
                                        headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"LLM API request failed with status {response.status}: {error_text}")

                data = await response.json()

                if 'choices' not in data or len(data['choices']) == 0:
                    raise Exception("No response returned from LLM API")

                content = data['choices'][0]['message']['content']
                
                # Extract token usage if available
                tokens_used = None
                if 'usage' in data:
                    tokens_used = {
                        'prompt_tokens': data['usage'].get('prompt_tokens', 0),
                        'completion_tokens': data['usage'].get('completion_tokens', 0),
                        'total_tokens': data['usage'].get('total_tokens', 0)
                    }

                return LLMResponse(
                    content=content,
                    model=data.get('model', model or self.default_model),
                    tokens_used=tokens_used
                )
        except Exception as e:
            print(f"Error generating LLM response: {str(e)}")
            raise

    async def generate_streaming_response(self, prompt: str, context: str = "", model: str = None,
                                       max_tokens: int = 1000, temperature: float = 0.7):
        """Generate a streaming response from the LLM."""
        if not self.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set")

        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json"
        }

        # Prepare the full prompt with context
        full_prompt = prompt
        if context:
            full_prompt = f"Context: {context}\n\nQuestion: {prompt}\n\nPlease provide a helpful answer based on the provided context."

        payload = {
            "model": model or self.default_model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant that answers questions based on provided documentation. Be concise, accurate, and cite sources when possible."
                },
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True
        }

        if not self._session:
            self._session = aiohttp.ClientSession()

        try:
            async with self._session.post(f"{self.openrouter_base_url}/chat/completions",
                                       headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"LLM API request failed with status {response.status}: {error_text}")

                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: ') and line != 'data: [DONE]':
                        try:
                            chunk_data = line[6:]  # Remove 'data: ' prefix
                            import json
                            chunk = json.loads(chunk_data)
                            
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"Error generating streaming LLM response: {str(e)}")
            raise

    async def check_model_availability(self, model: str) -> bool:
        """Check if a specific model is available on OpenRouter."""
        try:
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json"
            }

            async with self._session.get(f"{self.openrouter_base_url}/models", headers=headers) as response:
                if response.status != 200:
                    return False

                data = await response.json()
                available_models = [model_info['id'] for model_info in data.get('data', [])]
                return model in available_models
        except Exception:
            return False

    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get a list of available models from OpenRouter."""
        try:
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json"
            }

            async with self._session.get(f"{self.openrouter_base_url}/models", headers=headers) as response:
                if response.status != 200:
                    return []

                data = await response.json()
                return data.get('data', [])
        except Exception as e:
            print(f"Error getting available models: {str(e)}")
            return []

# Example usage function
async def test_llm_service():
    """Test the LLM service."""
    service = LLMService()
    
    # Test simple prompt
    response = await service.generate_response(
        prompt="What is the capital of France?",
        max_tokens=100,
        temperature=0.1
    )
    
    print(f"LLM Response: {response.content}")
    if response.tokens_used:
        print(f"Tokens used: {response.tokens_used}")
    
    return response

if __name__ == "__main__":
    async def main():
        try:
            response = await test_llm_service()
            print("LLM service test completed successfully")
        except Exception as e:
            print(f"Error during LLM service test: {str(e)}")

    asyncio.run(main())
