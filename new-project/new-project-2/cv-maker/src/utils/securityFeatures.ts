import DOMPurify from 'dompurify';
import { EncryptionUtils } from './encryptionUtils';
import { SecurityMonitoring } from './securityMonitoring';
import { ContentModeration } from './contentModeration';

export interface SecurityHeaders {
  'Content-Security-Policy': string;
  'X-Content-Type-Options': string;
  'X-Frame-Options': string;
  'X-XSS-Protection': string;
  'Strict-Transport-Security': string;
  'Referrer-Policy': string;
  'Permissions-Policy': string;
  'X-Content-Security-Policy': string;
}

export interface CSRFToken {
  token: string;
  expiresAt: string;
}

export interface SecurityConfig {
  enableCSP: boolean;
  enableXSSProtection: boolean;
  enableCSRFProtection: boolean;
  enableHSTS: boolean;
  enableRateLimiting: boolean;
  maxRequestsPerMinute: number;
  sessionTimeout: number;
  allowedOrigins: string[];
  blockedCountries: string[];
  enableIPWhitelist: boolean;
  whitelistedIPs: string[];
}

export class SecurityFeatures {
  private static readonly CSRF_TOKEN_KEY = 'csrf_token';
  private static readonly SECURITY_CONFIG_KEY = 'security_config';
  private static readonly NONCE_KEY = 'csp_nonce';

  private static readonly DEFAULT_CONFIG: SecurityConfig = {
    enableCSP: true,
    enableXSSProtection: true,
    enableCSRFProtection: true,
    enableHSTS: true,
    enableRateLimiting: true,
    maxRequestsPerMinute: 60,
    sessionTimeout: 30 * 60 * 1000, // 30 minutes
    allowedOrigins: ['http://localhost:3000', 'https://localhost:3000'],
    blockedCountries: [],
    enableIPWhitelist: false,
    whitelistedIPs: []
  };

  static async initialize(): Promise<void> {
    await this.ensureSecurityConfig();
    await this.generateCSRFToken();
    await this.generateCSPNonce();
  }

  static async getSecurityHeaders(): Promise<SecurityHeaders> {
    const config = await this.getSecurityConfig();
    const nonce = await this.getCSPNonce();

    return {
      'Content-Security-Policy': this.generateCSP(nonce, config),
      'X-Content-Type-Options': 'nosniff',
      'X-Frame-Options': 'DENY',
      'X-XSS-Protection': '1; mode=block',
      'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
      'Referrer-Policy': 'strict-origin-when-cross-origin',
      'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
      'X-Content-Security-Policy': this.generateCSP(nonce, config)
    };
  }

  static async validateCSRFToken(token: string): Promise<boolean> {
    if (!token) return false;

    const storedToken = await this.getCSRFToken();
    if (!storedToken) return false;

    // Check if token is expired
    if (new Date(storedToken.expiresAt) < new Date()) {
      await this.removeCSRFToken();
      return false;
    }

    // Verify token matches
    const isValid = await EncryptionUtils.verifyHMAC(
      token,
      'csrf_secret',
      storedToken.token
    );

    if (isValid) {
      // Regenerate token after successful use (optional security measure)
      await this.generateCSRFToken();
    }

    return isValid;
  }

  static async generateCSRFToken(): Promise<string> {
    const token = EncryptionUtils.generateSecureToken(32);
    const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(); // 24 hours

    const csrfToken: CSRFToken = {
      token: await EncryptionUtils.generateHMAC(token, 'csrf_secret'),
      expiresAt
    };

    localStorage.setItem(this.CSRF_TOKEN_KEY, JSON.stringify(csrfToken));

    return token;
  }

  static async sanitizeInput(input: string, allowHtml: boolean = false): Promise<string> {
    if (!allowHtml) {
      // Strip all HTML tags
      return DOMPurify.sanitize(input, {
        ALLOWED_TAGS: [],
        ALLOWED_ATTR: []
      });
    }

    // Allow basic HTML tags but sanitize dangerous content
    return await ContentModeration.sanitizeHtml(input);
  }

  static async validateJSONInput(jsonString: string, schema?: any): Promise<{ valid: boolean; data?: any; error?: string }> {
    try {
      const data = JSON.parse(jsonString);

      // Basic security checks
      if (this.containsPotentiallyDangerousContent(data)) {
        return {
          valid: false,
          error: 'Input contains potentially dangerous content'
        };
      }

      // Validate against schema if provided
      if (schema) {
        // Schema validation would go here
        // For now, just check basic structure
      }

      return {
        valid: true,
        data
      };
    } catch (error) {
      return {
        valid: false,
        error: 'Invalid JSON format'
      };
    }
  }

