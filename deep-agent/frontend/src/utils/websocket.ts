// WebSocket utility for real-time communication
import { io, Socket } from 'socket.io-client';
import React from 'react';
import { AgentUpdateMessage, ToolUpdateMessage, MessageUpdateMessage, WebSocketMessage } from '../types';

interface WebSocketConfig {
  url?: string;
  autoConnect?: boolean;
  reconnection?: boolean;
  reconnectionAttempts?: number;
  reconnectionDelay?: number;
  timeout?: number;
  transports?: string[];
}

interface WebSocketHandlers {
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: any) => void;
  onMessage?: (message: WebSocketMessage) => void;
  onAgentUpdate?: (message: AgentUpdateMessage) => void;
  onToolUpdate?: (message: ToolUpdateMessage) => void;
  onMessageUpdate?: (message: MessageUpdateMessage) => void;
}

class WebSocketService {
  private socket: Socket | null = null;
  private config: WebSocketConfig;
  private handlers: WebSocketHandlers;
  public isConnected = false;

  constructor(config: WebSocketConfig, handlers: WebSocketHandlers) {
    this.config = {
      url: config.url || 'http://localhost:8000',
      autoConnect: config.autoConnect || false,
      reconnection: config.reconnection || true,
      reconnectionAttempts: config.reconnectionAttempts || 5,
      reconnectionDelay: config.reconnectionDelay || 1000,
      timeout: config.timeout || 20000,
      transports: config.transports || ['websocket', 'polling'],
      ...config,
    };
    this.handlers = handlers;
  }

  connect(token?: string): void {
    if (this.socket) {
      this.disconnect();
    }

    const socketOptions: any = {
      ...this.config,
    };

    if (token) {
      socketOptions.auth = { token };
    }

    this.socket = io(this.config.url!, socketOptions);

    this.socket.on('connect', () => {
      this.isConnected = true;
      this.handlers.onConnect?.();
    });

    this.socket.on('disconnect', () => {
      this.isConnected = false;
      this.handlers.onDisconnect?.();
    });

    this.socket.on('error', (error) => {
      this.handlers.onError?.(error);
    });

    this.socket.on('message', (message: WebSocketMessage) => {
      this.handlers.onMessage?.(message);
    });

    this.socket.on('agent_update', (message: AgentUpdateMessage) => {
      this.handlers.onAgentUpdate?.(message);
    });

    this.socket.on('tool_update', (message: ToolUpdateMessage) => {
      this.handlers.onToolUpdate?.(message);
    });

    this.socket.on('message_update', (message: MessageUpdateMessage) => {
      this.handlers.onMessageUpdate?.(message);
    });
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
    }
  }

  joinConversation(conversationId: number): void {
    if (this.socket && this.isConnected) {
      this.socket.emit('join_conversation', { conversation_id: conversationId });
    }
  }

  leaveConversation(conversationId: number): void {
    if (this.socket && this.isConnected) {
      this.socket.emit('leave_conversation', { conversation_id: conversationId });
    }
  }

  sendMessage(conversationId: number, message: string): void {
    if (this.socket && this.isConnected) {
      this.socket.emit('send_message', {
        conversation_id: conversationId,
        message,
      });
    }
  }

  getConnectionStatus(): boolean {
    return this.isConnected;
  }

  updateToken(token: string): void {
    if (this.socket) {
      this.socket.auth = { token };
    }
  }

  destroy(): void {
    this.disconnect();
  }
}

// Hook for using WebSocket in components
export const useWebSocket = (handlers: WebSocketHandlers = {}, config?: WebSocketConfig) => {
  const wsService = new WebSocketService(config || {}, handlers);

  React.useEffect(() => {
    return () => {
      wsService.destroy();
    };
  }, []);

  return {
    connect: wsService.connect.bind(wsService),
    disconnect: wsService.disconnect.bind(wsService),
    joinConversation: wsService.joinConversation.bind(wsService),
    leaveConversation: wsService.leaveConversation.bind(wsService),
    sendMessage: wsService.sendMessage.bind(wsService),
    getConnectionStatus: wsService.getConnectionStatus.bind(wsService),
    updateToken: wsService.updateToken.bind(wsService),
    isConnected: wsService.isConnected,
  };
};

export default WebSocketService;