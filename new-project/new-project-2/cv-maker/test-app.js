#!/usr/bin/env node

const http = require('http');

// Test if the application is running
const options = {
  hostname: 'localhost',
  port: 3002,
  path: '/',
  method: 'GET',
  timeout: 5000
};

const req = http.request(options, (res) => {
  console.log(`Status Code: ${res.statusCode}`);
  console.log(`Content-Type: ${res.headers['content-type']}`);

  let data = '';
  res.on('data', (chunk) => {
    data += chunk;
  });

  res.on('end', () => {
    if (res.statusCode === 200) {
      console.log('✅ Application is running successfully');
      console.log('✅ HTML content detected');

      // Check for key indicators
      if (data.includes('CV Maker') || data.includes('Marriage Biodata')) {
        console.log('✅ Application content detected');
      } else {
        console.log('❌ Application content not found');
      }

      if (data.includes('React')) {
        console.log('✅ React application detected');
      }

    } else {
      console.log('❌ Application returned error status');
    }
  });
});

req.on('error', (e) => {
  console.error('❌ Application connection failed:', e.message);
});

req.on('timeout', () => {
  console.log('❌ Application request timed out');
  req.destroy();
});

req.end();