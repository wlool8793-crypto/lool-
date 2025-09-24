export interface ExportEvent {
  id: string;
  timestamp: Date;
  userId: string;
  documentId: string;
  documentType: 'cv' | 'marriage' | 'general';
  action: ExportAction;
  format: ExportFormat;
  success: boolean;
  fileSize?: number;
  processingTime: number;
  metadata: ExportMetadata;
  location?: string;
  deviceInfo?: DeviceInfo;
}

export interface ExportAction {
  type: 'generate' | 'download' | 'share' | 'email' | 'print';
  method: 'pdf' | 'docx' | 'html' | 'json' | 'txt' | 'link';
  template?: string;
  quality?: 'low' | 'medium' | 'high';
  privacy?: PrivacyLevel;
}

export interface ExportFormat {
  type: 'pdf' | 'docx' | 'html' | 'json' | 'txt';
  version: string;
  compression?: boolean;
  encryption?: boolean;
  watermark?: boolean;
}

export interface ExportMetadata {
  pages?: number;
  templateId: string;
  templateName: string;
  customizations: string[];
  features: string[];
  settings: Record<string, any>;
}

export interface DeviceInfo {
  type: 'desktop' | 'mobile' | 'tablet';
  browser: string;
  os: string;
  screenResolution: string;
  timezone: string;
  language: string;
}

export interface PrivacyLevel {
  password: boolean;
  watermark: boolean;
  expiration: boolean;
  accessControl: boolean;
  encryption: boolean;
}

export interface ExportAnalytics {
  totalExports: number;
  successfulExports: number;
  failedExports: number;
  popularFormats: FormatStats[];
  popularTemplates: TemplateStats[];
  usageByTime: TimeStats[];
  userBehavior: UserBehaviorStats;
  performance: PerformanceStats;
  trends: TrendData[];
}

export interface FormatStats {
  format: string;
  count: number;
  percentage: number;
  averageSize: number;
  averageTime: number;
  growth: number; // percentage growth over period
}

export interface TemplateStats {
  templateId: string;
  templateName: string;
  category: 'cv' | 'marriage' | 'general';
  exports: number;
  averageRating?: number;
  usage: number;
  lastUsed: Date;
  features: string[];
}

export interface TimeStats {
  period: 'hour' | 'day' | 'week' | 'month';
  data: TimeDataPoint[];
}

export interface TimeDataPoint {
  timestamp: Date;
  exports: number;
  uniqueUsers: number;
  popularFormat: string;
  averageTime: number;
}

export interface UserBehaviorStats {
  averageExportsPerUser: number;
  returnUsers: number;
  newUsers: number;
  commonWorkflow: string[];
  dropOffPoints: DropOffPoint[];
  userSegments: UserSegment[];
}

export interface DropOffPoint {
  step: string;
  count: number;
  percentage: number;
  reason?: string;
}

export interface UserSegment {
  segment: 'power' | 'regular' | 'casual' | 'new';
  count: number;
  percentage: number;
  characteristics: string[];
  averageExports: number;
}

export interface PerformanceStats {
  averageProcessingTime: number;
  averageFileSize: number;
  successRate: number;
  errorRates: ErrorRate[];
  systemLoad: SystemLoadData[];
}

export interface ErrorRate {
  errorType: string;
  count: number;
  percentage: number;
  commonCauses: string[];
  timestamp: Date;
}

export interface SystemLoadData {
  timestamp: Date;
  exports: number;
  processingTime: number;
  memoryUsage: number;
  cpuUsage: number;
}

export interface TrendData {
  metric: string;
  period: 'daily' | 'weekly' | 'monthly';
  data: TrendPoint[];
  direction: 'up' | 'down' | 'stable';
  change: number; // percentage change
}

export interface TrendPoint {
  date: Date;
  value: number;
  change: number;
}

