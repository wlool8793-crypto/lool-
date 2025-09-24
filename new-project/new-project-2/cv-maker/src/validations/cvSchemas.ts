import { z } from 'zod';
import type { CVData } from '../types/cv';

// Personal Info Schema
export const personalInfoSchema = z.object({
  fullName: z.string().min(1, 'Full name is required').max(100, 'Full name must be less than 100 characters'),
  email: z.string().email('Invalid email address').max(100, 'Email must be less than 100 characters'),
  phone: z.string().min(1, 'Phone number is required').regex(/^[+]?[\d\s\-()]+$/, 'Invalid phone number format'),
  address: z.string().min(1, 'Address is required').max(200, 'Address must be less than 200 characters'),
  linkedin: z.string().url('Invalid LinkedIn URL').optional().or(z.literal('')),
  website: z.string().url('Invalid website URL').optional().or(z.literal('')),
  github: z.string().url('Invalid GitHub URL').optional().or(z.literal('')),
  portfolio: z.string().url('Invalid portfolio URL').optional().or(z.literal('')),
  twitter: z.string().url('Invalid Twitter URL').optional().or(z.literal('')),
  facebook: z.string().url('Invalid Facebook URL').optional().or(z.literal('')),
  instagram: z.string().url('Invalid Instagram URL').optional().or(z.literal('')),
  profileImage: z.string().optional(),
  headline: z.string().max(100, 'Headline must be less than 100 characters').optional(),
  summary: z.string().max(500, 'Summary must be less than 500 characters').optional(),
});

// Professional Summary Schema
export const professionalSummarySchema = z.object({
  summary: z.string().min(10, 'Professional summary must be at least 10 characters').max(1000, 'Summary must be less than 1000 characters'),
});

// Work Experience Schema
export const workExperienceSchema = z.object({
  id: z.string(),
  company: z.string().min(1, 'Company name is required').max(100, 'Company name must be less than 100 characters'),
  position: z.string().min(1, 'Position is required').max(100, 'Position must be less than 100 characters'),
  startDate: z.string().min(1, 'Start date is required'),
  endDate: z.string().min(1, 'End date is required'),
  current: z.boolean(),
  description: z.string().min(10, 'Description must be at least 10 characters').max(1000, 'Description must be less than 1000 characters'),
  achievements: z.array(z.string().min(1, 'Achievement cannot be empty')).max(10, 'Maximum 10 achievements allowed'),
  skills: z.array(z.string().min(1, 'Skill cannot be empty')).max(20, 'Maximum 20 skills allowed'),
  location: z.string().min(1, 'Location is required').max(100, 'Location must be less than 100 characters'),
  employmentType: z.enum(['full-time', 'part-time', 'contract', 'internship', 'freelance'], {
    message: 'Please select a valid employment type',
  }),
  industry: z.string().min(1, 'Industry is required').max(50, 'Industry must be less than 50 characters'),
  website: z.string().url('Invalid company website URL').optional().or(z.literal('')),
}).refine(
  (data) => !data.current || data.endDate === '',
  {
    message: 'End date must be empty for current position',
    path: ['endDate'],
  }
).refine(
  (data) => data.current || new Date(data.endDate) > new Date(data.startDate),
  {
    message: 'End date must be after start date',
    path: ['endDate'],
  }
);

// Education Schema
export const educationSchema = z.object({
  id: z.string(),
  institution: z.string().min(1, 'Institution name is required').max(100, 'Institution name must be less than 100 characters'),
  degree: z.string().min(1, 'Degree is required').max(50, 'Degree must be less than 50 characters'),
  field: z.string().min(1, 'Field of study is required').max(50, 'Field must be less than 50 characters'),
  startDate: z.string().min(1, 'Start date is required'),
  endDate: z.string().min(1, 'End date is required'),
  gpa: z.string().regex(/^(\d+(\.\d+)?)$/, 'GPA must be a valid number').optional().or(z.literal('')),
  honors: z.string().max(100, 'Honors must be less than 100 characters').optional(),
  activities: z.array(z.string().min(1, 'Activity cannot be empty')).max(10, 'Maximum 10 activities allowed'),
  achievements: z.array(z.string().min(1, 'Achievement cannot be empty')).max(10, 'Maximum 10 achievements allowed'),
  description: z.string().max(500, 'Description must be less than 500 characters').optional(),
  coursework: z.array(z.string().min(1, 'Course cannot be empty')).max(20, 'Maximum 20 courses allowed'),
  location: z.string().min(1, 'Location is required').max(100, 'Location must be less than 100 characters'),
  website: z.string().url('Invalid institution website URL').optional().or(z.literal('')),
}).refine(
  (data) => new Date(data.endDate) > new Date(data.startDate),
  {
    message: 'End date must be after start date',
    path: ['endDate'],
  }
);

