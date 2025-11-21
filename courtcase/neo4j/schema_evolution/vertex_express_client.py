"""
Custom Vertex AI Express client for use with API keys
"""
import requests
import json
from typing import List, Dict, Any
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult


class VertexAIExpressChat(BaseChatModel):
    """Custom LangChain-compatible client for Vertex AI Express API"""

    api_key: str
    model: str = "gemini-2.5-pro"
    temperature: float = 0.7
    max_tokens: int = 8192

    @property
    def _llm_type(self) -> str:
        return "vertex-ai-express"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: List[str] | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate response from Vertex AI Express API"""

        # Convert messages to Vertex AI format
        contents = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = "user"
            elif isinstance(msg, AIMessage):
                role = "model"
            elif isinstance(msg, SystemMessage):
                # Vertex AI doesn't have system role, add as user message
                role = "user"
            else:
                role = "user"

            contents.append({
                "role": role,
                "parts": [{"text": msg.content}]
            })

        # Prepare request
        url = f"https://aiplatform.googleapis.com/v1/publishers/google/models/{self.model}:generateContent"
        headers = {
            "Content-Type": "application/json"
        }
        params = {
            "key": self.api_key
        }

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": self.max_tokens,
            }
        }

        # Make request
        try:
            response = requests.post(
                url,
                params=params,
                headers=headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()

            result = response.json()

            # Extract text from response
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    text = candidate["content"]["parts"][0].get("text", "")
                else:
                    text = ""
            else:
                text = ""

            # Create ChatResult
            message = AIMessage(content=text)
            generation = ChatGeneration(message=message)

            return ChatResult(generations=[generation])

        except requests.exceptions.RequestException as e:
            raise ValueError(f"Vertex AI Express API error: {str(e)}")