export interface AnalyticsFilter {
  dateRange?: {
    start: Date;
    end: Date;
  };
  documentType?: 'cv' | 'marriage' | 'general';
  format?: string;
  template?: string;
  userId?: string;
  success?: boolean;
  location?: string;
}

export class ExportAnalytics {
  private static readonly STORAGE_KEY = 'export_events';
  private static readonly ANALYTICS_KEY = 'export_analytics';

  static async trackExport(event: Omit<ExportEvent, 'id' | 'timestamp'>): Promise<string> {
    try {
      const exportEvent: ExportEvent = {
        ...event,
        id: this.generateEventId(),
        timestamp: new Date()
      };

      // Store event
      await this.storeEvent(exportEvent);

      // Update analytics cache
      await this.updateAnalyticsCache(exportEvent);

      // Send to analytics service (in real implementation)
      await this.sendToAnalyticsService(exportEvent);

      return exportEvent.id;
    } catch (error) {
      console.error('Error tracking export event:', error);
      throw new Error('Failed to track export event');
    }
  }

  static async getAnalytics(filter?: AnalyticsFilter): Promise<ExportAnalytics> {
    try {
      const events = await this.getEvents(filter);
      const analytics = await this.calculateAnalytics(events);

      return analytics;
    } catch (error) {
      console.error('Error getting analytics:', error);
      throw new Error('Failed to get analytics');
    }
  }

  static async getRealTimeStats(): Promise<{
    activeExports: number;
    exportsPerMinute: number;
    averageProcessingTime: number;
    successRate: number;
    popularFormat: string;
    systemHealth: 'good' | 'warning' | 'critical';
  }> {
    try {
      const now = new Date();
      const fiveMinutesAgo = new Date(now.getTime() - 5 * 60 * 1000);

      const recentEvents = await this.getEvents({
        dateRange: { start: fiveMinutesAgo, end: now }
      });

      const activeExports = recentEvents.filter(e => e.action.type === 'generate').length;
      const successfulExports = recentEvents.filter(e => e.success).length;
      const exportsPerMinute = activeExports / 5;

      const averageProcessingTime = recentEvents.length > 0
        ? recentEvents.reduce((sum, e) => sum + e.processingTime, 0) / recentEvents.length
        : 0;

      const successRate = recentEvents.length > 0
        ? (successfulExports / recentEvents.length) * 100
        : 0;

      const formatCounts = this.countByFormat(recentEvents);
      const popularFormat = Object.entries(formatCounts).reduce((a, b) =>
        a[1] > b[1] ? a : b
      )?.[0] || 'pdf';

      const systemHealth = this.calculateSystemHealth(recentEvents);

      return {
        activeExports,
        exportsPerMinute,
        averageProcessingTime,
        successRate,
        popularFormat,
        systemHealth
      };
    } catch (error) {
      console.error('Error getting real-time stats:', error);
      return {
        activeExports: 0,
        exportsPerMinute: 0,
        averageProcessingTime: 0,
        successRate: 0,
        popularFormat: 'pdf',
        systemHealth: 'good'
      };
    }
  }

  static async getUserExportHistory(userId: string, limit: number = 50): Promise<ExportEvent[]> {
    try {
      const events = await this.getEvents({ userId });
      return events.slice(0, limit);
    } catch (error) {
      console.error('Error getting user export history:', error);
      return [];
    }
  }

  static async getExportReport(
    filter: AnalyticsFilter,
    format: 'json' | 'csv' | 'pdf' = 'json'
  ): Promise<string | Blob> {
    try {
      const analytics = await this.getAnalytics(filter);

      switch (format) {
        case 'json':
          return JSON.stringify(analytics, null, 2);
        case 'csv':
          return this.generateCSVReport(analytics);
        case 'pdf':
          return await this.generatePDFReport(analytics);
        default:
          throw new Error('Unsupported report format');
      }
    } catch (error) {
      console.error('Error generating export report:', error);
      throw new Error('Failed to generate report');
    }
  }

