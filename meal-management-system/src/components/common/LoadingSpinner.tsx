import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  fullScreen?: boolean;
  message?: string;
}

const sizeClasses = {
  sm: 'w-4 h-4',
  md: 'w-8 h-8',
  lg: 'w-12 h-12',
  xl: 'w-16 h-16',
};

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  className = '',
  fullScreen = false,
  message,
}) => {
  const spinner = (
    <div className="flex flex-col items-center justify-center gap-3">
      <Loader2
        className={`${sizeClasses[size]} animate-spin text-blue-600 dark:text-blue-400 ${className}`}
      />
      {message && (
        <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">{message}</p>
      )}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-white dark:bg-gray-900 bg-opacity-90 dark:bg-opacity-90 z-50">
        {spinner}
      </div>
    );
  }

  return spinner;
};

export default LoadingSpinner;
