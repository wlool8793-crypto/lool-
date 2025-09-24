import {
  SecurityAlert,
  LoginAttempt,
  Device,
  Session
} from '../types/authentication';
import {
  PrivacyAuditLog
} from '../types/security';
import { EncryptionUtils } from './encryptionUtils';
import { SecureStorage } from './secureStorage';

export interface SecurityEvent {
  id: string;
  eventType: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  userId?: string;
  sessionId?: string;
  ipAddress: string;
  userAgent: string;
  timestamp: string;
  details: Record<string, any>;
  riskScore: number;
  mitigations: string[];
}

export interface SecurityMetrics {
  totalEvents: number;
  eventsByType: Record<string, number>;
  eventsBySeverity: Record<string, number>;
  topIPAddresses: Array<{ ip: string; count: number }>;
  topUserAgents: Array<{ userAgent: string; count: number }>;
  riskTrend: Array<{ date: string; score: number }>;
  blockedAttempts: number;
  suspiciousActivities: number;
}

export interface SecurityPolicy {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  rules: SecurityRule[];
  actions: SecurityAction[];
  priority: number;
}

export interface SecurityRule {
  id: string;
  name: string;
  condition: string;
  threshold: number;
  timeWindow: number; // minutes
  severity: 'low' | 'medium' | 'high' | 'critical';
  enabled: boolean;
}

export interface SecurityAction {
  id: string;
  name: string;
  type: 'block' | 'alert' | 'quarantine' | 'require_verification' | 'notify_admin';
  parameters: Record<string, any>;
}

export interface RateLimit {
  id: string;
  key: string;
  count: number;
  maxRequests: number;
  windowSize: number; // seconds
  resetTime: string;
}

export class SecurityMonitoring {
  private static readonly EVENTS_STORAGE_KEY = 'security_events';
  private static readonly POLICIES_STORAGE_KEY = 'security_policies';
  private static readonly RATE_LIMITS_KEY = 'rate_limits';
  private static readonly METRICS_STORAGE_KEY = 'security_metrics';

  private static readonly DEFAULT_POLICIES: SecurityPolicy[] = [
    {
      id: 'failed_login_policy',
      name: 'Failed Login Attempts',
      description: 'Detect multiple failed login attempts',
      enabled: true,
      rules: [
        {
          id: 'failed_login_rule',
          name: '5 failed logins in 15 minutes',
          condition: 'failed_login_count',
          threshold: 5,
          timeWindow: 15,
          severity: 'high',
          enabled: true
        }
      ],
      actions: [
        {
          id: 'lock_account',
          name: 'Lock Account',
          type: 'block',
          parameters: { duration: 15 }
        }
      ],
      priority: 1
    },
    {
      id: 'suspicious_ip_policy',
      name: 'Suspicious IP Activity',
      description: 'Detect activity from suspicious IP addresses',
      enabled: true,
      rules: [
        {
          id: 'high_request_rate',
          name: 'High request rate from single IP',
          condition: 'request_rate',
          threshold: 100,
          timeWindow: 5,
          severity: 'medium',
          enabled: true
        }
      ],
      actions: [
        {
          id: 'block_ip',
          name: 'Block IP Address',
          type: 'block',
          parameters: { duration: 60 }
        }
      ],
      priority: 2
    },
    {
      id: 'data_access_policy',
      name: 'Data Access Monitoring',
      description: 'Monitor unusual data access patterns',
      enabled: true,
      rules: [
        {
          id: 'bulk_data_access',
          name: 'Bulk data access',
          condition: 'bulk_access',
          threshold: 50,
          timeWindow: 10,
          severity: 'high',
          enabled: true
        }
      ],
      actions: [
        {
          id: 'require_verification',
          name: 'Require Additional Verification',
          type: 'require_verification',
          parameters: {}
        }
      ],
      priority: 3
    }
  ];

  static async initialize(): Promise<void> {
    await SecureStorage.initialize();
    await this.ensureDefaultPolicies();
    await this.cleanupOldEvents();
  }

  static async logEvent(
    eventType: string,
    severity: SecurityEvent['severity'],
    details: Record<string, any>,
    userId?: string,
    sessionId?: string,
    ipAddress?: string,
    userAgent?: string
  ): Promise<SecurityEvent> {
    const event: SecurityEvent = {
      id: EncryptionUtils.generateSecureId('event'),
      eventType,
      severity,
      userId,
      sessionId,
      ipAddress: ipAddress || 'unknown',
      userAgent: userAgent || 'unknown',
      timestamp: new Date().toISOString(),
      details,
      riskScore: this.calculateRiskScore(eventType, severity, details),
      mitigations: []
    };

    await this.storeEvent(event);

    // Check against security policies
    const violations = await this.checkSecurityPolicies(event);
    for (const violation of violations) {
      await this.handleSecurityViolation(violation, event);
    }

    // Update metrics
    await this.updateMetrics(event);

    return event;
  }

