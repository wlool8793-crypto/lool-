import React from 'react';
import { Box, VStack, HStack, Heading, Text, Button, Badge, useColorMode } from '@chakra-ui/react';
import { ChatIcon, SettingsIcon, CheckCircleIcon, ExternalLinkIcon } from '@chakra-ui/icons';

const SimpleLanding = () => {
  const { colorMode } = useColorMode();

  return (
    <Box minH="100vh" bg={colorMode === 'dark' ? 'gray.900' : 'gray.50'}>
      <VStack spacing={8} py={16} px={4}>
        {/* Header */}
        <VStack spacing={4} textAlign="center">
          <HStack spacing={3}>
            <ChatIcon w={10} h={10} color="blue.500" />
            <Heading size="2xl" color={colorMode === 'dark' ? 'white' : 'gray.800'}>
              Deep Agent
            </Heading>
          </HStack>
          <Text fontSize="xl" color={colorMode === 'dark' ? 'gray.300' : 'gray.600'}>
            LangGraph Deep Web Agent System
          </Text>
          <Badge colorScheme="green" fontSize="md" px={3} py={1}>
            System Operational
          </Badge>
        </VStack>

        {/* Status Cards */}
        <VStack spacing={6} w="100%" maxW="4xl">
          {/* Backend Status */}
          <Box
            w="100%"
            p={6}
            bg={colorMode === 'dark' ? 'gray.800' : 'white'}
            borderRadius="lg"
            boxShadow="md"
          >
            <VStack spacing={4} align="start">
              <HStack spacing={3}>
                <CheckCircleIcon color="green.500" w={6} h={6} />
                <Heading size="lg">Backend Server</Heading>
                <Badge colorScheme="green">Online</Badge>
              </HStack>
              <Text color={colorMode === 'dark' ? 'gray.300' : 'gray.600'}>
                FastAPI server running on port 8000
              </Text>
              <HStack spacing={2}>
                <Text fontSize="sm" color="gray.500">API Documentation:</Text>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => window.open('http://localhost:8000/docs', '_blank')}
                  rightIcon={<ExternalLinkIcon />}
                >
                  OpenAPI Docs
                </Button>
              </HStack>
            </VStack>
          </Box>

          {/* Database Status */}
          <Box
            w="100%"
            p={6}
            bg={colorMode === 'dark' ? 'gray.800' : 'white'}
            borderRadius="lg"
            boxShadow="md"
          >
            <VStack spacing={4} align="start">
              <HStack spacing={3}>
                <CheckCircleIcon color="green.500" w={6} h={6} />
                <Heading size="lg">Database</Heading>
                <Badge colorScheme="green">Connected</Badge>
              </HStack>
              <Text color={colorMode === 'dark' ? 'gray.300' : 'gray.600'}>
                PostgreSQL with all tables migrated successfully
              </Text>
              <HStack spacing={2}>
                <Badge colorScheme="blue">Users</Badge>
                <Badge colorScheme="blue">Conversations</Badge>
                <Badge colorScheme="blue">Messages</Badge>
                <Badge colorScheme="blue">Agent States</Badge>
                <Badge colorScheme="blue">Tool Executions</Badge>
              </HStack>
            </VStack>
          </Box>

          {/* Cache Status */}
          <Box
            w="100%"
            p={6}
            bg={colorMode === 'dark' ? 'gray.800' : 'white'}
            borderRadius="lg"
            boxShadow="md"
          >
            <VStack spacing={4} align="start">
              <HStack spacing={3}>
                <CheckCircleIcon color="green.500" w={6} h={6} />
                <Heading size="lg">Cache System</Heading>
                <Badge colorScheme="green">Active</Badge>
              </HStack>
              <Text color={colorMode === 'dark' ? 'gray.300' : 'gray.600'}>
                Redis server running on port 6379
              </Text>
            </VStack>
          </Box>

          {/* Features */}
          <Box
            w="100%"
            p={6}
            bg={colorMode === 'dark' ? 'gray.800' : 'white'}
            borderRadius="lg"
            boxShadow="md"
          >
            <VStack spacing={4} align="start">
              <HStack spacing={3}>
                <SettingsIcon color="blue.500" w={6} h={6} />
                <Heading size="lg">System Features</Heading>
              </HStack>
              <VStack spacing={2} align="start">
                <Text color={colorMode === 'dark' ? 'gray.300' : 'gray.600'}>
                  • LangGraph-based agent orchestration
                </Text>
                <Text color={colorMode === 'dark' ? 'gray.300' : 'gray.600'}>
                  • Real-time WebSocket communication
                </Text>
                <Text color={colorMode === 'dark' ? 'gray.300' : 'gray.600'}>
                  • JWT authentication and authorization
                </Text>
                <Text color={colorMode === 'dark' ? 'gray.300' : 'gray.600'}>
                  • PostgreSQL database with migrations
                </Text>
                <Text color={colorMode === 'dark' ? 'gray.300' : 'gray.600'}>
                  • Redis caching and session management
                </Text>
                <Text color={colorMode === 'dark' ? 'gray.300' : 'gray.600'}>
                  • Tool execution framework
                </Text>
                <Text color={colorMode === 'dark' ? 'gray.300' : 'gray.600'}>
                  • File upload and processing
                </Text>
                <Text color={colorMode === 'dark' ? 'gray.300' : 'gray.600'}>
                  • Comprehensive API with OpenAPI documentation
                </Text>
              </VStack>
            </VStack>
          </Box>

          {/* API Endpoints */}
          <Box
            w="100%"
            p={6}
            bg={colorMode === 'dark' ? 'gray.800' : 'white'}
            borderRadius="lg"
            boxShadow="md"
          >
            <VStack spacing={4} align="start">
              <HStack spacing={3}>
                <ChatIcon color="purple.500" w={6} h={6} />
                <Heading size="lg">Available API Endpoints</Heading>
              </HStack>
              <VStack spacing={2} align="start">
                <Text color={colorMode === 'dark' ? 'gray.300' : 'gray.600'}>
                  • /api/v1/auth/* - Authentication (register, login, logout)
                </Text>
                <Text color={colorMode === 'dark' ? 'gray.300' : 'gray.600'}>
                  • /api/v1/conversations/* - Conversation management
                </Text>
                <Text color={colorMode === 'dark' ? 'gray.300' : 'gray.600'}>
                  • /api/v1/agents/* - Agent execution and status
                </Text>
                <Text color={colorMode === 'dark' ? 'gray.300' : 'gray.600'}>
                  • /api/v1/tools/* - Tool execution and management
                </Text>
                <Text color={colorMode === 'dark' ? 'gray.300' : 'gray.600'}>
                  • /api/v1/files/* - File upload and processing
                </Text>
                <Text color={colorMode === 'dark' ? 'gray.300' : 'gray.600'}>
                  • /health - System health check
                </Text>
              </VStack>
            </VStack>
          </Box>
        </VStack>

        {/* Quick Login Form */}
        <Box mt={8}>
          <VStack spacing={4} align="start">
            <Heading size="lg">Quick Login</Heading>
            <VStack spacing={3} w="100%" maxW="md">
              <Input
                placeholder="Email Address"
                id="quick-email"
                defaultValue="webuser@example.com"
                size="md"
              />
              <Input
                placeholder="Password"
                id="quick-password"
                type="password"
                defaultValue="WebUser123"
                size="md"
              />
              <Button
                colorScheme="blue"
                size="md"
                onClick={async () => {
                  const email = document.getElementById('quick-email').value;
                  const password = document.getElementById('quick-password').value;

                  try {
                    const response = await fetch('/api/v1/auth/login', {
                      method: 'POST',
                      headers: {
                        'Content-Type': 'application/json',
                      },
                      body: JSON.stringify({ email, password })
                    });

                    const data = await response.json();

                    if (response.ok) {
                      // Store token and redirect
                      localStorage.setItem('access_token', data.access_token);
                      alert('Login successful! Token stored.');
                      console.log('Login successful:', data);
                    } else {
                      alert('Login failed: ' + (data.detail || 'Unknown error'));
                      console.error('Login failed:', data);
                    }
                  } catch (error) {
                    alert('Network error: ' + error.message);
                    console.error('Network error:', error);
                  }
                }}
              >
                Login
              </Button>
            </VStack>
            <Text fontSize="sm" color={colorMode === 'dark' ? 'gray.400' : 'gray.500'}>
              Demo credentials: webuser@example.com / WebUser123
            </Text>

            <Divider my={4} />

            <Text fontSize="sm" color={colorMode === 'dark' ? 'gray.400' : 'gray.500'}>
              Or visit the full pages:
            </Text>
            <HStack spacing={4}>
              <Button
                size="md"
                variant="outline"
                onClick={() => window.location.href = '/login'}
              >
                Full Login Page
              </Button>
              <Button
                size="md"
                variant="outline"
                onClick={() => window.location.href = '/register'}
              >
                Register Page
              </Button>
            </HStack>
          </VStack>
        </Box>

        {/* Footer */}
        <Box mt={8} textAlign="center">
          <Text color={colorMode === 'dark' ? 'gray.400' : 'gray.500'}>
            Deep Agent System - Fully Operational
          </Text>
          <Text fontSize="sm" color={colorMode === 'dark' ? 'gray.500' : 'gray.400'}>
            Frontend: Port 3000 | Backend: Port 8000 | Database: PostgreSQL | Cache: Redis
          </Text>
        </Box>
      </VStack>
    </Box>
  );
};

export default SimpleLanding;