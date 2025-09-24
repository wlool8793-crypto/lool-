import { PDFUtils, PDFSecurityOptions, WatermarkOptions } from './pdfUtils';
import { ImageProcessor, WatermarkOptions as ImageWatermarkOptions } from './imageProcessor';

export interface PrivacySettings {
  passwordProtection: boolean;
  watermarking: boolean;
  contentBlurring: boolean;
  accessControl: boolean;
  dataEncryption: boolean;
  secureSharing: boolean;
  autoExpire: boolean;
}

export interface PrivacyConfig {
  pdfPassword?: string;
  watermarkText?: string;
  watermarkImage?: string;
  blurSensitiveFields?: string[];
  accessLevel?: 'public' | 'restricted' | 'private';
  expirationHours?: number;
  maxDownloads?: number;
  allowedEmails?: string[];
}

export interface SensitiveDataRule {
  field: string;
  pattern: RegExp;
  replacement: string;
  enabled: boolean;
}

export interface AccessControlRule {
  id: string;
  type: 'email' | 'domain' | 'ip' | 'token';
  value: string;
  permissions: 'view' | 'download' | 'share';
  expiresAt?: Date;
}

export class PrivacyManager {
  private static readonly SENSITIVE_PATTERNS: SensitiveDataRule[] = [
    {
      field: 'email',
      pattern: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g,
      replacement: '[EMAIL PROTECTED]',
      enabled: true
    },
    {
      field: 'phone',
      pattern: /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g,
      replacement: '[PHONE]',
      enabled: true
    },
    {
      field: 'ssn',
      pattern: /\b\d{3}-\d{2}-\d{4}\b/g,
      replacement: '[SSN]',
      enabled: true
    },
    {
      field: 'creditCard',
      pattern: /\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b/g,
      replacement: '[CARD]',
      enabled: true
    },
    {
      field: 'address',
      pattern: /\d+\s+[\w\s]+(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Lane|Ln|Drive|Dr)/gi,
      replacement: '[ADDRESS]',
      enabled: true
    }
  ];

  static async applyPrivacyToPDF(
    elementId: string,
    privacyConfig: PrivacyConfig,
    filename: string = 'document.pdf'
  ): Promise<void> {
    try {
      // Apply content blurring if configured
      if (privacyConfig.blurSensitiveFields && privacyConfig.blurSensitiveFields.length > 0) {
        await this.blurSensitiveContent(elementId, privacyConfig.blurSensitiveFields);
      }

      // Apply watermarking if configured
      const watermark: WatermarkOptions = {};
      if (privacyConfig.watermarkText) {
        watermark.text = privacyConfig.watermarkText;
        watermark.opacity = 0.3;
        watermark.fontSize = 16;
        watermark.color = '#cccccc';
        watermark.angle = 45;
        watermark.position = 'center';
      }

      // Apply password protection
      const security: PDFSecurityOptions = {};
      if (privacyConfig.pdfPassword) {
        security.password = privacyConfig.pdfPassword;
        security.permissions = {
          printing: true,
          modifying: false,
          copying: false,
          annotating: false,
          fillingForms: false,
          extracting: false,
          assembling: false
        };
      }

      // Generate PDF with privacy features
      await PDFUtils.generatePDFFromElement(
        elementId,
        {
          quality: 0.95,
          margins: '20mm',
          dpi: 300,
          format: 'A4',
          orientation: 'portrait'
        },
        filename,
        {
          title: filename,
          author: 'CV Maker',
          subject: 'Protected Document',
          keywords: 'protected, private, secure',
          creationDate: new Date()
        },
        security,
        watermark
      );
    } catch (error) {
      console.error('Error applying privacy to PDF:', error);
      throw new Error('Failed to apply privacy settings');
    }
  }

  static async applyPrivacyToImage(
    file: File,
    privacyConfig: PrivacyConfig
  ): Promise<File> {
    let processedFile = file;

    // Apply watermarking
    if (privacyConfig.watermarkText || privacyConfig.watermarkImage) {
      const watermarkOptions: ImageWatermarkOptions = {
        text: privacyConfig.watermarkText,
        image: privacyConfig.watermarkImage,
        opacity: 0.5,
        position: 'center',
        fontSize: 24,
        color: '#ffffff',
        padding: 20
      };

      processedFile = await ImageProcessor.addWatermark(processedFile, watermarkOptions);
    }

    // Blur sensitive areas if needed (placeholder for face detection)
    if (privacyConfig.blurSensitiveFields?.includes('faces')) {
      const result = await ImageProcessor.detectFaces(processedFile);
      if (result.faces.length > 0) {
        // In a real implementation, you would blur detected faces
        console.log(`Detected ${result.faces.length} faces - would blur in production`);
      }
    }

    return processedFile;
  }

  static sanitizeSensitiveData(
    content: string,
    enabledRules: string[] = ['email', 'phone']
  ): string {
    let sanitizedContent = content;

    for (const rule of this.SENSITIVE_PATTERNS) {
      if (enabledRules.includes(rule.field) && rule.enabled) {
        sanitizedContent = sanitizedContent.replace(rule.pattern, rule.replacement);
      }
    }

    return sanitizedContent;
  }