  static async getPopularInsights(
    dateRange?: { start: Date; end: Date }
  ): Promise<{
    topTemplates: TemplateStats[];
    topFormats: FormatStats[];
    peakTimes: TimeDataPoint[];
    userTrends: string[];
    recommendations: string[];
  }> {
    try {
      const events = await this.getEvents({ dateRange });

      const topTemplates = this.calculateTemplateStats(events);
      const topFormats = this.calculateFormatStats(events);
      const peakTimes = this.calculatePeakTimes(events);
      const userTrends = this.analyzeUserTrends(events);
      const recommendations = this.generateRecommendations(events);

      return {
        topTemplates,
        topFormats,
        peakTimes,
        userTrends,
        recommendations
      };
    } catch (error) {
      console.error('Error getting insights:', error);
      return {
        topTemplates: [],
        topFormats: [],
        peakTimes: [],
        userTrends: [],
        recommendations: []
      };
    }
  }

  static async exportUserData(
    userId: string,
    format: 'json' | 'csv' = 'json'
  ): Promise<string | Blob> {
    try {
      const events = await this.getEvents({ userId });
      const userAnalytics = await this.calculateUserAnalytics(events, userId);

      switch (format) {
        case 'json':
          return JSON.stringify(userAnalytics, null, 2);
        case 'csv':
          return this.generateUserCSVReport(events);
        default:
          throw new Error('Unsupported format');
      }
    } catch (error) {
      console.error('Error exporting user data:', error);
      throw new Error('Failed to export user data');
    }
  }

  static async setAnalyticsPreferences(
    userId: string,
    preferences: {
      trackingEnabled?: boolean;
      dataRetentionDays?: number;
      anonymizeData?: boolean;
      shareAnonymousData?: boolean;
    }
  ): Promise<void> {
    try {
      const key = `user_analytics_prefs_${userId}`;
      const existing = JSON.parse(localStorage.getItem(key) || '{}');
      const updated = { ...existing, ...preferences };
      localStorage.setItem(key, JSON.stringify(updated));
    } catch (error) {
      console.error('Error setting analytics preferences:', error);
    }
  }

  static async getAnalyticsPreferences(userId: string): Promise<{
    trackingEnabled: boolean;
    dataRetentionDays: number;
    anonymizeData: boolean;
    shareAnonymousData: boolean;
  }> {
    try {
      const key = `user_analytics_prefs_${userId}`;
      const prefs = JSON.parse(localStorage.getItem(key) || '{}');

      return {
        trackingEnabled: prefs.trackingEnabled ?? true,
        dataRetentionDays: prefs.dataRetentionDays ?? 365,
        anonymizeData: prefs.anonymizeData ?? false,
        shareAnonymousData: prefs.shareAnonymousData ?? true
      };
    } catch (error) {
      console.error('Error getting analytics preferences:', error);
      return {
        trackingEnabled: true,
        dataRetentionDays: 365,
        anonymizeData: false,
        shareAnonymousData: true
      };
    }
  }

  static async cleanupOldData(retentionDays: number = 365): Promise<number> {
    try {
      const cutoffDate = new Date(Date.now() - retentionDays * 24 * 60 * 60 * 1000);
      const events = await this.getAllEvents();
      const eventsToDelete = events.filter(event => event.timestamp < cutoffDate);

      const remainingEvents = events.filter(event => event.timestamp >= cutoffDate);
      await this.saveAllEvents(remainingEvents);

      return eventsToDelete.length;
    } catch (error) {
      console.error('Error cleaning up old data:', error);
      return 0;
    }
  }

  private static async storeEvent(event: ExportEvent): Promise<void> {
    try {
      const events = await this.getAllEvents();
      events.push(event);

      // Keep only last 10000 events to prevent storage issues
      if (events.length > 10000) {
        events.splice(0, events.length - 10000);
      }

      await this.saveAllEvents(events);
    } catch (error) {
      console.error('Error storing event:', error);
      throw new Error('Failed to store event');
    }
  }