  static async monitorLoginAttempt(
    email: string,
    success: boolean,
    ipAddress?: string,
    userAgent?: string,
    userId?: string
  ): Promise<void> {
    const eventType = success ? 'successful_login' : 'failed_login';
    const severity = success ? 'low' : 'medium';

    await this.logEvent(eventType, severity, {
      email,
      success,
      timestamp: new Date().toISOString()
    }, userId, undefined, ipAddress, userAgent);
  }

  static async monitorDataAccess(
    userId: string,
    resourceType: string,
    resourceId: string,
    action: string,
    ipAddress?: string,
    userAgent?: string
  ): Promise<void> {
    await this.logEvent('data_access', 'low', {
      resourceType,
      resourceId,
      action,
      timestamp: new Date().toISOString()
    }, userId, undefined, ipAddress, userAgent);
  }

  static async monitorSuspiciousActivity(
    activityType: string,
    details: Record<string, any>,
    ipAddress?: string,
    userAgent?: string,
    userId?: string
  ): Promise<void> {
    await this.logEvent('suspicious_activity', 'high', {
      activityType,
      ...details,
      timestamp: new Date().toISOString()
    }, userId, undefined, ipAddress, userAgent);
  }

  static async checkRateLimit(
    key: string,
    maxRequests: number,
    windowSize: number
  ): Promise<{ allowed: boolean; remaining: number; resetTime: string }> {
    const now = new Date();
    const rateLimits = await this.getRateLimits();
    const existingLimit = rateLimits.find(rl => rl.key === key);

    if (existingLimit && new Date(existingLimit.resetTime) > now) {
      if (existingLimit.count >= maxRequests) {
        return {
          allowed: false,
          remaining: 0,
          resetTime: existingLimit.resetTime
        };
      }

      existingLimit.count++;
      await this.storeRateLimits(rateLimits);

      return {
        allowed: true,
        remaining: maxRequests - existingLimit.count,
        resetTime: existingLimit.resetTime
      };
    }

    // Create new rate limit
    const newLimit: RateLimit = {
      id: EncryptionUtils.generateSecureId('rate_limit'),
      key,
      count: 1,
      maxRequests,
      windowSize,
      resetTime: new Date(now.getTime() + windowSize * 1000).toISOString()
    };

    rateLimits.push(newLimit);
    await this.storeRateLimits(rateLimits);

    return {
      allowed: true,
      remaining: maxRequests - 1,
      resetTime: newLimit.resetTime
    };
  }

  static async getSecurityMetrics(timeRange: number = 24): Promise<SecurityMetrics> {
    const events = await this.getRecentEvents(timeRange);
    const metrics: SecurityMetrics = {
      totalEvents: events.length,
      eventsByType: {},
      eventsBySeverity: {},
      topIPAddresses: [],
      topUserAgents: [],
      riskTrend: [],
      blockedAttempts: 0,
      suspiciousActivities: 0
    };

    // Count by type and severity
    events.forEach(event => {
      metrics.eventsByType[event.eventType] = (metrics.eventsByType[event.eventType] || 0) + 1;
      metrics.eventsBySeverity[event.severity] = (metrics.eventsBySeverity[event.severity] || 0) + 1;

      if (event.eventType === 'failed_login') {
        metrics.blockedAttempts++;
      }

      if (event.eventType === 'suspicious_activity') {
        metrics.suspiciousActivities++;
      }
    });

    // Top IP addresses
    const ipCounts: Record<string, number> = {};
    events.forEach(event => {
      ipCounts[event.ipAddress] = (ipCounts[event.ipAddress] || 0) + 1;
    });

    metrics.topIPAddresses = Object.entries(ipCounts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 10)
      .map(([ip, count]) => ({ ip, count }));

    // Top user agents
    const uaCounts: Record<string, number> = {};
    events.forEach(event => {
      uaCounts[event.userAgent] = (uaCounts[event.userAgent] || 0) + 1;
    });

    metrics.topUserAgents = Object.entries(uaCounts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 10)
      .map(([userAgent, count]) => ({ userAgent, count }));

    return metrics;
  }

