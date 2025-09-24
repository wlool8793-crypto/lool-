import http from 'k6/http';
import ws from 'k6/ws';
import { check, sleep } from 'k6';
import { Rate, Counter, Trend } from 'k6/metrics';

// Custom metrics
export let errorRate = new Rate('errors');
export let requestCount = new Counter('requests');
export let apiResponseTime = new Trend('api_response_time');

// Test configuration
export let options = {
  stages: [
    { duration: '30s', target: 10 },   // Ramp up to 10 users
    { duration: '1m', target: 10 },    // Stay at 10 users
    { duration: '30s', target: 50 },   // Ramp up to 50 users
    { duration: '1m', target: 50 },    // Stay at 50 users
    { duration: '30s', target: 100 },  // Ramp up to 100 users
    { duration: '1m', target: 100 },   // Stay at 100 users
    { duration: '30s', target: 0 },    // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% of requests should be below 2s
    http_req_failed: ['rate<0.05'],     // Less than 5% errors
    errors: ['rate<0.05'],               // Less than 5% errors
  },
};

const BASE_URL = __ENV.TEST_URL || 'http://localhost:8000';
const API_KEY = __ENV.API_KEY || 'test-api-key';

export default function () {
  // Test health endpoint
  let healthRes = http.get(`${BASE_URL}/health`, {
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json',
    },
  });

  check(healthRes, {
    'health endpoint status is 200': (r) => r.status === 200,
    'health endpoint response time < 1s': (r) => r.timings.duration < 1000,
  });

  errorRate.add(healthRes.status >= 400);
  requestCount.add(1);
  apiResponseTime.add(healthRes.timings.duration);

  sleep(1);

  // Test API endpoints
  let testPayload = {
    message: 'Performance test message',
    user_id: 'perf-test-user',
    timestamp: new Date().toISOString(),
  };

  // Test chat endpoint
  let chatRes = http.post(`${BASE_URL}/api/v1/chat`, JSON.stringify(testPayload), {
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json',
    },
  });

  check(chatRes, {
    'chat endpoint status is 200': (r) => r.status === 200,
    'chat endpoint has response': (r) => r.json('response_id') !== undefined,
    'chat endpoint response time < 3s': (r) => r.timings.duration < 3000,
  });

  errorRate.add(chatRes.status >= 400);
  requestCount.add(1);
  apiResponseTime.add(chatRes.timings.duration);

  sleep(2);

  // Test agent execution endpoint
  let agentPayload = {
    task: 'Analyze performance metrics',
    context: {
      user_id: 'perf-test-user',
      session_id: 'perf-session-' + __VU,
    },
    tools: ['web_search', 'data_analysis'],
  };

  let agentRes = http.post(`${BASE_URL}/api/v1/agent/execute`, JSON.stringify(agentPayload), {
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json',
    },
  });

  check(agentRes, {
    'agent endpoint status is 200': (r) => r.status === 200,
    'agent endpoint has execution_id': (r) => r.json('execution_id') !== undefined,
    'agent endpoint response time < 5s': (r) => r.timings.duration < 5000,
  });

  errorRate.add(agentRes.status >= 400);
  requestCount.add(1);
  apiResponseTime.add(agentRes.timings.duration);

  sleep(3);

  // Test memory endpoint
  let memoryRes = http.get(`${BASE_URL}/api/v1/memory/perf-test-user`, {
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json',
    },
  });

  check(memoryRes, {
    'memory endpoint status is 200': (r) => r.status === 200,
    'memory endpoint response time < 2s': (r) => r.timings.duration < 2000,
  });

  errorRate.add(memoryRes.status >= 400);
  requestCount.add(1);
  apiResponseTime.add(memoryRes.timings.duration);

  sleep(1);
}

export function handleSummary(data) {
  return {
    'api-load-test-summary.json': JSON.stringify(data),
    stdout: `
    API Load Test Summary
    ====================

    Total Requests: ${data.metrics.http_reqs.values.count}
    Failed Requests: ${data.metrics.http_req_failed.values.count}
    Error Rate: ${(data.metrics.http_req_failed.values.rate * 100).toFixed(2)}%

    Response Times:
    - Min: ${data.metrics.http_req_duration.values.min}ms
    - Max: ${data.metrics.http_req_duration.values.max}ms
    - Avg: ${data.metrics.http_req_duration.values.avg}ms
    - p(95): ${data.metrics.http_req_duration.values['p(95)']}ms
    - p(99): ${data.metrics.http_req_duration.values['p(99)']}ms

    Custom Metrics:
    - Total API Requests: ${data.metrics.requests.values.count}
    - Error Rate: ${(data.metrics.errors.values.rate * 100).toFixed(2)}%
    - Avg API Response Time: ${data.metrics.api_response_time.values.avg}ms
    `,
  };
}