import { DocumentType, TemplateCategory } from './common';

export interface PersonalInfo {
  fullName: string;
  email: string;
  phone: string;
  address: string;
  linkedin?: string;
  website?: string;
  github?: string;
  portfolio?: string;
  twitter?: string;
  facebook?: string;
  instagram?: string;
  profileImage?: string;
  headline?: string;
  summary?: string;
}

export interface WorkExperience {
  id: string;
  company: string;
  position: string;
  startDate: string;
  endDate: string;
  current: boolean;
  description: string;
  achievements: string[];
  skills: string[];
  location: string;
  employmentType: 'full-time' | 'part-time' | 'contract' | 'internship' | 'freelance';
  industry: string;
  website?: string;
  projects?: Project[];
}

export interface Education {
  id: string;
  institution: string;
  degree: string;
  field: string;
  startDate: string;
  endDate: string;
  gpa?: string;
  honors?: string;
  activities: string[];
  achievements: string[];
  description?: string;
  coursework?: string[];
  location: string;
  website?: string;
}

export interface Skill {
  id: string;
  name: string;
  category: 'technical' | 'soft' | 'language' | 'tool' | 'framework' | 'database' | 'certification';
  level: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  yearsOfExperience?: number;
  description?: string;
  certifications?: string[];
}

export interface Project {
  id: string;
  title: string;
  description: string;
  technologies: string[];
  startDate: string;
  endDate?: string;
  url?: string;
  github?: string;
  demo?: string;
  achievements: string[];
  role: string;
  teamSize?: number;
  highlights: string[];
  images?: string[];
}

export interface Certification {
  id: string;
  name: string;
  issuer: string;
  issueDate: string;
  expiryDate?: string;
  credentialId?: string;
  url?: string;
  description?: string;
  skills: string[];
  level: 'basic' | 'intermediate' | 'advanced' | 'expert';
}

export interface Language {
  id: string;
  name: string;
  proficiency: 'native' | 'fluent' | 'conversational' | 'basic';
  certification?: string;
  reading: 'native' | 'fluent' | 'conversational' | 'basic';
  writing: 'native' | 'fluent' | 'conversational' | 'basic';
  speaking: 'native' | 'fluent' | 'conversational' | 'basic';
}

export interface VolunteerExperience {
  id: string;
  organization: string;
  position: string;
  startDate: string;
  endDate?: string;
  current: boolean;
  description: string;
  achievements: string[];
  cause: string;
  hoursPerWeek?: number;
  location: string;
}

export interface Award {
  id: string;
  name: string;
  issuer: string;
  date: string;
  description?: string;
  category: string;
  level: 'local' | 'regional' | 'national' | 'international';
}

export interface Publication {
  id: string;
  title: string;
  authors: string[];
  journal: string;
  date: string;
  doi?: string;
  url?: string;
  description?: string;
  type: 'journal' | 'conference' | 'book' | 'thesis' | 'report';
}

export interface Reference {
  id: string;
  name: string;
  position: string;
  company: string;
  email: string;
  phone: string;
  relationship: string;
  description?: string;
  contactPreference: 'email' | 'phone' | 'both';
}

export interface CustomSection {
  id: string;
  title: string;
  content: string;
  order: number;
  isVisible: boolean;
  type: 'text' | 'list' | 'timeline' | 'table';
}

export interface CVData {
  id: string;
  documentType: DocumentType;
  templateCategory: TemplateCategory;
  personalInfo: PersonalInfo;
  professionalSummary: string;
  workExperience: WorkExperience[];
  education: Education[];
  skills: Skill[];
  projects: Project[];
  certifications: Certification[];
  languages: Language[];
  volunteerExperience: VolunteerExperience[];
  awards: Award[];
  publications: Publication[];
  references: Reference[];
  customSections: CustomSection[];
  createdAt: string;
  updatedAt: string;
  isPublic: boolean;
  viewCount: number;
  downloadCount: number;
  settings: {
    showContact: boolean;
    showProfile: boolean;
    showSummary: boolean;
    template: string;
    language: string;
    currency: string;
  };
}

export type TemplateType = 'modern' | 'traditional' | 'minimal' | 'creative' | 'professional' | 'executive';
export type FormStep = 'personal' | 'summary' | 'experience' | 'education' | 'skills' | 'projects' | 'certifications' | 'languages' | 'volunteer' | 'awards' | 'publications' | 'references' | 'custom' | 'preview';

export interface CVTemplate {
  id: TemplateType;
  name: string;
  description: string;
  preview: string;
  category: 'professional' | 'creative' | 'minimal';
  sections: string[];
  isPremium: boolean;
  features: string[];
  colors: {
    primary: string;
    secondary: string;
    accent: string;
  };
  fonts: {
    heading: string;
    body: string;
  };
  layout: 'single-column' | 'two-column' | 'three-column';
}