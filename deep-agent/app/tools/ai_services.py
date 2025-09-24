import asyncio
import json
import uuid
import base64
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
import aiohttp
import requests
from PIL import Image
import io
import numpy as np
from app.services.cache_service import cache_service
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class AIService(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE_AI = "google_ai"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"
    STABILITY_AI = "stability_ai"
    REPLICATE = "replicate"
    ELEVENLABS = "elevenlabs"
    WHISPER = "whisper"


class ModelType(Enum):
    TEXT_GENERATION = "text_generation"
    CHAT = "chat"
    EMBEDDING = "embedding"
    IMAGE_GENERATION = "image_generation"
    IMAGE_ANALYSIS = "image_analysis"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    AUDIO_GENERATION = "audio_generation"
    CODE_GENERATION = "code_generation"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"


class AIServiceManager:
    """Advanced AI services integration manager"""

    def __init__(self):
        self.services = {}
        self.active_sessions = {}
        self.usage_stats = {}
        self.rate_limits = {}
        self.model_configs = {}

        # Initialize services
        self._initialize_services()
        self._initialize_model_configs()

    def _initialize_services(self):
        """Initialize AI service clients"""
        if settings.OPENAI_API_KEY:
            self.services[AIService.OPENAI] = {
                "api_key": settings.OPENAI_API_KEY,
                "base_url": "https://api.openai.com/v1",
                "enabled": True
            }

        if settings.ANTHROPIC_API_KEY:
            self.services[AIService.ANTHROPIC] = {
                "api_key": settings.ANTHROPIC_API_KEY,
                "base_url": "https://api.anthropic.com",
                "enabled": True
            }

        if settings.GOOGLE_AI_API_KEY:
            self.services[AIService.GOOGLE_AI] = {
                "api_key": settings.GOOGLE_AI_API_KEY,
                "base_url": "https://generativelanguage.googleapis.com/v1",
                "enabled": True
            }

        if settings.HUGGINGFACE_API_KEY:
            self.services[AIService.HUGGINGFACE] = {
                "api_key": settings.HUGGINGFACE_API_KEY,
                "base_url": "https://api-inference.huggingface.co/models",
                "enabled": True
            }

        if settings.STABILITY_AI_API_KEY:
            self.services[AIService.STABILITY_AI] = {
                "api_key": settings.STABILITY_AI_API_KEY,
                "base_url": "https://api.stability.ai/v1",
                "enabled": True
            }

        if settings.ELEVENLABS_API_KEY:
            self.services[AIService.ELEVENLABS] = {
                "api_key": settings.ELEVENLABS_API_KEY,
                "base_url": "https://api.elevenlabs.io/v1",
                "enabled": True
            }

    def _initialize_model_configs(self):
        """Initialize model configurations"""
        self.model_configs = {
            AIService.OPENAI: {
                ModelType.TEXT_GENERATION: "gpt-3.5-turbo-instruct",
                ModelType.CHAT: "gpt-3.5-turbo",
                ModelType.EMBEDDING: "text-embedding-ada-002",
                ModelType.IMAGE_GENERATION: "dall-e-3",
                ModelType.AUDIO_TRANSCRIPTION: "whisper-1",
                ModelType.CODE_GENERATION: "gpt-3.5-turbo",
                ModelType.TRANSLATION: "gpt-3.5-turbo",
                ModelType.SUMMARIZATION: "gpt-3.5-turbo"
            },
            AIService.ANTHROPIC: {
                ModelType.CHAT: "claude-3-sonnet-20240229",
                ModelType.TEXT_GENERATION: "claude-3-sonnet-20240229"
            },
            AIService.GOOGLE_AI: {
                ModelType.CHAT: "gemini-pro",
                ModelType.TEXT_GENERATION: "gemini-pro",
                ModelType.EMBEDDING: "embedding-001"
            },
            AIService.HUGGINGFACE: {
                ModelType.TEXT_GENERATION: "gpt2",
                ModelType.IMAGE_GENERATION: "stabilityai/stable-diffusion-2-1",
                ModelType.SUMMARIZATION: "facebook/bart-large-cnn"
            },
            AIService.STABILITY_AI: {
                ModelType.IMAGE_GENERATION: "stable-diffusion-xl-1024-v1-0"
            },
            AIService.ELEVENLABS: {
                ModelType.AUDIO_GENERATION: "eleven_multilingual_v2"
            }
        }

    async def generate_text(
        self,
        prompt: str,
        service: AIService = AIService.OPENAI,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text using AI service"""
        start_time = datetime.utcnow()

        try:
            if service not in self.services or not self.services[service]["enabled"]:
                return {
                    "success": False,
                    "error": f"Service {service.value} not available",
                    "service": service.value,
                    "execution_time": (datetime.utcnow() - start_time).total_seconds()
                }

            # Use default model if not specified
            if not model:
                model = self.model_configs[service].get(ModelType.TEXT_GENERATION, "default")

            if service == AIService.OPENAI:
                result = await self._generate_text_openai(prompt, model, max_tokens, temperature, **kwargs)
            elif service == AIService.ANTHROPIC:
                result = await self._generate_text_anthropic(prompt, model, max_tokens, temperature, **kwargs)
            elif service == AIService.GOOGLE_AI:
                result = await self._generate_text_google(prompt, model, max_tokens, temperature, **kwargs)
            elif service == AIService.HUGGINGFACE:
                result = await self._generate_text_huggingface(prompt, model, max_tokens, temperature, **kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Text generation not supported for {service.value}",
                    "service": service.value,
                    "execution_time": (datetime.utcnow() - start_time).total_seconds()
                }

            # Update usage stats
            await self._update_usage_stats(service, ModelType.TEXT_GENERATION, len(result.get("text", "")))

            return {
                **result,
                "execution_time": (datetime.utcnow() - start_time).total_seconds(),
                "service": service.value,
                "model": model
            }

        except Exception as e:
            logger.error(f"Error generating text with {service.value}: {e}")
            return {
                "success": False,
                "error": str(e),
                "service": service.value,
                "execution_time": (datetime.utcnow() - start_time).total_seconds()
            }

    async def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        service: AIService = AIService.OPENAI,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate chat response using AI service"""
        start_time = datetime.utcnow()

        try:
            if service not in self.services or not self.services[service]["enabled"]:
                return {
                    "success": False,
                    "error": f"Service {service.value} not available",
                    "service": service.value,
                    "execution_time": (datetime.utcnow() - start_time).total_seconds()
                }

            # Use default model if not specified
            if not model:
                model = self.model_configs[service].get(ModelType.CHAT, "default")

            if service == AIService.OPENAI:
                result = await self._generate_chat_openai(messages, model, max_tokens, temperature, **kwargs)
            elif service == AIService.ANTHROPIC:
                result = await self._generate_chat_anthropic(messages, model, max_tokens, temperature, **kwargs)
            elif service == AIService.GOOGLE_AI:
                result = await self._generate_chat_google(messages, model, max_tokens, temperature, **kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Chat not supported for {service.value}",
                    "service": service.value,
                    "execution_time": (datetime.utcnow() - start_time).total_seconds()
                }

            # Update usage stats
            await self._update_usage_stats(service, ModelType.CHAT, len(result.get("content", "")))

            return {
                **result,
                "execution_time": (datetime.utcnow() - start_time).total_seconds(),
                "service": service.value,
                "model": model
            }

        except Exception as e:
            logger.error(f"Error generating chat response with {service.value}: {e}")
            return {
                "success": False,
                "error": str(e),
                "service": service.value,
                "execution_time": (datetime.utcnow() - start_time).total_seconds()
            }

    async def generate_image(
        self,
        prompt: str,
        service: AIService = AIService.OPENAI,
        model: Optional[str] = None,
        size: str = "1024x1024",
        style: str = "vivid",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate image using AI service"""
        start_time = datetime.utcnow()

        try:
            if service not in self.services or not self.services[service]["enabled"]:
                return {
                    "success": False,
                    "error": f"Service {service.value} not available",
                    "service": service.value,
                    "execution_time": (datetime.utcnow() - start_time).total_seconds()
                }

            # Use default model if not specified
            if not model:
                model = self.model_configs[service].get(ModelType.IMAGE_GENERATION, "default")

            if service == AIService.OPENAI:
                result = await self._generate_image_openai(prompt, model, size, style, **kwargs)
            elif service == AIService.STABILITY_AI:
                result = await self._generate_image_stability(prompt, model, size, **kwargs)
            elif service == AIService.HUGGINGFACE:
                result = await self._generate_image_huggingface(prompt, model, **kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Image generation not supported for {service.value}",
                    "service": service.value,
                    "execution_time": (datetime.utcnow() - start_time).total_seconds()
                }

            # Update usage stats
            await self._update_usage_stats(service, ModelType.IMAGE_GENERATION, len(prompt))

            return {
                **result,
                "execution_time": (datetime.utcnow() - start_time).total_seconds(),
                "service": service.value,
                "model": model
            }

        except Exception as e:
            logger.error(f"Error generating image with {service.value}: {e}")
            return {
                "success": False,
                "error": str(e),
                "service": service.value,
                "execution_time": (datetime.utcnow() - start_time).total_seconds()
            }

    async def transcribe_audio(
        self,
        audio_data: Union[str, bytes],
        service: AIService = AIService.OPENAI,
        model: Optional[str] = None,
        language: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Transcribe audio using AI service"""
        start_time = datetime.utcnow()

        try:
            if service not in self.services or not self.services[service]["enabled"]:
                return {
                    "success": False,
                    "error": f"Service {service.value} not available",
                    "service": service.value,
                    "execution_time": (datetime.utcnow() - start_time).total_seconds()
                }

            # Use default model if not specified
            if not model:
                model = self.model_configs[service].get(ModelType.AUDIO_TRANSCRIPTION, "default")

            if service == AIService.OPENAI:
                result = await self._transcribe_audio_openai(audio_data, model, language, **kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Audio transcription not supported for {service.value}",
                    "service": service.value,
                    "execution_time": (datetime.utcnow() - start_time).total_seconds()
                }

            # Update usage stats
            await self._update_usage_stats(service, ModelType.AUDIO_TRANSCRIPTION, len(result.get("text", "")))

            return {
                **result,
                "execution_time": (datetime.utcnow() - start_time).total_seconds(),
                "service": service.value,
                "model": model
            }

        except Exception as e:
            logger.error(f"Error transcribing audio with {service.value}: {e}")
            return {
                "success": False,
                "error": str(e),
                "service": service.value,
                "execution_time": (datetime.utcnow() - start_time).total_seconds()
            }

    async def generate_embeddings(
        self,
        texts: List[str],
        service: AIService = AIService.OPENAI,
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate embeddings using AI service"""
        start_time = datetime.utcnow()

        try:
            if service not in self.services or not self.services[service]["enabled"]:
                return {
                    "success": False,
                    "error": f"Service {service.value} not available",
                    "service": service.value,
                    "execution_time": (datetime.utcnow() - start_time).total_seconds()
                }

            # Use default model if not specified
            if not model:
                model = self.model_configs[service].get(ModelType.EMBEDDING, "default")

            if service == AIService.OPENAI:
                result = await self._generate_embeddings_openai(texts, model, **kwargs)
            elif service == AIService.GOOGLE_AI:
                result = await self._generate_embeddings_google(texts, model, **kwargs)
            else:
                return {
                    "success": False,
                    "error": f"Embeddings not supported for {service.value}",
                    "service": service.value,
                    "execution_time": (datetime.utcnow() - start_time).total_seconds()
                }

            # Update usage stats
            await self._update_usage_stats(service, ModelType.EMBEDDING, sum(len(text) for text in texts))

            return {
                **result,
                "execution_time": (datetime.utcnow() - start_time).total_seconds(),
                "service": service.value,
                "model": model
            }

        except Exception as e:
            logger.error(f"Error generating embeddings with {service.value}: {e}")
            return {
                "success": False,
                "error": str(e),
                "service": service.value,
                "execution_time": (datetime.utcnow() - start_time).total_seconds()
            }

    # OpenAI implementations
    async def _generate_text_openai(self, prompt: str, model: str, max_tokens: int, temperature: float, **kwargs) -> Dict[str, Any]:
        """Generate text using OpenAI"""
        headers = {
            "Authorization": f"Bearer {self.services[AIService.OPENAI]['api_key']}",
            "Content-Type": "application/json"
        }

        data = {
            "model": model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.services[AIService.OPENAI]['base_url']}/completions",
                headers=headers,
                json=data,
                timeout=30
            ) as response:
                result = await response.json()

                if "error" in result:
                    return {
                        "success": False,
                        "error": result["error"]["message"]
                    }

                return {
                    "success": True,
                    "text": result["choices"][0]["text"],
                    "usage": result.get("usage", {}),
                    "model": result.get("model", model)
                }

    async def _generate_chat_openai(self, messages: List[Dict[str, str]], model: str, max_tokens: int, temperature: float, **kwargs) -> Dict[str, Any]:
        """Generate chat response using OpenAI"""
        headers = {
            "Authorization": f"Bearer {self.services[AIService.OPENAI]['api_key']}",
            "Content-Type": "application/json"
        }

        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.services[AIService.OPENAI]['base_url']}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            ) as response:
                result = await response.json()

                if "error" in result:
                    return {
                        "success": False,
                        "error": result["error"]["message"]
                    }

                return {
                    "success": True,
                    "content": result["choices"][0]["message"]["content"],
                    "role": result["choices"][0]["message"]["role"],
                    "usage": result.get("usage", {}),
                    "model": result.get("model", model)
                }

    async def _generate_image_openai(self, prompt: str, model: str, size: str, style: str, **kwargs) -> Dict[str, Any]:
        """Generate image using OpenAI DALL-E"""
        headers = {
            "Authorization": f"Bearer {self.services[AIService.OPENAI]['api_key']}",
            "Content-Type": "application/json"
        }

        data = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "style": style,
            "n": 1,
            **kwargs
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.services[AIService.OPENAI]['base_url']}/images/generations",
                headers=headers,
                json=data,
                timeout=60
            ) as response:
                result = await response.json()

                if "error" in result:
                    return {
                        "success": False,
                        "error": result["error"]["message"]
                    }

                return {
                    "success": True,
                    "image_url": result["data"][0]["url"],
                    "revised_prompt": result["data"][0].get("revised_prompt", prompt),
                    "size": size
                }

    async def _transcribe_audio_openai(self, audio_data: Union[str, bytes], model: str, language: Optional[str], **kwargs) -> Dict[str, Any]:
        """Transcribe audio using OpenAI Whisper"""
        headers = {
            "Authorization": f"Bearer {self.services[AIService.OPENAI]['api_key']}"
        }

        data = aiohttp.FormData()
        if isinstance(audio_data, bytes):
            data.add_field('file', audio_data, filename='audio.mp3', content_type='audio/mpeg')
        else:
            data.add_field('file', open(audio_data, 'rb'), filename='audio.mp3', content_type='audio/mpeg')

        data.add_field('model', model)
        if language:
            data.add_field('language', language)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.services[AIService.OPENAI]['base_url']}/audio/transcriptions",
                headers=headers,
                data=data,
                timeout=60
            ) as response:
                result = await response.json()

                if "error" in result:
                    return {
                        "success": False,
                        "error": result["error"]["message"]
                    }

                return {
                    "success": True,
                    "text": result["text"],
                    "language": result.get("language", language)
                }

    async def _generate_embeddings_openai(self, texts: List[str], model: str, **kwargs) -> Dict[str, Any]:
        """Generate embeddings using OpenAI"""
        headers = {
            "Authorization": f"Bearer {self.services[AIService.OPENAI]['api_key']}",
            "Content-Type": "application/json"
        }

        data = {
            "model": model,
            "input": texts,
            **kwargs
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.services[AIService.OPENAI]['base_url']}/embeddings",
                headers=headers,
                json=data,
                timeout=30
            ) as response:
                result = await response.json()

                if "error" in result:
                    return {
                        "success": False,
                        "error": result["error"]["message"]
                    }

                return {
                    "success": True,
                    "embeddings": result["data"],
                    "usage": result.get("usage", {}),
                    "model": result.get("model", model)
                }

    # Anthropic implementations
    async def _generate_text_anthropic(self, prompt: str, model: str, max_tokens: int, temperature: float, **kwargs) -> Dict[str, Any]:
        """Generate text using Anthropic Claude"""
        headers = {
            "x-api-key": self.services[AIService.ANTHROPIC]['api_key'],
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

        data = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            **kwargs
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.services[AIService.ANTHROPIC]['base_url']}/messages",
                headers=headers,
                json=data,
                timeout=30
            ) as response:
                result = await response.json()

                if "error" in result:
                    return {
                        "success": False,
                        "error": result["error"]["message"]
                    }

                return {
                    "success": True,
                    "text": result["content"][0]["text"],
                    "usage": result.get("usage", {}),
                    "model": result.get("model", model)
                }

    async def _generate_chat_anthropic(self, messages: List[Dict[str, str]], model: str, max_tokens: int, temperature: float, **kwargs) -> Dict[str, Any]:
        """Generate chat response using Anthropic Claude"""
        headers = {
            "x-api-key": self.services[AIService.ANTHROPIC]['api_key'],
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

        data = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
            **kwargs
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.services[AIService.ANTHROPIC]['base_url']}/messages",
                headers=headers,
                json=data,
                timeout=30
            ) as response:
                result = await response.json()

                if "error" in result:
                    return {
                        "success": False,
                        "error": result["error"]["message"]
                    }

                return {
                    "success": True,
                    "content": result["content"][0]["text"],
                    "role": "assistant",
                    "usage": result.get("usage", {}),
                    "model": result.get("model", model)
                }

    # Google AI implementations
    async def _generate_text_google(self, prompt: str, model: str, max_tokens: int, temperature: float, **kwargs) -> Dict[str, Any]:
        """Generate text using Google AI"""
        headers = {
            "Content-Type": "application/json"
        }

        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature,
                **kwargs
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.services[AIService.GOOGLE_AI]['base_url']}/{model}:generateContent?key={self.services[AIService.GOOGLE_AI]['api_key']}",
                headers=headers,
                json=data,
                timeout=30
            ) as response:
                result = await response.json()

                if "error" in result:
                    return {
                        "success": False,
                        "error": result["error"]["message"]
                    }

                return {
                    "success": True,
                    "text": result["candidates"][0]["content"]["parts"][0]["text"],
                    "usage": result.get("usageMetadata", {}),
                    "model": model
                }

    async def _generate_chat_google(self, messages: List[Dict[str, str]], model: str, max_tokens: int, temperature: float, **kwargs) -> Dict[str, Any]:
        """Generate chat response using Google AI"""
        headers = {
            "Content-Type": "application/json"
        }

        # Convert messages to Google format
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})

        data = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature,
                **kwargs
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.services[AIService.GOOGLE_AI]['base_url']}/{model}:generateContent?key={self.services[AIService.GOOGLE_AI]['api_key']}",
                headers=headers,
                json=data,
                timeout=30
            ) as response:
                result = await response.json()

                if "error" in result:
                    return {
                        "success": False,
                        "error": result["error"]["message"]
                    }

                return {
                    "success": True,
                    "content": result["candidates"][0]["content"]["parts"][0]["text"],
                    "role": "assistant",
                    "usage": result.get("usageMetadata", {}),
                    "model": model
                }

    # HuggingFace implementations
    async def _generate_text_huggingface(self, prompt: str, model: str, max_tokens: int, temperature: float, **kwargs) -> Dict[str, Any]:
        """Generate text using HuggingFace"""
        headers = {
            "Authorization": f"Bearer {self.services[AIService.HUGGINGFACE]['api_key']}",
            "Content-Type": "application/json"
        }

        data = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                **kwargs
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.services[AIService.HUGGINGFACE]['base_url']}/{model}",
                headers=headers,
                json=data,
                timeout=30
            ) as response:
                result = await response.json()

                if isinstance(result, dict) and "error" in result:
                    return {
                        "success": False,
                        "error": result["error"]
                    }

                return {
                    "success": True,
                    "text": result[0]["generated_text"],
                    "model": model
                }

    async def _generate_image_huggingface(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
        """Generate image using HuggingFace"""
        headers = {
            "Authorization": f"Bearer {self.services[AIService.HUGGINGFACE]['api_key']}",
            "Content-Type": "application/json"
        }

        data = {
            "inputs": prompt,
            "parameters": kwargs
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.services[AIService.HUGGINGFACE]['base_url']}/{model}",
                headers=headers,
                json=data,
                timeout=60
            ) as response:
                # Image is returned as bytes
                image_bytes = await response.read()

                # Convert to base64 for storage/transmission
                image_base64 = base64.b64encode(image_bytes).decode()

                return {
                    "success": True,
                    "image_base64": image_base64,
                    "model": model
                }

    # Stability AI implementations
    async def _generate_image_stability(self, prompt: str, model: str, size: str, **kwargs) -> Dict[str, Any]:
        """Generate image using Stability AI"""
        headers = {
            "Authorization": f"Bearer {self.services[AIService.STABILITY_AI]['api_key']}",
            "Accept": "application/json"
        }

        # Parse size
        width, height = map(int, size.split('x'))

        data = {
            "text_prompts": [{"text": prompt, "weight": 1}],
            "cfg_scale": 7,
            "height": height,
            "width": width,
            "samples": 1,
            "steps": 30,
            **kwargs
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.services[AIService.STABILITY_AI]['base_url']}/generation/{model}/text-to-image",
                headers=headers,
                json=data,
                timeout=60
            ) as response:
                result = await response.json()

                if "message" in result:
                    return {
                        "success": False,
                        "error": result["message"]
                    }

                # Convert image to base64
                image_base64 = base64.b64encode(result["artifacts"][0]["base64"].encode()).decode()

                return {
                    "success": True,
                    "image_base64": image_base64,
                    "model": model,
                    "size": size
                }

    async def _update_usage_stats(self, service: AIService, model_type: ModelType, tokens_used: int):
        """Update usage statistics"""
        key = f"{service.value}_{model_type.value}"

        if key not in self.usage_stats:
            self.usage_stats[key] = {
                "requests": 0,
                "tokens": 0,
                "last_used": None
            }

        self.usage_stats[key]["requests"] += 1
        self.usage_stats[key]["tokens"] += tokens_used
        self.usage_stats[key]["last_used"] = datetime.utcnow().isoformat()

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            "usage_stats": self.usage_stats,
            "available_services": list(self.services.keys()),
            "model_configs": {service.value: configs for service, configs in self.model_configs.items()}
        }

    def get_available_services(self) -> List[Dict[str, Any]]:
        """Get list of available AI services"""
        services_info = []
        for service, config in self.services.items():
            services_info.append({
                "name": service.value,
                "enabled": config["enabled"],
                "models": self.model_configs.get(service, {})
            })
        return services_info


# Global instance
ai_service_manager = AIServiceManager()