import json
import pickle
import hashlib
from typing import Any, Optional, Union, List, Dict
from datetime import datetime, timedelta
from app.core.redis import redis_manager
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """
    Comprehensive caching service with Redis backend
    """

    def __init__(self):
        self.default_ttl = settings.REDIS_TTL
        self.compression_threshold = 1024  # Compress data larger than 1KB

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate consistent cache keys
        """
        key_parts = [prefix]

        # Add args to key
        for arg in args:
            if isinstance(arg, (str, int, float, bool)):
                key_parts.append(str(arg))
            else:
                # Hash complex objects
                key_parts.append(hashlib.md5(str(arg).encode()).hexdigest())

        # Add kwargs to key
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            for k, v in sorted_kwargs:
                key_parts.append(f"{k}={v}")

        return ":".join(key_parts)

    def _serialize_value(self, value: Any) -> bytes:
        """
        Serialize value for storage with compression for large data
        """
        try:
            data = pickle.dumps(value)
            if len(data) > self.compression_threshold:
                # For large data, use JSON if possible, otherwise compressed pickle
                try:
                    json_data = json.dumps(value).encode('utf-8')
                    if len(json_data) < len(data):
                        return b'json:' + json_data
                except (TypeError, OverflowError):
                    pass
                return b'pickle:' + data
            return b'pickle:' + data
        except (pickle.PicklingError, TypeError) as e:
            logger.warning(f"Failed to serialize value: {e}")
            return b'str:' + str(value).encode('utf-8')

    def _deserialize_value(self, data: bytes) -> Any:
        """
        Deserialize value from storage
        """
        if data.startswith(b'json:'):
            return json.loads(data[5:].decode('utf-8'))
        elif data.startswith(b'pickle:'):
            return pickle.loads(data[7:])
        elif data.startswith(b'str:'):
            return data[4:].decode('utf-8')
        else:
            # Legacy format
            try:
                return pickle.loads(data)
            except:
                return data.decode('utf-8')

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        """
        try:
            data = await redis_manager.get(key)
            if data is None:
                return None
            return self._deserialize_value(data)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        nx: bool = False
    ) -> bool:
        """
        Set value in cache with optional TTL
        """
        try:
            ttl = ttl or self.default_ttl
            data = self._serialize_value(value)
            return await redis_manager.set(key, data, ex=ttl, nx=nx)
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete key from cache
        """
        try:
            return await redis_manager.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache
        """
        try:
            return await redis_manager.exists(key)
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False

    async def expire(self, key: str, ttl: int) -> bool:
        """
        Set expiration time for key
        """
        try:
            return await redis_manager.expire(key, ttl)
        except Exception as e:
            logger.error(f"Cache expire error for key {key}: {e}")
            return False

    async def ttl(self, key: str) -> Optional[int]:
        """
        Get time to live for key
        """
        try:
            return await redis_manager.ttl(key)
        except Exception as e:
            logger.error(f"Cache TTL error for key {key}: {e}")
            return None

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment numeric value in cache
        """
        try:
            return await redis_manager.increment(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return None

    async def hget(self, key: str, field: str) -> Optional[Any]:
        """
        Get hash field value
        """
        try:
            data = await redis_manager.hget(key, field)
            if data is None:
                return None
            return self._deserialize_value(data)
        except Exception as e:
            logger.error(f"Cache hget error for key {key}, field {field}: {e}")
            return None

    async def hset(
        self,
        key: str,
        field: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set hash field value
        """
        try:
            data = self._serialize_value(value)
            result = await redis_manager.hset(key, field, data)
            if ttl:
                await redis_manager.expire(key, ttl)
            return result
        except Exception as e:
            logger.error(f"Cache hset error for key {key}, field {field}: {e}")
            return False

    async def hgetall(self, key: str) -> Dict[str, Any]:
        """
        Get all hash fields and values
        """
        try:
            hash_data = await redis_manager.hgetall(key)
            return {
                field: self._deserialize_value(value)
                for field, value in hash_data.items()
            }
        except Exception as e:
            logger.error(f"Cache hgetall error for key {key}: {e}")
            return {}

    async def hdel(self, key: str, *fields: str) -> int:
        """
        Delete hash fields
        """
        try:
            return await redis_manager.hdel(key, *fields)
        except Exception as e:
            logger.error(f"Cache hdel error for key {key}: {e}")
            return 0

    async def lpush(self, key: str, *values: Any) -> int:
        """
        Push values to list head
        """
        try:
            serialized_values = [self._serialize_value(v) for v in values]
            return await redis_manager.lpush(key, *serialized_values)
        except Exception as e:
            logger.error(f"Cache lpush error for key {key}: {e}")
            return 0

    async def rpush(self, key: str, *values: Any) -> int:
        """
        Push values to list tail
        """
        try:
            serialized_values = [self._serialize_value(v) for v in values]
            return await redis_manager.rpush(key, *serialized_values)
        except Exception as e:
            logger.error(f"Cache rpush error for key {key}: {e}")
            return 0

    async def lpop(self, key: str) -> Optional[Any]:
        """
        Pop value from list head
        """
        try:
            data = await redis_manager.lpop(key)
            if data is None:
                return None
            return self._deserialize_value(data)
        except Exception as e:
            logger.error(f"Cache lpop error for key {key}: {e}")
            return None

    async def rpop(self, key: str) -> Optional[Any]:
        """
        Pop value from list tail
        """
        try:
            data = await redis_manager.rpop(key)
            if data is None:
                return None
            return self._deserialize_value(data)
        except Exception as e:
            logger.error(f"Cache rpop error for key {key}: {e}")
            return None

    async def llen(self, key: str) -> int:
        """
        Get list length
        """
        try:
            return await redis_manager.llen(key)
        except Exception as e:
            logger.error(f"Cache llen error for key {key}: {e}")
            return 0

    async def lrange(self, key: str, start: int = 0, end: int = -1) -> List[Any]:
        """
        Get list range
        """
        try:
            data = await redis_manager.lrange(key, start, end)
            return [self._deserialize_value(item) for item in data]
        except Exception as e:
            logger.error(f"Cache lrange error for key {key}: {e}")
            return []

    async def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching pattern
        """
        try:
            keys = await redis_manager.keys(pattern)
            if keys:
                return await redis_manager.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error for pattern {pattern}: {e}")
            return 0

    async def get_or_set(
        self,
        key: str,
        callback,
        ttl: Optional[int] = None,
        force_refresh: bool = False
    ) -> Any:
        """
        Get value from cache or set using callback if not exists
        """
        if not force_refresh:
            cached_value = await self.get(key)
            if cached_value is not None:
                return cached_value

        try:
            value = await callback()
            await self.set(key, value, ttl=ttl)
            return value
        except Exception as e:
            logger.error(f"Cache get_or_set error for key {key}: {e}")
            raise


# Global cache service instance
cache_service = CacheService()