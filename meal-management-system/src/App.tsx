import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { PWAProvider } from './contexts/PWAContext';
import { useAuth } from './hooks/useAuth';

// Auth pages
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';

// Student pages
import StudentDashboard from './pages/student/Dashboard';
import MealPlanner from './pages/student/MealPlanner';
import FinancialSummary from './pages/student/FinancialSummary';
import Profile from './pages/student/Profile';

// Manager pages
import ManagerDashboard from './pages/manager/Dashboard';
import Students from './pages/manager/Students';
import Expenses from './pages/manager/Expenses';
import Menu from './pages/manager/Menu';
import Deposits from './pages/manager/Deposits';
import MealManagement from './pages/manager/MealManagement';
import Settings from './pages/manager/Settings';

// PWA pages
import Offline from './pages/Offline';

// Common components
import { LoadingSpinner } from './components/common/LoadingSpinner';
import OfflineIndicator from './components/common/OfflineIndicator';
import InstallPrompt from './components/common/InstallPrompt';
import { LayoutWrapper } from './components/layout/LayoutWrapper';

// Protected Route Components
interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: 'student' | 'manager';
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, requiredRole }) => {
  const { user, loading, isAuthenticated } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && user?.role !== requiredRole) {
    // Redirect to appropriate dashboard based on role
    if (user?.role === 'student') {
      return <Navigate to="/student/dashboard" replace />;
    } else if (user?.role === 'manager') {
      return <Navigate to="/manager/dashboard" replace />;
    }
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// Public Route Component (redirects authenticated users to dashboard)
interface PublicRouteProps {
  children: React.ReactNode;
}

const PublicRoute: React.FC<PublicRouteProps> = ({ children }) => {
  const { user, loading, isAuthenticated } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (isAuthenticated && user) {
    // Redirect authenticated users to their dashboard
    if (user.role === 'student') {
      return <Navigate to="/student/dashboard" replace />;
    } else if (user.role === 'manager') {
      return <Navigate to="/manager/dashboard" replace />;
    }
  }

  return <>{children}</>;
};

// App Routes Component
const AppRoutes: React.FC = () => {
  const { user, isAuthenticated } = useAuth();

  return (
    <Routes>
      {/* Public Routes */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        }
      />
      <Route
        path="/register"
        element={
          <PublicRoute>
            <Register />
          </PublicRoute>
        }
      />

      {/* Student Routes with Layout */}
      <Route path="/student/*" element={<LayoutWrapper requiredRole="student" />}>
        <Route path="dashboard" element={<StudentDashboard />} />
        <Route path="meals" element={<MealPlanner />} />
        <Route path="deposits" element={<FinancialSummary />} />
        <Route path="profile" element={<Profile />} />
      </Route>

      {/* Manager Routes with Layout */}
      <Route path="/manager/*" element={<LayoutWrapper requiredRole="manager" />}>
        <Route path="dashboard" element={<ManagerDashboard />} />
        <Route path="meals" element={<MealManagement />} />
        <Route path="deposits" element={<Deposits />} />
        <Route path="expenses" element={<Expenses />} />
        <Route path="menu" element={<Menu />} />
        <Route path="users" element={<Students />} />
        <Route path="settings" element={<Settings />} />
      </Route>

      {/* Root Route - Redirect based on authentication */}
      <Route
        path="/"
        element={
          isAuthenticated && user ? (
            user.role === 'student' ? (
              <Navigate to="/student/dashboard" replace />
            ) : (
              <Navigate to="/manager/dashboard" replace />
            )
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />

      {/* PWA Offline Route */}
      <Route path="/offline" element={<Offline />} />

      {/* 404 Not Found */}
      <Route
        path="*"
        element={
          <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
            <div className="text-center">
              <h1 className="text-6xl font-bold text-gray-800 dark:text-gray-200 mb-4">404</h1>
              <p className="text-xl text-gray-600 dark:text-gray-400 mb-8">Page not found</p>
              <a
                href="/"
                className="px-6 py-3 bg-blue-600 dark:bg-blue-500 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 transition-colors"
              >
                Go to Dashboard
              </a>
            </div>
          </div>
        }
      />
    </Routes>
  );
};

// Main App Component
const App: React.FC = () => {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <PWAProvider>
          <AuthProvider>
            <OfflineIndicator />
            <InstallPrompt />
            <AppRoutes />
          </AuthProvider>
        </PWAProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
};

export default App;
