import { z } from 'zod';
import { MarriageBiodata } from '../types/marriage';

// Cultural and regional validation schemas
export const createCulturalValidationSchema = (region: string) => {
  const basePersonalInfo = z.object({
    fullName: z.string().min(2, 'Full name must be at least 2 characters'),
    age: z.number().min(18, 'Must be at least 18 years old').max(100, 'Age must be less than 100'),
    gender: z.enum(['male', 'female']),
    dateOfBirth: z.string().refine((date) => {
      const birthDate = new Date(date);
      const today = new Date();
      const age = today.getFullYear() - birthDate.getFullYear();
      return age >= 18 && age <= 100;
    }, 'Age must be between 18 and 100 years'),
    height: z.string().min(2, 'Height is required'),
    weight: z.string().min(2, 'Weight is required'),
    nationality: z.string().min(2, 'Nationality is required'),
    religion: z.string().min(2, 'Religion is required'),
    motherTongue: z.string().min(2, 'Mother tongue is required'),
    languages: z.array(z.object({
      name: z.string().min(2, 'Language name is required'),
      proficiency: z.enum(['native', 'fluent', 'conversational', 'basic']),
      canRead: z.boolean(),
      canWrite: z.boolean()
    })).min(1, 'At least one language must be specified')
  });

  // Region-specific validation rules
  const regionSpecificSchemas = {
    'north_indian': z.object({
      caste: z.string().min(2, 'Caste is required for North Indian profiles'),
      subCaste: z.string().optional(),
      gotra: z.string().optional(),
      // North Indian specific validation
    }),
    'south_indian': z.object({
      caste: z.string().min(2, 'Caste is required for South Indian profiles'),
      subCaste: z.string().optional(),
      // South Indian specific validation
    }),
    'bengali': z.object({
      caste: z.string().min(2, 'Caste is required for Bengali profiles'),
      subCaste: z.string().optional(),
      // Bengali specific validation
    }),
    'gujarati': z.object({
      caste: z.string().min(2, 'Caste is required for Gujarati profiles'),
      subCaste: z.string().optional(),
      // Gujarati specific validation
    }),
    'punjabi': z.object({
      caste: z.string().optional(), // Optional for Punjabi
      subCaste: z.string().optional(),
      // Punjabi specific validation
    }),
    'muslim': z.object({
      sect: z.string().min(2, 'Sect is required for Muslim profiles'),
      caste: z.string().optional(), // Caste is not primary for Muslims
      // Muslim specific validation
    }),
    'western': z.object({
      caste: z.string().optional(), // Caste is optional for Western profiles
      subCaste: z.string().optional(),
      // Western specific validation
    }),
    'default': z.object({
      caste: z.string().optional(),
      subCaste: z.string().optional(),
    })
  };

  const regionSchema = regionSpecificSchemas[region as keyof typeof regionSpecificSchemas] || regionSpecificSchemas.default;

  const familyInfoSchema = z.object({
    familyType: z.enum(['joint', 'nuclear']),
    familyStatus: z.enum(['upper_class', 'middle_class', 'lower_middle_class']),
    familyValues: z.enum(['traditional', 'moderate', 'liberal']),
    fatherName: z.string().min(2, 'Father name is required'),
    fatherOccupation: z.string().min(2, 'Father occupation is required'),
    fatherStatus: z.enum(['alive', 'deceased']),
    motherName: z.string().min(2, 'Mother name is required'),
    motherOccupation: z.string().min(2, 'Mother occupation is required'),
    motherStatus: z.enum(['alive', 'deceased']),
    brothers: z.number().min(0, 'Number of brothers cannot be negative'),
    marriedBrothers: z.number().min(0, 'Number of married brothers cannot be negative'),
    sisters: z.number().min(0, 'Number of sisters cannot be negative'),
    marriedSisters: z.number().min(0, 'Number of married sisters cannot be negative'),
    familyLocation: z.string().min(2, 'Family location is required'),
    familyOrigin: z.string().min(2, 'Family origin is required'),
    maternalUncle: z.string().optional(),
    parentalProperty: z.string().optional()
  }).refine(data => data.marriedBrothers <= data.brothers, {
    message: 'Married brothers cannot exceed total brothers',
    path: ['marriedBrothers']
  }).refine(data => data.marriedSisters <= data.sisters, {
    message: 'Married sisters cannot exceed total sisters',
    path: ['marriedSisters']
  });

  const contactInfoSchema = z.object({
    email: z.string().email('Please enter a valid email address'),
    phone: z.string().refine(phone => {
      const cleaned = phone.replace(/\D/g, '');
      return cleaned.length >= 10 && cleaned.length <= 15;
    }, 'Please enter a valid phone number'),
    whatsapp: z.string().optional(),
    address: z.string().min(5, 'Address must be at least 5 characters'),
    city: z.string().min(2, 'City is required'),
    state: z.string().min(2, 'State is required'),
    country: z.string().min(2, 'Country is required'),
    pinCode: z.string().refine(pin => {
      const cleaned = pin.replace(/\D/g, '');
      return cleaned.length >= 5 && cleaned.length <= 10;
    }, 'Please enter a valid postal code'),
    residenceType: z.enum(['own', 'rented', 'family'])
  });

  const educationSchema = z.object({
    level: z.enum(['primary', 'secondary', 'higher_secondary', 'bachelors', 'masters', 'phd', 'other']),
    degree: z.string().min(2, 'Degree is required'),
    institution: z.string().min(2, 'Institution name is required'),
    board: z.string().optional(),
    year: z.string().refine(year => {
      const yearNum = parseInt(year);
      return yearNum >= 1950 && yearNum <= new Date().getFullYear();
    }, 'Please enter a valid year'),
    percentage: z.string().optional(),
    grade: z.string().optional(),
    specialization: z.string().optional()
  }).refine(data => data.percentage || data.grade, {
    message: 'Either percentage or grade must be provided',
    path: ['percentage']
  });

  const occupationSchema = z.object({
    employmentType: z.enum(['employed', 'self_employed', 'business', 'student', 'unemployed', 'homemaker']),
    occupation: z.string().min(2, 'Occupation is required'),
    company: z.string().optional(),
    designation: z.string().optional(),
    industry: z.string().min(2, 'Industry is required'),
    annualIncome: z.string().min(1, 'Annual income is required'),
    workExperience: z.string().optional(),
    workLocation: z.string().min(2, 'Work location is required'),
    shift: z.enum(['day', 'night', 'rotating', 'remote'])
  });

  const lifestyleSchema = z.object({
    diet: z.enum(['vegetarian', 'non_vegetarian', 'eggetarian', 'vegan']),
    smoking: z.enum(['never', 'occasionally', 'regularly', 'quit']),
    drinking: z.enum(['never', 'occasionally', 'regularly', 'quit']),
    hobbies: z.array(z.string()).optional(),
    interests: z.array(z.string()).optional(),
    sports: z.array(z.string()).optional(),
    music: z.array(z.string()).optional(),
    movies: z.array(z.string()).optional(),
    books: z.array(z.string()).optional(),
    travel: z.array(z.string()).optional(),
    cuisine: z.array(z.string()).optional(),
    dressStyle: z.enum(['traditional', 'western', 'modern', 'casual']),
    socialMedia: z.array(z.string()).optional()
  });

  const partnerPreferenceSchema = z.object({
    ageRange: z.object({
      min: z.number().min(18, 'Minimum age must be at least 18'),
      max: z.number().max(100, 'Maximum age must be less than 100')
    }).refine(data => data.max > data.min, {
      message: 'Maximum age must be greater than minimum age',
      path: ['max']
    }),
    heightRange: z.object({
      min: z.string().min(2, 'Minimum height is required'),
      max: z.string().min(2, 'Maximum height is required')
    }),
    maritalStatus: z.array(z.enum(['never_married', 'divorced', 'widowed'])).min(1, 'At least one marital status must be selected'),
    religion: z.array(z.string()).min(1, 'At least one religion must be selected'),
    caste: z.array(z.string()).optional(),
    education: z.array(z.string()).min(1, 'At least one education preference must be selected'),
    occupation: z.array(z.string()).min(1, 'At least one occupation preference must be selected'),
    location: z.array(z.string()).min(1, 'At least one location preference must be selected'),
    motherTongue: z.array(z.string()).min(1, 'At least one mother tongue preference must be selected'),
    diet: z.enum(['vegetarian', 'non_vegetarian', 'eggetarian', 'vegan']),
    smoking: z.enum(['never', 'occasionally', 'regularly', 'quit']),
    drinking: z.enum(['never', 'occasionally', 'regularly', 'quit']),
    additionalPreferences: z.string().optional()
  });

  const horoscopeSchema = z.object({
    hasHoroscope: z.boolean(),
    birthTime: z.string().optional(),
    birthPlace: z.string().optional(),
    star: z.string().optional(),
    rashi: z.string().optional(),
    nakshatra: z.string().optional(),
    manglik: z.enum(['yes', 'no', 'partial', 'unknown']),
    dosh: z.array(z.string()).optional(),
    gotra: z.string().optional(),
    nadi: z.string().optional()
  }).refine(data => {
    if (data.hasHoroscope) {
      return data.birthTime && data.birthPlace;
    }
    return true;
  }, {
    message: 'Birth time and place are required when horoscope is available',
    path: ['birthTime']
  });

  return {
    personalInfo: basePersonalInfo.merge(regionSchema),
    familyInfo: familyInfoSchema,
    contactInfo: contactInfoSchema,
    education: educationSchema,
    occupation: occupationSchema,
    lifestyle: lifestyleSchema,
    partnerPreference: partnerPreferenceSchema,
    horoscope: horoscopeSchema
  };
};

