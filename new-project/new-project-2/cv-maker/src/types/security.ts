import { DocumentType } from './common';

export interface PrivacySettings {
  id: string;
  userId: string;
  documentType: DocumentType;
  profileVisibility: 'public' | 'private' | 'unlisted' | 'restricted';
  fieldVisibility: FieldVisibilitySettings;
  contactVisibility: ContactVisibilitySettings;
  photoVisibility: PhotoVisibilitySettings;
  dataRetention: DataRetentionSettings;
  sharingPermissions: SharingPermissions;
  createdAt: string;
  updatedAt: string;
}

export interface FieldVisibilitySettings {
  personalInfo: {
    fullName: 'public' | 'private' | 'contacts' | 'family';
    email: 'public' | 'private' | 'contacts' | 'family';
    phone: 'public' | 'private' | 'contacts' | 'family';
    address: 'public' | 'private' | 'contacts' | 'family';
    dateOfBirth: 'public' | 'private' | 'contacts' | 'family';
    age: 'public' | 'private' | 'contacts' | 'family';
    gender: 'public' | 'private' | 'contacts' | 'family';
    nationality: 'public' | 'private' | 'contacts' | 'family';
    religion: 'public' | 'private' | 'contacts' | 'family';
  };
  professionalInfo: {
    occupation: 'public' | 'private' | 'contacts' | 'family';
    company: 'public' | 'private' | 'contacts' | 'family';
    income: 'public' | 'private' | 'contacts' | 'family';
    education: 'public' | 'private' | 'contacts' | 'family';
    skills: 'public' | 'private' | 'contacts' | 'family';
    experience: 'public' | 'private' | 'contacts' | 'family';
  };
  familyInfo: {
    familyType: 'public' | 'private' | 'family';
    familyStatus: 'public' | 'private' | 'family';
    parentsInfo: 'public' | 'private' | 'family';
    siblingsInfo: 'public' | 'private' | 'family';
    familyLocation: 'public' | 'private' | 'family';
  };
  sensitiveInfo: {
    caste: 'private' | 'family';
    subCaste: 'private' | 'family';
    horoscope: 'private' | 'family';
    healthInfo: 'private' | 'family';
    disability: 'private' | 'family';
  };
}

export interface ContactVisibilitySettings {
  showEmail: boolean;
  showPhone: boolean;
  showAddress: boolean;
  showWhatsapp: boolean;
  allowEmailContact: boolean;
  allowPhoneContact: boolean;
  allowMessages: boolean;
  contactRequestRequired: boolean;
  maxContactsPerDay: number;
}

export interface PhotoVisibilitySettings {
  profilePhoto: 'public' | 'private' | 'contacts' | 'family';
  additionalPhotos: 'public' | 'private' | 'contacts' | 'family';
  allowPhotoDownload: boolean;
  photoWatermark: boolean;
  watermarkText?: string;
  photoExpiration: {
    enabled: boolean;
    daysUntilExpiration: number;
    autoDelete: boolean;
  };
  photoAccessLog: boolean;
}

export interface DataRetentionSettings {
  autoDeleteInactive: boolean;
  inactivityPeriod: number; // days
  deletePhotos: boolean;
  deleteDocuments: boolean;
  deleteContacts: boolean;
  exportBeforeDelete: boolean;
  notificationBeforeDelete: boolean;
}

export interface SharingPermissions {
  allowSharing: boolean;
  shareWithContacts: boolean;
  shareWithFamily: boolean;
  requirePassword: boolean;
  timeLimited: boolean;
  maxShareDuration: number; // hours
  trackShares: boolean;
  revokeAccess: boolean;
}

export interface PrivacyLevel {
  level: 'public' | 'restricted' | 'private' | 'family';
  description: string;
  accessibleFields: string[];
}

export interface DataField {
  name: string;
  label: string;
  type: 'personal' | 'contact' | 'professional' | 'family' | 'sensitive';
  defaultValue: 'public' | 'private' | 'contacts' | 'family';
  required: boolean;
  sensitive: boolean;
}

export interface PrivacyConsent {
  id: string;
  userId: string;
  consentType: 'data_collection' | 'data_sharing' | 'data_processing' | 'marketing' | 'analytics';
  title: string;
  description: string;
  version: string;
  granted: boolean;
  grantedAt?: string;
  revokedAt?: string;
  ipAddress?: string;
  userAgent?: string;
}

export interface PrivacyAuditLog {
  id: string;
  userId: string;
  action: 'privacy_settings_updated' | 'field_visibility_changed' | 'data_accessed' | 'data_shared' | 'consent_granted' | 'consent_revoked';
  details: Record<string, any>;
  timestamp: string;
  ipAddress?: string;
  userAgent?: string;
  sessionId?: string;
}

export interface DataMaskingRule {
  id: string;
  fieldName: string;
  pattern: string;
  replacement: string;
  condition?: (data: any) => boolean;
  applyTo: 'all' | 'unauthorized' | 'public';
}

export interface PrivacyComplianceReport {
  userId: string;
  reportType: 'data_access' | 'data_deletion' | 'data_portability' | 'consent_summary';
  generatedAt: string;
  data: any;
  format: 'json' | 'pdf' | 'csv';
}