  static async checkRateLimit(
    identifier: string,
    endpoint: string
  ): Promise<{ allowed: boolean; remaining: number; resetTime: string }> {
    const config = await this.getSecurityConfig();
    if (!config.enableRateLimiting) {
      return {
        allowed: true,
        remaining: config.maxRequestsPerMinute,
        resetTime: new Date(Date.now() + 60000).toISOString()
      };
    }

    const rateLimitKey = `rate_limit_${identifier}_${endpoint}`;
    return await SecurityMonitoring.checkRateLimit(
      rateLimitKey,
      config.maxRequestsPerMinute,
      60 // 1 minute window
    );
  }

  static async validateOrigin(origin: string): Promise<boolean> {
    const config = await this.getSecurityConfig();
    return config.allowedOrigins.includes(origin) || config.allowedOrigins.includes('*');
  }

  static async checkIPWhitelist(ipAddress: string): Promise<boolean> {
    const config = await this.getSecurityConfig();
    if (!config.enableIPWhitelist) {
      return true;
    }

    return config.whitelistedIPs.includes(ipAddress) || config.whitelistedIPs.includes('*');
  }

  static async checkGeoBlocking(ipAddress: string): Promise<{ allowed: boolean; country?: string; reason?: string }> {
    const config = await this.getSecurityConfig();
    if (config.blockedCountries.length === 0) {
      return { allowed: true };
    }

    // In a real implementation, this would use a GeoIP service
    // For now, we'll simulate country detection
    const country = await this.getCountryFromIP(ipAddress);

    if (config.blockedCountries.includes(country)) {
      return {
        allowed: false,
        country,
        reason: `Access blocked from country: ${country}`
      };
    }

    return { allowed: true, country };
  }

  static async preventClickjacking(): Promise<{ headers: Record<string, string>; frameOptions: string }> {
    return {
      headers: {
        'X-Frame-Options': 'DENY',
        'Content-Security-Policy': "frame-ancestors 'none'",
        'X-Content-Security-Policy': "frame-ancestors 'none'"
      },
      frameOptions: 'DENY'
    };
  }

  static async secureCookies(): Promise<Array<{ name: string; options: any }>> {
    return [
      {
        name: 'session',
        options: {
          secure: true,
          httpOnly: true,
          sameSite: 'strict',
          path: '/',
          domain: window.location.hostname
        }
      },
      {
        name: 'csrf_token',
        options: {
          secure: true,
          httpOnly: true,
          sameSite: 'strict',
          path: '/',
          domain: window.location.hostname
        }
      }
    ];
  }

  static async validateFileType(file: File, allowedTypes: string[]): Promise<{ valid: boolean; error?: string }> {
    if (!allowedTypes.includes(file.type)) {
      return {
        valid: false,
        error: `File type ${file.type} is not allowed`
      };
    }

    // Additional file type validation
    if (!this.isValidFileType(file)) {
      return {
        valid: false,
        error: 'Invalid file type detected'
      };
    }

    return { valid: true };
  }

