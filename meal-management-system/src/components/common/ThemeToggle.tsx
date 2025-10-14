import React from 'react';
import { Moon, Sun } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';

interface ThemeToggleProps {
  className?: string;
  showLabel?: boolean;
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({
  className = '',
  showLabel = false
}) => {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className={`relative p-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-all duration-200 ${className}`}
      aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
      title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
    >
      <div className="relative w-5 h-5">
        {/* Sun icon for light mode */}
        <Sun
          className={`absolute inset-0 w-5 h-5 transition-all duration-300 ${
            theme === 'light'
              ? 'opacity-100 rotate-0 scale-100'
              : 'opacity-0 rotate-90 scale-0'
          }`}
        />

        {/* Moon icon for dark mode */}
        <Moon
          className={`absolute inset-0 w-5 h-5 transition-all duration-300 ${
            theme === 'dark'
              ? 'opacity-100 rotate-0 scale-100'
              : 'opacity-0 -rotate-90 scale-0'
          }`}
        />
      </div>

      {showLabel && (
        <span className="ml-2 text-sm font-medium">
          {theme === 'light' ? 'Light' : 'Dark'} Mode
        </span>
      )}
    </button>
  );
};

export default ThemeToggle;
