// Type definitions for Deep Agent frontend

// User Types
export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  avatar_url?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at?: string;
}

// Authentication Types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

// Conversation Types
export interface Conversation {
  id: number;
  user_id: number;
  title: string;
  session_id: string;
  created_at: string;
  updated_at?: string;
  metadata?: Record<string, any>;
  message_count?: number;
  last_message?: string;
}

export interface Message {
  id: number;
  conversation_id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  message_type: 'text' | 'file' | 'system' | 'tool_result' | 'error';
  metadata?: Record<string, any>;
  created_at: string;
}

export interface CreateConversationData {
  title: string;
  session_id?: string;
  metadata?: Record<string, any>;
}

export interface CreateMessageData {
  conversation_id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  message_type?: 'text' | 'file' | 'system' | 'tool_result' | 'error';
  metadata?: Record<string, any>;
}

// Agent Types
export interface Agent {
  id: number;
  name: string;
  description: string;
  agent_type: string;
  capabilities: string[];
  config: Record<string, any>;
  is_active: boolean;
}

export interface AgentExecuteRequest {
  conversation_id: number;
  message: string;
  agent_type: string;
  tools?: string[];
  context?: Record<string, any>;
  max_iterations?: number;
  timeout?: number;
}

export interface AgentExecuteResponse {
  success: boolean;
  response: string;
  execution_time: number;
  tools_used: string[];
  tokens_used?: number;
  agent_state?: Record<string, any>;
  error_message?: string;
}

export interface AgentStatus {
  conversation_id: number;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'stopped';
  current_node?: string;
  state_data?: Record<string, any>;
  error_message?: string;
  updated_at?: string;
  execution_time?: number;
}

// Tool Types
export interface Tool {
  id: number;
  name: string;
  description: string;
  category: string;
  version: string;
  parameters_schema: Record<string, any>;
  is_active: boolean;
  requires_auth: boolean;
}

export interface ToolExecuteRequest {
  tool_name: string;
  parameters: Record<string, any>;
  conversation_id: number;
  timeout?: number;
  context?: Record<string, any>;
}

export interface ToolExecuteResponse {
  success: boolean;
  result?: any;
  execution_time: number;
  tool_name: string;
  error_message?: string;
  metadata?: Record<string, any>;
}

// File Types
export interface FileUpload {
  id: number;
  user_id: number;
  conversation_id?: number;
  filename: string;
  original_filename: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  file_type: 'document' | 'image' | 'audio' | 'video' | 'other';
  processed: boolean;
  metadata?: Record<string, any>;
  created_at: string;
}

// WebSocket Types
export interface WebSocketMessage {
  type: string;
  data?: any;
  conversation_id?: number;
  user_id?: number;
  timestamp: number;
}

export interface AgentUpdateMessage extends WebSocketMessage {
  type: 'agent_update';
  data: {
    status: string;
    current_node?: string;
    message?: string;
    progress?: number;
  };
}

export interface ToolUpdateMessage extends WebSocketMessage {
  type: 'tool_update';
  data: {
    tool_name: string;
    status: string;
    result?: any;
    error?: string;
  };
}

export interface MessageUpdateMessage extends WebSocketMessage {
  type: 'message_update';
  data: {
    message: Partial<Message>;
    conversation_id: number;
  };
}

// UI State Types
export interface AppState {
  user: User | null;
  isAuthenticated: boolean;
  conversations: Conversation[];
  currentConversation: Conversation | null;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  socket: WebSocket | null;
  socketConnected: boolean;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface ConversationState {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}

export interface AgentState {
  isExecuting: boolean;
  currentStatus: AgentStatus | null;
  executionHistory: any[];
  isLoading: boolean;
  error: string | null;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  has_more: boolean;
}

// Form Types
export interface LoginForm {
  email: string;
  password: string;
}

export interface RegisterForm {
  email: string;
  username: string;
  password: string;
  confirm_password: string;
  full_name?: string;
}

// Utility Types
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

// Error Types
export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, any>;
}

export interface ValidationError {
  field: string;
  message: string;
}

// Toast Notification Types
export interface ToastNotification {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  title: string;
  message?: string;
  duration?: number;
}

// Loading States
export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

// Pagination Types
export interface PaginationParams {
  page: number;
  limit: number;
}

export interface PaginationMeta {
  total: number;
  page: number;
  limit: number;
  has_next: boolean;
  has_prev: boolean;
  total_pages: number;
}