// Skill Schema
export const skillSchema = z.object({
  id: z.string(),
  name: z.string().min(1, 'Skill name is required').max(50, 'Skill name must be less than 50 characters'),
  category: z.enum(['technical', 'soft', 'language', 'tool', 'framework', 'database', 'certification'], {
    message: 'Please select a valid skill category',
  }),
  level: z.enum(['beginner', 'intermediate', 'advanced', 'expert'], {
    message: 'Please select a valid skill level',
  }),
  yearsOfExperience: z.number().min(0, 'Years of experience must be at least 0').max(50, 'Years of experience must be less than 50').optional(),
  description: z.string().max(200, 'Description must be less than 200 characters').optional(),
  certifications: z.array(z.string().min(1, 'Certification cannot be empty')).max(10, 'Maximum 10 certifications allowed').optional(),
});

// Project Schema
export const projectSchema = z.object({
  id: z.string(),
  title: z.string().min(1, 'Project title is required').max(100, 'Project title must be less than 100 characters'),
  description: z.string().min(10, 'Description must be at least 10 characters').max(1000, 'Description must be less than 1000 characters'),
  technologies: z.array(z.string().min(1, 'Technology cannot be empty')).min(1, 'At least one technology is required').max(20, 'Maximum 20 technologies allowed'),
  startDate: z.string().min(1, 'Start date is required'),
  endDate: z.string().optional(),
  url: z.string().url('Invalid project URL').optional().or(z.literal('')),
  github: z.string().url('Invalid GitHub URL').optional().or(z.literal('')),
  demo: z.string().url('Invalid demo URL').optional().or(z.literal('')),
  achievements: z.array(z.string().min(1, 'Achievement cannot be empty')).max(10, 'Maximum 10 achievements allowed'),
  role: z.string().min(1, 'Role is required').max(50, 'Role must be less than 50 characters'),
  teamSize: z.number().min(1, 'Team size must be at least 1').max(100, 'Team size must be less than 100').optional(),
  highlights: z.array(z.string().min(1, 'Highlight cannot be empty')).max(10, 'Maximum 10 highlights allowed'),
  images: z.array(z.string().url('Invalid image URL')).max(10, 'Maximum 10 images allowed').optional(),
}).refine(
  (data) => !data.endDate || new Date(data.endDate) > new Date(data.startDate),
  {
    message: 'End date must be after start date',
    path: ['endDate'],
  }
);

// Certification Schema
export const certificationSchema = z.object({
  id: z.string(),
  name: z.string().min(1, 'Certification name is required').max(100, 'Certification name must be less than 100 characters'),
  issuer: z.string().min(1, 'Issuer is required').max(100, 'Issuer must be less than 100 characters'),
  issueDate: z.string().min(1, 'Issue date is required'),
  expiryDate: z.string().optional(),
  credentialId: z.string().max(50, 'Credential ID must be less than 50 characters').optional(),
  url: z.string().url('Invalid certification URL').optional().or(z.literal('')),
  description: z.string().max(500, 'Description must be less than 500 characters').optional(),
  skills: z.array(z.string().min(1, 'Skill cannot be empty')).max(20, 'Maximum 20 skills allowed').optional(),
  level: z.enum(['basic', 'intermediate', 'advanced', 'expert'], {
    message: 'Please select a valid certification level',
  }),
}).refine(
  (data) => !data.expiryDate || new Date(data.expiryDate) > new Date(data.issueDate),
  {
    message: 'Expiry date must be after issue date',
    path: ['expiryDate'],
  }
);