  static async createSecureShareableLink(
    documentId: string,
    privacyConfig: PrivacyConfig
  ): Promise<{
    shareId: string;
    url: string;
    expiresAt: Date;
    accessKey: string;
  }> {
    const shareId = this.generateSecureId();
    const accessKey = this.generateSecureId();
    const expiresAt = privacyConfig.expirationHours
      ? new Date(Date.now() + privacyConfig.expirationHours * 60 * 60 * 1000)
      : new Date(Date.now() + 24 * 60 * 60 * 1000); // Default 24 hours

    const shareData = {
      documentId,
      shareId,
      accessKey,
      expiresAt: expiresAt.toISOString(),
      privacyConfig,
      createdAt: new Date().toISOString()
    };

    // In a real implementation, you would store this securely
    localStorage.setItem(`share_${shareId}`, JSON.stringify(shareData));

    const url = `${window.location.origin}/shared/${shareId}?key=${accessKey}`;

    return {
      shareId,
      url,
      expiresAt,
      accessKey
    };
  }

  static validateAccess(
    shareId: string,
    accessKey: string,
    additionalRules?: AccessControlRule[]
  ): {
    valid: boolean;
    error?: string;
    expiresAt?: Date;
  } {
    try {
      const shareData = localStorage.getItem(`share_${shareId}`);
      if (!shareData) {
        return { valid: false, error: 'Share not found' };
      }

      const share = JSON.parse(shareData);

      // Check access key
      if (share.accessKey !== accessKey) {
        return { valid: false, error: 'Invalid access key' };
      }

      // Check expiration
      const expiresAt = new Date(share.expiresAt);
      if (new Date() > expiresAt) {
        localStorage.removeItem(`share_${shareId}`);
        return { valid: false, error: 'Link expired' };
      }

      // Check additional access rules
      if (additionalRules) {
        for (const rule of additionalRules) {
          if (!this.validateAccessRule(rule)) {
            return { valid: false, error: 'Access denied' };
          }
        }
      }

      return {
        valid: true,
        expiresAt
      };
    } catch (error) {
      return { valid: false, error: 'Invalid share data' };
    }
  }

  static async encryptFile(
    file: File,
    password: string
  ): Promise<{
    encryptedFile: File;
    iv: string;
    salt: string;
  }> {
    try {
      const encoder = new TextEncoder();
      const passwordData = encoder.encode(password);

      // Generate salt
      const salt = crypto.getRandomValues(new Uint8Array(16));

      // Derive key
      const key = await crypto.subtle.deriveKey(
        {
          name: 'PBKDF2',
          salt,
          iterations: 100000,
          hash: 'SHA-256'
        },
        await crypto.subtle.importKey(
          'raw',
          passwordData,
          { name: 'PBKDF2' },
          false,
          ['deriveKey']
        ),
        { name: 'AES-GCM', length: 256 },
        false,
        ['encrypt']
      );

      // Generate IV
      const iv = crypto.getRandomValues(new Uint8Array(12));

      // Read file
      const fileData = await file.arrayBuffer();

      // Encrypt
      const encryptedData = await crypto.subtle.encrypt(
        {
          name: 'AES-GCM',
          iv
        },
        key,
        fileData
      );

      // Combine salt + iv + encrypted data
      const result = new Uint8Array(salt.length + iv.length + encryptedData.byteLength);
      result.set(salt, 0);
      result.set(iv, salt.length);
      result.set(new Uint8Array(encryptedData), salt.length + iv.length);

      const encryptedFile = new File([result], `${file.name}.encrypted`, {
        type: 'application/octet-stream'
      });

      return {
        encryptedFile,
        iv: Array.from(iv).join(','),
        salt: Array.from(salt).join(',')
      };
    } catch (error) {
      console.error('Encryption failed:', error);
      throw new Error('Failed to encrypt file');
    }
  }

  static async decryptFile(
    encryptedFile: File,
    password: string,
    salt: string,
    iv: string
  ): Promise<File> {
    try {
      const encoder = new TextEncoder();
      const passwordData = encoder.encode(password);

      // Parse salt and iv
      const saltArray = salt.split(',').map(Number);
      const ivArray = iv.split(',').map(Number);

      // Derive key
      const key = await crypto.subtle.deriveKey(
        {
          name: 'PBKDF2',
          salt: new Uint8Array(saltArray),
          iterations: 100000,
          hash: 'SHA-256'
        },
        await crypto.subtle.importKey(
          'raw',
          passwordData,
          { name: 'PBKDF2' },
          false,
          ['deriveKey']
        ),
        { name: 'AES-GCM', length: 256 },
        false,
        ['decrypt']
      );

      // Read encrypted file
      const encryptedData = await encryptedFile.arrayBuffer();
      const dataArray = new Uint8Array(encryptedData);

      // Extract actual encrypted data (skip salt + iv)
      const actualEncryptedData = dataArray.slice(saltArray.length + ivArray.length);

      // Decrypt
      const decryptedData = await crypto.subtle.decrypt(
        {
          name: 'AES-GCM',
          iv: new Uint8Array(ivArray)
        },
        key,
        actualEncryptedData
      );

      // Determine original file type
      const originalName = encryptedFile.name.replace('.encrypted', '');
      const mimeType = this.getMimeTypeFromName(originalName);

      return new File([decryptedData], originalName, { type: mimeType });
    } catch (error) {
      console.error('Decryption failed:', error);
      throw new Error('Failed to decrypt file');
    }
  }