  static async preventSQLInjection(input: string): Promise<string> {
    // Basic SQL injection prevention
    const sqlPatterns = [
      /(\s|^)(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE)(\s|$)/gi,
      /(\s|^)(UNION|JOIN|WHERE|HAVING|GROUP BY)(\s|$)/gi,
      /(\s|^)(OR|AND)(\s+\d+\s*=\s*\d+)(\s|$)/gi,
      /[';]/g,
      /\/\*.*?\*\//g,
      /--.*$/gm
    ];

    let sanitized = input;
    sqlPatterns.forEach(pattern => {
      sanitized = sanitized.replace(pattern, '');
    });

    return sanitized.trim();
  }

  static async preventXSS(input: string): Promise<string> {
    return this.sanitizeInput(input, false);
  }

  static async checkForMaliciousContent(content: string): Promise<{ isSafe: boolean; threats: string[] }> {
    const threats: string[] = [];

    // Check for common attack patterns
    const xssPatterns = [
      /<script[^>]*>.*?<\/script>/gi,
      /javascript:/gi,
      /on\w+\s*=/gi,
      /<iframe[^>]*>.*?<\/iframe>/gi,
      /<object[^>]*>.*?<\/object>/gi,
      /<embed[^>]*>.*?<\/embed>/gi
    ];

    xssPatterns.forEach(pattern => {
      if (pattern.test(content)) {
        threats.push('XSS attack detected');
      }
    });

    // Check for SQL injection patterns
    const sqlPatterns = [
      /(\s|^)(SELECT|INSERT|UPDATE|DELETE|DROP)(\s|$)/gi,
      /UNION\s+SELECT/gi,
      /OR\s+\d+\s*=\s*\d+/gi
    ];

    sqlPatterns.forEach(pattern => {
      if (pattern.test(content)) {
        threats.push('SQL injection detected');
      }
    });

    // Check for command injection
    const cmdPatterns = [
      /[;&|`$(){}]/g,
      /\/\bin\b/gi,
      /\/bin\/sh/gi,
      /cmd\.exe/gi
    ];

    cmdPatterns.forEach(pattern => {
      if (pattern.test(content)) {
        threats.push('Command injection detected');
      }
    });

    return {
      isSafe: threats.length === 0,
      threats
    };
  }

  static async logSecurityEvent(
    eventType: string,
    severity: 'low' | 'medium' | 'high' | 'critical',
    details: Record<string, any>
  ): Promise<void> {
    await SecurityMonitoring.logEvent(
      `security_${eventType}`,
      severity,
      details
    );
  }

  // Private helper methods
  private static async ensureSecurityConfig(): Promise<void> {
    const existingConfig = await this.getSecurityConfig();
    if (!existingConfig) {
      await this.saveSecurityConfig(this.DEFAULT_CONFIG);
    }
  }

  private static async getSecurityConfig(): Promise<SecurityConfig> {
    const config = localStorage.getItem(this.SECURITY_CONFIG_KEY);
    return config ? JSON.parse(config) : this.DEFAULT_CONFIG;
  }

  private static async saveSecurityConfig(config: SecurityConfig): Promise<void> {
    localStorage.setItem(this.SECURITY_CONFIG_KEY, JSON.stringify(config));
  }

  private static generateCSP(nonce: string, config: SecurityConfig): string {
    if (!config.enableCSP) {
      return "default-src 'self'";
    }

    return [
      "default-src 'self'",
      "script-src 'self' 'nonce-" + nonce + "' 'strict-dynamic'",
      "style-src 'self' 'nonce-" + nonce + "'",
      "img-src 'self' data: https:",
      "font-src 'self' data:",
      "connect-src 'self'",
      "object-src 'none'",
      "base-uri 'self'",
      "frame-ancestors 'none'",
      "form-action 'self'",
      "require-trusted-types-for 'script'"
    ].join('; ');
  }

  private static async generateCSPNonce(): Promise<string> {
    const nonce = EncryptionUtils.generateSecureToken(16);
    sessionStorage.setItem(this.NONCE_KEY, nonce);
    return nonce;
  }

  private static async getCSPNonce(): Promise<string> {
    return sessionStorage.getItem(this.NONCE_KEY) || '';
  }

  private static async getCSRFToken(): Promise<CSRFToken | null> {
    const tokenData = localStorage.getItem(this.CSRF_TOKEN_KEY);
    return tokenData ? JSON.parse(tokenData) : null;
  }

  private static async removeCSRFToken(): Promise<void> {
    localStorage.removeItem(this.CSRF_TOKEN_KEY);
  }

  private static containsPotentiallyDangerousContent(data: any): boolean {
    if (typeof data === 'string') {
      const dangerousPatterns = [
        /<script[^>]*>.*?<\/script>/gi,
        /javascript:/gi,
        /on\w+\s*=/gi,
        /vbscript:/gi,
        /data:text\/html/gi
      ];

      return dangerousPatterns.some(pattern => pattern.test(data));
    }

    if (typeof data === 'object' && data !== null) {
      return Object.values(data).some(value => this.containsPotentiallyDangerousContent(value));
    }

    return false;
  }

  private static isValidFileType(file: File): boolean {
    // Check file signature (magic numbers)
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const arr = new Uint8Array(e.target?.result as ArrayBuffer);
        const header = Array.from(arr.slice(0, 4)).map(b => b.toString(16).padStart(2, '0')).join('');

        // Common file signatures
        const signatures: Record<string, string[]> = {
          'image/jpeg': ['ffd8ff'],
          'image/png': ['89504e47'],
          'image/gif': ['47494638'],
          'image/webp': ['52494646'],
          'application/pdf': ['25504446']
        };

        const validSignatures = signatures[file.type] || [];
        resolve(validSignatures.some(sig => header.startsWith(sig)));
      };
      reader.onerror = () => resolve(false);
      reader.readAsArrayBuffer(file.slice(0, 4));
    });
  }

  private static async getCountryFromIP(ipAddress: string): Promise<string> {
    // In a real implementation, this would use a GeoIP service
    // For now, return a placeholder
    return 'US';
  }

  static async generateSecurityReport(): Promise<string> {
    const config = await this.getSecurityConfig();
    const headers = await this.getSecurityHeaders();

    const report = {
      generatedAt: new Date().toISOString(),
      configuration: config,
      securityHeaders: headers,
      recommendations: [
        'Enable HSTS in production',
        'Regularly update CSP policies',
        'Monitor for new security threats',
        'Conduct regular security audits'
      ],
      bestPractices: [
        'Use HTTPS for all communications',
        'Implement proper authentication and authorization',
        'Validate and sanitize all user input',
        'Use parameterized queries for database access',
        'Implement proper error handling',
        'Keep dependencies updated'
      ]
    };

    return JSON.stringify(report, null, 2);
  }
}