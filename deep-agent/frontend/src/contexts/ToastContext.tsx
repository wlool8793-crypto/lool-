import React, { createContext, useContext, useCallback } from 'react';
import { useToast, ToastId, UseToastOptions } from '@chakra-ui/react';
import { ToastNotification } from '../types';

interface ToastContextType {
  showToast: (notification: Omit<ToastNotification, 'id'>) => ToastId;
  showSuccess: (title: string, message?: string) => ToastId;
  showError: (title: string, message?: string) => ToastId;
  showInfo: (title: string, message?: string) => ToastId;
  showWarning: (title: string, message?: string) => ToastId;
  closeToast: (toastId: ToastId) => void;
  closeAllToasts: () => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

interface ToastProviderProps {
  children: React.ReactNode;
}

export const ToastProvider: React.FC<ToastProviderProps> = ({ children }) => {
  const toast = useToast();

  const showToast = useCallback((notification: Omit<ToastNotification, 'id'>): ToastId => {
    return toast({
      title: notification.title,
      description: notification.message,
      status: notification.type,
      duration: notification.duration || 5000,
      isClosable: true,
      position: 'top-right',
    });
  }, [toast]);

  const showSuccess = useCallback((title: string, message?: string): ToastId => {
    return showToast({ type: 'success', title, message });
  }, [showToast]);

  const showError = useCallback((title: string, message?: string): ToastId => {
    return showToast({ type: 'error', title, message });
  }, [showToast]);

  const showInfo = useCallback((title: string, message?: string): ToastId => {
    return showToast({ type: 'info', title, message });
  }, [showToast]);

  const showWarning = useCallback((title: string, message?: string): ToastId => {
    return showToast({ type: 'warning', title, message });
  }, [showToast]);

  const closeToast = useCallback((toastId: ToastId) => {
    toast.close(toastId);
  }, [toast]);

  const closeAllToasts = useCallback(() => {
    toast.closeAll();
  }, [toast]);

  const value: ToastContextType = {
    showToast,
    showSuccess,
    showError,
    showInfo,
    showWarning,
    closeToast,
    closeAllToasts,
  };

  return <ToastContext.Provider value={value}>{children}</ToastContext.Provider>;
};

export const useToastContext = (): ToastContextType => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToastContext must be used within a ToastProvider');
  }
  return context;
};