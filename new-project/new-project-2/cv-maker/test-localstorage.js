// Test localStorage functionality in the CVContext
// This simulates the localStorage operations that would happen in the app

const testData = {
  cvData: {
    id: 'test-cv-123',
    documentType: 'cv',
    templateCategory: 'professional',
    personalInfo: {
      fullName: 'John Doe',
      email: 'john@example.com',
      phone: '+1234567890',
      address: '123 Test St',
      linkedin: '',
      website: '',
      github: ''
    },
    professionalSummary: 'Test summary',
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
      currency: 'USD'
    }
  },
  marriageData: {
    id: 'test-marriage-123',
    documentType: 'marriage',
    templateCategory: 'marriage',
    personalInfo: {
      fullName: 'Jane Doe',
      age: 25,
      gender: 'female',
      dateOfBirth: '1998-01-01',
      birthPlace: 'Test City',
      height: '5\'5"',
      weight: '120 lbs',
      bloodGroup: 'O+',
      complexion: 'fair',
      bodyType: 'average',
      maritalStatus: 'never_married',
      nationality: 'Test Country',
      religion: 'Test Religion',
      motherTongue: 'Test Language',
      languages: []
    },
    contactInfo: {
      email: 'jane@example.com',
      phone: '+1234567890',
      address: '123 Test St',
      city: 'Test City',
      state: 'Test State',
      country: 'Test Country',
      pinCode: '12345',
      residenceType: 'own'
    },
    familyInfo: {
      familyType: 'nuclear',
      familyStatus: 'middle_class',
      familyValues: 'moderate',
      fatherName: 'Father Name',
      fatherOccupation: 'Father Occupation',
      fatherStatus: 'alive',
      motherName: 'Mother Name',
      motherOccupation: 'Mother Occupation',
      motherStatus: 'alive',
      brothers: 1,
      marriedBrothers: 0,
      sisters: 1,
      marriedSisters: 0,
      familyLocation: 'Test Location',
      familyOrigin: 'Test Origin'
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
      dressStyle: 'modern'
    },
    partnerPreference: {
      ageRange: { min: 25, max: 35 },
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
      additionalPreferences: ''
    },
    horoscope: {
      hasHoroscope: false,
      manglik: 'unknown'
    },
    photos: {
      profile: '',
      additional: []
    },
    references: [],
    aboutMe: 'Test about me',
    expectations: 'Test expectations',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    isPublished: false,
    viewCount: 0,
    settings: {
      showContact: true,
      showFamilyDetails: true,
      showIncome: true,
      showPhotos: true,
      allowMessages: true
    }
  },
  documentType: 'cv',
  selectedTemplate: 'modern',
  currentStep: 'personal',
  formProgress: {
    cv: {
      personal: 100,
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
      preview: 0
    },
    marriage: {
      personal: 100,
      contact: 0,
      family: 0,
      education: 0,
      occupation: 0,
      lifestyle: 0,
      'partner-preference': 0,
      horoscope: 0,
      photos: 0,
      about: 0,
      preview: 0
    }
  },
  settings: {
    template: 'modern',
    autoSave: true,
    validationMode: 'onBlur',
    language: 'en',
    theme: 'light'
  },
  userSession: {
    userId: 'test-user-123',
    role: 'owner',
    permissions: ['read', 'write', 'delete'],
    lastActivity: new Date().toISOString()
  },
  analytics: {
    timeSpent: {
      personal: 300000,
      summary: 120000
    },
    formErrors: [],
    completionRate: 15,
    abandonedSections: []
  }
};

console.log('Testing localStorage functionality...');

try {
  // Test saving data
  localStorage.setItem('cvData', JSON.stringify(testData.cvData));
  localStorage.setItem('marriageData', JSON.stringify(testData.marriageData));
  localStorage.setItem('documentType', testData.documentType);
  localStorage.setItem('selectedTemplate', testData.selectedTemplate);
  localStorage.setItem('currentStep', testData.currentStep);
  localStorage.setItem('formProgress', JSON.stringify(testData.formProgress));
  localStorage.setItem('settings', JSON.stringify(testData.settings));
  localStorage.setItem('userSession', JSON.stringify(testData.userSession));
  localStorage.setItem('analytics', JSON.stringify(testData.analytics));

  console.log('✅ Data saved to localStorage successfully');

  // Test loading data
  const savedCVData = localStorage.getItem('cvData');
  const savedMarriageData = localStorage.getItem('marriageData');
  const savedDocumentType = localStorage.getItem('documentType');
  const savedTemplate = localStorage.getItem('selectedTemplate');
  const savedStep = localStorage.getItem('currentStep');
  const savedProgress = localStorage.getItem('formProgress');
  const savedSettings = localStorage.getItem('settings');
  const savedUserSession = localStorage.getItem('userSession');
  const savedAnalytics = localStorage.getItem('analytics');

  if (savedCVData && savedMarriageData && savedDocumentType) {
    console.log('✅ Data loaded from localStorage successfully');

    const parsedCVData = JSON.parse(savedCVData);
    const parsedMarriageData = JSON.parse(savedMarriageData);

    if (parsedCVData.personalInfo.fullName === 'John Doe' &&
        parsedMarriageData.personalInfo.fullName === 'Jane Doe') {
      console.log('✅ Data integrity verified - personal info matches');
    } else {
      console.log('❌ Data integrity check failed');
    }
  } else {
    console.log('❌ Failed to load data from localStorage');
  }

  // Test clearing data
  localStorage.removeItem('cvData');
  localStorage.removeItem('marriageData');
  localStorage.removeItem('documentType');
  localStorage.removeItem('selectedTemplate');
  localStorage.removeItem('currentStep');
  localStorage.removeItem('formProgress');
  localStorage.removeItem('settings');
  localStorage.removeItem('userSession');
  localStorage.removeItem('analytics');

  console.log('✅ localStorage cleared successfully');

} catch (error) {
  console.error('❌ localStorage test failed:', error.message);
}

console.log('localStorage functionality test completed');