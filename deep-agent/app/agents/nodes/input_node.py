import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.services.cache_service import cache_service
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class InputProcessingNode:
    """
    Advanced input processing node with NLP capabilities
    """

    def __init__(self):
        self.intent_patterns = {
            "question": [
                r"^(what|how|why|when|where|who|which|whose|can|could|would|should|do|does|did|is|are|was|were)\s",
                r"\?$"
            ],
            "command": [
                r"^(create|delete|update|send|upload|download|start|stop|pause|resume)\s",
                r"^(please| kindly)\s+\w+"
            ],
            "information": [
                r"^(tell me|show me|give me|list|find|search for)\s",
                r"^(i want|i need|i'm looking for)\s"
            ],
            "greeting": [
                r"^(hello|hi|hey|good morning|good afternoon|good evening|greetings)\s*[\.,!]*",
                r"^(how are you|how do you do)\s*[\?]*"
            ],
            "farewell": [
                r"^(goodbye|bye|see you|later|farewell|take care)\s*[\.,!]*",
                r"^(thank you|thanks)\s*[\.,!]*"
            ]
        }

        self.entity_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "url": r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w .-]*\??[/\w .-]*',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "date": r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b',
            "time": r'\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?\b',
            "number": r'\b\d+(?:,\d{3})*(?:\.\d+)?\b',
            "currency": r'\$\d+(?:,\d{3})*(?:\.\d{2})?|\b\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:dollars|USD)\b',
            "percentage": r'\b\d+(?:\.\d+)?%\b'
        }

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user input with advanced NLP analysis
        """
        try:
            message = state.get("message", "")
            context = state.get("context", {})

            # Basic validation
            if not message or not message.strip():
                return {
                    "status": "error",
                    "error": "Empty message",
                    "processed_data": {}
                }

            # Preprocess message
            cleaned_message = self._preprocess_message(message)

            # Extract intent
            intent_data = await self._extract_intent(cleaned_message)

            # Extract entities
            entities = await self._extract_entities(cleaned_message)

            # Analyze sentiment
            sentiment = await self._analyze_sentiment(cleaned_message)

            # Extract key phrases
            key_phrases = await self._extract_key_phrases(cleaned_message)

            # Categorize message
            category = await self._categorize_message(cleaned_message, intent_data)

            # Detect language
            language = await self._detect_language(cleaned_message)

            # Generate message signature
            message_signature = self._generate_message_signature(cleaned_message)

            # Build processed data
            processed_data = {
                "original_message": message,
                "cleaned_message": cleaned_message,
                "intent": intent_data,
                "entities": entities,
                "sentiment": sentiment,
                "key_phrases": key_phrases,
                "category": category,
                "language": language,
                "signature": message_signature,
                "processing_metadata": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "processing_time": 0.0,  # Will be filled by orchestrator
                    "confidence_scores": {
                        "intent": intent_data.get("confidence", 0.0),
                        "entities": self._calculate_entity_confidence(entities),
                        "sentiment": sentiment.get("confidence", 0.0),
                        "category": category.get("confidence", 0.0)
                    }
                }
            }

            # Update context
            updated_context = await self._update_context(context, processed_data)

            # Cache processing results
            await self._cache_processing_results(state["conversation_id"], processed_data)

            return {
                "status": "success",
                "processed_data": processed_data,
                "updated_context": updated_context,
                "next_steps": await self._determine_next_steps(processed_data)
            }

        except Exception as e:
            logger.error(f"Input processing error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "processed_data": {}
            }

    def _preprocess_message(self, message: str) -> str:
        """
        Preprocess message for analysis
        """
        # Convert to lowercase
        message = message.lower()

        # Remove extra whitespace
        message = re.sub(r'\s+', ' ', message)

        # Remove special characters but keep basic punctuation
        message = re.sub(r'[^\w\s\.\?\!\,\;\:\-\'\"]', ' ', message)

        # Normalize quotes
        message = re.sub(r'[""]', '"', message)
        message = re.sub(r'['']', "'", message)

        return message.strip()

    async def _extract_intent(self, message: str) -> Dict[str, Any]:
        """
        Extract user intent from message
        """
        detected_intents = []

        # Check against predefined patterns
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    detected_intents.append({
                        "type": intent_type,
                        "confidence": 0.8,
                        "pattern_matched": pattern
                    })

        # If no pattern matched, use ML-based intent detection
        if not detected_intents:
            detected_intents.append({
                "type": "general",
                "confidence": 0.5,
                "pattern_matched": None
            })

        # Sort by confidence and return the best match
        detected_intents.sort(key=lambda x: x["confidence"], reverse=True)
        best_intent = detected_intents[0]

        return {
            "type": best_intent["type"],
            "confidence": best_intent["confidence"],
            "pattern_matched": best_intent["pattern_matched"],
            "all_intents": detected_intents
        }

    async def _extract_entities(self, message: str) -> List[Dict[str, Any]]:
        """
        Extract named entities from message
        """
        entities = []

        # Extract predefined entities
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.finditer(pattern, message, re.IGNORECASE)
            for match in matches:
                entities.append({
                    "type": entity_type,
                    "value": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 0.9
                })

        # Extract custom entities using context
        custom_entities = await self._extract_custom_entities(message)
        entities.extend(custom_entities)

        return entities

    async def _extract_custom_entities(self, message: str) -> List[Dict[str, Any]]:
        """
        Extract custom entities using context and machine learning
        """
        # This is a simplified version - in production, use NLP libraries
        custom_entities = []

        # Extract proper nouns (capitalized words)
        proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', message)
        for noun in proper_nouns:
            if len(noun) > 2:  # Filter out short words
                custom_entities.append({
                    "type": "proper_noun",
                    "value": noun,
                    "confidence": 0.6
                })

        return custom_entities

    async def _analyze_sentiment(self, message: str) -> Dict[str, Any]:
        """
        Analyze sentiment of the message
        """
        # Simple sentiment analysis using keyword matching
        positive_words = [
            "good", "great", "excellent", "amazing", "wonderful", "fantastic",
            "love", "like", "happy", "pleased", "satisfied", "perfect", "best"
        ]

        negative_words = [
            "bad", "terrible", "awful", "horrible", "hate", "dislike",
            "angry", "frustrated", "disappointed", "sad", "worst", "broken"
        ]

        message_lower = message.lower()

        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)

        total_words = len(message_lower.split())
        if total_words == 0:
            return {"sentiment": "neutral", "confidence": 0.5}

        positive_ratio = positive_count / total_words
        negative_ratio = negative_count / total_words

        if positive_ratio > negative_ratio:
            sentiment = "positive"
            confidence = min(0.5 + positive_ratio, 1.0)
        elif negative_ratio > positive_ratio:
            sentiment = "negative"
            confidence = min(0.5 + negative_ratio, 1.0)
        else:
            sentiment = "neutral"
            confidence = 0.5

        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "scores": {
                "positive": positive_ratio,
                "negative": negative_ratio,
                "neutral": 1.0 - positive_ratio - negative_ratio
            }
        }

    async def _extract_key_phrases(self, message: str) -> List[str]:
        """
        Extract key phrases from message
        """
        # Simple key phrase extraction using noun phrases
        # In production, use more sophisticated NLP techniques

        # Remove stop words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "about", "as", "is", "was", "are", "were",
            "be", "been", "have", "has", "had", "do", "does", "did", "will", "would",
            "could", "should", "may", "might", "must", "can", "this", "that", "these",
            "those", "i", "you", "he", "she", "it", "we", "they", "me", "him", "her",
            "us", "them", "my", "your", "his", "her", "its", "our", "their"
        }

        words = message.split()
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]

        # Extract phrases (consecutive meaningful words)
        key_phrases = []
        current_phrase = []

        for word in filtered_words:
            current_phrase.append(word)
            if len(current_phrase) >= 2:
                key_phrases.append(" ".join(current_phrase))
                current_phrase = [word]  # Start new phrase with overlap

        return key_phrases[:10]  # Return top 10 phrases

    async def _categorize_message(self, message: str, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Categorize message into predefined categories
        """
        categories = {
            "technical": [
                "code", "programming", "software", "development", "bug", "debug",
                "api", "database", "server", "algorithm", "function", "variable"
            ],
            "business": [
                "business", "company", "market", "sales", "revenue", "profit",
                "customer", "client", "project", "meeting", "strategy", "plan"
            ],
            "personal": [
                "personal", "life", "family", "health", "hobby", "interest",
                "feeling", "emotion", "experience", "opinion", "preference"
            ],
            "information": [
                "information", "data", "fact", "detail", "explanation", "description",
                "summary", "overview", "analysis", "research", "study"
            ],
            "action": [
                "do", "make", "create", "build", "implement", "execute", "run",
                "start", "stop", "change", "update", "modify", "improve"
            ]
        }

        message_lower = message.lower()
        category_scores = {}

        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            category_scores[category] = score

        # Find best category
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            confidence = category_scores[best_category] / len(message_lower.split())
            confidence = min(confidence, 1.0)
        else:
            best_category = "general"
            confidence = 0.5

        return {
            "category": best_category,
            "confidence": confidence,
            "all_scores": category_scores
        }

    async def _detect_language(self, message: str) -> Dict[str, Any]:
        """
        Detect language of the message
        """
        # Simple language detection using character patterns
        # In production, use proper language detection libraries

        english_patterns = [
            r'\b(the|and|or|but|in|on|at|to|for|of|with|by)\b',
            r'\b(is|are|was|were|be|been|have|has|had|do|does|did)\b'
        ]

        message_lower = message.lower()
        english_score = 0

        for pattern in english_patterns:
            matches = re.findall(pattern, message_lower)
            english_score += len(matches)

        # Calculate confidence based on message length
        total_words = len(message.split())
        if total_words == 0:
            return {"language": "unknown", "confidence": 0.0}

        confidence = min(english_score / total_words, 1.0)

        if confidence > 0.3:
            language = "english"
        else:
            language = "unknown"
            confidence = 0.5

        return {
            "language": language,
            "confidence": confidence
        }

    def _generate_message_signature(self, message: str) -> str:
        """
        Generate unique signature for message
        """
        import hashlib
        return hashlib.md5(message.encode()).hexdigest()[:16]

    def _calculate_entity_confidence(self, entities: List[Dict[str, Any]]) -> float:
        """
        Calculate overall entity confidence score
        """
        if not entities:
            return 0.0

        total_confidence = sum(entity.get("confidence", 0.0) for entity in entities)
        return total_confidence / len(entities)

    async def _update_context(self, context: Dict[str, Any], processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update conversation context with processed data
        """
        updated_context = context.copy()

        # Update conversation history
        if "conversation_history" not in updated_context:
            updated_context["conversation_history"] = []

        updated_context["conversation_history"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "message": processed_data["original_message"],
            "intent": processed_data["intent"],
            "entities": processed_data["entities"],
            "sentiment": processed_data["sentiment"]
        })

        # Update user preferences based on sentiment
        if "user_preferences" not in updated_context:
            updated_context["user_preferences"] = {}

        sentiment = processed_data["sentiment"]["sentiment"]
        if sentiment in ["positive", "negative"]:
            updated_context["user_preferences"]["recent_sentiment"] = sentiment

        # Update entity memory
        if "entity_memory" not in updated_context:
            updated_context["entity_memory"] = {}

        for entity in processed_data["entities"]:
            entity_type = entity["type"]
            entity_value = entity["value"]

            if entity_type not in updated_context["entity_memory"]:
                updated_context["entity_memory"][entity_type] = []

            if entity_value not in updated_context["entity_memory"][entity_type]:
                updated_context["entity_memory"][entity_type].append({
                    "value": entity_value,
                    "first_seen": datetime.utcnow().isoformat(),
                    "mentions": 1
                })
            else:
                # Update existing entity
                for existing_entity in updated_context["entity_memory"][entity_type]:
                    if existing_entity["value"] == entity_value:
                        existing_entity["mentions"] += 1
                        existing_entity["last_seen"] = datetime.utcnow().isoformat()
                        break

        return updated_context

    async def _cache_processing_results(self, conversation_id: int, processed_data: Dict[str, Any]):
        """
        Cache processing results for future reference
        """
        cache_key = f"input_processing:{conversation_id}:{processed_data['signature']}"
        await cache_service.set(cache_key, processed_data, ttl=3600)

    async def _determine_next_steps(self, processed_data: Dict[str, Any]) -> List[str]:
        """
        Determine next steps based on processed input
        """
        next_steps = []

        intent = processed_data["intent"]["type"]
        category = processed_data["category"]["category"]
        entities = processed_data["entities"]

        # Basic routing logic
        if intent == "question":
            next_steps.append("information_retrieval")
            if any(e["type"] == "url" for e in entities):
                next_steps.append("web_search")
        elif intent == "command":
            next_steps.append("command_execution")
        elif intent == "information":
            next_steps.append("information_retrieval")
        elif category == "technical":
            next_steps.append("technical_analysis")
        elif category == "business":
            next_steps.append("business_analysis")

        # Always include planning
        if "planning" not in next_steps:
            next_steps.append("planning")

        return next_steps


# Global instance
input_processing_node = InputProcessingNode()