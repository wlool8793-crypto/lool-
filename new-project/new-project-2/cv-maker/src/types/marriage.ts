import { DocumentType, TemplateCategory } from './common';

export interface MarriagePersonalInfo {
  fullName: string;
  age: number;
  gender: 'male' | 'female';
  dateOfBirth: string;
  birthPlace: string;
  height: string;
  weight: string;
  bloodGroup: string;
  complexion: 'very_fair' | 'fair' | 'wheatish' | 'olive' | 'dark';
  bodyType: 'slim' | 'average' | 'athletic' | 'heavy';
  maritalStatus: 'never_married' | 'divorced' | 'widowed';
  children?: number;
  disability?: string;
  nationality: string;
  religion: string;
  caste?: string;
  subCaste?: string;
  motherTongue: string;
  languages: MarriageLanguage[];
}

export interface MarriageLanguage {
  name: string;
  proficiency: 'native' | 'fluent' | 'conversational' | 'basic';
  canRead: boolean;
  canWrite: boolean;
}

export interface MarriageFamilyInfo {
  familyType: 'joint' | 'nuclear';
  familyStatus: 'upper_class' | 'middle_class' | 'lower_middle_class';
  familyValues: 'traditional' | 'moderate' | 'liberal';
  fatherName: string;
  fatherOccupation: string;
  fatherStatus: 'alive' | 'deceased';
  motherName: string;
  motherOccupation: string;
  motherStatus: 'alive' | 'deceased';
  brothers: number;
  marriedBrothers: number;
  sisters: number;
  marriedSisters: number;
  familyLocation: string;
  familyOrigin: string;
  maternalUncle?: string;
  parentalProperty?: string;
}

export interface MarriageEducation {
  id: string;
  level: 'primary' | 'secondary' | 'higher_secondary' | 'bachelors' | 'masters' | 'phd' | 'other';
  degree: string;
  institution: string;
  board?: string;
  year: string;
  percentage?: string;
  grade?: string;
  specialization?: string;
}

export interface MarriageOccupation {
  id: string;
  employmentType: 'employed' | 'self_employed' | 'business' | 'student' | 'unemployed' | 'homemaker';
  occupation: string;
  company?: string;
  designation?: string;
  industry: string;
  annualIncome: string;
  workExperience?: string;
  workLocation: string;
  shift: 'day' | 'night' | 'rotating' | 'remote';
}

export interface MarriageContactInfo {
  email: string;
  phone: string;
  whatsapp?: string;
  address: string;
  city: string;
  state: string;
  country: string;
  pinCode: string;
  residenceType: 'own' | 'rented' | 'family';
}

export interface MarriagePartnerPreference {
  ageRange: {
    min: number;
    max: number;
  };
  heightRange: {
    min: string;
    max: string;
  };
  maritalStatus: ('never_married' | 'divorced' | 'widowed')[];
  religion: string[];
  caste?: string[];
  education: string[];
  occupation: string[];
  location: string[];
  motherTongue: string[];
  diet: 'vegetarian' | 'non_vegetarian' | 'eggetarian' | 'vegan';
  smoking: 'never' | 'occasionally' | 'regularly' | 'quit';
  drinking: 'never' | 'occasionally' | 'regularly' | 'quit';
  additionalPreferences: string;
}

export interface MarriageLifestyle {
  diet: 'vegetarian' | 'non_vegetarian' | 'eggetarian' | 'vegan';
  smoking: 'never' | 'occasionally' | 'regularly' | 'quit';
  drinking: 'never' | 'occasionally' | 'regularly' | 'quit';
  hobbies: string[];
  interests: string[];
  sports: string[];
  music: string[];
  movies: string[];
  books: string[];
  travel: string[];
  cuisine: string[];
  dressStyle: 'traditional' | 'western' | 'modern' | 'casual';
  socialMedia?: string[];
}

export interface MarriageHoroscope {
  hasHoroscope: boolean;
  birthTime?: string;
  birthPlace?: string;
  star?: string;
  rashi?: string;
  nakshatra?: string;
  manglik: 'yes' | 'no' | 'partial' | 'unknown';
  dosh?: string[];
  gotra?: string;
  nadi?: string;
}

export interface MarriagePhotos {
  profile: string;
  additional: string[];
  idProof?: string;
  certificates?: string[];
}

export interface MarriageReferences {
  name: string;
  relation: string;
  contact: string;
  address: string;
  occupation: string;
}

export interface MarriageBiodata {
  id: string;
  documentType: DocumentType;
  templateCategory: TemplateCategory;
  personalInfo: MarriagePersonalInfo;
  contactInfo: MarriageContactInfo;
  familyInfo: MarriageFamilyInfo;
  education: MarriageEducation[];
  occupation: MarriageOccupation[];
  lifestyle: MarriageLifestyle;
  partnerPreference: MarriagePartnerPreference;
  horoscope?: MarriageHoroscope;
  photos: MarriagePhotos;
  references: MarriageReferences[];
  aboutMe: string;
  expectations: string;
  createdAt: string;
  updatedAt: string;
  isPublished: boolean;
  viewCount: number;
  settings: {
    showContact: boolean;
    showFamilyDetails: boolean;
    showIncome: boolean;
    showPhotos: boolean;
    allowMessages: boolean;
  };
}

export type MarriageFormStep = 'personal' | 'contact' | 'family' | 'education' | 'occupation' | 'lifestyle' | 'partner-preference' | 'horoscope' | 'photos' | 'about' | 'preview';
export type MarriageTemplateType = 'traditional' | 'modern' | 'elegant' | 'simple' | 'detailed';