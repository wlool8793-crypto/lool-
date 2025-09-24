import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  VStack,
  HStack,
  Heading,
  Text,
  Button,
  Grid,
  GridItem,
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Progress,
  Badge,
  useColorMode,
  Flex,
  Icon,
  Divider,
  Avatar,
  Stack,
} from '@chakra-ui/react';
import {
  AddIcon,
  ChatIcon,
  TimeIcon,
  CheckCircleIcon,
  WarningIcon,
  ExternalLinkIcon,
  SettingsIcon,
  ViewIcon,
} from '@chakra-ui/icons';
import { useQuery } from 'react-query';
import { useAuth } from '../../contexts/AuthContext';
import { useWebSocketContext } from '../../contexts/WebSocketContext';
import { useToastContext } from '../../contexts/ToastContext';
import { conversationsApi, agentsApi, toolsApi } from '../../utils/api';
import { Conversation, AgentStatus } from '../../types';
import LoadingSpinner from '../Common/LoadingSpinner';
import ConversationCard from './ConversationCard';

const Dashboard: React.FC = () => {
  const { colorMode } = useColorMode();
  const { user } = useAuth();
  const { connect, isConnected } = useWebSocketContext();
  const { showError } = useToastContext();
  const navigate = useNavigate();
  const [recentConversations, setRecentConversations] = useState<Conversation[]>([]);
  const [agentStatus, setAgentStatus] = useState<AgentStatus | null>(null);

  const { data: conversations, isLoading: isLoadingConversations } = useQuery(
    'conversations',
    () => conversationsApi.getConversations({ limit: 10 }),
    {
      onSuccess: (data) => {
        setRecentConversations(data.data || []);
      },
      onError: (error) => {
        showError('Error', 'Failed to load conversations');
      },
    }
  );

  const { data: agents } = useQuery(
    'agents',
    () => agentsApi.getAgents(),
    {
      onError: (error) => {
        showError('Error', 'Failed to load agents');
      },
    }
  );

  const { data: tools } = useQuery(
    'tools',
    () => toolsApi.getTools(),
    {
      onError: (error) => {
        showError('Error', 'Failed to load tools');
      },
    }
  );

  const createNewConversation = async () => {
    try {
      const newConversation = await conversationsApi.createConversation({
        title: `New Conversation ${new Date().toLocaleDateString()}`,
      });
      navigate(`/chat/${newConversation.id}`);
    } catch (error) {
      showError('Error', 'Failed to create new conversation');
    }
  };

  const handleConversationClick = (conversationId: number) => {
    navigate(`/chat/${conversationId}`);
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const bgCard = colorMode === 'dark' ? 'gray.800' : 'white';
  const borderColor = colorMode === 'dark' ? 'gray.700' : 'gray.200';
  const textPrimary = colorMode === 'dark' ? 'white' : 'gray.800';
  const textSecondary = colorMode === 'dark' ? 'gray.400' : 'gray.600';

  if (isLoadingConversations) {
    return (
      <Box p={8}>
        <LoadingSpinner size="lg" />
      </Box>
    );
  }

  return (
    <Box p={8}>
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box>
          <Heading size="xl" color={textPrimary} mb={2}>
            {getGreeting()}, {user?.full_name || user?.username}
          </Heading>
          <Text color={textSecondary}>
            Welcome back to your AI assistant dashboard
          </Text>
        </Box>

        {/* Quick Stats */}
        <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(4, 1fr)' }} gap={6}>
          <Card bg={bgCard} borderColor={borderColor} borderWidth="1px">
            <CardBody>
              <Stat>
                <StatLabel color={textSecondary}>Total Conversations</StatLabel>
                <StatNumber color={textPrimary}>{conversations?.data?.length || 0}</StatNumber>
                <StatHelpText>
                  <StatArrow type="increase" />
                  23.36%
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={bgCard} borderColor={borderColor} borderWidth="1px">
            <CardBody>
              <Stat>
                <StatLabel color={textSecondary}>Active Agents</StatLabel>
                <StatNumber color={textPrimary}>{agents?.data?.length || 0}</StatNumber>
                <StatHelpText>
                  <StatArrow type="increase" />
                  12.5%
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={bgCard} borderColor={borderColor} borderWidth="1px">
            <CardBody>
              <Stat>
                <StatLabel color={textSecondary}>Available Tools</StatLabel>
                <StatNumber color={textPrimary}>{tools?.data?.length || 0}</StatNumber>
                <StatHelpText>
                  <StatArrow type="increase" />
                  8.2%
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={bgCard} borderColor={borderColor} borderWidth="1px">
            <CardBody>
              <Stat>
                <StatLabel color={textSecondary}>System Status</StatLabel>
                <StatNumber color={textPrimary}>
                  <HStack>
                    <Box
                      w={3}
                      h={3}
                      borderRadius="full"
                      bg={isConnected ? 'green.500' : 'red.500'}
                    />
                    {isConnected ? 'Online' : 'Offline'}
                  </HStack>
                </StatNumber>
                <StatHelpText>
                  <StatArrow type="increase" />
                  All systems operational
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Card bg={bgCard} borderColor={borderColor} borderWidth="1px">
          <CardHeader>
            <Heading size="md" color={textPrimary}>Quick Actions</Heading>
          </CardHeader>
          <CardBody>
            <HStack spacing={4} flexWrap="wrap">
              <Button
                leftIcon={<AddIcon />}
                colorScheme="blue"
                onClick={createNewConversation}
                size="lg"
              >
                New Conversation
              </Button>
              <Button
                leftIcon={<SettingsIcon />}
                variant="outline"
                onClick={() => navigate('/settings')}
                size="lg"
              >
                Settings
              </Button>
              <Button
                leftIcon={<ViewIcon />}
                variant="outline"
                onClick={() => navigate('/docs')}
                size="lg"
              >
                Documentation
              </Button>
            </HStack>
          </CardBody>
        </Card>

        {/* Recent Conversations */}
        <VStack spacing={4} align="stretch">
          <HStack justify="space-between" align="center">
            <Heading size="lg" color={textPrimary}>Recent Conversations</Heading>
            <Button
              variant="ghost"
              colorScheme="blue"
              onClick={() => navigate('/conversations')}
            >
              View All
            </Button>
          </HStack>

          {recentConversations.length > 0 ? (
            <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' }} gap={4}>
              {recentConversations.slice(0, 6).map((conversation) => (
                <ConversationCard
                  key={conversation.id}
                  conversation={conversation}
                  onClick={() => handleConversationClick(conversation.id)}
                />
              ))}
            </Grid>
          ) : (
            <Card bg={bgCard} borderColor={borderColor} borderWidth="1px" p={8}>
              <VStack spacing={4}>
                <ChatIcon w={12} h={12} color="gray.400" />
                <VStack spacing={2}>
                  <Heading size="md" color={textPrimary}>No conversations yet</Heading>
                  <Text color={textSecondary} textAlign="center">
                    Start a new conversation to begin chatting with your AI assistant
                  </Text>
                </VStack>
                <Button
                  leftIcon={<AddIcon />}
                  colorScheme="blue"
                  onClick={createNewConversation}
                >
                  Start New Conversation
                </Button>
              </VStack>
            </Card>
          )}
        </VStack>

        {/* Agent Status */}
        {agentStatus && (
          <Card bg={bgCard} borderColor={borderColor} borderWidth="1px">
            <CardHeader>
              <HStack justify="space-between">
                <Heading size="md" color={textPrimary}>Agent Status</Heading>
                <Badge colorScheme={agentStatus.status === 'running' ? 'green' : 'yellow'}>
                  {agentStatus.status}
                </Badge>
              </HStack>
            </CardHeader>
            <CardBody>
              <VStack spacing={3} align="stretch">
                <HStack justify="space-between">
                  <Text color={textSecondary}>Current Node</Text>
                  <Text color={textPrimary} fontFamily="monospace">
                    {agentStatus.current_node || 'N/A'}
                  </Text>
                </HStack>
                <HStack justify="space-between">
                  <Text color={textSecondary}>Execution Time</Text>
                  <Text color={textPrimary}>
                    {agentStatus.execution_time ? `${agentStatus.execution_time.toFixed(2)}s` : 'N/A'}
                  </Text>
                </HStack>
                {agentStatus.error_message && (
                  <HStack justify="space-between">
                    <Text color={textSecondary}>Error</Text>
                    <Text color="red.500">{agentStatus.error_message}</Text>
                  </HStack>
                )}
              </VStack>
            </CardBody>
          </Card>
        )}
      </VStack>
    </Box>
  );
};

export default Dashboard;