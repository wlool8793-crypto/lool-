import React from 'react';
import { useCV } from '@/contexts/CVContext';
import { getStepProgress } from '@/utils/validation';
import { CheckCircle, Circle, AlertCircle } from 'lucide-react';

interface ProgressIndicatorProps {
  currentStep: string;
}

const steps = [
  { id: 'personal', name: 'Personal Info', description: 'Basic information' },
  { id: 'summary', name: 'Summary', description: 'Professional summary' },
  { id: 'experience', name: 'Experience', description: 'Work history' },
  { id: 'education', name: 'Education', description: 'Academic background' },
  { id: 'skills', name: 'Skills', description: 'Technical & soft skills' },
  { id: 'projects', name: 'Projects', description: 'Personal & professional projects' },
  { id: 'certifications', name: 'Certifications', description: 'Professional certifications' },
  { id: 'languages', name: 'Languages', description: 'Language proficiency' },
  { id: 'preview', name: 'Preview', description: 'Review & export' },
];

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({ currentStep }) => {
  const { state } = useCV();
  const stepProgress = getStepProgress(state.cvData);

  const getCurrentStepIndex = () => {
    return steps.findIndex(step => step.id === currentStep);
  };

  const currentIndex = getCurrentStepIndex();

  return (
    <nav className="flex justify-center">
      <ol className="flex items-center space-x-1 sm:space-x-4 overflow-x-auto pb-2">
        {steps.map((step, index) => {
          const isCompleted = index < currentIndex;
          const isCurrent = index === currentIndex;
          const stepId = step.id as keyof typeof stepProgress;
          const isStepValid = stepProgress[stepId];

          return (
            <li key={step.id} className="flex items-center flex-shrink-0">
              <div className="flex items-center">
                <div className={`flex items-center justify-center w-6 h-6 sm:w-8 sm:h-8 rounded-full border-2 ${
                  isCompleted
                    ? 'bg-green-500 border-green-500 text-white'
                    : isCurrent
                    ? isStepValid
                      ? 'border-blue-500 text-blue-500'
                      : 'border-orange-500 text-orange-500'
                    : isStepValid
                    ? 'border-green-500 text-green-500'
                    : 'border-gray-300 text-gray-300'
                }`}>
                  {isCompleted ? (
                    <CheckCircle className="w-3 h-3 sm:w-5 sm:h-5" />
                  ) : isStepValid ? (
                    <Circle className="w-2 h-2 sm:w-4 sm:h-4" />
                  ) : (
                    <AlertCircle className="w-3 h-3 sm:w-4 sm:h-4" />
                  )}
                </div>
                <div className="ml-1 sm:ml-3 hidden sm:block">
                  <p className={`text-xs sm:text-sm font-medium ${
                    isCurrent ? 'text-blue-600' : isCompleted ? 'text-green-600' : 'text-gray-500'
                  }`}>
                    {step.name}
                  </p>
                  <p className="text-xs text-gray-500 hidden md:block">{step.description}</p>
                </div>
              </div>

              {index < steps.length - 1 && (
                <div className={`ml-1 sm:ml-3 w-4 sm:w-8 h-0.5 ${
                  index < currentIndex ? 'bg-green-500' : 'bg-gray-300'
                }`} />
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
};