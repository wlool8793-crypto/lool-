import React from 'react';
import { HStack, Box, useColorMode } from '@chakra-ui/react';

const TypingIndicator: React.FC = () => {
  const { colorMode } = useColorMode();

  const dotColor = colorMode === 'dark' ? 'gray.400' : 'gray.600';

  return (
    <HStack spacing={1} py={2}>
      <Box
        w={2}
        h={2}
        borderRadius="full"
        bg={dotColor}
        className="pulse"
        style={{ animationDelay: '0s' }}
      />
      <Box
        w={2}
        h={2}
        borderRadius="full"
        bg={dotColor}
        className="pulse"
        style={{ animationDelay: '0.2s' }}
      />
      <Box
        w={2}
        h={2}
        borderRadius="full"
        bg={dotColor}
        className="pulse"
        style={{ animationDelay: '0.4s' }}
      />
    </HStack>
  );
};

export default TypingIndicator;