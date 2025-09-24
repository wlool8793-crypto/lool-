import React from 'react';
import { Loader2, Sparkles } from 'lucide-react';

interface LoadingScreenProps {
  message?: string;
  subMessage?: string;
  progress?: number;
  showProgress?: boolean;
  variant?: 'default' | 'minimal' | 'full-page';
}

export const LoadingScreen: React.FC<LoadingScreenProps> = ({
  message = 'Loading...',
  subMessage,
  progress,
  showProgress = false,
  variant = 'default'
}) => {
  const getLoadingContent = () => (
    <div className="flex flex-col items-center justify-center space-y-4">
      <div className="relative">
        <Loader2 className="w-12 h-12 text-blue-600 animate-spin" />
        <Sparkles className="w-4 h-4 text-yellow-500 absolute -top-1 -right-1 animate-pulse" />
      </div>

      <div className="text-center space-y-2">
        {message && (
          <h3 className="text-lg font-semibold text-gray-900 animate-pulse">
            {message}
          </h3>
        )}
        {subMessage && (
          <p className="text-sm text-gray-600">
            {subMessage}
          </p>
        )}
      </div>

      {showProgress && typeof progress === 'number' && (
        <div className="w-full max-w-xs">
          <div className="flex justify-between text-xs text-gray-600 mb-1">
            <span>Progress</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );

  if (variant === 'full-page') {
    return (
      <div className="fixed inset-0 bg-white bg-opacity-95 backdrop-blur-sm flex items-center justify-center z-50">
        <div className="p-8">
          {getLoadingContent()}
        </div>
      </div>
    );
  }

  if (variant === 'minimal') {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="flex items-center space-x-3">
          <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
          <span className="text-gray-600">{message}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-[400px] bg-gray-50 rounded-lg">
      {getLoadingContent()}
    </div>
  );
};

export const LoadingSpinner: React.FC<{
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}> = ({ size = 'md', className = '' }) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  };

  return (
    <Loader2
      className={`animate-spin text-blue-600 ${sizeClasses[size]} ${className}`}
    />
  );
};

export const LoadingSkeleton: React.FC<{
  lines?: number;
  className?: string;
}> = ({ lines = 3, className = '' }) => {
  return (
    <div className={`space-y-3 ${className}`}>
      {Array.from({ length: lines }).map((_, index) => (
        <div
          key={index}
          className="animate-pulse bg-gray-200 rounded"
          style={{
            height: index === 0 ? '1.5rem' : '1rem',
            width: index === lines - 1 ? '80%' : '100%'
          }}
        />
      ))}
    </div>
  );
};

export const LoadingCard: React.FC<{
  title?: string;
  subtitle?: string;
}> = ({ title, subtitle }) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border p-6 space-y-4">
      <div className="space-y-2">
        <div className="h-6 bg-gray-200 rounded animate-pulse w-3/4"></div>
        {subtitle && <div className="h-4 bg-gray-200 rounded animate-pulse w-1/2"></div>}
      </div>
      <LoadingSkeleton lines={4} />
    </div>
  );
};