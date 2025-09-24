import { z } from 'zod';
import type { } from '../types/marriage';

// Personal Info Schema
export const marriagePersonalInfoSchema = z.object({
  fullName: z.string().min(1, 'Full name is required').max(100, 'Full name must be less than 100 characters'),
  age: z.number().min(18, 'Age must be at least 18').max(80, 'Age must be less than 80'),
  gender: z.enum(['male', 'female'], {
    message: 'Please select a valid gender',
  }),
  dateOfBirth: z.string().min(1, 'Date of birth is required'),
  birthPlace: z.string().min(1, 'Birth place is required').max(100, 'Birth place must be less than 100 characters'),
  height: z.string().min(1, 'Height is required').max(20, 'Height must be less than 20 characters'),
  weight: z.string().min(1, 'Weight is required').max(20, 'Weight must be less than 20 characters'),
  bloodGroup: z.string().min(1, 'Blood group is required').max(10, 'Blood group must be less than 10 characters'),
  complexion: z.enum(['very_fair', 'fair', 'wheatish', 'olive', 'dark'], {
    message: 'Please select a valid complexion',
  }),
  bodyType: z.enum(['slim', 'average', 'athletic', 'heavy'], {
    message: 'Please select a valid body type',
  }),
  maritalStatus: z.enum(['never_married', 'divorced', 'widowed'], {
    message: 'Please select a valid marital status',
  }),
  children: z.number().min(0, 'Number of children cannot be negative').max(10, 'Number of children must be less than 10').optional(),
  disability: z.string().max(200, 'Disability information must be less than 200 characters').optional(),
  nationality: z.string().min(1, 'Nationality is required').max(50, 'Nationality must be less than 50 characters'),
  religion: z.string().min(1, 'Religion is required').max(50, 'Religion must be less than 50 characters'),
  caste: z.string().max(50, 'Caste must be less than 50 characters').optional(),
  subCaste: z.string().max(50, 'Sub-caste must be less than 50 characters').optional(),
  motherTongue: z.string().min(1, 'Mother tongue is required').max(50, 'Mother tongue must be less than 50 characters'),
  languages: z.array(z.object({
    name: z.string().min(1, 'Language name is required').max(50, 'Language name must be less than 50 characters'),
    proficiency: z.enum(['native', 'fluent', 'conversational', 'basic'], {
      message: 'Please select a valid proficiency level',
    }),
    canRead: z.boolean(),
    canWrite: z.boolean(),
  })).max(10, 'Maximum 10 languages allowed'),
}).refine(
  (data) => {
    if (data.maritalStatus === 'divorced' || data.maritalStatus === 'widowed') {
      return data.children !== undefined;
    }
    return true;
  },
  {
    message: 'Number of children is required for divorced or widowed status',
    path: ['children'],
  }
);

// Contact Info Schema
export const marriageContactInfoSchema = z.object({
  email: z.string().email('Invalid email address').max(100, 'Email must be less than 100 characters'),
  phone: z.string().min(1, 'Phone number is required').regex(/^[+]?[\d\s\-()]+$/, 'Invalid phone number format'),
  whatsapp: z.string().regex(/^[+]?[\d\s\-()]+$/, 'Invalid WhatsApp number format').optional().or(z.literal('')),
  address: z.string().min(1, 'Address is required').max(200, 'Address must be less than 200 characters'),
  city: z.string().min(1, 'City is required').max(50, 'City must be less than 50 characters'),
  state: z.string().min(1, 'State is required').max(50, 'State must be less than 50 characters'),
  country: z.string().min(1, 'Country is required').max(50, 'Country must be less than 50 characters'),
  pinCode: z.string().min(1, 'PIN code is required').regex(/^\d+$/, 'PIN code must contain only digits'),
  residenceType: z.enum(['own', 'rented', 'family'], {
    message: 'Please select a valid residence type',
  }),
});

