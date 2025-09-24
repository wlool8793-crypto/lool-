import DOMPurify from 'dompurify';
import { EncryptionUtils } from './encryptionUtils';
import { SecurityMonitoring } from './securityMonitoring';

export interface ModerationRule {
  id: string;
  name: string;
  type: 'text' | 'image' | 'file';
  pattern: string | RegExp;
  severity: 'low' | 'medium' | 'high' | 'critical';
  action: 'flag' | 'block' | 'quarantine' | 'require_review';
  enabled: boolean;
  category: string;
}

export interface ContentReport {
  id: string;
  reporterId: string;
  reportedUserId?: string;
  contentType: 'text' | 'image' | 'profile' | 'document';
  contentId: string;
  reason: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'pending' | 'under_review' | 'resolved' | 'dismissed';
  reviewedBy?: string;
  reviewedAt?: string;
  resolution?: string;
  createdAt: string;
  evidence?: any;
}

export interface ModerationResult {
  isApproved: boolean;
  flags: ModerationFlag[];
  score: number;
  requiresReview: boolean;
  blockedReason?: string;
}

export interface ModerationFlag {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  ruleId: string;
  message: string;
  confidence: number;
  category: string;
}

export interface ContentCategory {
  id: string;
  name: string;
  description: string;
  allowed: boolean;
  requiresReview: boolean;
  maxSeverity: 'low' | 'medium' | 'high' | 'critical';
}

export class ContentModeration {
  private static readonly REPORTS_STORAGE_KEY = 'moderation_reports';
  private static readonly RULES_STORAGE_KEY = 'moderation_rules';
  private static readonly CATEGORIES_STORAGE_KEY = 'moderation_categories';

  private static readonly DEFAULT_RULES: ModerationRule[] = [
    {
      id: 'profanity_filter',
      name: 'Profanity Filter',
      type: 'text',
      pattern: /\b(bad|swear|curse|explicit)\b/gi,
      severity: 'medium',
      action: 'flag',
      enabled: true,
      category: 'inappropriate_content'
    },
    {
      id: 'personal_info_filter',
      name: 'Personal Information Filter',
      type: 'text',
      pattern: /\b(\d{3}[-.\s]?\d{3}[-.\s]?\d{4}|\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b)/g,
      severity: 'high',
      action: 'flag',
      enabled: true,
      category: 'personal_data'
    },
    {
      id: 'hate_speech_filter',
      name: 'Hate Speech Filter',
      type: 'text',
      pattern: /\b(hate|discrimination|racist|sexist|homophobic)\b/gi,
      severity: 'critical',
      action: 'block',
      enabled: true,
      category: 'hate_speech'
    },
    {
      id: 'spam_filter',
      name: 'Spam Filter',
      type: 'text',
      pattern: /(https?:\/\/\S+|www\.\S+|\bclick\b|\bfree\b|\bwin\b|\bmoney\b)/gi,
      severity: 'medium',
      action: 'flag',
      enabled: true,
      category: 'spam'
    },
    {
      id: 'inappropriate_content_filter',
      name: 'Inappropriate Content Filter',
      type: 'text',
      pattern: /\b(nude|explicit|adult|porn|sexual)\b/gi,
      severity: 'high',
      action: 'block',
      enabled: true,
      category: 'inappropriate_content'
    },
    {
      id: 'suspicious_links_filter',
      name: 'Suspicious Links Filter',
      type: 'text',
      pattern: /(bit\.ly|t\.co|tinyurl\.com|short\.url)/gi,
      severity: 'medium',
      action: 'flag',
      enabled: true,
      category: 'suspicious_links'
    }
  ];

