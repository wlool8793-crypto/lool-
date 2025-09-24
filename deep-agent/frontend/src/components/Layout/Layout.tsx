import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  VStack,
  HStack,
  Flex,
  Heading,
  Text,
  Button,
  Avatar,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  MenuDivider,
  IconButton,
  useColorMode,
  useDisclosure,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  Badge,
  useToast,
} from '@chakra-ui/react';
import {
  HamburgerIcon,
  CloseIcon,
  MoonIcon,
  SunIcon,
  SettingsIcon,
  BellIcon,
  ChatIcon,
  ViewIcon,
  ArrowRightIcon,
} from '@chakra-ui/icons';
import { useAuth } from '../../contexts/AuthContext';
import { useWebSocketContext } from '../../contexts/WebSocketContext';
import { useToastContext } from '../../contexts/ToastContext';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { colorMode, toggleColorMode } = useColorMode();
  const { user, logout } = useAuth();
  const { isConnected } = useWebSocketContext();
  const { showSuccess } = useToastContext();
  const navigate = useNavigate();
  const location = useLocation();
  const { isOpen, onOpen, onClose } = useDisclosure();

  const handleLogout = () => {
    logout();
    showSuccess('Logged Out', 'You have been successfully logged out');
    navigate('/login');
  };

  const navigationItems = [
    { name: 'Dashboard', icon: ViewIcon, path: '/dashboard' },
    { name: 'New Chat', icon: ChatIcon, path: '/chat/new' },
  ];

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  return (
    <Box minH="100vh" bg={colorMode === 'dark' ? 'gray.900' : 'gray.50'}>
      {/* Desktop Header */}
      <Box
        display={{ base: 'none', md: 'block' }}
        bg={colorMode === 'dark' ? 'gray.800' : 'white'}
        borderBottom="1px solid"
        borderColor={colorMode === 'dark' ? 'gray.700' : 'gray.200'}
        px={6}
        py={4}
      >
        <Flex align="center" justify="space-between">
          <HStack spacing={8}>
            <HStack align="center" spacing={3}>
              <ChatIcon w={8} h={8} color="blue.500" />
              <Heading size="lg" color={colorMode === 'dark' ? 'white' : 'gray.800'}>
                Deep Agent
              </Heading>
            </HStack>

            <HStack spacing={4}>
              {navigationItems.map((item) => (
                <Button
                  key={item.name}
                  variant="ghost"
                  color={isActive(item.path) ? 'blue.500' : colorMode === 'dark' ? 'gray.300' : 'gray.600'}
                  _hover={{ color: 'blue.500' }}
                  leftIcon={<item.icon />}
                  onClick={() => navigate(item.path)}
                >
                  {item.name}
                </Button>
              ))}
            </HStack>
          </HStack>

          <HStack spacing={4}>
            {/* Connection Status */}
            <HStack spacing={2}>
              <Box
                w={2}
                h={2}
                borderRadius="full"
                bg={isConnected ? 'green.500' : 'red.500'}
                className={isConnected ? 'pulse' : ''}
              />
              <Text fontSize="xs" color={colorMode === 'dark' ? 'gray.400' : 'gray.600'}>
                {isConnected ? 'Connected' : 'Disconnected'}
              </Text>
            </HStack>

            {/* Theme Toggle */}
            <IconButton
              aria-label="Toggle theme"
              icon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
              onClick={toggleColorMode}
              variant="ghost"
              color={colorMode === 'dark' ? 'gray.300' : 'gray.600'}
            />

            {/* Notifications */}
            <IconButton
              aria-label="Notifications"
              icon={<BellIcon />}
              variant="ghost"
              color={colorMode === 'dark' ? 'gray.300' : 'gray.600'}
            />

            {/* User Menu */}
            <Menu>
              <MenuButton
                as={Button}
                variant="ghost"
                p={1}
                rounded="full"
              >
                <Avatar
                  size="sm"
                  name={user?.full_name || user?.username}
                  src={user?.avatar_url}
                />
              </MenuButton>
              <MenuList bg={colorMode === 'dark' ? 'gray.800' : 'white'}>
                <Box px={3} py={2}>
                  <Text fontWeight="semibold" color={colorMode === 'dark' ? 'white' : 'gray.800'}>
                    {user?.full_name || user?.username}
                  </Text>
                  <Text fontSize="sm" color={colorMode === 'dark' ? 'gray.400' : 'gray.600'}>
                    {user?.email}
                  </Text>
                </Box>
                <MenuDivider />
                <MenuItem
                  icon={<SettingsIcon />}
                  onClick={() => navigate('/settings')}
                  color={colorMode === 'dark' ? 'gray.300' : 'gray.700'}
                >
                  Settings
                </MenuItem>
                <MenuItem
                  icon={<ArrowRightIcon />}
                  onClick={handleLogout}
                  color={colorMode === 'dark' ? 'gray.300' : 'gray.700'}
                >
                  Logout
                </MenuItem>
              </MenuList>
            </Menu>
          </HStack>
        </Flex>
      </Box>

      {/* Mobile Header */}
      <Box
        display={{ base: 'block', md: 'none' }}
        bg={colorMode === 'dark' ? 'gray.800' : 'white'}
        borderBottom="1px solid"
        borderColor={colorMode === 'dark' ? 'gray.700' : 'gray.200'}
        px={4}
        py={3}
      >
        <Flex align="center" justify="space-between">
          <HStack spacing={3}>
            <IconButton
              aria-label="Open menu"
              icon={<HamburgerIcon />}
              onClick={onOpen}
              variant="ghost"
              color={colorMode === 'dark' ? 'gray.300' : 'gray.600'}
            />
            <ChatIcon w={6} h={6} color="blue.500" />
            <Heading size="md" color={colorMode === 'dark' ? 'white' : 'gray.800'}>
              Deep Agent
            </Heading>
          </HStack>

          <HStack spacing={2}>
            <Box
              w={2}
              h={2}
              borderRadius="full"
              bg={isConnected ? 'green.500' : 'red.500'}
              className={isConnected ? 'pulse' : ''}
            />
            <Avatar
              size="sm"
              name={user?.full_name || user?.username}
              src={user?.avatar_url}
            />
          </HStack>
        </Flex>
      </Box>

      {/* Mobile Drawer */}
      <Drawer isOpen={isOpen} placement="left" onClose={onClose}>
        <DrawerOverlay>
          <DrawerContent bg={colorMode === 'dark' ? 'gray.800' : 'white'}>
            <DrawerCloseButton color={colorMode === 'dark' ? 'gray.300' : 'gray.600'} />
            <DrawerHeader>
              <VStack align="start" spacing={2}>
                <Text fontWeight="semibold" color={colorMode === 'dark' ? 'white' : 'gray.800'}>
                  {user?.full_name || user?.username}
                </Text>
                <Text fontSize="sm" color={colorMode === 'dark' ? 'gray.400' : 'gray.600'}>
                  {user?.email}
                </Text>
              </VStack>
            </DrawerHeader>
            <DrawerBody>
              <VStack align="start" spacing={4}>
                {navigationItems.map((item) => (
                  <Button
                    key={item.name}
                    variant="ghost"
                    color={isActive(item.path) ? 'blue.500' : colorMode === 'dark' ? 'gray.300' : 'gray.600'}
                    _hover={{ color: 'blue.500' }}
                    leftIcon={<item.icon />}
                    w="full"
                    justifyContent="flex-start"
                    onClick={() => {
                      navigate(item.path);
                      onClose();
                    }}
                  >
                    {item.name}
                  </Button>
                ))}
                <Button
                  variant="ghost"
                  color={colorMode === 'dark' ? 'gray.300' : 'gray.600'}
                  _hover={{ color: 'blue.500' }}
                  leftIcon={<SettingsIcon />}
                  w="full"
                  justifyContent="flex-start"
                  onClick={() => {
                    navigate('/settings');
                    onClose();
                  }}
                >
                  Settings
                </Button>
                <Button
                  variant="ghost"
                  color={colorMode === 'dark' ? 'gray.300' : 'gray.600'}
                  _hover={{ color: 'red.500' }}
                  leftIcon={<ArrowRightIcon />}
                  w="full"
                  justifyContent="flex-start"
                  onClick={handleLogout}
                >
                  Logout
                </Button>
              </VStack>
            </DrawerBody>
          </DrawerContent>
        </DrawerOverlay>
      </Drawer>

      {/* Main Content */}
      <Box>
        <Outlet />
      </Box>
    </Box>
  );
};

export default Layout;