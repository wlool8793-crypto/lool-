export interface AppSettings {
  language: string;
  theme: 'light' | 'dark' | 'auto';
  autoSave: boolean;
  notifications: boolean;
  dateFormat: string;
  currency: string;
  timezone: string;
}

export interface FileUploadConfig {
  maxSize: number;
  allowedTypes: string[];
  maxWidth: number;
  maxHeight: number;
  quality: number;
  maxFiles: number;
}

export interface ImageCropConfig {
  aspectRatio?: number;
  width: number;
  height: number;
  x: number;
  y: number;
}

export interface PDFConfig {
  quality: number;
  margins: string;
  dpi: number;
  format: 'A4' | 'A3' | 'Letter';
  orientation: 'portrait' | 'landscape';
}

export interface ExportOptions {
  format: 'pdf' | 'docx' | 'html';
  template: string;
  includePhoto: boolean;
  watermark?: string;
  password?: string;
  encryption: boolean;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

export interface FormState {
  isSubmitting: boolean;
  errors: ValidationError[];
  isValid: boolean;
  touched: Set<string>;
}

export interface TemplateConfig {
  id: string;
  name: string;
  category: 'professional' | 'marriage';
  preview: string;
  description: string;
  features: string[];
  isPremium: boolean;
}

export type AppLanguage = 'en' | 'hi' | 'ur' | 'ar' | 'fr' | 'es' | 'de' | 'zh' | 'ja' | 'pt';
export type AppTheme = 'light' | 'dark' | 'auto';
export type DocumentType = 'cv' | 'marriage';
export type ExportFormat = 'pdf' | 'docx' | 'html';
export type TemplateCategory = 'professional' | 'marriage';