  private static readonly DEFAULT_CATEGORIES: ContentCategory[] = [
    {
      id: 'personal_data',
      name: 'Personal Data',
      description: 'Content containing personal information',
      allowed: true,
      requiresReview: true,
      maxSeverity: 'medium'
    },
    {
      id: 'inappropriate_content',
      name: 'Inappropriate Content',
      description: 'Content that may be inappropriate for some audiences',
      allowed: false,
      requiresReview: true,
      maxSeverity: 'medium'
    },
    {
      id: 'hate_speech',
      name: 'Hate Speech',
      description: 'Content promoting hate or discrimination',
      allowed: false,
      requiresReview: false,
      maxSeverity: 'low'
    },
    {
      id: 'spam',
      name: 'Spam',
      description: 'Unsolicited promotional content',
      allowed: false,
      requiresReview: false,
      maxSeverity: 'low'
    },
    {
      id: 'suspicious_links',
      name: 'Suspicious Links',
      description: 'Links that may be malicious or deceptive',
      allowed: false,
      requiresReview: true,
      maxSeverity: 'medium'
    }
  ];

  static async initialize(): Promise<void> {
    await this.ensureDefaultRules();
    await this.ensureDefaultCategories();
  }

  static async moderateText(
    text: string,
    userId?: string,
    context: Record<string, any> = {}
  ): Promise<ModerationResult> {
    const flags: ModerationFlag[] = [];
    let totalScore = 0;

    const rules = await this.getModerationRules();

    for (const rule of rules) {
      if (!rule.enabled || rule.type !== 'text') continue;

      const matches = this.matchPattern(rule.pattern, text);
      if (matches.length > 0) {
        const flag: ModerationFlag = {
          id: EncryptionUtils.generateSecureId('flag'),
          type: 'pattern_match',
          severity: rule.severity,
          ruleId: rule.id,
          message: `Matched ${rule.name}: ${matches.length} occurrence(s)`,
          confidence: this.calculateConfidence(matches.length, text.length),
          category: rule.category
        };

        flags.push(flag);
        totalScore += this.getSeverityScore(rule.severity);

        // Log the flag
        await this.logModerationEvent('text_flagged', rule.severity, {
          userId,
          ruleId: rule.id,
          matches: matches.length,
          textLength: text.length,
          context
        });
      }
    }

    // Additional text analysis
    const textAnalysis = this.analyzeTextContent(text);
    flags.push(...textAnalysis.flags);
    totalScore += textAnalysis.score;

    // Determine result
    const isApproved = this.isContentApproved(flags, totalScore);
    const requiresReview = this.requiresReview(flags, totalScore);
    const blockedReason = isApproved ? undefined : this.getBlockedReason(flags);

    const result: ModerationResult = {
      isApproved,
      flags,
      score: totalScore,
      requiresReview,
      blockedReason
    };

    // Log the moderation result
    await this.logModerationEvent('text_moderated', isApproved ? 'low' : 'high', {
      userId,
      approved: isApproved,
      score: totalScore,
      flagCount: flags.length,
      requiresReview,
      context
    });

    return result;
  }

  static async moderateImage(
    imageFile: File,
    userId?: string,
    context: Record<string, any> = {}
  ): Promise<ModerationResult> {
    const flags: ModerationFlag[] = [];
    let totalScore = 0;

    // Basic file checks
    const fileAnalysis = this.analyzeImageFile(imageFile);
    flags.push(...fileAnalysis.flags);
    totalScore += fileAnalysis.score;

    // Image content analysis (placeholder - would use AI service in production)
    const contentAnalysis = await this.analyzeImageContent(imageFile);
    flags.push(...contentAnalysis.flags);
    totalScore += contentAnalysis.score;

    // Determine result
    const isApproved = this.isContentApproved(flags, totalScore);
    const requiresReview = this.requiresReview(flags, totalScore);
    const blockedReason = isApproved ? undefined : this.getBlockedReason(flags);

    const result: ModerationResult = {
      isApproved,
      flags,
      score: totalScore,
      requiresReview,
      blockedReason
    };

    // Log the moderation result
    await this.logModerationEvent('image_moderated', isApproved ? 'low' : 'high', {
      userId,
      approved: isApproved,
      score: totalScore,
      flagCount: flags.length,
      requiresReview,
      fileSize: imageFile.size,
      mimeType: imageFile.type,
      context
    });

    return result;
  }

