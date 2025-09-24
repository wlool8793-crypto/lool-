import * as React from 'react';
import { cn } from '@/lib/utils';
import { Check, Circle, ChevronRight } from 'lucide-react';

export interface Step {
  id: string;
  title: string;
  description?: string;
  icon?: React.ReactNode;
  isCompleted?: boolean;
  isCurrent?: boolean;
  isOptional?: boolean;
}

export interface StepperProps {
  steps: Step[];
  currentStep: number;
  onStepClick?: (stepIndex: number) => void;
  orientation?: 'horizontal' | 'vertical';
  variant?: 'default' | 'minimal' | 'numbered';
  className?: string;
}

const Stepper: React.FC<StepperProps> = ({
  steps,
  currentStep,
  onStepClick,
  orientation = 'horizontal',
  variant = 'default',
  className,
}) => {
  const isVertical = orientation === 'vertical';

  return (
    <div
      className={cn(
        'flex',
        isVertical ? 'flex-col space-y-4' : 'items-center space-x-4',
        className
      )}
    >
      {steps.map((step, index) => (
        <React.Fragment key={step.id}>
          <StepComponent
            step={step}
            index={index}
            isCurrent={currentStep === index}
            isCompleted={currentStep > index}
            isLast={index === steps.length - 1}
            orientation={orientation}
            variant={variant}
            onClick={() => onStepClick?.(index)}
          />
          {!isLast && index < steps.length - 1 && (
            <Connector
              isCompleted={currentStep > index}
              orientation={orientation}
              variant={variant}
            />
          )}
        </React.Fragment>
      ))}
    </div>
  );
};

interface StepComponentProps {
  step: Step;
  index: number;
  isCurrent: boolean;
  isCompleted: boolean;
  isLast: boolean;
  orientation: 'horizontal' | 'vertical';
  variant: 'default' | 'minimal' | 'numbered';
  onClick?: () => void;
}

const StepComponent: React.FC<StepComponentProps> = ({
  step,
  index,
  isCurrent,
  isCompleted,
  orientation,
  variant,
  onClick,
}) => {
  const isClickable = onClick && (isCompleted || index === 0);

  const handleClick = () => {
    if (isClickable) {
      onClick();
    }
  };

  return (
    <div
      className={cn(
        'flex items-center',
        orientation === 'vertical' ? 'w-full' : 'flex-shrink-0',
        isClickable && 'cursor-pointer hover:opacity-80 transition-opacity'
      )}
      onClick={handleClick}
    >
      {variant === 'default' && (
        <div className="flex items-center space-x-3">
          <StepIndicator
            isCurrent={isCurrent}
            isCompleted={isCompleted}
            variant={variant}
            icon={step.icon}
            stepNumber={index + 1}
          />
          <div className="flex flex-col">
            <h3
              className={cn(
                'text-sm font-medium',
                isCurrent && 'text-primary-600',
                isCompleted && 'text-secondary-600',
                !isCurrent && !isCompleted && 'text-muted-foreground'
              )}
            >
              {step.title}
              {step.isOptional && (
                <span className="text-xs text-muted-foreground ml-1">
                  (Optional)
                </span>
              )}
            </h3>
            {step.description && (
              <p
                className={cn(
                  'text-xs',
                  isCurrent && 'text-primary-500',
                  isCompleted && 'text-secondary-500',
                  !isCurrent && !isCompleted && 'text-muted-foreground'
                )}
              >
                {step.description}
              </p>
            )}
          </div>
        </div>
      )}

      {variant === 'minimal' && (
        <div className="flex items-center space-x-2">
          <div
            className={cn(
              'w-2 h-2 rounded-full transition-colors',
              isCurrent && 'bg-primary-600',
              isCompleted && 'bg-secondary-600',
              !isCurrent && !isCompleted && 'bg-muted-foreground'
            )}
          />
          <span
            className={cn(
              'text-sm font-medium',
              isCurrent && 'text-primary-600',
              isCompleted && 'text-secondary-600',
              !isCurrent && !isCompleted && 'text-muted-foreground'
            )}
          >
            {step.title}
          </span>
        </div>
      )}

      {variant === 'numbered' && (
        <div className="flex items-center">
          <div
            className={cn(
              'w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium border-2 transition-colors',
              isCurrent && 'border-primary-600 text-primary-600 bg-primary-50',
              isCompleted && 'border-secondary-600 text-secondary-600 bg-secondary-50',
              !isCurrent && !isCompleted && 'border-muted-foreground text-muted-foreground'
            )}
          >
            {isCompleted ? (
              <Check className="w-4 h-4" />
            ) : (
              index + 1
            )}
          </div>
        </div>
      )}
    </div>
  );
};

interface StepIndicatorProps {
  isCurrent: boolean;
  isCompleted: boolean;
  variant: 'default' | 'minimal' | 'numbered';
  icon?: React.ReactNode;
  stepNumber: number;
}

const StepIndicator: React.FC<StepIndicatorProps> = ({
  isCurrent,
  isCompleted,
  icon,
  stepNumber,
}) => {
  if (isCompleted) {
    return (
      <div className="w-8 h-8 rounded-full bg-secondary-600 flex items-center justify-center">
        <Check className="w-4 h-4 text-white" />
      </div>
    );
  }

  if (isCurrent) {
    return (
      <div className="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center">
        {icon || (
          <Circle className="w-3 h-3 text-white fill-current" />
        )}
      </div>
    );
  }

  return (
    <div className="w-8 h-8 rounded-full border-2 border-muted-300 flex items-center justify-center">
      <span className="text-sm font-medium text-muted-500">
        {stepNumber}
      </span>
    </div>
  );
};

interface ConnectorProps {
  isCompleted: boolean;
  orientation: 'horizontal' | 'vertical';
  variant: 'default' | 'minimal' | 'numbered';
}

const Connector: React.FC<ConnectorProps> = ({
  isCompleted,
  orientation,
  variant,
}) => {
  if (variant === 'minimal') {
    return (
      <div
        className={cn(
          'flex-1',
          orientation === 'horizontal' ? 'h-0.5' : 'w-0.5 h-4',
          isCompleted ? 'bg-secondary-600' : 'bg-muted-300'
        )}
      />
    );
  }

  if (variant === 'numbered') {
    return (
      <div
        className={cn(
          orientation === 'horizontal' ? 'flex-1 h-0.5' : 'w-0.5 h-8',
          isCompleted ? 'bg-secondary-600' : 'bg-muted-300'
        )}
      />
    );
  }

  return (
    <ChevronRight
      className={cn(
        'flex-shrink-0',
        isCompleted ? 'text-secondary-600' : 'text-muted-300'
      )}
    />
  );
};

export { Stepper };