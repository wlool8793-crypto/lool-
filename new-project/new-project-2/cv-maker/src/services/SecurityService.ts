import { PrivacyUtils } from '../utils/privacyUtils';
import { PhotoProtectionUtils } from '../utils/photoProtectionUtils';
import { AccessControlUtils } from '../utils/accessControlUtils';
import { EncryptionUtils } from '../utils/encryptionUtils';
import { SecureStorage } from '../utils/secureStorage';
import { SecureSharing } from '../utils/secureSharing';
import { AuthenticationUtils } from '../utils/authenticationUtils';
import { GDPRUtils } from '../utils/gdprUtils';
import { SecurityMonitoring } from '../utils/securityMonitoring';
import { ContentModeration } from '../utils/contentModeration';
import { SecurityFeatures } from '../utils/securityFeatures';

import {
  PrivacySettings,
  PhotoProtectionSettings,
  ShareConfig,
  AuthConfig,
  SecurityConfig
} from '../types/security';

export interface SecurityInitializationOptions {
  enablePrivacy: boolean;
  enablePhotoProtection: boolean;
  enableAccessControl: boolean;
  enableEncryption: boolean;
  enableSecureSharing: boolean;
  enableAuthentication: boolean;
  enableGDPR: boolean;
  enableMonitoring: boolean;
  enableContentModeration: boolean;
  enableSecurityFeatures: boolean;
}

export class SecurityService {
  private static isInitialized = false;
  private static initializationOptions: SecurityInitializationOptions = {
    enablePrivacy: true,
    enablePhotoProtection: true,
    enableAccessControl: true,
    enableEncryption: true,
    enableSecureSharing: true,
    enableAuthentication: true,
    enableGDPR: true,
    enableMonitoring: true,
    enableContentModeration: true,
    enableSecurityFeatures: true
  };

  static async initialize(options?: Partial<SecurityInitializationOptions>): Promise<void> {
    if (this.isInitialized) {
      console.warn('SecurityService is already initialized');
      return;
    }

    this.initializationOptions = { ...this.initializationOptions, ...options };

    try {
      // Initialize core security features first
      if (this.initializationOptions.enableEncryption) {
        await SecureStorage.initialize();
      }

      // Initialize authentication system
      if (this.initializationOptions.enableAuthentication) {
        await AuthenticationUtils.initialize();
      }

      // Initialize GDPR compliance
      if (this.initializationOptions.enableGDPR) {
        await GDPRUtils.initialize();
      }

      // Initialize content moderation
      if (this.initializationOptions.enableContentModeration) {
        await ContentModeration.initialize();
      }

      // Initialize security monitoring
      if (this.initializationOptions.enableMonitoring) {
        await SecurityMonitoring.initialize();
      }

      // Initialize security features
      if (this.initializationOptions.enableSecurityFeatures) {
        await SecurityFeatures.initialize();
      }

      this.isInitialized = true;
      console.log('SecurityService initialized successfully');

      // Log initialization event
      await this.logSecurityEvent('security_initialized', 'low', {
        enabledFeatures: Object.keys(this.initializationOptions).filter(key => this.initializationOptions[key as keyof SecurityInitializationOptions]),
        timestamp: new Date().toISOString()
      });

    } catch (error) {
      console.error('Failed to initialize SecurityService:', error);
      throw new Error('Security initialization failed');
    }
  }

  // Privacy Management
  static async createPrivacySettings(userId: string): Promise<PrivacySettings> {
    this.ensureInitialized();
    return PrivacyUtils.createDefaultPrivacySettings(userId);
  }

  static async canAccessField(
    fieldName: string,
    userRole: string,
    privacySettings: PrivacySettings,
    userRelationship: string = 'public'
  ): Promise<boolean> {
    this.ensureInitialized();
    return PrivacyUtils.canAccessField(fieldName, userRole, privacySettings, userRelationship);
  }

  static async filterVisibleFields(
    data: Record<string, any>,
    userRole: string,
    privacySettings: PrivacySettings,
    userRelationship: string = 'public'
  ): Promise<Record<string, any>> {
    this.ensureInitialized();
    return PrivacyUtils.filterVisibleFields(data, userRole, privacySettings, userRelationship);
  }

  // Photo Protection
  static async createSecurePhoto(
    file: File,
    settings: PhotoProtectionSettings,
    userId: string
  ) {
    this.ensureInitialized();
    return PhotoProtectionUtils.createSecurePhoto(file, settings, userId);
  }

  static async applyWatermark(imageElement: HTMLImageElement, watermarkConfig: any): Promise<string> {
    this.ensureInitialized();
    return PhotoProtectionUtils.applyWatermark(imageElement, watermarkConfig);
  }

  // Access Control
  static async checkAccess(check: any): Promise<any> {
    this.ensureInitialized();
    return AccessControlUtils.checkAccess(check);
  }

