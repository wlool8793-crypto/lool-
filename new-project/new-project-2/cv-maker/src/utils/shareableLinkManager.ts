
export interface ShareableLink {
  id: string;
  documentId: string;
  url: string;
  accessKey: string;
  expiresAt: Date;
  createdAt: Date;
  createdBy: string;
  accessLevel: 'public' | 'restricted' | 'private';
  maxDownloads?: number;
  currentDownloads: number;
  password?: string;
  allowedEmails?: string[];
  settings: ShareSettings;
  analytics: LinkAnalytics;
}

export interface ShareSettings {
  requirePassword: boolean;
  allowDownload: boolean;
  allowSharing: boolean;
  showWatermark: boolean;
  expirationEnabled: boolean;
  notifyOnAccess: boolean;
  blockBots: boolean;
  requireVerification: boolean;
}

export interface LinkAnalytics {
  views: number;
  downloads: number;
  uniqueVisitors: number;
  lastAccessed?: Date;
  accessLog: AccessLog[];
  geographicData: GeoData[];
  deviceData: DeviceData[];
}

export interface AccessLog {
  id: string;
  timestamp: Date;
  ipAddress?: string;
  userAgent?: string;
  action: 'view' | 'download' | 'share';
  success: boolean;
  location?: string;
  deviceType?: string;
}

export interface GeoData {
  country: string;
  city: string;
  views: number;
  lastAccessed: Date;
}

export interface DeviceData {
  type: 'desktop' | 'mobile' | 'tablet';
  browser: string;
  os: string;
  views: number;
  lastAccessed: Date;
}

export interface LinkCreateOptions {
  documentId: string;
  documentName: string;
  accessLevel: 'public' | 'restricted' | 'private';
  expirationHours?: number;
  maxDownloads?: number;
  password?: string;
  allowedEmails?: string[];
  notifyOnAccess?: boolean;
  requireVerification?: boolean;
  customMessage?: string;
  branding?: {
    logo?: string;
    companyName?: string;
    customColors?: {
      primary: string;
      secondary: string;
    };
  };
}

export class ShareableLinkManager {
  private static readonly STORAGE_KEY = 'shareable_links';
  private static readonly ANALYTICS_KEY = 'link_analytics';

  static async createShareableLink(
    options: LinkCreateOptions
  ): Promise<ShareableLink> {
    const linkId = this.generateLinkId();
    const accessKey = this.generateAccessKey();
    const expiresAt = options.expirationHours
      ? new Date(Date.now() + options.expirationHours * 60 * 60 * 1000)
      : new Date(Date.now() + 30 * 24 * 60 * 60 * 1000); // 30 days default

    const shareableLink: ShareableLink = {
      id: linkId,
      documentId: options.documentId,
      url: `${window.location.origin}/shared/${linkId}`,
      accessKey,
      expiresAt,
      createdAt: new Date(),
      createdBy: 'current-user', // In real app, get from auth
      accessLevel: options.accessLevel,
      maxDownloads: options.maxDownloads,
      currentDownloads: 0,
      password: options.password,
      allowedEmails: options.allowedEmails,
      settings: {
        requirePassword: !!options.password,
        allowDownload: true,
        allowSharing: false,
        showWatermark: true,
        expirationEnabled: !!options.expirationHours,
        notifyOnAccess: options.notifyOnAccess || false,
        blockBots: true,
        requireVerification: options.requireVerification || false
      },
      analytics: {
        views: 0,
        downloads: 0,
        uniqueVisitors: 0,
        accessLog: [],
        geographicData: [],
        deviceData: []
      }
    };

    // Store link data
    await this.storeLinkData(shareableLink);

    return shareableLink;
  }

