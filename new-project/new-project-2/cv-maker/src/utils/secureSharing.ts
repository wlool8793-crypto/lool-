import {
  SecureShare,
  ShareAccessLog
} from '../types/encryption';
import { EncryptionUtils } from './encryptionUtils';
import { SecureStorage } from './secureStorage';

export interface ShareConfig {
  password?: string;
  expiresAt?: Date;
  maxAccessCount?: number;
  permissions: 'view' | 'download' | 'edit';
  allowResharing: boolean;
  requireAuthentication: boolean;
  notifyOnAccess: boolean;
}

export interface ShareAnalytics {
  shareId: string;
  totalAccesses: number;
  uniqueAccesses: number;
  lastAccessed: Date | null;
  accessByDate: Record<string, number>;
  accessByLocation: Record<string, number>;
  topReferrers: string[];
  isExpired: boolean;
  isAccessLimitReached: boolean;
}

export class SecureSharing {
  private static readonly SHARES_STORAGE_KEY = 'secure_shares';
  private static readonly ANALYTICS_STORAGE_KEY = 'share_analytics';

  static async createShare(
    documentId: string,
    documentName: string,
    createdBy: string,
    config: ShareConfig
  ): Promise<SecureShare> {
    const share: SecureShare = {
      id: EncryptionUtils.generateSecureId('share'),
      documentId,
      shareToken: EncryptionUtils.generateSecureToken(16),
      password: config.password ? await this.hashPassword(config.password) : undefined,
      permissions: config.permissions,
      expiresAt: config.expiresAt?.toISOString(),
      maxAccessCount: config.maxAccessCount,
      accessCount: 0,
      createdBy,
      createdAt: new Date().toISOString(),
      isActive: true,
      accessLogs: []
    };

    // Store the share
    await this.storeShare(share);

    // Initialize analytics
    await this.initializeAnalytics(share.id);

    return share;
  }

  static async validateShare(
    shareToken: string,
    password?: string
  ): Promise<{ valid: boolean; share?: SecureShare; reason?: string }> {
    const share = await this.getShareByToken(shareToken);

    if (!share) {
      return { valid: false, reason: 'Share not found' };
    }

    if (!share.isActive) {
      return { valid: false, reason: 'Share is not active' };
    }

    if (share.expiresAt && new Date(share.expiresAt) < new Date()) {
      return { valid: false, reason: 'Share has expired' };
    }

    if (share.maxAccessCount && share.accessCount >= share.maxAccessCount) {
      return { valid: false, reason: 'Access limit reached' };
    }

    if (share.password && password) {
      const isValid = await this.verifyPassword(password, share.password);
      if (!isValid) {
        return { valid: false, reason: 'Invalid password' };
      }
    } else if (share.password && !password) {
      return { valid: false, reason: 'Password required' };
    }

    return { valid: true, share };
  }

  static async accessShare(
    shareToken: string,
    accessedBy: string,
    ipAddress?: string,
    userAgent?: string,
    password?: string
  ): Promise<{ success: boolean; share?: SecureShare; reason?: string }> {
    const validation = await this.validateShare(shareToken, password);

    if (!validation.valid) {
      await this.logAccessAttempt(shareToken, accessedBy, 'access_denied', ipAddress, userAgent, validation.reason);
      return { success: false, reason: validation.reason };
    }

    const share = validation.share!;

    // Log successful access
    const accessLog: ShareAccessLog = {
      id: EncryptionUtils.generateSecureId('access'),
      accessedBy,
      ipAddress: ipAddress || 'unknown',
      userAgent: userAgent || 'unknown',
      timestamp: new Date().toISOString(),
      action: 'view',
      success: true
    };

    share.accessLogs.push(accessLog);
    share.accessCount++;

    // Update analytics
    await this.updateAnalytics(share.id, accessedBy, ipAddress);

    // Store updated share
    await this.storeShare(share);

    return { success: true, share };
  }

  static async revokeShare(shareId: string, revokedBy: string): Promise<boolean> {
    const share = await this.getShareById(shareId);

    if (!share) {
      return false;
    }

    share.isActive = false;
    share.updatedAt = new Date().toISOString();

    await this.storeShare(share);

    // Log revocation
    await this.logAccessAttempt(share.shareToken, revokedBy, 'share_revoked', '', '', 'Share revoked by owner');

    return true;
  }

