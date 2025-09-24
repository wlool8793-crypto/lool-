import React, { createContext, useContext, useEffect, useRef, useState } from 'react';
import { useWebSocket } from '../utils/websocket';
import { AgentUpdateMessage, ToolUpdateMessage, MessageUpdateMessage, WebSocketMessage } from '../types';
import { useToast } from '@chakra-ui/react';

interface WebSocketContextType {
  isConnected: boolean;
  connect: (token?: string) => void;
  disconnect: () => void;
  joinConversation: (conversationId: number) => void;
  leaveConversation: (conversationId: number) => void;
  sendMessage: (conversationId: number, message: string) => void;
  getConnectionStatus: () => boolean;
  updateToken: (token: string) => void;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

interface WebSocketProviderProps {
  children: React.ReactNode;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
  const toast = useToast();
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef<any>(null);

  const {
    connect,
    disconnect,
    joinConversation,
    leaveConversation,
    sendMessage,
    getConnectionStatus,
    updateToken,
    isConnected: wsIsConnected,
  } = useWebSocket({
    onConnect: () => {
      setIsConnected(true);
      toast({
        title: 'Connected',
        description: 'Real-time connection established',
        status: 'success',
        duration: 2000,
        isClosable: true,
      });
    },
    onDisconnect: () => {
      setIsConnected(false);
      toast({
        title: 'Disconnected',
        description: 'Real-time connection lost',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
    },
    onError: (error) => {
      toast({
        title: 'Connection Error',
        description: 'Failed to establish real-time connection',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    },
    onAgentUpdate: (message: AgentUpdateMessage) => {
      // Handle agent updates - will be implemented by components
      console.log('Agent update:', message);
    },
    onToolUpdate: (message: ToolUpdateMessage) => {
      // Handle tool updates - will be implemented by components
      console.log('Tool update:', message);
    },
    onMessageUpdate: (message: MessageUpdateMessage) => {
      // Handle message updates - will be implemented by components
      console.log('Message update:', message);
    },
    onMessage: (message: WebSocketMessage) => {
      if (message.type === 'system_notification') {
        toast({
          title: 'System Notification',
          description: message.data?.message || 'System update',
          status: 'info',
          duration: 5000,
          isClosable: true,
        });
      }
    },
  });

  useEffect(() => {
    setIsConnected(wsIsConnected);
  }, [wsIsConnected]);

  const value: WebSocketContextType = {
    isConnected,
    connect,
    disconnect,
    joinConversation,
    leaveConversation,
    sendMessage,
    getConnectionStatus,
    updateToken,
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocketContext = (): WebSocketContextType => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocketContext must be used within a WebSocketProvider');
  }
  return context;
};