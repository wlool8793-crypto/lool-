
import React, { createContext, useContext, useReducer, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { CVData, TemplateType, FormStep } from '../types/cv';
import type { MarriageBiodata, MarriageFormStep, MarriageTemplateType } from '../types/marriage';
import type { DocumentType, ValidationError } from '../types/common';

interface CVState {
  documentType: DocumentType;
  cvData: CVData;
  marriageData: MarriageBiodata;
  currentStep: FormStep | MarriageFormStep;
  selectedTemplate: TemplateType | MarriageTemplateType;
  isSaved: boolean;
  isLoading: boolean;
  formProgress: {
    cv: Record<FormStep, number>;
    marriage: Record<MarriageFormStep, number>;
  };
  userSession: {
    userId: string;
    role: 'owner' | 'editor' | 'viewer';
    permissions: string[];
    lastActivity: string;
  };
  analytics: {
    timeSpent: Record<string, number>;
    formErrors: Array<{
      field: string;
      message: string;
      timestamp: string;
    }>;
    completionRate: number;
    abandonedSections: string[];
  };
  settings: {
    template: TemplateType | MarriageTemplateType;
    autoSave: boolean;
    validationMode: 'onBlur' | 'onChange' | 'onSubmit';
    language: string;
    theme: 'light' | 'dark' | 'auto';
  };
}

type CVAction =
  // CV Actions
  | { type: 'UPDATE_PERSONAL_INFO'; payload: Partial<CVData['personalInfo']> }
  | { type: 'UPDATE_PROFESSIONAL_SUMMARY'; payload: string }
  | { type: 'ADD_WORK_EXPERIENCE'; payload: CVData['workExperience'][0] }
  | { type: 'UPDATE_WORK_EXPERIENCE'; payload: { id: string; data: Partial<CVData['workExperience'][0]> } }
  | { type: 'DELETE_WORK_EXPERIENCE'; payload: string }
  | { type: 'ADD_EDUCATION'; payload: CVData['education'][0] }
  | { type: 'UPDATE_EDUCATION'; payload: { id: string; data: Partial<CVData['education'][0]> } }
  | { type: 'DELETE_EDUCATION'; payload: string }
  | { type: 'ADD_SKILL'; payload: CVData['skills'][0] }
  | { type: 'UPDATE_SKILL'; payload: { id: string; data: Partial<CVData['skills'][0]> } }
  | { type: 'DELETE_SKILL'; payload: string }
  | { type: 'ADD_PROJECT'; payload: CVData['projects'][0] }
  | { type: 'UPDATE_PROJECT'; payload: { id: string; data: Partial<CVData['projects'][0]> } }
  | { type: 'DELETE_PROJECT'; payload: string }
  | { type: 'ADD_CERTIFICATION'; payload: CVData['certifications'][0] }
  | { type: 'UPDATE_CERTIFICATION'; payload: { id: string; data: Partial<CVData['certifications'][0]> } }
  | { type: 'DELETE_CERTIFICATION'; payload: string }
  | { type: 'ADD_LANGUAGE'; payload: CVData['languages'][0] }
  | { type: 'UPDATE_LANGUAGE'; payload: { id: string; data: Partial<CVData['languages'][0]> } }
  | { type: 'DELETE_LANGUAGE'; payload: string }
  | { type: 'ADD_VOLUNTEER_EXPERIENCE'; payload: CVData['volunteerExperience'][0] }
  | { type: 'UPDATE_VOLUNTEER_EXPERIENCE'; payload: { id: string; data: Partial<CVData['volunteerExperience'][0]> } }
  | { type: 'DELETE_VOLUNTEER_EXPERIENCE'; payload: string }
  | { type: 'ADD_AWARD'; payload: CVData['awards'][0] }
  | { type: 'UPDATE_AWARD'; payload: { id: string; data: Partial<CVData['awards'][0]> } }
  | { type: 'DELETE_AWARD'; payload: string }
  | { type: 'ADD_PUBLICATION'; payload: CVData['publications'][0] }
  | { type: 'UPDATE_PUBLICATION'; payload: { id: string; data: Partial<CVData['publications'][0]> } }
  | { type: 'DELETE_PUBLICATION'; payload: string }
  | { type: 'ADD_REFERENCE'; payload: CVData['references'][0] }
  | { type: 'UPDATE_REFERENCE'; payload: { id: string; data: Partial<CVData['references'][0]> } }
  | { type: 'DELETE_REFERENCE'; payload: string }
  | { type: 'ADD_CUSTOM_SECTION'; payload: CVData['customSections'][0] }
  | { type: 'UPDATE_CUSTOM_SECTION'; payload: { id: string; data: Partial<CVData['customSections'][0]> } }
  | { type: 'DELETE_CUSTOM_SECTION'; payload: string }

  // Marriage Biodata Actions
  | { type: 'UPDATE_MARRIAGE_PERSONAL_INFO'; payload: Partial<MarriageBiodata['personalInfo']> }
  | { type: 'UPDATE_MARRIAGE_CONTACT_INFO'; payload: Partial<MarriageBiodata['contactInfo']> }
  | { type: 'UPDATE_MARRIAGE_FAMILY_INFO'; payload: Partial<MarriageBiodata['familyInfo']> }
  | { type: 'ADD_MARRIAGE_EDUCATION'; payload: MarriageBiodata['education'][0] }
  | { type: 'UPDATE_MARRIAGE_EDUCATION'; payload: { id: string; data: Partial<MarriageBiodata['education'][0]> } }
  | { type: 'DELETE_MARRIAGE_EDUCATION'; payload: string }
  | { type: 'ADD_MARRIAGE_OCCUPATION'; payload: MarriageBiodata['occupation'][0] }
  | { type: 'UPDATE_MARRIAGE_OCCUPATION'; payload: { id: string; data: Partial<MarriageBiodata['occupation'][0]> } }
  | { type: 'DELETE_MARRIAGE_OCCUPATION'; payload: string }
  | { type: 'UPDATE_MARRIAGE_LIFESTYLE'; payload: Partial<MarriageBiodata['lifestyle']> }
  | { type: 'UPDATE_MARRIAGE_PARTNER_PREFERENCE'; payload: Partial<MarriageBiodata['partnerPreference']> }
  | { type: 'UPDATE_MARRIAGE_HOROSCOPE'; payload: Partial<MarriageBiodata['horoscope']> }
  | { type: 'UPDATE_MARRIAGE_PHOTOS'; payload: Partial<MarriageBiodata['photos']> }
  | { type: 'ADD_MARRIAGE_REFERENCE'; payload: MarriageBiodata['references'][0] }
  | { type: 'UPDATE_MARRIAGE_REFERENCE'; payload: { id: string; data: Partial<MarriageBiodata['references'][0]> } }
  | { type: 'DELETE_MARRIAGE_REFERENCE'; payload: string }
  | { type: 'UPDATE_MARRIAGE_DATA'; payload: Partial<MarriageBiodata> }
  | { type: 'UPDATE_MARRIAGE_ABOUT'; payload: string }
  | { type: 'UPDATE_MARRIAGE_EXPECTATIONS'; payload: string }

  // Common Actions
  | { type: 'SET_DOCUMENT_TYPE'; payload: DocumentType }
  | { type: 'SET_CURRENT_STEP'; payload: FormStep | MarriageFormStep }
  | { type: 'NEXT_STEP' }
  | { type: 'PREVIOUS_STEP' }
  | { type: 'SET_TEMPLATE'; payload: TemplateType | MarriageTemplateType }
  | { type: 'UPDATE_SETTINGS'; payload: Partial<CVState['settings']> }
  | { type: 'UPDATE_FORM_PROGRESS'; payload: { documentType: DocumentType; step: string; progress: number } }
  | { type: 'ADD_ANALYTICS_ERROR'; payload: { field: string; message: string } }
  | { type: 'UPDATE_TIME_SPENT'; payload: { section: string; time: number } }
  | { type: 'UPDATE_USER_SESSION'; payload: Partial<CVState['userSession']> }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'LOAD_CV_DATA'; payload: CVData }
  | { type: 'LOAD_MARRIAGE_DATA'; payload: MarriageBiodata }
  | { type: 'RESET_FORM' }
  | { type: 'MARK_AS_SAVED' };