  static async sanitizeHtml(html: string): Promise<string> {
    return DOMPurify.sanitize(html, {
      ALLOWED_TAGS: [
        'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'blockquote',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'img', 'span', 'div'
      ],
      ALLOWED_ATTR: ['href', 'src', 'alt', 'title', 'class', 'style'],
      ALLOW_DATA_ATTR: false,
      ALLOW_UNKNOWN_PROTOCOLS: false,
      ALLOW_SCRIPT_PROTOCOLS: false,
      FORCE_BODY: false,
      RETURN_DOM: false,
      RETURN_DOM_FRAGMENT: false,
      RETURN_TRUSTED_TYPE: false
    });
  }

  static async reportContent(
    reporterId: string,
    contentType: ContentReport['contentType'],
    contentId: string,
    reason: string,
    description: string,
    severity: ContentReport['severity'],
    reportedUserId?: string,
    evidence?: any
  ): Promise<ContentReport> {
    const report: ContentReport = {
      id: EncryptionUtils.generateSecureId('report'),
      reporterId,
      reportedUserId,
      contentType,
      contentId,
      reason,
      description,
      severity,
      status: 'pending',
      createdAt: new Date().toISOString(),
      evidence
    };

    await this.storeReport(report);

    // Log the report
    await this.logModerationEvent('content_reported', severity, {
      reporterId,
      reportedUserId,
      contentType,
      contentId,
      reason,
      severity
    });

    return report;
  }

  static async getReports(status?: ContentReport['status']): Promise<ContentReport[]> {
    const reports = await this.getAllReports();
    return status ? reports.filter(r => r.status === status) : reports;
  }

  static async reviewReport(
    reportId: string,
    reviewedBy: string,
    resolution: string,
    action: 'approve' | 'reject' | 'flag' | 'block'
  ): Promise<boolean> {
    const report = await this.getReportById(reportId);
    if (!report) return false;

    report.status = 'resolved';
    report.reviewedBy = reviewedBy;
    report.reviewedAt = new Date().toISOString();
    report.resolution = resolution;

    await this.storeReport(report);

    // Log the review
    await this.logModerationEvent('report_resolved', 'medium', {
      reportId,
      reviewedBy,
      resolution,
      action,
      originalSeverity: report.severity
    });

    return true;
  }

