import {
  PrivacyConsent,
  PrivacyComplianceReport,
  PrivacyAuditLog
} from '../types/security';
import { EncryptionUtils } from './encryptionUtils';
import { SecureStorage } from './secureStorage';

export interface ConsentRecord {
  id: string;
  userId: string;
  consentType: PrivacyConsent['consentType'];
  version: string;
  granted: boolean;
  grantedAt?: string;
  revokedAt?: string;
  ipAddress?: string;
  userAgent?: string;
  documentUrl?: string;
  language?: string;
}

export interface DataSubjectRequest {
  id: string;
  userId: string;
  requestType: 'access' | 'deletion' | 'portability' | 'rectification' | 'objection';
  status: 'pending' | 'processing' | 'completed' | 'rejected';
  requestData: Record<string, any>;
  response?: any;
  processedAt?: string;
  processedBy?: string;
  rejectionReason?: string;
  createdAt: string;
  dueDate: string;
}

export interface DataRetentionPolicy {
  dataType: string;
  retentionPeriod: number; // days
  action: 'delete' | 'archive' | 'anonymize';
  lastApplied: string;
  nextApplication: string;
}

export interface PrivacyPolicy {
  id: string;
  version: string;
  title: string;
  content: string;
  effectiveDate: string;
  lastUpdated: string;
  language: string;
  isActive: boolean;
}

export interface CookieConsent {
  id: string;
  userId?: string;
  sessionId: string;
  consentDate: string;
  necessary: boolean;
  analytics: boolean;
  marketing: boolean;
  personalization: boolean;
  ipAddress: string;
  userAgent: string;
}

export class GDPRUtils {
  private static readonly CONSENTS_STORAGE_KEY = 'gdpr_consents';
  private static readonly REQUESTS_STORAGE_KEY = 'gdpr_requests';
  private static readonly POLICIES_STORAGE_KEY = 'gdpr_policies';
  private static readonly RETENTION_STORAGE_KEY = 'gdpr_retention';
  private static readonly COOKIE_CONSENTS_KEY = 'gdpr_cookie_consents';

  private static readonly CONSENT_TYPES = [
    'data_collection',
    'data_sharing',
    'data_processing',
    'marketing',
    'analytics',
    'cookies',
    'third_party_sharing'
  ];

  static async initialize(): Promise<void> {
    await SecureStorage.initialize();
    await this.ensureDefaultPolicies();
  }

  static async recordConsent(
    userId: string,
    consentType: PrivacyConsent['consentType'],
    granted: boolean,
    version: string = '1.0',
    documentUrl?: string,
    language?: string
  ): Promise<ConsentRecord> {
    const consent: ConsentRecord = {
      id: EncryptionUtils.generateSecureId('consent'),
      userId,
      consentType,
      version,
      granted,
      grantedAt: granted ? new Date().toISOString() : undefined,
      revokedAt: granted ? undefined : new Date().toISOString(),
      documentUrl,
      language,
      ipAddress: 'unknown',
      userAgent: 'unknown'
    };

    await this.storeConsent(consent);

    // Log the consent action
    await this.logPrivacyAction(userId, granted ? 'consent_granted' : 'consent_revoked', {
      consentType,
      version,
      granted,
      documentUrl
    });

    return consent;
  }

  static async getUserConsents(userId: string): Promise<ConsentRecord[]> {
    const consents = await this.getAllConsents();
    return consents.filter(c => c.userId === userId);
  }

  static async hasConsent(
    userId: string,
    consentType: PrivacyConsent['consentType'],
    version?: string
  ): Promise<boolean> {
    const consents = await this.getUserConsents(userId);
    const consent = consents.find(c => c.consentType === consentType && c.granted);

    if (!consent) return false;

    if (version && consent.version !== version) return false;

    // Check if consent has been revoked
    return !consent.revokedAt || new Date(consent.revokedAt) < new Date(consent.grantedAt!);
  }