const createDefaultCVData = (): CVData => ({
  id: '',
  documentType: 'cv',
  templateCategory: 'professional',
  personalInfo: {
    fullName: '',
    email: '',
    phone: '',
    address: '',
    linkedin: '',
    website: '',
    github: '',
  },
  professionalSummary: '',
  workExperience: [],
  education: [],
  skills: [],
  projects: [],
  certifications: [],
  languages: [],
  volunteerExperience: [],
  awards: [],
  publications: [],
  references: [],
  customSections: [],
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
  isPublic: false,
  viewCount: 0,
  downloadCount: 0,
  settings: {
    showContact: true,
    showProfile: true,
    showSummary: true,
    template: 'modern',
    language: 'en',
    currency: 'USD',
  },
});

const createDefaultMarriageData = (): MarriageBiodata => ({
  id: '',
  documentType: 'marriage',
  templateCategory: 'marriage',
  personalInfo: {
    fullName: '',
    age: 0,
    gender: 'male',
    dateOfBirth: '',
    birthPlace: '',
    height: '',
    weight: '',
    bloodGroup: '',
    complexion: 'fair',
    bodyType: 'average',
    maritalStatus: 'never_married',
    nationality: '',
    religion: '',
    motherTongue: '',
    languages: [],
  },
  contactInfo: {
    email: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    country: '',
    pinCode: '',
    residenceType: 'own',
  },
  familyInfo: {
    familyType: 'nuclear',
    familyStatus: 'middle_class',
    familyValues: 'moderate',
    fatherName: '',
    fatherOccupation: '',
    fatherStatus: 'alive',
    motherName: '',
    motherOccupation: '',
    motherStatus: 'alive',
    brothers: 0,
    marriedBrothers: 0,
    sisters: 0,
    marriedSisters: 0,
    familyLocation: '',
    familyOrigin: '',
  },
  education: [],
  occupation: [],
  lifestyle: {
    diet: 'vegetarian',
    smoking: 'never',
    drinking: 'never',
    hobbies: [],
    interests: [],
    sports: [],
    music: [],
    movies: [],
    books: [],
    travel: [],
    cuisine: [],
    dressStyle: 'modern',
  },
  partnerPreference: {
    ageRange: { min: 18, max: 35 },
    heightRange: { min: '5\'0"', max: '6\'0"' },
    maritalStatus: ['never_married'],
    religion: [],
    education: [],
    occupation: [],
    location: [],
    motherTongue: [],
    diet: 'vegetarian',
    smoking: 'never',
    drinking: 'never',
    additionalPreferences: '',
  },
  horoscope: {
    hasHoroscope: false,
    manglik: 'unknown',
  },
  photos: {
    profile: '',
    additional: [],
  },
  references: [],
  aboutMe: '',
  expectations: '',
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
  isPublished: false,
  viewCount: 0,
  settings: {
    showContact: true,
    showFamilyDetails: true,
    showIncome: true,
    showPhotos: true,
    allowMessages: true,
  },
});

const createDefaultFormProgress = () => ({
  cv: {
    personal: 0,
    summary: 0,
    experience: 0,
    education: 0,
    skills: 0,
    projects: 0,
    certifications: 0,
    languages: 0,
    volunteer: 0,
    awards: 0,
    publications: 0,
    references: 0,
    custom: 0,
    preview: 0,
  },
  marriage: {
    personal: 0,
    contact: 0,
    family: 0,
    education: 0,
    occupation: 0,
    lifestyle: 0,
    'partner-preference': 0,
    horoscope: 0,
    photos: 0,
    about: 0,
    preview: 0,
  },
});

const initialState: CVState = {
  documentType: 'cv',
  cvData: createDefaultCVData(),
  marriageData: createDefaultMarriageData(),
  currentStep: 'personal',
  selectedTemplate: 'modern',
  isSaved: true,
  isLoading: false,
  formProgress: createDefaultFormProgress(),
  userSession: {
    userId: 'default-user',
    role: 'owner',
    permissions: ['read', 'write', 'delete'],
    lastActivity: new Date().toISOString(),
  },
  analytics: {
    timeSpent: {},
    formErrors: [],
    completionRate: 0,
    abandonedSections: [],
  },
  settings: {
    template: 'modern',
    autoSave: true,
    validationMode: 'onBlur',
    language: 'en',
    theme: 'light',
  },
};

