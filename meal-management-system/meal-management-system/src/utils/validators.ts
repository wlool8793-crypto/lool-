/**
 * Validation utility functions for the Hostel Meal Management System
 * Provides validators for common input types including email, phone, amounts, etc.
 */

/**
 * Validation result interface
 */
export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

/**
 * Email validation regex pattern
 * Matches standard email format: local@domain.tld
 */
const EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

/**
 * Phone validation regex pattern
 * Matches 10-digit Indian phone numbers
 */
const PHONE_REGEX = /^[6-9]\d{9}$/;

/**
 * Roll number validation regex pattern
 * Matches alphanumeric roll numbers (e.g., "21BCS001", "2021/BCS/001")
 */
const ROLL_NUMBER_REGEX = /^[A-Z0-9\/\-]+$/i;

/**
 * Validate email address
 *
 * @param email - Email address to validate
 * @returns Validation result with error message if invalid
 *
 * @example
 * ```typescript
 * validateEmail('user@example.com'); // { isValid: true }
 * validateEmail('invalid-email'); // { isValid: false, error: 'Invalid email format' }
 * validateEmail(''); // { isValid: false, error: 'Email is required' }
 * ```
 */
export const validateEmail = (email: string): ValidationResult => {
  // Check if email is provided
  if (!email || email.trim() === '') {
    return {
      isValid: false,
      error: 'Email is required',
    };
  }

  // Trim whitespace
  const trimmedEmail = email.trim();

  // Check format
  if (!EMAIL_REGEX.test(trimmedEmail)) {
    return {
      isValid: false,
      error: 'Invalid email format',
    };
  }

  // Check length
  if (trimmedEmail.length > 255) {
    return {
      isValid: false,
      error: 'Email is too long (maximum 255 characters)',
    };
  }

  return { isValid: true };
};

/**
 * Validate phone number (10 digits, Indian format)
 *
 * @param phone - Phone number to validate
 * @returns Validation result with error message if invalid
 *
 * @example
 * ```typescript
 * validatePhone('9876543210'); // { isValid: true }
 * validatePhone('123456789'); // { isValid: false, error: 'Phone number must be exactly 10 digits' }
 * validatePhone('0123456789'); // { isValid: false, error: 'Phone number must start with 6-9' }
 * ```
 */
export const validatePhone = (phone: string): ValidationResult => {
  // Check if phone is provided
  if (!phone || phone.trim() === '') {
    return {
      isValid: false,
      error: 'Phone number is required',
    };
  }

  // Remove all non-digit characters
  const cleanedPhone = phone.replace(/\D/g, '');

  // Check length
  if (cleanedPhone.length !== 10) {
    return {
      isValid: false,
      error: 'Phone number must be exactly 10 digits',
    };
  }

  // Check format (must start with 6-9)
  if (!PHONE_REGEX.test(cleanedPhone)) {
    return {
      isValid: false,
      error: 'Phone number must start with 6-9',
    };
  }

  return { isValid: true };
};

/**
 * Validate amount (must be positive number)
 *
 * @param amount - Amount to validate (number or string)
 * @param options - Validation options
 * @returns Validation result with error message if invalid
 *
 * @example
 * ```typescript
 * validateAmount(100); // { isValid: true }
 * validateAmount(-50); // { isValid: false, error: 'Amount must be positive' }
 * validateAmount('abc'); // { isValid: false, error: 'Amount must be a valid number' }
 * validateAmount(1000000, { max: 100000 }); // { isValid: false, error: 'Amount exceeds maximum...' }
 * ```
 */
export const validateAmount = (
  amount: number | string,
  options?: {
    min?: number;
    max?: number;
    allowZero?: boolean;
  }
): ValidationResult => {
  const { min = 0, max, allowZero = false } = options || {};

  // Check if amount is provided
  if (amount === undefined || amount === null || amount === '') {
    return {
      isValid: false,
      error: 'Amount is required',
    };
  }

  // Convert to number if string
  const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount;

  // Check if valid number
  if (isNaN(numAmount)) {
    return {
      isValid: false,
      error: 'Amount must be a valid number',
    };
  }

  // Check if zero is allowed
  if (!allowZero && numAmount === 0) {
    return {
      isValid: false,
      error: 'Amount must be greater than zero',
    };
  }

  // Check if positive
  if (numAmount < 0) {
    return {
      isValid: false,
      error: 'Amount must be positive',
    };
  }

  // Check minimum
  if (numAmount < min) {
    return {
      isValid: false,
      error: `Amount must be at least ${min}`,
    };
  }

  // Check maximum
  if (max !== undefined && numAmount > max) {
    return {
      isValid: false,
      error: `Amount exceeds maximum of ${max}`,
    };
  }

  return { isValid: true };
};

/**
 * Validate required field (checks if value is provided and not empty)
 *
 * @param value - Value to validate
 * @param fieldName - Name of the field (for error message)
 * @returns Validation result with error message if invalid
 *
 * @example
 * ```typescript
 * validateRequired('John', 'Name'); // { isValid: true }
 * validateRequired('', 'Name'); // { isValid: false, error: 'Name is required' }
 * validateRequired('   ', 'Name'); // { isValid: false, error: 'Name is required' }
 * ```
 */
export const validateRequired = (
  value: any,
  fieldName: string = 'This field'
): ValidationResult => {
  // Check for null or undefined
  if (value === null || value === undefined) {
    return {
      isValid: false,
      error: `${fieldName} is required`,
    };
  }

  // Check for empty string
  if (typeof value === 'string' && value.trim() === '') {
    return {
      isValid: false,
      error: `${fieldName} is required`,
    };
  }

  // Check for empty array
  if (Array.isArray(value) && value.length === 0) {
    return {
      isValid: false,
      error: `${fieldName} is required`,
    };
  }

  return { isValid: true };
};