// Language Schema
export const languageSchema = z.object({
  id: z.string(),
  name: z.string().min(1, 'Language name is required').max(50, 'Language name must be less than 50 characters'),
  proficiency: z.enum(['native', 'fluent', 'conversational', 'basic'], {
    message: 'Please select a valid proficiency level',
  }),
  certification: z.string().max(100, 'Certification must be less than 100 characters').optional(),
  reading: z.enum(['native', 'fluent', 'conversational', 'basic'], {
    message: 'Please select a valid reading proficiency',
  }),
  writing: z.enum(['native', 'fluent', 'conversational', 'basic'], {
    message: 'Please select a valid writing proficiency',
  }),
  speaking: z.enum(['native', 'fluent', 'conversational', 'basic'], {
    message: 'Please select a valid speaking proficiency',
  }),
});

// Volunteer Experience Schema
export const volunteerExperienceSchema = z.object({
  id: z.string(),
  organization: z.string().min(1, 'Organization name is required').max(100, 'Organization name must be less than 100 characters'),
  position: z.string().min(1, 'Position is required').max(100, 'Position must be less than 100 characters'),
  startDate: z.string().min(1, 'Start date is required'),
  endDate: z.string().optional(),
  current: z.boolean(),
  description: z.string().min(10, 'Description must be at least 10 characters').max(1000, 'Description must be less than 1000 characters'),
  achievements: z.array(z.string().min(1, 'Achievement cannot be empty')).max(10, 'Maximum 10 achievements allowed'),
  cause: z.string().min(1, 'Cause is required').max(50, 'Cause must be less than 50 characters'),
  hoursPerWeek: z.number().min(1, 'Hours per week must be at least 1').max(80, 'Hours per week must be less than 80').optional(),
  location: z.string().min(1, 'Location is required').max(100, 'Location must be less than 100 characters'),
}).refine(
  (data) => !data.current || data.endDate === '',
  {
    message: 'End date must be empty for current position',
    path: ['endDate'],
  }
).refine(
  (data) => data.current || !data.endDate || new Date(data.endDate) > new Date(data.startDate),
  {
    message: 'End date must be after start date',
    path: ['endDate'],
  }
);

// Award Schema
export const awardSchema = z.object({
  id: z.string(),
  name: z.string().min(1, 'Award name is required').max(100, 'Award name must be less than 100 characters'),
  issuer: z.string().min(1, 'Issuer is required').max(100, 'Issuer must be less than 100 characters'),
  date: z.string().min(1, 'Date is required'),
  description: z.string().max(500, 'Description must be less than 500 characters').optional(),
  category: z.string().min(1, 'Category is required').max(50, 'Category must be less than 50 characters'),
  level: z.enum(['local', 'regional', 'national', 'international'], {
    message: 'Please select a valid award level',
  }),
});

// Publication Schema
export const publicationSchema = z.object({
  id: z.string(),
  title: z.string().min(1, 'Publication title is required').max(200, 'Title must be less than 200 characters'),
  authors: z.array(z.string().min(1, 'Author name cannot be empty')).min(1, 'At least one author is required').max(10, 'Maximum 10 authors allowed'),
  journal: z.string().min(1, 'Journal/conference name is required').max(100, 'Journal name must be less than 100 characters'),
  date: z.string().min(1, 'Publication date is required'),
  doi: z.string().regex(/^10\.\d{4,9}\/[-._;()/:A-Z0-9]+$/i, 'Invalid DOI format').optional().or(z.literal('')),
  url: z.string().url('Invalid publication URL').optional().or(z.literal('')),
  description: z.string().max(1000, 'Description must be less than 1000 characters').optional(),
  type: z.enum(['journal', 'conference', 'book', 'thesis', 'report'], {
    message: 'Please select a valid publication type',
  }),
});