  static async getShareAnalytics(shareId: string): Promise<ShareAnalytics | null> {
    const analytics = await SecureStorage.retrieve<ShareAnalytics>(`${this.ANALYTICS_STORAGE_KEY}_${shareId}`);
    return analytics;
  }

  static async getUserShares(userId: string): Promise<SecureShare[]> {
    const shares = await this.getAllShares();
    return shares.filter(share => share.createdBy === userId);
  }

  static async getActiveShares(): Promise<SecureShare[]> {
    const shares = await this.getAllShares();
    const now = new Date();

    return shares.filter(share => {
      if (!share.isActive) return false;
      if (share.expiresAt && new Date(share.expiresAt) < now) return false;
      if (share.maxAccessCount && share.accessCount >= share.maxAccessCount) return false;
      return true;
    });
  }

  static async cleanupExpiredShares(): Promise<number> {
    const shares = await this.getAllShares();
    const now = new Date();
    let cleanedCount = 0;

    for (const share of shares) {
      if ((share.expiresAt && new Date(share.expiresAt) < now) ||
          (share.maxAccessCount && share.accessCount >= share.maxAccessCount)) {
        share.isActive = false;
        await this.storeShare(share);
        cleanedCount++;
      }
    }

    return cleanedCount;
  }

  static async createShareableLink(
    share: SecureShare,
    baseUrl: string
  ): Promise<string> {
    const params = new URLSearchParams({
      token: share.shareToken
    });

    if (share.password) {
      params.set('protected', 'true');
    }

    return `${baseUrl}/share?${params.toString()}`;
  }

  static async regenerateShareToken(shareId: string): Promise<string | null> {
    const share = await this.getShareById(shareId);

    if (!share) {
      return null;
    }

    share.shareToken = EncryptionUtils.generateSecureToken(16);
    share.updatedAt = new Date().toISOString();

    await this.storeShare(share);

    return share.shareToken;
  }

  static async updateSharePermissions(
    shareId: string,
    permissions: 'view' | 'download' | 'edit'
  ): Promise<boolean> {
    const share = await this.getShareById(shareId);

    if (!share) {
      return false;
    }

    share.permissions = permissions;
    share.updatedAt = new Date().toISOString();

    await this.storeShare(share);

    return true;
  }

  static async extendShareExpiration(
    shareId: string,
    newExpiration: Date
  ): Promise<boolean> {
    const share = await this.getShareById(shareId);

    if (!share) {
      return false;
    }

    share.expiresAt = newExpiration.toISOString();
    share.updatedAt = new Date().toISOString();

    await this.storeShare(share);

    return true;
  }

  static async getShareAccessLogs(shareId: string): Promise<ShareAccessLog[]> {
    const share = await this.getShareById(shareId);
    return share?.accessLogs || [];
  }

  static async exportShareData(userId: string): Promise<{
    shares: SecureShare[];
    analytics: any[];
    exportedAt: string;
  }> {
    const shares = await this.getUserShares(userId);
    const analyticsPromises = shares.map(share => this.getShareAnalytics(share.id));
    const analyticsResults = await Promise.all(analyticsPromises);

    return {
      shares,
      analytics: analyticsResults.filter(a => a !== null),
      exportedAt: new Date().toISOString(),
      totalShares: shares.length,
      activeShares: shares.filter(s => s.isActive).length
    };
  }

  private static async storeShare(share: SecureShare): Promise<void> {
    const shares = await this.getAllShares();
    const existingIndex = shares.findIndex(s => s.id === share.id);

    if (existingIndex >= 0) {
      shares[existingIndex] = share;
    } else {
      shares.push(share);
    }

    await SecureStorage.store(this.SHARES_STORAGE_KEY, shares);
  }

  private static async getAllShares(): Promise<SecureShare[]> {
    return (await SecureStorage.retrieve<SecureShare[]>(this.SHARES_STORAGE_KEY)) || [];
  }

  private static async getShareById(shareId: string): Promise<SecureShare | null> {
    const shares = await this.getAllShares();
    return shares.find(share => share.id === shareId) || null;
  }

