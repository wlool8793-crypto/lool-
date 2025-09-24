import * as React from 'react';
import { cn } from '@/lib/utils';
import { Eye, EyeOff, AlertCircle, CheckCircle, Info } from 'lucide-react';

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  required?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  showPasswordToggle?: boolean;
  isValid?: boolean;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({
    className,
    type,
    label,
    error,
    helperText,
    required,
    leftIcon,
    rightIcon,
    showPasswordToggle = false,
    isValid,
    id,
    ...props
  }, ref) => {
    const [showPassword, setShowPassword] = React.useState(false);
    const [inputType, setInputType] = React.useState(type);

    const inputId = id || React.useId();
    const hasError = !!error;
    const hasSuccess = isValid && !hasError;

    React.useEffect(() => {
      if (type === 'password' && showPasswordToggle) {
        setInputType(showPassword ? 'text' : 'password');
      }
    }, [showPassword, type, showPasswordToggle]);

    const togglePassword = () => {
      setShowPassword(!showPassword);
    };

    return (
      <div className="space-y-1.5">
        {label && (
          <label
            htmlFor={inputId}
            className={cn(
              'text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70',
              hasError && 'text-red-600',
              hasSuccess && 'text-green-600'
            )}
          >
            {label}
            {required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}

        <div className="relative">
          {leftIcon && (
            <div className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground">
              {leftIcon}
            </div>
          )}

          <input
            type={inputType}
            className={cn(
              'flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50',
              leftIcon && 'pl-9',
              (rightIcon || showPasswordToggle || hasError || hasSuccess) && 'pr-9',
              hasError && 'border-red-500 focus-visible:ring-red-500',
              hasSuccess && 'border-green-500 focus-visible:ring-green-500',
              className
            )}
            ref={ref}
            id={inputId}
            {...props}
          />

          <div className="absolute right-3 top-1/2 flex -translate-y-1/2 items-center gap-1">
            {showPasswordToggle && type === 'password' && (
              <button
                type="button"
                onClick={togglePassword}
                className="text-muted-foreground hover:text-foreground focus:outline-none"
                tabIndex={-1}
              >
                {showPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </button>
            )}

            {rightIcon && !hasError && !hasSuccess && (
              <div className="text-muted-foreground">{rightIcon}</div>
            )}

            {hasError && <AlertCircle className="h-4 w-4 text-red-500" />}
            {hasSuccess && <CheckCircle className="h-4 w-4 text-green-500" />}
          </div>
        </div>

        {(error || helperText) && (
          <div className="text-xs">
            {error && (
              <span className="text-red-600 flex items-center gap-1">
                <AlertCircle className="h-3 w-3" />
                {error}
              </span>
            )}
            {!error && helperText && (
              <span className="text-muted-foreground flex items-center gap-1">
                <Info className="h-3 w-3" />
                {helperText}
              </span>
            )}
          </div>
        )}
      </div>
    );
  }
);
Input.displayName = 'Input';

export { Input };