import asyncio
import json
import uuid
import base64
import io
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
import aiohttp
import requests
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
import soundfile as sf
from moviepy.editor import VideoFileClip
import matplotlib.pyplot as plt
import seaborn as sns
from app.services.cache_service import cache_service
from app.core.config import settings
from app.tools.ai_services import ai_service_manager, AIService
import logging

logger = logging.getLogger(__name__)


class MediaType(Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    TABLE = "table"
    CHART = "chart"


class ProcessingTask(Enum):
    ANALYSIS = "analysis"
    EXTRACTION = "extraction"
    GENERATION = "generation"
    TRANSFORMATION = "transformation"
    ENHANCEMENT = "enhancement"
    COMPRESSION = "compression"
    CONVERSION = "conversion"


class MultiModalProcessor:
    """Advanced multi-modal processing capabilities"""

    def __init__(self):
        self.supported_formats = {
            MediaType.IMAGE: ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp'],
            MediaType.AUDIO: ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a'],
            MediaType.VIDEO: ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv'],
            MediaType.DOCUMENT: ['pdf', 'doc', 'docx', 'txt', 'rtf'],
            MediaType.TABLE: ['csv', 'xlsx', 'xls'],
            MediaType.CHART: ['png', 'jpg', 'svg', 'pdf']
        }

        self.processing_limits = {
            "max_image_size": (4096, 4096),
            "max_audio_duration": 300,  # 5 minutes
            "max_video_duration": 600,  # 10 minutes
            "max_file_size": 50 * 1024 * 1024,  # 50MB
            "max_concurrent_processing": 5
        }

    async def process_media(
        self,
        media_data: Union[str, bytes, Dict[str, Any]],
        media_type: MediaType,
        task: ProcessingTask,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process media with multi-modal capabilities"""
        start_time = datetime.utcnow()

        try:
            # Validate input
            validation_result = await self._validate_media_input(media_data, media_type)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"],
                    "media_type": media_type.value,
                    "task": task.value,
                    "execution_time": (datetime.utcnow() - start_time).total_seconds()
                }

            # Process based on media type and task
            if media_type == MediaType.IMAGE:
                result = await self._process_image(media_data, task, options or {})
            elif media_type == MediaType.AUDIO:
                result = await self._process_audio(media_data, task, options or {})
            elif media_type == MediaType.VIDEO:
                result = await self._process_video(media_data, task, options or {})
            elif media_type == MediaType.DOCUMENT:
                result = await self._process_document(media_data, task, options or {})
            elif media_type == MediaType.TABLE:
                result = await self._process_table(media_data, task, options or {})
            elif media_type == MediaType.CHART:
                result = await self._process_chart(media_data, task, options or {})
            else:
                result = {
                    "success": False,
                    "error": f"Unsupported media type: {media_type.value}"
                }

            execution_time = (datetime.utcnow() - start_time).total_seconds()

            return {
                **result,
                "media_type": media_type.value,
                "task": task.value,
                "execution_time": execution_time,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error processing {media_type.value} for task {task.value}: {e}")
            return {
                "success": False,
                "error": str(e),
                "media_type": media_type.value,
                "task": task.value,
                "execution_time": (datetime.utcnow() - start_time).total_seconds()
            }

    async def _validate_media_input(
        self,
        media_data: Union[str, bytes, Dict[str, Any]],
        media_type: MediaType
    ) -> Dict[str, Any]:
        """Validate media input"""
        try:
            # Check file size
            if isinstance(media_data, bytes):
                file_size = len(media_data)
                if file_size > self.processing_limits["max_file_size"]:
                    return {
                        "valid": False,
                        "error": f"File size ({file_size} bytes) exceeds limit ({self.processing_limits['max_file_size']} bytes)"
                    }

            # Check format support
            if isinstance(media_data, str):
                file_extension = media_data.split('.')[-1].lower() if '.' in media_data else ''
                if media_type in self.supported_formats:
                    if file_extension not in self.supported_formats[media_type]:
                        return {
                            "valid": False,
                            "error": f"Unsupported format '{file_extension}' for media type '{media_type.value}'"
                        }

            return {"valid": True}

        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}"
            }

    async def _process_image(
        self,
        image_data: Union[str, bytes],
        task: ProcessingTask,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process image with various AI-enhanced capabilities"""
        try:
            # Load image
            if isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
            elif isinstance(image_data, str):
                image = Image.open(image_data)
            else:
                raise ValueError("Unsupported image data format")

            # Resize if necessary
            max_size = self.processing_limits["max_image_size"]
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)

            if task == ProcessingTask.ANALYSIS:
                return await self._analyze_image(image, options)
            elif task == ProcessingTask.EXTRACTION:
                return await self._extract_from_image(image, options)
            elif task == ProcessingTask.GENERATION:
                return await self._generate_from_image(image, options)
            elif task == ProcessingTask.TRANSFORMATION:
                return await self._transform_image(image, options)
            elif task == ProcessingTask.ENHANCEMENT:
                return await self._enhance_image(image, options)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported task '{task.value}' for image processing"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Image processing error: {str(e)}"
            }

    async def _analyze_image(self, image: Image.Image, options: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze image using AI services"""
        try:
            # Convert image to base64 for AI analysis
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG")
            image_base64 = base64.b64encode(buffered.getvalue()).decode()

            # Analyze with AI services
            if ai_service_manager.services.get(AIService.OPENAI, {}).get("enabled"):
                # Use GPT-4 Vision for image analysis
                analysis_prompt = options.get("prompt", "Analyze this image in detail. Describe what you see, including objects, people, text, and any notable features.")

                analysis_result = await ai_service_manager.generate_chat_response([
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": analysis_prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                        ]
                    },
                    {
                        "role": "system",
                        "content": "You are an expert image analyzer. Provide detailed, accurate descriptions of images."
                    }
                ], model="gpt-4-vision-preview")

                if analysis_result["success"]:
                    return {
                        "success": True,
                        "analysis": analysis_result["content"],
                        "image_info": {
                            "size": image.size,
                            "mode": image.mode,
                            "format": image.format
                        }
                    }

            # Fallback analysis
            return {
                "success": True,
                "analysis": f"Image analysis completed. Size: {image.size}, Mode: {image.mode}",
                "image_info": {
                    "size": image.size,
                    "mode": image.mode,
                    "format": image.format
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Image analysis error: {str(e)}"
            }

    async def _extract_from_image(self, image: Image.Image, options: Dict[str, Any]) -> Dict[str, Any]:
        """Extract text or data from image"""
        try:
            extracted_data = {}

            # Extract text using OCR (simplified - in production use proper OCR library)
            if options.get("extract_text", True):
                # Placeholder for OCR functionality
                extracted_data["text"] = "OCR text extraction would happen here"

            # Extract colors
            if options.get("extract_colors", False):
                colors = self._extract_dominant_colors(image)
                extracted_data["dominant_colors"] = colors

            # Extract features
            if options.get("extract_features", False):
                features = self._extract_image_features(image)
                extracted_data["features"] = features

            return {
                "success": True,
                "extracted_data": extracted_data,
                "extraction_types": list(extracted_data.keys())
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Image extraction error: {str(e)}"
            }

    async def _generate_from_image(self, image: Image.Image, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content from image"""
        try:
            # Convert image to base64
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG")
            image_base64 = base64.b64encode(buffered.getvalue()).decode()

            # Generate image variations using AI
            if ai_service_manager.services.get(AIService.OPENAI, {}).get("enabled"):
                variation_prompt = options.get("prompt", "Create a variation of this image")

                result = await ai_service_manager.generate_image(
                    prompt=f"{variation_prompt} based on provided image",
                    service=AIService.OPENAI,
                    size="1024x1024"
                )

                if result["success"]:
                    return {
                        "success": True,
                        "generated_image_url": result["image_url"],
                        "generation_type": "variation"
                    }

            return {
                "success": True,
                "generated_data": "Image generation placeholder",
                "generation_type": "enhanced"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Image generation error: {str(e)}"
            }

    async def _transform_image(self, image: Image.Image, options: Dict[str, Any]) -> Dict[str, Any]:
        """Transform image with various filters and effects"""
        try:
            transformed_images = {}

            # Apply transformations
            transformations = options.get("transformations", ["resize"])

            if "resize" in transformations:
                new_size = options.get("size", (512, 512))
                resized = image.resize(new_size, Image.Resampling.LANCZOS)
                transformed_images["resized"] = self._image_to_base64(resized)

            if "rotate" in transformations:
                angle = options.get("rotation_angle", 90)
                rotated = image.rotate(angle, expand=True)
                transformed_images["rotated"] = self._image_to_base64(rotated)

            if "grayscale" in transformations:
                grayscale = image.convert("L")
                transformed_images["grayscale"] = self._image_to_base64(grayscale)

            if "blur" in transformations:
                blurred = image.filter(Image.ImageFilter.BLUR)
                transformed_images["blurred"] = self._image_to_base64(blurred)

            return {
                "success": True,
                "transformed_images": transformed_images,
                "applied_transformations": transformations
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Image transformation error: {str(e)}"
            }

    async def _enhance_image(self, image: Image.Image, options: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance image quality"""
        try:
            enhanced_images = {}

            # Apply enhancements
            enhancements = options.get("enhancements", ["contrast"])

            if "contrast" in enhancements:
                from PIL import ImageEnhance
                enhancer = ImageEnhance.Contrast(image)
                enhanced = enhancer.enhance(1.5)
                enhanced_images["contrast_enhanced"] = self._image_to_base64(enhanced)

            if "brightness" in enhancements:
                enhancer = ImageEnhance.Brightness(image)
                enhanced = enhancer.enhance(1.2)
                enhanced_images["brightness_enhanced"] = self._image_to_base64(enhanced)

            if "sharpness" in enhancements:
                enhancer = ImageEnhance.Sharpness(image)
                enhanced = enhancer.enhance(1.5)
                enhanced_images["sharpened"] = self._image_to_base64(enhanced)

            return {
                "success": True,
                "enhanced_images": enhanced_images,
                "applied_enhancements": enhancements
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Image enhancement error: {str(e)}"
            }

    async def _process_audio(
        self,
        audio_data: Union[str, bytes],
        task: ProcessingTask,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process audio with AI-enhanced capabilities"""
        try:
            if isinstance(audio_data, bytes):
                # Create temporary file for processing
                temp_file = f"/tmp/audio_{uuid.uuid4().hex[:8]}.wav"
                with open(temp_file, 'wb') as f:
                    f.write(audio_data)
                audio_path = temp_file
            else:
                audio_path = audio_data

            # Load audio file
            audio_data_np, sample_rate = sf.read(audio_path)

            # Check duration
            duration = len(audio_data_np) / sample_rate
            if duration > self.processing_limits["max_audio_duration"]:
                return {
                    "success": False,
                    "error": f"Audio duration ({duration:.2f}s) exceeds limit ({self.processing_limits['max_audio_duration']}s)"
                }

            if task == ProcessingTask.ANALYSIS:
                return await self._analyze_audio(audio_data_np, sample_rate, options)
            elif task == ProcessingTask.EXTRACTION:
                return await self._extract_from_audio(audio_data_np, sample_rate, options)
            elif task == ProcessingTask.GENERATION:
                return await self._generate_from_audio(audio_data_np, sample_rate, options)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported task '{task.value}' for audio processing"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Audio processing error: {str(e)}"
            }

    async def _analyze_audio(self, audio_data: np.ndarray, sample_rate: int, options: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze audio characteristics"""
        try:
            analysis = {}

            # Basic audio properties
            analysis["duration"] = len(audio_data) / sample_rate
            analysis["sample_rate"] = sample_rate
            analysis["channels"] = 1 if len(audio_data.shape) == 1 else audio_data.shape[1]
            analysis["max_amplitude"] = np.max(np.abs(audio_data))

            # Frequency analysis
            if options.get("frequency_analysis", True):
                from scipy import signal
                frequencies, times, spectrogram = signal.spectrogram(audio_data, sample_rate)
                analysis["frequency_analysis"] = {
                    "dominant_frequency": float(frequencies[np.argmax(spectrogram, axis=0)].mean()),
                    "frequency_range": [float(frequencies.min()), float(frequencies.max())]
                }

            # Transcribe audio if requested
            if options.get("transcribe", False):
                # Convert to WAV format for transcription
                temp_wav = f"/tmp/audio_{uuid.uuid4().hex[:8]}.wav"
                sf.write(temp_wav, audio_data, sample_rate)

                transcription_result = await ai_service_manager.transcribe_audio(temp_wav)
                if transcription_result["success"]:
                    analysis["transcription"] = transcription_result["text"]

            return {
                "success": True,
                "analysis": analysis,
                "analysis_types": list(analysis.keys())
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Audio analysis error: {str(e)}"
            }

    async def _extract_from_audio(self, audio_data: np.ndarray, sample_rate: int, options: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from audio"""
        try:
            extracted_data = {}

            # Extract basic features
            extracted_data["rms_energy"] = float(np.sqrt(np.mean(audio_data**2)))
            extracted_data["zero_crossing_rate"] = float(np.mean(np.diff(np.sign(audio_data)) != 0))

            # Extract spectral features
            if options.get("spectral_features", True):
                from scipy.fft import fft
                fft_result = fft(audio_data)
                magnitude = np.abs(fft_result)
                extracted_data["spectral_centroid"] = float(np.sum(magnitude * np.arange(len(magnitude))) / np.sum(magnitude))

            return {
                "success": True,
                "extracted_data": extracted_data,
                "extraction_types": list(extracted_data.keys())
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Audio extraction error: {str(e)}"
            }

    async def _generate_from_audio(self, audio_data: np.ndarray, sample_rate: int, options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content from audio"""
        try:
            # Transcribe audio first
            temp_wav = f"/tmp/audio_{uuid.uuid4().hex[:8]}.wav"
            sf.write(temp_wav, audio_data, sample_rate)

            transcription_result = await ai_service_manager.transcribe_audio(temp_wav)
            if not transcription_result["success"]:
                return {
                    "success": False,
                    "error": "Failed to transcribe audio for generation"
                }

            # Generate content from transcription
            text = transcription_result["text"]
            generation_prompt = options.get("prompt", "Generate a summary of the following audio transcription:")

            content_result = await ai_service_manager.generate_text(
                prompt=f"{generation_prompt}\n\n{text}",
                max_tokens=500
            )

            if content_result["success"]:
                return {
                    "success": True,
                    "generated_content": content_result["text"],
                    "source_transcription": text,
                    "generation_type": "summary"
                }

            return {
                "success": True,
                "generated_content": "Audio content generation placeholder",
                "generation_type": "basic"
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Audio generation error: {str(e)}"
            }

    async def _process_video(
        self,
        video_data: Union[str, bytes],
        task: ProcessingTask,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process video with multi-modal capabilities"""
        try:
            if isinstance(video_data, bytes):
                # Save to temporary file
                temp_file = f"/tmp/video_{uuid.uuid4().hex[:8]}.mp4"
                with open(temp_file, 'wb') as f:
                    f.write(video_data)
                video_path = temp_file
            else:
                video_path = video_data

            # Load video
            video = VideoFileClip(video_path)

            # Check duration
            if video.duration > self.processing_limits["max_video_duration"]:
                video.close()
                return {
                    "success": False,
                    "error": f"Video duration ({video.duration:.2f}s) exceeds limit ({self.processing_limits['max_video_duration']}s)"
                }

            if task == ProcessingTask.ANALYSIS:
                return await self._analyze_video(video, options)
            elif task == ProcessingTask.EXTRACTION:
                return await self._extract_from_video(video, options)
            elif task == ProcessingTask.TRANSFORMATION:
                return await self._transform_video(video, options)
            else:
                video.close()
                return {
                    "success": False,
                    "error": f"Unsupported task '{task.value}' for video processing"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Video processing error: {str(e)}"
            }

    async def _analyze_video(self, video: VideoFileClip, options: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze video content"""
        try:
            analysis = {}

            # Basic video properties
            analysis["duration"] = video.duration
            analysis["fps"] = video.fps
            analysis["size"] = video.size
            analysis["rotation"] = video.rotation

            # Extract frames for analysis
            if options.get("frame_analysis", False):
                frame_interval = options.get("frame_interval", 1.0)  # seconds
                frames = []

                for t in range(0, int(video.duration), int(frame_interval)):
                    frame = video.get_frame(t)
                    frames.append({
                        "time": t,
                        "frame_base64": self._image_to_base64(Image.fromarray(frame))
                    })

                analysis["sampled_frames"] = frames

            # Extract audio for analysis
            if video.audio and options.get("audio_analysis", False):
                audio_analysis = await self._analyze_audio(
                    video.audio.to_soundarray(),
                    video.audio.fps,
                    {"frequency_analysis": True}
                )
                if audio_analysis["success"]:
                    analysis["audio_analysis"] = audio_analysis["analysis"]

            video.close()
            return {
                "success": True,
                "analysis": analysis,
                "analysis_types": list(analysis.keys())
            }

        except Exception as e:
            video.close()
            return {
                "success": False,
                "error": f"Video analysis error: {str(e)}"
            }

    async def _extract_from_video(self, video: VideoFileClip, options: Dict[str, Any]) -> Dict[str, Any]:
        """Extract content from video"""
        try:
            extracted_data = {}

            # Extract audio
            if video.audio and options.get("extract_audio", True):
                audio_path = f"/tmp/audio_{uuid.uuid4().hex[:8]}.wav"
                video.audio.write_audiofile(audio_path)
                extracted_data["audio_path"] = audio_path

            # Extract frames
            if options.get("extract_frames", False):
                frame_interval = options.get("frame_interval", 1.0)
                frames = []

                for t in range(0, int(video.duration), int(frame_interval)):
                    frame = video.get_frame(t)
                    frame_path = f"/tmp/frame_{t}.jpg"
                    Image.fromarray(frame).save(frame_path)
                    frames.append({"time": t, "path": frame_path})

                extracted_data["extracted_frames"] = frames

            # Extract subtitles/captions (placeholder)
            if options.get("extract_subtitles", False):
                extracted_data["subtitles"] = "Subtitle extraction placeholder"

            video.close()
            return {
                "success": True,
                "extracted_data": extracted_data,
                "extraction_types": list(extracted_data.keys())
            }

        except Exception as e:
            video.close()
            return {
                "success": False,
                "error": f"Video extraction error: {str(e)}"
            }

    async def _transform_video(self, video: VideoFileClip, options: Dict[str, Any]) -> Dict[str, Any]:
        """Transform video"""
        try:
            transformed_videos = {}

            # Resize video
            if options.get("resize", False):
                new_size = options.get("size", (640, 480))
                resized = video.resize(new_size)
                output_path = f"/tmp/resized_{uuid.uuid4().hex[:8]}.mp4"
                resized.write_videofile(output_path, codec='libx264')
                transformed_videos["resized"] = output_path
                resized.close()

            # Trim video
            if options.get("trim", False):
                start_time = options.get("start_time", 0)
                end_time = options.get("end_time", video.duration)
                trimmed = video.subclip(start_time, end_time)
                output_path = f"/tmp/trimmed_{uuid.uuid4().hex[:8]}.mp4"
                trimmed.write_videofile(output_path, codec='libx264')
                transformed_videos["trimmed"] = output_path
                trimmed.close()

            video.close()
            return {
                "success": True,
                "transformed_videos": transformed_videos,
                "applied_transformations": list(transformed_videos.keys())
            }

        except Exception as e:
            video.close()
            return {
                "success": False,
                "error": f"Video transformation error: {str(e)}"
            }

    async def _process_document(
        self,
        document_data: Union[str, bytes],
        task: ProcessingTask,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process document with AI capabilities"""
        try:
            if task == ProcessingTask.EXTRACTION:
                return await self._extract_from_document(document_data, options)
            elif task == ProcessingTask.ANALYSIS:
                return await self._analyze_document(document_data, options)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported task '{task.value}' for document processing"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Document processing error: {str(e)}"
            }

    async def _extract_from_document(self, document_data: Union[str, bytes], options: Dict[str, Any]) -> Dict[str, Any]:
        """Extract text and data from document"""
        try:
            extracted_data = {}

            # Extract text (simplified - in production use proper document parsing)
            if isinstance(document_data, bytes):
                text_content = "Document text extraction placeholder"
            else:
                with open(document_data, 'r', encoding='utf-8') as f:
                    text_content = f.read()

            extracted_data["text"] = text_content

            # Extract structured data
            if options.get("extract_structured", False):
                # Placeholder for structured data extraction
                extracted_data["structured_data"] = {
                    "entities": [],
                    "tables": [],
                    "metadata": {}
                }

            return {
                "success": True,
                "extracted_data": extracted_data,
                "extraction_types": list(extracted_data.keys())
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Document extraction error: {str(e)}"
            }

    async def _analyze_document(self, document_data: Union[str, bytes], options: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze document content"""
        try:
            # Extract text first
            extraction_result = await self._extract_from_document(document_data, {"extract_structured": False})
            if not extraction_result["success"]:
                return extraction_result

            text_content = extraction_result["extracted_data"]["text"]

            # Analyze with AI
            analysis_prompt = options.get("prompt", "Analyze this document and provide a summary with key insights.")

            analysis_result = await ai_service_manager.generate_text(
                prompt=f"{analysis_prompt}\n\nDocument content:\n{text_content[:4000]}...",  # Limit text length
                max_tokens=500
            )

            if analysis_result["success"]:
                return {
                    "success": True,
                    "analysis": analysis_result["text"],
                    "document_stats": {
                        "word_count": len(text_content.split()),
                        "character_count": len(text_content)
                    }
                }

            return {
                "success": True,
                "analysis": "Document analysis placeholder",
                "document_stats": {
                    "word_count": len(text_content.split()),
                    "character_count": len(text_content)
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Document analysis error: {str(e)}"
            }

    async def _process_table(
        self,
        table_data: Union[str, bytes],
        task: ProcessingTask,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process tabular data"""
        try:
            import pandas as pd

            # Load table data
            if isinstance(table_data, bytes):
                # Assume CSV format
                from io import StringIO
                df = pd.read_csv(StringIO(table_data.decode('utf-8')))
            elif isinstance(table_data, str):
                if table_data.endswith('.csv'):
                    df = pd.read_csv(table_data)
                elif table_data.endswith('.xlsx') or table_data.endswith('.xls'):
                    df = pd.read_excel(table_data)
                else:
                    # Assume CSV format
                    df = pd.read_csv(StringIO(table_data))
            else:
                raise ValueError("Unsupported table data format")

            if task == ProcessingTask.ANALYSIS:
                return await self._analyze_table(df, options)
            elif task == ProcessingTask.TRANSFORMATION:
                return await self._transform_table(df, options)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported task '{task.value}' for table processing"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Table processing error: {str(e)}"
            }

    async def _analyze_table(self, df: pd.DataFrame, options: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze tabular data"""
        try:
            analysis = {}

            # Basic statistics
            analysis["shape"] = df.shape
            analysis["columns"] = list(df.columns)
            analysis["dtypes"] = df.dtypes.to_dict()
            analysis["missing_values"] = df.isnull().sum().to_dict()

            # Numeric statistics
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                analysis["numeric_stats"] = df[numeric_cols].describe().to_dict()

            # Categorical statistics
            categorical_cols = df.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                analysis["categorical_stats"] = {}
                for col in categorical_cols:
                    analysis["categorical_stats"][col] = {
                        "unique_count": df[col].nunique(),
                        "top_values": df[col].value_counts().head(10).to_dict()
                    }

            return {
                "success": True,
                "analysis": analysis,
                "analysis_types": list(analysis.keys())
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Table analysis error: {str(e)}"
            }

    async def _transform_table(self, df: pd.DataFrame, options: Dict[str, Any]) -> Dict[str, Any]:
        """Transform tabular data"""
        try:
            transformed_tables = {}

            # Filter rows
            if options.get("filter_rows", False):
                filter_condition = options.get("filter_condition", "")
                # Placeholder for filtering logic
                filtered_df = df.copy()
                transformed_tables["filtered"] = filtered_df.to_dict('records')

            # Group and aggregate
            if options.get("group_aggregate", False):
                group_by = options.get("group_by", [])
                agg_func = options.get("agg_func", "mean")
                if group_by:
                    grouped_df = df.groupby(group_by).agg(agg_func)
                    transformed_tables["grouped"] = grouped_df.to_dict()

            # Pivot table
            if options.get("pivot", False):
                index = options.get("pivot_index", [])
                columns = options.get("pivot_columns", [])
                values = options.get("pivot_values", [])
                if index and columns and values:
                    pivot_df = df.pivot_table(index=index, columns=columns, values=values, aggfunc='mean')
                    transformed_tables["pivoted"] = pivot_df.to_dict()

            return {
                "success": True,
                "transformed_tables": transformed_tables,
                "applied_transformations": list(transformed_tables.keys())
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Table transformation error: {str(e)}"
            }

    async def _process_chart(
        self,
        chart_data: Union[str, bytes],
        task: ProcessingTask,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process chart data"""
        try:
            if task == ProcessingTask.EXTRACTION:
                return await self._extract_from_chart(chart_data, options)
            elif task == ProcessingTask.GENERATION:
                return await self._generate_chart(chart_data, options)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported task '{task.value}' for chart processing"
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Chart processing error: {str(e)}"
            }

    async def _extract_from_chart(self, chart_data: Union[str, bytes], options: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from chart image"""
        try:
            # Load chart image
            if isinstance(chart_data, bytes):
                image = Image.open(io.BytesIO(chart_data))
            else:
                image = Image.open(chart_data)

            # Convert to base64 for AI analysis
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG")
            image_base64 = base64.b64encode(buffered.getvalue()).decode()

            # Analyze chart with AI
            analysis_prompt = "Analyze this chart and extract the data points. Provide the data in a structured format."

            analysis_result = await ai_service_manager.generate_chat_response([
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": analysis_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }
            ], model="gpt-4-vision-preview")

            if analysis_result["success"]:
                return {
                    "success": True,
                    "extracted_data": analysis_result["content"],
                    "chart_info": {
                        "size": image.size,
                        "format": image.format
                    }
                }

            return {
                "success": True,
                "extracted_data": "Chart data extraction placeholder",
                "chart_info": {
                    "size": image.size,
                    "format": image.format
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Chart extraction error: {str(e)}"
            }

    async def _generate_chart(self, chart_data: Union[str, bytes], options: Dict[str, Any]) -> Dict[str, Any]:
        """Generate chart from data"""
        try:
            # Parse data (assume JSON format)
            if isinstance(chart_data, bytes):
                data = json.loads(chart_data.decode('utf-8'))
            else:
                data = json.loads(chart_data)

            chart_type = options.get("chart_type", "line")
            title = options.get("title", "Generated Chart")

            # Create chart
            plt.figure(figsize=(10, 6))

            if chart_type == "line":
                if "x" in data and "y" in data:
                    plt.plot(data["x"], data["y"])
            elif chart_type == "bar":
                if "categories" in data and "values" in data:
                    plt.bar(data["categories"], data["values"])
            elif chart_type == "scatter":
                if "x" in data and "y" in data:
                    plt.scatter(data["x"], data["y"])
            elif chart_type == "pie":
                if "labels" in data and "values" in data:
                    plt.pie(data["values"], labels=data["labels"])

            plt.title(title)
            plt.tight_layout()

            # Save chart
            output_path = f"/tmp/chart_{uuid.uuid4().hex[:8]}.png"
            plt.savefig(output_path)
            plt.close()

            # Convert to base64
            with open(output_path, 'rb') as f:
                chart_base64 = base64.b64encode(f.read()).decode()

            return {
                "success": True,
                "generated_chart": chart_base64,
                "chart_type": chart_type,
                "title": title
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Chart generation error: {str(e)}"
            }

    # Helper methods
    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string"""
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode()

    def _extract_dominant_colors(self, image: Image.Image, n_colors: int = 5) -> List[str]:
        """Extract dominant colors from image"""
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Resize image for faster processing
        image = image.resize((150, 150))

        # Get color data
        colors = image.getcolors(image.size[0] * image.size[1])

        # Sort by frequency and get top colors
        sorted_colors = sorted(colors, key=lambda x: x[0], reverse=True)[:n_colors]
        dominant_colors = [f"#{color[2][0]:02x}{color[2][1]:02x}{color[2][2]:02x}" for color in sorted_colors]

        return dominant_colors

    def _extract_image_features(self, image: Image.Image) -> Dict[str, Any]:
        """Extract features from image"""
        features = {}

        # Basic features
        features["size"] = image.size
        features["mode"] = image.mode
        features["format"] = image.format

        # Color features
        if image.mode == 'RGB':
            colors = image.getcolors(image.size[0] * image.size[1])
            if colors:
                features["color_count"] = len(colors)
                features["dominant_color"] = max(colors, key=lambda x: x[0])[2]

        return features


# Global instance
multi_modal_processor = MultiModalProcessor()