  private static async getShareByToken(shareToken: string): Promise<SecureShare | null> {
    const shares = await this.getAllShares();
    return shares.find(share => share.shareToken === shareToken) || null;
  }

  private static async hashPassword(password: string): Promise<string> {
    const hashResult = await EncryptionUtils.hashPassword(password);
    return hashResult.hash;
  }

  private static async verifyPassword(password: string, hashedPassword: string): Promise<boolean> {
    const hashData = { hash: hashedPassword, algorithm: 'pbkdf2', iterations: 100000, version: '1' };
    return EncryptionUtils.verifyPassword(password, hashData);
  }

  private static async logAccessAttempt(
    shareToken: string,
    accessedBy: string,
    action: ShareAccessLog['action'],
    ipAddress?: string,
    userAgent?: string,
    reason?: string
  ): Promise<void> {
    // This would typically log to a secure audit system
    console.log('Share access attempt:', {
      shareToken,
      accessedBy,
      action,
      ipAddress,
      userAgent,
      reason,
      timestamp: new Date().toISOString()
    });
  }

  private static async initializeAnalytics(shareId: string): Promise<void> {
    const analytics: ShareAnalytics = {
      shareId,
      totalAccesses: 0,
      uniqueAccesses: 0,
      lastAccessed: null,
      accessByDate: {},
      accessByLocation: {},
      topReferrers: [],
      isExpired: false,
      isAccessLimitReached: false
    };

    await SecureStorage.store(`${this.ANALYTICS_STORAGE_KEY}_${shareId}`, analytics);
  }

  private static async updateAnalytics(
    shareId: string,
    accessedBy: string,
    ipAddress?: string
  ): Promise<void> {
    const analytics = await this.getShareAnalytics(shareId);
    if (!analytics) return;

    const today = new Date().toISOString().split('T')[0];
    const location = ipAddress || 'unknown';

    // Update counters
    analytics.totalAccesses++;
    analytics.lastAccessed = new Date();

    // Update date-based stats
    analytics.accessByDate[today] = (analytics.accessByDate[today] || 0) + 1;

    // Update location-based stats
    analytics.accessByLocation[location] = (analytics.accessByLocation[location] || 0) + 1;

    // Update unique access count (simplified)
    // In a real implementation, this would track unique users more accurately
    analytics.uniqueAccesses = Object.keys(analytics.accessByLocation).length;

    // Update status flags
    const share = await this.getShareById(shareId);
    if (share) {
      analytics.isExpired = share.expiresAt ? new Date(share.expiresAt) < new Date() : false;
      analytics.isAccessLimitReached = share.maxAccessCount ? share.accessCount >= share.maxAccessCount : false;
    }

    // Update top referrers (simplified)
    if (location !== 'unknown') {
      analytics.topReferrers.push(location);
      analytics.topReferrers = [...new Set(analytics.topReferrers)].slice(0, 10);
    }

    await SecureStorage.store(`${this.ANALYTICS_STORAGE_KEY}_${shareId}`, analytics);
  }

  static async generateQRCode(shareUrl: string): Promise<string> {
    // This would typically use a QR code generation library
    // For now, return a placeholder
    return `data:image/svg+xml;base64,${btoa(`
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
        <rect width="100" height="100" fill="white"/>
        <rect x="10" y="10" width="80" height="80" fill="black"/>
        <rect x="20" y="20" width="60" height="60" fill="white"/>
        <rect x="30" y="30" width="40" height="40" fill="black"/>
        <text x="50" y="50" text-anchor="middle" fill="white" font-size="8">QR Code</text>
      </svg>
    `)}`;
  }

  static async validateShareUrl(url: string): Promise<{ isValid: boolean; shareToken?: string }> {
    try {
      const urlObj = new URL(url);
      const shareToken = urlObj.searchParams.get('token');

      if (!shareToken) {
        return { isValid: false };
      }

      const share = await this.getShareByToken(shareToken);
      if (!share) {
        return { isValid: false };
      }

      const validation = await this.validateShare(shareToken);
      return { isValid: validation.valid, shareToken };
    } catch (error) {
      return { isValid: false };
    }
  }
}