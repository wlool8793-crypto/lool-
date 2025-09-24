import { z } from 'zod';
import { ValidationError } from '../types/common';

export class ValidationUtils {
  static validateEmail(email: string): boolean {
    const emailSchema = z.string().email();
    try {
      emailSchema.parse(email);
      return true;
    } catch {
      return false;
    }
  }

  static validatePhone(phone: string): boolean {
    const phoneSchema = z.string().regex(/^[+]?[\d\s\-()]{10,}$/);
    try {
      phoneSchema.parse(phone);
      return true;
    } catch {
      return false;
    }
  }

  static validateUrl(url: string): boolean {
    const urlSchema = z.string().url();
    try {
      urlSchema.parse(url);
      return true;
    } catch {
      return false;
    }
  }

  static validateAge(age: number, minAge: number = 18, maxAge: number = 100): boolean {
    return age >= minAge && age <= maxAge;
  }

  static validateRequired(value: string): boolean {
    return value.trim().length > 0;
  }

  static validateLength(value: string, min: number, max: number): boolean {
    return value.length >= min && value.length <= max;
  }

  static validateDate(dateString: string): boolean {
    const dateSchema = z.string().regex(/^\d{4}-\d{2}-\d{2}$/);
    try {
      dateSchema.parse(dateString);
      const date = new Date(dateString);
      return !isNaN(date.getTime());
    } catch {
      return false;
    }
  }

  static validateYear(year: string): boolean {
    const currentYear = new Date().getFullYear();
    const yearSchema = z.string().regex(/^\d{4}$/);
    try {
      yearSchema.parse(year);
      const yearNum = parseInt(year);
      return yearNum >= 1900 && yearNum <= currentYear + 10;
    } catch {
      return false;
    }
  }

  static validatePercentage(percentage: string): boolean {
    const percentageSchema = z.string().regex(/^(100|[1-9]?\d)%?$/);
    try {
      percentageSchema.parse(percentage);
      return true;
    } catch {
      return false;
    }
  }

  static validateGPA(gpa: string): boolean {
    const gpaSchema = z.string().regex(/^[0-4](\.\d{1,2})?$/);
    try {
      gpaSchema.parse(gpa);
      return true;
    } catch {
      return false;
    }
  }

  static validateFileExtension(filename: string, allowedExtensions: string[]): boolean {
    const extension = filename.split('.').pop()?.toLowerCase();
    return extension ? allowedExtensions.includes(extension) : false;
  }

  static validateFileSize(fileSize: number, maxSizeInMB: number): boolean {
    return fileSize <= maxSizeInMB * 1024 * 1024;
  }

  static validatePassword(password: string): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (password.length < 8) {
      errors.push('Password must be at least 8 characters long');
    }

    if (!/[A-Z]/.test(password)) {
      errors.push('Password must contain at least one uppercase letter');
    }

    if (!/[a-z]/.test(password)) {
      errors.push('Password must contain at least one lowercase letter');
    }

    if (!/[0-9]/.test(password)) {
      errors.push('Password must contain at least one number');
    }

    if (!/[!@#$%^&*]/.test(password)) {
      errors.push('Password must contain at least one special character');
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  static sanitizeInput(input: string): string {
    return input
      .replace(/<[^>]*>/g, '') // Remove HTML tags
      .replace(/javascript:/gi, '') // Remove JavaScript protocols
      .replace(/on\w+\s*=/gi, '') // Remove event handlers
      .trim();
  }

  static formatValidationErrors(errors: z.ZodIssue[]): ValidationError[] {
    return errors.map(error => ({
      field: error.path.join('.'),
      message: error.message,
      code: 'validation_error'
    }));
  }

  static validateForm<T>(schema: z.ZodSchema<T>, data: T): { isValid: boolean; errors: ValidationError[] } {
    try {
      schema.parse(data);
      return { isValid: true, errors: [] };
    } catch (error) {
      if (error instanceof z.ZodError) {
        return {
          isValid: false,
          errors: this.formatValidationErrors(error.issues)
        };
      }
      return {
        isValid: false,
        errors: [{ field: 'unknown', message: 'Unknown validation error', code: 'unknown_error' }]
      };
    }
  }

  static validateStep<T>(stepSchema: z.ZodSchema<T>, data: Partial<T>): { isValid: boolean; errors: ValidationError[] } {
    try {
      stepSchema.parse(data);
      return { isValid: true, errors: [] };
    } catch (error) {
      if (error instanceof z.ZodError) {
        return {
          isValid: false,
          errors: this.formatValidationErrors(error.issues)
        };
      }
      return {
        isValid: false,
        errors: [{ field: 'unknown', message: 'Unknown validation error', code: 'unknown_error' }]
      };
    }
  }

  static validateRequiredFields(fields: Record<string, any>, requiredFields: string[]): ValidationError[] {
    const errors: ValidationError[] = [];

    requiredFields.forEach(field => {
      const value = fields[field];
      if (!value || (typeof value === 'string' && value.trim() === '')) {
        errors.push({
          field,
          message: `${field} is required`,
          code: 'required'
        });
      }
    });

    return errors;
  }

  static validateField<T>(field: string, value: T, validators: ((val: T) => boolean)[]): ValidationError[] {
    const errors: ValidationError[] = [];

    validators.forEach((validator, index) => {
      if (!validator(value)) {
        errors.push({
          field,
          message: `Field ${field} failed validation ${index + 1}`,
          code: `validation_${index + 1}`
        });
      }
    });

    return errors;
  }
}