  static async createDataSubjectRequest(
    userId: string,
    requestType: DataSubjectRequest['requestType'],
    requestData: Record<string, any> = {}
  ): Promise<DataSubjectRequest> {
    const request: DataSubjectRequest = {
      id: EncryptionUtils.generateSecureId('request'),
      userId,
      requestType,
      status: 'pending',
      requestData,
      createdAt: new Date().toISOString(),
      dueDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString() // 30 days
    };

    await this.storeRequest(request);

    // Log the request
    await this.logPrivacyAction(userId, 'data_access', {
      requestType,
      requestId: request.id,
      status: 'pending'
    });

    return request;
  }

  static async processRequest(
    requestId: string,
    response: any,
    processedBy: string,
    status: 'completed' | 'rejected',
    rejectionReason?: string
  ): Promise<boolean> {
    const request = await this.getRequestById(requestId);
    if (!request) return false;

    request.status = status;
    request.response = response;
    request.processedAt = new Date().toISOString();
    request.processedBy = processedBy;
    request.rejectionReason = rejectionReason;

    await this.storeRequest(request);

    // Log the processing
    await this.logPrivacyAction(request.userId, 'data_access', {
      requestType: request.requestType,
      requestId,
      status,
      processedBy
    });

    return true;
  }

  static async exportUserData(userId: string): Promise<any> {
    const user = await this.getUserData(userId);
    if (!user) throw new Error('User not found');

    const consents = await this.getUserConsents(userId);
    const requests = await this.getUserRequests(userId);
    const sessions = await this.getUserSessions(userId);
    const securityAlerts = await this.getUserSecurityAlerts(userId);

    const exportData = {
      userProfile: {
        id: user.id,
        email: user.email,
        fullName: user.fullName,
        createdAt: user.createdAt,
        updatedAt: user.updatedAt,
        settings: user.settings
      },
      consents,
      dataRequests: requests,
      sessions,
      securityAlerts,
      exportMetadata: {
        exportedAt: new Date().toISOString(),
        format: 'json',
        version: '1.0',
        requestedBy: userId
      }
    };

    return exportData;
  }

  static async deleteUserData(userId: string): Promise<boolean> {
    try {
      // Get all user data
      const userData = await this.exportUserData(userId);

      // Archive data before deletion (for compliance)
      await this.archiveUserData(userId, userData);

      // Delete user consents
      await this.deleteUserConsents(userId);

      // Delete user requests
      await this.deleteUserRequests(userId);

      // Delete user sessions
      await this.deleteUserSessions(userId);

      // Delete user security alerts
      await this.deleteUserSecurityAlerts(userId);

      // Anonymize user profile data
      await this.anonymizeUserProfile(userId);

      // Log the deletion
      await this.logPrivacyAction(userId, 'data_access', {
        action: 'data_deletion',
        userId,
        timestamp: new Date().toISOString()
      });

      return true;
    } catch (error) {
      console.error('Error deleting user data:', error);
      return false;
    }
  }

  static async getPrivacyPolicy(language: string = 'en'): Promise<PrivacyPolicy | null> {
    const policies = await this.getAllPolicies();
    return policies.find(p => p.language === language && p.isActive) || null;
  }

  static async updatePrivacyPolicy(
    version: string,
    title: string,
    content: string,
    language: string = 'en'
  ): Promise<PrivacyPolicy> {
    // Deactivate existing policies for this language
    const policies = await this.getAllPolicies();
    policies.forEach(p => {
      if (p.language === language) {
        p.isActive = false;
      }
    });

    const newPolicy: PrivacyPolicy = {
      id: EncryptionUtils.generateSecureId('policy'),
      version,
      title,
      content,
      effectiveDate: new Date().toISOString(),
      lastUpdated: new Date().toISOString(),
      language,
      isActive: true
    };

    policies.push(newPolicy);
    await this.storePolicies(policies);

    return newPolicy;
  }

  static async getRetentionPolicies(): Promise<DataRetentionPolicy[]> {
    return (await SecureStorage.retrieve<DataRetentionPolicy[]>(this.RETENTION_STORAGE_KEY)) || [];
  }