// Family Info Schema
export const marriageFamilyInfoSchema = z.object({
  familyType: z.enum(['joint', 'nuclear'], {
    message: 'Please select a valid family type',
  }),
  familyStatus: z.enum(['upper_class', 'middle_class', 'lower_middle_class'], {
    message: 'Please select a valid family status',
  }),
  familyValues: z.enum(['traditional', 'moderate', 'liberal'], {
    message: 'Please select a valid family value',
  }),
  fatherName: z.string().min(1, 'Father\'s name is required').max(100, 'Father\'s name must be less than 100 characters'),
  fatherOccupation: z.string().min(1, 'Father\'s occupation is required').max(100, 'Father\'s occupation must be less than 100 characters'),
  fatherStatus: z.enum(['alive', 'deceased'], {
    message: 'Please select father\'s status',
  }),
  motherName: z.string().min(1, 'Mother\'s name is required').max(100, 'Mother\'s name must be less than 100 characters'),
  motherOccupation: z.string().min(1, 'Mother\'s occupation is required').max(100, 'Mother\'s occupation must be less than 100 characters'),
  motherStatus: z.enum(['alive', 'deceased'], {
    message: 'Please select mother\'s status',
  }),
  brothers: z.number().min(0, 'Number of brothers cannot be negative').max(20, 'Number of brothers must be less than 20'),
  marriedBrothers: z.number().min(0, 'Number of married brothers cannot be negative').max(20, 'Number of married brothers must be less than 20'),
  sisters: z.number().min(0, 'Number of sisters cannot be negative').max(20, 'Number of sisters must be less than 20'),
  marriedSisters: z.number().min(0, 'Number of married sisters cannot be negative').max(20, 'Number of married sisters must be less than 20'),
  familyLocation: z.string().min(1, 'Family location is required').max(100, 'Family location must be less than 100 characters'),
  familyOrigin: z.string().min(1, 'Family origin is required').max(100, 'Family origin must be less than 100 characters'),
  maternalUncle: z.string().max(100, 'Maternal uncle\'s name must be less than 100 characters').optional(),
  parentalProperty: z.string().max(200, 'Parental property information must be less than 200 characters').optional(),
}).refine(
  (data) => data.marriedBrothers <= data.brothers,
  {
    message: 'Married brothers cannot exceed total brothers',
    path: ['marriedBrothers'],
  }
).refine(
  (data) => data.marriedSisters <= data.sisters,
  {
    message: 'Married sisters cannot exceed total sisters',
    path: ['marriedSisters'],
  }
);

// Education Schema
export const marriageEducationSchema = z.object({
  id: z.string(),
  level: z.enum(['primary', 'secondary', 'higher_secondary', 'bachelors', 'masters', 'phd', 'other'], {
    message: 'Please select a valid education level',
  }),
  degree: z.string().min(1, 'Degree is required').max(100, 'Degree must be less than 100 characters'),
  institution: z.string().min(1, 'Institution is required').max(100, 'Institution must be less than 100 characters'),
  board: z.string().max(50, 'Board must be less than 50 characters').optional(),
  year: z.string().min(1, 'Year is required').regex(/^\d{4}$/, 'Year must be a valid 4-digit year'),
  percentage: z.string().regex(/^(\d+(\.\d+)?)%$/, 'Percentage must be in valid format (e.g., 85.5%)').optional().or(z.literal('')),
  grade: z.string().max(10, 'Grade must be less than 10 characters').optional(),
  specialization: z.string().max(100, 'Specialization must be less than 100 characters').optional(),
});

