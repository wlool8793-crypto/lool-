import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  UtensilsCrossed,
  Users,
  CalendarDays,
  Receipt,
  Settings,
  ChevronLeft,
  ChevronRight,
  FileText,
  BarChart3,
} from 'lucide-react';

interface SidebarProps {
  isCollapsed: boolean;
  onToggle: () => void;
  userRole: 'admin' | 'manager' | 'student';
}

interface MenuItem {
  path: string;
  label: string;
  icon: React.ElementType;
  roles: string[];
}

const menuItems: MenuItem[] = [
  {
    path: '/dashboard',
    label: 'Dashboard',
    icon: LayoutDashboard,
    roles: ['admin', 'manager', 'student'],
  },
  {
    path: '/meals',
    label: 'Meals',
    icon: UtensilsCrossed,
    roles: ['admin', 'manager', 'student'],
  },
  {
    path: '/menu',
    label: 'Menu Planning',
    icon: CalendarDays,
    roles: ['admin', 'manager'],
  },
  {
    path: '/orders',
    label: 'Orders',
    icon: Receipt,
    roles: ['admin', 'manager', 'student'],
  },
  {
    path: '/students',
    label: 'Students',
    icon: Users,
    roles: ['admin', 'manager'],
  },
  {
    path: '/reports',
    label: 'Reports',
    icon: BarChart3,
    roles: ['admin', 'manager'],
  },
  {
    path: '/feedback',
    label: 'Feedback',
    icon: FileText,
    roles: ['admin', 'manager', 'student'],
  },
  {
    path: '/settings',
    label: 'Settings',
    icon: Settings,
    roles: ['admin', 'manager', 'student'],
  },
];

export const Sidebar: React.FC<SidebarProps> = ({
  isCollapsed,
  onToggle,
  userRole,
}) => {
  const filteredMenuItems = menuItems.filter((item) =>
    item.roles.includes(userRole)
  );

  return (
    <aside
      className={`${
        isCollapsed ? 'w-20' : 'w-64'
      } bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-all duration-300 ease-in-out flex flex-col fixed left-0 top-0 h-full z-30`}
    >
      {/* Logo Section */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200 dark:border-gray-700">
        {!isCollapsed && (
          <div className="flex items-center gap-2">
            <UtensilsCrossed className="w-8 h-8 text-blue-600 dark:text-blue-400" />
            <span className="font-bold text-xl text-gray-900 dark:text-white">MealManager</span>
          </div>
        )}
        {isCollapsed && (
          <UtensilsCrossed className="w-8 h-8 text-blue-600 dark:text-blue-400 mx-auto" />
        )}
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 overflow-y-auto py-4 px-2">
        <ul className="space-y-1">
          {filteredMenuItems.map((item) => {
            const Icon = item.icon;
            return (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-3 rounded-lg transition-colors group ${
                      isActive
                        ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                    }`
                  }
                  title={isCollapsed ? item.label : undefined}
                >
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  {!isCollapsed && (
                    <span className="font-medium text-sm">{item.label}</span>
                  )}
                </NavLink>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Toggle Button */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <button
          onClick={onToggle}
          className="w-full flex items-center justify-center p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-gray-600 dark:text-gray-400"
          aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? (
            <ChevronRight className="w-5 h-5" />
          ) : (
            <>
              <ChevronLeft className="w-5 h-5" />
              <span className="ml-2 text-sm font-medium">Collapse</span>
            </>
          )}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
