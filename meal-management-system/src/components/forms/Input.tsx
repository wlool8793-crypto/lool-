import React, { InputHTMLAttributes, forwardRef } from 'react';
import { AlertCircle } from 'lucide-react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      error,
      hint,
      leftIcon,
      rightIcon,
      fullWidth = true,
      className = '',
      disabled,
      required,
      type = 'text',
      ...props
    },
    ref
  ) => {
    const inputClasses = `
      block w-full px-4 py-2.5 text-gray-900 bg-white border rounded-lg
      focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
      transition-colors duration-200
      ${leftIcon ? 'pl-11' : ''}
      ${rightIcon ? 'pr-11' : ''}
      ${error ? 'border-red-300 focus:ring-red-500' : 'border-gray-300'}
      ${disabled ? 'bg-gray-50 text-gray-500 cursor-not-allowed' : ''}
      ${className}
    `;

    return (
      <div className={fullWidth ? 'w-full' : ''}>
        {label && (
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            {label}
            {required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}

        <div className="relative">
          {leftIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
              {leftIcon}
            </div>
          )}

          <input
            ref={ref}
            type={type}
            disabled={disabled}
            className={inputClasses}
            aria-invalid={error ? 'true' : 'false'}
            aria-describedby={
              error ? `${props.id}-error` : hint ? `${props.id}-hint` : undefined
            }
            {...props}
          />

          {rightIcon && !error && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
              {rightIcon}
            </div>
          )}

          {error && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-red-500">
              <AlertCircle className="w-5 h-5" />
            </div>
          )}
        </div>

        {error && (
          <p
            id={`${props.id}-error`}
            className="mt-1.5 text-sm text-red-600 flex items-center gap-1"
          >
            {error}
          </p>
        )}

        {hint && !error && (
          <p
            id={`${props.id}-hint`}
            className="mt-1.5 text-sm text-gray-500"
          >
            {hint}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
