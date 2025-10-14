import React, { SelectHTMLAttributes, forwardRef } from 'react';
import { AlertCircle, ChevronDown } from 'lucide-react';

export interface SelectOption {
  value: string | number;
  label: string;
  disabled?: boolean;
}

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  hint?: string;
  options: SelectOption[];
  placeholder?: string;
  fullWidth?: boolean;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  (
    {
      label,
      error,
      hint,
      options,
      placeholder = 'Select an option',
      fullWidth = true,
      className = '',
      disabled,
      required,
      ...props
    },
    ref
  ) => {
    const selectClasses = `
      block w-full px-4 py-2.5 pr-10 text-gray-900 bg-white border rounded-lg
      appearance-none cursor-pointer
      focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
      transition-colors duration-200
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
          <select
            ref={ref}
            disabled={disabled}
            className={selectClasses}
            aria-invalid={error ? 'true' : 'false'}
            aria-describedby={
              error ? `${props.id}-error` : hint ? `${props.id}-hint` : undefined
            }
            {...props}
          >
            {placeholder && (
              <option value="" disabled>
                {placeholder}
              </option>
            )}
            {options.map((option) => (
              <option
                key={option.value}
                value={option.value}
                disabled={option.disabled}
              >
                {option.label}
              </option>
            ))}
          </select>

          {/* Dropdown Icon */}
          <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
            {error ? (
              <AlertCircle className="w-5 h-5 text-red-500" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </div>
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

Select.displayName = 'Select';

export default Select;