  static async getSecurityAlerts(userId?: string): Promise<SecurityAlert[]> {
    const events = await this.getRecentEvents(168); // Last 7 days

    return events
      .filter(event => {
        if (userId && event.userId !== userId) return false;
        return event.severity === 'high' || event.severity === 'critical';
      })
      .map(event => ({
        id: event.id,
        userId: event.userId || 'system',
        type: event.eventType as SecurityAlert['type'],
        severity: event.severity,
        title: `Security Alert: ${event.eventType}`,
        message: `${event.eventType} detected with ${event.severity} severity`,
        details: event.details,
        timestamp: event.timestamp,
        read: false,
        actionTaken: event.mitigations.length > 0
      }));
  }

  static async analyzeThreatIntelligence(): Promise<{
    threats: string[];
    recommendations: string[];
    riskLevel: 'low' | 'medium' | 'high' | 'critical';
  }> {
    const events = await this.getRecentEvents(24);
    const threats: string[] = [];
    const recommendations: string[] = [];

    // Analyze patterns
    const failedLogins = events.filter(e => e.eventType === 'failed_login');
    const suspiciousActivities = events.filter(e => e.eventType === 'suspicious_activity');

    if (failedLogins.length > 10) {
      threats.push('High volume of failed login attempts detected');
      recommendations.push('Consider implementing stronger authentication measures');
    }

    if (suspiciousActivities.length > 5) {
      threats.push('Multiple suspicious activities detected');
      recommendations.push('Review recent access logs and consider blocking suspicious IPs');
    }

    // Calculate overall risk level
    const highSeverityEvents = events.filter(e => e.severity === 'high' || e.severity === 'critical');
    let riskLevel: 'low' | 'medium' | 'high' | 'critical' = 'low';

    if (highSeverityEvents.length > 10) {
      riskLevel = 'critical';
    } else if (highSeverityEvents.length > 5) {
      riskLevel = 'high';
    } else if (highSeverityEvents.length > 2) {
      riskLevel = 'medium';
    }

    return {
      threats,
      recommendations,
      riskLevel
    };
  }

  static async generateSecurityReport(): Promise<string> {
    const metrics = await this.getSecurityMetrics(168); // Last 7 days
    const alerts = await this.getSecurityAlerts();
    const threatAnalysis = await this.analyzeThreatIntelligence();

    const report = {
      generatedAt: new Date().toISOString(),
      period: 'Last 7 days',
      metrics,
      alerts: alerts.length,
      threatAnalysis,
      recommendations: threatAnalysis.recommendations,
      policies: await this.getSecurityPolicies(),
      systemHealth: {
        monitoringEnabled: true,
        lastCheck: new Date().toISOString(),
        status: 'operational'
      }
    };

    return JSON.stringify(report, null, 2);
  }

  static async blockIPAddress(ipAddress: string, duration: number = 60): Promise<void> {
    // Log the block action
    await this.logEvent('ip_blocked', 'medium', {
      ipAddress,
      duration,
      blockedAt: new Date().toISOString(),
      reason: 'Security policy violation'
    });

    // In a real implementation, this would interface with a firewall or reverse proxy
    console.log(`Blocking IP address: ${ipAddress} for ${duration} minutes`);
  }

  static async quarantineSession(sessionId: string): Promise<void> {
    // Log the quarantine action
    await this.logEvent('session_quarantined', 'high', {
      sessionId,
      quarantinedAt: new Date().toISOString(),
      reason: 'Suspicious activity detected'
    });

    // In a real implementation, this would invalidate the session
    console.log(`Quarantining session: ${sessionId}`);
  }

  // Private helper methods
  private static async storeEvent(event: SecurityEvent): Promise<void> {
    const events = await this.getAllEvents();
    events.push(event);

    // Keep only last 10,000 events
    if (events.length > 10000) {
      events.splice(0, events.length - 10000);
    }

    await SecureStorage.store(this.EVENTS_STORAGE_KEY, events);
  }

  private static async getAllEvents(): Promise<SecurityEvent[]> {
    return (await SecureStorage.retrieve<SecurityEvent[]>(this.EVENTS_STORAGE_KEY)) || [];
  }

  private static async getRecentEvents(hours: number): Promise<SecurityEvent[]> {
    const events = await this.getAllEvents();
    const cutoffTime = new Date(Date.now() - hours * 60 * 60 * 1000);

    return events.filter(event => new Date(event.timestamp) > cutoffTime);
  }

