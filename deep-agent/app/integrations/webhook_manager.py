"""
Webhook Management System for LangGraph Deep Web Agent

This module provides comprehensive webhook management capabilities including
webhook creation, handling, validation, and monitoring for all integrated services.
"""

import asyncio
import json
import logging
import hmac
import hashlib
import base64
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import asyncpg
import redis.asyncio as redis
from urllib.parse import urlparse, parse_qs

from app.core.config import settings
from app.database.redis import RedisManager
from app.integrations.external_apis import ExternalAPIManager
from app.integrations.social_media import SocialMediaManager
from app.integrations.payment_services import PaymentServiceManager
from app.integrations.cloud_services import CloudIntegrationManager

logger = logging.getLogger(__name__)

class WebhookEventType(Enum):
    PAYMENT_SUCCESS = "payment.success"
    PAYMENT_FAILED = "payment.failed"
    PAYMENT_REFUNDED = "payment.refunded"
    SUBSCRIPTION_CREATED = "subscription.created"
    SUBSCRIPTION_CANCELLED = "subscription.cancelled"
    CUSTOMER_CREATED = "customer.created"
    CUSTOMER_UPDATED = "customer.updated"
    SOCIAL_POST_CREATED = "social.post.created"
    SOCIAL_POST_UPDATED = "social.post.updated"
    CLOUD_RESOURCE_CREATED = "cloud.resource.created"
    CLOUD_RESOURCE_UPDATED = "cloud.resource.updated"
    CLOUD_RESOURCE_DELETED = "cloud.resource.deleted"
    API_CALL_SUCCESS = "api.call.success"
    API_CALL_FAILED = "api.call.failed"
    SYSTEM_ALERT = "system.alert"
    SECURITY_EVENT = "security.event"
    DATA_SYNC_COMPLETE = "data.sync.complete"

class WebhookStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    PENDING = "pending"

@dataclass
class WebhookConfig:
    """Webhook configuration"""
    id: str
    name: str
    url: str
    events: List[WebhookEventType]
    secret: str
    provider: str
    status: WebhookStatus
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_triggered: Optional[datetime] = None
    failure_count: int = 0
    retry_count: int = 0
    timeout: int = 30
    headers: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WebhookDelivery:
    """Webhook delivery attempt"""
    id: str
    webhook_id: str
    event_type: WebhookEventType
    payload: Dict[str, Any]
    status: str
    response_code: int
    response_body: str
    attempt_number: int
    created_at: datetime = field(default_factory=datetime.now)
    next_retry_at: Optional[datetime] = None
    error_message: str = ""

@dataclass
class WebhookMetrics:
    """Webhook performance metrics"""
    webhook_id: str
    date: datetime
    total_deliveries: int
    successful_deliveries: int
    failed_deliveries: int
    average_response_time: float
    success_rate: float
    last_delivery_time: Optional[datetime]
    error_rate: float