// Occupation Schema
export const marriageOccupationSchema = z.object({
  id: z.string(),
  employmentType: z.enum(['employed', 'self_employed', 'business', 'student', 'unemployed', 'homemaker'], {
    message: 'Please select a valid employment type',
  }),
  occupation: z.string().min(1, 'Occupation is required').max(100, 'Occupation must be less than 100 characters'),
  company: z.string().max(100, 'Company name must be less than 100 characters').optional(),
  designation: z.string().max(100, 'Designation must be less than 100 characters').optional(),
  industry: z.string().min(1, 'Industry is required').max(50, 'Industry must be less than 50 characters'),
  annualIncome: z.string().min(1, 'Annual income is required').max(50, 'Annual income must be less than 50 characters'),
  workExperience: z.string().max(100, 'Work experience must be less than 100 characters').optional(),
  workLocation: z.string().min(1, 'Work location is required').max(100, 'Work location must be less than 100 characters'),
  shift: z.enum(['day', 'night', 'rotating', 'remote'], {
    message: 'Please select a valid work shift',
  }),
});

// Lifestyle Schema
export const marriageLifestyleSchema = z.object({
  diet: z.enum(['vegetarian', 'non_vegetarian', 'eggetarian', 'vegan'], {
    message: 'Please select a valid diet preference',
  }),
  smoking: z.enum(['never', 'occasionally', 'regularly', 'quit'], {
    message: 'Please select a valid smoking habit',
  }),
  drinking: z.enum(['never', 'occasionally', 'regularly', 'quit'], {
    message: 'Please select a valid drinking habit',
  }),
  hobbies: z.array(z.string().min(1, 'Hobby cannot be empty')).max(20, 'Maximum 20 hobbies allowed'),
  interests: z.array(z.string().min(1, 'Interest cannot be empty')).max(20, 'Maximum 20 interests allowed'),
  sports: z.array(z.string().min(1, 'Sport cannot be empty')).max(20, 'Maximum 20 sports allowed'),
  music: z.array(z.string().min(1, 'Music genre cannot be empty')).max(20, 'Maximum 20 music genres allowed'),
  movies: z.array(z.string().min(1, 'Movie genre cannot be empty')).max(20, 'Maximum 20 movie genres allowed'),
  books: z.array(z.string().min(1, 'Book genre cannot be empty')).max(20, 'Maximum 20 book genres allowed'),
  travel: z.array(z.string().min(1, 'Travel destination cannot be empty')).max(20, 'Maximum 20 travel destinations allowed'),
  cuisine: z.array(z.string().min(1, 'Cuisine cannot be empty')).max(20, 'Maximum 20 cuisines allowed'),
  dressStyle: z.enum(['traditional', 'western', 'modern', 'casual'], {
    message: 'Please select a valid dress style',
  }),
  socialMedia: z.array(z.string().url('Invalid social media URL')).max(10, 'Maximum 10 social media links allowed').optional(),
});

// Partner Preference Schema
export const marriagePartnerPreferenceSchema = z.object({
  ageRange: z.object({
    min: z.number().min(18, 'Minimum age must be at least 18').max(80, 'Minimum age must be less than 80'),
    max: z.number().min(18, 'Maximum age must be at least 18').max(80, 'Maximum age must be less than 80'),
  }),
  heightRange: z.object({
    min: z.string().min(1, 'Minimum height is required').max(20, 'Minimum height must be less than 20 characters'),
    max: z.string().min(1, 'Maximum height is required').max(20, 'Maximum height must be less than 20 characters'),
  }),
  maritalStatus: z.array(z.enum(['never_married', 'divorced', 'widowed'])).min(1, 'At least one marital status preference is required'),
  religion: z.array(z.string().min(1, 'Religion cannot be empty')).max(10, 'Maximum 10 religions allowed'),
  caste: z.array(z.string().min(1, 'Caste cannot be empty')).max(10, 'Maximum 10 castes allowed').optional(),
  education: z.array(z.string().min(1, 'Education cannot be empty')).max(10, 'Maximum 10 education preferences allowed'),
  occupation: z.array(z.string().min(1, 'Occupation cannot be empty')).max(10, 'Maximum 10 occupation preferences allowed'),
  location: z.array(z.string().min(1, 'Location cannot be empty')).max(20, 'Maximum 20 location preferences allowed'),
  motherTongue: z.array(z.string().min(1, 'Mother tongue cannot be empty')).max(10, 'Maximum 10 mother tongue preferences allowed'),
  diet: z.enum(['vegetarian', 'non_vegetarian', 'eggetarian', 'vegan'], {
    message: 'Please select a valid diet preference',
  }),
  smoking: z.enum(['never', 'occasionally', 'regularly', 'quit'], {
    message: 'Please select a valid smoking preference',
  }),
  drinking: z.enum(['never', 'occasionally', 'regularly', 'quit'], {
    message: 'Please select a valid drinking preference',
  }),
  additionalPreferences: z.string().max(1000, 'Additional preferences must be less than 1000 characters'),
}).refine(
  (data) => data.ageRange.min <= data.ageRange.max,
  {
    message: 'Minimum age must be less than or equal to maximum age',
    path: ['ageRange'],
  }
);