  private static async getEvents(filter?: AnalyticsFilter): Promise<ExportEvent[]> {
    try {
      const events = await this.getAllEvents();
      let filteredEvents = [...events];

      // Apply filters
      if (filter) {
        if (filter.dateRange) {
          filteredEvents = filteredEvents.filter(event =>
            event.timestamp >= filter.dateRange!.start &&
            event.timestamp <= filter.dateRange!.end
          );
        }

        if (filter.documentType) {
          filteredEvents = filteredEvents.filter(event => event.documentType === filter.documentType);
        }

        if (filter.format) {
          filteredEvents = filteredEvents.filter(event => event.action.method === filter.format);
        }

        if (filter.template) {
          filteredEvents = filteredEvents.filter(event => event.metadata.templateId === filter.template);
        }

        if (filter.userId) {
          filteredEvents = filteredEvents.filter(event => event.userId === filter.userId);
        }

        if (filter.success !== undefined) {
          filteredEvents = filteredEvents.filter(event => event.success === filter.success);
        }
      }

      return filteredEvents.reverse(); // Most recent first
    } catch (error) {
      console.error('Error getting events:', error);
      return [];
    }
  }

  private static async calculateAnalytics(events: ExportEvent[]): Promise<ExportAnalytics> {
    const totalExports = events.length;
    const successfulExports = events.filter(e => e.success).length;
    const failedExports = totalExports - successfulExports;

    const popularFormats = this.calculateFormatStats(events);
    const popularTemplates = this.calculateTemplateStats(events);
    const usageByTime = this.calculateTimeStats(events);
    const userBehavior = this.calculateUserBehavior(events);
    const performance = this.calculatePerformance(events);
    const trends = this.calculateTrends(events);

    return {
      totalExports,
      successfulExports,
      failedExports,
      popularFormats,
      popularTemplates,
      usageByTime,
      userBehavior,
      performance,
      trends
    };
  }

  private static calculateFormatStats(events: ExportEvent[]): FormatStats[] {
    const formatCounts = this.countByFormat(events);
    const total = events.length;

    return Object.entries(formatCounts).map(([format, count]) => {
      const formatEvents = events.filter(e => e.action.method === format);
      const averageSize = formatEvents.reduce((sum, e) => sum + (e.fileSize || 0), 0) / formatEvents.length;
      const averageTime = formatEvents.reduce((sum, e) => sum + e.processingTime, 0) / formatEvents.length;

      return {
        format,
        count,
        percentage: (count / total) * 100,
        averageSize,
        averageTime,
        growth: Math.random() * 20 - 10 // Placeholder
      };
    });
  }

  private static calculateTemplateStats(events: ExportEvent[]): TemplateStats[] {
    const templateCounts = this.countByTemplate(events);
    const allTemplates = Object.keys(templateCounts);

    return allTemplates.map(templateId => {
      const templateEvents = events.filter(e => e.metadata.templateId === templateId);
      const template = templateEvents[0]?.metadata;

      return {
        templateId,
        templateName: template?.templateName || 'Unknown',
        category: templateEvents[0]?.documentType || 'general',
        exports: templateCounts[templateId],
        averageRating: Math.random() * 5, // Placeholder
        usage: templateCounts[templateId],
        lastUsed: new Date(Math.max(...templateEvents.map(e => e.timestamp.getTime()))),
        features: template?.features || []
      };
    });
  }

  private static calculateTimeStats(events: ExportEvent[]): TimeStats[] {
    const periods: ('hour' | 'day' | 'week' | 'month')[] = ['hour', 'day', 'week', 'month'];
    const stats: TimeStats[] = [];

    for (const period of periods) {
      const data = this.groupByTimePeriod(events, period);
      stats.push({ period, data });
    }

    return stats;
  }

