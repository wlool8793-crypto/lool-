import React, { useState, useRef, useEffect } from 'react';
import { Bell, User, LogOut, Settings, ChevronDown } from 'lucide-react';
import { ThemeToggle } from '../common/ThemeToggle';

interface HeaderProps {
  userName: string;
  userRole: string;
  userAvatar?: string;
  notifications?: Notification[];
  onLogout: () => void;
}

interface Notification {
  id: string;
  title: string;
  message: string;
  time: string;
  read: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  userName,
  userRole,
  userAvatar,
  notifications = [],
  onLogout,
}) => {
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const notificationsRef = useRef<HTMLDivElement>(null);

  const unreadCount = notifications.filter((n) => !n.read).length;

  // Close menus when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        userMenuRef.current &&
        !userMenuRef.current.contains(event.target as Node)
      ) {
        setShowUserMenu(false);
      }
      if (
        notificationsRef.current &&
        !notificationsRef.current.contains(event.target as Node)
      ) {
        setShowNotifications(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <header className="h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 fixed top-0 right-0 left-0 z-20 flex items-center justify-between px-6 transition-colors">
      {/* Left side - could add breadcrumbs or search here */}
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-semibold text-gray-900 dark:text-white hidden sm:block">
          Hostel Meal Management
        </h1>
      </div>

      {/* Right side - theme toggle, notifications and user menu */}
      <div className="flex items-center gap-2">
        {/* Theme Toggle */}
        <ThemeToggle />

        {/* Notifications */}
        <div className="relative" ref={notificationsRef}>
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            aria-label="Notifications"
          >
            <Bell className="w-5 h-5" />
            {unreadCount > 0 && (
              <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </button>

          {/* Notifications Dropdown */}
          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-2 max-h-96 overflow-y-auto">
              <div className="px-4 py-2 border-b border-gray-200 dark:border-gray-700">
                <h3 className="font-semibold text-gray-900 dark:text-white">Notifications</h3>
              </div>

              {notifications.length === 0 ? (
                <div className="px-4 py-8 text-center text-gray-500 dark:text-gray-400 text-sm">
                  No notifications
                </div>
              ) : (
                <ul>
                  {notifications.map((notification) => (
                    <li
                      key={notification.id}
                      className={`px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer border-b border-gray-100 dark:border-gray-700 last:border-0 ${
                        !notification.read ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                      }`}
                    >
                      <h4 className="font-medium text-sm text-gray-900 dark:text-white">
                        {notification.title}
                      </h4>
                      <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                        {notification.message}
                      </p>
                      <span className="text-xs text-gray-400 dark:text-gray-500 mt-1 block">
                        {notification.time}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>

        {/* User Menu */}
        <div className="relative" ref={userMenuRef}>
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-3 p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <div className="flex items-center gap-3">
              {userAvatar ? (
                <img
                  src={userAvatar}
                  alt={userName}
                  className="w-8 h-8 rounded-full object-cover"
                />
              ) : (
                <div className="w-8 h-8 rounded-full bg-blue-600 dark:bg-blue-500 flex items-center justify-center">
                  <User className="w-5 h-5 text-white" />
                </div>
              )}
              <div className="hidden md:block text-left">
                <p className="text-sm font-medium text-gray-900 dark:text-white">{userName}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 capitalize">{userRole}</p>
              </div>
            </div>
            <ChevronDown className="w-4 h-4 text-gray-600 dark:text-gray-400" />
          </button>

          {/* User Dropdown */}
          {showUserMenu && (
            <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-2">
              <div className="px-4 py-2 border-b border-gray-200 dark:border-gray-700 md:hidden">
                <p className="text-sm font-medium text-gray-900 dark:text-white">{userName}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 capitalize">{userRole}</p>
              </div>

              <a
                href="/profile"
                className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <User className="w-4 h-4" />
                Profile
              </a>

              <a
                href="/settings"
                className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <Settings className="w-4 h-4" />
                Settings
              </a>

              <hr className="my-2 border-gray-200 dark:border-gray-700" />

              <button
                onClick={onLogout}
                className="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
