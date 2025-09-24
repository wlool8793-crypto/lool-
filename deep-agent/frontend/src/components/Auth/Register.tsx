import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import {
  Box,
  VStack,
  HStack,
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
  Checkbox,
} from '@chakra-ui/react';
import { ViewIcon, ViewOffIcon } from '@chakra-ui/icons';
import { useAuth } from '../../contexts/AuthContext';
import { useToastContext } from '../../contexts/ToastContext';
import { RegisterForm, RegisterData } from '../../types';
import LoadingSpinner from '../Common/LoadingSpinner';

const Register: React.FC = () => {
  const { colorMode } = useColorMode();
  const { register: registerUser, isLoading } = useAuth();
  const { showError, showSuccess } = useToastContext();
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [acceptTerms, setAcceptTerms] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<RegisterForm>();

  const password = watch('password');

  const onSubmit = async (data: RegisterForm) => {
    if (!acceptTerms) {
      showError('Terms Required', 'Please accept the terms and conditions');
      return;
    }

    try {
      const registerData: RegisterData = {
        email: data.email,
        username: data.username,
        password: data.password,
        full_name: data.full_name,
      };

      await registerUser(registerData);
      showSuccess('Registration Successful', 'Welcome to Deep Agent!');
      navigate('/dashboard');
    } catch (error: any) {
      const errorMessage = error.response?.data?.message || 'Registration failed';
      showError('Registration Failed', errorMessage);
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
              Create Account
            </Heading>
            <Text
              color={colorMode === 'dark' ? 'gray.400' : 'gray.600'}
              fontSize="sm"
            >
              Join Deep Agent and start building with AI
            </Text>
          </Box>

          <Box w="full">
            <form onSubmit={handleSubmit(onSubmit)}>
              <VStack spacing={4}>
                <FormControl isInvalid={!!errors.full_name}>
                  <FormLabel htmlFor="full_name" color={colorMode === 'dark' ? 'gray.300' : 'gray.700'}>
                    Full Name
                  </FormLabel>
                  <Input
                    id="full_name"
                    type="text"
                    placeholder="John Doe"
                    bg={colorMode === 'dark' ? 'gray.700' : 'gray.50'}
                    border={colorMode === 'dark' ? '1px solid' : '1px solid'}
                    borderColor={colorMode === 'dark' ? 'gray.600' : 'gray.300'}
                    color={colorMode === 'dark' ? 'white' : 'gray.800'}
                    _placeholder={{ color: colorMode === 'dark' ? 'gray.500' : 'gray.400' }}
                    {...register('full_name', {
                      required: 'Full name is required',
                      minLength: {
                        value: 2,
                        message: 'Full name must be at least 2 characters',
                      },
                    })}
                  />
                  <FormErrorMessage>{errors.full_name?.message}</FormErrorMessage>
                </FormControl>

                <FormControl isInvalid={!!errors.username}>
                  <FormLabel htmlFor="username" color={colorMode === 'dark' ? 'gray.300' : 'gray.700'}>
                    Username
                  </FormLabel>
                  <Input
                    id="username"
                    type="text"
                    placeholder="johndoe"
                    bg={colorMode === 'dark' ? 'gray.700' : 'gray.50'}
                    border={colorMode === 'dark' ? '1px solid' : '1px solid'}
                    borderColor={colorMode === 'dark' ? 'gray.600' : 'gray.300'}
                    color={colorMode === 'dark' ? 'white' : 'gray.800'}
                    _placeholder={{ color: colorMode === 'dark' ? 'gray.500' : 'gray.400' }}
                    {...register('username', {
                      required: 'Username is required',
                      minLength: {
                        value: 3,
                        message: 'Username must be at least 3 characters',
                      },
                      pattern: {
                        value: /^[a-zA-Z0-9_]+$/,
                        message: 'Username can only contain letters, numbers, and underscores',
                      },
                    })}
                  />
                  <FormErrorMessage>{errors.username?.message}</FormErrorMessage>
                </FormControl>

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
                      placeholder="Create a password"
                      bg={colorMode === 'dark' ? 'gray.700' : 'gray.50'}
                      border={colorMode === 'dark' ? '1px solid' : '1px solid'}
                      borderColor={colorMode === 'dark' ? 'gray.600' : 'gray.300'}
                      color={colorMode === 'dark' ? 'white' : 'gray.800'}
                      _placeholder={{ color: colorMode === 'dark' ? 'gray.500' : 'gray.400' }}
                      {...register('password', {
                        required: 'Password is required',
                        minLength: {
                          value: 8,
                          message: 'Password must be at least 8 characters',
                        },
                        pattern: {
                          value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
                          message: 'Password must contain at least one uppercase letter, one lowercase letter, and one number',
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

                <FormControl isInvalid={!!errors.confirm_password}>
                  <FormLabel htmlFor="confirm_password" color={colorMode === 'dark' ? 'gray.300' : 'gray.700'}>
                    Confirm Password
                  </FormLabel>
                  <InputGroup>
                    <Input
                      id="confirm_password"
                      type={showConfirmPassword ? 'text' : 'password'}
                      placeholder="Confirm your password"
                      bg={colorMode === 'dark' ? 'gray.700' : 'gray.50'}
                      border={colorMode === 'dark' ? '1px solid' : '1px solid'}
                      borderColor={colorMode === 'dark' ? 'gray.600' : 'gray.300'}
                      color={colorMode === 'dark' ? 'white' : 'gray.800'}
                      _placeholder={{ color: colorMode === 'dark' ? 'gray.500' : 'gray.400' }}
                      {...register('confirm_password', {
                        required: 'Please confirm your password',
                        validate: (value) =>
                          value === password || 'Passwords do not match',
                      })}
                    />
                    <InputRightElement h="full">
                      <Button
                        variant="ghost"
                        onClick={() => setShowConfirmPassword((showConfirmPassword) => !showConfirmPassword)}
                        color={colorMode === 'dark' ? 'gray.400' : 'gray.600'}
                      >
                        {showConfirmPassword ? <ViewOffIcon /> : <ViewIcon />}
                      </Button>
                    </InputRightElement>
                  </InputGroup>
                  <FormErrorMessage>{errors.confirm_password?.message}</FormErrorMessage>
                </FormControl>

                <FormControl>
                  <Checkbox
                    isChecked={acceptTerms}
                    onChange={(e) => setAcceptTerms(e.target.checked)}
                    color={colorMode === 'dark' ? 'gray.300' : 'gray.700'}
                  >
                    I accept the{' '}
                    <Text
                      as="span"
                      color="blue.500"
                      cursor="pointer"
                      _hover={{ textDecoration: 'underline' }}
                    >
                      Terms of Service
                    </Text>{' '}
                    and{' '}
                    <Text
                      as="span"
                      color="blue.500"
                      cursor="pointer"
                      _hover={{ textDecoration: 'underline' }}
                    >
                      Privacy Policy
                    </Text>
                  </Checkbox>
                </FormControl>

                <Button
                  type="submit"
                  w="full"
                  colorScheme="blue"
                  size="lg"
                  isLoading={isLoading}
                  className="btn-hover"
                >
                  Create Account
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
              Already have an account?{' '}
              <Link to="/login">
                <Text
                  as="span"
                  color="blue.500"
                  fontWeight="semibold"
                  cursor="pointer"
                  _hover={{ color: 'blue.600' }}
                >
                  Sign in
                </Text>
              </Link>
            </Text>
          </VStack>
        </VStack>
      </Box>
    </Flex>
  );
};

export default Register;