// Cultural compatibility validation
export const validateCulturalCompatibility = (profile1: MarriageBiodata, profile2: MarriageBiodata) => {
  const compatibilityIssues: string[] = [];
  const warnings: string[] = [];

  // Religious compatibility
  if (profile1.personalInfo.religion !== profile2.personalInfo.religion) {
    warnings.push('Different religious backgrounds may require additional considerations');
  }

  // Caste compatibility (for Indian profiles)
  if (profile1.personalInfo.religion === 'Hindu' && profile2.personalInfo.religion === 'Hindu') {
    if (profile1.personalInfo.caste !== profile2.personalInfo.caste) {
      warnings.push('Different castes may face family resistance');
    }
  }

  // Dietary compatibility
  if (profile1.lifestyle?.diet !== profile2.lifestyle?.diet) {
    compatibilityIssues.push('Different dietary preferences may cause lifestyle conflicts');
  }

  // Age gap validation
  const ageDiff = Math.abs(profile1.personalInfo.age - profile2.personalInfo.age);
  if (ageDiff > 15) {
    warnings.push('Significant age gap may affect compatibility');
  }

  // Geographic compatibility
  if (profile1.contactInfo.country !== profile2.contactInfo.country) {
    warnings.push('Long-distance relationship may require relocation');
  }

  // Lifestyle compatibility
  if (profile1.lifestyle?.smoking !== profile2.lifestyle?.smoking) {
    compatibilityIssues.push('Different smoking habits may cause conflicts');
  }

  if (profile1.lifestyle?.drinking !== profile2.lifestyle?.drinking) {
    compatibilityIssues.push('Different drinking habits may cause conflicts');
  }

  // Family values compatibility
  if (profile1.familyInfo.familyValues !== profile2.familyInfo.familyValues) {
    warnings.push('Different family values may require compromise');
  }

  // Education level compatibility
  const getHighestEducation = (education: any[]) => {
    const levels = ['primary', 'secondary', 'higher_secondary', 'bachelors', 'masters', 'phd'];
    return Math.max(...education.map(edu => levels.indexOf(edu.level)));
  };

  const edu1 = getHighestEducation(profile1.education);
  const edu2 = getHighestEducation(profile2.education);

  if (Math.abs(edu1 - edu2) > 2) {
    warnings.push('Significant difference in education levels may affect intellectual compatibility');
  }

  return {
    compatibilityIssues,
    warnings,
    isCompatible: compatibilityIssues.length === 0,
    hasWarnings: warnings.length > 0
  };
};