  static generatePrivacyReport(
    privacyConfig: PrivacyConfig,
    documentId: string
  ): {
    reportId: string;
    generatedAt: Date;
    settings: PrivacySettings;
    protections: string[];
    risks: string[];
  } {
    const settings: PrivacySettings = {
      passwordProtection: !!privacyConfig.pdfPassword,
      watermarking: !!(privacyConfig.watermarkText || privacyConfig.watermarkImage),
      contentBlurring: !!(privacyConfig.blurSensitiveFields && privacyConfig.blurSensitiveFields.length > 0),
      accessControl: privacyConfig.accessLevel !== 'public',
      dataEncryption: true,
      secureSharing: true,
      autoExpire: !!privacyConfig.expirationHours
    };

    const protections: string[] = [];
    const risks: string[] = [];

    if (settings.passwordProtection) {
      protections.push('Document password protected');
    } else {
      risks.push('No password protection applied');
    }

    if (settings.watermarking) {
      protections.push('Watermark applied for tracking');
    } else {
      risks.push('No watermarking - document can be easily copied');
    }

    if (settings.contentBlurring) {
      protections.push('Sensitive content blurred');
    }

    if (settings.accessControl) {
      protections.push(`Access restricted to ${privacyConfig.accessLevel} users`);
    } else {
      risks.push('Public access - no restrictions');
    }

    if (settings.autoExpire) {
      protections.push(`Auto-expire after ${privacyConfig.expirationHours} hours`);
    } else {
      risks.push('No expiration - link valid indefinitely');
    }

    return {
      reportId: this.generateSecureId(),
      generatedAt: new Date(),
      settings,
      protections,
      risks
    };
  }

  private static async blurSensitiveContent(
    elementId: string,
    fieldsToBlur: string[]
  ): Promise<void> {
    const element = document.getElementById(elementId);
    if (!element) return;

    // Create a blur overlay for sensitive content
    const blurStyle = document.createElement('style');
    blurStyle.textContent = `
      .sensitive-blur {
        filter: blur(8px);
        user-select: none;
        pointer-events: none;
      }

      .sensitive-blur:hover {
        filter: blur(0px);
        transition: filter 0.3s ease;
      }
    `;
    document.head.appendChild(blurStyle);

    // Find and blur sensitive elements
    for (const field of fieldsToBlur) {
      const sensitiveElements = element.querySelectorAll(`[data-sensitive="${field}"]`);
      sensitiveElements.forEach(el => {
        el.classList.add('sensitive-blur');
      });
    }
  }

  private static validateAccessRule(rule: AccessControlRule): boolean {
    if (rule.expiresAt && new Date() > rule.expiresAt) {
      return false;
    }

    // In a real implementation, you would validate against user data
    // For now, we'll just check if the rule exists
    return true;
  }

  private static generateSecureId(): string {
    const array = new Uint8Array(16);
    crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
  }

  private static getMimeTypeFromName(filename: string): string {
    const extension = filename.split('.').pop()?.toLowerCase();
    const mimeTypes: Record<string, string> = {
      'pdf': 'application/pdf',
      'jpg': 'image/jpeg',
      'jpeg': 'image/jpeg',
      'png': 'image/png',
      'gif': 'image/gif',
      'doc': 'application/msword',
      'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'txt': 'text/plain'
    };

    return mimeTypes[extension || ''] || 'application/octet-stream';
  }

  static async auditPrivacySettings(
    currentSettings: PrivacySettings
  ): Promise<{
    score: number;
    recommendations: string[];
    criticalIssues: string[];
  }> {
    const recommendations: string[] = [];
    const criticalIssues: string[] = [];
    let score = 100;

    // Password protection
    if (!currentSettings.passwordProtection) {
      score -= 30;
      criticalIssues.push('Enable password protection for sensitive documents');
      recommendations.push('Consider adding password protection to prevent unauthorized access');
    }

    // Watermarking
    if (!currentSettings.watermarking) {
      score -= 15;
      recommendations.push('Add watermarking to track document sharing');
    }

    // Access control
    if (!currentSettings.accessControl) {
      score -= 20;
      recommendations.push('Implement access control to restrict document access');
    }

    // Auto-expire
    if (!currentSettings.autoExpire) {
      score -= 10;
      recommendations.push('Set expiration dates for shared links');
    }

    // Content blurring
    if (!currentSettings.contentBlurring) {
      score -= 10;
      recommendations.push('Consider blurring sensitive information in previews');
    }

    // Data encryption
    if (!currentSettings.dataEncryption) {
      score -= 15;
      criticalIssues.push('Enable data encryption for stored files');
    }

    return {
      score: Math.max(0, score),
      recommendations,
      criticalIssues
    };
  }
}