import * as React from 'react';
import { cn } from '@/lib/utils';
import { ChevronDown, Check } from 'lucide-react';

export interface DropdownOption {
  value: string;
  label: string;
  disabled?: boolean;
  icon?: React.ReactNode;
  description?: string;
}

export interface DropdownProps {
  options: DropdownOption[];
  value?: string;
  onValueChange: (value: string) => void;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
  required?: boolean;
  label?: string;
  error?: string;
  helperText?: string;
  searchable?: boolean;
  multiSelect?: boolean;
  selectedValues?: string[];
}

const Dropdown: React.FC<DropdownProps> = ({
  options,
  value,
  onValueChange,
  placeholder = 'Select an option...',
  className,
  disabled = false,
  required = false,
  label,
  error,
  helperText,
  searchable = false,
  multiSelect = false,
  selectedValues = [],
}) => {
  const [isOpen, setIsOpen] = React.useState(false);
  const [searchTerm, setSearchTerm] = React.useState('');
  const dropdownRef = React.useRef<HTMLDivElement>(null);
  const searchInputRef = React.useRef<HTMLInputElement>(null);

  const selectedOption = options.find(option => option.value === value);
  const selectedOptions = options.filter(option => selectedValues.includes(option.value));

  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleEscape);
      if (searchable && searchInputRef.current) {
        searchInputRef.current.focus();
      }
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, searchable]);

  const filteredOptions = options.filter(option =>
    option.label.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleOptionClick = (optionValue: string) => {
    if (multiSelect) {
      const newSelectedValues = selectedValues.includes(optionValue)
        ? selectedValues.filter(v => v !== optionValue)
        : [...selectedValues, optionValue];
      onValueChange(newSelectedValues.join(','));
    } else {
      onValueChange(optionValue);
      setIsOpen(false);
    }
  };

  const removeSelectedValue = (valueToRemove: string, event: React.MouseEvent) => {
    event.stopPropagation();
    const newSelectedValues = selectedValues.filter(v => v !== valueToRemove);
    onValueChange(newSelectedValues.join(','));
  };

  const displayValue = multiSelect
    ? selectedOptions.map(opt => opt.label).join(', ')
    : selectedOption?.label || placeholder;

  return (
    <div className="space-y-1.5">
      {label && (
        <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}

      <div ref={dropdownRef} className="relative">
        <button
          type="button"
          onClick={() => !disabled && setIsOpen(!isOpen)}
          className={cn(
            'flex h-9 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm ring-offset-background',
            'focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
            'disabled:cursor-not-allowed disabled:opacity-50',
            error && 'border-red-500 focus:ring-red-500',
            className
          )}
          disabled={disabled}
          aria-haspopup="listbox"
          aria-expanded={isOpen}
        >
          <div className="flex flex-1 items-center overflow-hidden">
            {multiSelect && selectedOptions.length > 0 ? (
              <div className="flex flex-wrap gap-1">
                {selectedOptions.map((option) => (
                  <span
                    key={option.value}
                    className="inline-flex items-center px-2 py-1 rounded bg-secondary-100 text-secondary-700 text-xs"
                  >
                    {option.label}
                    <button
                      type="button"
                      onClick={(e) => removeSelectedValue(option.value, e)}
                      className="ml-1 hover:text-red-600"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            ) : (
              <span className={cn(displayValue === placeholder ? 'text-muted-foreground' : 'text-foreground')}>
                {displayValue}
              </span>
            )}
          </div>
          <ChevronDown
            className={cn(
              'h-4 w-4 text-muted-foreground transition-transform',
              isOpen && 'rotate-180'
            )}
          />
        </button>

        {isOpen && (
          <div className="absolute z-50 mt-1 w-full rounded-md border bg-popover shadow-md animate-slide-up">
            {searchable && (
              <div className="p-2 border-b">
                <input
                  ref={searchInputRef}
                  type="text"
                  placeholder="Search..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full h-8 px-2 text-sm border rounded focus:outline-none focus:ring-1 focus:ring-ring"
                />
              </div>
            )}

            <div className="max-h-60 overflow-auto">
              {filteredOptions.length === 0 ? (
                <div className="py-6 text-center text-sm text-muted-foreground">
                  No options found
                </div>
              ) : (
                filteredOptions.map((option) => {
                  const isSelected = multiSelect
                    ? selectedValues.includes(option.value)
                    : value === option.value;

                  return (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => !option.disabled && handleOptionClick(option.value)}
                      className={cn(
                        'w-full px-3 py-2 text-left text-sm hover:bg-accent hover:text-accent-foreground transition-colors',
                        isSelected && 'bg-accent text-accent-foreground',
                        option.disabled && 'opacity-50 cursor-not-allowed',
                        'flex items-center space-x-2'
                      )}
                      disabled={option.disabled}
                      role="option"
                      aria-selected={isSelected}
                    >
                      {multiSelect && (
                        <div className="w-4 h-4 border rounded flex items-center justify-center">
                          {isSelected && <Check className="w-3 h-3" />}
                        </div>
                      )}
                      {option.icon && <span className="flex-shrink-0">{option.icon}</span>}
                      <div className="flex-1">
                        <div>{option.label}</div>
                        {option.description && (
                          <div className="text-xs text-muted-foreground">{option.description}</div>
                        )}
                      </div>
                      {!multiSelect && isSelected && (
                        <Check className="w-4 h-4 text-primary-600" />
                      )}
                    </button>
                  );
                })
              )}
            </div>
          </div>
        )}
      </div>

      {(error || helperText) && (
        <div className="text-xs">
          {error && (
            <span className="text-red-600">{error}</span>
          )}
          {!error && helperText && (
            <span className="text-muted-foreground">{helperText}</span>
          )}
        </div>
      )}
    </div>
  );
};

export { Dropdown };