  static async grantPermission(
    userId: string,
    roleId: string,
    resourceId?: string,
    grantedBy: string,
    expiresAt?: string
  ): Promise<any> {
    this.ensureInitialized();
    return AccessControlUtils.grantPermission(userId, roleId, resourceId, grantedBy, expiresAt);
  }

  // Encryption
  static async encryptData(data: string, key: string): Promise<any> {
    this.ensureInitialized();
    return EncryptionUtils.encryptData(data, key);
  }

  static async decryptData(encryptedData: any, key: string): Promise<string> {
    this.ensureInitialized();
    return EncryptionUtils.decryptData(encryptedData, key);
  }

  // Secure Storage
  static async storeSecureData(key: string, value: any, expiresAt?: Date): Promise<void> {
    this.ensureInitialized();
    return SecureStorage.store(key, value, expiresAt);
  }

  static async retrieveSecureData<T>(key: string): Promise<T | null> {
    this.ensureInitialized();
    return SecureStorage.retrieve<T>(key);
  }

  // Secure Sharing
  static async createShare(
    documentId: string,
    documentName: string,
    createdBy: string,
    config: ShareConfig
  ): Promise<any> {
    this.ensureInitialized();
    return SecureSharing.createShare(documentId, documentName, createdBy, config);
  }

  static async validateShare(shareToken: string, password?: string): Promise<any> {
    this.ensureInitialized();
    return SecureSharing.validateShare(shareToken, password);
  }

  // Authentication
  static async register(request: any): Promise<any> {
    this.ensureInitialized();
    return AuthenticationUtils.register(request);
  }

  static async login(request: any): Promise<any> {
    this.ensureInitialized();
    return AuthenticationUtils.login(request);
  }

  static async logout(sessionId: string): Promise<boolean> {
    this.ensureInitialized();
    return AuthenticationUtils.logout(sessionId);
  }

  static async validateSession(sessionId: string): Promise<any> {
    this.ensureInitialized();
    return AuthenticationUtils.validateSession(sessionId);
  }

  // GDPR Compliance
  static async recordConsent(
    userId: string,
    consentType: any,
    granted: boolean,
    version?: string
  ): Promise<any> {
    this.ensureInitialized();
    return GDPRUtils.recordConsent(userId, consentType, granted, version);
  }

  static async createDataSubjectRequest(
    userId: string,
    requestType: any,
    requestData?: any
  ): Promise<any> {
    this.ensureInitialized();
    return GDPRUtils.createDataSubjectRequest(userId, requestType, requestData);
  }

  static async exportUserData(userId: string): Promise<any> {
    this.ensureInitialized();
    return GDPRUtils.exportUserData(userId);
  }

  // Security Monitoring
  static async logSecurityEvent(
    eventType: string,
    severity: 'low' | 'medium' | 'high' | 'critical',
    details: Record<string, any>
  ): Promise<void> {
    this.ensureInitialized();
    await SecurityMonitoring.logEvent(eventType, severity, details);
  }

  static async getSecurityMetrics(timeRange?: number): Promise<any> {
    this.ensureInitialized();
    return SecurityMonitoring.getSecurityMetrics(timeRange);
  }

  static async getSecurityAlerts(userId?: string): Promise<any> {
    this.ensureInitialized();
    return SecurityMonitoring.getSecurityAlerts(userId);
  }

  // Content Moderation
  static async moderateText(text: string, userId?: string): Promise<any> {
    this.ensureInitialized();
    return ContentModeration.moderateText(text, userId);
  }

  static async moderateImage(imageFile: File, userId?: string): Promise<any> {
    this.ensureInitialized();
    return ContentModeration.moderateImage(imageFile, userId);
  }

  static async reportContent(
    reporterId: string,
    contentType: any,
    contentId: string,
    reason: string,
    description: string,
    severity: any
  ): Promise<any> {
    this.ensureInitialized();
    return ContentModeration.reportContent(reporterId, contentType, contentId, reason, description, severity);
  }

  // Security Features
  static async getSecurityHeaders(): Promise<any> {
    this.ensureInitialized();
    return SecurityFeatures.getSecurityHeaders();
  }

  static async validateCSRFToken(token: string): Promise<boolean> {
    this.ensureInitialized();
    return SecurityFeatures.validateCSRFToken(token);
  }

  static async sanitizeInput(input: string, allowHtml?: boolean): Promise<string> {
    this.ensureInitialized();
    return SecurityFeatures.sanitizeInput(input, allowHtml);
  }

  static async checkRateLimit(identifier: string, endpoint: string): Promise<any> {
    this.ensureInitialized();
    return SecurityFeatures.checkRateLimit(identifier, endpoint);
  }

  // Utility Methods
  static async generateSecurityReport(): Promise<string> {
    this.ensureInitialized();

    const report = {
      timestamp: new Date().toISOString(),
      service: 'CV Maker Security Service',
      version: '1.0.0',
      initializedFeatures: Object.keys(this.initializationOptions).filter(key => this.initializationOptions[key as keyof SecurityInitializationOptions]),
      securityMetrics: await this.getSecurityMetrics(24),
      recommendations: [
        'Regular security audits',
        'Keep dependencies updated',
        'Monitor for new threats',
        'Educate users on security best practices'
      ],
      bestPractices: [
        'Use strong passwords',
        'Enable two-factor authentication',
        'Be cautious with sharing personal information',
        'Report suspicious activities'
      ]
    };

    return JSON.stringify(report, null, 2);
  }

