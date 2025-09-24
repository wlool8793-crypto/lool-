import * as React from 'react';
import { cn } from '@/lib/utils';

export interface ToggleProps {
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
  disabled?: boolean;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'marriage';
  label?: string;
  description?: string;
  required?: boolean;
}

const Toggle: React.FC<ToggleProps> = ({
  checked,
  onCheckedChange,
  disabled = false,
  className,
  size = 'md',
  variant = 'default',
  label,
  description,
  required = false,
}) => {
  const toggleRef = React.useRef<HTMLButtonElement>(null);

  const handleClick = () => {
    if (!disabled) {
      onCheckedChange(!checked);
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleClick();
    }
  };

  const sizeClasses = {
    sm: 'w-9 h-5',
    md: 'w-11 h-6',
    lg: 'w-14 h-7',
  };

  const thumbSizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  };

  const thumbTranslateClasses = {
    sm: checked ? 'translate-x-4' : 'translate-x-0.5',
    md: checked ? 'translate-x-5' : 'translate-x-0.5',
    lg: checked ? 'translate-x-7' : 'translate-x-0.5',
  };

  const variantClasses = {
    default: {
      track: cn(
        'transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
        checked
          ? 'bg-primary-600'
          : 'bg-secondary-200'
      ),
      thumb: 'bg-white',
    },
    marriage: {
      track: cn(
        'transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-marriage-600 focus-visible:ring-offset-2',
        checked
          ? 'bg-marriage-600'
          : 'bg-secondary-200'
      ),
      thumb: 'bg-white',
    },
  };

  const currentVariant = variantClasses[variant];

  return (
    <div className={cn('flex items-center space-x-3', className)}>
      <button
        ref={toggleRef}
        type="button"
        role="switch"
        aria-checked={checked}
        aria-disabled={disabled}
        disabled={disabled}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        className={cn(
          'relative inline-flex flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors',
          sizeClasses[size],
          currentVariant.track,
          disabled && 'opacity-50 cursor-not-allowed'
        )}
      >
        <span
          className={cn(
            'pointer-events-none relative inline-block transform rounded-full bg-white shadow-lg ring-0 transition-transform',
            thumbSizeClasses[size],
            thumbTranslateClasses[size],
            disabled && 'cursor-not-allowed'
          )}
        >
          <span
            className={cn(
              'absolute inset-0 flex h-full w-full items-center justify-center transition-opacity',
              checked ? 'opacity-0 duration-100 ease-out' : 'opacity-100 duration-200 ease-in'
            )}
            aria-hidden="true"
          >
            <svg className="h-3 w-3 text-gray-400" fill="none" viewBox="0 0 12 12">
              <path
                d="M4 8l2-2m0 0l2-2M6 6L4 4m2 2l2 2"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </span>
          <span
            className={cn(
              'absolute inset-0 flex h-full w-full items-center justify-center transition-opacity',
              checked ? 'opacity-100 duration-200 ease-in' : 'opacity-0 duration-100 ease-out'
            )}
            aria-hidden="true"
          >
            <svg className="h-3 w-3 text-primary-600" fill="currentColor" viewBox="0 0 12 12">
              <path d="M3.707 5.293a1 1 0 00-1.414 1.414l1.414-1.414zM5 8l-.707.707a1 1 0 001.414 0L5 8zm4.707-4.293a1 1 0 00-1.414-1.414l1.414 1.414zm-7.414 2l2 2 1.414-1.414-2-2-1.414 1.414zm3.414 2l4-4-1.414-1.414-4 4 1.414 1.414z" />
            </svg>
          </span>
        </span>
      </button>

      {(label || description) && (
        <div className="flex flex-col">
          {label && (
            <label
              className={cn(
                'text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70',
                disabled && 'opacity-50'
              )}
            >
              {label}
              {required && <span className="text-red-500 ml-1">*</span>}
            </label>
          )}
          {description && (
            <p
              className={cn(
                'text-xs text-muted-foreground',
                disabled && 'opacity-50'
              )}
            >
              {description}
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export { Toggle };