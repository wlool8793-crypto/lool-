import React from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Badge,
  Progress,
  Divider,
  useColorMode,
  Flex,
  Icon,
  Circle,
  Stack,
} from '@chakra-ui/react';
import {
  CheckCircleIcon,
  TimeIcon,
  WarningIcon,
  CloseIcon,
  SpinnerIcon,
} from '@chakra-ui/icons';

interface AgentStatusPanelProps {
  status: {
    status: 'pending' | 'running' | 'completed' | 'failed' | 'stopped';
    current_node?: string;
    progress?: number;
    execution_time?: number;
    error_message?: string;
    tools_used?: string[];
    state_data?: Record<string, any>;
  };
}

const AgentStatusPanel: React.FC<AgentStatusPanelProps> = ({ status }) => {
  const { colorMode } = useColorMode();

  const getStatusInfo = () => {
    switch (status.status) {
      case 'pending':
        return {
          color: 'yellow',
          icon: TimeIcon,
          label: 'Pending',
        };
      case 'running':
        return {
          color: 'blue',
          icon: SpinnerIcon,
          label: 'Running',
        };
      case 'completed':
        return {
          color: 'green',
          icon: CheckCircleIcon,
          label: 'Completed',
        };
      case 'failed':
        return {
          color: 'red',
          icon: CloseIcon,
          label: 'Failed',
        };
      case 'stopped':
        return {
          color: 'orange',
          icon: WarningIcon,
          label: 'Stopped',
        };
      default:
        return {
          color: 'gray',
          icon: TimeIcon,
          label: 'Unknown',
        };
    }
  };

  const statusInfo = getStatusInfo();
  const bgCard = colorMode === 'dark' ? 'gray.800' : 'white';
  const borderColor = colorMode === 'dark' ? 'gray.700' : 'gray.200';
  const textPrimary = colorMode === 'dark' ? 'white' : 'gray.800';
  const textSecondary = colorMode === 'dark' ? 'gray.400' : 'gray.600';

  const formatExecutionTime = (seconds: number) => {
    if (seconds < 1) return `${(seconds * 1000).toFixed(0)}ms`;
    if (seconds < 60) return `${seconds.toFixed(2)}s`;
    return `${(seconds / 60).toFixed(1)}min`;
  };

  return (
    <Box
      bg={bgCard}
      borderBottom="1px solid"
      borderColor={borderColor}
      p={4}
    >
      <VStack spacing={3} align="stretch">
        <HStack justify="space-between" align="center">
          <HStack spacing={3}>
            <Circle size="8px" bg={`${statusInfo.color}.500`} className="pulse" />
            <Text fontWeight="semibold" color={textPrimary}>
              Agent Status
            </Text>
            <Badge colorScheme={statusInfo.color} variant="solid">
              {statusInfo.label}
            </Badge>
          </HStack>
          {status.execution_time !== undefined && (
            <Text fontSize="sm" color={textSecondary}>
              {formatExecutionTime(status.execution_time)}
            </Text>
          )}
        </HStack>

        {status.current_node && (
          <HStack spacing={2} align="center">
            <Icon as={statusInfo.icon} color={`${statusInfo.color}.500`} w={4} h={4} />
            <Text fontSize="sm" color={textSecondary}>
              Current Node:
            </Text>
            <Text
              fontSize="sm"
              color={textPrimary}
              fontFamily="monospace"
              fontWeight="medium"
            >
              {status.current_node}
            </Text>
          </HStack>
        )}

        {status.progress !== undefined && status.progress > 0 && (
          <VStack spacing={1} align="stretch">
            <HStack justify="space-between">
              <Text fontSize="sm" color={textSecondary}>
                Progress
              </Text>
              <Text fontSize="sm" color={textPrimary}>
                {Math.round(status.progress)}%
              </Text>
            </HStack>
            <Progress
              value={status.progress}
              size="sm"
              colorScheme={statusInfo.color}
              borderRadius="full"
            />
          </VStack>
        )}

        {status.tools_used && status.tools_used.length > 0 && (
          <VStack spacing={2} align="stretch">
            <Text fontSize="sm" color={textSecondary}>
              Tools Used:
            </Text>
            <HStack spacing={2} flexWrap="wrap">
              {status.tools_used.map((tool, index) => (
                <Badge
                  key={index}
                  colorScheme="blue"
                  variant="outline"
                  fontSize="xs"
                  px={2}
                  py={1}
                >
                  {tool}
                </Badge>
              ))}
            </HStack>
          </VStack>
        )}

        {status.error_message && (
          <Box>
            <Divider my={2} />
            <VStack spacing={2} align="stretch">
              <HStack spacing={2} align="center">
                <Icon as={CloseIcon} color="red.500" w={4} h={4} />
                <Text fontSize="sm" color={textSecondary} fontWeight="semibold">
                  Error
                </Text>
              </HStack>
              <Text
                fontSize="sm"
                color="red.500"
                bg={colorMode === 'dark' ? 'red.900' : 'red.50'}
                p={2}
                borderRadius="md"
                fontFamily="monospace"
              >
                {status.error_message}
              </Text>
            </VStack>
          </Box>
        )}

        {status.state_data && Object.keys(status.state_data).length > 0 && (
          <Box>
            <Divider my={2} />
            <VStack spacing={2} align="stretch">
              <Text fontSize="sm" color={textSecondary} fontWeight="semibold">
                State Information
              </Text>
              <Stack spacing={1}>
                {Object.entries(status.state_data).map(([key, value]) => (
                  <HStack key={key} spacing={2} align="start">
                    <Text fontSize="xs" color={textSecondary} minW="100px">
                      {key}:
                    </Text>
                    <Text
                      fontSize="xs"
                      color={textPrimary}
                      fontFamily="monospace"
                      flex={1}
                    >
                      {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                    </Text>
                  </HStack>
                ))}
              </Stack>
            </VStack>
          </Box>
        )}
      </VStack>
    </Box>
  );
};

export default AgentStatusPanel;