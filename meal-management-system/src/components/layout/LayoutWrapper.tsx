import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { AppLayout } from './AppLayout';
import { logout } from '../../services/auth.service';

interface LayoutWrapperProps {
  requiredRole: 'student' | 'manager';
}

export const LayoutWrapper: React.FC<LayoutWrapperProps> = ({ requiredRole }) => {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  if (user.role !== requiredRole) {
    // Redirect to appropriate dashboard
    if (user.role === 'student') {
      return <Navigate to="/student/dashboard" replace />;
    } else if (user.role === 'manager') {
      return <Navigate to="/manager/dashboard" replace />;
    }
    return <Navigate to="/login" replace />;
  }

  const handleLogout = async () => {
    await logout();
    window.location.href = '/login';
  };

  return (
    <AppLayout
      userName={user.full_name}
      userRole={user.role as 'admin' | 'manager' | 'student'}
      onLogout={handleLogout}
    />
  );
};

export default LayoutWrapper;