  static async validateLinkAccess(
    linkId: string,
    accessKey?: string,
    password?: string,
    ipAddress?: string,
    userAgent?: string
  ): Promise<{
    valid: boolean;
    link?: ShareableLink;
    error?: string;
    requiresAction?: 'password' | 'verification' | 'email';
  }> {
    try {
      const link = await this.getLinkData(linkId);
      if (!link) {
        return { valid: false, error: 'Link not found' };
      }

      // Check expiration
      if (new Date() > link.expiresAt) {
        return { valid: false, error: 'Link expired' };
      }

      // Check access key
      if (link.accessKey !== accessKey) {
        await this.logAccess(linkId, 'view', false, ipAddress, userAgent);
        return { valid: false, error: 'Invalid access key' };
      }

      // Check download limit
      if (link.maxDownloads && link.currentDownloads >= link.maxDownloads) {
        return { valid: false, error: 'Download limit exceeded' };
      }

      // Check password
      if (link.settings.requirePassword && !password) {
        return {
          valid: false,
          requiresAction: 'password',
          error: 'Password required'
        };
      }

      if (link.settings.requirePassword && password !== link.password) {
        await this.logAccess(linkId, 'view', false, ipAddress, userAgent);
        return { valid: false, error: 'Invalid password' };
      }

      // Check bot blocking
      if (link.settings.blockBots && this.isBot(userAgent)) {
        return { valid: false, error: 'Bot access blocked' };
      }

      // Log successful access
      await this.logAccess(linkId, 'view', true, ipAddress, userAgent);

      return { valid: true, link };
    } catch (error) {
      console.error('Error validating link access:', error);
      return { valid: false, error: 'Validation failed' };
    }
  }

  static async recordDownload(
    linkId: string,
    ipAddress?: string,
    userAgent?: string
  ): Promise<boolean> {
    try {
      const link = await this.getLinkData(linkId);
      if (!link) return false;

      // Check if download is allowed
      if (!link.settings.allowDownload) {
        return false;
      }

      // Check download limit
      if (link.maxDownloads && link.currentDownloads >= link.maxDownloads) {
        return false;
      }

      // Update download count
      link.currentDownloads++;
      link.analytics.downloads++;

      // Log download
      await this.logAccess(linkId, 'download', true, ipAddress, userAgent);

      // Save updated link data
      await this.storeLinkData(link);

      return true;
    } catch (error) {
      console.error('Error recording download:', error);
      return false;
    }
  }

  static async getLinkAnalytics(
    linkId: string,
    dateRange?: { start: Date; end: Date }
  ): Promise<LinkAnalytics | null> {
    try {
      const analytics = await this.getAnalyticsData(linkId);
      if (!analytics) return null;

      // Filter by date range if specified
      if (dateRange) {
        analytics.accessLog = analytics.accessLog.filter(log =>
          log.timestamp >= dateRange.start && log.timestamp <= dateRange.end
        );
      }

      return analytics;
    } catch (error) {
      console.error('Error getting link analytics:', error);
      return null;
    }
  }

  static async revokeLink(linkId: string): Promise<boolean> {
    try {
      const links = await this.getAllLinks();
      const linkIndex = links.findIndex(link => link.id === linkId);

      if (linkIndex === -1) {
        return false;
      }

      links.splice(linkIndex, 1);
      await this.saveAllLinks(links);

      // Also remove analytics
      const analytics = await this.getAllAnalytics();
      delete analytics[linkId];
      await this.saveAllAnalytics(analytics);

      return true;
    } catch (error) {
      console.error('Error revoking link:', error);
      return false;
    }
  }

  static async extendLinkExpiration(
    linkId: string,
    additionalHours: number
  ): Promise<boolean> {
    try {
      const link = await this.getLinkData(linkId);
      if (!link) return false;

      link.expiresAt = new Date(link.expiresAt.getTime() + additionalHours * 60 * 60 * 1000);
      await this.storeLinkData(link);

      return true;
    } catch (error) {
      console.error('Error extending link expiration:', error);
      return false;
    }
  }

  static async updateLinkSettings(
    linkId: string,
    settings: Partial<ShareSettings>
  ): Promise<boolean> {
    try {
      const link = await this.getLinkData(linkId);
      if (!link) return false;

      link.settings = { ...link.settings, ...settings };
      await this.storeLinkData(link);

      return true;
    } catch (error) {
      console.error('Error updating link settings:', error);
      return false;
    }
  }

  static async getAllUserLinks(userId: string): Promise<ShareableLink[]> {
    try {
      const allLinks = await this.getAllLinks();
      return allLinks.filter(link => link.createdBy === userId);
    } catch (error) {
      console.error('Error getting user links:', error);
      return [];
    }
  }

