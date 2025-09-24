import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import {
  Box,
  VStack,
  Heading,
  Text,
  Button,
  Input,
  FormControl,
  FormLabel,
  FormErrorMessage,
  InputGroup,
  InputRightElement,
  Divider,
  useColorMode,
  Flex,
} from '@chakra-ui/react';
import { ViewIcon, ViewOffIcon } from '@chakra-ui/icons';
import { useAuth } from '../../contexts/AuthContext';
import { useToastContext } from '../../contexts/ToastContext';
import { LoginCredentials } from '../../types';
import LoadingSpinner from '../Common/LoadingSpinner';

const Login: React.FC = () => {
  const { colorMode } = useColorMode();
  const { login, isLoading } = useAuth();
  const { showError } = useToastContext();
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginCredentials>();

  const onSubmit = async (data: LoginCredentials) => {
    try {
      console.log('Attempting login with:', data);
      await login(data);
      navigate('/dashboard');
    } catch (error) {
      console.error('Login error:', error);
      showError('Login Failed', 'Please check your credentials and try again');
    }
  };

  if (isLoading) {
    return (
      <Flex height="100vh" alignItems="center" justifyContent="center">
        <LoadingSpinner size="lg" />
      </Flex>
    );
  }

  return (
    <Flex
      minH="100vh"
      align="center"
      justify="center"
      bg={colorMode === 'dark' ? 'gray.900' : 'gray.50'}
    >
      <Box
        w="full"
        maxW="md"
        p={8}
        bg={colorMode === 'dark' ? 'gray.800' : 'white'}
        rounded="lg"
        shadow="xl"
        borderWidth="1px"
        borderColor={colorMode === 'dark' ? 'gray.700' : 'gray.200'}
      >
        <VStack spacing={6}>
          <Box textAlign="center">
            <Heading
              size="xl"
              color={colorMode === 'dark' ? 'white' : 'gray.800'}
              mb={2}
            >
              Deep Agent
            </Heading>
            <Text
              color={colorMode === 'dark' ? 'gray.400' : 'gray.600'}
              fontSize="sm"
            >
              Advanced AI Assistant Platform
            </Text>
          </Box>

          <Box w="full">
            <form onSubmit={handleSubmit(onSubmit)}>
              <VStack spacing={4}>
                <FormControl isInvalid={!!errors.email}>
                  <FormLabel htmlFor="email" color={colorMode === 'dark' ? 'gray.300' : 'gray.700'}>
                    Email Address
                  </FormLabel>
                  <Input
                    id="email"
                    type="email"
                    placeholder="you@example.com"
                    bg={colorMode === 'dark' ? 'gray.700' : 'gray.50'}
                    border={colorMode === 'dark' ? '1px solid' : '1px solid'}
                    borderColor={colorMode === 'dark' ? 'gray.600' : 'gray.300'}
                    color={colorMode === 'dark' ? 'white' : 'gray.800'}
                    _placeholder={{ color: colorMode === 'dark' ? 'gray.500' : 'gray.400' }}
                    {...register('email', {
                      required: 'Email is required',
                      pattern: {
                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                        message: 'Invalid email address',
                      },
                    })}
                  />
                  <FormErrorMessage>{errors.email?.message}</FormErrorMessage>
                </FormControl>

                <FormControl isInvalid={!!errors.password}>
                  <FormLabel htmlFor="password" color={colorMode === 'dark' ? 'gray.300' : 'gray.700'}>
                    Password
                  </FormLabel>
                  <InputGroup>
                    <Input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      placeholder="Enter your password"
                      bg={colorMode === 'dark' ? 'gray.700' : 'gray.50'}
                      border={colorMode === 'dark' ? '1px solid' : '1px solid'}
                      borderColor={colorMode === 'dark' ? 'gray.600' : 'gray.300'}
                      color={colorMode === 'dark' ? 'white' : 'gray.800'}
                      _placeholder={{ color: colorMode === 'dark' ? 'gray.500' : 'gray.400' }}
                      {...register('password', {
                        required: 'Password is required',
                        minLength: {
                          value: 6,
                          message: 'Password must be at least 6 characters',
                        },
                      })}
                    />
                    <InputRightElement h="full">
                      <Button
                        variant="ghost"
                        onClick={() => setShowPassword((showPassword) => !showPassword)}
                        color={colorMode === 'dark' ? 'gray.400' : 'gray.600'}
                      >
                        {showPassword ? <ViewOffIcon /> : <ViewIcon />}
                      </Button>
                    </InputRightElement>
                  </InputGroup>
                  <FormErrorMessage>{errors.password?.message}</FormErrorMessage>
                </FormControl>

                <Button
                  type="submit"
                  w="full"
                  colorScheme="blue"
                  size="lg"
                  isLoading={isLoading}
                  className="btn-hover"
                >
                  Sign In
                </Button>
              </VStack>
            </form>
          </Box>

          <Divider />

          <VStack w="full" spacing={3}>
            <Text
              fontSize="sm"
              color={colorMode === 'dark' ? 'gray.400' : 'gray.600'}
              textAlign="center"
            >
              Don't have an account?{' '}
              <Link to="/register">
                <Text
                  as="span"
                  color="blue.500"
                  fontWeight="semibold"
                  cursor="pointer"
                  _hover={{ color: 'blue.600' }}
                >
                  Sign up
                </Text>
              </Link>
            </Text>

            <Button
              variant="outline"
              w="full"
              size="sm"
              onClick={() => {
                // Demo login functionality
                onSubmit({
                  email: 'demo@example.com',
                  password: 'Demo12345',
                });
              }}
              colorScheme="gray"
            >
              Demo Account
            </Button>
          </VStack>
        </VStack>
      </Box>
    </Flex>
  );
};

export default Login;