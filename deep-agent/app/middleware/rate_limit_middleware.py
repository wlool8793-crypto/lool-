from fastapi import Request, Response, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional, Callable, Dict, Any
from app.services.rate_limiter import rate_limiter
from app.services.cache_service import cache_service
from app.core.config import settings
import logging
import time

logger = logging.getLogger(__name__)


async def get_client_identifier(request: Request) -> str:
    """
    Get client identifier for rate limiting
    """
    # Try to get user ID from authentication
    if hasattr(request.state, 'user') and request.state.user:
        return f"user:{request.state.user.id}"

    # Try to get API key
    api_key = request.headers.get('X-API-Key') or request.headers.get('Authorization')
    if api_key:
        return f"api_key:{api_key[:10]}"

    # Fall back to IP address
    client_ip = request.client.host if request.client else "unknown"
    x_forwarded_for = request.headers.get('X-Forwarded-For')

    if x_forwarded_for:
        # Get the first IP from X-Forwarded-For
        client_ip = x_forwarded_for.split(',')[0].strip()

    return f"ip:{client_ip}"


async def rate_limit_middleware(
    request: Request,
    call_next: Callable,
    rule_name: str = "api_general",
    weight: int = 1,
    identifier_generator: Optional[Callable] = None
) -> Response:
    """
    Rate limiting middleware
    """
    try:
        # Get client identifier
        if identifier_generator:
            identifier = await identifier_generator(request)
        else:
            identifier = await get_client_identifier(request)

        # Check rate limit
        result = await rate_limiter.check_rate_limit(
            rule_name=rule_name,
            identifier=identifier,
            weight=weight
        )

        # Add rate limit headers to response
        response = await call_next(request)

        rule = rate_limiter.get_rule(rule_name)
        if rule.headers:
            headers = await rate_limiter.get_rate_limit_headers(result)
            for key, value in headers.items():
                response.headers[key] = value

        # If rate limited, return 429
        if not result['allowed']:
            raise HTTPException(
                status_code=429,
                detail=result['error_message'],
                headers=headers if rule.headers else {}
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rate limiting middleware error: {e}")
        # Continue without rate limiting on error
        return await call_next(request)


class RateLimitMiddleware:
    """
    Rate limiting middleware class for dependency injection
    """

    def __init__(
        self,
        rule_name: str = "api_general",
        weight: int = 1,
        identifier_generator: Optional[Callable] = None
    ):
        self.rule_name = rule_name
        self.weight = weight
        self.identifier_generator = identifier_generator

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        return await rate_limit_middleware(
            request,
            call_next,
            rule_name=self.rule_name,
            weight=self.weight,
            identifier_generator=self.identifier_generator
        )


# Specific middleware instances for different endpoints
auth_rate_limiter = RateLimitMiddleware(rule_name="auth_requests", weight=1)
message_rate_limiter = RateLimitMiddleware(rule_name="message_send", weight=1)
file_upload_rate_limiter = RateLimitMiddleware(rule_name="file_upload", weight=1)
agent_execution_rate_limiter = RateLimitMiddleware(rule_name="agent_execution", weight=1)


async def get_rate_limit_status(
    request: Request,
    rule_name: str = "api_general"
) -> Dict[str, Any]:
    """
    Get current rate limit status for client
    """
    identifier = await get_client_identifier(request)
    return await rate_limiter.get_rate_limit_stats(rule_name, identifier)


# FastAPI dependency for rate limiting
async def rate_limit_dependency(
    request: Request,
    rule_name: str = "api_general",
    weight: int = 1
) -> Dict[str, Any]:
    """
    FastAPI dependency for rate limiting
    """
    identifier = await get_client_identifier(request)

    result = await rate_limiter.check_rate_limit(
        rule_name=rule_name,
        identifier=identifier,
        weight=weight
    )

    if not result['allowed']:
        raise HTTPException(
            status_code=429,
            detail=result['error_message']
        )

    return result


# Common rate limit dependencies
RateLimitGeneral = lambda: rate_limit_dependency(rule_name="api_general")
RateLimitAuth = lambda: rate_limit_dependency(rule_name="auth_requests")
RateLimitMessage = lambda: rate_limit_dependency(rule_name="message_send")
RateLimitFileUpload = lambda: rate_limit_dependency(rule_name="file_upload")
RateLimitAgentExecution = lambda: rate_limit_dependency(rule_name="agent_execution")