  private static async cleanupOldEvents(): Promise<void> {
    const events = await this.getAllEvents();
    const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);

    const filteredEvents = events.filter(event => new Date(event.timestamp) > thirtyDaysAgo);
    await SecureStorage.store(this.EVENTS_STORAGE_KEY, filteredEvents);
  }

  private static async checkSecurityPolicies(event: SecurityEvent): Promise<SecurityPolicy[]> {
    const policies = await this.getSecurityPolicies();
    const violations: SecurityPolicy[] = [];

    for (const policy of policies) {
      if (!policy.enabled) continue;

      for (const rule of policy.rules) {
        if (!rule.enabled) continue;

        const isViolation = await this.evaluateRule(rule, event);
        if (isViolation) {
          violations.push(policy);
          break; // Only need one rule violation to trigger policy
        }
      }
    }

    return violations;
  }

  private static async evaluateRule(rule: SecurityRule, event: SecurityEvent): Promise<boolean> {
    const timeWindowStart = new Date(Date.now() - rule.timeWindow * 60 * 1000);
    const recentEvents = (await this.getAllEvents()).filter(e =>
      e.eventType === event.eventType &&
      new Date(e.timestamp) > timeWindowStart
    );

    switch (rule.condition) {
      case 'failed_login_count':
        return recentEvents.length >= rule.threshold;
      case 'request_rate':
        return recentEvents.length >= rule.threshold;
      case 'bulk_access':
        return event.details.accessCount >= rule.threshold;
      default:
        return false;
    }
  }

  private static async handleSecurityViolation(policy: SecurityPolicy, event: SecurityEvent): Promise<void> {
    for (const action of policy.actions) {
      await this.executeAction(action, event);
    }

    // Add mitigation to event
    event.mitigations.push(`Applied policy: ${policy.name}`);
    await this.storeEvent(event);
  }

  private static async executeAction(action: SecurityAction, event: SecurityEvent): Promise<void> {
    switch (action.type) {
      case 'block':
        if (event.ipAddress !== 'unknown') {
          await this.blockIPAddress(event.ipAddress, action.parameters.duration || 60);
        }
        break;
      case 'quarantine':
        if (event.sessionId) {
          await this.quarantineSession(event.sessionId);
        }
        break;
      case 'require_verification':
        // Would trigger additional verification
        break;
      case 'notify_admin':
        // Would send notification to admin
        break;
    }
  }

  private static async updateMetrics(event: SecurityEvent): Promise<void> {
    // Update security metrics
    const metrics = await this.getSecurityMetrics();
    // Implementation would update metrics based on the event
  }

  private static async ensureDefaultPolicies(): Promise<void> {
    const policies = await this.getSecurityPolicies();
    if (policies.length === 0) {
      await this.storeSecurityPolicies(this.DEFAULT_POLICIES);
    }
  }

  private static async getSecurityPolicies(): Promise<SecurityPolicy[]> {
    return (await SecureStorage.retrieve<SecurityPolicy[]>(this.POLICIES_STORAGE_KEY)) || this.DEFAULT_POLICIES;
  }

  private static async storeSecurityPolicies(policies: SecurityPolicy[]): Promise<void> {
    await SecureStorage.store(this.POLICIES_STORAGE_KEY, policies);
  }

  private static async getRateLimits(): Promise<RateLimit[]> {
    return (await SecureStorage.retrieve<RateLimit[]>(this.RATE_LIMITS_KEY)) || [];
  }

  private static async storeRateLimits(rateLimits: RateLimit[]): Promise<void> {
    // Clean up expired rate limits
    const now = new Date();
    const activeLimits = rateLimits.filter(rl => new Date(rl.resetTime) > now);
    await SecureStorage.store(this.RATE_LIMITS_KEY, activeLimits);
  }

  private static calculateRiskScore(
    eventType: string,
    severity: SecurityEvent['severity'],
    details: Record<string, any>
  ): number {
    let score = 0;

    // Base score by severity
    switch (severity) {
      case 'low':
        score = 1;
        break;
      case 'medium':
        score = 5;
        break;
      case 'high':
        score = 10;
        break;
      case 'critical':
        score = 20;
        break;
    }

    // Adjust by event type
    if (eventType === 'failed_login') score += 2;
    if (eventType === 'suspicious_activity') score += 5;
    if (eventType === 'data_breach') score += 15;

    // Adjust by details
    if (details.success === false) score += 3;
    if (details.bulkAccess) score += 5;

    return Math.min(score, 100); // Cap at 100
  }
}