  static async performSecurityHealthCheck(): Promise<{
    status: 'healthy' | 'warning' | 'critical';
    checks: Array<{ name: string; status: 'pass' | 'fail' | 'warning'; message?: string }>;
    score: number;
    recommendations: string[];
  }> {
    this.ensureInitialized();

    const checks = [];
    let score = 0;
    const totalChecks = 10;

    // Check encryption
    try {
      await EncryptionUtils.generateSecureToken(16);
      checks.push({ name: 'Encryption', status: 'pass' });
      score++;
    } catch (error) {
      checks.push({ name: 'Encryption', status: 'fail', message: 'Encryption not available' });
    }

    // Check secure storage
    try {
      await SecureStorage.store('health_check', 'test');
      const value = await SecureStorage.retrieve('health_check');
      if (value === 'test') {
        checks.push({ name: 'Secure Storage', status: 'pass' });
        score++;
      } else {
        checks.push({ name: 'Secure Storage', status: 'fail', message: 'Storage not working properly' });
      }
    } catch (error) {
      checks.push({ name: 'Secure Storage', status: 'fail', message: 'Storage initialization failed' });
    }

    // Check content moderation
    try {
      await ContentModeration.moderateText('test text');
      checks.push({ name: 'Content Moderation', status: 'pass' });
      score++;
    } catch (error) {
      checks.push({ name: 'Content Moderation', status: 'fail', message: 'Moderation service not available' });
    }

    // Check security monitoring
    try {
      await SecurityMonitoring.getSecurityMetrics();
      checks.push({ name: 'Security Monitoring', status: 'pass' });
      score++;
    } catch (error) {
      checks.push({ name: 'Security Monitoring', status: 'fail', message: 'Monitoring service not available' });
    }

    // Check authentication
    try {
      await AuthenticationUtils.initialize();
      checks.push({ name: 'Authentication', status: 'pass' });
      score++;
    } catch (error) {
      checks.push({ name: 'Authentication', status: 'fail', message: 'Authentication service not available' });
    }

    // Check GDPR compliance
    try {
      await GDPRUtils.initialize();
      checks.push({ name: 'GDPR Compliance', status: 'pass' });
      score++;
    } catch (error) {
      checks.push({ name: 'GDPR Compliance', status: 'fail', message: 'GDPR service not available' });
    }

    // Check secure sharing
    try {
      await SecureSharing.createShare('test', 'test', 'test', {
        permissions: 'view',
        allowResharing: false,
        requireAuthentication: true,
        notifyOnAccess: false
      });
      checks.push({ name: 'Secure Sharing', status: 'pass' });
      score++;
    } catch (error) {
      checks.push({ name: 'Secure Sharing', status: 'fail', message: 'Sharing service not available' });
    }

    // Check access control
    try {
      await AccessControlUtils.checkAccess({
        resourceId: 'test',
        resourceType: 'test',
        action: 'read',
        userId: 'test',
        userRole: 'user'
      });
      checks.push({ name: 'Access Control', status: 'pass' });
      score++;
    } catch (error) {
      checks.push({ name: 'Access Control', status: 'fail', message: 'Access control service not available' });
    }

    // Check privacy controls
    try {
      await PrivacyUtils.createDefaultPrivacySettings('test');
      checks.push({ name: 'Privacy Controls', status: 'pass' });
      score++;
    } catch (error) {
      checks.push({ name: 'Privacy Controls', status: 'fail', message: 'Privacy service not available' });
    }

    // Calculate overall status
    const percentage = (score / totalChecks) * 100;
    let status: 'healthy' | 'warning' | 'critical';

    if (percentage >= 80) {
      status = 'healthy';
    } else if (percentage >= 60) {
      status = 'warning';
    } else {
      status = 'critical';
    }

    const recommendations = [];
    if (status === 'critical') {
      recommendations.push('Immediate security review required');
      recommendations.push('Check all security service configurations');
    } else if (status === 'warning') {
      recommendations.push('Review failed security checks');
      recommendations.push('Consider enabling additional security features');
    } else {
      recommendations.push('Regular security maintenance recommended');
      recommendations.push('Monitor for new security threats');
    }

    return {
      status,
      checks,
      score: percentage,
      recommendations
    };
  }

  // Configuration
  static updateConfiguration(options: Partial<SecurityInitializationOptions>): void {
    this.initializationOptions = { ...this.initializationOptions, ...options };
  }

  static getConfiguration(): SecurityInitializationOptions {
    return { ...this.initializationOptions };
  }

  private static ensureInitialized(): void {
    if (!this.isInitialized) {
      throw new Error('SecurityService is not initialized. Call initialize() first.');
    }
  }
}