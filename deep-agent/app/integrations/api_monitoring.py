"""
API Testing and Monitoring Tools for LangGraph Deep Web Agent

This module provides comprehensive API testing, monitoring, and performance
analysis capabilities for all integrated services and APIs.
"""

import asyncio
import json
import logging
import time
import statistics
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import asyncpg
import redis.asyncio as redis
from concurrent.futures import ThreadPoolExecutor

from app.core.config import settings
from app.database.redis import RedisManager
from app.integrations.external_apis import ExternalAPIManager
from app.integrations.web_services import WebServiceManager
from app.tools.ai_services import AIServiceManager

logger = logging.getLogger(__name__)

class APIMonitoringLevel(Enum):
    BASIC = "basic"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"

class APIStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class APITestResult:
    """API test result"""
    id: str
    endpoint: str
    method: str
    status_code: int
    response_time: float
    success: bool
    error_message: str = ""
    response_size: int = 0
    headers: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class APIMetrics:
    """API performance metrics"""
    endpoint: str
    timestamp: datetime
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    p99_response_time: float
    error_rate: float
    availability_percentage: float
    total_data_transferred: int
    average_data_size: float

@dataclass
class APIAlert:
    """API monitoring alert"""
    id: str
    endpoint: str
    severity: AlertSeverity
    message: str
    details: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    resolved_at: Optional[datetime] = None

@dataclass
class SLAReport:
    """Service Level Agreement report"""
    endpoint: str
    period_start: datetime
    period_end: datetime
    uptime_percentage: float
    average_response_time: float
    error_budget_used: float
    sla_compliant: bool
    violations: List[Dict[str, Any]]
    recommendations: List[str]

