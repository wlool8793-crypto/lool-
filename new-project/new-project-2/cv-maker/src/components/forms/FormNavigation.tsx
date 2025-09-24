import React from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  ChevronLeft,
  ChevronRight,
  Save,
  Eye,
  Loader2,
  RotateCcw,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

export interface FormNavigationProps {
  currentStep: number;
  totalSteps: number;
  onPrevious?: () => void;
  onNext?: () => void;
  onSave?: () => void;
  onPreview?: () => void;
  onSubmit?: () => void;
  onReset?: () => void;
  isPreviousDisabled?: boolean;
  isNextDisabled?: boolean;
  isLoading?: boolean;
  isSaving?: boolean;
  isSubmitting?: boolean;
  isValid?: boolean;
  saveMessage?: string;
  className?: string;
  variant?: 'default' | 'compact' | 'minimal';
}

const FormNavigation: React.FC<FormNavigationProps> = ({
  currentStep,
  totalSteps,
  onPrevious,
  onNext,
  onSave,
  onPreview,
  onSubmit,
  onReset,
  isPreviousDisabled = false,
  isNextDisabled = false,
  isLoading = false,
  isSaving = false,
  isSubmitting = false,
  isValid = true,
  saveMessage,
  className,
  variant = 'default',
}) => {
  const isFirstStep = currentStep === 0;
  const isLastStep = currentStep === totalSteps - 1;
  const progress = ((currentStep + 1) / totalSteps) * 100;

  if (variant === 'minimal') {
    return (
      <div className={cn('flex items-center justify-between', className)}>
        <div className="flex items-center gap-2">
          {!isFirstStep && onPrevious && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onPrevious}
              disabled={isPreviousDisabled || isLoading}
            >
              <ChevronLeft className="w-4 h-4" />
            </Button>
          )}

          <Badge variant="outline" className="text-xs">
            {currentStep + 1} / {totalSteps}
          </Badge>
        </div>

        <div className="flex items-center gap-2">
          {onSave && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onSave}
              disabled={isLoading || isSaving}
            >
              {isSaving ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Save className="w-4 h-4" />
              )}
            </Button>
          )}

          {!isLastStep && onNext && (
            <Button
              size="sm"
              onClick={onNext}
              disabled={isNextDisabled || isLoading || !isValid}
            >
              <ChevronRight className="w-4 h-4" />
            </Button>
          )}

          {isLastStep && onSubmit && (
            <Button
              size="sm"
              onClick={onSubmit}
              disabled={isLoading || isSubmitting || !isValid}
            >
              {isSubmitting ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <CheckCircle className="w-4 h-4" />
              )}
            </Button>
          )}
        </div>
      </div>
    );
  }

  if (variant === 'compact') {
    return (
      <div className={cn('flex items-center justify-between bg-gray-50 p-4 rounded-lg', className)}>
        <div className="flex items-center gap-4">
          <div className="text-sm text-gray-600">
            Step {currentStep + 1} of {totalSteps}
          </div>

          {!isValid && (
            <div className="flex items-center gap-1 text-red-600 text-sm">
              <AlertCircle className="w-4 h-4" />
              <span>Please fix errors before continuing</span>
            </div>
          )}

          {saveMessage && (
            <div className="flex items-center gap-1 text-green-600 text-sm">
              <CheckCircle className="w-4 h-4" />
              <span>{saveMessage}</span>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          {!isFirstStep && onPrevious && (
            <Button
              variant="outline"
              size="sm"
              onClick={onPrevious}
              disabled={isPreviousDisabled || isLoading}
            >
              Previous
            </Button>
          )}

          {onSave && (
            <Button
              variant="outline"
              size="sm"
              onClick={onSave}
              disabled={isLoading || isSaving}
            >
              {isSaving ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  Save
                </>
              )}
            </Button>
          )}

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

          {!isLastStep && onNext && (
            <Button
              size="sm"
              onClick={onNext}
              disabled={isNextDisabled || isLoading || !isValid}
            >
              Next
              <ChevronRight className="w-4 h-4 ml-2" />
            </Button>
          )}

          {isLastStep && onSubmit && (
            <Button
              size="sm"
              onClick={onSubmit}
              disabled={isLoading || isSubmitting || !isValid}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Submit
                </>
              )}
            </Button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className={cn('space-y-4', className)}>
      {/* Progress Summary */}
      <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center gap-4">
          <div>
            <div className="text-sm font-medium text-gray-900">
              Step {currentStep + 1} of {totalSteps}
            </div>
            <div className="text-xs text-gray-500">
              {Math.round(progress)}% Complete
            </div>
          </div>

          <div className="flex items-center gap-2">
            {!isValid && (
              <Badge variant="destructive" className="text-xs flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                Form has errors
              </Badge>
            )}

            {saveMessage && (
              <Badge variant="secondary" className="text-xs flex items-center gap-1">
                <CheckCircle className="w-3 h-3" />
                {saveMessage}
              </Badge>
            )}
          </div>
        </div>

        {onReset && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onReset}
            disabled={isLoading}
          >
            <RotateCcw className="w-4 h-4 mr-2" />
            Reset
          </Button>
        )}
      </div>

      {/* Navigation Buttons */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {!isFirstStep && onPrevious && (
            <Button
              variant="outline"
              onClick={onPrevious}
              disabled={isPreviousDisabled || isLoading}
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
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  Save Progress
                </>
              )}
            </Button>
          )}

          {onPreview && (
            <Button
              variant="outline"
              onClick={onPreview}
              disabled={isLoading}
            >
              <Eye className="w-4 h-4 mr-2" />
              Preview
            </Button>
          )}

          {!isLastStep && onNext && (
            <Button
              onClick={onNext}
              disabled={isNextDisabled || isLoading || !isValid}
            >
              Continue
              <ChevronRight className="w-4 h-4 ml-2" />
            </Button>
          )}

          {isLastStep && onSubmit && (
            <Button
              onClick={onSubmit}
              disabled={isLoading || isSubmitting || !isValid}
              size="lg"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Submit Application
                </>
              )}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export { FormNavigation };