// Horoscope Schema
export const marriageHoroscopeSchema = z.object({
  hasHoroscope: z.boolean(),
  birthTime: z.string().max(20, 'Birth time must be less than 20 characters').optional(),
  birthPlace: z.string().max(100, 'Birth place must be less than 100 characters').optional(),
  star: z.string().max(50, 'Star must be less than 50 characters').optional(),
  rashi: z.string().max(50, 'Rashi must be less than 50 characters').optional(),
  nakshatra: z.string().max(50, 'Nakshatra must be less than 50 characters').optional(),
  manglik: z.enum(['yes', 'no', 'partial', 'unknown'], {
    message: 'Please select a valid manglik status',
  }),
  dosh: z.array(z.string().min(1, 'Dosh cannot be empty')).max(10, 'Maximum 10 dosh entries allowed').optional(),
  gotra: z.string().max(50, 'Gotra must be less than 50 characters').optional(),
  nadi: z.string().max(50, 'Nadi must be less than 50 characters').optional(),
}).refine(
  (data) => {
    if (data.hasHoroscope) {
      return data.birthTime && data.birthPlace;
    }
    return true;
  },
  {
    message: 'Birth time and place are required when horoscope is available',
    path: ['birthTime'],
  }
);

// Photos Schema
export const marriagePhotosSchema = z.object({
  profile: z.string().url('Invalid profile photo URL').or(z.literal('')),
  additional: z.array(z.string().url('Invalid photo URL')).max(10, 'Maximum 10 additional photos allowed'),
  idProof: z.string().url('Invalid ID proof URL').or(z.literal('')),
  certificates: z.array(z.string().url('Invalid certificate URL')).max(10, 'Maximum 10 certificates allowed').optional(),
});

// References Schema
export const marriageReferencesSchema = z.object({
  name: z.string().min(1, 'Reference name is required').max(100, 'Name must be less than 100 characters'),
  relation: z.string().min(1, 'Relation is required').max(50, 'Relation must be less than 50 characters'),
  contact: z.string().min(1, 'Contact information is required').max(100, 'Contact must be less than 100 characters'),
  address: z.string().min(1, 'Address is required').max(200, 'Address must be less than 200 characters'),
  occupation: z.string().min(1, 'Occupation is required').max(100, 'Occupation must be less than 100 characters'),
});

// About Me and Expectations Schema
export const marriageAboutSchema = z.object({
  aboutMe: z.string().min(10, 'About me must be at least 10 characters').max(2000, 'About me must be less than 2000 characters'),
  expectations: z.string().min(10, 'Expectations must be at least 10 characters').max(2000, 'Expectations must be less than 2000 characters'),
});

