import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from app.services.cache_service import cache_service
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class RateLimitType(Enum):
    """Rate limit types"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"


@dataclass
class RateLimitRule:
    """Rate limit rule configuration"""
    limit: int
    window: int  # in seconds
    type: RateLimitType = RateLimitType.FIXED_WINDOW
    key_generator: Optional[str] = None
    error_message: str = "Rate limit exceeded"
    headers: bool = True


class RateLimiter:
    """
    Comprehensive rate limiter with multiple algorithms
    """

    def __init__(self):
        self.rules: Dict[str, RateLimitRule] = {}
        self.default_rule = RateLimitRule(
            limit=100,
            window=3600,  # 1 hour
            type=RateLimitType.FIXED_WINDOW
        )

    def add_rule(
        self,
        name: str,
        limit: int,
        window: int,
        type: RateLimitType = RateLimitType.FIXED_WINDOW,
        key_generator: Optional[str] = None,
        error_message: str = "Rate limit exceeded",
        headers: bool = True
    ):
        """Add a rate limit rule"""
        self.rules[name] = RateLimitRule(
            limit=limit,
            window=window,
            type=type,
            key_generator=key_generator,
            error_message=error_message,
            headers=headers
        )

    def get_rule(self, name: str) -> RateLimitRule:
        """Get rate limit rule"""
        return self.rules.get(name, self.default_rule)

    async def check_rate_limit(
        self,
        rule_name: str,
        identifier: str,
        weight: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Check if request is within rate limit
        Returns: {
            'allowed': bool,
            'remaining': int,
            'reset_time': int,
            'total_limit': int,
            'error_message': Optional[str]
        }
        """
        rule = self.get_rule(rule_name)
        cache_key = f"rate_limit:{rule_name}:{identifier}"

        if rule.type == RateLimitType.FIXED_WINDOW:
            return await self._fixed_window_check(cache_key, rule, weight)
        elif rule.type == RateLimitType.SLIDING_WINDOW:
            return await self._sliding_window_check(cache_key, rule, weight)
        elif rule.type == RateLimitType.TOKEN_BUCKET:
            return await self._token_bucket_check(cache_key, rule, weight)
        elif rule.type == RateLimitType.LEAKY_BUCKET:
            return await self._leaky_bucket_check(cache_key, rule, weight)
        else:
            raise ValueError(f"Unknown rate limit type: {rule.type}")

    async def _fixed_window_check(
        self,
        cache_key: str,
        rule: RateLimitRule,
        weight: int
    ) -> Dict[str, Any]:
        """Fixed window rate limiting"""
        current_time = int(time.time())
        window_start = current_time - (current_time % rule.window)

        # Create unique key for this window
        window_key = f"{cache_key}:{window_start}"

        # Get current count
        current_count = await cache_service.get(window_key) or 0

        # Check if limit exceeded
        if current_count + weight > rule.limit:
            remaining = max(0, rule.limit - current_count)
            reset_time = window_start + rule.window

            return {
                'allowed': False,
                'remaining': remaining,
                'reset_time': reset_time,
                'total_limit': rule.limit,
                'error_message': rule.error_message
            }

        # Increment counter
        new_count = await cache_service.increment(window_key, weight)
        await cache_service.expire(window_key, rule.window)

        return {
            'allowed': True,
            'remaining': max(0, rule.limit - new_count),
            'reset_time': window_start + rule.window,
            'total_limit': rule.limit,
            'error_message': None
        }

    async def _sliding_window_check(
        self,
        cache_key: str,
        rule: RateLimitRule,
        weight: int
    ) -> Dict[str, Any]:
        """Sliding window rate limiting"""
        current_time = time.time()
        window_start = current_time - rule.window

        # Get all timestamps in current window
        timestamps = await cache_service.lrange(cache_key, 0, -1)

        # Remove timestamps outside window
        valid_timestamps = [
            ts for ts in timestamps
            if ts > window_start
        ]

        # Check if limit exceeded
        if len(valid_timestamps) + weight > rule.limit:
            remaining = max(0, rule.limit - len(valid_timestamps))
            reset_time = valid_timestamps[0] + rule.window if valid_timestamps else current_time

            return {
                'allowed': False,
                'remaining': remaining,
                'reset_time': int(reset_time),
                'total_limit': rule.limit,
                'error_message': rule.error_message
            }

        # Add current timestamp
        await cache_service.lpush(cache_key, current_time)
        await cache_service.expire(cache_key, rule.window)

        return {
            'allowed': True,
            'remaining': max(0, rule.limit - len(valid_timestamps) - 1),
            'reset_time': int(current_time + rule.window),
            'total_limit': rule.limit,
            'error_message': None
        }

    async def _token_bucket_check(
        self,
        cache_key: str,
        rule: RateLimitRule,
        weight: int
    ) -> Dict[str, Any]:
        """Token bucket rate limiting"""
        current_time = time.time()

        # Get current bucket state
        bucket_data = await cache_service.get(cache_key) or {
            'tokens': rule.limit,
            'last_refill': current_time
        }

        # Calculate tokens to add
        time_passed = current_time - bucket_data['last_refill']
        tokens_to_add = (time_passed / rule.window) * rule.limit

        # Update tokens
        bucket_data['tokens'] = min(
            rule.limit,
            bucket_data['tokens'] + tokens_to_add
        )
        bucket_data['last_refill'] = current_time

        # Check if enough tokens
        if bucket_data['tokens'] < weight:
            # Calculate when enough tokens will be available
            tokens_needed = weight - bucket_data['tokens']
            wait_time = (tokens_needed / rule.limit) * rule.window

            return {
                'allowed': False,
                'remaining': int(bucket_data['tokens']),
                'reset_time': int(current_time + wait_time),
                'total_limit': rule.limit,
                'error_message': rule.error_message
            }

        # Remove tokens
        bucket_data['tokens'] -= weight

        # Save bucket state
        await cache_service.set(cache_key, bucket_data, ttl=rule.window)

        return {
            'allowed': True,
            'remaining': int(bucket_data['tokens']),
            'reset_time': int(current_time),
            'total_limit': rule.limit,
            'error_message': None
        }

    async def _leaky_bucket_check(
        self,
        cache_key: str,
        rule: RateLimitRule,
        weight: int
    ) -> Dict[str, Any]:
        """Leaky bucket rate limiting"""
        current_time = time.time()

        # Get current bucket state
        bucket_data = await cache_service.get(cache_key) or {
            'current_size': 0,
            'last_leak': current_time
        }

        # Calculate leak
        time_passed = current_time - bucket_data['last_leak']
        leak_rate = rule.limit / rule.window  # tokens per second
        leak_amount = time_passed * leak_rate

        # Update bucket size
        bucket_data['current_size'] = max(
            0,
            bucket_data['current_size'] - leak_amount
        )
        bucket_data['last_leak'] = current_time

        # Check if bucket has capacity
        if bucket_data['current_size'] + weight > rule.limit:
            # Calculate when bucket will have capacity
            overflow = (bucket_data['current_size'] + weight) - rule.limit
            wait_time = overflow / leak_rate

            return {
                'allowed': False,
                'remaining': int(rule.limit - bucket_data['current_size']),
                'reset_time': int(current_time + wait_time),
                'total_limit': rule.limit,
                'error_message': rule.error_message
            }

        # Add to bucket
        bucket_data['current_size'] += weight

        # Save bucket state
        await cache_service.set(cache_key, bucket_data, ttl=rule.window)

        return {
            'allowed': True,
            'remaining': int(rule.limit - bucket_data['current_size']),
            'reset_time': int(current_time),
            'total_limit': rule.limit,
            'error_message': None
        }

    async def get_rate_limit_headers(
        self,
        result: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate rate limit headers"""
        return {
            'X-RateLimit-Limit': str(result['total_limit']),
            'X-RateLimit-Remaining': str(result['remaining']),
            'X-RateLimit-Reset': str(result['reset_time']),
        }

    async def reset_rate_limit(self, rule_name: str, identifier: str):
        """Reset rate limit for identifier"""
        cache_key = f"rate_limit:{rule_name}:{identifier}"
        await cache_service.delete(cache_key)

    async def get_rate_limit_stats(
        self,
        rule_name: str,
        identifier: str
    ) -> Dict[str, Any]:
        """Get current rate limit statistics"""
        rule = self.get_rule(rule_name)
        cache_key = f"rate_limit:{rule_name}:{identifier}"

        current_time = time.time()
        window_start = current_time - (current_time % rule.window)
        window_key = f"{cache_key}:{window_start}"

        current_count = await cache_service.get(window_key) or 0

        return {
            'rule': rule_name,
            'identifier': identifier,
            'current_count': current_count,
            'limit': rule.limit,
            'window': rule.window,
            'remaining': max(0, rule.limit - current_count),
            'reset_time': window_start + rule.window,
            'type': rule.type.value
        }


# Global rate limiter instance
rate_limiter = RateLimiter()

# Add default rules
rate_limiter.add_rule(
    name="api_general",
    limit=1000,
    window=3600,  # 1 hour
    type=RateLimitType.FIXED_WINDOW
)

rate_limiter.add_rule(
    name="auth_requests",
    limit=5,
    window=300,  # 5 minutes
    type=RateLimitType.FIXED_WINDOW,
    error_message="Too many authentication attempts. Please try again later."
)

rate_limiter.add_rule(
    name="message_send",
    limit=100,
    window=3600,  # 1 hour
    type=RateLimitType.SLIDING_WINDOW,
    error_message="Message limit exceeded. Please wait before sending more messages."
)

rate_limiter.add_rule(
    name="file_upload",
    limit=10,
    window=3600,  # 1 hour
    type=RateLimitType.TOKEN_BUCKET,
    error_message="File upload limit exceeded. Please wait before uploading more files."
)

rate_limiter.add_rule(
    name="agent_execution",
    limit=50,
    window=3600,  # 1 hour
    type=RateLimitType.LEAKY_BUCKET,
    error_message="Agent execution limit exceeded. Please wait before running more agents."
)