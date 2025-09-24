// API utility functions for Deep Agent frontend
import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { LoginCredentials, RegisterData, AuthResponse, ApiResponse, ApiError } from '../types';

// Create axios instance with default configuration
const api: AxiosInstance = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication API
export const authApi = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/login', credentials);
    return response.data;
  },

  register: async (data: RegisterData) => {
    const response = await api.post('/auth/register', data);
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  refreshToken: async (): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/refresh');
    return response.data;
  },

  logout: async () => {
    const response = await api.post('/auth/logout');
    return response.data;
  },
};

// Conversations API
export const conversationsApi = {
  getConversations: async (params?: { skip?: number; limit?: number }) => {
    const response = await api.get('/conversations', { params });
    return response.data;
  },

  createConversation: async (data: { title: string; session_id?: string; metadata?: Record<string, any> }) => {
    const response = await api.post('/conversations', data);
    return response.data;
  },

  getConversation: async (id: number) => {
    const response = await api.get(`/conversations/${id}`);
    return response.data;
  },

  updateConversation: async (id: number, data: Partial<{ title: string; metadata?: Record<string, any> }>) => {
    const response = await api.put(`/conversations/${id}`, data);
    return response.data;
  },

  deleteConversation: async (id: number) => {
    const response = await api.delete(`/conversations/${id}`);
    return response.data;
  },

  getMessages: async (conversationId: number, params?: { skip?: number; limit?: number }) => {
    const response = await api.get(`/conversations/${conversationId}/messages`, { params });
    return response.data;
  },

  createMessage: async (data: { conversation_id: number; role: string; content: string; message_type?: string; metadata?: Record<string, any> }) => {
    const response = await api.post(`/conversations/${data.conversation_id}/messages`, data);
    return response.data;
  },

  getConversationBySessionId: async (sessionId: string) => {
    const response = await api.get(`/conversations/session/${sessionId}`);
    return response.data;
  },
};

// Agents API
export const agentsApi = {
  getAgents: async () => {
    const response = await api.get('/agents');
    return response.data;
  },

  executeAgent: async (data: { conversation_id: number; message: string; agent_type: string; tools?: string[]; context?: Record<string, any> }) => {
    const response = await api.post('/agents/execute', data);
    return response.data;
  },

  getAgentStatus: async (conversationId: number) => {
    const response = await api.get(`/agents/status/${conversationId}`);
    return response.data;
  },

  getAgentHistory: async (conversationId: number, params?: { limit?: number }) => {
    const response = await api.get(`/agents/history/${conversationId}`, { params });
    return response.data;
  },

  clearAgentState: async (conversationId: number) => {
    const response = await api.delete(`/agents/state/${conversationId}`);
    return response.data;
  },

  stopAgentExecution: async (conversationId: number) => {
    const response = await api.post(`/agents/stop/${conversationId}`);
    return response.data;
  },
};

// Tools API
export const toolsApi = {
  getTools: async (params?: { category?: string }) => {
    const response = await api.get('/tools', { params });
    return response.data;
  },

  getToolCategories: async () => {
    const response = await api.get('/tools/categories');
    return response.data;
  },

  executeTool: async (data: { tool_name: string; parameters: Record<string, any>; conversation_id: number; timeout?: number; context?: Record<string, any> }) => {
    const response = await api.post('/tools/execute', data);
    return response.data;
  },

  getToolHistory: async (conversationId: number, params?: { tool_name?: string; limit?: number }) => {
    const response = await api.get(`/tools/history/${conversationId}`, { params });
    return response.data;
  },

  getToolSchema: async (toolName: string) => {
    const response = await api.get(`/tools/schema/${toolName}`);
    return response.data;
  },

  validateToolParameters: async (toolName: string, parameters: Record<string, any>) => {
    const response = await api.post(`/tools/validate/${toolName}`, parameters);
    return response.data;
  },

  getToolStats: async (conversationId: number) => {
    const response = await api.get(`/tools/stats/${conversationId}`);
    return response.data;
  },

  clearToolHistory: async (conversationId: number) => {
    const response = await api.delete(`/tools/history/${conversationId}`);
    return response.data;
  },

  batchExecuteTools: async (requests: Array<{ tool_name: string; parameters: Record<string, any>; conversation_id: number }>) => {
    const response = await api.post('/tools/batch-execute', { requests });
    return response.data;
  },
};

// Files API
export const filesApi = {
  uploadFile: async (file: File, conversationId?: number) => {
    const formData = new FormData();
    formData.append('file', file);
    if (conversationId) {
      formData.append('conversation_id', conversationId.toString());
    }

    const response = await api.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getFiles: async (params?: { conversation_id?: number; file_type?: string; skip?: number; limit?: number }) => {
    const response = await api.get('/files', { params });
    return response.data;
  },

  getFile: async (id: number) => {
    const response = await api.get(`/files/${id}`);
    return response.data;
  },

  downloadFile: async (id: number) => {
    const response = await api.get(`/files/${id}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  deleteFile: async (id: number) => {
    const response = await api.delete(`/files/${id}`);
    return response.data;
  },

  processFile: async (id: number, data: { processing_type: string; options?: Record<string, any> }) => {
    const response = await api.post(`/files/${id}/process`, data);
    return response.data;
  },

  getAvailableProcessingTypes: async () => {
    const response = await api.get('/files/types/available');
    return response.data;
  },

  getFileStats: async () => {
    const response = await api.get('/files/stats/user');
    return response.data;
  },

  batchUploadFiles: async (files: FileList, conversationId?: number) => {
    const formData = new FormData();
    Array.from(files).forEach((file, index) => {
      formData.append(`files`, file);
    });
    if (conversationId) {
      formData.append('conversation_id', conversationId.toString());
    }

    const response = await api.post('/files/batch-upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

// Utility functions
export const setAuthToken = (token: string) => {
  localStorage.setItem('access_token', token);
};

export const removeAuthToken = () => {
  localStorage.removeItem('access_token');
};

export const getAuthToken = () => {
  return localStorage.getItem('access_token');
};

export const isAuthenticated = () => {
  return !!getAuthToken();
};

// Error handling utilities
export const handleApiError = (error: AxiosError): ApiError => {
  if (error.response) {
    const response = error.response.data as ApiResponse<any>;
    return {
      message: response.message || 'An error occurred',
      code: error.response.status.toString(),
      details: typeof response.error === 'object' && response.error !== null ? response.error as Record<string, any> : undefined,
    };
  } else if (error.request) {
    return {
      message: 'Network error - please check your connection',
      code: 'NETWORK_ERROR',
    };
  } else {
    return {
      message: 'An unexpected error occurred',
      code: 'UNKNOWN_ERROR',
    };
  }
};

export default api;