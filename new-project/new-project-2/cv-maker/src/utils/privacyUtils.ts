import {
  PrivacySettings,
  FieldVisibilitySettings,
  PrivacyLevel,
  DataField,
  PrivacyAuditLog,
  DataMaskingRule
} from '../types/security';

export class PrivacyUtils {
  private static readonly DEFAULT_PRIVACY_LEVELS: PrivacyLevel[] = [
    {
      level: 'public',
      description: 'Visible to everyone',
      accessibleFields: ['fullName', 'headline', 'summary', 'skills', 'education', 'experience']
    },
    {
      level: 'restricted',
      description: 'Visible to registered users',
      accessibleFields: ['fullName', 'email', 'phone', 'address', 'occupation', 'company']
    },
    {
      level: 'private',
      description: 'Visible only to you',
      accessibleFields: ['fullName', 'email', 'phone', 'address', 'all_personal_data']
    },
    {
      level: 'family',
      description: 'Visible to family members',
      accessibleFields: ['fullName', 'email', 'phone', 'address', 'family_info', 'personal_details']
    }
  ];

  private static readonly DATA_FIELDS: DataField[] = [
    {
      name: 'fullName',
      label: 'Full Name',
      type: 'personal',
      defaultValue: 'public',
      required: true,
      sensitive: false
    },
    {
      name: 'email',
      label: 'Email Address',
      type: 'contact',
      defaultValue: 'contacts',
      required: true,
      sensitive: true
    },
    {
      name: 'phone',
      label: 'Phone Number',
      type: 'contact',
      defaultValue: 'contacts',
      required: false,
      sensitive: true
    },
    {
      name: 'address',
      label: 'Address',
      type: 'personal',
      defaultValue: 'private',
      required: false,
      sensitive: true
    },
    {
      name: 'dateOfBirth',
      label: 'Date of Birth',
      type: 'personal',
      defaultValue: 'private',
      required: false,
      sensitive: true
    },
    {
      name: 'age',
      label: 'Age',
      type: 'personal',
      defaultValue: 'public',
      required: false,
      sensitive: false
    },
    {
      name: 'gender',
      label: 'Gender',
      type: 'personal',
      defaultValue: 'private',
      required: false,
      sensitive: true
    },
    {
      name: 'nationality',
      label: 'Nationality',
      type: 'personal',
      defaultValue: 'public',
      required: false,
      sensitive: false
    },
    {
      name: 'religion',
      label: 'Religion',
      type: 'personal',
      defaultValue: 'private',
      required: false,
      sensitive: true
    },
    {
      name: 'caste',
      label: 'Caste',
      type: 'sensitive',
      defaultValue: 'family',
      required: false,
      sensitive: true
    },
    {
      name: 'occupation',
      label: 'Occupation',
      type: 'professional',
      defaultValue: 'public',
      required: false,
      sensitive: false
    },
    {
      name: 'company',
      label: 'Company',
      type: 'professional',
      defaultValue: 'public',
      required: false,
      sensitive: false
    },
    {
      name: 'income',
      label: 'Income',
      type: 'professional',
      defaultValue: 'private',
      required: false,
      sensitive: true
    },
    {
      name: 'familyType',
      label: 'Family Type',
      type: 'family',
      defaultValue: 'family',
      required: false,
      sensitive: false
    },
    {
      name: 'horoscope',
      label: 'Horoscope',
      type: 'sensitive',
      defaultValue: 'family',
      required: false,
      sensitive: true
    }
  ];

  private static readonly MASKING_RULES: DataMaskingRule[] = [
    {
      id: 'email_mask',
      fieldName: 'email',
      pattern: '(.{2}).*(@.*)',
      replacement: '$1***$2',
      applyTo: 'unauthorized'
    },
    {
      id: 'phone_mask',
      fieldName: 'phone',
      pattern: '(.{3}).*([0-9]{4})',
      replacement: '$1****$2',
      applyTo: 'unauthorized'
    },
    {
      id: 'address_mask',
      fieldName: 'address',
      pattern: '(.*?),.*',
      replacement: '$1, ***',
      applyTo: 'unauthorized'
    }
  ];