const cvReducer = (state: CVState, action: CVAction): CVState => {
  switch (action.type) {
    // Common Actions
    case 'SET_DOCUMENT_TYPE':
      return {
        ...state,
        documentType: action.payload,
        currentStep: action.payload === 'cv' ? 'personal' : 'personal',
        selectedTemplate: action.payload === 'cv' ? 'modern' : 'traditional',
      };

    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };

    case 'SET_CURRENT_STEP':
      return { ...state, currentStep: action.payload };

    case 'NEXT_STEP': {
      const cvSteps: FormStep[] = ['personal', 'summary', 'experience', 'education', 'skills', 'projects', 'certifications', 'languages', 'preview'];
      const marriageSteps: MarriageFormStep[] = ['personal', 'contact', 'family', 'education', 'occupation', 'lifestyle', 'partner-preference', 'horoscope', 'photos', 'about', 'preview'];

      if (state.documentType === 'cv') {
        const currentIndex = cvSteps.indexOf(state.currentStep as FormStep);
        if (currentIndex < cvSteps.length - 1) {
          return { ...state, currentStep: cvSteps[currentIndex + 1] };
        }
      } else {
        const currentIndex = marriageSteps.indexOf(state.currentStep as MarriageFormStep);
        if (currentIndex < marriageSteps.length - 1) {
          return { ...state, currentStep: marriageSteps[currentIndex + 1] };
        }
      }
      return state;
    }

    case 'PREVIOUS_STEP': {
      const cvSteps: FormStep[] = ['personal', 'summary', 'experience', 'education', 'skills', 'projects', 'certifications', 'languages', 'preview'];
      const marriageSteps: MarriageFormStep[] = ['personal', 'contact', 'family', 'education', 'occupation', 'lifestyle', 'partner-preference', 'horoscope', 'photos', 'about', 'preview'];

      if (state.documentType === 'cv') {
        const currentIndex = cvSteps.indexOf(state.currentStep as FormStep);
        if (currentIndex > 0) {
          return { ...state, currentStep: cvSteps[currentIndex - 1] };
        }
      } else {
        const currentIndex = marriageSteps.indexOf(state.currentStep as MarriageFormStep);
        if (currentIndex > 0) {
          return { ...state, currentStep: marriageSteps[currentIndex - 1] };
        }
      }
      return state;
    }

    case 'SET_TEMPLATE':
      return {
        ...state,
        selectedTemplate: action.payload,
        settings: { ...state.settings, template: action.payload },
        isSaved: false,
      };

    case 'UPDATE_SETTINGS':
      return {
        ...state,
        settings: { ...state.settings, ...action.payload },
        isSaved: false,
      };

    case 'UPDATE_FORM_PROGRESS':
      return {
        ...state,
        formProgress: {
          ...state.formProgress,
          [action.payload.documentType]: {
            ...state.formProgress[action.payload.documentType],
            [action.payload.step]: action.payload.progress,
          },
        },
      };

    case 'ADD_ANALYTICS_ERROR':
      return {
        ...state,
        analytics: {
          ...state.analytics,
          formErrors: [
            ...state.analytics.formErrors,
            {
              field: action.payload.field,
              message: action.payload.message,
              timestamp: new Date().toISOString(),
            },
          ],
        },
      };

    case 'UPDATE_TIME_SPENT':
      return {
        ...state,
        analytics: {
          ...state.analytics,
          timeSpent: {
            ...state.analytics.timeSpent,
            [action.payload.section]:
              (state.analytics.timeSpent[action.payload.section] || 0) + action.payload.time,
          },
        },
      };

    case 'UPDATE_USER_SESSION':
      return {
        ...state,
        userSession: {
          ...state.userSession,
          ...action.payload,
          lastActivity: new Date().toISOString(),
        },
      };

    // CV Actions
    case 'UPDATE_PERSONAL_INFO':
      return {
        ...state,
        cvData: {
          ...state.cvData,
          personalInfo: { ...state.cvData.personalInfo, ...action.payload },
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'UPDATE_PROFESSIONAL_SUMMARY':
      return {
        ...state,
        cvData: {
          ...state.cvData,
          professionalSummary: action.payload,
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'ADD_WORK_EXPERIENCE':
      return {
        ...state,
        cvData: {
          ...state.cvData,
          workExperience: [...state.cvData.workExperience, action.payload],
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'UPDATE_WORK_EXPERIENCE':
      return {
        ...state,
        cvData: {
          ...state.cvData,
          workExperience: state.cvData.workExperience.map((exp) =>
            exp.id === action.payload.id ? { ...exp, ...action.payload.data } : exp
          ),
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'DELETE_WORK_EXPERIENCE':
      return {
        ...state,
        cvData: {
          ...state.cvData,
          workExperience: state.cvData.workExperience.filter((exp) => exp.id !== action.payload),
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'ADD_EDUCATION':
      return {
        ...state,
        cvData: {
          ...state.cvData,
          education: [...state.cvData.education, action.payload],
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'UPDATE_EDUCATION':
      return {
        ...state,
        cvData: {
          ...state.cvData,
          education: state.cvData.education.map((edu) =>
            edu.id === action.payload.id ? { ...edu, ...action.payload.data } : edu
          ),
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'DELETE_EDUCATION':
      return {
        ...state,
        cvData: {
          ...state.cvData,
          education: state.cvData.education.filter((edu) => edu.id !== action.payload),
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'ADD_SKILL':
      return {
        ...state,
        cvData: {
          ...state.cvData,
          skills: [...state.cvData.skills, action.payload],
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'UPDATE_SKILL':
      return {
        ...state,
        cvData: {
          ...state.cvData,
          skills: state.cvData.skills.map((skill) =>
            skill.id === action.payload.id ? { ...skill, ...action.payload.data } : skill
          ),
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'DELETE_SKILL':
      return {
        ...state,
        cvData: {
          ...state.cvData,
          skills: state.cvData.skills.filter((skill) => skill.id !== action.payload),
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    // Additional CV actions (Volunteer, Awards, Publications, References, Custom)
    case 'ADD_VOLUNTEER_EXPERIENCE':
      return {
        ...state,
        cvData: {
          ...state.cvData,
          volunteerExperience: [...state.cvData.volunteerExperience, action.payload],
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'UPDATE_VOLUNTEER_EXPERIENCE':
      return {
        ...state,
        cvData: {
          ...state.cvData,
          volunteerExperience: state.cvData.volunteerExperience.map((exp) =>
            exp.id === action.payload.id ? { ...exp, ...action.payload.data } : exp
          ),
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'DELETE_VOLUNTEER_EXPERIENCE':
      return {
        ...state,
        cvData: {
          ...state.cvData,
          volunteerExperience: state.cvData.volunteerExperience.filter((exp) => exp.id !== action.payload),
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'ADD_AWARD':
      return {
        ...state,
        cvData: {
          ...state.cvData,
          awards: [...state.cvData.awards, action.payload],
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'UPDATE_AWARD':
      return {
        ...state,
        cvData: {
          ...state.cvData,
          awards: state.cvData.awards.map((award) =>
            award.id === action.payload.id ? { ...award, ...action.payload.data } : award
          ),
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'DELETE_AWARD':
      return {
        ...state,
        cvData: {
          ...state.cvData,
          awards: state.cvData.awards.filter((award) => award.id !== action.payload),
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'ADD_PUBLICATION':
      return {
        ...state,
        cvData: {
          ...state.cvData,
          publications: [...state.cvData.publications, action.payload],
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'UPDATE_PUBLICATION':
      return {
        ...state,
        cvData: {
          ...state.cvData,
          publications: state.cvData.publications.map((pub) =>
            pub.id === action.payload.id ? { ...pub, ...action.payload.data } : pub
          ),
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'DELETE_PUBLICATION':
      return {
        ...state,
        cvData: {
          ...state.cvData,
          publications: state.cvData.publications.filter((pub) => pub.id !== action.payload),
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'ADD_REFERENCE':
      return {
        ...state,
        cvData: {
          ...state.cvData,
          references: [...state.cvData.references, action.payload],
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'UPDATE_REFERENCE':
      return {
        ...state,
        cvData: {
          ...state.cvData,
          references: state.cvData.references.map((ref) =>
            ref.id === action.payload.id ? { ...ref, ...action.payload.data } : ref
          ),
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'DELETE_REFERENCE':
      return {
        ...state,
        cvData: {
          ...state.cvData,
          references: state.cvData.references.filter((ref) => ref.id !== action.payload),
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'ADD_CUSTOM_SECTION':
      return {
        ...state,
        cvData: {
          ...state.cvData,
          customSections: [...state.cvData.customSections, action.payload],
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'UPDATE_CUSTOM_SECTION':
      return {
        ...state,
        cvData: {
          ...state.cvData,
          customSections: state.cvData.customSections.map((section) =>
            section.id === action.payload.id ? { ...section, ...action.payload.data } : section
          ),
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'DELETE_CUSTOM_SECTION':
      return {
        ...state,
        cvData: {
          ...state.cvData,
          customSections: state.cvData.customSections.filter((section) => section.id !== action.payload),
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    // Marriage Biodata Actions
    case 'UPDATE_MARRIAGE_PERSONAL_INFO':
      return {
        ...state,
        marriageData: {
          ...state.marriageData,
          personalInfo: { ...state.marriageData.personalInfo, ...action.payload },
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'UPDATE_MARRIAGE_CONTACT_INFO':
      return {
        ...state,
        marriageData: {
          ...state.marriageData,
          contactInfo: { ...state.marriageData.contactInfo, ...action.payload },
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'UPDATE_MARRIAGE_FAMILY_INFO':
      return {
        ...state,
        marriageData: {
          ...state.marriageData,
          familyInfo: { ...state.marriageData.familyInfo, ...action.payload },
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'ADD_MARRIAGE_EDUCATION':
      return {
        ...state,
        marriageData: {
          ...state.marriageData,
          education: [...state.marriageData.education, action.payload],
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'UPDATE_MARRIAGE_EDUCATION':
      return {
        ...state,
        marriageData: {
          ...state.marriageData,
          education: state.marriageData.education.map((edu) =>
            edu.id === action.payload.id ? { ...edu, ...action.payload.data } : edu
          ),
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'DELETE_MARRIAGE_EDUCATION':
      return {
        ...state,
        marriageData: {
          ...state.marriageData,
          education: state.marriageData.education.filter((edu) => edu.id !== action.payload),
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'ADD_MARRIAGE_OCCUPATION':
      return {
        ...state,
        marriageData: {
          ...state.marriageData,
          occupation: [...state.marriageData.occupation, action.payload],
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'UPDATE_MARRIAGE_OCCUPATION':
      return {
        ...state,
        marriageData: {
          ...state.marriageData,
          occupation: state.marriageData.occupation.map((occ) =>
            occ.id === action.payload.id ? { ...occ, ...action.payload.data } : occ
          ),
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'DELETE_MARRIAGE_OCCUPATION':
      return {
        ...state,
        marriageData: {
          ...state.marriageData,
          occupation: state.marriageData.occupation.filter((occ) => occ.id !== action.payload),
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'UPDATE_MARRIAGE_LIFESTYLE':
      return {
        ...state,
        marriageData: {
          ...state.marriageData,
          lifestyle: { ...state.marriageData.lifestyle, ...action.payload },
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'UPDATE_MARRIAGE_PARTNER_PREFERENCE':
      return {
        ...state,
        marriageData: {
          ...state.marriageData,
          partnerPreference: { ...state.marriageData.partnerPreference, ...action.payload },
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'UPDATE_MARRIAGE_HOROSCOPE':
      return {
        ...state,
        marriageData: {
          ...state.marriageData,
          horoscope: { ...state.marriageData.horoscope, ...action.payload },
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'UPDATE_MARRIAGE_PHOTOS':
      return {
        ...state,
        marriageData: {
          ...state.marriageData,
          photos: { ...state.marriageData.photos, ...action.payload },
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'ADD_MARRIAGE_REFERENCE':
      return {
        ...state,
        marriageData: {
          ...state.marriageData,
          references: [...state.marriageData.references, action.payload],
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'UPDATE_MARRIAGE_REFERENCE':
      return {
        ...state,
        marriageData: {
          ...state.marriageData,
          references: state.marriageData.references.map((ref) =>
            ref.id === action.payload.id ? { ...ref, ...action.payload.data } : ref
          ),
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'DELETE_MARRIAGE_REFERENCE':
      return {
        ...state,
        marriageData: {
          ...state.marriageData,
          references: state.marriageData.references.filter((ref) => ref.id !== action.payload),
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'UPDATE_MARRIAGE_DATA':
      return {
        ...state,
        marriageData: {
          ...state.marriageData,
          ...action.payload,
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'UPDATE_MARRIAGE_ABOUT':
      return {
        ...state,
        marriageData: {
          ...state.marriageData,
          aboutMe: action.payload,
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'UPDATE_MARRIAGE_EXPECTATIONS':
      return {
        ...state,
        marriageData: {
          ...state.marriageData,
          expectations: action.payload,
          updatedAt: new Date().toISOString(),
        },
        isSaved: false,
      };

    case 'LOAD_CV_DATA':
      return {
        ...state,
        cvData: { ...action.payload, updatedAt: new Date().toISOString() },
        isSaved: true,
        documentType: 'cv',
      };

    case 'LOAD_MARRIAGE_DATA':
      return {
        ...state,
        marriageData: { ...action.payload, updatedAt: new Date().toISOString() },
        isSaved: true,
        documentType: 'marriage',
      };

    case 'RESET_FORM':
      return {
        ...initialState,
        documentType: state.documentType,
        userSession: state.userSession,
      };

    case 'MARK_AS_SAVED':
      return { ...state, isSaved: true };

    default:
      return state;
  }
};

interface CVContextType {
  state: CVState;
  dispatch: React.Dispatch<CVAction>;
  saveToLocalStorage: () => void;
  loadFromLocalStorage: () => void;
  generateId: () => string;
  markAsSaved: () => void;

  // Document management
  setDocumentType: (type: DocumentType) => void;
  setLoading: (loading: boolean) => void;

  // Form navigation
  setCurrentStep: (step: FormStep | MarriageFormStep) => void;
  setTemplate: (template: TemplateType | MarriageTemplateType) => void;

  // Progress tracking
  updateFormProgress: (documentType: DocumentType, step: string, progress: number) => void;
  calculateCompletionRate: () => number;

  // Analytics
  addAnalyticsError: (field: string, message: string) => void;
  updateTimeSpent: (section: string, time: number) => void;
  trackSectionAbandonment: (section: string) => void;

  // User session
  updateUserSession: (session: Partial<CVState['userSession']>) => void;
  hasPermission: (permission: string) => boolean;

  // CV specific actions
  updatePersonalInfo: (data: Partial<CVData['personalInfo']>) => void;
  updateProfessionalSummary: (summary: string) => void;
  addWorkExperience: (experience: CVData['workExperience'][0]) => void;
  updateWorkExperience: (id: string, data: Partial<CVData['workExperience'][0]>) => void;
  deleteWorkExperience: (id: string) => void;
  addEducation: (education: CVData['education'][0]) => void;
  updateEducation: (id: string, data: Partial<CVData['education'][0]>) => void;
  deleteEducation: (id: string) => void;
  addSkill: (skill: CVData['skills'][0]) => void;
  updateSkill: (id: string, data: Partial<CVData['skills'][0]>) => void;
  deleteSkill: (id: string) => void;
  addProject: (project: CVData['projects'][0]) => void;
  updateProject: (id: string, data: Partial<CVData['projects'][0]>) => void;
  deleteProject: (id: string) => void;
  addCertification: (certification: CVData['certifications'][0]) => void;
  updateCertification: (id: string, data: Partial<CVData['certifications'][0]>) => void;
  deleteCertification: (id: string) => void;
  addLanguage: (language: CVData['languages'][0]) => void;
  updateLanguage: (id: string, data: Partial<CVData['languages'][0]>) => void;
  deleteLanguage: (id: string) => void;
  addVolunteerExperience: (experience: CVData['volunteerExperience'][0]) => void;
  updateVolunteerExperience: (id: string, data: Partial<CVData['volunteerExperience'][0]>) => void;
  deleteVolunteerExperience: (id: string) => void;
  addAward: (award: CVData['awards'][0]) => void;
  updateAward: (id: string, data: Partial<CVData['awards'][0]>) => void;
  deleteAward: (id: string) => void;
  addPublication: (publication: CVData['publications'][0]) => void;
  updatePublication: (id: string, data: Partial<CVData['publications'][0]>) => void;
  deletePublication: (id: string) => void;
  addReference: (reference: CVData['references'][0]) => void;
  updateReference: (id: string, data: Partial<CVData['references'][0]>) => void;
  deleteReference: (id: string) => void;
  addCustomSection: (section: CVData['customSections'][0]) => void;
  updateCustomSection: (id: string, data: Partial<CVData['customSections'][0]>) => void;
  deleteCustomSection: (id: string) => void;

  // Marriage biodata specific actions
  updateMarriagePersonalInfo: (data: Partial<MarriageBiodata['personalInfo']>) => void;
  updateMarriageContactInfo: (data: Partial<MarriageBiodata['contactInfo']>) => void;
  updateMarriageFamilyInfo: (data: Partial<MarriageBiodata['familyInfo']>) => void;
  addMarriageEducation: (education: MarriageBiodata['education'][0]) => void;
  updateMarriageEducation: (id: string, data: Partial<MarriageBiodata['education'][0]>) => void;
  deleteMarriageEducation: (id: string) => void;
  addMarriageOccupation: (occupation: MarriageBiodata['occupation'][0]) => void;
  updateMarriageOccupation: (id: string, data: Partial<MarriageBiodata['occupation'][0]>) => void;
  deleteMarriageOccupation: (id: string) => void;
  updateMarriageLifestyle: (data: Partial<MarriageBiodata['lifestyle']>) => void;
  updateMarriagePartnerPreference: (data: Partial<MarriageBiodata['partnerPreference']>) => void;
  updateMarriageHoroscope: (data: Partial<MarriageBiodata['horoscope']>) => void;
  updateMarriagePhotos: (data: Partial<MarriageBiodata['photos']>) => void;
  addMarriageReference: (reference: MarriageBiodata['references'][0]) => void;
  updateMarriageReference: (id: string, data: Partial<MarriageBiodata['references'][0]>) => void;
  deleteMarriageReference: (id: string) => void;
  updateMarriageAbout: (about: string) => void;
  updateMarriageExpectations: (expectations: string) => void;

  // Form utilities
  resetForm: () => void;
  exportData: () => { cv?: CVData; marriage?: MarriageBiodata };
  importData: (data: { cv?: CVData; marriage?: MarriageBiodata }) => void;

  // Validation helpers
  validateCurrentStep: () => boolean;
  getStepErrors: () => ValidationError[];
}

const CVContext = createContext<CVContextType | undefined>(undefined);

export const CVProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(cvReducer, initialState);

  // Local storage management
  const saveToLocalStorage = () => {
    try {
      localStorage.setItem('cvData', JSON.stringify(state.cvData));
      localStorage.setItem('marriageData', JSON.stringify(state.marriageData));
      localStorage.setItem('documentType', state.documentType);
      localStorage.setItem('selectedTemplate', state.selectedTemplate);
      localStorage.setItem('currentStep', state.currentStep);
      localStorage.setItem('formProgress', JSON.stringify(state.formProgress));
      localStorage.setItem('settings', JSON.stringify(state.settings));
      localStorage.setItem('userSession', JSON.stringify(state.userSession));
      localStorage.setItem('analytics', JSON.stringify(state.analytics));
    } catch (error) {
      console.error('Error saving to localStorage:', error);
    }
  };

  const loadFromLocalStorage = () => {
    try {
      const savedCVData = localStorage.getItem('cvData');
      const savedMarriageData = localStorage.getItem('marriageData');
      const savedDocumentType = localStorage.getItem('documentType');
      const savedTemplate = localStorage.getItem('selectedTemplate');
      const savedStep = localStorage.getItem('currentStep');
      const savedProgress = localStorage.getItem('formProgress');
      const savedSettings = localStorage.getItem('settings');
      const savedUserSession = localStorage.getItem('userSession');
      const savedAnalytics = localStorage.getItem('analytics');

      if (savedCVData) {
        const parsedData = JSON.parse(savedCVData);
        dispatch({ type: 'LOAD_CV_DATA', payload: parsedData });
      }

      if (savedMarriageData) {
        const parsedData = JSON.parse(savedMarriageData);
        dispatch({ type: 'LOAD_MARRIAGE_DATA', payload: parsedData });
      }

      if (savedDocumentType) {
        dispatch({ type: 'SET_DOCUMENT_TYPE', payload: savedDocumentType as DocumentType });
      }

      if (savedTemplate) {
        dispatch({ type: 'SET_TEMPLATE', payload: savedTemplate as TemplateType | MarriageTemplateType });
      }

      if (savedStep) {
        dispatch({ type: 'SET_CURRENT_STEP', payload: savedStep as FormStep | MarriageFormStep });
      }

      if (savedProgress) {
        const parsedProgress = JSON.parse(savedProgress);
        // Update form progress individually
        Object.entries(parsedProgress).forEach(([docType, steps]) => {
          Object.entries(steps as Record<string, number>).forEach(([step, progress]) => {
            dispatch({
              type: 'UPDATE_FORM_PROGRESS',
              payload: { documentType: docType as DocumentType, step, progress }
            });
          });
        });
      }

      if (savedSettings) {
        const parsedSettings = JSON.parse(savedSettings);
        dispatch({ type: 'UPDATE_SETTINGS', payload: parsedSettings });
      }

      if (savedUserSession) {
        const parsedSession = JSON.parse(savedUserSession);
        dispatch({ type: 'UPDATE_USER_SESSION', payload: parsedSession });
      }

      if (savedAnalytics) {
        const parsedAnalytics = JSON.parse(savedAnalytics);
        // Update analytics individually
        parsedAnalytics.formErrors?.forEach((error: any) => {
          dispatch({ type: 'ADD_ANALYTICS_ERROR', payload: error });
        });

        Object.entries(parsedAnalytics.timeSpent || {}).forEach(([section, time]) => {
          dispatch({ type: 'UPDATE_TIME_SPENT', payload: { section, time: time as number } });
        });
      }
    } catch (error) {
      console.error('Error loading from localStorage:', error);
    }
  };

  const generateId = () => Date.now().toString(36) + Math.random().toString(36).substr(2);

  const markAsSaved = () => {
    dispatch({ type: 'MARK_AS_SAVED' });
  };

  // Document management
  const setDocumentType = (type: DocumentType) => {
    dispatch({ type: 'SET_DOCUMENT_TYPE', payload: type });
  };

  const setLoading = (loading: boolean) => {
    dispatch({ type: 'SET_LOADING', payload: loading });
  };

  // Form navigation
  const setCurrentStep = (step: FormStep | MarriageFormStep) => {
    dispatch({ type: 'SET_CURRENT_STEP', payload: step });
  };

  const setTemplate = (template: TemplateType | MarriageTemplateType) => {
    dispatch({ type: 'SET_TEMPLATE', payload: template });
  };

  // Progress tracking
  const updateFormProgress = (documentType: DocumentType, step: string, progress: number) => {
    dispatch({ type: 'UPDATE_FORM_PROGRESS', payload: { documentType, step, progress } });
  };

  const calculateCompletionRate = () => {
    const currentProgress = state.formProgress[state.documentType];
    const steps = Object.values(currentProgress);
    const completedSteps = steps.filter(progress => progress === 100);
    return Math.round((completedSteps.length / steps.length) * 100);
  };

  // Analytics
  const addAnalyticsError = (field: string, message: string) => {
    dispatch({ type: 'ADD_ANALYTICS_ERROR', payload: { field, message } });
  };

  const updateTimeSpent = (section: string, time: number) => {
    dispatch({ type: 'UPDATE_TIME_SPENT', payload: { section, time } });
  };

  const trackSectionAbandonment = (section: string) => {
    const currentProgress = state.formProgress[state.documentType][section];
    if (currentProgress > 0 && currentProgress < 100) {
      dispatch({
        type: 'UPDATE_FORM_PROGRESS',
        payload: { documentType: state.documentType, step: section, progress: 0 },
      });
    }
  };

  // User session
  const updateUserSession = (session: Partial<CVState['userSession']>) => {
    dispatch({ type: 'UPDATE_USER_SESSION', payload: session });
  };

  const hasPermission = (permission: string) => {
    return state.userSession.permissions.includes(permission);
  };

  // CV specific actions
  const updatePersonalInfo = (data: Partial<CVData['personalInfo']>) => {
    dispatch({ type: 'UPDATE_PERSONAL_INFO', payload: data });
  };

  const updateProfessionalSummary = (summary: string) => {
    dispatch({ type: 'UPDATE_PROFESSIONAL_SUMMARY', payload: summary });
  };

  const addWorkExperience = (experience: CVData['workExperience'][0]) => {
    dispatch({ type: 'ADD_WORK_EXPERIENCE', payload: experience });
  };

  const updateWorkExperience = (id: string, data: Partial<CVData['workExperience'][0]>) => {
    dispatch({ type: 'UPDATE_WORK_EXPERIENCE', payload: { id, data } });
  };

  const deleteWorkExperience = (id: string) => {
    dispatch({ type: 'DELETE_WORK_EXPERIENCE', payload: id });
  };

  const addEducation = (education: CVData['education'][0]) => {
    dispatch({ type: 'ADD_EDUCATION', payload: education });
  };

  const updateEducation = (id: string, data: Partial<CVData['education'][0]>) => {
    dispatch({ type: 'UPDATE_EDUCATION', payload: { id, data } });
  };

  const deleteEducation = (id: string) => {
    dispatch({ type: 'DELETE_EDUCATION', payload: id });
  };

  const addSkill = (skill: CVData['skills'][0]) => {
    dispatch({ type: 'ADD_SKILL', payload: skill });
  };

  const updateSkill = (id: string, data: Partial<CVData['skills'][0]>) => {
    dispatch({ type: 'UPDATE_SKILL', payload: { id, data } });
  };

  const deleteSkill = (id: string) => {
    dispatch({ type: 'DELETE_SKILL', payload: id });
  };

  // Additional CV actions
  const addProject = (project: CVData['projects'][0]) => {
    dispatch({ type: 'ADD_PROJECT', payload: project });
  };

  const updateProject = (id: string, data: Partial<CVData['projects'][0]>) => {
    dispatch({ type: 'UPDATE_PROJECT', payload: { id, data } });
  };

  const deleteProject = (id: string) => {
    dispatch({ type: 'DELETE_PROJECT', payload: id });
  };

  const addCertification = (certification: CVData['certifications'][0]) => {
    dispatch({ type: 'ADD_CERTIFICATION', payload: certification });
  };

  const updateCertification = (id: string, data: Partial<CVData['certifications'][0]>) => {
    dispatch({ type: 'UPDATE_CERTIFICATION', payload: { id, data } });
  };

  const deleteCertification = (id: string) => {
    dispatch({ type: 'DELETE_CERTIFICATION', payload: id });
  };

  const addLanguage = (language: CVData['languages'][0]) => {
    dispatch({ type: 'ADD_LANGUAGE', payload: language });
  };

  const updateLanguage = (id: string, data: Partial<CVData['languages'][0]>) => {
    dispatch({ type: 'UPDATE_LANGUAGE', payload: { id, data } });
  };

  const deleteLanguage = (id: string) => {
    dispatch({ type: 'DELETE_LANGUAGE', payload: id });
  };

  const addVolunteerExperience = (experience: CVData['volunteerExperience'][0]) => {
    dispatch({ type: 'ADD_VOLUNTEER_EXPERIENCE', payload: experience });
  };

  const updateVolunteerExperience = (id: string, data: Partial<CVData['volunteerExperience'][0]>) => {
    dispatch({ type: 'UPDATE_VOLUNTEER_EXPERIENCE', payload: { id, data } });
  };

  const deleteVolunteerExperience = (id: string) => {
    dispatch({ type: 'DELETE_VOLUNTEER_EXPERIENCE', payload: id });
  };

  const addAward = (award: CVData['awards'][0]) => {
    dispatch({ type: 'ADD_AWARD', payload: award });
  };

  const updateAward = (id: string, data: Partial<CVData['awards'][0]>) => {
    dispatch({ type: 'UPDATE_AWARD', payload: { id, data } });
  };

  const deleteAward = (id: string) => {
    dispatch({ type: 'DELETE_AWARD', payload: id });
  };

  const addPublication = (publication: CVData['publications'][0]) => {
    dispatch({ type: 'ADD_PUBLICATION', payload: publication });
  };

  const updatePublication = (id: string, data: Partial<CVData['publications'][0]>) => {
    dispatch({ type: 'UPDATE_PUBLICATION', payload: { id, data } });
  };

  const deletePublication = (id: string) => {
    dispatch({ type: 'DELETE_PUBLICATION', payload: id });
  };

  const addReference = (reference: CVData['references'][0]) => {
    dispatch({ type: 'ADD_REFERENCE', payload: reference });
  };

  const updateReference = (id: string, data: Partial<CVData['references'][0]>) => {
    dispatch({ type: 'UPDATE_REFERENCE', payload: { id, data } });
  };

  const deleteReference = (id: string) => {
    dispatch({ type: 'DELETE_REFERENCE', payload: id });
  };

  const addCustomSection = (section: CVData['customSections'][0]) => {
    dispatch({ type: 'ADD_CUSTOM_SECTION', payload: section });
  };

  const updateCustomSection = (id: string, data: Partial<CVData['customSections'][0]>) => {
    dispatch({ type: 'UPDATE_CUSTOM_SECTION', payload: { id, data } });
  };

  const deleteCustomSection = (id: string) => {
    dispatch({ type: 'DELETE_CUSTOM_SECTION', payload: id });
  };

  // Marriage biodata specific actions
  const updateMarriagePersonalInfo = (data: Partial<MarriageBiodata['personalInfo']>) => {
    dispatch({ type: 'UPDATE_MARRIAGE_PERSONAL_INFO', payload: data });
  };

  const updateMarriageContactInfo = (data: Partial<MarriageBiodata['contactInfo']>) => {
    dispatch({ type: 'UPDATE_MARRIAGE_CONTACT_INFO', payload: data });
  };

  const updateMarriageFamilyInfo = (data: Partial<MarriageBiodata['familyInfo']>) => {
    dispatch({ type: 'UPDATE_MARRIAGE_FAMILY_INFO', payload: data });
  };

  const addMarriageEducation = (education: MarriageBiodata['education'][0]) => {
    dispatch({ type: 'ADD_MARRIAGE_EDUCATION', payload: education });
  };

  const updateMarriageEducation = (id: string, data: Partial<MarriageBiodata['education'][0]>) => {
    dispatch({ type: 'UPDATE_MARRIAGE_EDUCATION', payload: { id, data } });
  };

  const deleteMarriageEducation = (id: string) => {
    dispatch({ type: 'DELETE_MARRIAGE_EDUCATION', payload: id });
  };

  const addMarriageOccupation = (occupation: MarriageBiodata['occupation'][0]) => {
    dispatch({ type: 'ADD_MARRIAGE_OCCUPATION', payload: occupation });
  };

  const updateMarriageOccupation = (id: string, data: Partial<MarriageBiodata['occupation'][0]>) => {
    dispatch({ type: 'UPDATE_MARRIAGE_OCCUPATION', payload: { id, data } });
  };

  const deleteMarriageOccupation = (id: string) => {
    dispatch({ type: 'DELETE_MARRIAGE_OCCUPATION', payload: id });
  };

  const updateMarriageLifestyle = (data: Partial<MarriageBiodata['lifestyle']>) => {
    dispatch({ type: 'UPDATE_MARRIAGE_LIFESTYLE', payload: data });
  };

  const updateMarriagePartnerPreference = (data: Partial<MarriageBiodata['partnerPreference']>) => {
    dispatch({ type: 'UPDATE_MARRIAGE_PARTNER_PREFERENCE', payload: data });
  };

  const updateMarriageHoroscope = (data: Partial<MarriageBiodata['horoscope']>) => {
    dispatch({ type: 'UPDATE_MARRIAGE_HOROSCOPE', payload: data });
  };

  const updateMarriagePhotos = (data: Partial<MarriageBiodata['photos']>) => {
    dispatch({ type: 'UPDATE_MARRIAGE_PHOTOS', payload: data });
  };

  const addMarriageReference = (reference: MarriageBiodata['references'][0]) => {
    dispatch({ type: 'ADD_MARRIAGE_REFERENCE', payload: reference });
  };

  const updateMarriageReference = (id: string, data: Partial<MarriageBiodata['references'][0]>) => {
    dispatch({ type: 'UPDATE_MARRIAGE_REFERENCE', payload: { id, data } });
  };

  const deleteMarriageReference = (id: string) => {
    dispatch({ type: 'DELETE_MARRIAGE_REFERENCE', payload: id });
  };

  const updateMarriageAbout = (about: string) => {
    dispatch({ type: 'UPDATE_MARRIAGE_ABOUT', payload: about });
  };

  const updateMarriageExpectations = (expectations: string) => {
    dispatch({ type: 'UPDATE_MARRIAGE_EXPECTATIONS', payload: expectations });
  };

  // Form utilities
  const resetForm = () => {
    dispatch({ type: 'RESET_FORM' });
  };

  const exportData = () => {
    return {
      cv: state.documentType === 'cv' ? state.cvData : undefined,
      marriage: state.documentType === 'marriage' ? state.marriageData : undefined,
    };
  };

  const importData = (data: { cv?: CVData; marriage?: MarriageBiodata }) => {
    if (data.cv) {
      dispatch({ type: 'LOAD_CV_DATA', payload: data.cv });
    }
    if (data.marriage) {
      dispatch({ type: 'LOAD_MARRIAGE_DATA', payload: data.marriage });
    }
  };

  // Validation helpers (placeholder implementations)
  const validateCurrentStep = () => {
    // This will be implemented with Zod schemas later
    return true;
  };

  const getStepErrors = (): ValidationError[] => {
    // This will be implemented with Zod schemas later
    return [];
  };

  // Effects
  useEffect(() => {
    loadFromLocalStorage();
  }, []);

  useEffect(() => {
    if (!state.isSaved && state.settings.autoSave) {
      const timer = setTimeout(() => {
        saveToLocalStorage();
        markAsSaved();
      }, 1000);
      return () => clearTimeout(timer);
    }
    return undefined;
  }, [
    state.cvData,
    state.marriageData,
    state.selectedTemplate,
    state.settings,
    state.formProgress,
    state.userSession,
    state.analytics,
    state.isSaved,
  ]);

  // Time tracking
  useEffect(() => {
    const startTime = Date.now();
    const currentSection = state.currentStep;

    const interval = setInterval(() => {
      const timeSpent = Date.now() - startTime;
      updateTimeSpent(currentSection, timeSpent);
    }, 5000); // Update every 5 seconds

    return () => {
      clearInterval(interval);
      const finalTimeSpent = Date.now() - startTime;
      updateTimeSpent(currentSection, finalTimeSpent);
    };
  }, [state.currentStep]);

  const contextValue: CVContextType = {
    state,
    dispatch,
    saveToLocalStorage,
    loadFromLocalStorage,
    generateId,
    markAsSaved,
    setDocumentType,
    setLoading,
    setCurrentStep,
    setTemplate,
    updateFormProgress,
    calculateCompletionRate,
    addAnalyticsError,
    updateTimeSpent,
    trackSectionAbandonment,
    updateUserSession,
    hasPermission,
    updatePersonalInfo,
    updateProfessionalSummary,
    addWorkExperience,
    updateWorkExperience,
    deleteWorkExperience,
    addEducation,
    updateEducation,
    deleteEducation,
    addSkill,
    updateSkill,
    deleteSkill,
    addProject,
    updateProject,
    deleteProject,
    addCertification,
    updateCertification,
    deleteCertification,
    addLanguage,
    updateLanguage,
    deleteLanguage,
    addVolunteerExperience,
    updateVolunteerExperience,
    deleteVolunteerExperience,
    addAward,
    updateAward,
    deleteAward,
    addPublication,
    updatePublication,
    deletePublication,
    addReference,
    updateReference,
    deleteReference,
    addCustomSection,
    updateCustomSection,
    deleteCustomSection,
    updateMarriagePersonalInfo,
    updateMarriageContactInfo,
    updateMarriageFamilyInfo,
    addMarriageEducation,
    updateMarriageEducation,
    deleteMarriageEducation,
    addMarriageOccupation,
    updateMarriageOccupation,
    deleteMarriageOccupation,
    updateMarriageLifestyle,
    updateMarriagePartnerPreference,
    updateMarriageHoroscope,
    updateMarriagePhotos,
    addMarriageReference,
    updateMarriageReference,
    deleteMarriageReference,
    updateMarriageAbout,
    updateMarriageExpectations,
    resetForm,
    exportData,
    importData,
    validateCurrentStep,
    getStepErrors,
  };

  return (
    <CVContext.Provider value={contextValue}>
      {children}
    </CVContext.Provider>
  );
};

export const useCV = () => {
  const context = useContext(CVContext);
  if (context === undefined) {
    throw new Error('useCV must be used within a CVProvider');
  }
  return context;
};