// Complete Marriage Biodata Schema
export const marriageBiodataSchema = z.object({
  personalInfo: marriagePersonalInfoSchema,
  contactInfo: marriageContactInfoSchema,
  familyInfo: marriageFamilyInfoSchema,
  education: z.array(marriageEducationSchema),
  occupation: z.array(marriageOccupationSchema),
  lifestyle: marriageLifestyleSchema,
  partnerPreference: marriagePartnerPreferenceSchema,
  horoscope: marriageHoroscopeSchema,
  photos: marriagePhotosSchema,
  references: z.array(marriageReferencesSchema),
  aboutMe: z.string().min(10, 'About me must be at least 10 characters').max(2000, 'About me must be less than 2000 characters'),
  expectations: z.string().min(10, 'Expectations must be at least 10 characters').max(2000, 'Expectations must be less than 2000 characters'),
}).refine(
  (data) => data.education.length <= 10,
  {
    message: 'Maximum 10 education entries allowed',
    path: ['education'],
  }
).refine(
  (data) => data.occupation.length <= 5,
  {
    message: 'Maximum 5 occupation entries allowed',
    path: ['occupation'],
  }
).refine(
  (data) => data.references.length <= 5,
  {
    message: 'Maximum 5 references allowed',
    path: ['references'],
  }
);

// Step-specific schemas for validation
export const marriageStepSchemas = {
  personal: marriagePersonalInfoSchema,
  contact: marriageContactInfoSchema,
  family: marriageFamilyInfoSchema,
  education: z.object({ education: z.array(marriageEducationSchema) }),
  occupation: z.object({ occupation: z.array(marriageOccupationSchema) }),
  lifestyle: marriageLifestyleSchema,
  'partner-preference': marriagePartnerPreferenceSchema,
  horoscope: marriageHoroscopeSchema,
  photos: marriagePhotosSchema,
  about: marriageAboutSchema,
};

// Custom validation functions
export const validateAgeFromDateOfBirth = (dateOfBirth: string): number => {
  const birthDate = new Date(dateOfBirth);
  const today = new Date();
  let age = today.getFullYear() - birthDate.getFullYear();
  const monthDiff = today.getMonth() - birthDate.getMonth();

  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }

  return age;
};

export const validateHeightFormat = (height: string): boolean => {
  // Accept formats like "5'10\"", "5 feet 10 inches", "178 cm", etc.
  const heightRegex = /^(?:(\d+)'\s*(\d*)"?|(\d+)\s*(?:feet|ft)\s*(\d+)\s*(?:inches|in)|(\d+(?:\.\d+)?)\s*cm)$/;
  return heightRegex.test(height.trim());
};

export const validateIncomeFormat = (income: string): boolean => {
  // Accept formats like "50000", "50,000", "50K", "5 Lakhs", "5 LPA", etc.
  const incomeRegex = /^(?:(\d{1,3}(?:,\d{3})*|\d+)(?:\s*(?:K|LPA|Lakhs|PA))?|\d+(?:\.\d+)\s*(?:LPA|Lakhs|PA))$/i;
  return incomeRegex.test(income.trim());
};

// Type exports
export type MarriagePersonalInfoFormData = z.infer<typeof marriagePersonalInfoSchema>;
export type MarriageContactInfoFormData = z.infer<typeof marriageContactInfoSchema>;
export type MarriageFamilyInfoFormData = z.infer<typeof marriageFamilyInfoSchema>;
export type MarriageEducationFormData = z.infer<typeof marriageEducationSchema>;
export type MarriageOccupationFormData = z.infer<typeof marriageOccupationSchema>;
export type MarriageLifestyleFormData = z.infer<typeof marriageLifestyleSchema>;
export type MarriagePartnerPreferenceFormData = z.infer<typeof marriagePartnerPreferenceSchema>;
export type MarriageHoroscopeFormData = z.infer<typeof marriageHoroscopeSchema>;
export type MarriagePhotosFormData = z.infer<typeof marriagePhotosSchema>;
export type MarriageReferencesFormData = z.infer<typeof marriageReferencesSchema>;
export type MarriageAboutFormData = z.infer<typeof marriageAboutSchema>;
export type MarriageBiodataFormData = z.infer<typeof marriageBiodataSchema>;