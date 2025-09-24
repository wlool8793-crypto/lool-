import React, { useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Flex,
  Avatar,
  Badge,
  Code,
  useColorMode,
  IconButton,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  useToast,
} from '@chakra-ui/react';
import {
  CopyIcon,
  CheckIcon,
  CloseIcon,
  ChevronDownIcon,
  RepeatIcon,
  DownloadIcon,
} from '@chakra-ui/icons';
import { Message } from '../../types';

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const { colorMode } = useColorMode();
  const toast = useToast();
  const [isCopied, setIsCopied] = useState(false);

  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  const bgBubble = isUser
    ? colorMode === 'dark' ? 'blue.900' : 'blue.50'
    : isSystem
    ? colorMode === 'dark' ? 'gray.700' : 'gray.100'
    : colorMode === 'dark' ? 'gray.800' : 'white';

  const textColor = isUser
    ? colorMode === 'dark' ? 'blue.100' : 'blue.900'
    : isSystem
    ? colorMode === 'dark' ? 'gray.300' : 'gray.700'
    : colorMode === 'dark' ? 'gray.100' : 'gray.800';

  const borderColor = colorMode === 'dark' ? 'gray.700' : 'gray.200';

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setIsCopied(true);
      toast({
        title: 'Copied to clipboard',
        status: 'success',
        duration: 2000,
        isClosable: true,
      });
      setTimeout(() => setIsCopied(false), 2000);
    } catch (error) {
      toast({
        title: 'Failed to copy',
        status: 'error',
        duration: 2000,
        isClosable: true,
      });
    }
  };

  const renderMessageContent = () => {
    const content = message.content;

    // Check if content contains code blocks
    const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
    const parts = [];
    let lastIndex = 0;
    let match;

    while ((match = codeBlockRegex.exec(content)) !== null) {
      // Add text before code block
      if (match.index > lastIndex) {
        parts.push({
          type: 'text',
          content: content.substring(lastIndex, match.index),
        });
      }

      // Add code block
      parts.push({
        type: 'code',
        language: match[1] || 'text',
        content: match[2],
      });

      lastIndex = match.index + match[0].length;
    }

    // Add remaining text
    if (lastIndex < content.length) {
      parts.push({
        type: 'text',
        content: content.substring(lastIndex),
      });
    }

    return parts.map((part, index) => {
      if (part.type === 'code') {
        return (
          <Box key={index} my={2}>
            <Code
              p={3}
              borderRadius="md"
              display="block"
              whiteSpace="pre-wrap"
              bg={colorMode === 'dark' ? 'gray.900' : 'gray.100'}
              color={colorMode === 'dark' ? 'gray.100' : 'gray.900'}
              fontSize="sm"
            >
              {part.content}
            </Code>
          </Box>
        );
      } else {
        return (
          <Text key={index} color={textColor} whiteSpace="pre-wrap" wordBreak="break-word">
            {part.content}
          </Text>
        );
      }
    });
  };

  const getMessageIcon = () => {
    if (isUser) return null;

    switch (message.message_type) {
      case 'tool_result':
        return <Badge colorScheme="green" variant="subtle">Tool Result</Badge>;
      case 'error':
        return <Badge colorScheme="red" variant="subtle">Error</Badge>;
      case 'system':
        return <Badge colorScheme="gray" variant="subtle">System</Badge>;
      case 'file':
        return <Badge colorScheme="blue" variant="subtle">File</Badge>;
      default:
        return <Badge colorScheme="purple" variant="subtle">AI</Badge>;
    }
  };

  return (
    <Flex
      justify={isUser ? 'flex-end' : 'flex-start'}
      mb={4}
      className="chat-message"
    >
      <VStack
        align={isUser ? 'flex-end' : 'flex-start'}
        maxW="70%"
        spacing={1}
      >
        {!isUser && (
          <HStack spacing={2} align="center">
            <Avatar size="xs" name="AI Assistant" />
            <Text fontSize="xs" color={colorMode === 'dark' ? 'gray.500' : 'gray.500'}>
              AI Assistant
            </Text>
          </HStack>
        )}

        <HStack align="flex-end" spacing={2}>
          {!isUser && getMessageIcon()}

          <Box
            bg={bgBubble}
            borderRadius="lg"
            px={4}
            py={3}
            borderWidth="1px"
            borderColor={borderColor}
            position="relative"
            maxW="100%"
          >
            <VStack align="stretch" spacing={2}>
              {renderMessageContent()}

              {message.metadata && Object.keys(message.metadata).length > 0 && (
                <Box
                  mt={2}
                  pt={2}
                  borderTop="1px solid"
                  borderColor={colorMode === 'dark' ? 'gray.600' : 'gray.300'}
                >
                  <Text fontSize="xs" color={colorMode === 'dark' ? 'gray.500' : 'gray.500'} mb={1}>
                    Metadata:
                  </Text>
                  {Object.entries(message.metadata).map(([key, value]) => (
                    <Text key={key} fontSize="xs" color={colorMode === 'dark' ? 'gray.400' : 'gray.600'}>
                      {key}: {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                    </Text>
                  ))}
                </Box>
              )}
            </VStack>

            {/* Message actions */}
            <HStack
              position="absolute"
              top={-6}
              right={isUser ? 0 : 'auto'}
              left={isUser ? 'auto' : 0}
              spacing={1}
              opacity={0}
              transition="opacity 0.2s"
              _groupHover={{ opacity: 1 }}
            >
              <IconButton
                aria-label="Copy message"
                icon={<CopyIcon />}
                size="xs"
                variant="ghost"
                color={colorMode === 'dark' ? 'gray.400' : 'gray.600'}
                onClick={copyToClipboard}
              />
              {!isUser && (
                <>
                  <IconButton
                    aria-label="Like"
                    icon={<CheckIcon />}
                    size="xs"
                    variant="ghost"
                    color={colorMode === 'dark' ? 'gray.400' : 'gray.600'}
                  />
                  <IconButton
                    aria-label="Dislike"
                    icon={<CloseIcon />}
                    size="xs"
                    variant="ghost"
                    color={colorMode === 'dark' ? 'gray.400' : 'gray.600'}
                  />
                  <IconButton
                    aria-label="Regenerate"
                    icon={<RepeatIcon />}
                    size="xs"
                    variant="ghost"
                    color={colorMode === 'dark' ? 'gray.400' : 'gray.600'}
                  />
                </>
              )}
            </HStack>
          </Box>

          <Menu>
            <MenuButton
              as={IconButton}
              aria-label="More options"
              icon={<ChevronDownIcon />}
              size="xs"
              variant="ghost"
              color={colorMode === 'dark' ? 'gray.400' : 'gray.600'}
            />
            <MenuList>
              <MenuItem icon={<CopyIcon />} onClick={copyToClipboard}>
                Copy
              </MenuItem>
              {!isUser && (
                <>
                  <MenuItem icon={<RepeatIcon />}>Regenerate</MenuItem>
                  <MenuItem icon={<DownloadIcon />}>Export</MenuItem>
                </>
              )}
            </MenuList>
          </Menu>
        </HStack>

        <Text fontSize="xs" color={colorMode === 'dark' ? 'gray.500' : 'gray.500'}>
          {formatTime(message.created_at)}
        </Text>
      </VStack>
    </Flex>
  );
};

export default MessageBubble;