/**
 * Validate password strength
 *
 * @param password - Password to validate
 * @param options - Validation options
 * @returns Validation result with error message if invalid
 *
 * @example
 * ```typescript
 * validatePassword('StrongPass123!'); // { isValid: true }
 * validatePassword('weak'); // { isValid: false, error: 'Password must be at least 8 characters' }
 * ```
 */
export const validatePassword = (
  password: string,
  options?: {
    minLength?: number;
    requireUppercase?: boolean;
    requireLowercase?: boolean;
    requireNumbers?: boolean;
    requireSpecialChars?: boolean;
  }
): ValidationResult => {
  const {
    minLength = 8,
    requireUppercase = true,
    requireLowercase = true,
    requireNumbers = true,
    requireSpecialChars = false,
  } = options || {};

  // Check if password is provided
  if (!password) {
    return {
      isValid: false,
      error: 'Password is required',
    };
  }

  // Check minimum length
  if (password.length < minLength) {
    return {
      isValid: false,
      error: `Password must be at least ${minLength} characters`,
    };
  }

  // Check uppercase
  if (requireUppercase && !/[A-Z]/.test(password)) {
    return {
      isValid: false,
      error: 'Password must contain at least one uppercase letter',
    };
  }

  // Check lowercase
  if (requireLowercase && !/[a-z]/.test(password)) {
    return {
      isValid: false,
      error: 'Password must contain at least one lowercase letter',
    };
  }

  // Check numbers
  if (requireNumbers && !/\d/.test(password)) {
    return {
      isValid: false,
      error: 'Password must contain at least one number',
    };
  }

  // Check special characters
  if (requireSpecialChars && !/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    return {
      isValid: false,
      error: 'Password must contain at least one special character',
    };
  }

  return { isValid: true };
};

/**
 * Validate roll number
 *
 * @param rollNumber - Roll number to validate
 * @returns Validation result with error message if invalid
 *
 * @example
 * ```typescript
 * validateRollNumber('21BCS001'); // { isValid: true }
 * validateRollNumber('2021/BCS/001'); // { isValid: true }
 * validateRollNumber(''); // { isValid: false, error: 'Roll number is required' }
 * ```
 */
export const validateRollNumber = (rollNumber: string): ValidationResult => {
  // Check if roll number is provided
  if (!rollNumber || rollNumber.trim() === '') {
    return {
      isValid: false,
      error: 'Roll number is required',
    };
  }

  const trimmedRollNumber = rollNumber.trim();

  // Check format
  if (!ROLL_NUMBER_REGEX.test(trimmedRollNumber)) {
    return {
      isValid: false,
      error: 'Roll number can only contain letters, numbers, hyphens, and slashes',
    };
  }

  // Check length
  if (trimmedRollNumber.length < 3 || trimmedRollNumber.length > 20) {
    return {
      isValid: false,
      error: 'Roll number must be between 3 and 20 characters',
    };
  }

  return { isValid: true };
};

/**
 * Validate name (must contain only letters and spaces)
 *
 * @param name - Name to validate
 * @param fieldName - Name of the field (for error message)
 * @returns Validation result with error message if invalid
 *
 * @example
 * ```typescript
 * validateName('John Doe'); // { isValid: true }
 * validateName('John123'); // { isValid: false, error: 'Name can only contain letters...' }
 * ```
 */
export const validateName = (
  name: string,
  fieldName: string = 'Name'
): ValidationResult => {
  // Check if name is provided
  const requiredCheck = validateRequired(name, fieldName);
  if (!requiredCheck.isValid) {
    return requiredCheck;
  }

  const trimmedName = name.trim();

  // Check format (letters, spaces, hyphens, apostrophes)
  if (!/^[a-zA-Z\s'-]+$/.test(trimmedName)) {
    return {
      isValid: false,
      error: `${fieldName} can only contain letters, spaces, hyphens, and apostrophes`,
    };
  }

  // Check length
  if (trimmedName.length < 2) {
    return {
      isValid: false,
      error: `${fieldName} must be at least 2 characters`,
    };
  }

  if (trimmedName.length > 100) {
    return {
      isValid: false,
      error: `${fieldName} is too long (maximum 100 characters)`,
    };
  }

  return { isValid: true };
};

/**
 * Validate multiple fields at once
 *
 * @param validations - Object with field names and validation functions
 * @returns Object with validation results for each field
 *
 * @example
 * ```typescript
 * const results = validateMultiple({
 *   email: () => validateEmail(formData.email),
 *   phone: () => validatePhone(formData.phone),
 *   amount: () => validateAmount(formData.amount)
 * });
 *
 * if (!results.isValid) {
 *   console.log(results.errors); // { email: 'Invalid email format', ... }
 * }
 * ```
 */
export const validateMultiple = (
  validations: Record<string, () => ValidationResult>
): {
  isValid: boolean;
  errors: Record<string, string>;
} => {
  const errors: Record<string, string> = {};
  let isValid = true;

  for (const [field, validationFn] of Object.entries(validations)) {
    const result = validationFn();
    if (!result.isValid) {
      isValid = false;
      errors[field] = result.error || 'Invalid';
    }
  }

  return { isValid, errors };
};

/**
 * Sanitize string input (remove potentially harmful characters)
 *
 * @param input - String to sanitize
 * @returns Sanitized string
 *
 * @example
 * ```typescript
 * sanitizeInput('<script>alert("xss")</script>'); // 'scriptalert("xss")/script'
 * ```
 */
export const sanitizeInput = (input: string): string => {
  if (!input) return '';

  return input
    .trim()
    .replace(/[<>]/g, '') // Remove < and >
    .replace(/[^\w\s@.,\-'/]/gi, ''); // Keep only safe characters
};