// Regional validation helpers
export const validateRegionalRequirements = (data: MarriageBiodata, region: string) => {
  const errors: string[] = [];

  switch (region) {
    case 'north_indian':
      if (!data.personalInfo.caste) {
        errors.push('Caste is required for North Indian marriage profiles');
      }
      if (data.horoscope?.hasHoroscope && !data.horoscope.manglik) {
        errors.push('Manglik status is required for North Indian horoscope matching');
      }
      break;

    case 'south_indian':
      if (!data.personalInfo.caste) {
        errors.push('Caste is required for South Indian marriage profiles');
      }
      if (data.horoscope?.hasHoroscope && !data.horoscope.nakshatra) {
        errors.push('Nakshatra is required for South Indian horoscope matching');
      }
      break;

    case 'bengali':
      if (!data.personalInfo.caste) {
        errors.push('Caste is required for Bengali marriage profiles');
      }
      break;

    case 'muslim':
      if (!data.horoscope) {
        // Muslim profiles may not require horoscope
      }
      if (data.lifestyle?.diet !== 'non_vegetarian' && data.lifestyle?.diet !== 'halal') {
        errors.push('Muslim profiles typically require halal dietary preferences');
      }
      break;

    case 'western':
      // Western profiles have fewer cultural requirements
      if (data.lifestyle?.diet === 'jain') {
        errors.push('Jain diet is unusual for Western profiles');
      }
      break;
  }

  return errors;
};