  static async applyRetentionPolicies(): Promise<number> {
    const policies = await this.getRetentionPolicies();
    let processedCount = 0;

    for (const policy of policies) {
      if (new Date(policy.nextApplication) <= new Date()) {
        await this.applyRetentionPolicy(policy);
        policy.lastApplied = new Date().toISOString();
        policy.nextApplication = new Date(Date.now() + policy.retentionPeriod * 24 * 60 * 60 * 1000).toISOString();
        processedCount++;
      }
    }

    await SecureStorage.store(this.RETENTION_STORAGE_KEY, policies);
    return processedCount;
  }

  static async recordCookieConsent(
    sessionId: string,
    necessary: boolean,
    analytics: boolean,
    marketing: boolean,
    personalization: boolean,
    userId?: string
  ): Promise<CookieConsent> {
    const consent: CookieConsent = {
      id: EncryptionUtils.generateSecureId('cookie_consent'),
      userId,
      sessionId,
      consentDate: new Date().toISOString(),
      necessary,
      analytics,
      marketing,
      personalization,
      ipAddress: 'unknown',
      userAgent: 'unknown'
    };

    const consents = await this.getAllCookieConsents();
    consents.push(consent);
    await SecureStorage.store(this.COOKIE_CONSENTS_KEY, consents);

    return consent;
  }

  static async generateComplianceReport(userId: string): Promise<PrivacyComplianceReport> {
    const consents = await this.getUserConsents(userId);
    const requests = await this.getUserRequests(userId);
    const user = await this.getUserData(userId);

    const report: PrivacyComplianceReport = {
      userId,
      reportType: 'consent_summary',
      generatedAt: new Date().toISOString(),
      data: {
        user: {
          id: userId,
          email: user?.email,
          createdAt: user?.createdAt
        },
        consents: consents.map(c => ({
          type: c.consentType,
          granted: c.granted,
          grantedAt: c.grantedAt,
          revokedAt: c.revokedAt,
          version: c.version
        })),
        requests: requests.map(r => ({
          type: r.requestType,
          status: r.status,
          createdAt: r.createdAt,
          processedAt: r.processedAt
        })),
        dataRetention: await this.getUserDataRetentionInfo(userId)
      },
      format: 'json'
    };

    return report;
  }

  static async checkPolicyCompliance(userId: string): Promise<{
    compliant: boolean;
    issues: string[];
    recommendations: string[];
  }> {
    const issues: string[] = [];
    const recommendations: string[] = [];

    // Check consent for required types
    const requiredConsents = ['data_collection', 'data_processing'];
    for (const consentType of requiredConsents) {
      const hasConsent = await this.hasConsent(userId, consentType);
      if (!hasConsent) {
        issues.push(`Missing required consent: ${consentType}`);
      }
    }

    // Check for outdated requests
    const requests = await this.getUserRequests(userId);
    const overdueRequests = requests.filter(r =>
      r.status === 'pending' && new Date(r.dueDate) < new Date()
    );

    if (overdueRequests.length > 0) {
      issues.push(`${overdueRequests.length} overdue data subject requests`);
    }

    // Check data retention
    const retentionIssues = await this.checkDataRetentionCompliance(userId);
    issues.push(...retentionIssues);

    // Generate recommendations
    if (issues.length === 0) {
      recommendations.push('All compliance checks passed');
    } else {
      recommendations.push('Review and address compliance issues');
    }

    return {
      compliant: issues.length === 0,
      issues,
      recommendations
    };
  }

  // Private helper methods
  private static async storeConsent(consent: ConsentRecord): Promise<void> {
    const consents = await this.getAllConsents();
    consents.push(consent);
    await SecureStorage.store(this.CONSENTS_STORAGE_KEY, consents);
  }

  private static async getAllConsents(): Promise<ConsentRecord[]> {
    return (await SecureStorage.retrieve<ConsentRecord[]>(this.CONSENTS_STORAGE_KEY)) || [];
  }

