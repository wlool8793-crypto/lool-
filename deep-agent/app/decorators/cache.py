import functools
import inspect
from typing import Any, Optional, Union, Callable, List, Dict
from datetime import timedelta
from app.services.cache_service import cache_service
import logging

logger = logging.getLogger(__name__)


def cache(
    ttl: Optional[int] = None,
    key_prefix: str = "",
    ignore_args: Optional[List[str]] = None,
    condition: Optional[Callable] = None,
    force_refresh: bool = False
):
    """
    Cache decorator for functions and methods
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Check cache condition
            if condition and not condition(*args, **kwargs):
                return await func(*args, **kwargs)

            # Generate cache key
            cache_key = _generate_cache_key(
                func, key_prefix, args, kwargs, ignore_args
            )

            # Get from cache or call function
            return await cache_service.get_or_set(
                cache_key,
                lambda: func(*args, **kwargs),
                ttl=ttl,
                force_refresh=force_refresh
            )

        return wrapper
    return decorator


def cache_result(
    ttl: Optional[int] = None,
    key_prefix: str = "",
    ignore_args: Optional[List[str]] = None
):
    """
    Cache function result with custom key generation
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = _generate_cache_key(
                func, key_prefix, args, kwargs, ignore_args
            )

            cached_result = await cache_service.get(cache_key)
            if cached_result is not None:
                return cached_result

            result = await func(*args, **kwargs)
            await cache_service.set(cache_key, result, ttl=ttl)
            return result

        return wrapper
    return decorator


def cache_invalidate(
    pattern: Optional[str] = None,
    key_prefix: Optional[str] = None,
    args_to_key: Optional[Callable] = None
):
    """
    Invalidate cache entries when function is called
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)

            # Invalidate cache
            if pattern:
                await cache_service.clear_pattern(pattern)
            elif key_prefix:
                if args_to_key:
                    cache_key = args_to_key(*args, **kwargs)
                    await cache_service.delete(cache_key)
                else:
                    await cache_service.clear_pattern(f"{key_prefix}*")

            return result

        return wrapper
    return decorator


def cache_by_user(
    ttl: Optional[int] = None,
    key_prefix: str = "",
    user_arg: str = "user_id"
):
    """
    Cache data per user
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Get user ID from args or kwargs
            user_id = None

            # Check in kwargs
            if user_arg in kwargs:
                user_id = kwargs[user_arg]
            else:
                # Check in args (get function signature)
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()

                if user_arg in bound_args.arguments:
                    user_id = bound_args.arguments[user_arg]

            if user_id is None:
                return await func(*args, **kwargs)

            # Generate cache key with user ID
            cache_key = f"{key_prefix}user:{user_id}:{func.__name__}"

            # Add other args to key
            other_args = {
                k: v for k, v in kwargs.items()
                if k != user_arg
            }

            if other_args:
                import hashlib
                args_hash = hashlib.md5(
                    str(sorted(other_args.items())).encode()
                ).hexdigest()
                cache_key += f":{args_hash}"

            return await cache_service.get_or_set(
                cache_key,
                lambda: func(*args, **kwargs),
                ttl=ttl
            )

        return wrapper
    return decorator


def cache_list(
    ttl: Optional[int] = None,
    key_prefix: str = "",
    list_key: str = None
):
    """
    Cache and manage lists with automatic updates
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if list_key:
                # Try to get from cache
                cached_list = await cache_service.get(list_key)
                if cached_list is not None:
                    return cached_list

            # Get fresh data
            result = await func(*args, **kwargs)

            # Cache the result
            if list_key:
                await cache_service.set(list_key, result, ttl=ttl)

            return result

        return wrapper
    return decorator


def cache_hash(
    ttl: Optional[int] = None,
    key_prefix: str = "",
    field_generator: Optional[Callable] = None
):
    """
    Cache data in Redis hashes
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate hash key and field
            hash_key = key_prefix or f"hash:{func.__name__}"

            if field_generator:
                field = field_generator(*args, **kwargs)
            else:
                import hashlib
                field = hashlib.md5(
                    str(args + tuple(sorted(kwargs.items()))).encode()
                ).hexdigest()

            # Try to get from hash
            cached_value = await cache_service.hget(hash_key, field)
            if cached_value is not None:
                return cached_value

            # Get fresh data
            result = await func(*args, **kwargs)

            # Cache in hash
            await cache_service.hset(hash_key, field, result, ttl=ttl)

            return result

        return wrapper
    return decorator


def rate_limit(
    limit: int,
    window: Union[int, timedelta],
    key_generator: Optional[Callable] = None,
    error_message: str = "Rate limit exceeded"
):
    """
    Rate limiting decorator
    """
    if isinstance(window, timedelta):
        window_seconds = window.total_seconds()
    else:
        window_seconds = window

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate rate limit key
            if key_generator:
                rate_key = key_generator(*args, **kwargs)
            else:
                import hashlib
                rate_key = f"rate_limit:{func.__name__}:{hashlib.md5(str(args + tuple(sorted(kwargs.items()))).encode()).hexdigest()}"

            # Check current count
            current_count = await cache_service.get(rate_key) or 0

            if current_count >= limit:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=429,
                    detail=error_message
                )

            # Increment counter
            await cache_service.increment(rate_key)
            await cache_service.expire(rate_key, int(window_seconds))

            return await func(*args, **kwargs)

        return wrapper
    return decorator


def memoize(max_size: int = 1000, ttl: Optional[int] = None):
    """
    Memoization decorator with size limit
    """
    def decorator(func: Callable) -> Callable:
        cache_data = {}
        access_order = []

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            key = str(args) + str(sorted(kwargs.items()))

            # Check cache
            if key in cache_data:
                # Move to end of access order
                access_order.remove(key)
                access_order.append(key)
                return cache_data[key]

            # Call function
            result = await func(*args, **kwargs)

            # Add to cache
            cache_data[key] = result
            access_order.append(key)

            # Remove oldest if over size limit
            if len(cache_data) > max_size:
                oldest_key = access_order.pop(0)
                del cache_data[oldest_key]

            # Set TTL if specified
            if ttl:
                import asyncio
                asyncio.create_task(_remove_after_ttl(key, ttl))

            return result

        return wrapper
    return decorator


async def _remove_after_ttl(key: str, ttl: int):
    """
    Helper function to remove memoized item after TTL
    """
    import asyncio
    await asyncio.sleep(ttl)
    # This is a simplified version - in practice, you'd need
    # to handle the cache_data and access_order properly


def _generate_cache_key(
    func: Callable,
    prefix: str,
    args: tuple,
    kwargs: dict,
    ignore_args: Optional[List[str]] = None
) -> str:
    """
    Generate cache key for function call
    """
    import hashlib

    # Start with function name and prefix
    key_parts = [prefix, func.__name__]

    # Process args (skip self for methods)
    if args and inspect.ismethod(func):
        args = args[1:]  # Skip self

    # Add relevant args
    for i, arg in enumerate(args):
        if ignore_args and str(i) in ignore_args:
            continue
        key_parts.append(str(arg))

    # Add relevant kwargs
    if kwargs:
        filtered_kwargs = {
            k: v for k, v in kwargs.items()
            if not ignore_args or k not in ignore_args
        }
        if filtered_kwargs:
            key_parts.append(str(sorted(filtered_kwargs.items())))

    # Generate final key
    key_string = ":".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()[:32]