// Reference Schema
export const referenceSchema = z.object({
  id: z.string(),
  name: z.string().min(1, 'Reference name is required').max(100, 'Name must be less than 100 characters'),
  position: z.string().min(1, 'Position is required').max(100, 'Position must be less than 100 characters'),
  company: z.string().min(1, 'Company name is required').max(100, 'Company name must be less than 100 characters'),
  email: z.string().email('Invalid email address').max(100, 'Email must be less than 100 characters'),
  phone: z.string().regex(/^[+]?[\d\s\-()]+$/, 'Invalid phone number format').optional(),
  relationship: z.string().min(1, 'Relationship is required').max(50, 'Relationship must be less than 50 characters'),
  description: z.string().max(500, 'Description must be less than 500 characters').optional(),
  contactPreference: z.enum(['email', 'phone', 'both'], {
    message: 'Please select a valid contact preference',
  }),
});

// Custom Section Schema
export const customSectionSchema = z.object({
  id: z.string(),
  title: z.string().min(1, 'Section title is required').max(100, 'Title must be less than 100 characters'),
  content: z.string().min(1, 'Content is required').max(5000, 'Content must be less than 5000 characters'),
  order: z.number().min(0, 'Order must be at least 0'),
  isVisible: z.boolean(),
  type: z.enum(['text', 'list', 'timeline', 'table'], {
    message: 'Please select a valid section type',
  }),
});

// Complete CV Data Schema
export const cvDataSchema = z.object({
  personalInfo: personalInfoSchema,
  professionalSummary: z.string().max(1000, 'Professional summary must be less than 1000 characters'),
  workExperience: z.array(workExperienceSchema),
  education: z.array(educationSchema),
  skills: z.array(skillSchema),
  projects: z.array(projectSchema),
  certifications: z.array(certificationSchema),
  languages: z.array(languageSchema),
  volunteerExperience: z.array(volunteerExperienceSchema),
  awards: z.array(awardSchema),
  publications: z.array(publicationSchema),
  references: z.array(referenceSchema),
  customSections: z.array(customSectionSchema),
}).refine(
  (data) => data.references.length <= 5,
  {
    message: 'Maximum 5 references allowed',
    path: ['references'],
  }
).refine(
  (data) => data.customSections.length <= 10,
  {
    message: 'Maximum 10 custom sections allowed',
    path: ['customSections'],
  }
);

// Step-specific schemas for validation
export const cvStepSchemas = {
  personal: personalInfoSchema,
  summary: professionalSummarySchema,
  experience: z.object({ workExperience: z.array(workExperienceSchema) }),
  education: z.object({ education: z.array(educationSchema) }),
  skills: z.object({ skills: z.array(skillSchema) }),
  projects: z.object({ projects: z.array(projectSchema) }),
  certifications: z.object({ certifications: z.array(certificationSchema) }),
  languages: z.object({ languages: z.array(languageSchema) }),
  volunteer: z.object({ volunteerExperience: z.array(volunteerExperienceSchema) }),
  awards: z.object({ awards: z.array(awardSchema) }),
  publications: z.object({ publications: z.array(publicationSchema) }),
  references: z.object({ references: z.array(referenceSchema) }),
  custom: z.object({ customSections: z.array(customSectionSchema) }),
};

// Type exports
export type PersonalInfoFormData = z.infer<typeof personalInfoSchema>;
export type ProfessionalSummaryFormData = z.infer<typeof professionalSummarySchema>;
export type WorkExperienceFormData = z.infer<typeof workExperienceSchema>;
export type EducationFormData = z.infer<typeof educationSchema>;
export type SkillFormData = z.infer<typeof skillSchema>;
export type ProjectFormData = z.infer<typeof projectSchema>;
export type CertificationFormData = z.infer<typeof certificationSchema>;
export type LanguageFormData = z.infer<typeof languageSchema>;
export type VolunteerExperienceFormData = z.infer<typeof volunteerExperienceSchema>;
export type AwardFormData = z.infer<typeof awardSchema>;
export type PublicationFormData = z.infer<typeof publicationSchema>;
export type ReferenceFormData = z.infer<typeof referenceSchema>;
export type CustomSectionFormData = z.infer<typeof customSectionSchema>;
export type CVDataFormData = z.infer<typeof cvDataSchema>;