  private static async deleteUserConsents(userId: string): Promise<void> {
    const consents = await this.getAllConsents();
    const filtered = consents.filter(c => c.userId !== userId);
    await SecureStorage.store(this.CONSENTS_STORAGE_KEY, filtered);
  }

  private static async storeRequest(request: DataSubjectRequest): Promise<void> {
    const requests = await this.getAllRequests();
    requests.push(request);
    await SecureStorage.store(this.REQUESTS_STORAGE_KEY, requests);
  }

  private static async getAllRequests(): Promise<DataSubjectRequest[]> {
    return (await SecureStorage.retrieve<DataSubjectRequest[]>(this.REQUESTS_STORAGE_KEY)) || [];
  }

  private static async getRequestById(requestId: string): Promise<DataSubjectRequest | null> {
    const requests = await this.getAllRequests();
    return requests.find(r => r.id === requestId) || null;
  }

  private static async getUserRequests(userId: string): Promise<DataSubjectRequest[]> {
    const requests = await this.getAllRequests();
    return requests.filter(r => r.userId === userId);
  }

  private static async deleteUserRequests(userId: string): Promise<void> {
    const requests = await this.getAllRequests();
    const filtered = requests.filter(r => r.userId !== userId);
    await SecureStorage.store(this.REQUESTS_STORAGE_KEY, filtered);
  }

  private static async getAllPolicies(): Promise<PrivacyPolicy[]> {
    return (await SecureStorage.retrieve<PrivacyPolicy[]>(this.POLICIES_STORAGE_KEY)) || [];
  }

  private static async storePolicies(policies: PrivacyPolicy[]): Promise<void> {
    await SecureStorage.store(this.POLICIES_STORAGE_KEY, policies);
  }

  private static async ensureDefaultPolicies(): Promise<void> {
    const policies = await this.getAllPolicies();
    if (policies.length === 0) {
      await this.updatePrivacyPolicy(
        '1.0',
        'Privacy Policy',
        'Default privacy policy content...',
        'en'
      );
    }
  }

  private static async getUserData(userId: string): Promise<any> {
    // This would typically fetch from user storage
    return null;
  }

  private static async getUserSessions(userId: string): Promise<any[]> {
    // This would typically fetch from session storage
    return [];
  }

  private static async getUserSecurityAlerts(userId: string): Promise<any[]> {
    // This would typically fetch from security alerts storage
    return [];
  }

  private static async deleteUserSessions(userId: string): Promise<void> {
    // Implementation would depend on session storage
  }

  private static async deleteUserSecurityAlerts(userId: string): Promise<void> {
    // Implementation would depend on security alerts storage
  }

  private static async anonymizeUserProfile(userId: string): Promise<void> {
    // Implementation would anonymize user data while preserving compliance records
  }

  private static async archiveUserData(userId: string, userData: any): Promise<void> {
    // Implementation would archive data for compliance purposes
  }

  private static async applyRetentionPolicy(policy: DataRetentionPolicy): Promise<void> {
    // Implementation would apply the specific retention policy
  }

  private static async getUserDataRetentionInfo(userId: string): Promise<any> {
    // Implementation would return data retention information for the user
    return {};
  }

  private static async checkDataRetentionCompliance(userId: string): Promise<string[]> {
    const issues: string[] = [];
    // Implementation would check data retention compliance
    return issues;
  }

  private static async getAllCookieConsents(): Promise<CookieConsent[]> {
    return (await SecureStorage.retrieve<CookieConsent[]>(this.COOKIE_CONSENTS_KEY)) || [];
  }

  private static async logPrivacyAction(
    userId: string,
    action: PrivacyAuditLog['action'],
    details: Record<string, any>
  ): Promise<void> {
    const log: PrivacyAuditLog = {
      id: EncryptionUtils.generateSecureId('log'),
      userId,
      action,
      details,
      timestamp: new Date().toISOString()
    };

    // Store log in a secure audit system
    console.log('GDPR Audit Log:', log);
  }
}