  private static calculateUserBehavior(events: ExportEvent[]): UserBehaviorStats {
    const userCounts = this.countByUser(events);
    const totalUsers = Object.keys(userCounts).length;

    const averageExportsPerUser = totalUsers > 0 ? events.length / totalUsers : 0;

    // Placeholder calculations
    const returnUsers = Math.floor(totalUsers * 0.6);
    const newUsers = totalUsers - returnUsers;

    const commonWorkflow = ['select_template', 'fill_data', 'preview', 'export'];
    const dropOffPoints: DropOffPoint[] = [
      { step: 'template_selection', count: Math.floor(events.length * 0.1), percentage: 10 },
      { step: 'data_entry', count: Math.floor(events.length * 0.05), percentage: 5 }
    ];

    const userSegments: UserSegment[] = [
      { segment: 'power', count: Math.floor(totalUsers * 0.1), percentage: 10, characteristics: ['frequent', 'advanced'], averageExports: 20 },
      { segment: 'regular', count: Math.floor(totalUsers * 0.3), percentage: 30, characteristics: ['consistent'], averageExports: 5 },
      { segment: 'casual', count: Math.floor(totalUsers * 0.4), percentage: 40, characteristics: ['occasional'], averageExports: 2 },
      { segment: 'new', count: Math.floor(totalUsers * 0.2), percentage: 20, characteristics: ['first_time'], averageExports: 1 }
    ];

    return {
      averageExportsPerUser,
      returnUsers,
      newUsers,
      commonWorkflow,
      dropOffPoints,
      userSegments
    };
  }

  private static calculatePerformance(events: ExportEvent[]): PerformanceStats {
    const successfulEvents = events.filter(e => e.success);
    const averageProcessingTime = successfulEvents.length > 0
      ? successfulEvents.reduce((sum, e) => sum + e.processingTime, 0) / successfulEvents.length
      : 0;

    const averageFileSize = successfulEvents.length > 0
      ? successfulEvents.reduce((sum, e) => sum + (e.fileSize || 0), 0) / successfulEvents.length
      : 0;

    const successRate = events.length > 0 ? (successfulEvents.length / events.length) * 100 : 0;

    const errorRates = this.calculateErrorRates(events);
    const systemLoad = this.calculateSystemLoad(events);

    return {
      averageProcessingTime,
      averageFileSize,
      successRate,
      errorRates,
      systemLoad
    };
  }

  private static calculateTrends(events: ExportEvent[]): TrendData[] {
    const metrics = ['exports', 'success_rate', 'processing_time'];
    const trends: TrendData[] = [];

    for (const metric of metrics) {
      const data = this.calculateTrendData(events, metric);
      const direction = this.calculateTrendDirection(data);
      const change = this.calculateTrendChange(data);

      trends.push({
        metric,
        period: 'daily',
        data,
        direction,
        change
      });
    }

    return trends;
  }

  private static countByFormat(events: ExportEvent[]): Record<string, number> {
    return events.reduce((counts, event) => {
      const format = event.action.method;
      counts[format] = (counts[format] || 0) + 1;
      return counts;
    }, {} as Record<string, number>);
  }

  private static countByTemplate(events: ExportEvent[]): Record<string, number> {
    return events.reduce((counts, event) => {
      const template = event.metadata.templateId;
      counts[template] = (counts[template] || 0) + 1;
      return counts;
    }, {} as Record<string, number>);
  }

  private static countByUser(events: ExportEvent[]): Record<string, number> {
    return events.reduce((counts, event) => {
      const user = event.userId;
      counts[user] = (counts[user] || 0) + 1;
      return counts;
    }, {} as Record<string, number>);
  }

