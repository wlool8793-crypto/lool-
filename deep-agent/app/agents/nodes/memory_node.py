import json
import hashlib
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from app.services.cache_service import cache_service
from app.core.config import settings
from app.models import AgentState, Conversation, Message
import logging

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    SHORT_TERM = "short_term"      # Current conversation context
    LONG_TERM = "long_term"        # Persistent memories across conversations
    EPISODIC = "episodic"          # Specific episodes or events
    SEMANTIC = "semantic"          # General knowledge and facts
    WORKING = "working"            # Current active working memory


class MemoryPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Memory:
    """Memory data structure"""
    id: str
    type: MemoryType
    content: Dict[str, Any]
    priority: MemoryPriority
    created_at: datetime
    last_accessed: datetime
    access_count: int
    tags: List[str]
    metadata: Dict[str, Any]
    expiration: Optional[datetime] = None
    conversation_id: Optional[int] = None
    user_id: Optional[int] = None


class MemoryNode:
    """
    Advanced memory management node with hierarchical memory system
    """

    def __init__(self):
        self.memory_cache = {}
        self.memory_index = {}
        self.memory_limits = {
            "short_term_capacity": 1000,
            "long_term_capacity": 10000,
            "working_capacity": 100,
            "max_memory_age_days": 365,
            "consolidation_threshold": 100,
            "retrieval_limit": 50
        }

        # Memory consolidation patterns
        self.consolidation_patterns = {
            "conversation_summary": self._consolidate_conversation,
            "frequent_patterns": self._consolidate_frequent_patterns,
            "user_preferences": self._consolidate_user_preferences,
            "knowledge_facts": self._consolidate_knowledge_facts
        }

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process memory operations including storage, retrieval, and consolidation
        """
        try:
            conversation_id = state.get("conversation_id")
            user_id = state.get("user_id")
            current_context = state.get("context", {})
            execution_results = state.get("execution_results", {})
            processed_input = state.get("processed_data", {})

            # Store current interaction in working memory
            await self._store_working_memory(
                conversation_id, user_id, processed_input, execution_results, current_context
            )

            # Retrieve relevant memories
            retrieved_memories = await self._retrieve_relevant_memories(
                processed_input, current_context, conversation_id, user_id
            )

            # Update conversation context with retrieved memories
            enhanced_context = await self._enhance_context_with_memories(
                current_context, retrieved_memories
            )

            # Consolidate memories if needed
            await self._consolidate_memories_if_needed(conversation_id, user_id)

            # Clean up expired memories
            await self._cleanup_expired_memories()

            return {
                "status": "success",
                "retrieved_memories": retrieved_memories,
                "enhanced_context": enhanced_context,
                "memory_operations": {
                    "stored_working_memories": 1,
                    "retrieved_memories_count": len(retrieved_memories),
                    "memory_enhancements": len(enhanced_context.get("memory_enhancements", []))
                },
                "memory_metadata": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "memory_stats": await self._get_memory_stats(conversation_id, user_id)
                }
            }

        except Exception as e:
            logger.error(f"Memory processing error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "retrieved_memories": [],
                "enhanced_context": current_context,
                "memory_operations": {},
                "memory_metadata": {
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

    async def _store_working_memory(
        self,
        conversation_id: int,
        user_id: int,
        processed_input: Dict[str, Any],
        execution_results: Dict[str, Any],
        current_context: Dict[str, Any]
    ):
        """
        Store current interaction in working memory
        """
        # Create working memory entry
        working_memory = Memory(
            id=str(uuid.uuid4()),
            type=MemoryType.WORKING,
            content={
                "input": processed_input,
                "execution_results": execution_results,
                "context": current_context
            },
            priority=MemoryPriority.HIGH,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            access_count=1,
            tags=["current_interaction", f"conversation_{conversation_id}"],
            metadata={
                "conversation_id": conversation_id,
                "user_id": user_id,
                "interaction_type": "current"
            },
            expiration=datetime.utcnow() + timedelta(hours=1),  # Working memory expires after 1 hour
            conversation_id=conversation_id,
            user_id=user_id
        )

        # Store in cache
        cache_key = f"memory:working:{working_memory.id}"
        await cache_service.set(cache_key, asdict(working_memory), ttl=3600)

        # Update memory index
        await self._update_memory_index(working_memory)

    async def _retrieve_relevant_memories(
        self,
        processed_input: Dict[str, Any],
        current_context: Dict[str, Any],
        conversation_id: int,
        user_id: int
    ) -> List[Memory]:
        """
        Retrieve relevant memories based on current context
        """
        relevant_memories = []

        # Extract search terms from input
        search_terms = await self._extract_search_terms(processed_input)

        # Search different memory types
        for memory_type in [MemoryType.SHORT_TERM, MemoryType.LONG_TERM, MemoryType.SEMANTIC]:
            memories = await self._search_memories_by_type(
                memory_type, search_terms, conversation_id, user_id
            )
            relevant_memories.extend(memories)

        # Sort by relevance and priority
        relevant_memories.sort(
            key=lambda m: (m.priority.value, m.access_count, m.last_accessed),
            reverse=True
        )

        # Limit results
        return relevant_memories[:self.memory_limits["retrieval_limit"]]

    async def _extract_search_terms(self, processed_input: Dict[str, Any]) -> List[str]:
        """
        Extract search terms from processed input
        """
        terms = []

        # Add entities as search terms
        entities = processed_input.get("entities", [])
        for entity in entities:
            if "value" in entity:
                terms.append(str(entity["value"]).lower())

        # Add key phrases
        key_phrases = processed_input.get("key_phrases", [])
        terms.extend([phrase.lower() for phrase in key_phrases[:5]])  # Top 5 phrases

        # Add intent
        intent = processed_input.get("intent", {}).get("type", "")
        if intent:
            terms.append(intent)

        # Add category
        category = processed_input.get("category", {}).get("category", "")
        if category:
            terms.append(category)

        return list(set(terms))  # Remove duplicates

    async def _search_memories_by_type(
        self,
        memory_type: MemoryType,
        search_terms: List[str],
        conversation_id: int,
        user_id: int
    ) -> List[Memory]:
        """
        Search memories of a specific type
        """
        memories = []

        # Get memory cache key pattern
        cache_pattern = f"memory:{memory_type.value}:*"

        # Search through memories (simplified - in production, use proper search)
        # This is a basic implementation - production would use vector search or better indexing
        for term in search_terms:
            if term in self.memory_index:
                for memory_id in self.memory_index[term]:
                    memory_data = await cache_service.get(f"memory:{memory_type.value}:{memory_id}")
                    if memory_data:
                        memory = Memory(**memory_data)

                        # Check if memory is relevant to current context
                        if await self._is_memory_relevant(memory, conversation_id, user_id):
                            memories.append(memory)

        return memories

    async def _is_memory_relevant(
        self,
        memory: Memory,
        conversation_id: int,
        user_id: int
    ) -> bool:
        """
        Check if memory is relevant to current context
        """
        # Check if memory belongs to current user
        if memory.user_id and memory.user_id != user_id:
            return False

        # Check expiration
        if memory.expiration and memory.expiration < datetime.utcnow():
            return False

        # For working memory, check conversation
        if memory.type == MemoryType.WORKING:
            return memory.conversation_id == conversation_id

        # For other memory types, check if not too old
        memory_age = (datetime.utcnow() - memory.created_at).days
        if memory_age > self.memory_limits["max_memory_age_days"]:
            return False

        return True

    async def _enhance_context_with_memories(
        self,
        current_context: Dict[str, Any],
        retrieved_memories: List[Memory]
    ) -> Dict[str, Any]:
        """
        Enhance current context with retrieved memories
        """
        enhanced_context = current_context.copy()
        memory_enhancements = []

        for memory in retrieved_memories:
            # Update access statistics
            memory.last_accessed = datetime.utcnow()
            memory.access_count += 1

            # Extract relevant information based on memory type
            if memory.type == MemoryType.SHORT_TERM:
                enhancement = await self._enhance_with_short_term_memory(memory, enhanced_context)
            elif memory.type == MemoryType.LONG_TERM:
                enhancement = await self._enhance_with_long_term_memory(memory, enhanced_context)
            elif memory.type == MemoryType.SEMANTIC:
                enhancement = await self._enhance_with_semantic_memory(memory, enhanced_context)
            else:
                enhancement = await self._enhance_with_general_memory(memory, enhanced_context)

            if enhancement:
                memory_enhancements.append(enhancement)

        enhanced_context["memory_enhancements"] = memory_enhancements
        enhanced_context["retrieved_memory_count"] = len(retrieved_memories)

        return enhanced_context

    async def _enhance_with_short_term_memory(self, memory: Memory, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Enhance context with short-term memory
        """
        if "recent_interactions" not in context:
            context["recent_interactions"] = []

        context["recent_interactions"].append({
            "memory_id": memory.id,
            "timestamp": memory.created_at.isoformat(),
            "summary": f"Short-term memory: {memory.metadata.get('interaction_type', 'general')}"
        })

        return {
            "type": "short_term",
            "memory_id": memory.id,
            "enhancement": "Added recent interaction context"
        }

    async def _enhance_with_long_term_memory(self, memory: Memory, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Enhance context with long-term memory
        """
        if "long_term_patterns" not in context:
            context["long_term_patterns"] = []

        context["long_term_patterns"].append({
            "memory_id": memory.id,
            "created_at": memory.created_at.isoformat(),
            "content": memory.content.get("summary", "Long-term pattern")
        })

        return {
            "type": "long_term",
            "memory_id": memory.id,
            "enhancement": "Added long-term pattern context"
        }

    async def _enhance_with_semantic_memory(self, memory: Memory, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Enhance context with semantic memory
        """
        if "knowledge_base" not in context:
            context["knowledge_base"] = []

        context["knowledge_base"].append({
            "memory_id": memory.id,
            "fact": memory.content.get("fact", "Knowledge fact"),
            "confidence": memory.content.get("confidence", 0.5)
        })

        return {
            "type": "semantic",
            "memory_id": memory.id,
            "enhancement": "Added semantic knowledge"
        }

    async def _enhance_with_general_memory(self, memory: Memory, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Enhance context with general memory
        """
        return {
            "type": "general",
            "memory_id": memory.id,
            "enhancement": "Added general memory context"
        }

    async def _consolidate_memories_if_needed(self, conversation_id: int, user_id: int):
        """
        Consolidate memories if consolidation threshold is reached
        """
        # Check if consolidation is needed
        working_memories = await self._get_working_memories(conversation_id)

        if len(working_memories) >= self.memory_limits["consolidation_threshold"]:
            await self._consolidate_working_memories(working_memories, conversation_id, user_id)

    async def _get_working_memories(self, conversation_id: int) -> List[Memory]:
        """
        Get all working memories for a conversation
        """
        memories = []

        # Get all memory keys
        cache_keys = await cache_service.keys("memory:working:*")

        for key in cache_keys:
            memory_data = await cache_service.get(key)
            if memory_data:
                memory = Memory(**memory_data)
                if memory.conversation_id == conversation_id:
                    memories.append(memory)

        return memories

    async def _consolidate_working_memories(
        self,
        working_memories: List[Memory],
        conversation_id: int,
        user_id: int
    ):
        """
        Consolidate working memories into long-term memory
        """
        if not working_memories:
            return

        # Create consolidated memory
        consolidated_memory = Memory(
            id=str(uuid.uuid4()),
            type=MemoryType.LONG_TERM,
            content={
                "consolidated_from": len(working_memories),
                "conversation_id": conversation_id,
                "summary": await self._generate_conversation_summary(working_memories),
                "key_patterns": await self._extract_key_patterns(working_memories),
                "timestamp": datetime.utcnow().isoformat()
            },
            priority=MemoryPriority.NORMAL,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            access_count=1,
            tags=["consolidated", f"conversation_{conversation_id}"],
            metadata={
                "consolidation_type": "working_to_long_term",
                "source_memories": [m.id for m in working_memories],
                "conversation_id": conversation_id,
                "user_id": user_id
            },
            conversation_id=conversation_id,
            user_id=user_id
        )

        # Store consolidated memory
        cache_key = f"memory:long_term:{consolidated_memory.id}"
        await cache_service.set(cache_key, asdict(consolidated_memory), ttl=86400 * 30)  # 30 days

        # Update memory index
        await self._update_memory_index(consolidated_memory)

        # Clean up working memories
        for memory in working_memories:
            cache_key = f"memory:working:{memory.id}"
            await cache_service.delete(cache_key)

    async def _generate_conversation_summary(self, working_memories: List[Memory]) -> str:
        """
        Generate summary from working memories
        """
        # Extract key information
        interactions = []
        for memory in working_memories:
            if "input" in memory.content:
                input_data = memory.content["input"]
                original_message = input_data.get("original_message", "")
                if original_message:
                    interactions.append(original_message)

        # Simple summary generation
        if len(interactions) == 1:
            return f"Single interaction: {interactions[0][:100]}..."
        elif len(interactions) > 1:
            return f"Conversation with {len(interactions)} interactions. Topics: {', '.join([i[:50] for i in interactions[:3]])}..."
        else:
            return "Conversation with no text content"

    async def _extract_key_patterns(self, working_memories: List[Memory]) -> List[str]:
        """
        Extract key patterns from working memories
        """
        patterns = []

        # Extract intents
        intents = []
        for memory in working_memories:
            if "input" in memory.content:
                intent = memory.content["input"].get("intent", {}).get("type")
                if intent:
                    intents.append(intent)

        # Find most common intents
        intent_counts = {}
        for intent in intents:
            intent_counts[intent] = intent_counts.get(intent, 0) + 1

        top_intents = sorted(intent_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        patterns.extend([f"Intent: {intent} ({count} times)" for intent, count in top_intents])

        return patterns

    async def _consolidate_conversation(self, memories: List[Memory]) -> Memory:
        """
        Consolidate conversation memories
        """
        return Memory(
            id=str(uuid.uuid4()),
            type=MemoryType.EPISODIC,
            content={
                "type": "conversation_summary",
                "memories_consolidated": len(memories),
                "summary": "Consolidated conversation memories"
            },
            priority=MemoryPriority.NORMAL,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            access_count=1,
            tags=["consolidated", "conversation"],
            metadata={"consolidation_pattern": "conversation_summary"}
        )

    async def _consolidate_frequent_patterns(self, memories: List[Memory]) -> Memory:
        """
        Consolidate frequent patterns
        """
        return Memory(
            id=str(uuid.uuid4()),
            type=MemoryType.SEMANTIC,
            content={
                "type": "frequent_patterns",
                "pattern_frequency": "high",
                "description": "Consolidated frequent patterns"
            },
            priority=MemoryPriority.HIGH,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            access_count=1,
            tags=["consolidated", "patterns"],
            metadata={"consolidation_pattern": "frequent_patterns"}
        )

    async def _consolidate_user_preferences(self, memories: List[Memory]) -> Memory:
        """
        Consolidate user preferences
        """
        return Memory(
            id=str(uuid.uuid4()),
            type=MemoryType.SEMANTIC,
            content={
                "type": "user_preferences",
                "preferences": {},
                "confidence": 0.8
            },
            priority=MemoryPriority.HIGH,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            access_count=1,
            tags=["consolidated", "preferences"],
            metadata={"consolidation_pattern": "user_preferences"}
        )

    async def _consolidate_knowledge_facts(self, memories: List[Memory]) -> Memory:
        """
        Consolidate knowledge facts
        """
        return Memory(
            id=str(uuid.uuid4()),
            type=MemoryType.SEMANTIC,
            content={
                "type": "knowledge_facts",
                "facts": [],
                "sources": []
            },
            priority=MemoryPriority.NORMAL,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            access_count=1,
            tags=["consolidated", "knowledge"],
            metadata={"consolidation_pattern": "knowledge_facts"}
        )

    async def _update_memory_index(self, memory: Memory):
        """
        Update memory search index
        """
        # Generate index terms
        index_terms = []

        # Add tags
        index_terms.extend(memory.tags)

        # Add content-based terms
        if "input" in memory.content:
            input_data = memory.content["input"]
            entities = input_data.get("entities", [])
            for entity in entities:
                if "value" in entity:
                    index_terms.append(str(entity["value"]).lower())

        # Add metadata terms
        for key, value in memory.metadata.items():
            if isinstance(value, str):
                index_terms.append(value.lower())

        # Update index
        for term in index_terms:
            if term not in self.memory_index:
                self.memory_index[term] = []
            if memory.id not in self.memory_index[term]:
                self.memory_index[term].append(memory.id)

    async def _cleanup_expired_memories(self):
        """
        Clean up expired memories
        """
        current_time = datetime.utcnow()

        # Check all memory types
        for memory_type in MemoryType:
            cache_keys = await cache_service.keys(f"memory:{memory_type.value}:*")

            for key in cache_keys:
                memory_data = await cache_service.get(key)
                if memory_data:
                    memory = Memory(**memory_data)

                    # Check if memory is expired
                    if memory.expiration and memory.expiration < current_time:
                        await cache_service.delete(key)

                        # Remove from index
                        await self._remove_from_index(memory.id)

    async def _remove_from_index(self, memory_id: str):
        """
        Remove memory from search index
        """
        for term, memory_ids in self.memory_index.items():
            if memory_id in memory_ids:
                memory_ids.remove(memory_id)

                # Remove empty terms
                if not memory_ids:
                    del self.memory_index[term]

    async def _get_memory_stats(self, conversation_id: int, user_id: int) -> Dict[str, Any]:
        """
        Get memory statistics
        """
        stats = {
            "total_memories": 0,
            "memories_by_type": {},
            "average_access_count": 0,
            "oldest_memory_age_days": 0
        }

        # Count memories by type
        for memory_type in MemoryType:
            cache_keys = await cache_service.keys(f"memory:{memory_type.value}:*")
            type_count = 0
            total_access = 0
            oldest_age = 0

            for key in cache_keys:
                memory_data = await cache_service.get(key)
                if memory_data:
                    memory = Memory(**memory_data)
                    type_count += 1
                    total_access += memory.access_count

                    memory_age = (datetime.utcnow() - memory.created_at).days
                    oldest_age = max(oldest_age, memory_age)

            stats["memories_by_type"][memory_type.value] = type_count
            stats["total_memories"] += type_count

            if type_count > 0:
                stats["average_access_count"] += total_access / type_count
                stats["oldest_memory_age_days"] = max(stats["oldest_memory_age_days"], oldest_age)

        # Calculate overall average
        if stats["total_memories"] > 0:
            stats["average_access_count"] /= len(MemoryType)

        return stats

    async def store_memory(
        self,
        memory_type: MemoryType,
        content: Dict[str, Any],
        priority: MemoryPriority = MemoryPriority.NORMAL,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> str:
        """
        Store a new memory
        """
        memory = Memory(
            id=str(uuid.uuid4()),
            type=memory_type,
            content=content,
            priority=priority,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            access_count=1,
            tags=tags or [],
            metadata=metadata or {},
            conversation_id=conversation_id,
            user_id=user_id
        )

        cache_key = f"memory:{memory_type.value}:{memory.id}"
        await cache_service.set(cache_key, asdict(memory), ttl=86400 * 30)  # 30 days

        await self._update_memory_index(memory)

        return memory.id

    async def retrieve_memory(self, memory_id: str) -> Optional[Memory]:
        """
        Retrieve a specific memory by ID
        """
        # Search through all memory types
        for memory_type in MemoryType:
            cache_key = f"memory:{memory_type.value}:{memory_id}"
            memory_data = await cache_service.get(cache_key)

            if memory_data:
                memory = Memory(**memory_data)

                # Update access statistics
                memory.last_accessed = datetime.utcnow()
                memory.access_count += 1

                # Store updated memory
                await cache_service.set(cache_key, asdict(memory), ttl=86400 * 30)

                return memory

        return None

    async def search_memories(
        self,
        query: str,
        memory_type: Optional[MemoryType] = None,
        user_id: Optional[int] = None,
        limit: int = 10
    ) -> List[Memory]:
        """
        Search memories by query
        """
        results = []
        query_terms = query.lower().split()

        # Determine memory types to search
        memory_types = [memory_type] if memory_type else list(MemoryType)

        for memory_type in memory_types:
            cache_keys = await cache_service.keys(f"memory:{memory_type.value}:*")

            for key in cache_keys:
                memory_data = await cache_service.get(key)
                if memory_data:
                    memory = Memory(**memory_data)

                    # Check user filter
                    if user_id and memory.user_id and memory.user_id != user_id:
                        continue

                    # Check if memory matches query
                    if await self._memory_matches_query(memory, query_terms):
                        results.append(memory)

        # Sort by relevance and limit results
        results.sort(key=lambda m: (m.priority.value, m.access_count), reverse=True)
        return results[:limit]

    async def _memory_matches_query(self, memory: Memory, query_terms: List[str]) -> bool:
        """
        Check if memory matches search query
        """
        # Search in content
        content_str = json.dumps(memory.content).lower()

        # Search in tags
        tags_str = " ".join(memory.tags).lower()

        # Search in metadata
        metadata_str = json.dumps(memory.metadata).lower()

        combined_text = f"{content_str} {tags_str} {metadata_str}"

        return any(term in combined_text for term in query_terms)


# Global instance
memory_node = MemoryNode()