// Form field validation with cultural context
export const validateFormField = (field: string, value: any, context: {
  region: string;
  religion?: string;
  language: string;
}) => {
  const errors: string[] = [];

  switch (field) {
    case 'height':
      if (context.region === 'indian' && !value.match(/cm/i)) {
        errors.push('Height should be specified in centimeters for Indian profiles');
      }
      if (context.region === 'western' && !value.match(/ft/i)) {
        errors.push('Height should be specified in feet for Western profiles');
      }
      break;

    case 'phone':
      const cleaned = value.replace(/\D/g, '');
      if (context.region === 'indian' && cleaned.length !== 10) {
        errors.push('Phone number must be 10 digits for Indian profiles');
      }
      if (context.region === 'western' && cleaned.length !== 10) {
        errors.push('Phone number must be 10 digits for Western profiles');
      }
      break;

    case 'pinCode':
      if (context.region === 'indian' && !/^[1-9][0-9]{5}$/.test(value)) {
        errors.push('Invalid Indian PIN code format');
      }
      if (context.region === 'western' && !/^[0-9]{5}(?:-[0-9]{4})?$/.test(value)) {
        errors.push('Invalid ZIP code format');
      }
      break;

    case 'caste':
      if (context.region === 'north_indian' && !value) {
        errors.push('Caste is required for North Indian profiles');
      }
      if (context.religion === 'muslim' && value) {
        errors.push('Caste is not typically required for Muslim profiles');
      }
      break;

    case 'gotra':
      if (context.religion === 'hindu' && !value) {
        errors.push('Gotra is important for Hindu marriage compatibility');
      }
      break;

    case 'manglik':
      if (context.religion === 'hindu' && context.region === 'north_indian' && !value) {
        errors.push('Manglik status is crucial for North Indian Hindu marriages');
      }
      break;
  }

  return errors;
};

// Complete cultural validation
export const performCulturalValidation = (data: MarriageBiodata, region: string) => {
  const schema = createCulturalValidationSchema(region);
  const errors: string[] = [];
  const warnings: string[] = [];

  // Validate against schema
  try {
    const fullSchema = z.object({
      personalInfo: schema.personalInfo,
      familyInfo: schema.familyInfo,
      contactInfo: schema.contactInfo,
      education: z.array(schema.education).min(1, 'At least one education record is required'),
      occupation: z.array(schema.occupation).min(1, 'At least one occupation record is required'),
      lifestyle: schema.lifestyle,
      partnerPreference: schema.partnerPreference,
      horoscope: schema.horoscope
    });

    fullSchema.parse(data);
  } catch (error) {
    if (error instanceof z.ZodError) {
      error.errors.forEach(err => {
        errors.push(`${err.path.join('.')}: ${err.message}`);
      });
    }
  }

  // Validate regional requirements
  const regionalErrors = validateRegionalRequirements(data, region);
  errors.push(...regionalErrors);

  // Validate individual fields
  const fieldsToValidate = [
    'height', 'phone', 'pinCode', 'caste', 'gotra', 'manglik'
  ];

  fieldsToValidate.forEach(field => {
    const value = field.split('.').reduce((obj, key) => obj?.[key], data);
    const fieldErrors = validateFormField(field, value, {
      region,
      religion: data.personalInfo.religion,
      language: data.personalInfo.motherTongue
    });
    errors.push(...fieldErrors);
  });

  return {
    isValid: errors.length === 0,
    errors,
    warnings
  };
};