  private static groupByTimePeriod(events: ExportEvent[], period: string): TimeDataPoint[] {
    // Simplified time grouping
    const now = new Date();
    const data: TimeDataPoint[] = [];

    for (let i = 0; i < 24; i++) { // Last 24 periods
      const timestamp = new Date(now.getTime() - i * this.getPeriodDuration(period));
      const periodEvents = events.filter(e => this.isInPeriod(e.timestamp, timestamp, period));

      data.unshift({
        timestamp,
        exports: periodEvents.length,
        uniqueUsers: new Set(periodEvents.map(e => e.userId)).size,
        popularFormat: this.getMostPopularFormat(periodEvents),
        averageTime: periodEvents.length > 0
          ? periodEvents.reduce((sum, e) => sum + e.processingTime, 0) / periodEvents.length
          : 0
      });
    }

    return data;
  }

  private static getPeriodDuration(period: string): number {
    switch (period) {
      case 'hour': return 60 * 60 * 1000;
      case 'day': return 24 * 60 * 60 * 1000;
      case 'week': return 7 * 24 * 60 * 60 * 1000;
      case 'month': return 30 * 24 * 60 * 60 * 1000;
      default: return 60 * 60 * 1000;
    }
  }

  private static isInPeriod(timestamp: Date, periodStart: Date, period: string): boolean {
    const duration = this.getPeriodDuration(period);
    return timestamp >= periodStart && timestamp < new Date(periodStart.getTime() + duration);
  }

  private static getMostPopularFormat(events: ExportEvent[]): string {
    const counts = this.countByFormat(events);
    return Object.entries(counts).reduce((a, b) => a[1] > b[1] ? a : b)[0] || 'pdf';
  }

  private static calculateErrorRates(events: ExportEvent[]): ErrorRate[] {
    const failedEvents = events.filter(e => !e.success);
    const errorTypes = new Set(failedEvents.map(e => e.metadata.settings?.error || 'unknown'));

    return Array.from(errorTypes).map(errorType => ({
      errorType,
      count: failedEvents.filter(e => e.metadata.settings?.error === errorType).length,
      percentage: (failedEvents.filter(e => e.metadata.settings?.error === errorType).length / failedEvents.length) * 100,
      commonCauses: ['server_error', 'timeout', 'invalid_input'], // Placeholder
      timestamp: new Date()
    }));
  }

  private static calculateSystemLoad(events: ExportEvent[]): SystemLoadData[] {
    // Placeholder system load calculation
    return Array.from({ length: 24 }, (_, i) => ({
      timestamp: new Date(Date.now() - (23 - i) * 60 * 60 * 1000),
      exports: Math.floor(Math.random() * 100),
      processingTime: Math.random() * 5000,
      memoryUsage: Math.random() * 100,
      cpuUsage: Math.random() * 100
    }));
  }

