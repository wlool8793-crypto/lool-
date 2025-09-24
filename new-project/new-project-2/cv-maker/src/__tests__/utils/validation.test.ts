import { validateStep, ValidationResult } from '@/utils/validation';
import type { CVData } from '@/types/cv';

describe('Validation Utils', () => {
  const mockCVData: CVData = {
    personalInfo: {
      fullName: 'John Doe',
      email: 'john@example.com',
      phone: '+1 (555) 123-4567',
      address: '123 Main St, City, State 12345',
      linkedin: 'https://linkedin.com/in/johndoe',
      website: 'https://johndoe.com',
      github: 'https://github.com/johndoe',
    },
    professionalSummary: 'Experienced software developer with 5+ years in full-stack development.',
    workExperience: [
      {
        id: '1',
        jobTitle: 'Senior Developer',
        company: 'Tech Corp',
        location: 'San Francisco, CA',
        startDate: '2020-01-01',
        endDate: '2023-01-01',
        description: 'Led development of web applications.',
        achievements: ['Improved performance by 50%'],
      },
    ],
    education: [
      {
        id: '1',
        degree: 'Bachelor of Science',
        field: 'Computer Science',
        institution: 'University of Technology',
        location: 'City, State',
        graduationDate: '2019-05-01',
        gpa: '3.8',
      },
    ],
    skills: [
      { id: '1', name: 'JavaScript', level: 'Advanced' },
      { id: '2', name: 'React', level: 'Advanced' },
    ],
    projects: [
      {
        id: '1',
        name: 'E-commerce Platform',
        description: 'Full-stack e-commerce solution',
        technologies: ['React', 'Node.js', 'MongoDB'],
        url: 'https://example.com',
        startDate: '2022-01-01',
        endDate: '2022-06-01',
      },
    ],
    certifications: [],
    languages: [],
    volunteerWork: [],
  };

  describe('validateStep', () => {
    describe('personal step validation', () => {
      it('should pass validation with valid personal info', () => {
        const result = validateStep('personal', mockCVData);

        expect(result.isValid).toBe(true);
        expect(result.errors).toEqual({});
      });

      it('should fail validation when full name is empty', () => {
        const invalidData = {
          ...mockCVData,
          personalInfo: { ...mockCVData.personalInfo, fullName: '' },
        };

        const result = validateStep('personal', invalidData);

        expect(result.isValid).toBe(false);
        expect(result.errors.fullName).toBe('Full name is required');
      });

      it('should fail validation when full name is only whitespace', () => {
        const invalidData = {
          ...mockCVData,
          personalInfo: { ...mockCVData.personalInfo, fullName: '   ' },
        };

        const result = validateStep('personal', invalidData);

        expect(result.isValid).toBe(false);
        expect(result.errors.fullName).toBe('Full name is required');
      });

      it('should fail validation when email is empty', () => {
        const invalidData = {
          ...mockCVData,
          personalInfo: { ...mockCVData.personalInfo, email: '' },
        };

        const result = validateStep('personal', invalidData);

        expect(result.isValid).toBe(false);
        expect(result.errors.email).toBe('Email is required');
      });

      it('should fail validation when email is invalid', () => {
        const invalidData = {
          ...mockCVData,
          personalInfo: { ...mockCVData.personalInfo, email: 'invalid-email' },
        };

        const result = validateStep('personal', invalidData);

        expect(result.isValid).toBe(false);
        expect(result.errors.email).toBe('Email is invalid');
      });

      it('should validate email format correctly', () => {
        const validEmails = [
          'test@example.com',
          'user.name@domain.co.uk',
          'user+tag@example.org',
          'user_name@example.io',
        ];

        const invalidEmails = [
          'invalid-email',
          '@example.com',
          'test@',
          'test.com',
          'test@.com',
        ];

        validEmails.forEach(email => {
          const data = {
            ...mockCVData,
            personalInfo: { ...mockCVData.personalInfo, email },
          };
          const result = validateStep('personal', data);
          expect(result.errors.email).toBeUndefined();
        });

        invalidEmails.forEach(email => {
          const data = {
            ...mockCVData,
            personalInfo: { ...mockCVData.personalInfo, email },
          };
          const result = validateStep('personal', data);
          expect(result.errors.email).toBe('Email is invalid');
        });
      });

      it('should fail validation when phone is empty', () => {
        const invalidData = {
          ...mockCVData,
          personalInfo: { ...mockCVData.personalInfo, phone: '' },
        };

        const result = validateStep('personal', invalidData);

        expect(result.isValid).toBe(false);
        expect(result.errors.phone).toBe('Phone number is required');
      });

      it('should fail validation when address is empty', () => {
        const invalidData = {
          ...mockCVData,
          personalInfo: { ...mockCVData.personalInfo, address: '' },
        };

        const result = validateStep('personal', invalidData);

        expect(result.isValid).toBe(false);
        expect(result.errors.address).toBe('Address is required');
      });

      it('should allow optional fields to be empty', () => {
        const data = {
          ...mockCVData,
          personalInfo: {
            ...mockCVData.personalInfo,
            linkedin: '',
            website: '',
            github: '',
          },
        };

        const result = validateStep('personal', data);

        expect(result.isValid).toBe(true);
        expect(result.errors).toEqual({});
      });
    });

    describe('summary step validation', () => {
      it('should pass validation with valid professional summary', () => {
        const result = validateStep('summary', mockCVData);

        expect(result.isValid).toBe(true);
        expect(result.errors).toEqual({});
      });

      it('should fail validation when professional summary is empty', () => {
        const invalidData = {
          ...mockCVData,
          professionalSummary: '',
        };

        const result = validateStep('summary', invalidData);

        expect(result.isValid).toBe(false);
        expect(result.errors.professionalSummary).toBe('Professional summary is required');
      });

      it('should fail validation when professional summary is too short', () => {
        const invalidData = {
          ...mockCVData,
          professionalSummary: 'Too short',
        };

        const result = validateStep('summary', invalidData);

        expect(result.isValid).toBe(false);
        expect(result.errors.professionalSummary).toBe('Summary must be at least 10 characters long');
      });

      it('should pass validation with exactly 10 characters', () => {
        const data = {
          ...mockCVData,
          professionalSummary: '1234567890',
        };

        const result = validateStep('summary', data);

        expect(result.isValid).toBe(true);
        expect(result.errors).toEqual({});
      });

      it('should allow whitespace-only content if it meets length requirement', () => {
        const data = {
          ...mockCVData,
          professionalSummary: '          1234567890          ',
        };

        const result = validateStep('summary', data);

        expect(result.isValid).toBe(true);
        expect(result.errors).toEqual({});
      });
    });

    describe('experience step validation', () => {
      it('should pass validation with work experience entries', () => {
        const result = validateStep('experience', mockCVData);

        expect(result.isValid).toBe(true);
        expect(result.errors).toEqual({});
      });

      it('should fail validation when no work experience entries', () => {
        const invalidData = {
          ...mockCVData,
          workExperience: [],
        };

        const result = validateStep('experience', invalidData);

        expect(result.isValid).toBe(false);
        expect(result.errors.workExperience).toBe('At least one work experience is required');
      });
    });

    describe('education step validation', () => {
      it('should pass validation with education entries', () => {
        const result = validateStep('education', mockCVData);

        expect(result.isValid).toBe(true);
        expect(result.errors).toEqual({});
      });

      it('should fail validation when no education entries', () => {
        const invalidData = {
          ...mockCVData,
          education: [],
        };

        const result = validateStep('education', invalidData);

        expect(result.isValid).toBe(false);
        expect(result.errors.education).toBe('At least one education entry is required');
      });
    });

    describe('skills step validation', () => {
      it('should pass validation with skills entries', () => {
        const result = validateStep('skills', mockCVData);

        expect(result.isValid).toBe(true);
        expect(result.errors).toEqual({});
      });

      it('should fail validation when no skills entries', () => {
        const invalidData = {
          ...mockCVData,
          skills: [],
        };

        const result = validateStep('skills', invalidData);

        expect(result.isValid).toBe(false);
        expect(result.errors.skills).toBe('At least one skill is required');
      });
    });

    describe('unknown step validation', () => {
      it('should return valid result for unknown steps', () => {
        const result = validateStep('unknown', mockCVData);

        expect(result.isValid).toBe(true);
        expect(result.errors).toEqual({});
      });
    });

    describe('performance testing', () => {
      it('should validate quickly even with large datasets', () => {
        const largeData = {
          ...mockCVData,
          workExperience: Array.from({ length: 100 }, (_, i) => ({
            id: i.toString(),
            jobTitle: `Job ${i}`,
            company: `Company ${i}`,
            location: `Location ${i}`,
            startDate: '2020-01-01',
            endDate: '2023-01-01',
            description: `Description ${i}`,
            achievements: [`Achievement ${i}`],
          })),
          education: Array.from({ length: 50 }, (_, i) => ({
            id: i.toString(),
            degree: `Degree ${i}`,
            field: `Field ${i}`,
            institution: `Institution ${i}`,
            location: `Location ${i}`,
            graduationDate: '2019-05-01',
            gpa: '3.8',
          })),
          skills: Array.from({ length: 200 }, (_, i) => ({
            id: i.toString(),
            name: `Skill ${i}`,
            level: 'Advanced',
          })),
        };

        const start = performance.now();
        const result = validateStep('experience', largeData);
        const end = performance.now();

        expect(result.isValid).toBe(true);
        expect(end - start).toBeLessThan(10); // Should complete in under 10ms
      });

      it('should handle multiple validation calls efficiently', () => {
        const iterations = 1000;
        const start = performance.now();

        for (let i = 0; i < iterations; i++) {
          validateStep('personal', mockCVData);
        }

        const end = performance.now();
        const avgTime = (end - start) / iterations;

        expect(avgTime).toBeLessThan(0.1); // Should be very fast per validation
      });
    });

    describe('edge cases', () => {
      it('should handle undefined values gracefully', () => {
        const undefinedData = {
          ...mockCVData,
          personalInfo: {
            ...mockCVData.personalInfo,
            fullName: undefined as unknown as string,
            email: undefined as unknown as string,
          },
        };

        const result = validateStep('personal', undefinedData);

        expect(result.isValid).toBe(false);
        expect(result.errors.fullName).toBe('Full name is required');
        expect(result.errors.email).toBe('Email is required');
      });

      it('should handle null values gracefully', () => {
        const nullData = {
          ...mockCVData,
          personalInfo: {
            ...mockCVData.personalInfo,
            fullName: null as unknown as string,
            email: null as unknown as string,
          },
        };

        const result = validateStep('personal', nullData);

        expect(result.isValid).toBe(false);
        expect(result.errors.fullName).toBe('Full name is required');
        expect(result.errors.email).toBe('Email is required');
      });

      it('should handle non-string values gracefully', () => {
        const nonStringData = {
          ...mockCVData,
          personalInfo: {
            ...mockCVData.personalInfo,
            fullName: 123 as unknown as string,
            email: 456 as unknown as string,
          },
        };

        const result = validateStep('personal', nonStringData);

        expect(result.isValid).toBe(false);
        expect(result.errors.fullName).toBe('Full name is required');
        expect(result.errors.email).toBe('Email is required');
      });
    });
  });

  describe('ValidationResult interface', () => {
    it('should create valid ValidationResult object', () => {
      const result: ValidationResult = {
        isValid: true,
        errors: {},
      };

      expect(result.isValid).toBe(true);
      expect(Object.keys(result.errors)).toHaveLength(0);
    });

    it('should create invalid ValidationResult object', () => {
      const result: ValidationResult = {
        isValid: false,
        errors: {
          fullName: 'Full name is required',
          email: 'Email is required',
        },
      };

      expect(result.isValid).toBe(false);
      expect(result.errors.fullName).toBe('Full name is required');
      expect(result.errors.email).toBe('Email is required');
      expect(Object.keys(result.errors)).toHaveLength(2);
    });
  });
});