class WebhookManager:
    """Manages webhook operations and delivery"""

    def __init__(self):
        self.redis_manager = RedisManager()
        self.api_manager = ExternalAPIManager()
        self.social_manager = SocialMediaManager()
        self.payment_manager = PaymentServiceManager()
        self.cloud_manager = CloudIntegrationManager()

        # Webhook configurations
        self.webhooks: Dict[str, WebhookConfig] = {}
        self._load_webhooks()

        # Event handlers
        self.event_handlers: Dict[WebhookEventType, List[Callable]] = {}
        self._initialize_event_handlers()

        # Delivery queue
        self.delivery_queue = asyncio.Queue()
        self._delivery_worker_running = False

        # Rate limiting
        self.rate_limits = {}
        self._initialize_rate_limits()

        # Metrics collection
        self.metrics_cache = {}

    def _load_webhooks(self):
        """Load webhook configurations"""
        try:
            # Load from database or configuration
            # For now, initialize with empty dict
            pass
        except Exception as e:
            logger.error(f"Error loading webhooks: {e}")

    def _initialize_event_handlers(self):
        """Initialize event handlers for different webhook types"""
        self.event_handlers = {
            WebhookEventType.PAYMENT_SUCCESS: [self._handle_payment_success],
            WebhookEventType.PAYMENT_FAILED: [self._handle_payment_failed],
            WebhookEventType.PAYMENT_REFUNDED: [self._handle_payment_refunded],
            WebhookEventType.SUBSCRIPTION_CREATED: [self._handle_subscription_created],
            WebhookEventType.SUBSCRIPTION_CANCELLED: [self._handle_subscription_cancelled],
            WebhookEventType.CUSTOMER_CREATED: [self._handle_customer_created],
            WebhookEventType.CUSTOMER_UPDATED: [self._handle_customer_updated],
            WebhookEventType.SOCIAL_POST_CREATED: [self._handle_social_post_created],
            WebhookEventType.SOCIAL_POST_UPDATED: [self._handle_social_post_updated],
            WebhookEventType.CLOUD_RESOURCE_CREATED: [self._handle_cloud_resource_created],
            WebhookEventType.CLOUD_RESOURCE_UPDATED: [self._handle_cloud_resource_updated],
            WebhookEventType.CLOUD_RESOURCE_DELETED: [self._handle_cloud_resource_deleted],
            WebhookEventType.API_CALL_SUCCESS: [self._handle_api_call_success],
            WebhookEventType.API_CALL_FAILED: [self._handle_api_call_failed],
            WebhookEventType.SYSTEM_ALERT: [self._handle_system_alert],
            WebhookEventType.SECURITY_EVENT: [self._handle_security_event],
            WebhookEventType.DATA_SYNC_COMPLETE: [self._handle_data_sync_complete]
        }

    def _initialize_rate_limits(self):
        """Initialize rate limiting for webhook deliveries"""
        self.rate_limits = {
            "default": {
                "requests_per_second": 100,
                "window_seconds": 1
            },
            "high_priority": {
                "requests_per_second": 1000,
                "window_seconds": 1
            },
            "low_priority": {
                "requests_per_second": 10,
                "window_seconds": 1
            }
        }

    async def create_webhook(self, name: str, url: str, events: List[WebhookEventType],
                           provider: str, secret: str = None,
                           headers: Dict[str, str] = None,
                           timeout: int = 30) -> WebhookConfig:
        """Create a new webhook configuration"""
        try:
            # Generate webhook ID
            webhook_id = f"wh_{int(datetime.now().timestamp())}"

            # Generate secret if not provided
            if not secret:
                import secrets
                secret = secrets.token_urlsafe(32)

            # Create webhook config
            webhook = WebhookConfig(
                id=webhook_id,
                name=name,
                url=url,
                events=events,
                secret=secret,
                provider=provider,
                status=WebhookStatus.ACTIVE,
                timeout=timeout,
                headers=headers or {}
            )

            # Store webhook
            self.webhooks[webhook_id] = webhook

            # Save to database
            await self._save_webhook_to_db(webhook)

            logger.info(f"Created webhook {webhook_id} for {url}")

            return webhook

        except Exception as e:
            logger.error(f"Error creating webhook: {e}")
            raise

    async def _save_webhook_to_db(self, webhook: WebhookConfig):
        """Save webhook configuration to database"""
        # This would save to PostgreSQL database
        pass

    async def update_webhook(self, webhook_id: str, **kwargs) -> WebhookConfig:
        """Update webhook configuration"""
        try:
            if webhook_id not in self.webhooks:
                raise ValueError(f"Webhook {webhook_id} not found")

            webhook = self.webhooks[webhook_id]

            # Update fields
            for key, value in kwargs.items():
                if hasattr(webhook, key):
                    setattr(webhook, key, value)

            webhook.updated_at = datetime.now()

            # Save to database
            await self._save_webhook_to_db(webhook)

            logger.info(f"Updated webhook {webhook_id}")

            return webhook

        except Exception as e:
            logger.error(f"Error updating webhook {webhook_id}: {e}")
            raise

    async def delete_webhook(self, webhook_id: str) -> bool:
        """Delete webhook configuration"""
        try:
            if webhook_id not in self.webhooks:
                raise ValueError(f"Webhook {webhook_id} not found")

            # Remove from memory
            del self.webhooks[webhook_id]

            # Delete from database
            await self._delete_webhook_from_db(webhook_id)

            logger.info(f"Deleted webhook {webhook_id}")

            return True

        except Exception as e:
            logger.error(f"Error deleting webhook {webhook_id}: {e}")
            raise

    async def _delete_webhook_from_db(self, webhook_id: str):
        """Delete webhook from database"""
        # This would delete from PostgreSQL database
        pass

    async def trigger_webhook(self, event_type: WebhookEventType, payload: Dict[str, Any],
                            webhook_id: str = None) -> List[WebhookDelivery]:
        """Trigger webhook for specific event"""
        deliveries = []

        try:
            # Get webhooks to trigger
            if webhook_id:
                webhooks_to_trigger = [self.webhooks.get(webhook_id)]
            else:
                webhooks_to_trigger = [
                    webhook for webhook in self.webhooks.values()
                    if webhook.status == WebhookStatus.ACTIVE
                    and event_type in webhook.events
                ]

            # Trigger each webhook
            for webhook in webhooks_to_trigger:
                if webhook:
                    delivery = await self._deliver_webhook(webhook, event_type, payload)
                    deliveries.append(delivery)

            # Process event handlers
            await self._process_event_handlers(event_type, payload)

            return deliveries

        except Exception as e:
            logger.error(f"Error triggering webhook for {event_type.value}: {e}")
            return deliveries

    async def _deliver_webhook(self, webhook: WebhookConfig, event_type: WebhookEventType,
                             payload: Dict[str, Any]) -> WebhookDelivery:
        """Deliver webhook to specified URL"""
        delivery_id = f"delivery_{int(datetime.now().timestamp())}_{webhook.id}"
        delivery = WebhookDelivery(
            id=delivery_id,
            webhook_id=webhook.id,
            event_type=event_type,
            payload=payload,
            status="pending",
            response_code=0,
            response_body="",
            attempt_number=1
        )

        try:
            # Add to delivery queue
            await self.delivery_queue.put((webhook, delivery))

            # Start delivery worker if not running
            if not self._delivery_worker_running:
                asyncio.create_task(self._delivery_worker())

            return delivery

        except Exception as e:
            logger.error(f"Error queuing webhook delivery: {e}")
            delivery.status = "failed"
            delivery.error_message = str(e)
            return delivery

    async def _delivery_worker(self):
        """Worker process for delivering webhooks"""
        self._delivery_worker_running = True
        logger.info("Webhook delivery worker started")

        while True:
            try:
                # Get webhook from queue
                webhook, delivery = await asyncio.wait_for(
                    self.delivery_queue.get(), timeout=1.0
                )

                # Process delivery
                await self._process_webhook_delivery(webhook, delivery)

            except asyncio.TimeoutError:
                # No webhooks in queue
                continue
            except Exception as e:
                logger.error(f"Error in webhook delivery worker: {e}")

    async def _process_webhook_delivery(self, webhook: WebhookConfig, delivery: WebhookDelivery):
        """Process individual webhook delivery"""
        try:
            # Prepare request data
            headers = webhook.headers.copy()
            headers['Content-Type'] = 'application/json'
            headers['User-Agent'] = 'DeepAgent-Webhook/1.0'
            headers['X-Webhook-Event'] = delivery.event_type.value
            headers['X-Webhook-ID'] = delivery.id
            headers['X-Webhook-Timestamp'] = str(int(datetime.now().timestamp()))

            # Add signature if secret is configured
            if webhook.secret:
                signature = self._generate_signature(webhook.secret, delivery.payload)
                headers['X-Webhook-Signature'] = f'sha256={signature}'

            # Make HTTP request
            start_time = datetime.now()
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=webhook.timeout)) as session:
                async with session.post(
                    webhook.url,
                    json=delivery.payload,
                    headers=headers
                ) as response:
                    response_time = (datetime.now() - start_time).total_seconds()
                    response_body = await response.text()

                    # Update delivery
                    delivery.response_code = response.status
                    delivery.response_body = response_body

                    if response.status < 400:
                        delivery.status = "success"
                        webhook.failure_count = 0
                    else:
                        delivery.status = "failed"
                        webhook.failure_count += 1
                        delivery.error_message = f"HTTP {response.status}"

            # Update webhook last triggered time
            webhook.last_triggered = datetime.now()
            await self._save_webhook_to_db(webhook)

            # Save delivery record
            await self._save_delivery_to_db(delivery)

            # Update metrics
            await self._update_webhook_metrics(webhook.id, delivery, response_time)

            logger.info(f"Webhook {webhook.id} delivered to {webhook.url} with status {delivery.status}")

        except Exception as e:
            logger.error(f"Error delivering webhook {webhook.id}: {e}")
            delivery.status = "failed"
            delivery.error_message = str(e)
            webhook.failure_count += 1

            # Schedule retry if within retry limit
            if webhook.retry_count < 3:
                webhook.retry_count += 1
                delivery.next_retry_at = datetime.now() + timedelta(minutes=webhook.retry_count * 5)
                await self.delivery_queue.put((webhook, delivery))
            else:
                webhook.status = WebhookStatus.FAILED
                await self._save_webhook_to_db(webhook)

            await self._save_delivery_to_db(delivery)

    def _generate_signature(self, secret: str, payload: Dict[str, Any]) -> str:
        """Generate webhook signature"""
        payload_json = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            secret.encode('utf-8'),
            payload_json.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    async def _save_delivery_to_db(self, delivery: WebhookDelivery):
        """Save delivery record to database"""
        # This would save to PostgreSQL database
        pass

    async def _update_webhook_metrics(self, webhook_id: str, delivery: WebhookDelivery, response_time: float):
        """Update webhook metrics"""
        try:
            # Get or create metrics
            today = datetime.now().date()
            metrics_key = f"webhook_metrics:{webhook_id}:{today}"

            if metrics_key not in self.metrics_cache:
                self.metrics_cache[metrics_key] = WebhookMetrics(
                    webhook_id=webhook_id,
                    date=datetime.now(),
                    total_deliveries=0,
                    successful_deliveries=0,
                    failed_deliveries=0,
                    average_response_time=0.0,
                    success_rate=0.0,
                    last_delivery_time=None,
                    error_rate=0.0
                )

            metrics = self.metrics_cache[metrics_key]

            # Update metrics
            metrics.total_deliveries += 1
            metrics.last_delivery_time = datetime.now()

            if delivery.status == "success":
                metrics.successful_deliveries += 1
            else:
                metrics.failed_deliveries += 1

            # Calculate success rate
            metrics.success_rate = (metrics.successful_deliveries / metrics.total_deliveries) * 100

            # Calculate error rate
            metrics.error_rate = (metrics.failed_deliveries / metrics.total_deliveries) * 100

            # Update average response time
            if metrics.average_response_time == 0:
                metrics.average_response_time = response_time
            else:
                metrics.average_response_time = (metrics.average_response_time + response_time) / 2

            # Save to Redis
            await self.redis_manager.set(
                metrics_key,
                json.dumps({
                    'total_deliveries': metrics.total_deliveries,
                    'successful_deliveries': metrics.successful_deliveries,
                    'failed_deliveries': metrics.failed_deliveries,
                    'average_response_time': metrics.average_response_time,
                    'success_rate': metrics.success_rate,
                    'error_rate': metrics.error_rate,
                    'last_delivery_time': metrics.last_delivery_time.isoformat() if metrics.last_delivery_time else None
                }),
                expire=86400  # 24 hours
            )

        except Exception as e:
            logger.error(f"Error updating webhook metrics: {e}")

    async def validate_webhook_signature(self, webhook_id: str, payload: bytes,
                                       signature: str, timestamp: str) -> bool:
        """Validate webhook signature"""
        try:
            webhook = self.webhooks.get(webhook_id)
            if not webhook or not webhook.secret:
                return False

            # Check timestamp (prevent replay attacks)
            try:
                request_time = datetime.fromtimestamp(int(timestamp))
                if datetime.now() - request_time > timedelta(minutes=5):
                    return False
            except (ValueError, TypeError):
                return False

            # Generate expected signature
            expected_signature = self._generate_signature(webhook.secret, json.loads(payload.decode('utf-8')))

            # Compare signatures
            return hmac.compare_digest(signature, f'sha256={expected_signature}')

        except Exception as e:
            logger.error(f"Error validating webhook signature: {e}")
            return False

    async def handle_incoming_webhook(self, webhook_id: str, payload: Dict[str, Any],
                                    headers: Dict[str, str]) -> Dict[str, Any]:
        """Handle incoming webhook from external service"""
        result = {
            'success': False,
            'processed': False,
            'error': None
        }

        try:
            # Validate webhook
            webhook = self.webhooks.get(webhook_id)
            if not webhook:
                result['error'] = f"Webhook {webhook_id} not found"
                return result

            # Validate signature if configured
            if webhook.secret:
                signature = headers.get('X-Webhook-Signature')
                timestamp = headers.get('X-Webhook-Timestamp')

                if not signature or not timestamp:
                    result['error'] = "Missing signature or timestamp"
                    return result

                if not await self.validate_webhook_signature(webhook_id, json.dumps(payload).encode(), signature, timestamp):
                    result['error'] = "Invalid signature"
                    return result

            # Process webhook based on provider
            processed = await self._process_incoming_webhook(webhook.provider, payload)

            result['success'] = True
            result['processed'] = processed

        except Exception as e:
            logger.error(f"Error handling incoming webhook: {e}")
            result['error'] = str(e)

        return result

    async def _process_incoming_webhook(self, provider: str, payload: Dict[str, Any]) -> bool:
        """Process incoming webhook based on provider"""
        try:
            if provider == "stripe":
                return await self._process_stripe_webhook(payload)
            elif provider == "paypal":
                return await self._process_paypal_webhook(payload)
            elif provider == "twitter":
                return await self._process_twitter_webhook(payload)
            elif provider == "facebook":
                return await self._process_facebook_webhook(payload)
            elif provider == "aws":
                return await self._process_aws_webhook(payload)
            else:
                logger.warning(f"Unknown webhook provider: {provider}")
                return False

        except Exception as e:
            logger.error(f"Error processing incoming webhook: {e}")
            return False

    async def _process_stripe_webhook(self, payload: Dict[str, Any]) -> bool:
        """Process Stripe webhook"""
        try:
            event_type = payload.get('type')
            event_data = payload.get('data', {})

            if event_type == 'payment_intent.succeeded':
                await self.trigger_webhook(WebhookEventType.PAYMENT_SUCCESS, event_data)
            elif event_type == 'payment_intent.payment_failed':
                await self.trigger_webhook(WebhookEventType.PAYMENT_FAILED, event_data)
            elif event_type == 'customer.created':
                await self.trigger_webhook(WebhookEventType.CUSTOMER_CREATED, event_data)
            elif event_type == 'customer.updated':
                await self.trigger_webhook(WebhookEventType.CUSTOMER_UPDATED, event_data)

            return True

        except Exception as e:
            logger.error(f"Error processing Stripe webhook: {e}")
            return False

    async def _process_paypal_webhook(self, payload: Dict[str, Any]) -> bool:
        """Process PayPal webhook"""
        # Placeholder implementation
        return True

    async def _process_twitter_webhook(self, payload: Dict[str, Any]) -> bool:
        """Process Twitter webhook"""
        # Placeholder implementation
        return True

    async def _process_facebook_webhook(self, payload: Dict[str, Any]) -> bool:
        """Process Facebook webhook"""
        # Placeholder implementation
        return True

    async def _process_aws_webhook(self, payload: Dict[str, Any]) -> bool:
        """Process AWS webhook"""
        # Placeholder implementation
        return True

    async def _process_event_handlers(self, event_type: WebhookEventType, payload: Dict[str, Any]):
        """Process event handlers for webhook event"""
        try:
            if event_type in self.event_handlers:
                for handler in self.event_handlers[event_type]:
                    try:
                        await handler(payload)
                    except Exception as e:
                        logger.error(f"Error in event handler for {event_type.value}: {e}")

        except Exception as e:
            logger.error(f"Error processing event handlers: {e}")

    async def _handle_payment_success(self, payload: Dict[str, Any]):
        """Handle payment success event"""
        logger.info(f"Payment succeeded: {payload.get('id')}")

    async def _handle_payment_failed(self, payload: Dict[str, Any]):
        """Handle payment failed event"""
        logger.warning(f"Payment failed: {payload.get('id')}")

    async def _handle_payment_refunded(self, payload: Dict[str, Any]):
        """Handle payment refunded event"""
        logger.info(f"Payment refunded: {payload.get('id')}")

    async def _handle_subscription_created(self, payload: Dict[str, Any]):
        """Handle subscription created event"""
        logger.info(f"Subscription created: {payload.get('id')}")

    async def _handle_subscription_cancelled(self, payload: Dict[str, Any]):
        """Handle subscription cancelled event"""
        logger.info(f"Subscription cancelled: {payload.get('id')}")

    async def _handle_customer_created(self, payload: Dict[str, Any]):
        """Handle customer created event"""
        logger.info(f"Customer created: {payload.get('id')}")

    async def _handle_customer_updated(self, payload: Dict[str, Any]):
        """Handle customer updated event"""
        logger.info(f"Customer updated: {payload.get('id')}")

    async def _handle_social_post_created(self, payload: Dict[str, Any]):
        """Handle social post created event"""
        logger.info(f"Social post created: {payload.get('id')}")

    async def _handle_social_post_updated(self, payload: Dict[str, Any]):
        """Handle social post updated event"""
        logger.info(f"Social post updated: {payload.get('id')}")

    async def _handle_cloud_resource_created(self, payload: Dict[str, Any]):
        """Handle cloud resource created event"""
        logger.info(f"Cloud resource created: {payload.get('id')}")

    async def _handle_cloud_resource_updated(self, payload: Dict[str, Any]):
        """Handle cloud resource updated event"""
        logger.info(f"Cloud resource updated: {payload.get('id')}")

    async def _handle_cloud_resource_deleted(self, payload: Dict[str, Any]):
        """Handle cloud resource deleted event"""
        logger.info(f"Cloud resource deleted: {payload.get('id')}")

    async def _handle_api_call_success(self, payload: Dict[str, Any]):
        """Handle API call success event"""
        logger.info(f"API call successful: {payload.get('endpoint')}")

    async def _handle_api_call_failed(self, payload: Dict[str, Any]):
        """Handle API call failed event"""
        logger.warning(f"API call failed: {payload.get('endpoint')}")

    async def _handle_system_alert(self, payload: Dict[str, Any]):
        """Handle system alert event"""
        logger.warning(f"System alert: {payload.get('message')}")

    async def _handle_security_event(self, payload: Dict[str, Any]):
        """Handle security event"""
        logger.warning(f"Security event: {payload.get('type')}")

    async def _handle_data_sync_complete(self, payload: Dict[str, Any]):
        """Handle data sync complete event"""
        logger.info(f"Data sync complete: {payload.get('sync_id')}")

    async def get_webhook_metrics(self, webhook_id: str, start_date: datetime,
                                end_date: datetime) -> List[WebhookMetrics]:
        """Get webhook metrics for specified period"""
        metrics = []

        try:
            # Get metrics from Redis cache
            current_date = start_date.date()
            while current_date <= end_date.date():
                metrics_key = f"webhook_metrics:{webhook_id}:{current_date}"
                cached_metrics = await self.redis_manager.get(metrics_key)

                if cached_metrics:
                    metrics_data = json.loads(cached_metrics)
                    metrics.append(WebhookMetrics(
                        webhook_id=webhook_id,
                        date=datetime.combine(current_date, datetime.min.time()),
                        total_deliveries=metrics_data['total_deliveries'],
                        successful_deliveries=metrics_data['successful_deliveries'],
                        failed_deliveries=metrics_data['failed_deliveries'],
                        average_response_time=metrics_data['average_response_time'],
                        success_rate=metrics_data['success_rate'],
                        last_delivery_time=datetime.fromisoformat(metrics_data['last_delivery_time']) if metrics_data['last_delivery_time'] else None,
                        error_rate=metrics_data['error_rate']
                    ))

                current_date += timedelta(days=1)

        except Exception as e:
            logger.error(f"Error getting webhook metrics: {e}")

        return metrics

    async def get_webhook_health(self, webhook_id: str) -> Dict[str, Any]:
        """Get webhook health status"""
        health = {
            'webhook_id': webhook_id,
            'status': 'unknown',
            'last_delivery': None,
            'success_rate': 0.0,
            'error_rate': 0.0,
            'failure_count': 0,
            'recommendations': []
        }

        try:
            webhook = self.webhooks.get(webhook_id)
            if not webhook:
                health['status'] = 'not_found'
                return health

            # Get recent metrics
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            metrics = await self.get_webhook_metrics(webhook_id, start_date, end_date)

            if metrics:
                total_deliveries = sum(m.total_deliveries for m in metrics)
                successful_deliveries = sum(m.successful_deliveries for m in metrics)
                failed_deliveries = sum(m.failed_deliveries for m in metrics)

                health['success_rate'] = (successful_deliveries / total_deliveries) * 100 if total_deliveries > 0 else 0
                health['error_rate'] = (failed_deliveries / total_deliveries) * 100 if total_deliveries > 0 else 0

                # Get last delivery time
                last_delivery = max((m.last_delivery_time for m in metrics if m.last_delivery_time), default=None)
                health['last_delivery'] = last_delivery

                # Determine health status
                if webhook.status == WebhookStatus.FAILED:
                    health['status'] = 'failed'
                elif webhook.failure_count > 5:
                    health['status'] = 'degraded'
                elif health['success_rate'] < 95:
                    health['status'] = 'degraded'
                elif webhook.last_triggered and (datetime.now() - webhook.last_triggered) > timedelta(hours=24):
                    health['status'] = 'stale'
                else:
                    health['status'] = 'healthy'

                health['failure_count'] = webhook.failure_count

                # Generate recommendations
                if health['error_rate'] > 5:
                    health['recommendations'].append("High error rate detected. Check webhook endpoint.")
                if health['success_rate'] < 95:
                    health['recommendations'].append("Low success rate. Consider retry mechanism.")
                if webhook.failure_count > 3:
                    health['recommendations'].append("Multiple failures detected. Investigate webhook configuration.")
                if webhook.last_triggered and (datetime.now() - webhook.last_triggered) > timedelta(hours=24):
                    health['recommendations'].append("Webhook not triggered recently. Check if events are being generated.")

        except Exception as e:
            logger.error(f"Error getting webhook health: {e}")
            health['status'] = 'error'

        return health

    async def retry_failed_deliveries(self, webhook_id: str = None) -> Dict[str, Any]:
        """Retry failed webhook deliveries"""
        retry_result = {
            'success': False,
            'retried_deliveries': 0,
            'successful_retries': 0,
            'failed_retries': 0,
            'error': None
        }

        try:
            # Get failed deliveries from database
            failed_deliveries = await self._get_failed_deliveries(webhook_id)

            for delivery in failed_deliveries:
                webhook = self.webhooks.get(delivery.webhook_id)
                if webhook and webhook.status == WebhookStatus.ACTIVE:
                    # Reset delivery for retry
                    delivery.status = "pending"
                    delivery.attempt_number += 1
                    delivery.next_retry_at = None

                    # Add to queue
                    await self.delivery_queue.put((webhook, delivery))
                    retry_result['retried_deliveries'] += 1

            retry_result['success'] = True

        except Exception as e:
            logger.error(f"Error retrying failed deliveries: {e}")
            retry_result['error'] = str(e)

        return retry_result

    async def _get_failed_deliveries(self, webhook_id: str = None) -> List[WebhookDelivery]:
        """Get failed deliveries from database"""
        # This would fetch from PostgreSQL database
        return []

    async def cleanup_old_deliveries(self, days_to_keep: int = 30) -> Dict[str, Any]:
        """Clean up old webhook delivery records"""
        cleanup_result = {
            'success': False,
            'cleaned_deliveries': 0,
            'error': None
        }

        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)

            # Delete old deliveries from database
            cleaned_count = await self._delete_old_deliveries(cutoff_date)

            cleanup_result['success'] = True
            cleanup_result['cleaned_deliveries'] = cleaned_count

            logger.info(f"Cleaned up {cleaned_count} old webhook deliveries")

        except Exception as e:
            logger.error(f"Error cleaning up old deliveries: {e}")
            cleanup_result['error'] = str(e)

        return cleanup_result

    async def _delete_old_deliveries(self, cutoff_date: datetime) -> int:
        """Delete old deliveries from database"""
        # This would delete from PostgreSQL database
        return 0

    async def create_webhook_endpoint(self, path: str, handler: Callable) -> str:
        """Create a webhook endpoint for receiving webhooks"""
        try:
            # This would register the endpoint with the FastAPI app
            # For now, return the path
            return path

        except Exception as e:
            logger.error(f"Error creating webhook endpoint: {e}")
            raise

    async def test_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """Test webhook connectivity"""
        test_result = {
            'success': False,
            'response_code': 0,
            'response_time': 0.0,
            'error': None
        }

        try:
            webhook = self.webhooks.get(webhook_id)
            if not webhook:
                test_result['error'] = f"Webhook {webhook_id} not found"
                return test_result

            # Prepare test payload
            test_payload = {
                'test': True,
                'webhook_id': webhook_id,
                'timestamp': datetime.now().isoformat(),
                'message': 'Test webhook delivery'
            }

            # Send test request
            start_time = datetime.now()
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=webhook.timeout)) as session:
                async with session.post(
                    webhook.url,
                    json=test_payload,
                    headers={'Content-Type': 'application/json', 'User-Agent': 'DeepAgent-Webhook-Test/1.0'}
                ) as response:
                    response_time = (datetime.now() - start_time).total_seconds()
                    response_body = await response.text()

                    test_result['success'] = response.status < 400
                    test_result['response_code'] = response.status
                    test_result['response_time'] = response_time

                    if not test_result['success']:
                        test_result['error'] = f"HTTP {response.status}: {response_body}"

        except Exception as e:
            logger.error(f"Error testing webhook {webhook_id}: {e}")
            test_result['error'] = str(e)

        return test_result