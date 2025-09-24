import React from 'react';
import { Card, CardHeader, CardBody, HStack, VStack, Text, Badge, Box, useColorMode } from '@chakra-ui/react';
import { TimeIcon } from '@chakra-ui/icons';
import { Conversation } from '../../types';

interface ConversationCardProps {
  conversation: Conversation;
  onClick: () => void;
}

const ConversationCard: React.FC<ConversationCardProps> = ({ conversation, onClick }) => {
  const { colorMode } = useColorMode();

  const bgCard = colorMode === 'dark' ? 'gray.800' : 'white';
  const borderColor = colorMode === 'dark' ? 'gray.700' : 'gray.200';
  const textPrimary = colorMode === 'dark' ? 'white' : 'gray.800';
  const textSecondary = colorMode === 'dark' ? 'gray.400' : 'gray.600';

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));

    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    if (diffInHours < 48) return 'Yesterday';
    return date.toLocaleDateString();
  };

  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  return (
    <Card
      bg={bgCard}
      borderColor={borderColor}
      borderWidth="1px"
      cursor="pointer"
      onClick={onClick}
      className="card-hover"
      transition="all 0.2s ease"
      _hover={{
        transform: 'translateY(-2px)',
        shadow: 'lg',
        borderColor: 'blue.500',
      }}
    >
      <CardHeader pb={2}>
        <HStack justify="space-between" align="start">
          <VStack align="start" spacing={1} flex={1}>
            <Text
              fontWeight="semibold"
              color={textPrimary}
              fontSize="md"
              noOfLines={1}
              className="text-ellipsis"
            >
              {conversation.title}
            </Text>
            <HStack spacing={2} align="center">
              <TimeIcon w={3} h={3} color={textSecondary} />
              <Text fontSize="xs" color={textSecondary}>
                {formatDate(conversation.created_at)}
              </Text>
            </HStack>
          </VStack>
          <Badge colorScheme="blue" variant="subtle" fontSize="xs">
            {conversation.message_count || 0} messages
          </Badge>
        </HStack>
      </CardHeader>

      <CardBody pt={0}>
        {conversation.last_message && (
          <VStack align="start" spacing={2}>
            <HStack align="center" spacing={2}>
              <TimeIcon w={3} h={3} color={textSecondary} />
              <Text
                fontSize="sm"
                color={textSecondary}
                noOfLines={2}
                className="text-break"
              >
                {truncateText(conversation.last_message, 80)}
              </Text>
            </HStack>
          </VStack>
        )}

        {conversation.metadata && Object.keys(conversation.metadata).length > 0 && (
          <Box mt={3}>
            <HStack spacing={2} flexWrap="wrap">
              {Object.entries(conversation.metadata)
                .filter(([key, value]) => value && typeof value === 'string')
                .slice(0, 2)
                .map(([key, value]) => (
                  <Badge
                    key={key}
                    colorScheme="gray"
                    variant="outline"
                    fontSize="xs"
                    px={2}
                    py={1}
                  >
                    {key}: {truncateText(value, 15)}
                  </Badge>
                ))}
            </HStack>
          </Box>
        )}
      </CardBody>
    </Card>
  );
};

export default ConversationCard;