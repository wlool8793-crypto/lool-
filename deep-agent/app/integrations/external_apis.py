import asyncio
import json
import uuid
import base64
import hashlib
import hmac
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
import aiohttp
import requests
from urllib.parse import urlencode, quote, urlparse, parse_qs
import pandas as pd
import numpy as np
from app.services.cache_service import cache_service
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class APIProvider(Enum):
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    GITHUB = "github"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    AWS = "aws"
    SLACK = "slack"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    STRIPE = "stripe"
    PAYPAL = "paypal"
    SHOPIFY = "shopify"
    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"
    MAILCHIMP = "mailchimp"
    SENDGRID = "sendgrid"
    TWILIO = "twilio"
    OPEN_WEATHER = "open_weather"
    NEWS_API = "news_api"
    ALPHA_VANTAGE = "alpha_vantage"
    COINBASE = "coinbase"
    BINANCE = "binance"


class APIAuthType(Enum):
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"
    WEBHOOK_SECRET = "webhook_secret"
    SIGNATURE = "signature"


class APIRequestType(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class ExternalAPIManager:
    """Advanced external API integration manager"""

    def __init__(self):
        self.api_configs = {}
        self.active_sessions = {}
        self.webhook_handlers = {}
        self.rate_limiters = {}
        self.request_history = {}
        self.webhook_signatures = {}

        # Initialize API configurations
        self._initialize_api_configs()

    def _initialize_api_configs(self):
        """Initialize API configurations"""
        # Social Media APIs
        self.api_configs[APIProvider.TWITTER] = {
            "base_url": "https://api.twitter.com/2",
            "auth_type": APIAuthType.BEARER_TOKEN,
            "rate_limit": {
                "requests_per_minute": 300,
                "requests_per_hour": 15000
            },
            "scopes": ["tweet.read", "tweet.write", "users.read", "follows.read"]
        }

        self.api_configs[APIProvider.FACEBOOK] = {
            "base_url": "https://graph.facebook.com/v18.0",
            "auth_type": APIAuthType.OAUTH2,
            "rate_limit": {
                "requests_per_hour": 200
            },
            "scopes": ["public_profile", "email", "pages_read_engagement"]
        }

        self.api_configs[APIProvider.LINKEDIN] = {
            "base_url": "https://api.linkedin.com/v2",
            "auth_type": APIAuthType.OAUTH2,
            "rate_limit": {
                "requests_per_hour": 500
            },
            "scopes": ["r_liteprofile", "r_emailaddress", "w_member_social"]
        }

        # Development Platforms
        self.api_configs[APIProvider.GITHUB] = {
            "base_url": "https://api.github.com",
            "auth_type": APIAuthType.API_KEY,
            "rate_limit": {
                "requests_per_hour": 5000
            }
        }

        # Cloud Services
        self.api_configs[APIProvider.AWS] = {
            "base_url": "https://sts.amazonaws.com",
            "auth_type": APIAuthType.SIGNATURE,
            "rate_limit": {
                "requests_per_second": 100
            }
        }

        self.api_configs[APIProvider.MICROSOFT] = {
            "base_url": "https://graph.microsoft.com/v1.0",
            "auth_type": APIAuthType.OAUTH2,
            "rate_limit": {
                "requests_per_minute": 10000
            }
        }

        # Communication Platforms
        self.api_configs[APIProvider.SLACK] = {
            "base_url": "https://slack.com/api",
            "auth_type": APIAuthType.OAUTH2,
            "rate_limit": {
                "requests_per_minute": 100
            }
        }

        self.api_configs[APIProvider.DISCORD] = {
            "base_url": "https://discord.com/api/v10",
            "auth_type": APIAuthType.BEARER_TOKEN,
            "rate_limit": {
                "requests_per_minute": 120
            }
        }

        # Payment Services
        self.api_configs[APIProvider.STRIPE] = {
            "base_url": "https://api.stripe.com/v1",
            "auth_type": APIAuthType.API_KEY,
            "rate_limit": {
                "requests_per_second": 100
            }
        }

        self.api_configs[APIProvider.PAYPAL] = {
            "base_url": "https://api-m.paypal.com/v2",
            "auth_type": APIAuthType.OAUTH2,
            "rate_limit": {
                "requests_per_hour": 1000
            }
        }

        # E-commerce
        self.api_configs[APIProvider.SHOPIFY] = {
            "base_url": "https://{shop}.myshopify.com/admin/api/2023-10",
            "auth_type": APIAuthType.API_KEY,
            "rate_limit": {
                "requests_per_minute": 40
            }
        }

        # CRM & Marketing
        self.api_configs[APIProvider.SALESFORCE] = {
            "base_url": "https://{instance}.my.salesforce.com/services/data/v57.0",
            "auth_type": APIAuthType.OAUTH2,
            "rate_limit": {
                "requests_per_day": 15000
            }
        }

        self.api_configs[APIProvider.HUBSPOT] = {
            "base_url": "https://api.hubapi.com",
            "auth_type": APIAuthType.API_KEY,
            "rate_limit": {
                "requests_per_second": 10
            }
        }

        self.api_configs[APIProvider.MAILCHIMP] = {
            "base_url": "https://{dc}.api.mailchimp.com/3.0",
            "auth_type": APIAuthType.API_KEY,
            "rate_limit": {
                "requests_per_second": 10
            }
        }

        # Communication Services
        self.api_configs[APIProvider.SENDGRID] = {
            "base_url": "https://api.sendgrid.com/v3",
            "auth_type": APIAuthType.API_KEY,
            "rate_limit": {
                "requests_per_second": 100
            }
        }

        self.api_configs[APIProvider.TWILIO] = {
            "base_url": "https://api.twilio.com/2010-04-01/Accounts/{account_sid}",
            "auth_type": APIAuthType.API_KEY,
            "rate_limit": {
                "requests_per_second": 1
            }
        }

        # Data & Weather APIs
        self.api_configs[APIProvider.OPEN_WEATHER] = {
            "base_url": "https://api.openweathermap.org/data/2.5",
            "auth_type": APIAuthType.API_KEY,
            "rate_limit": {
                "requests_per_minute": 60,
                "requests_per_day": 1000
            }
        }

        self.api_configs[APIProvider.NEWS_API] = {
            "base_url": "https://newsapi.org/v2",
            "auth_type": APIAuthType.API_KEY,
            "rate_limit": {
                "requests_per_hour": 100,
                "requests_per_day": 1000
            }
        }

        self.api_configs[APIProvider.ALPHA_VANTAGE] = {
            "base_url": "https://www.alphavantage.co/query",
            "auth_type": APIAuthType.API_KEY,
            "rate_limit": {
                "requests_per_minute": 5,
                "requests_per_day": 500
            }
        }

        # Cryptocurrency
        self.api_configs[APIProvider.COINBASE] = {
            "base_url": "https://api.coinbase.com/v2",
            "auth_type": APIAuthType.API_KEY,
            "rate_limit": {
                "requests_per_minute": 10
            }
        }

        self.api_configs[APIProvider.BINANCE] = {
            "base_url": "https://api.binance.com/api/v3",
            "auth_type": APIAuthType.API_KEY,
            "rate_limit": {
                "requests_per_minute": 1200,
                "requests_per_second": 10
            }
        }

    async def configure_api(
        self,
        provider: APIProvider,
        credentials: Dict[str, str],
        webhook_secret: Optional[str] = None,
        custom_settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Configure API provider with credentials"""
        try:
            if provider not in self.api_configs:
                return {
                    "success": False,
                    "error": f"Unsupported API provider: {provider.value}"
                }

            config = self.api_configs[provider].copy()
            config.update({
                "credentials": credentials,
                "configured_at": datetime.utcnow().isoformat(),
                "custom_settings": custom_settings or {}
            })

            # Validate credentials
            validation_result = await self._validate_credentials(provider, credentials)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"]
                }

            # Store webhook secret if provided
            if webhook_secret:
                self.webhook_signatures[provider] = webhook_secret

            # Store configuration
            session_id = str(uuid.uuid4())
            self.active_sessions[session_id] = config

            # Initialize rate limiter
            self.rate_limiters[session_id] = {
                "requests": [],
                "limits": config["rate_limit"]
            }

            return {
                "success": True,
                "session_id": session_id,
                "provider": provider.value,
                "configured_at": config["configured_at"]
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"API configuration error: {str(e)}"
            }

    async def make_api_request(
        self,
        session_id: str,
        endpoint: str,
        method: APIRequestType = APIRequestType.GET,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Make authenticated API request"""
        try:
            # Get session configuration
            session_config = self.active_sessions.get(session_id)
            if not session_config:
                return {
                    "success": False,
                    "error": "Invalid session ID"
                }

            # Check rate limits
            rate_check = await self._check_rate_limit(session_id)
            if not rate_check["allowed"]:
                return {
                    "success": False,
                    "error": rate_check["error"]
                }

            # Build request URL
            base_url = session_config["base_url"]
            url = self._build_url(base_url, endpoint, session_config.get("custom_settings", {}))

            # Prepare headers
            request_headers = await self._prepare_headers(session_config, headers)

            # Make request
            start_time = datetime.utcnow()
            result = await self._execute_request(
                url, method, params, data, request_headers, timeout
            )

            # Record request
            await self._record_request(session_id, url, method, result, start_time)

            return result

        except Exception as e:
            logger.error(f"API request error: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def setup_webhook(
        self,
        session_id: str,
        webhook_url: str,
        events: List[str],
        handler_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Setup webhook for API provider"""
        try:
            session_config = self.active_sessions.get(session_id)
            if not session_config:
                return {
                    "success": False,
                    "error": "Invalid session ID"
                }

            provider_name = session_config.get("provider_name")
            if not provider_name:
                return {
                    "success": False,
                    "error": "Provider not configured in session"
                }

            # Generate webhook ID
            webhook_id = str(uuid.uuid4())

            # Store webhook configuration
            self.webhook_handlers[webhook_id] = {
                "session_id": session_id,
                "provider": provider_name,
                "webhook_url": webhook_url,
                "events": events,
                "handler_callback": handler_callback,
                "created_at": datetime.utcnow().isoformat(),
                "active": True
            }

            # Register webhook with provider (implementation varies by provider)
            registration_result = await self._register_webhook_with_provider(
                session_id, webhook_url, events
            )

            return {
                "success": True,
                "webhook_id": webhook_id,
                "webhook_url": webhook_url,
                "events": events,
                "registration_result": registration_result
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Webhook setup error: {str(e)}"
            }

    async def handle_webhook(
        self,
        webhook_id: str,
        payload: Dict[str, Any],
        headers: Dict[str, str],
        signature: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handle incoming webhook"""
        try:
            webhook_config = self.webhook_handlers.get(webhook_id)
            if not webhook_config:
                return {
                    "success": False,
                    "error": "Invalid webhook ID"
                }

            # Verify signature if required
            if signature and webhook_config["provider"] in self.webhook_signatures:
                verification_result = await self._verify_webhook_signature(
                    webhook_config["provider"], payload, signature, headers
                )
                if not verification_result["valid"]:
                    return {
                        "success": False,
                        "error": "Invalid webhook signature"
                    }

            # Process webhook payload
            processing_result = await self._process_webhook_payload(
                webhook_config, payload, headers
            )

            return {
                "success": True,
                "webhook_id": webhook_id,
                "processing_result": processing_result,
                "processed_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Webhook handling error: {str(e)}"
            }

    async def batch_api_requests(
        self,
        session_id: str,
        requests: List[Dict[str, Any]],
        max_concurrent: int = 5
    ) -> Dict[str, Any]:
        """Execute batch API requests"""
        try:
            session_config = self.active_sessions.get(session_id)
            if not session_config:
                return {
                    "success": False,
                    "error": "Invalid session ID"
                }

            # Check rate limits for batch
            rate_check = await self._check_rate_limit(session_id, len(requests))
            if not rate_check["allowed"]:
                return {
                    "success": False,
                    "error": rate_check["error"]
                }

            # Execute requests concurrently
            semaphore = asyncio.Semaphore(max_concurrent)

            async def execute_single_request(request_data):
                async with semaphore:
                    return await self.make_api_request(
                        session_id=session_id,
                        endpoint=request_data["endpoint"],
                        method=APIRequestType(request_data.get("method", "GET")),
                        params=request_data.get("params"),
                        data=request_data.get("data"),
                        headers=request_data.get("headers"),
                        timeout=request_data.get("timeout", 30)
                    )

            # Execute all requests
            tasks = [execute_single_request(req) for req in requests]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            successful_requests = []
            failed_requests = []

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failed_requests.append({
                        "request_index": i,
                        "error": str(result)
                    })
                elif not result.get("success"):
                    failed_requests.append({
                        "request_index": i,
                        "error": result.get("error", "Unknown error")
                    })
                else:
                    successful_requests.append({
                        "request_index": i,
                        "result": result
                    })

            return {
                "success": True,
                "total_requests": len(requests),
                "successful_requests": len(successful_requests),
                "failed_requests": len(failed_requests),
                "results": results,
                "success_rate": (len(successful_requests) / len(requests)) * 100
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Batch request error: {str(e)}"
            }

    async def get_api_usage_stats(self, session_id: str) -> Dict[str, Any]:
        """Get API usage statistics"""
        try:
            session_config = self.active_sessions.get(session_id)
            if not session_config:
                return {
                    "success": False,
                    "error": "Invalid session ID"
                }

            rate_limiter = self.rate_limiters.get(session_id, {})
            request_history = self.request_history.get(session_id, [])

            # Calculate usage statistics
            total_requests = len(request_history)
            successful_requests = sum(1 for req in request_history if req.get("success"))
            failed_requests = total_requests - successful_requests

            # Calculate average response time
            response_times = [req.get("execution_time", 0) for req in request_history]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0

            # Get rate limit status
            current_rate_limit = rate_limiter.get("limits", {})
            current_usage = len(rate_limiter.get("requests", []))

            return {
                "success": True,
                "usage_stats": {
                    "total_requests": total_requests,
                    "successful_requests": successful_requests,
                    "failed_requests": failed_requests,
                    "success_rate": (successful_requests / total_requests * 100) if total_requests > 0 else 0,
                    "average_response_time": avg_response_time,
                    "current_rate_limit_usage": current_usage,
                    "rate_limit": current_rate_limit
                },
                "recent_activity": request_history[-10:]  # Last 10 requests
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Usage stats error: {str(e)}"
            }

    # Helper methods
    async def _validate_credentials(self, provider: APIProvider, credentials: Dict[str, str]) -> Dict[str, bool]:
        """Validate API credentials"""
        try:
            if provider == APIProvider.GITHUB:
                # Validate GitHub token
                async with aiohttp.ClientSession() as session:
                    headers = {"Authorization": f"token {credentials.get('token')}"}
                    async with session.get("https://api.github.com/user", headers=headers) as response:
                        return {"valid": response.status == 200}

            elif provider == APIProvider.STRIPE:
                # Validate Stripe API key
                import stripe
                stripe.api_key = credentials.get('api_key')
                try:
                    stripe.Balance.retrieve()
                    return {"valid": True}
                except Exception:
                    return {"valid": False, "error": "Invalid Stripe API key"}

            elif provider == APIProvider.OPEN_WEATHER:
                # Validate OpenWeather API key
                async with aiohttp.ClientSession() as session:
                    params = {"q": "London", "appid": credentials.get('api_key')}
                    async with session.get("https://api.openweathermap.org/data/2.5/weather", params=params) as response:
                        return {"valid": response.status == 200}

            # For other providers, assume valid if credentials are provided
            return {"valid": True}

        except Exception as e:
            return {"valid": False, "error": str(e)}

    def _build_url(self, base_url: str, endpoint: str, custom_settings: Dict[str, Any]) -> str:
        """Build full API URL"""
        # Replace template variables
        for key, value in custom_settings.items():
            base_url = base_url.replace(f"{{{key}}}", str(value))

        # Combine base URL with endpoint
        if endpoint.startswith('/'):
            return base_url + endpoint
        else:
            return base_url + '/' + endpoint

    async def _prepare_headers(self, session_config: Dict[str, Any], custom_headers: Optional[Dict[str, str]]) -> Dict[str, str]:
        """Prepare request headers with authentication"""
        headers = custom_headers or {}
        auth_type = session_config["auth_type"]
        credentials = session_config["credentials"]

        if auth_type == APIAuthType.API_KEY:
            api_key = credentials.get("api_key")
            if session_config.get("provider_name") == "GitHub":
                headers["Authorization"] = f"token {api_key}"
            elif session_config.get("provider_name") == "Stripe":
                headers["Authorization"] = f"Bearer {api_key}"
            else:
                headers["X-API-Key"] = api_key

        elif auth_type == APIAuthType.BEARER_TOKEN:
            token = credentials.get("access_token")
            headers["Authorization"] = f"Bearer {token}"

        elif auth_type == APIAuthType.OAUTH2:
            # OAuth2 implementation would include token refresh logic
            token = credentials.get("access_token")
            headers["Authorization"] = f"Bearer {token}"

        elif auth_type == APIAuthType.BASIC_AUTH:
            import base64
            username = credentials.get("username")
            password = credentials.get("password")
            auth_string = base64.b64encode(f"{username}:{password}".encode()).decode()
            headers["Authorization"] = f"Basic {auth_string}"

        # Add common headers
        headers["Content-Type"] = "application/json"
        headers["User-Agent"] = "Deep-Agent/1.0"

        return headers

    async def _execute_request(
        self,
        url: str,
        method: APIRequestType,
        params: Optional[Dict[str, Any]],
        data: Optional[Dict[str, Any]],
        headers: Dict[str, str],
        timeout: int
    ) -> Dict[str, Any]:
        """Execute HTTP request"""
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method.value,
                url,
                params=params,
                json=data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:

                response_data = await response.text()

                try:
                    json_response = json.loads(response_data)
                except json.JSONDecodeError:
                    json_response = response_data

                return {
                    "success": response.status < 400,
                    "status_code": response.status,
                    "data": json_response,
                    "headers": dict(response.headers),
                    "timestamp": datetime.utcnow().isoformat()
                }

    async def _check_rate_limit(self, session_id: str, request_count: int = 1) -> Dict[str, Any]:
        """Check if request is allowed by rate limits"""
        rate_limiter = self.rate_limiters.get(session_id)
        if not rate_limiter:
            return {"allowed": True}

        limits = rate_limiter["limits"]
        requests = rate_limiter["requests"]

        # Clean old requests (older than 1 minute)
        current_time = datetime.utcnow()
        recent_requests = [
            req_time for req_time in requests
            if (current_time - req_time).total_seconds() < 60
        ]

        rate_limiter["requests"] = recent_requests

        # Check limits
        if len(recent_requests) + request_count > limits.get("requests_per_minute", float('inf')):
            return {
                "allowed": False,
                "error": "Rate limit exceeded (per minute)"
            }

        # Check hourly limit
        hourly_requests = [
            req_time for req_time in requests
            if (current_time - req_time).total_seconds() < 3600
        ]

        if len(hourly_requests) + request_count > limits.get("requests_per_hour", float('inf')):
            return {
                "allowed": False,
                "error": "Rate limit exceeded (per hour)"
            }

        return {"allowed": True}

    async def _record_request(
        self,
        session_id: str,
        url: str,
        method: APIRequestType,
        result: Dict[str, Any],
        start_time: datetime
    ):
        """Record API request for analytics"""
        execution_time = (datetime.utcnow() - start_time).total_seconds()

        request_record = {
            "url": url,
            "method": method.value,
            "success": result.get("success", False),
            "status_code": result.get("status_code"),
            "execution_time": execution_time,
            "timestamp": start_time.isoformat()
        }

        # Add to request history
        if session_id not in self.request_history:
            self.request_history[session_id] = []

        self.request_history[session_id].append(request_record)

        # Keep only last 1000 requests
        if len(self.request_history[session_id]) > 1000:
            self.request_history[session_id] = self.request_history[session_id][-1000:]

        # Add to rate limiter
        if session_id in self.rate_limiters:
            self.rate_limiters[session_id]["requests"].append(start_time)

    async def _register_webhook_with_provider(
        self,
        session_id: str,
        webhook_url: str,
        events: List[str]
    ) -> Dict[str, Any]:
        """Register webhook with the API provider"""
        # Implementation varies by provider
        # This is a simplified version - production would need provider-specific implementations

        session_config = self.active_sessions.get(session_id)
        provider_name = session_config.get("provider_name")

        if provider_name == "github":
            # GitHub webhook registration
            registration_data = {
                "name": "web",
                "active": True,
                "events": events,
                "config": {
                    "url": webhook_url,
                    "content_type": "json"
                }
            }

            result = await self.make_api_request(
                session_id,
                "/repos/{owner}/{repo}/hooks",
                APIRequestType.POST,
                data=registration_data
            )

            return result

        elif provider_name == "stripe":
            # Stripe webhook endpoint creation
            # This would typically be done through Stripe dashboard
            return {"success": True, "message": "Webhook configured manually"}

        return {"success": True, "message": "Webhook registration simulated"}

    async def _verify_webhook_signature(
        self,
        provider: str,
        payload: Dict[str, Any],
        signature: str,
        headers: Dict[str, str]
    ) -> Dict[str, bool]:
        """Verify webhook signature"""
        try:
            secret = self.webhook_signatures.get(provider)
            if not secret:
                return {"valid": False, "error": "No signature secret configured"}

            payload_str = json.dumps(payload, sort_keys=True)

            if provider == "github":
                # GitHub webhook signature verification
                expected_signature = headers.get("X-Hub-Signature-256")
                if expected_signature:
                    signature = expected_signature.replace("sha256=", "")
                    computed_signature = hmac.new(
                        secret.encode(),
                        payload_str.encode(),
                        hashlib.sha256
                    ).hexdigest()
                    return {"valid": hmac.compare_digest(computed_signature, signature)}

            elif provider == "stripe":
                # Stripe webhook signature verification
                timestamp = headers.get("Stripe-Signature", "").split(",")[0].split("=")[1]
                signed_payload = f"{timestamp}.{payload_str}"
                expected_signature = headers.get("Stripe-Signature", "").split(",")[1].split("=")[1]
                computed_signature = hmac.new(
                    secret.encode(),
                    signed_payload.encode(),
                    hashlib.sha256
                ).hexdigest()
                return {"valid": hmac.compare_digest(computed_signature, expected_signature)}

            return {"valid": False, "error": "Unsupported provider for signature verification"}

        except Exception as e:
            return {"valid": False, "error": str(e)}

    async def _process_webhook_payload(
        self,
        webhook_config: Dict[str, Any],
        payload: Dict[str, Any],
        headers: Dict[str, str]
    ) -> Dict[str, Any]:
        """Process webhook payload"""
        try:
            # Extract event type
            event_type = headers.get("X-GitHub-Event") or headers.get("Stripe-Event") or "unknown"

            # Basic payload processing
            processed_data = {
                "event_type": event_type,
                "provider": webhook_config["provider"],
                "received_at": datetime.utcnow().isoformat(),
                "payload_summary": self._summarize_payload(payload)
            }

            # Call custom handler if provided
            if webhook_config.get("handler_callback"):
                try:
                    custom_result = webhook_config["handler_callback"](payload, headers)
                    processed_data["custom_handler_result"] = custom_result
                except Exception as e:
                    processed_data["handler_error"] = str(e)

            return processed_data

        except Exception as e:
            return {"error": str(e)}

    def _summarize_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of webhook payload"""
        summary = {}

        # Extract common fields
        if "action" in payload:
            summary["action"] = payload["action"]
        if "type" in payload:
            summary["type"] = payload["type"]
        if "repository" in payload:
            summary["repository"] = payload["repository"].get("full_name")
        if "user" in payload:
            summary["user"] = payload["user"].get("login")

        return summary

    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get list of available API providers"""
        providers = []
        for provider, config in self.api_configs.items():
            providers.append({
                "name": provider.value,
                "auth_type": config["auth_type"].value,
                "base_url": config["base_url"],
                "rate_limit": config["rate_limit"]
            })
        return providers

    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get list of active API sessions"""
        sessions = []
        for session_id, config in self.active_sessions.items():
            sessions.append({
                "session_id": session_id,
                "provider": config.get("provider_name"),
                "configured_at": config.get("configured_at"),
                "rate_limit": config.get("rate_limit", {})
            })
        return sessions


# Global instance
external_api_manager = ExternalAPIManager()