  private static calculateTrendData(events: ExportEvent[], metric: string): TrendPoint[] {
    // Placeholder trend calculation
    return Array.from({ length: 30 }, (_, i) => ({
      date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000),
      value: Math.random() * 100,
      change: (Math.random() - 0.5) * 10
    }));
  }

  private static calculateTrendDirection(data: TrendPoint[]): 'up' | 'down' | 'stable' {
    if (data.length < 2) return 'stable';
    const recent = data.slice(-7);
    const earlier = data.slice(-14, -7);
    const recentAvg = recent.reduce((sum, d) => sum + d.value, 0) / recent.length;
    const earlierAvg = earlier.reduce((sum, d) => sum + d.value, 0) / earlier.length;
    const change = ((recentAvg - earlierAvg) / earlierAvg) * 100;

    return Math.abs(change) < 5 ? 'stable' : change > 0 ? 'up' : 'down';
  }

  private static calculateTrendChange(data: TrendPoint[]): number {
    if (data.length < 2) return 0;
    const first = data[0].value;
    const last = data[data.length - 1].value;
    return ((last - first) / first) * 100;
  }

  private static calculatePeakTimes(events: ExportEvent[]): TimeDataPoint[] {
    return this.groupByTimePeriod(events, 'hour');
  }

  private static analyzeUserTrends(events: ExportEvent[]): string[] {
    // Placeholder user trend analysis
    return [
      'Mobile usage increasing',
      'PDF exports most popular',
      'Weekday peak usage',
      'Template preferences changing'
    ];
  }

  private static generateRecommendations(events: ExportEvent[]): string[] {
    // Placeholder recommendations
    return [
      'Optimize PDF generation for better performance',
      'Add more template options for CVs',
      'Improve mobile export experience',
      'Add batch export functionality'
    ];
  }

  private static calculateSystemHealth(events: ExportEvent[]): 'good' | 'warning' | 'critical' {
    const recentEvents = events.slice(-100);
    const successRate = recentEvents.filter(e => e.success).length / recentEvents.length;
    const avgTime = recentEvents.reduce((sum, e) => sum + e.processingTime, 0) / recentEvents.length;

    if (successRate < 0.8 || avgTime > 10000) return 'critical';
    if (successRate < 0.95 || avgTime > 5000) return 'warning';
    return 'good';
  }

  private static generateCSVReport(analytics: ExportAnalytics): Blob {
    // Placeholder CSV generation
    const csv = 'Export Analytics Report\n' + JSON.stringify(analytics, null, 2);
    return new Blob([csv], { type: 'text/csv' });
  }

  private static async generatePDFReport(analytics: ExportAnalytics): Promise<Blob> {
    // Placeholder PDF generation
    const pdf = 'PDF Analytics Report';
    return new Blob([pdf], { type: 'application/pdf' });
  }

  private static generateUserCSVReport(events: ExportEvent[]): Blob {
    // Placeholder user CSV generation
    const csv = 'User Export History\n' + events.map(e =>
      `${e.timestamp},${e.action.type},${e.action.method},${e.success}`
    ).join('\n');
    return new Blob([csv], { type: 'text/csv' });
  }

  private static async calculateUserAnalytics(events: ExportEvent[], userId: string): Promise<any> {
    // Placeholder user analytics calculation
    return {
      userId,
      totalExports: events.length,
      successfulExports: events.filter(e => e.success).length,
      favoriteFormat: this.getMostPopularFormat(events),
      favoriteTemplate: events[0]?.metadata.templateId,
      lastExport: events[0]?.timestamp
    };
  }

  private static async updateAnalyticsCache(event: ExportEvent): Promise<void> {
    // Update cached analytics for faster retrieval
    try {
      const cacheKey = 'analytics_cache';
      const cached = JSON.parse(localStorage.getItem(cacheKey) || '{}');

      // Update cache with new event
      cached.lastEvent = event.timestamp;
      cached.totalEvents = (cached.totalEvents || 0) + 1;

      if (event.success) {
        cached.successfulEvents = (cached.successfulEvents || 0) + 1;
      }

      localStorage.setItem(cacheKey, JSON.stringify(cached));
    } catch (error) {
      console.error('Error updating analytics cache:', error);
    }
  }

  private static async sendToAnalyticsService(event: ExportEvent): Promise<void> {
    // In a real implementation, this would send data to an analytics service
    // like Google Analytics, Mixpanel, or a custom backend
    console.log('Sending to analytics service:', event);
  }

  private static async getAllEvents(): Promise<ExportEvent[]> {
    try {
      const data = localStorage.getItem(this.STORAGE_KEY);
      if (!data) return [];

      return JSON.parse(data).map((event: any) => ({
        ...event,
        timestamp: new Date(event.timestamp)
      }));
    } catch (error) {
      console.error('Error getting all events:', error);
      return [];
    }
  }

  private static async saveAllEvents(events: ExportEvent[]): Promise<void> {
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(events));
    } catch (error) {
      console.error('Error saving all events:', error);
      throw new Error('Failed to save events');
    }
  }

  private static generateEventId(): string {
    return `event_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}