import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { CVProvider, useCV } from '../../contexts/CVContext';
import { ProgressIndicator } from './ProgressIndicator';
import { LoadingScreen } from './LoadingScreen';
import { DocumentType } from '../../types/common';

// Import CV Form Steps
import { PersonalInfoStep } from '../FormSteps/PersonalInfoStep';
import { SummaryStep } from '../FormSteps/SummaryStep';
import { ExperienceStep } from '../FormSteps/ExperienceStep';
import { EducationStep } from '../FormSteps/EducationStep';
import { SkillsStep } from '../FormSteps/SkillsStep';
import { ProjectsStep } from '../FormSteps/ProjectsStep';
import { CertificationsStep } from '../FormSteps/CertificationsStep';
import { LanguagesStep } from '../FormSteps/LanguagesStep';
import { PreviewStep } from '../FormSteps/PreviewStep';

// Import Marriage Biodata Form Steps
import { MarriagePersonalInfoStep } from '../FormSteps/Marriage/MarriagePersonalInfoStep';
import { MarriageContactStep } from '../FormSteps/Marriage/MarriageContactStep';
import { MarriageFamilyInfoStep } from '../FormSteps/Marriage/MarriageFamilyInfoStep';
import { MarriageEducationStep } from '../FormSteps/Marriage/MarriageEducationStep';
import { MarriageOccupationStep } from '../FormSteps/Marriage/MarriageOccupationStep';
import { MarriageLifestyleStep } from '../FormSteps/Marriage/MarriageLifestyleStep';
import { MarriagePartnerPreferenceStep } from '../FormSteps/Marriage/MarriagePartnerPreferenceStep';
import { MarriageHoroscopeStep } from '../FormSteps/Marriage/MarriageHoroscopeStep';
import { MarriagePhotosStep } from '../FormSteps/Marriage/MarriagePhotosStep';
import { MarriageAboutStep } from '../FormSteps/Marriage/MarriageAboutStep';
import { MarriagePreviewStep } from '../FormSteps/Marriage/MarriagePreviewStep';

interface DocumentRoutesProps {
  selectedDocument: DocumentType;
}

const cvStepComponents = {
  personal: PersonalInfoStep,
  summary: SummaryStep,
  experience: ExperienceStep,
  education: EducationStep,
  skills: SkillsStep,
  projects: ProjectsStep,
  certifications: CertificationsStep,
  languages: LanguagesStep,
  preview: PreviewStep,
};

const marriageStepComponents = {
  personal: MarriagePersonalInfoStep,
  contact: MarriageContactStep,
  family: MarriageFamilyInfoStep,
  education: MarriageEducationStep,
  occupation: MarriageOccupationStep,
  lifestyle: MarriageLifestyleStep,
  'partner-preference': MarriagePartnerPreferenceStep,
  horoscope: MarriageHoroscopeStep,
  photos: MarriagePhotosStep,
  about: MarriageAboutStep,
  preview: MarriagePreviewStep,
};

const CVRoutes: React.FC = () => {
  const { state } = useCV();
  const CurrentStep = cvStepComponents[state.currentStep as keyof typeof cvStepComponents] || PersonalInfoStep;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
      <div className="mb-6 sm:mb-8">
        <ProgressIndicator currentStep={state.currentStep} />
      </div>
      <div className="mt-4 sm:mt-8">
        <CurrentStep />
      </div>
    </div>
  );
};

const MarriageRoutes: React.FC = () => {
  const { state } = useCV();
  const CurrentStep = marriageStepComponents[state.currentStep as keyof typeof marriageStepComponents] || marriageStepComponents.personal;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
      <div className="mb-6 sm:mb-8">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">Marriage Biodata</h2>
          <div className="text-sm text-gray-600">
            {state.isSaved ? 'Auto-saved • All changes saved' : 'Unsaved changes'}
          </div>
        </div>
        {/* Placeholder for marriage progress indicator */}
        <div className="mt-4 h-2 bg-gray-200 rounded-full overflow-hidden">
          <div className="h-full bg-pink-600 rounded-full transition-all duration-300" style={{ width: '30%' }} />
        </div>
      </div>
      <div className="mt-4 sm:mt-8">
        <CurrentStep />
      </div>
    </div>
  );
};

export const DocumentRoutes: React.FC<DocumentRoutesProps> = ({ selectedDocument }) => {
  if (selectedDocument === 'cv') {
    return (
      <Routes>
        <Route path="/*" element={<CVRoutes />} />
      </Routes>
    );
  }

  if (selectedDocument === 'marriage') {
    return (
      <Routes>
        <Route path="/*" element={<MarriageRoutes />} />
      </Routes>
    );
  }

  return <LoadingScreen message="Invalid document type" />;
};