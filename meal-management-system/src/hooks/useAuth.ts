import { useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';

/**
 * Custom hook to access authentication context
 * Must be used within AuthProvider
 */
export const useAuth = () => {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
};

/**
 * Helper hook to check if user has a specific role
 */
export const useRole = (requiredRole: 'manager' | 'student') => {
  const { user, isAuthenticated } = useAuth();

  return {
    hasRole: isAuthenticated && user?.role === requiredRole,
    isManager: isAuthenticated && user?.role === 'manager',
    isStudent: isAuthenticated && user?.role === 'student',
  };
};
