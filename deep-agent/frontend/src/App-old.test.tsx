import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { ChakraProvider, Box, useColorMode } from '@chakra-ui/react';
import SimpleLanding from './components/SimpleLanding';

const AppContent: React.FC = () => {
  const { colorMode } = useColorMode();

  return (
    <Box minH="100vh" bg={colorMode === 'dark' ? 'gray.900' : 'gray.50'}>
      <Routes>
        <Route path="/" element={<SimpleLanding />} />
        <Route path="*" element={<SimpleLanding />} />
      </Routes>
    </Box>
  );
};

export default AppContent;