import type { CVData } from '@/types/cv';

export interface ValidationResult {
  isValid: boolean;
  errors: Record<string, string>;
}

export const validateStep = (step: string, cvData: CVData): ValidationResult => {
  const errors: Record<string, string> = {};

  switch (step) {
    case 'personal':
      if (!cvData.personalInfo.fullName.trim()) {
        errors.fullName = 'Full name is required';
      }
      if (!cvData.personalInfo.email.trim()) {
        errors.email = 'Email is required';
      } else if (!/\S+@\S+\.\S+/.test(cvData.personalInfo.email)) {
        errors.email = 'Email is invalid';
      }
      if (!cvData.personalInfo.phone.trim()) {
        errors.phone = 'Phone number is required';
      }
      if (!cvData.personalInfo.address.trim()) {
        errors.address = 'Address is required';
      }
      break;

    case 'summary':
      if (!cvData.professionalSummary.trim()) {
        errors.professionalSummary = 'Professional summary is required';
      } else if (cvData.professionalSummary.trim().length < 10) {
        errors.professionalSummary = 'Summary must be at least 10 characters long';
      }
      break;

    case 'experience':
      if (cvData.workExperience.length === 0) {
        errors.workExperience = 'At least one work experience is required';
      }
      break;

    case 'education':
      if (cvData.education.length === 0) {
        errors.education = 'At least one education entry is required';
      }
      break;

    case 'skills':
      if (cvData.skills.length === 0) {
        errors.skills = 'At least one skill is required';
      }
      break;

    case 'preview':
      // Validate that all required sections are completed
      if (!cvData.personalInfo.fullName.trim()) {
        errors.personal = 'Personal information is required';
      }
      if (!cvData.professionalSummary.trim()) {
        errors.summary = 'Professional summary is required';
      }
      if (cvData.workExperience.length === 0) {
        errors.experience = 'Work experience is required';
      }
      if (cvData.education.length === 0) {
        errors.education = 'Education is required';
      }
      break;
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
};

export const getStepProgress = (cvData: CVData): Record<string, boolean> => {
  return {
    personal: validateStep('personal', cvData).isValid,
    summary: validateStep('summary', cvData).isValid,
    experience: validateStep('experience', cvData).isValid,
    education: validateStep('education', cvData).isValid,
    skills: validateStep('skills', cvData).isValid,
    projects: cvData.projects.length > 0,
    certifications: cvData.certifications.length > 0,
    languages: cvData.languages.length > 0,
  };
};