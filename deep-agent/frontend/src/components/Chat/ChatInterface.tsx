import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  VStack,
  HStack,
  Flex,
  Heading,
  Text,
  Button,
  Input,
  FormControl,
  IconButton,
  Avatar,
  Badge,
  Progress,
  useColorMode,
  Divider,
  Spacer,
} from '@chakra-ui/react';
import {
  ArrowUpIcon,
  ArrowLeftIcon,
  AttachmentIcon,
  PhoneIcon,
  SettingsIcon,
  ChevronDownIcon,
  ArrowRightIcon,
} from '@chakra-ui/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useAuth } from '../../contexts/AuthContext';
import { useWebSocketContext } from '../../contexts/WebSocketContext';
import { useToastContext } from '../../contexts/ToastContext';
import { conversationsApi, agentsApi } from '../../utils/api';
import { Conversation, Message, AgentExecuteRequest } from '../../types';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';
import AgentStatusPanel from './AgentStatusPanel';
import LoadingSpinner from '../Common/LoadingSpinner';

const ChatInterface: React.FC = () => {
  const { conversationId } = useParams<{ conversationId: string }>();
  const { colorMode } = useColorMode();
  const { user } = useAuth();
  const { connect, sendMessage, isConnected, joinConversation } = useWebSocketContext();
  const { showSuccess, showError } = useToastContext();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isAgentExecuting, setIsAgentExecuting] = useState(false);
  const [agentStatus, setAgentStatus] = useState<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const { data: conversation, isLoading: isLoadingConversation } = useQuery(
    ['conversation', conversationId],
    () => conversationsApi.getConversation(Number(conversationId)),
    {
      enabled: !!conversationId,
      onError: (error) => {
        showError('Error', 'Failed to load conversation');
        navigate('/dashboard');
      },
    }
  );

  const { data: conversationMessages, isLoading: isLoadingMessages } = useQuery(
    ['messages', conversationId],
    () => conversationsApi.getMessages(Number(conversationId)),
    {
      enabled: !!conversationId,
      onSuccess: (data) => {
        setMessages(data.data || []);
      },
      onError: (error) => {
        showError('Error', 'Failed to load messages');
      },
    }
  );

  const executeAgentMutation = useMutation(
    (data: AgentExecuteRequest) => agentsApi.executeAgent(data),
    {
      onSuccess: (response) => {
        setIsAgentExecuting(false);
        setAgentStatus(null);
        showSuccess('Agent Response', 'Your request has been processed');
      },
      onError: (error) => {
        setIsAgentExecuting(false);
        setAgentStatus(null);
        showError('Agent Error', 'Failed to process your request');
      },
    }
  );

  useEffect(() => {
    if (!isConnected) {
      connect();
    }
  }, [connect, isConnected]);

  useEffect(() => {
    if (conversationId && isConnected) {
      joinConversation(Number(conversationId));
    }
  }, [conversationId, isConnected, joinConversation]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (!message.trim() || !conversationId) return;

    const userMessage: Message = {
      id: Date.now(),
      conversation_id: Number(conversationId),
      role: 'user',
      content: message,
      message_type: 'text',
      created_at: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setMessage('');
    setIsLoading(true);

    try {
      // Send message via WebSocket
      sendMessage(Number(conversationId), message);

      // Execute agent
      setIsAgentExecuting(true);
      executeAgentMutation.mutate({
        conversation_id: Number(conversationId),
        message: message,
        agent_type: 'deep_web_agent',
        tools: ['web_search', 'document_processing', 'code_execution'],
      });
    } catch (error) {
      setIsLoading(false);
      setIsAgentExecuting(false);
      showError('Error', 'Failed to send message');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !conversationId) return;

    try {
      // Implement file upload logic
      const result = await conversationsApi.createMessage({
        conversation_id: Number(conversationId),
        role: 'user',
        content: `Uploaded file: ${file.name}`,
        message_type: 'file',
        metadata: { filename: file.name, size: file.size, type: file.type },
      });
      setMessages(prev => [...prev, result]);
    } catch (error) {
      showError('Error', 'Failed to upload file');
    }
  };

  const bgCard = colorMode === 'dark' ? 'gray.800' : 'white';
  const borderColor = colorMode === 'dark' ? 'gray.700' : 'gray.200';
  const textPrimary = colorMode === 'dark' ? 'white' : 'gray.800';
  const textSecondary = colorMode === 'dark' ? 'gray.400' : 'gray.600';

  if (isLoadingConversation || isLoadingMessages) {
    return (
      <Flex height="100vh" alignItems="center" justifyContent="center">
        <LoadingSpinner size="lg" />
      </Flex>
    );
  }

  return (
    <Flex height="100vh" bg={colorMode === 'dark' ? 'gray.900' : 'gray.50'}>
      {/* Sidebar */}
      <Box
        w="80px"
        bg={bgCard}
        borderRight="1px solid"
        borderColor={borderColor}
        display="flex"
        flexDirection="column"
        alignItems="center"
        py={4}
        gap={4}
      >
        <IconButton
          aria-label="Back to dashboard"
          icon={<ArrowLeftIcon />}
          onClick={() => navigate('/dashboard')}
          variant="ghost"
          color={textSecondary}
        />
        <Avatar
          size="sm"
          name={user?.full_name || user?.username}
          src={user?.avatar_url}
        />
        <IconButton
          aria-label="Settings"
          icon={<SettingsIcon />}
          variant="ghost"
          color={textSecondary}
        />
        <Spacer />
        <IconButton
          aria-label="More options"
          icon={<ChevronDownIcon />}
          variant="ghost"
          color={textSecondary}
        />
      </Box>

      {/* Main Chat Area */}
      <Flex flex={1} flexDirection="column">
        {/* Header */}
        <Box
          bg={bgCard}
          borderBottom="1px solid"
          borderColor={borderColor}
          p={4}
        >
          <HStack justify="space-between" align="center">
            <VStack align="start" spacing={1}>
              <Heading size="md" color={textPrimary}>
                {conversation?.title || 'New Conversation'}
              </Heading>
              <Text fontSize="sm" color={textSecondary}>
                {conversation?.created_at && new Date(conversation.created_at).toLocaleDateString()}
              </Text>
            </VStack>
            <HStack spacing={2}>
              <Badge colorScheme={isConnected ? 'green' : 'red'}>
                {isConnected ? 'Connected' : 'Disconnected'}
              </Badge>
              {isAgentExecuting && (
                <Badge colorScheme="yellow">
                  Agent Running
                </Badge>
              )}
            </HStack>
          </HStack>
        </Box>

        {/* Agent Status Panel */}
        {agentStatus && (
          <AgentStatusPanel status={agentStatus} />
        )}

        {/* Messages Area */}
        <Box flex={1} overflow="auto" p={4}>
          <VStack spacing={4} align="stretch" maxW="4xl" mx="auto">
            {messages.length === 0 ? (
              <VStack spacing={4} py={20}>
                <Text fontSize="lg" color={textSecondary}>
                  Start a conversation with your AI assistant
                </Text>
                <Text fontSize="sm" color={textSecondary}>
                  Ask questions, request analysis, or get help with your tasks
                </Text>
              </VStack>
            ) : (
              messages.map((msg) => (
                <MessageBubble key={msg.id} message={msg} />
              ))
            )}

            {isLoading && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </VStack>
        </Box>

        {/* Input Area */}
        <Box
          bg={bgCard}
          borderTop="1px solid"
          borderColor={borderColor}
          p={4}
        >
          <VStack spacing={3}>
            {isAgentExecuting && (
              <Progress
                size="xs"
                isIndeterminate
                colorScheme="blue"
                w="full"
              />
            )}

            <HStack spacing={2}>
              <Input
                ref={inputRef}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                bg={colorMode === 'dark' ? 'gray.700' : 'gray.50'}
                border={colorMode === 'dark' ? '1px solid' : '1px solid'}
                borderColor={colorMode === 'dark' ? 'gray.600' : 'gray.300'}
                color={textPrimary}
                _placeholder={{ color: colorMode === 'dark' ? 'gray.500' : 'gray.400' }}
                disabled={isLoading || isAgentExecuting}
              />
              <input
                type="file"
                id="file-upload"
                style={{ display: 'none' }}
                onChange={handleFileUpload}
                disabled={isLoading || isAgentExecuting}
              />
              <IconButton
                as="label"
                htmlFor="file-upload"
                aria-label="Upload file"
                icon={<AttachmentIcon />}
                variant="ghost"
                color={textSecondary}
                disabled={isLoading || isAgentExecuting}
                cursor="pointer"
              />
              <IconButton
                aria-label="Voice input"
                icon={<PhoneIcon />}
                variant="ghost"
                color={textSecondary}
                disabled={isLoading || isAgentExecuting}
              />
              <IconButton
                aria-label="Send message"
                icon={<ArrowRightIcon />}
                colorScheme="blue"
                onClick={handleSendMessage}
                disabled={!message.trim() || isLoading || isAgentExecuting}
                isLoading={isLoading || isAgentExecuting}
              />
            </HStack>
          </VStack>
        </Box>
      </Flex>
    </Flex>
  );
};

export default ChatInterface;