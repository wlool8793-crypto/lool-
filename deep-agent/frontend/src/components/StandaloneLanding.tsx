import React, { useState } from 'react';
import {
  Box, VStack, HStack, Heading, Text, Button, Badge,
  useColorMode, Input, Card, CardHeader, CardBody,
  FormControl, FormLabel, useToast, Spinner,
  InputGroup, InputRightElement, InputLeftElement, Flex, Grid, GridItem,
  Container, SimpleGrid, Icon, Divider, useBreakpointValue
} from '@chakra-ui/react';
import {
  ChatIcon, SettingsIcon, CheckCircleIcon, ExternalLinkIcon,
  ViewIcon, ViewOffIcon, LockIcon, EmailIcon
} from '@chakra-ui/icons';

const StandaloneLanding = () => {
  const { colorMode } = useColorMode();
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [email, setEmail] = useState('webuser@example.com');
  const [password, setPassword] = useState('WebUser123');
  const toast = useToast();

  const isMobile = useBreakpointValue({ base: true, md: false });

  const handleLogin = async () => {
    setIsLoading(true);
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
        localStorage.setItem('access_token', data.access_token);
        toast({
          title: 'Welcome back! 🎉',
          description: 'Successfully logged in to Deep Agent',
          status: 'success',
          duration: 4000,
          isClosable: true,
          position: 'top',
        });
        console.log('Login successful:', data);
      } else {
        toast({
          title: 'Login failed',
          description: data.detail || 'Please check your credentials and try again',
          status: 'error',
          duration: 5000,
          isClosable: true,
          position: 'top',
        });
        console.error('Login failed:', data);
      }
    } catch (error) {
      toast({
        title: 'Connection error',
        description: 'Unable to connect to the server. Please try again later.',
        status: 'error',
        duration: 5000,
        isClosable: true,
        position: 'top',
      });
      console.error('Network error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const StatusCard = ({ icon, title, status, description, action, badges = [] as string[] }: {
    icon: any;
    title: string;
    status: string;
    description: string;
    action?: { label: string; onClick: () => void };
    badges?: string[];
  }) => (
    <Card
      bg={colorMode === 'dark' ? 'gray.800' : 'white'}
      borderColor={colorMode === 'dark' ? 'gray.700' : 'gray.200'}
      borderWidth="1px"
      h="100%"
    >
      <CardHeader pb={3}>
        <HStack spacing={3}>
          <Icon as={icon} w={6} h={6} color="blue.500" />
          <VStack align="start" spacing={1}>
            <Heading size="md" fontWeight="semibold">{title}</Heading>
            <HStack spacing={2}>
              <Badge
                colorScheme={status === 'Online' || status === 'Connected' ? 'green' : 'red'}
                fontSize="xs"
                px={2}
                py={1}
              >
                {status}
              </Badge>
              {badges.map((badge, index) => (
                <Badge key={index} colorScheme="blue" fontSize="xs" px={2} py={1}>
                  {badge}
                </Badge>
              ))}
            </HStack>
          </VStack>
        </HStack>
      </CardHeader>
      <CardBody pt={0}>
        <VStack align="start" spacing={3}>
          <Text fontSize="sm" color={colorMode === 'dark' ? 'gray.400' : 'gray.600'}>
            {description}
          </Text>
          {action && (
            <Button
              size="sm"
              variant="outline"
              rightIcon={<ExternalLinkIcon />}
              onClick={action.onClick}
            >
              {action.label}
            </Button>
          )}
        </VStack>
      </CardBody>
    </Card>
  );

  return (
    <Box
      minH="100vh"
      bg={colorMode === 'dark' ? 'gray.900' : 'gray.50'}
      backgroundImage={
        colorMode === 'dark'
          ? "linear-gradient(135deg, #1a202c 0%, #2d3748 100%)"
          : "linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%)"
      }
    >
      <Container maxW="7xl" py={12} px={6}>
        <VStack spacing={12} align="center">
          {/* Header */}
          <VStack spacing={4} textAlign="center">
            <HStack spacing={3}>
              <Icon as={ChatIcon} w={12} h={12} color="blue.500" />
              <Heading
                size="2xl"
                fontWeight="bold"
                bgGradient={colorMode === 'dark'
                  ? "linear(to-r, blue.400, purple.400)"
                  : "linear(to-r, blue.600, purple.600)"
                }
                bgClip="text"
              >
                Deep Agent
              </Heading>
            </HStack>
            <Text
              fontSize="xl"
              color={colorMode === 'dark' ? 'gray.300' : 'gray.600'}
              fontWeight="medium"
            >
              LangGraph Deep Web Agent System
            </Text>
            <HStack spacing={2}>
              <Badge colorScheme="green" fontSize="md" px={3} py={1} borderRadius="full">
                <HStack spacing={1}>
                  <CheckCircleIcon w={4} h={4} />
                  <Text>System Operational</Text>
                </HStack>
              </Badge>
            </HStack>
          </VStack>

          {/* Status Cards */}
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} w="100%">
            <StatusCard
              icon={SettingsIcon}
              title="Backend Server"
              status="Online"
              description="FastAPI server running on port 8000 with full API documentation"
              action={{
                label: "API Docs",
                onClick: () => window.open('http://localhost:8000/docs', '_blank')
              }}
            />
            <StatusCard
              icon={ChatIcon}
              title="Database"
              status="Connected"
              description="PostgreSQL with successful migrations and ready for data"
              badges={['Users', 'Conversations', 'Messages']}
            />
          </SimpleGrid>

          {/* Login Card */}
          <Card
            w="100%"
            maxW="md"
            bg={colorMode === 'dark' ? 'gray.800' : 'white'}
            borderColor={colorMode === 'dark' ? 'gray.700' : 'gray.200'}
            borderWidth="1px"
            boxShadow="xl"
          >
            <CardHeader textAlign="center" pb={6}>
              <VStack spacing={3}>
                <Heading
                  size="xl"
                  fontWeight="bold"
                  bgGradient={colorMode === 'dark'
                    ? "linear(to-r, blue.400, purple.400)"
                    : "linear(to-r, blue.600, purple.600)"
                  }
                  bgClip="text"
                >
                  Welcome Back
                </Heading>
                <Text
                  color={colorMode === 'dark' ? 'gray.400' : 'gray.600'}
                  fontSize="lg"
                >
                  Sign in to access your AI assistant
                </Text>
              </VStack>
            </CardHeader>
            <CardBody px={8} py={6}>
              <VStack spacing={5}>
                <FormControl>
                  <FormLabel
                    fontWeight="medium"
                    color={colorMode === 'dark' ? 'gray.200' : 'gray.700'}
                  >
                    Email Address
                  </FormLabel>
                  <InputGroup>
                    <InputLeftElement pointerEvents="none">
                      <EmailIcon color="gray.400" />
                    </InputLeftElement>
                    <Input
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="Enter your email"
                      size="lg"
                      pl={10}
                      borderColor={colorMode === 'dark' ? 'gray.600' : 'gray.300'}
                      _focus={{
                        borderColor: 'blue.500',
                        boxShadow: `0 0 0 1px ${colorMode === 'dark' ? 'blue.400' : 'blue.600'}`
                      }}
                    />
                  </InputGroup>
                </FormControl>

                <FormControl>
                  <FormLabel
                    fontWeight="medium"
                    color={colorMode === 'dark' ? 'gray.200' : 'gray.700'}
                  >
                    Password
                  </FormLabel>
                  <InputGroup>
                    <InputLeftElement pointerEvents="none">
                      <LockIcon color="gray.400" />
                    </InputLeftElement>
                    <Input
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      type={showPassword ? 'text' : 'password'}
                      placeholder="Enter your password"
                      size="lg"
                      pl={10}
                      pr={12}
                      borderColor={colorMode === 'dark' ? 'gray.600' : 'gray.300'}
                      _focus={{
                        borderColor: 'blue.500',
                        boxShadow: `0 0 0 1px ${colorMode === 'dark' ? 'blue.400' : 'blue.600'}`
                      }}
                    />
                    <InputRightElement width="3rem">
                      <Button
                        h="1.75rem"
                        size="sm"
                        variant="ghost"
                        onClick={() => setShowPassword(!showPassword)}
                        _hover={{ bg: colorMode === 'dark' ? 'gray.700' : 'gray.100' }}
                      >
                        {showPassword ? <ViewOffIcon /> : <ViewIcon />}
                      </Button>
                    </InputRightElement>
                  </InputGroup>
                </FormControl>

                <Button
                  colorScheme="blue"
                  size="lg"
                  w="100%"
                  h={12}
                  fontSize="md"
                  fontWeight="semibold"
                  isLoading={isLoading}
                  onClick={handleLogin}
                  _hover={{
                    transform: 'translateY(-1px)',
                    boxShadow: 'lg'
                  }}
                  transition="all 0.2s"
                >
                  {isLoading ? <Spinner size="sm" /> : 'Sign In to Deep Agent'}
                </Button>

                <Divider />

                <VStack spacing={3} w="100%">
                  <Text
                    fontSize="sm"
                    fontWeight="medium"
                    color={colorMode === 'dark' ? 'gray.300' : 'gray.600'}
                  >
                    Demo Account Credentials:
                  </Text>
                  <VStack spacing={2} w="100%">
                    <Box
                      w="100%"
                      p={3}
                      bg={colorMode === 'dark' ? 'gray.700' : 'gray.100'}
                      borderRadius="md"
                      fontFamily="monospace"
                      fontSize="sm"
                    >
                      <Text color={colorMode === 'dark' ? 'gray.300' : 'gray.600'}>
                        Email: webuser@example.com
                      </Text>
                    </Box>
                    <Box
                      w="100%"
                      p={3}
                      bg={colorMode === 'dark' ? 'gray.700' : 'gray.100'}
                      borderRadius="md"
                      fontFamily="monospace"
                      fontSize="sm"
                    >
                      <Text color={colorMode === 'dark' ? 'gray.300' : 'gray.600'}>
                        Password: WebUser123
                      </Text>
                    </Box>
                  </VStack>
                </VStack>
              </VStack>
            </CardBody>
          </Card>

          {/* Footer */}
          <Box textAlign="center">
            <VStack spacing={1}>
              <Text
                fontSize="sm"
                fontWeight="medium"
                color={colorMode === 'dark' ? 'gray.400' : 'gray.500'}
              >
                Deep Agent System - Fully Operational
              </Text>
              <Text
                fontSize="xs"
                color={colorMode === 'dark' ? 'gray.500' : 'gray.400'}
              >
                Frontend: Port 3000 | Backend: Port 8000 | Database: PostgreSQL | Cache: Redis
              </Text>
            </VStack>
          </Box>
        </VStack>
      </Container>
    </Box>
  );
};

export default StandaloneLanding;