  static createDefaultPrivacySettings(userId: string): PrivacySettings {
    return {
      id: this.generatePrivacyId(),
      userId,
      documentType: 'cv',
      profileVisibility: 'private',
      fieldVisibility: this.createDefaultFieldVisibility(),
      contactVisibility: this.createDefaultContactVisibility(),
      photoVisibility: this.createDefaultPhotoVisibility(),
      dataRetention: this.createDefaultDataRetention(),
      sharingPermissions: this.createDefaultSharingPermissions(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
  }

  static canAccessField(
    fieldName: string,
    userRole: string,
    privacySettings: PrivacySettings,
    userRelationship: string = 'public'
  ): boolean {
    const field = this.DATA_FIELDS.find(f => f.name === fieldName);
    if (!field) return false;

    const fieldVisibility = this.getFieldVisibility(fieldName, privacySettings);

    switch (fieldVisibility) {
      case 'public':
        return true;
      case 'contacts':
        return ['contacts', 'family'].includes(userRelationship);
      case 'family':
        return userRelationship === 'family';
      case 'private':
        return userRole === 'admin' || userRole === 'owner';
      default:
        return false;
    }
  }

  static maskSensitiveData(
    data: Record<string, any>,
    userRole: string,
    userRelationship: string = 'public'
  ): Record<string, any> {
    const maskedData = { ...data };

    this.MASKING_RULES.forEach(rule => {
      if (rule.applyTo === 'unauthorized' && userRelationship === 'public') {
        if (maskedData[rule.fieldName]) {
          const regex = new RegExp(rule.pattern);
          maskedData[rule.fieldName] = maskedData[rule.fieldName].replace(regex, rule.replacement);
        }
      }
    });

    return maskedData;
  }

  static filterVisibleFields(
    data: Record<string, any>,
    userRole: string,
    privacySettings: PrivacySettings,
    userRelationship: string = 'public'
  ): Record<string, any> {
    const filteredData: Record<string, any> = {};

    Object.keys(data).forEach(fieldName => {
      if (this.canAccessField(fieldName, userRole, privacySettings, userRelationship)) {
        filteredData[fieldName] = data[fieldName];
      }
    });

    return this.maskSensitiveData(filteredData, userRole, userRelationship);
  }

  static logPrivacyAction(
    userId: string,
    action: PrivacyAuditLog['action'],
    details: Record<string, any>,
    ipAddress?: string,
    userAgent?: string,
    sessionId?: string
  ): PrivacyAuditLog {
    return {
      id: this.generatePrivacyId(),
      userId,
      action,
      details,
      timestamp: new Date().toISOString(),
      ipAddress,
      userAgent,
      sessionId
    };
  }

  static validatePrivacySettings(settings: PrivacySettings): boolean {
    if (!settings.userId || !settings.documentType) return false;

    // Validate profile visibility
    if (!['public', 'private', 'unlisted', 'restricted'].includes(settings.profileVisibility)) {
      return false;
    }

    // Validate field visibility
    if (!this.validateFieldVisibility(settings.fieldVisibility)) {
      return false;
    }

    return true;
  }

  static exportPrivacyData(userId: string, privacySettings: PrivacySettings): any {
    return {
      userId,
      privacySettings,
      dataFields: this.DATA_FIELDS,
      maskingRules: this.MASKING_RULES,
      privacyLevels: this.DEFAULT_PRIVACY_LEVELS,
      exportedAt: new Date().toISOString()
    };
  }

  static getFieldVisibility(fieldName: string, privacySettings: PrivacySettings): string {
    const [category, field] = fieldName.split('.');

    switch (category) {
      case 'personalInfo':
        return privacySettings.fieldVisibility.personalInfo[field as keyof typeof privacySettings.fieldVisibility.personalInfo];
      case 'professionalInfo':
        return privacySettings.fieldVisibility.professionalInfo[field as keyof typeof privacySettings.fieldVisibility.professionalInfo];
      case 'familyInfo':
        return privacySettings.fieldVisibility.familyInfo[field as keyof typeof privacySettings.fieldVisibility.familyInfo];
      case 'sensitiveInfo':
        return privacySettings.fieldVisibility.sensitiveInfo[field as keyof typeof privacySettings.fieldVisibility.sensitiveInfo];
      default:
        return 'private';
    }
  }

  static getAccessibleFields(
    privacyLevel: string,
    privacySettings: PrivacySettings
  ): string[] {
    const level = this.DEFAULT_PRIVACY_LEVELS.find(l => l.level === privacyLevel);
    return level ? level.accessibleFields : [];
  }

  static generatePrivacyReport(userId: string, privacySettings: PrivacySettings): any {
    return {
      userId,
      profileVisibility: privacySettings.profileVisibility,
      publicFields: this.getPublicFields(privacySettings),
      privateFields: this.getPrivateFields(privacySettings),
      sensitiveFields: this.getSensitiveFields(privacySettings),
      dataRetentionSettings: privacySettings.dataRetention,
      sharingPermissions: privacySettings.sharingPermissions,
      generatedAt: new Date().toISOString()
    };
  }

  private static createDefaultFieldVisibility(): FieldVisibilitySettings {
    return {
      personalInfo: {
        fullName: 'public',
        email: 'contacts',
        phone: 'contacts',
        address: 'private',
        dateOfBirth: 'private',
        age: 'public',
        gender: 'private',
        nationality: 'public',
        religion: 'private'
      },
      professionalInfo: {
        occupation: 'public',
        company: 'public',
        income: 'private',
        education: 'public',
        skills: 'public',
        experience: 'public'
      },
      familyInfo: {
        familyType: 'family',
        familyStatus: 'family',
        parentsInfo: 'family',
        siblingsInfo: 'family',
        familyLocation: 'family'
      },
      sensitiveInfo: {
        caste: 'family',
        subCaste: 'family',
        horoscope: 'family',
        healthInfo: 'private',
        disability: 'private'
      }
    };
  }

  private static createDefaultContactVisibility() {
    return {
      showEmail: false,
      showPhone: false,
      showAddress: false,
      showWhatsapp: false,
      allowEmailContact: true,
      allowPhoneContact: true,
      allowMessages: true,
      contactRequestRequired: true,
      maxContactsPerDay: 10
    };
  }

  private static createDefaultPhotoVisibility() {
    return {
      profilePhoto: 'public',
      additionalPhotos: 'contacts',
      allowPhotoDownload: false,
      photoWatermark: true,
      watermarkText: 'Confidential',
      photoExpiration: {
        enabled: false,
        daysUntilExpiration: 30,
        autoDelete: false
      },
      photoAccessLog: true
    };
  }

  private static createDefaultDataRetention() {
    return {
      autoDeleteInactive: false,
      inactivityPeriod: 365,
      deletePhotos: true,
      deleteDocuments: true,
      deleteContacts: true,
      exportBeforeDelete: true,
      notificationBeforeDelete: true
    };
  }

  private static createDefaultSharingPermissions() {
    return {
      allowSharing: true,
      shareWithContacts: true,
      shareWithFamily: true,
      requirePassword: true,
      timeLimited: true,
      maxShareDuration: 24,
      trackShares: true,
      revokeAccess: true
    };
  }

  private static validateFieldVisibility(fieldVisibility: FieldVisibilitySettings): boolean {
    const validLevels = ['public', 'private', 'contacts', 'family'];

    // Check personalInfo
    Object.values(fieldVisibility.personalInfo).forEach(level => {
      if (!validLevels.includes(level)) return false;
    });

    // Check professionalInfo
    Object.values(fieldVisibility.professionalInfo).forEach(level => {
      if (!validLevels.includes(level)) return false;
    });

    // Check familyInfo
    Object.values(fieldVisibility.familyInfo).forEach(level => {
      if (!validLevels.includes(level)) return false;
    });

    // Check sensitiveInfo
    Object.values(fieldVisibility.sensitiveInfo).forEach(level => {
      if (!validLevels.includes(level)) return false;
    });

    return true;
  }

  private static generatePrivacyId(): string {
    return `privacy_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private static getPublicFields(privacySettings: PrivacySettings): string[] {
    return this.DATA_FIELDS
      .filter(field => {
        const visibility = this.getFieldVisibility(field.name, privacySettings);
        return visibility === 'public';
      })
      .map(field => field.name);
  }

  private static getPrivateFields(privacySettings: PrivacySettings): string[] {
    return this.DATA_FIELDS
      .filter(field => {
        const visibility = this.getFieldVisibility(field.name, privacySettings);
        return visibility === 'private';
      })
      .map(field => field.name);
  }

  private static getSensitiveFields(privacySettings: PrivacySettings): string[] {
    return this.DATA_FIELDS
      .filter(field => field.sensitive)
      .map(field => field.name);
  }
}