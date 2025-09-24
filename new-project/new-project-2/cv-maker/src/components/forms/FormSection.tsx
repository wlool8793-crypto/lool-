import React from 'react';
import { cn } from '@/lib/utils';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { HelpCircle, AlertTriangle } from 'lucide-react';

export interface FormSectionProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
  required?: boolean;
  optional?: boolean;
  error?: string;
  helpText?: string;
  icon?: React.ReactNode;
  collapsible?: boolean;
  defaultCollapsed?: boolean;
}

const FormSection: React.FC<FormSectionProps> = ({
  title,
  description,
  children,
  className,
  required = false,
  optional = false,
  error,
  helpText,
  icon,
  collapsible = false,
  defaultCollapsed = false,
}) => {
  const [isCollapsed, setIsCollapsed] = React.useState(defaultCollapsed);

  return (
    <Card className={cn('mb-6', error && 'border-red-200 bg-red-50', className)}>
      <CardHeader
        className={cn(
          'cursor-pointer transition-colors',
          collapsible && 'hover:bg-gray-50',
          error && 'bg-red-50'
        )}
        onClick={() => collapsible && setIsCollapsed(!isCollapsed)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {icon && <div className="text-primary-600">{icon}</div>}
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <CardTitle className="text-lg">{title}</CardTitle>
                {required && (
                  <Badge variant="destructive" className="text-xs">Required</Badge>
                )}
                {optional && (
                  <Badge variant="outline" className="text-xs">Optional</Badge>
                )}
                {error && (
                  <Badge variant="destructive" className="text-xs flex items-center gap-1">
                    <AlertTriangle className="w-3 h-3" />
                    Error
                  </Badge>
                )}
              </div>
              {description && (
                <p className="text-sm text-muted-foreground mt-1">
                  {description}
                </p>
              )}
              {error && (
                <p className="text-sm text-red-600 mt-1 flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3" />
                  {error}
                </p>
              )}
            </div>
          </div>
          {collapsible && (
            <div className="text-gray-400">
              <svg
                className={cn(
                  'w-5 h-5 transition-transform',
                  isCollapsed ? 'rotate-0' : 'rotate-180'
                )}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </div>
          )}
        </div>
      </CardHeader>

      {!isCollapsed && (
        <CardContent>
          {children}
          {helpText && (
            <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-start gap-2">
                <HelpCircle className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-blue-700">{helpText}</p>
              </div>
            </div>
          )}
        </CardContent>
      )}
    </Card>
  );
};

export { FormSection };