class APIMonitor:
    """API monitoring and testing system"""

    def __init__(self):
        self.redis_manager = RedisManager()
        self.api_manager = ExternalAPIManager()
        self.web_service_manager = WebServiceManager()
        self.ai_service = AIServiceManager()

        # Monitoring configuration
        self.monitored_endpoints = {}
        self.test_schedules = {}
        self.alert_rules = {}
        self.sla_definitions = {}

        # Performance data storage
        self.metrics_cache = {}
        self.alert_history = []

        # Monitoring workers
        self._monitoring_workers = {}
        self._alert_worker_running = False

        # Rate limiting
        self.rate_limits = {}
        self._initialize_rate_limits()

        # Initialize monitoring
        self._initialize_monitoring()

    def _initialize_rate_limits(self):
        """Initialize rate limiting for API monitoring"""
        self.rate_limits = {
            "health_checks": {
                "requests_per_minute": 60,
                "window_seconds": 60
            },
            "load_tests": {
                "requests_per_second": 100,
                "window_seconds": 1
            },
            "continuous_monitoring": {
                "requests_per_second": 10,
                "window_seconds": 1
            }
        }

    def _initialize_monitoring(self):
        """Initialize API monitoring system"""
        try:
            # Load monitored endpoints from configuration
            self._load_monitored_endpoints()

            # Load alert rules
            self._load_alert_rules()

            # Load SLA definitions
            self._load_sla_definitions()

            # Start alert worker
            if not self._alert_worker_running:
                asyncio.create_task(self._alert_worker())
                self._alert_worker_running = True

            logger.info("API monitoring system initialized")

        except Exception as e:
            logger.error(f"Error initializing API monitoring: {e}")

    def _load_monitored_endpoints(self):
        """Load endpoints to monitor"""
        # This would load from configuration or database
        self.monitored_endpoints = {
            "external_apis": {
                "twitter": "https://api.twitter.com/2/health",
                "facebook": "https://graph.facebook.com/v18.0/me",
                "stripe": "https://api.stripe.com/v1/charges",
                "openai": "https://api.openai.com/v1/models",
                "weather": "https://api.openweathermap.org/data/2.5/weather"
            },
            "internal_services": {
                "auth": f"{settings.API_BASE_URL}/auth/health",
                "database": f"{settings.API_BASE_URL}/database/health",
                "redis": f"{settings.API_BASE_URL}/redis/health",
                "agent": f"{settings.API_BASE_URL}/agent/health"
            }
        }

    def _load_alert_rules(self):
        """Load alert rules"""
        self.alert_rules = {
            "high_error_rate": {
                "condition": "error_rate > 5",
                "severity": AlertSeverity.ERROR,
                "threshold": 5.0,
                "duration": 300,  # 5 minutes
                "message": "High error rate detected: {error_rate}%"
            },
            "slow_response": {
                "condition": "avg_response_time > 2",
                "severity": AlertSeverity.WARNING,
                "threshold": 2.0,
                "duration": 300,
                "message": "Slow response time detected: {avg_response_time}s"
            },
            "service_down": {
                "condition": "availability < 95",
                "severity": AlertSeverity.CRITICAL,
                "threshold": 95.0,
                "duration": 60,
                "message": "Service availability below threshold: {availability}%"
            },
            "high_latency": {
                "condition": "p95_response_time > 1",
                "severity": AlertSeverity.WARNING,
                "threshold": 1.0,
                "duration": 180,
                "message": "High P95 latency detected: {p95_response_time}s"
            }
        }

    def _load_sla_definitions(self):
        """Load SLA definitions"""
        self.sla_definitions = {
            "critical_services": {
                "uptime_target": 99.9,
                "response_time_target": 0.5,
                "error_rate_target": 0.1,
                "error_budget": 0.1  # 0.1% error budget
            },
            "standard_services": {
                "uptime_target": 99.0,
                "response_time_target": 1.0,
                "error_rate_target": 1.0,
                "error_budget": 1.0
            },
            "background_services": {
                "uptime_target": 95.0,
                "response_time_target": 2.0,
                "error_rate_target": 5.0,
                "error_budget": 5.0
            }
        }

    async def test_endpoint(self, endpoint: str, method: str = "GET",
                           headers: Dict[str, str] = None,
                           data: Any = None, timeout: int = 30) -> APITestResult:
        """Test a single API endpoint"""
        test_id = f"test_{int(time.time())}_{hash(endpoint) % 10000}"
        test_result = APITestResult(
            id=test_id,
            endpoint=endpoint,
            method=method,
            status_code=0,
            response_time=0.0,
            success=False
        )

        try:
            start_time = time.time()

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.request(
                    method,
                    endpoint,
                    headers=headers,
                    json=data if isinstance(data, dict) else None,
                    data=data if not isinstance(data, dict) else None
                ) as response:
                    response_time = time.time() - start_time

                    test_result.status_code = response.status
                    test_result.response_time = response_time
                    test_result.success = response.status < 400
                    test_result.response_size = len(await response.read())
                    test_result.headers = dict(response.headers)

                    if not test_result.success:
                        error_text = await response.text()
                        test_result.error_message = f"HTTP {response.status}: {error_text[:200]}"

            # Store test result
            await self._store_test_result(test_result)

            # Update metrics
            await self._update_endpoint_metrics(endpoint, test_result)

            logger.info(f"Test {test_id} completed: {endpoint} - {response.status} ({response_time:.3f}s)")

            return test_result

        except Exception as e:
            test_result.response_time = time.time() - start_time
            test_result.error_message = str(e)
            test_result.success = False

            await self._store_test_result(test_result)
            await self._update_endpoint_metrics(endpoint, test_result)

            logger.error(f"Test {test_id} failed: {endpoint} - {str(e)}")

            return test_result

    async def _store_test_result(self, test_result: APITestResult):
        """Store test result in database"""
        try:
            # Store in Redis for quick access
            redis_key = f"api_test:{test_result.endpoint}:{int(test_result.timestamp.timestamp())}"
            await self.redis_manager.set(
                redis_key,
                json.dumps({
                    'id': test_result.id,
                    'endpoint': test_result.endpoint,
                    'method': test_result.method,
                    'status_code': test_result.status_code,
                    'response_time': test_result.response_time,
                    'success': test_result.success,
                    'error_message': test_result.error_message,
                    'response_size': test_result.response_size,
                    'headers': test_result.headers,
                    'metadata': test_result.metadata,
                    'timestamp': test_result.timestamp.isoformat()
                }),
                expire=86400 * 7  # 7 days
            )

        except Exception as e:
            logger.error(f"Error storing test result: {e}")

    async def _update_endpoint_metrics(self, endpoint: str, test_result: APITestResult):
        """Update metrics for endpoint"""
        try:
            # Get current metrics
            today = datetime.now().date()
            metrics_key = f"api_metrics:{endpoint}:{today}"

            current_metrics = await self.redis_manager.get(metrics_key)
            if current_metrics:
                metrics_data = json.loads(current_metrics)
            else:
                metrics_data = {
                    'total_requests': 0,
                    'successful_requests': 0,
                    'failed_requests': 0,
                    'response_times': [],
                    'total_data_transferred': 0,
                    'first_request': None,
                    'last_request': None
                }

            # Update metrics
            metrics_data['total_requests'] += 1
            metrics_data['total_data_transferred'] += test_result.response_size

            if test_result.success:
                metrics_data['successful_requests'] += 1
            else:
                metrics_data['failed_requests'] += 1

            metrics_data['response_times'].append(test_result.response_time)

            if not metrics_data['first_request']:
                metrics_data['first_request'] = test_result.timestamp.isoformat()
            metrics_data['last_request'] = test_result.timestamp.isoformat()

            # Keep only last 1000 response times for memory efficiency
            if len(metrics_data['response_times']) > 1000:
                metrics_data['response_times'] = metrics_data['response_times'][-1000:]

            # Save updated metrics
            await self.redis_manager.set(
                metrics_key,
                json.dumps(metrics_data),
                expire=86400 * 30  # 30 days
            )

        except Exception as e:
            logger.error(f"Error updating endpoint metrics: {e}")

    async def run_health_check(self, endpoint: str) -> Dict[str, Any]:
        """Run comprehensive health check for endpoint"""
        health_result = {
            'endpoint': endpoint,
            'status': APIStatus.UNKNOWN,
            'response_time': 0.0,
            'availability': 0.0,
            'error_rate': 0.0,
            'last_check': datetime.now(),
            'checks': {},
            'recommendations': []
        }

        try:
            # Basic connectivity test
            basic_test = await self.test_endpoint(endpoint)
            health_result['checks']['basic_connectivity'] = {
                'success': basic_test.success,
                'response_time': basic_test.response_time,
                'status_code': basic_test.status_code
            }
            health_result['response_time'] = basic_test.response_time

            # Get historical metrics
            metrics = await self.get_endpoint_metrics(endpoint, days=1)
            if metrics:
                total_requests = sum(m.total_requests for m in metrics)
                successful_requests = sum(m.successful_requests for m in metrics)
                health_result['availability'] = (successful_requests / total_requests) * 100 if total_requests > 0 else 0
                health_result['error_rate'] = 100 - health_result['availability']

            # Determine overall status
            if health_result['availability'] >= 99.9 and health_result['response_time'] < 0.5:
                health_result['status'] = APIStatus.HEALTHY
            elif health_result['availability'] >= 95.0 and health_result['response_time'] < 2.0:
                health_result['status'] = APIStatus.DEGRADED
            elif health_result['availability'] >= 90.0:
                health_result['status'] = APIStatus.DEGRADED
            else:
                health_result['status'] = APIStatus.UNHEALTHY

            # Generate recommendations
            if health_result['status'] == APIStatus.UNHEALTHY:
                health_result['recommendations'].append("Endpoint is unhealthy. Immediate investigation required.")
            elif health_result['status'] == APIStatus.DEGRADED:
                health_result['recommendations'].append("Performance degraded. Consider optimization.")
            if health_result['error_rate'] > 5:
                health_result['recommendations'].append("High error rate detected. Review error logs.")

        except Exception as e:
            logger.error(f"Error running health check for {endpoint}: {e}")
            health_result['status'] = APIStatus.UNKNOWN
            health_result['recommendations'].append(f"Health check failed: {str(e)}")

        return health_result

    async def run_load_test(self, endpoint: str, concurrent_users: int = 10,
                          requests_per_user: int = 10, ramp_up_time: int = 30) -> Dict[str, Any]:
        """Run load test on endpoint"""
        load_test_result = {
            'endpoint': endpoint,
            'concurrent_users': concurrent_users,
            'requests_per_user': requests_per_user,
            'total_requests': concurrent_users * requests_per_user,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'min_response_time': float('inf'),
            'max_response_time': 0.0,
            'p95_response_time': 0.0,
            'p99_response_time': 0.0,
            'requests_per_second': 0.0,
            'error_rate': 0.0,
            'duration': 0.0,
            'test_id': f"load_test_{int(time.time())}"
        }

        try:
            start_time = time.time()
            response_times = []
            semaphore = asyncio.Semaphore(concurrent_users)

            async def make_request():
                async with semaphore:
                    result = await self.test_endpoint(endpoint)
                    return result

            # Create tasks for all requests
            tasks = []
            for _ in range(requests_per_user):
                for _ in range(concurrent_users):
                    tasks.append(make_request())

            # Execute all requests
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            successful_results = []
            for result in results:
                if isinstance(result, Exception):
                    load_test_result['failed_requests'] += 1
                elif result.success:
                    load_test_result['successful_requests'] += 1
                    successful_results.append(result)
                    response_times.append(result.response_time)
                else:
                    load_test_result['failed_requests'] += 1

            # Calculate metrics
            load_test_result['duration'] = time.time() - start_time

            if response_times:
                load_test_result['average_response_time'] = statistics.mean(response_times)
                load_test_result['min_response_time'] = min(response_times)
                load_test_result['max_response_time'] = max(response_times)
                load_test_result['p95_response_time'] = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
                load_test_result['p99_response_time'] = statistics.quantiles(response_times, n=100)[98]  # 99th percentile

            load_test_result['requests_per_second'] = load_test_result['total_requests'] / load_test_result['duration']
            load_test_result['error_rate'] = (load_test_result['failed_requests'] / load_test_result['total_requests']) * 100

            logger.info(f"Load test {load_test_result['test_id']} completed for {endpoint}")

        except Exception as e:
            logger.error(f"Error running load test for {endpoint}: {e}")
            load_test_result['error'] = str(e)

        return load_test_result

    async def get_endpoint_metrics(self, endpoint: str, days: int = 7) -> List[APIMetrics]:
        """Get metrics for endpoint over specified period"""
        metrics = []

        try:
            # Get metrics from Redis
            current_date = datetime.now().date()
            for i in range(days):
                date = current_date - timedelta(days=i)
                metrics_key = f"api_metrics:{endpoint}:{date}"

                metrics_data = await self.redis_manager.get(metrics_key)
                if metrics_data:
                    data = json.loads(metrics_data)

                    # Calculate statistics
                    response_times = data['response_times']
                    if response_times:
                        avg_response_time = statistics.mean(response_times)
                        min_response_time = min(response_times)
                        max_response_time = max(response_times)
                        p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times)
                        p99_response_time = statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else max(response_times)
                    else:
                        avg_response_time = min_response_time = max_response_time = p95_response_time = p99_response_time = 0.0

                    # Calculate rates
                    total_requests = data['total_requests']
                    successful_requests = data['successful_requests']
                    failed_requests = data['failed_requests']
                    error_rate = (failed_requests / total_requests) * 100 if total_requests > 0 else 0
                    availability_percentage = (successful_requests / total_requests) * 100 if total_requests > 0 else 0

                    # Calculate average data size
                    average_data_size = data['total_data_transferred'] / total_requests if total_requests > 0 else 0

                    metric = APIMetrics(
                        endpoint=endpoint,
                        timestamp=datetime.combine(date, datetime.min.time()),
                        total_requests=total_requests,
                        successful_requests=successful_requests,
                        failed_requests=failed_requests,
                        average_response_time=avg_response_time,
                        min_response_time=min_response_time,
                        max_response_time=max_response_time,
                        p95_response_time=p95_response_time,
                        p99_response_time=p99_response_time,
                        error_rate=error_rate,
                        availability_percentage=availability_percentage,
                        total_data_transferred=data['total_data_transferred'],
                        average_data_size=average_data_size
                    )

                    metrics.append(metric)

        except Exception as e:
            logger.error(f"Error getting endpoint metrics: {e}")

        return metrics

    async def monitor_endpoints(self, check_interval: int = 60):
        """Continuously monitor all endpoints"""
        logger.info("Starting endpoint monitoring")

        while True:
            try:
                for category, endpoints in self.monitored_endpoints.items():
                    for name, endpoint in endpoints.items():
                        try:
                            # Run health check
                            health_result = await self.run_health_check(endpoint)

                            # Check for alerts
                            await self._check_alert_rules(f"{category}.{name}", health_result)

                            # Log results
                            logger.debug(f"Health check {category}.{name}: {health_result['status'].value}")

                        except Exception as e:
                            logger.error(f"Error monitoring {category}.{name}: {e}")

                # Wait for next check
                await asyncio.sleep(check_interval)

            except Exception as e:
                logger.error(f"Error in endpoint monitoring loop: {e}")
                await asyncio.sleep(check_interval)

    async def _check_alert_rules(self, endpoint_name: str, health_result: Dict[str, Any]):
        """Check alert rules for endpoint"""
        try:
            for rule_name, rule in self.alert_rules.items():
                # Evaluate rule condition
                should_alert = False
                alert_data = {}

                if rule_name == "high_error_rate":
                    error_rate = health_result.get('error_rate', 0)
                    should_alert = error_rate > rule['threshold']
                    alert_data = {'error_rate': error_rate}

                elif rule_name == "slow_response":
                    response_time = health_result.get('response_time', 0)
                    should_alert = response_time > rule['threshold']
                    alert_data = {'avg_response_time': response_time}

                elif rule_name == "service_down":
                    availability = health_result.get('availability', 0)
                    should_alert = availability < rule['threshold']
                    alert_data = {'availability': availability}

                elif rule_name == "high_latency":
                    # This would need historical data
                    metrics = await self.get_endpoint_metrics(health_result['endpoint'], days=1)
                    if metrics:
                        latest_metric = metrics[0]
                        p95_response_time = latest_metric.p95_response_time
                        should_alert = p95_response_time > rule['threshold']
                        alert_data = {'p95_response_time': p95_response_time}

                if should_alert:
                    # Create alert
                    alert = APIAlert(
                        id=f"alert_{int(time.time())}_{hash(endpoint_name) % 10000}",
                        endpoint=endpoint_name,
                        severity=rule['severity'],
                        message=rule['message'].format(**alert_data),
                        details={
                            'rule': rule_name,
                            'threshold': rule['threshold'],
                            'current_value': alert_data,
                            'health_result': health_result
                        }
                    )

                    # Store alert
                    await self._store_alert(alert)

                    logger.warning(f"Alert triggered: {alert.message}")

        except Exception as e:
            logger.error(f"Error checking alert rules: {e}")

    async def _store_alert(self, alert: APIAlert):
        """Store alert in database"""
        try:
            # Store in Redis
            alert_key = f"alert:{alert.id}"
            await self.redis_manager.set(
                alert_key,
                json.dumps({
                    'id': alert.id,
                    'endpoint': alert.endpoint,
                    'severity': alert.severity.value,
                    'message': alert.message,
                    'details': alert.details,
                    'created_at': alert.created_at.isoformat(),
                    'acknowledged': alert.acknowledged,
                    'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None
                }),
                expire=86400 * 30  # 30 days
            )

            # Add to recent alerts list
            recent_alerts_key = "recent_alerts"
            recent_alerts = await self.redis_manager.lrange(recent_alerts_key, 0, -1)
            recent_alerts_data = [json.loads(alert) for alert in recent_alerts]

            # Keep only last 100 alerts
            if len(recent_alerts_data) >= 100:
                await self.redis_manager.lpop(recent_alerts_key)

            await self.redis_manager.rpush(
                recent_alerts_key,
                json.dumps({
                    'id': alert.id,
                    'endpoint': alert.endpoint,
                    'severity': alert.severity.value,
                    'message': alert.message,
                    'created_at': alert.created_at.isoformat()
                })
            )

        except Exception as e:
            logger.error(f"Error storing alert: {e}")

    async def _alert_worker(self):
        """Worker for processing alerts"""
        logger.info("Alert worker started")

        while True:
            try:
                # Process alert notifications
                await self._process_alert_notifications()

                # Clean up old resolved alerts
                await self._cleanup_old_alerts()

                # Wait for next cycle
                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Error in alert worker: {e}")
                await asyncio.sleep(60)

    async def _process_alert_notifications(self):
        """Process alert notifications"""
        try:
            # Get unacknowledged alerts
            recent_alerts = await self.redis_manager.lrange("recent_alerts", 0, -1)

            for alert_data in recent_alerts:
                alert = json.loads(alert_data)

                # Send notification if not acknowledged
                if not alert.get('acknowledged', False):
                    await self._send_alert_notification(alert)

        except Exception as e:
            logger.error(f"Error processing alert notifications: {e}")

    async def _send_alert_notification(self, alert_data: Dict[str, Any]):
        """Send alert notification"""
        try:
            # This would send notifications via email, Slack, etc.
            logger.warning(f"Alert notification: {alert_data['message']}")

            # For now, just log the alert
            if alert_data['severity'] in ['error', 'critical']:
                logger.error(f"CRITICAL ALERT: {alert_data['message']}")
            else:
                logger.warning(f"ALERT: {alert_data['message']}")

        except Exception as e:
            logger.error(f"Error sending alert notification: {e}")

    async def _cleanup_old_alerts(self):
        """Clean up old resolved alerts"""
        try:
            # This would clean up old alerts from database
            pass

        except Exception as e:
            logger.error(f"Error cleaning up old alerts: {e}")

    async def generate_sla_report(self, endpoint: str, start_date: datetime,
                                end_date: datetime, sla_category: str = "standard_services") -> SLAReport:
        """Generate SLA report for endpoint"""
        try:
            # Get SLA definition
            sla_def = self.sla_definitions.get(sla_category, self.sla_definitions['standard_services'])

            # Get metrics for the period
            metrics = await self.get_endpoint_metrics(endpoint, days=(end_date - start_date).days)

            if not metrics:
                return SLAReport(
                    endpoint=endpoint,
                    period_start=start_date,
                    period_end=end_date,
                    uptime_percentage=0.0,
                    average_response_time=0.0,
                    error_budget_used=0.0,
                    sla_compliant=False,
                    violations=[],
                    recommendations=["No data available for the specified period"]
                )

            # Calculate SLA metrics
            total_requests = sum(m.total_requests for m in metrics)
            successful_requests = sum(m.successful_requests for m in metrics)
            uptime_percentage = (successful_requests / total_requests) * 100 if total_requests > 0 else 0

            # Calculate average response time
            total_response_time = sum(m.average_response_time * m.total_requests for m in metrics)
            average_response_time = total_response_time / total_requests if total_requests > 0 else 0

            # Calculate error budget used
            error_budget_used = ((100 - uptime_percentage) / sla_def['error_budget']) * 100 if sla_def['error_budget'] > 0 else 0

            # Check SLA compliance
            sla_compliant = (
                uptime_percentage >= sla_def['uptime_target'] and
                average_response_time <= sla_def['response_time_target'] and
                error_budget_used <= 100
            )

            # Find violations
            violations = []
            if uptime_percentage < sla_def['uptime_target']:
                violations.append({
                    'type': 'uptime',
                    'target': sla_def['uptime_target'],
                    'actual': uptime_percentage,
                    'severity': 'critical' if uptime_percentage < 99 else 'warning'
                })

            if average_response_time > sla_def['response_time_target']:
                violations.append({
                    'type': 'response_time',
                    'target': sla_def['response_time_target'],
                    'actual': average_response_time,
                    'severity': 'warning'
                })

            # Generate recommendations
            recommendations = []
            if not sla_compliant:
                recommendations.append("SLA not met. Immediate action required.")
            if uptime_percentage < sla_def['uptime_target']:
                recommendations.append("Improve service reliability and reduce downtime.")
            if average_response_time > sla_def['response_time_target']:
                recommendations.append("Optimize performance to reduce response times.")
            if error_budget_used > 80:
                recommendations.append("Error budget nearly exhausted. Review error handling.")

            return SLAReport(
                endpoint=endpoint,
                period_start=start_date,
                period_end=end_date,
                uptime_percentage=uptime_percentage,
                average_response_time=average_response_time,
                error_budget_used=error_budget_used,
                sla_compliant=sla_compliant,
                violations=violations,
                recommendations=recommendations
            )

        except Exception as e:
            logger.error(f"Error generating SLA report: {e}")
            return SLAReport(
                endpoint=endpoint,
                period_start=start_date,
                period_end=end_date,
                uptime_percentage=0.0,
                average_response_time=0.0,
                error_budget_used=0.0,
                sla_compliant=False,
                violations=[],
                recommendations=[f"Error generating report: {str(e)}"]
            )

    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data for API monitoring"""
        dashboard_data = {
            'overall_health': APIStatus.HEALTHY,
            'total_endpoints': 0,
            'healthy_endpoints': 0,
            'degraded_endpoints': 0,
            'unhealthy_endpoints': 0,
            'recent_alerts': [],
            'performance_summary': {},
            'availability_summary': {}
        }

        try:
            # Get health status for all endpoints
            all_endpoints = []
            for category, endpoints in self.monitored_endpoints.items():
                for name, endpoint in endpoints.items():
                    all_endpoints.append((f"{category}.{name}", endpoint))

            dashboard_data['total_endpoints'] = len(all_endpoints)

            # Run health checks
            health_results = await asyncio.gather(
                *[self.run_health_check(endpoint) for _, endpoint in all_endpoints],
                return_exceptions=True
            )

            # Process health results
            for (name, endpoint), result in zip(all_endpoints, health_results):
                if isinstance(result, Exception):
                    dashboard_data['unhealthy_endpoints'] += 1
                else:
                    if result['status'] == APIStatus.HEALTHY:
                        dashboard_data['healthy_endpoints'] += 1
                    elif result['status'] == APIStatus.DEGRADED:
                        dashboard_data['degraded_endpoints'] += 1
                    else:
                        dashboard_data['unhealthy_endpoints'] += 1

            # Determine overall health
            if dashboard_data['unhealthy_endpoints'] > 0:
                dashboard_data['overall_health'] = APIStatus.UNHEALTHY
            elif dashboard_data['degraded_endpoints'] > dashboard_data['healthy_endpoints']:
                dashboard_data['overall_health'] = APIStatus.DEGRADED
            elif dashboard_data['degraded_endpoints'] > 0:
                dashboard_data['overall_health'] = APIStatus.DEGRADED

            # Get recent alerts
            recent_alerts = await self.redis_manager.lrange("recent_alerts", 0, 9)
            dashboard_data['recent_alerts'] = [json.loads(alert) for alert in recent_alerts]

            # Get performance summary
            all_metrics = []
            for name, endpoint in all_endpoints:
                metrics = await self.get_endpoint_metrics(endpoint, days=1)
                all_metrics.extend(metrics)

            if all_metrics:
                total_requests = sum(m.total_requests for m in all_metrics)
                successful_requests = sum(m.successful_requests for m in all_metrics)
                avg_response_time = statistics.mean([m.average_response_time for m in all_metrics if m.total_requests > 0])

                dashboard_data['performance_summary'] = {
                    'total_requests': total_requests,
                    'success_rate': (successful_requests / total_requests) * 100 if total_requests > 0 else 0,
                    'average_response_time': avg_response_time
                }

                dashboard_data['availability_summary'] = {
                    'overall_availability': (successful_requests / total_requests) * 100 if total_requests > 0 else 0,
                    'uptime_percentage': (successful_requests / total_requests) * 100 if total_requests > 0 else 0
                }

        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            dashboard_data['error'] = str(e)

        return dashboard_data

    async def start_monitoring(self):
        """Start continuous monitoring"""
        logger.info("Starting API monitoring system")

        # Start endpoint monitoring
        asyncio.create_task(self.monitor_endpoints())

        logger.info("API monitoring system started")

    async def stop_monitoring(self):
        """Stop continuous monitoring"""
        logger.info("Stopping API monitoring system")

        # Cancel all monitoring tasks
        for task in asyncio.all_tasks():
            if "monitor_endpoints" in str(task):
                task.cancel()

        logger.info("API monitoring system stopped")

    async def export_metrics(self, endpoint: str, start_date: datetime,
                           end_date: datetime, format: str = "json") -> str:
        """Export metrics data"""
        try:
            metrics = await self.get_endpoint_metrics(endpoint, days=(end_date - start_date).days)

            if format == "json":
                return json.dumps([{
                    'timestamp': m.timestamp.isoformat(),
                    'total_requests': m.total_requests,
                    'successful_requests': m.successful_requests,
                    'failed_requests': m.failed_requests,
                    'average_response_time': m.average_response_time,
                    'error_rate': m.error_rate,
                    'availability_percentage': m.availability_percentage
                } for m in metrics], indent=2)

            elif format == "csv":
                import csv
                import io

                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=[
                    'timestamp', 'total_requests', 'successful_requests', 'failed_requests',
                    'average_response_time', 'error_rate', 'availability_percentage'
                ])
                writer.writeheader()

                for m in metrics:
                    writer.writerow({
                        'timestamp': m.timestamp.isoformat(),
                        'total_requests': m.total_requests,
                        'successful_requests': m.successful_requests,
                        'failed_requests': m.failed_requests,
                        'average_response_time': m.average_response_time,
                        'error_rate': m.error_rate,
                        'availability_percentage': m.availability_percentage
                    })

                return output.getvalue()

            else:
                raise ValueError(f"Unsupported format: {format}")

        except Exception as e:
            logger.error(f"Error exporting metrics: {e}")
            return f"Error exporting metrics: {str(e)}"