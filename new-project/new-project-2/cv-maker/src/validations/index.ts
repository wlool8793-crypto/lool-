import { z } from 'zod';

// CV Validation Schemas
export {
  personalInfoSchema,
  professionalSummarySchema,
  workExperienceSchema,
  educationSchema,
  skillSchema,
  projectSchema,
  certificationSchema,
  languageSchema,
  volunteerExperienceSchema,
  awardSchema,
  publicationSchema,
  referenceSchema,
  customSectionSchema,
  cvDataSchema,
  cvStepSchemas,
} from './cvSchemas';

export type {
  PersonalInfoFormData,
  ProfessionalSummaryFormData,
  WorkExperienceFormData,
  EducationFormData,
  SkillFormData,
  ProjectFormData,
  CertificationFormData,
  LanguageFormData,
  VolunteerExperienceFormData,
  AwardFormData,
  PublicationFormData,
  ReferenceFormData,
  CustomSectionFormData,
  CVDataFormData,
} from './cvSchemas';

// Marriage Biodata Validation Schemas
export {
  marriagePersonalInfoSchema,
  marriageContactInfoSchema,
  marriageFamilyInfoSchema,
  marriageEducationSchema,
  marriageOccupationSchema,
  marriageLifestyleSchema,
  marriagePartnerPreferenceSchema,
  marriageHoroscopeSchema,
  marriagePhotosSchema,
  marriageReferencesSchema,
  marriageAboutSchema,
  marriageBiodataSchema,
  marriageStepSchemas,
  validateAgeFromDateOfBirth,
  validateHeightFormat,
  validateIncomeFormat,
} from './marriageSchemas';

export type {
  MarriagePersonalInfoFormData,
  MarriageContactInfoFormData,
  MarriageFamilyInfoFormData,
  MarriageEducationFormData,
  MarriageOccupationFormData,
  MarriageLifestyleFormData,
  MarriagePartnerPreferenceFormData,
  MarriageHoroscopeFormData,
  MarriagePhotosFormData,
  MarriageReferencesFormData,
  MarriageAboutFormData,
  MarriageBiodataFormData,
} from './marriageSchemas';

// Common validation utilities
export const createValidationResolver = <T extends Record<string, any>>(
  schema: z.ZodSchema<T>
) => {
  return (data: any) => {
    try {
      const validatedData = schema.parse(data);
      return {
        values: validatedData,
        errors: {},
      };
    } catch (error) {
      if (error instanceof z.ZodError) {
        const fieldErrors: Record<string, string> = {};
        (error as any).errors.forEach((err: any) => {
          const fieldPath = err.path.join('.');
          fieldErrors[fieldPath] = err.message;
        });
        return {
          values: {},
          errors: fieldErrors,
        };
      }
      return {
        values: {},
        errors: {
          _form: 'An unexpected error occurred during validation',
        },
      };
    }
  };
};

export const validateStep = (
  step: string,
  data: any,
  documentType: 'cv' | 'marriage'
) => {
  // This is a simplified validation function
  // In a real implementation, you would import and use the actual schemas
  return { success: true, data };
};

export const getFieldError = (errors: Record<string, string>, fieldName: string): string | undefined => {
  return errors[fieldName] || errors[`${fieldName}.root`] || undefined;
};

export const hasFieldError = (errors: Record<string, string>, fieldName: string): boolean => {
  return Boolean(getFieldError(errors, fieldName));
};

export const clearFieldError = (errors: Record<string, string>, fieldName: string): Record<string, string> => {
  const newErrors = { ...errors };
  delete newErrors[fieldName];
  delete newErrors[`${fieldName}.root`];
  return newErrors;
};