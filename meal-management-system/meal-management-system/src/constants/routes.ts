/**
 * Application route constants
 * Centralized route paths for the Hostel Meal Management System
 */

/**
 * Public routes (accessible without authentication)
 */
export const PUBLIC_ROUTES = {
  LOGIN: '/login',
  REGISTER: '/register',
  FORGOT_PASSWORD: '/forgot-password',
  RESET_PASSWORD: '/reset-password',
} as const;

/**
 * Student routes
 */
export const STUDENT_ROUTES = {
  DASHBOARD: '/student/dashboard',
  MEAL_SELECTION: '/student/meals',
  MEAL_HISTORY: '/student/history',
  MONTHLY_BILL: '/student/bill',
  PROFILE: '/student/profile',
} as const;

/**
 * Mess Manager routes
 */
export const MANAGER_ROUTES = {
  DASHBOARD: '/manager/dashboard',
  EXPENSES: '/manager/expenses',
  MEAL_LOGS: '/manager/logs',
  REPORTS: '/manager/reports',
  STUDENTS: '/manager/students',
  SETTINGS: '/manager/settings',
} as const;

/**
 * Hostel Admin routes
 */
export const ADMIN_ROUTES = {
  DASHBOARD: '/admin/dashboard',
  MANAGERS: '/admin/managers',
  STUDENTS: '/admin/students',
  HOSTELS: '/admin/hostels',
  REPORTS: '/admin/reports',
  SETTINGS: '/admin/settings',
} as const;

/**
 * All routes combined
 */
export const ROUTES = {
  HOME: '/',
  ...PUBLIC_ROUTES,
  STUDENT: STUDENT_ROUTES,
  MANAGER: MANAGER_ROUTES,
  ADMIN: ADMIN_ROUTES,
} as const;

/**
 * Route path type helper
 */
export type RoutePath =
  | typeof PUBLIC_ROUTES[keyof typeof PUBLIC_ROUTES]
  | typeof STUDENT_ROUTES[keyof typeof STUDENT_ROUTES]
  | typeof MANAGER_ROUTES[keyof typeof MANAGER_ROUTES]
  | typeof ADMIN_ROUTES[keyof typeof ADMIN_ROUTES]
  | '/';

/**
 * Check if a route is public (doesn't require authentication)
 * @param path - The route path to check
 * @returns True if the route is public
 */
export const isPublicRoute = (path: string): boolean => {
  return Object.values(PUBLIC_ROUTES).includes(path as any);
};

/**
 * Get the default route for a user role
 * @param role - The user role
 * @returns The default dashboard route for the role
 */
export const getDefaultRouteForRole = (role: 'student' | 'manager' | 'admin'): string => {
  switch (role) {
    case 'student':
      return STUDENT_ROUTES.DASHBOARD;
    case 'manager':
      return MANAGER_ROUTES.DASHBOARD;
    case 'admin':
      return ADMIN_ROUTES.DASHBOARD;
    default:
      return PUBLIC_ROUTES.LOGIN;
  }
};