  static async generateQRCode(linkId: string): Promise<string> {
    try {
      const link = await this.getLinkData(linkId);
      if (!link) throw new Error('Link not found');

      // In a real implementation, you would use a QR code library
      // For now, return a placeholder URL
      return `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(link.url)}`;
    } catch (error) {
      console.error('Error generating QR code:', error);
      throw new Error('Failed to generate QR code');
    }
  }

  static async createShareablePackage(
    linkIds: string[],
    packageName: string,
    options: {
      password?: string;
      expirationHours?: number;
      description?: string;
    } = {}
  ): Promise<{
    packageId: string;
    url: string;
    links: ShareableLink[];
  }> {
    const packageId = this.generateLinkId();
    const links: ShareableLink[] = [];

    for (const linkId of linkIds) {
      const link = await this.getLinkData(linkId);
      if (link) {
        links.push(link);
      }
    }

    if (links.length === 0) {
      throw new Error('No valid links found');
    }

    const packageData = {
      id: packageId,
      name: packageName,
      description: options.description,
      links: links.map(link => link.id),
      createdAt: new Date().toISOString(),
      expiresAt: options.expirationHours
        ? new Date(Date.now() + options.expirationHours * 60 * 60 * 1000).toISOString()
        : null,
      password: options.password
    };

    // Store package data
    localStorage.setItem(`package_${packageId}`, JSON.stringify(packageData));

    const url = `${window.location.origin}/package/${packageId}`;

    return {
      packageId,
      url,
      links
    };
  }

  private static async storeLinkData(link: ShareableLink): Promise<void> {
    const links = await this.getAllLinks();
    const existingIndex = links.findIndex(l => l.id === link.id);

    if (existingIndex >= 0) {
      links[existingIndex] = link;
    } else {
      links.push(link);
    }

    await this.saveAllLinks(links);
  }

  private static async getLinkData(linkId: string): Promise<ShareableLink | null> {
    const links = await this.getAllLinks();
    return links.find(link => link.id === linkId) || null;
  }

  private static async getAllLinks(): Promise<ShareableLink[]> {
    try {
      const data = localStorage.getItem(this.STORAGE_KEY);
      if (!data) return [];

      const links = JSON.parse(data);
      return links.map((link: any) => ({
        ...link,
        expiresAt: new Date(link.expiresAt),
        createdAt: new Date(link.createdAt),
        analytics: {
          ...link.analytics,
          accessLog: link.analytics.accessLog.map((log: any) => ({
            ...log,
            timestamp: new Date(log.timestamp)
          }))
        }
      }));
    } catch (error) {
      console.error('Error getting all links:', error);
      return [];
    }
  }

