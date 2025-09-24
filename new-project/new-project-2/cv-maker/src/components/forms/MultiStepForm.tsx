import React from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Stepper, type Step } from '@/components/ui/stepper';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress, CircularProgress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { ChevronLeft, ChevronRight, Save, Eye, Loader2 } from 'lucide-react';

export interface FormStepConfig {
  id: string;
  title: string;
  description?: string;
  component: React.ComponentType<{
    data: any;
    onChange: (data: any) => void;
    errors?: Record<string, string>;
    onNext?: () => void;
    onPrevious?: () => void;
  }>;
  validation?: (data: any) => boolean | Promise<boolean>;
  optional?: boolean;
  icon?: React.ReactNode;
}

export interface MultiStepFormProps {
  steps: FormStepConfig[];
  currentStep: number;
  data: any;
  onStepChange: (step: number) => void;
  onDataChange: (stepId: string, data: any) => void;
  onSubmit?: () => void;
  onSave?: () => void;
  onPreview?: () => void;
  errors?: Record<string, string>;
  isLoading?: boolean;
  isSaving?: boolean;
  showProgress?: boolean;
  showStepper?: boolean;
  variant?: 'default' | 'compact' | 'vertical';
  allowSkip?: boolean;
  className?: string;
}

const MultiStepForm: React.FC<MultiStepFormProps> = ({
  steps,
  currentStep,
  data,
  onStepChange,
  onDataChange,
  onSubmit,
  onSave,
  onPreview,
  errors = {},
  isLoading = false,
  isSaving = false,
  showProgress = true,
  showStepper = true,
  variant = 'default',
  allowSkip = false,
  className,
}) => {
  const currentStepConfig = steps[currentStep];
  const CurrentStepComponent = currentStepConfig?.component;

  const progress = ((currentStep + 1) / steps.length) * 100;

  const stepperSteps: Step[] = steps.map((step, index) => ({
    id: step.id,
    title: step.title,
    description: step.description,
    icon: step.icon,
    isCompleted: index < currentStep,
    isCurrent: index === currentStep,
    isOptional: step.optional,
  }));

  const handleNext = async () => {
    const currentConfig = steps[currentStep];

    // Validate current step if validation function exists
    if (currentConfig.validation) {
      const isValid = await currentConfig.validation(data[currentConfig.id]);
      if (!isValid) return;
    }

    if (currentStep < steps.length - 1) {
      onStepChange(currentStep + 1);
    } else if (onSubmit) {
      onSubmit();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      onStepChange(currentStep - 1);
    }
  };

  const handleStepClick = (stepIndex: number) => {
    // Only allow navigation to completed steps or previous steps
    if (stepIndex <= currentStep || stepIndex === 0 || allowSkip) {
      onStepChange(stepIndex);
    }
  };

  const handleStepDataChange = (stepData: any) => {
    onDataChange(steps[currentStep].id, stepData);
  };

  const isLastStep = currentStep === steps.length - 1;
  const isFirstStep = currentStep === 0;

  return (
    <div className={cn('w-full max-w-6xl mx-auto', className)}>
      {/* Progress Bar */}
      {showProgress && (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              Step {currentStep + 1} of {steps.length}
            </span>
            <span className="text-sm text-gray-500">{Math.round(progress)}% Complete</span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>
      )}

      {/* Stepper */}
      {showStepper && (
        <div className="mb-8">
          <Stepper
            steps={stepperSteps}
            currentStep={currentStep}
            onStepClick={handleStepClick}
            orientation={variant === 'vertical' ? 'vertical' : 'horizontal'}
            variant={variant === 'compact' ? 'minimal' : 'default'}
          />
        </div>
      )}

      {/* Current Step Content */}
      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                {currentStepConfig?.icon && <span className="text-primary-600">{currentStepConfig.icon}</span>}
                {currentStepConfig?.title}
                {currentStepConfig?.optional && (
                  <Badge variant="outline" className="text-xs">Optional</Badge>
                )}
              </CardTitle>
              {currentStepConfig?.description && (
                <p className="text-sm text-muted-foreground mt-1">
                  {currentStepConfig.description}
                </p>
              )}
            </div>
            {onPreview && (
              <Button
                variant="outline"
                size="sm"
                onClick={onPreview}
                disabled={isLoading}
              >
                <Eye className="w-4 h-4 mr-2" />
                Preview
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-6 h-6 animate-spin" />
              <span className="ml-2">Loading...</span>
            </div>
          ) : CurrentStepComponent ? (
            <CurrentStepComponent
              data={data[currentStepConfig.id] || {}}
              onChange={handleStepDataChange}
              errors={errors}
              onNext={handleNext}
              onPrevious={handlePrevious}
            />
          ) : null}
        </CardContent>
      </Card>

      {/* Form Navigation */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {!isFirstStep && (
            <Button
              variant="outline"
              onClick={handlePrevious}
              disabled={isLoading}
            >
              <ChevronLeft className="w-4 h-4 mr-2" />
              Previous
            </Button>
          )}
        </div>

        <div className="flex items-center gap-2">
          {onSave && (
            <Button
              variant="outline"
              onClick={onSave}
              disabled={isLoading || isSaving}
            >
              {isSaving ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Save className="w-4 h-4 mr-2" />
              )}
              Save
            </Button>
          )}

          {!isLastStep ? (
            <Button onClick={handleNext} disabled={isLoading}>
              Next
              <ChevronRight className="w-4 h-4 ml-2" />
            </Button>
          ) : (
            <Button onClick={handleNext} disabled={isLoading}>
              {onSubmit ? 'Submit' : 'Finish'}
              <ChevronRight className="w-4 h-4 ml-2" />
            </Button>
          )}
        </div>
      </div>

      {/* Auto-save Indicator */}
      {isSaving && (
        <div className="mt-4 text-center">
          <Badge variant="secondary" className="text-xs">
            <Loader2 className="w-3 h-3 mr-1 animate-spin" />
            Auto-saving...
          </Badge>
        </div>
      )}
    </div>
  );
};

export { MultiStepForm };