  static async getModerationStats(): Promise<{
    totalReports: number;
    reportsByStatus: Record<string, number>;
    reportsByType: Record<string, number>;
    averageResolutionTime: number;
    topCategories: Array<{ category: string; count: number }>;
  }> {
    const reports = await this.getAllReports();

    const stats = {
      totalReports: reports.length,
      reportsByStatus: {},
      reportsByType: {},
      averageResolutionTime: 0,
      topCategories: [] as Array<{ category: string; count: number }>
    };

    // Count by status
    reports.forEach(report => {
      stats.reportsByStatus[report.status] = (stats.reportsByStatus[report.status] || 0) + 1;
    });

    // Count by type
    reports.forEach(report => {
      stats.reportsByType[report.contentType] = (stats.reportsByType[report.contentType] || 0) + 1;
    });

    // Calculate average resolution time
    const resolvedReports = reports.filter(r => r.status === 'resolved' && r.reviewedAt);
    if (resolvedReports.length > 0) {
      const totalTime = resolvedReports.reduce((sum, report) => {
        return sum + (new Date(report.reviewedAt!).getTime() - new Date(report.createdAt).getTime());
      }, 0);
      stats.averageResolutionTime = totalTime / resolvedReports.length / (1000 * 60 * 60); // Convert to hours
    }

    // Top categories (from rules)
    const categories = await this.getModerationRules();
    const categoryCounts: Record<string, number> = {};
    categories.forEach(category => {
      categoryCounts[category.category] = (categoryCounts[category.category] || 0) + 1;
    });

    stats.topCategories = Object.entries(categoryCounts)
      .map(([category, count]) => ({ category, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);

    return stats;
  }

  static async addModerationRule(rule: Omit<ModerationRule, 'id'>): Promise<ModerationRule> {
    const newRule: ModerationRule = {
      ...rule,
      id: EncryptionUtils.generateSecureId('rule')
    };

    const rules = await this.getModerationRules();
    rules.push(newRule);
    await this.storeModerationRules(rules);

    return newRule;
  }

  static async updateModerationRule(ruleId: string, updates: Partial<ModerationRule>): Promise<boolean> {
    const rules = await this.getModerationRules();
    const ruleIndex = rules.findIndex(r => r.id === ruleId);

    if (ruleIndex === -1) return false;

    rules[ruleIndex] = { ...rules[ruleIndex], ...updates };
    await this.storeModerationRules(rules);

    return true;
  }

  static async deleteModerationRule(ruleId: string): Promise<boolean> {
    const rules = await this.getModerationRules();
    const filteredRules = rules.filter(r => r.id !== ruleId);

    if (filteredRules.length === rules.length) return false;

    await this.storeModerationRules(filteredRules);
    return true;
  }

  // Private helper methods
  private static matchPattern(pattern: string | RegExp, text: string): string[] {
    if (typeof pattern === 'string') {
      const regex = new RegExp(pattern, 'gi');
      const matches = text.match(regex);
      return matches || [];
    } else {
      const matches = text.match(pattern);
      return matches || [];
    }
  }

  private static calculateConfidence(matchCount: number, textLength: number): number {
    const density = matchCount / (textLength / 100); // Matches per 100 characters
    return Math.min(100, density * 20); // Scale to 0-100
  }

  private static getSeverityScore(severity: ModerationFlag['severity']): number {
    switch (severity) {
      case 'low': return 1;
      case 'medium': return 5;
      case 'high': return 10;
      case 'critical': return 20;
      default: return 0;
    }
  }

  private static analyzeTextContent(text: string): { flags: ModerationFlag[]; score: number } {
    const flags: ModerationFlag[] = [];
    let score = 0;

    // Check for excessive capitalization
    const capsRatio = (text.match(/[A-Z]/g) || []).length / text.length;
    if (capsRatio > 0.5 && text.length > 20) {
      flags.push({
        id: EncryptionUtils.generateSecureId('flag'),
        type: 'excessive_caps',
        severity: 'low',
        ruleId: 'caps_analysis',
        message: 'Excessive capitalization detected',
        confidence: capsRatio * 100,
        category: 'formatting'
      });
      score += 1;
    }

    // Check for repetitive text
    const words = text.toLowerCase().split(/\s+/);
    const uniqueWords = new Set(words);
    const repetitionRatio = 1 - (uniqueWords.size / words.length);
    if (repetitionRatio > 0.3 && words.length > 10) {
      flags.push({
        id: EncryptionUtils.generateSecureId('flag'),
        type: 'repetitive_text',
        severity: 'medium',
        ruleId: 'repetition_analysis',
        message: 'High text repetition detected',
        confidence: repetitionRatio * 100,
        category: 'spam'
      });
      score += 3;
    }

    // Check for excessive length
    if (text.length > 5000) {
      flags.push({
        id: EncryptionUtils.generateSecureId('flag'),
        type: 'excessive_length',
        severity: 'low',
        ruleId: 'length_analysis',
        message: 'Content is unusually long',
        confidence: Math.min(100, text.length / 100),
        category: 'formatting'
      });
      score += 1;
    }

    return { flags, score };
  }

  private static analyzeImageFile(imageFile: File): { flags: ModerationFlag[]; score: number } {
    const flags: ModerationFlag[] = [];
    let score = 0;

    // Check file size
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (imageFile.size > maxSize) {
      flags.push({
        id: EncryptionUtils.generateSecureId('flag'),
        type: 'large_file',
        severity: 'medium',
        ruleId: 'file_size_analysis',
        message: 'Image file is too large',
        confidence: Math.min(100, imageFile.size / maxSize * 100),
        category: 'file_analysis'
      });
      score += 3;
    }

    // Check file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(imageFile.type)) {
      flags.push({
        id: EncryptionUtils.generateSecureId('flag'),
        type: 'invalid_type',
        severity: 'high',
        ruleId: 'file_type_analysis',
        message: 'Invalid image file type',
        confidence: 100,
        category: 'file_analysis'
      });
      score += 10;
    }

    return { flags, score };
  }

  private static async analyzeImageContent(imageFile: File): Promise<{ flags: ModerationFlag[]; score: number }> {
    // This is a placeholder for AI-based image analysis
    // In production, this would use services like Google Vision API, AWS Rekognition, etc.
    const flags: ModerationFlag[] = [];
    const score = 0;

    // For now, just check basic properties
    return { flags, score };
  }

  private static isContentApproved(flags: ModerationFlag[], score: number): boolean {
    // Block if any critical flags
    if (flags.some(f => f.severity === 'critical')) {
      return false;
    }

    // Block if score is too high
    if (score > 20) {
      return false;
    }

    // Block if multiple high severity flags
    const highFlags = flags.filter(f => f.severity === 'high');
    if (highFlags.length > 2) {
      return false;
    }

    return true;
  }

  private static requiresReview(flags: ModerationFlag[], score: number): boolean {
    // Require review if score is moderate
    if (score > 10) {
      return true;
    }

    // Require review if any high severity flags
    if (flags.some(f => f.severity === 'high')) {
      return true;
    }

    // Require review if multiple medium flags
    const mediumFlags = flags.filter(f => f.severity === 'medium');
    if (mediumFlags.length > 2) {
      return true;
    }

    return false;
  }

  private static getBlockedReason(flags: ModerationFlag[]): string {
    const criticalFlags = flags.filter(f => f.severity === 'critical');
    if (criticalFlags.length > 0) {
      return 'Content contains critically inappropriate material';
    }

    const highFlags = flags.filter(f => f.severity === 'high');
    if (highFlags.length > 2) {
      return 'Content contains multiple high-severity violations';
    }

    return 'Content violates community guidelines';
  }

  private static async logModerationEvent(
    eventType: string,
    severity: 'low' | 'medium' | 'high' | 'critical',
    details: Record<string, any>
  ): Promise<void> {
    await SecurityMonitoring.logEvent(
      `content_moderation_${eventType}`,
      severity,
      details
    );
  }

  // Storage methods
  private static async storeReport(report: ContentReport): Promise<void> {
    const reports = await this.getAllReports();
    reports.push(report);
    await SecureStorage.store(this.REPORTS_STORAGE_KEY, reports);
  }

  private static async getAllReports(): Promise<ContentReport[]> {
    return (await SecureStorage.retrieve<ContentReport[]>(this.REPORTS_STORAGE_KEY)) || [];
  }

  private static async getReportById(reportId: string): Promise<ContentReport | null> {
    const reports = await this.getAllReports();
    return reports.find(r => r.id === reportId) || null;
  }

  private static async getModerationRules(): Promise<ModerationRule[]> {
    const rules = await SecureStorage.retrieve<ModerationRule[]>(this.RULES_STORAGE_KEY);
    return rules || this.DEFAULT_RULES;
  }

  private static async storeModerationRules(rules: ModerationRule[]): Promise<void> {
    await SecureStorage.store(this.RULES_STORAGE_KEY, rules);
  }

  private static async ensureDefaultRules(): Promise<void> {
    const existingRules = await SecureStorage.retrieve<ModerationRule[]>(this.RULES_STORAGE_KEY);
    if (!existingRules || existingRules.length === 0) {
      await this.storeModerationRules(this.DEFAULT_RULES);
    }
  }

  private static async ensureDefaultCategories(): Promise<void> {
    const existingCategories = await SecureStorage.retrieve<ContentCategory[]>(this.CATEGORIES_STORAGE_KEY);
    if (!existingCategories || existingCategories.length === 0) {
      await SecureStorage.store(this.CATEGORIES_STORAGE_KEY, this.DEFAULT_CATEGORIES);
    }
  }
}