  private static async saveAllLinks(links: ShareableLink[]): Promise<void> {
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(links));
    } catch (error) {
      console.error('Error saving links:', error);
      throw new Error('Failed to save links');
    }
  }

  private static async logAccess(
    linkId: string,
    action: 'view' | 'download' | 'share',
    success: boolean,
    ipAddress?: string,
    userAgent?: string
  ): Promise<void> {
    try {
      const analytics = await this.getAnalyticsData(linkId) || {
        views: 0,
        downloads: 0,
        uniqueVisitors: 0,
        accessLog: [],
        geographicData: [],
        deviceData: []
      };

      const accessLog: AccessLog = {
        id: this.generateLinkId(),
        timestamp: new Date(),
        ipAddress,
        userAgent,
        action,
        success,
        location: await this.getGeoLocation(ipAddress),
        deviceType: this.getDeviceType(userAgent)
      };

      analytics.accessLog.push(accessLog);

      // Update counters
      if (success) {
        if (action === 'view') {
          analytics.views++;
          analytics.uniqueVisitors = this.countUniqueVisitors(analytics.accessLog);
        } else if (action === 'download') {
          analytics.downloads++;
        }
      }

      // Update geographic data
      this.updateGeoData(analytics, accessLog);

      // Update device data
      this.updateDeviceData(analytics, accessLog);

      await this.saveAnalyticsData(linkId, analytics);
    } catch (error) {
      console.error('Error logging access:', error);
    }
  }

  private static async getAnalyticsData(linkId: string): Promise<LinkAnalytics | null> {
    try {
      const data = localStorage.getItem(`${this.ANALYTICS_KEY}_${linkId}`);
      if (!data) return null;

      const analytics = JSON.parse(data);
      return {
        ...analytics,
        accessLog: analytics.accessLog.map((log: any) => ({
          ...log,
          timestamp: new Date(log.timestamp)
        })),
        geographicData: analytics.geographicData.map((geo: any) => ({
          ...geo,
          lastAccessed: new Date(geo.lastAccessed)
        })),
        deviceData: analytics.deviceData.map((device: any) => ({
          ...device,
          lastAccessed: new Date(device.lastAccessed)
        }))
      };
    } catch (error) {
      console.error('Error getting analytics data:', error);
      return null;
    }
  }

  private static async saveAnalyticsData(linkId: string, analytics: LinkAnalytics): Promise<void> {
    try {
      localStorage.setItem(`${this.ANALYTICS_KEY}_${linkId}`, JSON.stringify(analytics));
    } catch (error) {
      console.error('Error saving analytics data:', error);
    }
  }

  private static async getAllAnalytics(): Promise<Record<string, LinkAnalytics>> {
    try {
      const analytics: Record<string, LinkAnalytics> = {};
      const keys = Object.keys(localStorage).filter(key => key.startsWith(this.ANALYTICS_KEY));

      for (const key of keys) {
        const linkId = key.replace(`${this.ANALYTICS_KEY}_`, '');
        const data = await this.getAnalyticsData(linkId);
        if (data) {
          analytics[linkId] = data;
        }
      }

      return analytics;
    } catch (error) {
      console.error('Error getting all analytics:', error);
      return {};
    }
  }

  private static async saveAllAnalytics(analytics: Record<string, LinkAnalytics>): Promise<void> {
    try {
      for (const [linkId, data] of Object.entries(analytics)) {
        await this.saveAnalyticsData(linkId, data);
      }
    } catch (error) {
      console.error('Error saving all analytics:', error);
    }
  }

  private static countUniqueVisitors(accessLog: AccessLog[]): number {
    const uniqueIPs = new Set(accessLog.filter(log => log.success && log.ipAddress).map(log => log.ipAddress));
    return uniqueIPs.size;
  }

  private static updateGeoData(analytics: LinkAnalytics, accessLog: AccessLog): void {
    if (!accessLog.location) return;

    const existing = analytics.geographicData.find(geo => geo.country === accessLog.location);
    if (existing) {
      existing.views++;
      existing.lastAccessed = accessLog.timestamp;
    } else {
      analytics.geographicData.push({
        country: accessLog.location,
        city: 'Unknown',
        views: 1,
        lastAccessed: accessLog.timestamp
      });
    }
  }

  private static updateDeviceData(analytics: LinkAnalytics, accessLog: AccessLog): void {
    if (!accessLog.deviceType) return;

    const existing = analytics.deviceData.find(device => device.type === accessLog.deviceType);
    if (existing) {
      existing.views++;
      existing.lastAccessed = accessLog.timestamp;
    } else {
      analytics.deviceData.push({
        type: accessLog.deviceType as 'desktop' | 'mobile' | 'tablet',
        browser: 'Unknown',
        os: 'Unknown',
        views: 1,
        lastAccessed: accessLog.timestamp
      });
    }
  }

  private static async getGeoLocation(ipAddress?: string): Promise<string | undefined> {
    // In a real implementation, you would use a geolocation service
    // For now, return a placeholder
    return ipAddress ? 'Unknown' : undefined;
  }

  private static getDeviceType(userAgent?: string): 'desktop' | 'mobile' | 'tablet' {
    if (!userAgent) return 'desktop';

    if (/tablet|ipad|playbook|silk/i.test(userAgent)) {
      return 'tablet';
    } else if (/mobile|iphone|ipod|android|blackberry|opera|mini|windows\sce|palm|smartphone|iemobile/i.test(userAgent)) {
      return 'mobile';
    } else {
      return 'desktop';
    }
  }

  private static isBot(userAgent?: string): boolean {
    if (!userAgent) return false;

    const botPatterns = [
      /bot/i, /crawler/i, /spider/i, /scraper/i,
      /curl/i, /wget/i, /python/i, /go-http/i
    ];

    return botPatterns.some(pattern => pattern.test(userAgent));
  }

  private static generateLinkId(): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < 12; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  }

  private static generateAccessKey(): string {
    return crypto.randomUUID().replace(/-/g, '').substring(0, 16);
  }
}