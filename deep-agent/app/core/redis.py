"""
Redis configuration and connection management.
"""
import json
import redis
from typing import Optional, Union, Any
from .config import settings


class RedisManager:
    """Redis connection and operations manager."""

    def __init__(self):
        self._redis_client: Optional[redis.Redis] = None

    @property
    def client(self) -> redis.Redis:
        """Get Redis client instance."""
        if self._redis_client is None:
            self._redis_client = redis.Redis(**settings.redis_settings)
        return self._redis_client

    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis."""
        try:
            value = self.client.get(key)
            if value is not None:
                return json.loads(value)
            return None
        except (redis.RedisError, json.JSONDecodeError):
            return None

    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set value in Redis with optional expiration."""
        try:
            serialized_value = json.dumps(value, default=str)
            return self.client.set(key, serialized_value, ex=ex)
        except (redis.RedisError, json.JSONEncodeError):
            return False

    def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        try:
            return bool(self.client.delete(key))
        except redis.RedisError:
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            return bool(self.client.exists(key))
        except redis.RedisError:
            return False

    def expire(self, key: str, seconds: int) -> bool:
        """Set expiration time for key."""
        try:
            return bool(self.client.expire(key, seconds))
        except redis.RedisError:
            return False

    def hget(self, name: str, key: str) -> Optional[Any]:
        """Get hash field value."""
        try:
            value = self.client.hget(name, key)
            if value is not None:
                return json.loads(value)
            return None
        except (redis.RedisError, json.JSONDecodeError):
            return None

    def hset(self, name: str, key: str, value: Any) -> bool:
        """Set hash field value."""
        try:
            serialized_value = json.dumps(value, default=str)
            return bool(self.client.hset(name, key, serialized_value))
        except (redis.RedisError, json.JSONEncodeError):
            return False

    def hgetall(self, name: str) -> dict:
        """Get all hash fields and values."""
        try:
            result = self.client.hgetall(name)
            return {k: json.loads(v) for k, v in result.items()}
        except (redis.RedisError, json.JSONDecodeError):
            return {}

    def lpush(self, name: str, *values: Any) -> int:
        """Push values to the left of a list."""
        try:
            serialized_values = [json.dumps(v, default=str) for v in values]
            return self.client.lpush(name, *serialized_values)
        except (redis.RedisError, json.JSONEncodeError):
            return 0

    def rpush(self, name: str, *values: Any) -> int:
        """Push values to the right of a list."""
        try:
            serialized_values = [json.dumps(v, default=str) for v in values]
            return self.client.rpush(name, *serialized_values)
        except (redis.RedisError, json.JSONEncodeError):
            return 0

    def llen(self, name: str) -> int:
        """Get length of list."""
        try:
            return self.client.llen(name)
        except redis.RedisError:
            return 0

    def lrange(self, name: str, start: int = 0, end: int = -1) -> list:
        """Get range of list elements."""
        try:
            result = self.client.lrange(name, start, end)
            return [json.loads(item) for item in result]
        except (redis.RedisError, json.JSONDecodeError):
            return []

    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except redis.RedisError:
            return 0

    def ping(self) -> bool:
        """Ping Redis server."""
        try:
            return self.client.ping()
        except redis.RedisError:
            return False

    def close(self):
        """Close Redis connection."""
        if self._redis_client is not None:
            self._redis_client.close()
            self._redis_client = None


# Global Redis manager instance
redis_manager = RedisManager()


# Convenience functions
def get_redis_connection() -> redis.Redis:
    """Get Redis connection for dependency injection."""
    return redis_manager.client