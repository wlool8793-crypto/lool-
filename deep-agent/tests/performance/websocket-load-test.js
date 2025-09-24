import ws from 'k6/ws';
import { check, sleep } from 'k6';
import { Rate, Counter, Trend } from 'k6/metrics';

// Custom metrics for WebSocket testing
export let wsConnectionRate = new Rate('ws_connections');
export let wsMessageRate = new Rate('ws_messages');
export let wsErrorRate = new Rate('ws_errors');
export let wsResponseTime = new Trend('ws_response_time');
export let wsConnectionTime = new Trend('ws_connection_time');

// Test configuration
export let options = {
  stages: [
    { duration: '30s', target: 20 },   // Ramp up to 20 concurrent connections
    { duration: '1m', target: 20 },    // Stay at 20 connections
    { duration: '30s', target: 50 },   // Ramp up to 50 connections
    { duration: '1m', target: 50 },    // Stay at 50 connections
    { duration: '30s', target: 100 },  // Ramp up to 100 connections
    { duration: '1m', target: 100 },   // Stay at 100 connections
    { duration: '30s', target: 0 },    // Ramp down to 0 connections
  ],
  thresholds: {
    ws_connection_time: ['p(95)<5000'], // 95% of connections should establish within 5s
    ws_response_time: ['p(95)<1000'],   // 95% of messages should get response within 1s
    ws_errors: ['rate<0.05'],           // Less than 5% errors
  },
};

const WS_URL = __ENV.WS_URL || 'ws://localhost:8000/ws/chat';
const API_KEY = __ENV.API_KEY || 'test-api-key';

export default function () {
  const connectionStartTime = Date.now();
  let connected = false;
  let messageReceived = false;
  let responseTime = 0;

  // Test WebSocket connection
  const res = ws.connect(WS_URL, {
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
    },
  }, function (socket) {
    socket.on('open', () => {
      console.log('WebSocket connected');
      connected = true;
      wsConnectionTime.add(Date.now() - connectionStartTime);
      wsConnectionRate.add(true);

      // Send test message
      const messageStartTime = Date.now();
      const testMessage = {
        type: 'chat',
        message: 'Performance test WebSocket message',
        user_id: `perf-test-user-${__VU}`,
        session_id: `perf-session-${__VU}-${__ITER}`,
        timestamp: new Date().toISOString(),
      };

      socket.send(JSON.stringify(testMessage));

      socket.on('message', (message) => {
        const messageEndTime = Date.now();
        responseTime = messageEndTime - messageStartTime;
        wsResponseTime.add(responseTime);
        wsMessageRate.add(true);
        messageReceived = true;

        console.log(`Received message: ${message}`);

        // Send another message to test bidirectional communication
        if (__ITER < 5) { // Limit messages per test
          setTimeout(() => {
            const followUpMessage = {
              type: 'follow_up',
              message: `Follow-up message ${__ITER}`,
              user_id: `perf-test-user-${__VU}`,
              session_id: `perf-session-${__VU}-${__ITER}`,
              timestamp: new Date().toISOString(),
            };
            socket.send(JSON.stringify(followUpMessage));
          }, 1000);
        }
      });

      socket.on('error', (error) => {
        console.log(`WebSocket error: ${error}`);
        wsErrorRate.add(true);
        wsConnectionRate.add(false);
      });

      socket.on('close', () => {
        console.log('WebSocket closed');
        if (!connected) {
          wsConnectionRate.add(false);
        }
      });

      // Test message rate
      let messageCount = 0;
      const messageInterval = setInterval(() => {
        if (messageCount < 10) { // Send 10 messages per connection
          const rateTestMessage = {
            type: 'rate_test',
            message: `Rate test message ${messageCount}`,
            user_id: `perf-test-user-${__VU}`,
            session_id: `perf-session-${__VU}-${__ITER}`,
            timestamp: new Date().toISOString(),
          };
          socket.send(JSON.stringify(rateTestMessage));
          messageCount++;
        } else {
          clearInterval(messageInterval);
        }
      }, 2000); // Send message every 2 seconds

      // Keep connection open for test duration
      setTimeout(() => {
        clearInterval(messageInterval);
        socket.close();
      }, 30000); // Close after 30 seconds
    });
  });

  check(res, {
    'WebSocket connection established': (r) => r && r.status === 101,
    'WebSocket connected successfully': () => connected,
    'At least one message received': () => messageReceived,
    'WebSocket response time < 1s': () => responseTime > 0 && responseTime < 1000,
  });

  sleep(1);
}

export function handleSummary(data) {
  return {
    'websocket-load-test-summary.json': JSON.stringify(data),
    stdout: `
    WebSocket Load Test Summary
    ==========================

    Connection Stats:
    - Total Connection Attempts: ${data.metrics.ws_connections.values.count}
    - Successful Connections: ${data.metrics.ws_connections.values.count * data.metrics.ws_connections.values.rate}
    - Connection Success Rate: ${(data.metrics.ws_connections.values.rate * 100).toFixed(2)}%

    Message Stats:
    - Total Messages Sent: ${data.metrics.ws_messages.values.count}
    - Messages Received: ${data.metrics.ws_messages.values.count}
    - Message Success Rate: ${(data.metrics.ws_messages.values.rate * 100).toFixed(2)}%

    Performance Metrics:
    - Avg Connection Time: ${data.metrics.ws_connection_time.values.avg}ms
    - p(95) Connection Time: ${data.metrics.ws_connection_time.values['p(95)']}ms
    - Avg Response Time: ${data.metrics.ws_response_time.values.avg}ms
    - p(95) Response Time: ${data.metrics.ws_response_time.values['p(95)']}ms
    - Error Rate: ${(data.metrics.ws_errors.values.rate * 100).toFixed(2)}%

    VU Stats:
    - Max VUs: ${data.metrics.vus_max.values.max}
    - Min VUs: ${data.metrics.vus_max.values.min}
    `,
  };
}